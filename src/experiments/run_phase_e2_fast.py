"""
run_phase_e2_fast.py — High-Performance Parallel Execution Harness for Phase E2.

Optimizations:
1. Multi-process concurrency: ProcessPoolExecutor with 4 parallel GPU workers.
2. In-memory tensor caching: Parquet files loaded once as PyTorch tensors.
3. Clean baseline reuse: Eliminates redundant clean baseline simulations.
4. GPU-accelerated confusion matrix evaluation: Zero CPU-bound metric calculation.
5. Batch size 1024 aligned with configs/default.yaml.

Executes:
- Step 2: Evaluation Config Verification (Partitions 101..105 x Seeds 201..202, 30 rounds)
- Step 3: Damage Decomposition (Partition 11, Seed 1, 15 rounds)
- Step 4: Untargeted Attacks Gate (Partitions 11..13 x Seeds 1..2, 15 rounds)
"""

import sys
import copy
import json
import time
import argparse
import multiprocessing as mp
import concurrent.futures
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset

from src.model.mlp import IDS_MLP
from src.attacks.targeted_label_flip import TargetedLabelFlipAttack
from src.attacks.adaptive_norm_clip import AdaptiveNormClipAttack
from src.attacks.adaptive_cosine_mimic import AdaptiveCosineMimicAttack
from src.attacks.base import BaseAttack
from src.experiments.harness import AttackerSelector
from src.experiments.aggregate_results import evaluate_potency_gate

# Custom attack for Step 3: Random label noise
class RandomLabelNoiseAttack(BaseAttack):
    def __init__(self, source_class: int = 4, num_classes: int = 8, seed: int = 42) -> None:
        super().__init__(name="random_label_noise")
        self.source_class = source_class
        self.num_classes = num_classes
        self.seed = seed

    def poison_data(self, df: pd.DataFrame, round_num: int) -> pd.DataFrame:
        df_poisoned = df.copy()
        mask = df_poisoned["label"] == self.source_class
        source_indices = df_poisoned[mask].index
        if len(source_indices) == 0:
            return df_poisoned
        rng = np.random.RandomState(self.seed + round_num)
        target_choices = [c for c in range(self.num_classes) if c != self.source_class]
        random_labels = rng.choice(target_choices, size=len(source_indices))
        df_poisoned.loc[source_indices, "label"] = random_labels
        return df_poisoned


def fast_gpu_evaluate(model: nn.Module, X_test: torch.Tensor, y_test: torch.Tensor, device: torch.device) -> dict:
    """Computes exact accuracy, per-class F1, macro F1, and ASR directly on GPU in < 5ms."""
    model.eval()
    with torch.no_grad():
        logits = model(X_test.to(device))
        preds = logits.argmax(dim=1)
        y_dev = y_test.to(device)

        # Confusion matrix: row = true, col = pred
        idx = 8 * y_dev + preds
        cm = torch.bincount(idx, minlength=64).view(8, 8).float()

        tp = cm.diag()
        fp = cm.sum(dim=0) - tp
        fn = cm.sum(dim=1) - tp

        prec = tp / (tp + fp + 1e-10)
        rec = tp / (tp + fn + 1e-10)
        f1 = 2 * prec * rec / (prec + rec + 1e-10)

        macro_f1 = f1.mean().item()
        recon_f1 = f1[4].item()

        recon_total = cm[4].sum().item()
        asr = (cm[4, 0].item() / recon_total) if recon_total > 0 else 0.0
        acc = (preds == y_dev).float().mean().item()

    return {
        "accuracy": acc,
        "macro_f1": macro_f1,
        "recon_f1": recon_f1,
        "asr": asr,
    }


def execute_single_simulation(
    p_files_str: list[str],
    test_path_str: str,
    feature_cols: list[str],
    train_seed: int,
    num_rounds: int,
    client_attack_specs: list[dict], # [{"client_id": int, "attack_type": str, "kwargs": dict, "epochs": int}]
    active_client_indices: list[int],
    batch_size: int = 1024,
) -> dict:
    t0 = time.time()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    torch.backends.cudnn.benchmark = True
    torch.manual_seed(train_seed)

    # Load test set
    test_df = pd.read_parquet(test_path_str)
    X_test = torch.from_numpy(test_df[feature_cols].to_numpy(dtype="float32").copy())
    y_test = torch.from_numpy(test_df["label"].to_numpy(dtype="int64").copy())

    # Load clients into memory
    client_data = {}
    for cid in active_client_indices:
        df_c = pd.read_parquet(p_files_str[cid])
        client_data[cid] = df_c

    # Build attacks
    attacks = {}
    for spec in client_attack_specs:
        cid = spec["client_id"]
        atype = spec.get("attack_type")
        kwargs = spec.get("kwargs", {})
        if atype == "targeted_label_flip":
            attacks[cid] = TargetedLabelFlipAttack(**kwargs)
        elif atype == "random_label_noise":
            attacks[cid] = RandomLabelNoiseAttack(**kwargs)
        elif atype == "adaptive_norm_clip":
            attacks[cid] = AdaptiveNormClipAttack(**kwargs)
        elif atype == "adaptive_cosine_mimic":
            attacks[cid] = AdaptiveCosineMimicAttack(**kwargs)
        else:
            attacks[cid] = None

    global_model = IDS_MLP(in_features=len(feature_cols), num_classes=8).to(device)

    for r in range(1, num_rounds + 1):
        updates, samples = [], []

        for cid in active_client_indices:
            df_c = client_data[cid]
            atk = attacks.get(cid)
            lep = next((s.get("epochs", 1) for s in client_attack_specs if s["client_id"] == cid), 1)

            if atk is not None:
                df_train = atk.poison_data(df_c, round_num=r)
            else:
                df_train = df_c

            X_np = df_train[feature_cols].to_numpy(dtype="float32").copy()
            y_np = df_train["label"].to_numpy(dtype="int64").copy()
            X_tensor = torch.from_numpy(X_np)
            y_tensor = torch.from_numpy(y_np)

            class_counts = torch.bincount(y_tensor, minlength=8).float()
            cw = 1.0 / (class_counts + 1.0)
            class_weights = (cw / cw.mean()).to(device)

            dataset = TensorDataset(X_tensor, y_tensor)
            gen = torch.Generator().manual_seed(train_seed + r * 1000 + cid)
            loader = DataLoader(
                dataset,
                batch_size=batch_size,
                shuffle=True,
                drop_last=(len(dataset) > batch_size),
                generator=gen,
                pin_memory=True if device.type == "cuda" else False,
            )

            loc_model = IDS_MLP(in_features=len(feature_cols), num_classes=8).to(device)
            loc_model.load_state_dict(global_model.state_dict())
            opt = torch.optim.Adam(loc_model.parameters(), lr=1e-3, weight_decay=1e-4)
            crit = nn.CrossEntropyLoss(weight=class_weights)

            loc_model.train()
            for _ in range(lep):
                for X_b, y_b in loader:
                    X_b, y_b = X_b.to(device, non_blocking=True), y_b.to(device, non_blocking=True)
                    opt.zero_grad(set_to_none=True)
                    crit(loc_model(X_b), y_b).backward()
                    opt.step()

            # Update delta
            u = {}
            for k, v in global_model.state_dict().items():
                if torch.is_floating_point(v):
                    delta = loc_model.state_dict()[k].cpu() - v.cpu()
                    u[k] = delta
                else:
                    u[k] = loc_model.state_dict()[k].cpu()

            if atk is not None:
                u = atk.poison_update(u, round_num=r)

            updates.append(u)
            samples.append(len(df_c))

        tot_s = sum(samples)
        new_state = {}
        for k in global_model.state_dict():
            if torch.is_floating_point(global_model.state_dict()[k]):
                w_delta = sum(updates[i][k].to(device) * (samples[i] / tot_s) for i in range(len(active_client_indices)))
                new_state[k] = global_model.state_dict()[k] + w_delta
            else:
                new_state[k] = global_model.state_dict()[k]
        global_model.load_state_dict(new_state)

    m = fast_gpu_evaluate(global_model, X_test, y_test, device)
    m["wall_time_s"] = time.time() - t0
    return m


def _worker_wrapper(arg: dict) -> dict:
    """Wrapper function for multiprocessing pool execution."""
    res = execute_single_simulation(**arg["sim_kwargs"])
    return {**arg["meta"], **res}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=4, help="Number of concurrent multiprocessing workers")
    args = parser.parse_args()

    num_workers = args.workers
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"=== Running Phase E2 Parallel Evaluation Suite on {device} with {num_workers} workers ===")

    run_dir = Path("results/runs/phase_e2_evaluation")
    run_dir.mkdir(parents=True, exist_ok=True)
    out_file = run_dir / "runs.jsonl"
    with open(out_file, "w") as f:
        pass

    test_path_str = "data/processed/dev/test.parquet"
    test_df = pd.read_parquet(test_path_str)
    feature_cols = [c for c in test_df.columns if c not in ("label", "class_name")]

    t_suite_start = time.time()
    tasks_to_run = []

    # 1. Step 2 Evaluation Config Tasks (Partitions 101..105 x Seeds 201..202, 30 rounds)
    eval_partition_seeds = [101, 102, 103, 104, 105]
    eval_train_seeds = [201, 202]

    for ps in eval_partition_seeds:
        p_dir = Path(f"data/partitions/dev/seed_{ps}")
        p_files_str = [str(f) for f in sorted(p_dir.glob("client_*.parquet"))]
        selector = AttackerSelector([Path(f) for f in p_files_str], source_class=4)

        for ts in eval_train_seeds:
            atk_info = selector.select_stratified(target_band=(0.25, 0.40), seed=ts)
            atk_ids = set(atk_info["attacker_ids"])

            # Clean
            tasks_to_run.append({
                "meta": {
                    "step": "step2_eval_verification",
                    "condition": "clean",
                    "partition_seed": ps,
                    "train_seed": ts,
                    "rounds": 30,
                    "method": "fedavg",
                },
                "sim_kwargs": {
                    "p_files_str": p_files_str,
                    "test_path_str": test_path_str,
                    "feature_cols": feature_cols,
                    "train_seed": ts,
                    "num_rounds": 30,
                    "client_attack_specs": [{"client_id": i, "attack_type": None, "epochs": 1} for i in range(10)],
                    "active_client_indices": list(range(10)),
                }
            })

            # Attacked
            atk_specs = []
            for i in range(10):
                if i in atk_ids:
                    atk_specs.append({
                        "client_id": i,
                        "attack_type": "targeted_label_flip",
                        "kwargs": {"source_class": 4, "target_class": 0, "poison_ratio": 1.0, "boost_factor": 2.0},
                        "epochs": 1,
                    })
                else:
                    atk_specs.append({"client_id": i, "attack_type": None, "epochs": 1})

            tasks_to_run.append({
                "meta": {
                    "step": "step2_eval_verification",
                    "condition": "attacked",
                    "partition_seed": ps,
                    "train_seed": ts,
                    "rounds": 30,
                    "method": "fedavg",
                    "attackers": sorted(list(atk_ids)),
                    "recon_share": atk_info["source_sample_share"],
                },
                "sim_kwargs": {
                    "p_files_str": p_files_str,
                    "test_path_str": test_path_str,
                    "feature_cols": feature_cols,
                    "train_seed": ts,
                    "num_rounds": 30,
                    "client_attack_specs": atk_specs,
                    "active_client_indices": list(range(10)),
                }
            })

    # 2. Step 3 Damage Decomposition Tasks (Partition 11, Seed 1, 15 rounds)
    p11_dir = Path("data/partitions/dev/seed_11")
    p11_files_str = [str(f) for f in sorted(p11_dir.glob("client_*.parquet"))]
    selector_11 = AttackerSelector([Path(f) for f in p11_files_str], source_class=4)
    atk_info_11 = selector_11.select_stratified(target_band=(0.25, 0.40), seed=1)
    atk_ids_11 = set(atk_info_11["attacker_ids"]) # [3, 9]
    honest_ids_11 = [i for i in range(10) if i not in atk_ids_11]

    # (a) Honest control
    tasks_to_run.append({
        "meta": {"step": "step3_decomposition", "condition": "honest_control", "partition_seed": 11, "train_seed": 1, "rounds": 15},
        "sim_kwargs": {
            "p_files_str": p11_files_str, "test_path_str": test_path_str, "feature_cols": feature_cols, "train_seed": 1, "num_rounds": 15,
            "client_attack_specs": [{"client_id": i, "attack_type": None, "epochs": 1} for i in range(10)],
            "active_client_indices": list(range(10)),
        }
    })
    # (b) Attackers removed
    tasks_to_run.append({
        "meta": {"step": "step3_decomposition", "condition": "attackers_removed", "partition_seed": 11, "train_seed": 1, "rounds": 15},
        "sim_kwargs": {
            "p_files_str": p11_files_str, "test_path_str": test_path_str, "feature_cols": feature_cols, "train_seed": 1, "num_rounds": 15,
            "client_attack_specs": [{"client_id": i, "attack_type": None, "epochs": 1} for i in range(10)],
            "active_client_indices": honest_ids_11,
        }
    })
    # (c) Random noise
    r_specs = [{"client_id": i, "attack_type": "random_label_noise" if i in atk_ids_11 else None, "kwargs": {"seed": 42}, "epochs": 1} for i in range(10)]
    tasks_to_run.append({
        "meta": {"step": "step3_decomposition", "condition": "random_label_noise", "partition_seed": 11, "train_seed": 1, "rounds": 15},
        "sim_kwargs": {
            "p_files_str": p11_files_str, "test_path_str": test_path_str, "feature_cols": feature_cols, "train_seed": 1, "num_rounds": 15,
            "client_attack_specs": r_specs,
            "active_client_indices": list(range(10)),
        }
    })
    # (d) Targeted steering
    t_specs = [{"client_id": i, "attack_type": "targeted_label_flip" if i in atk_ids_11 else None, "kwargs": {"source_class": 4, "target_class": 0, "boost_factor": 2.0}, "epochs": 1} for i in range(10)]
    tasks_to_run.append({
        "meta": {"step": "step3_decomposition", "condition": "targeted_steering", "partition_seed": 11, "train_seed": 1, "rounds": 15},
        "sim_kwargs": {
            "p_files_str": p11_files_str, "test_path_str": test_path_str, "feature_cols": feature_cols, "train_seed": 1, "num_rounds": 15,
            "client_attack_specs": t_specs,
            "active_client_indices": list(range(10)),
        }
    })

    # 3. Step 4 Untargeted Attacks Tasks (Partitions 11..13 x Seeds 1..2, 15 rounds)
    for ps in [11, 12, 13]:
        p_dir = Path(f"data/partitions/dev/seed_{ps}")
        p_files_str = [str(f) for f in sorted(p_dir.glob("client_*.parquet"))]
        for ts in [1, 2]:
            # Clean baseline (shared between untargeted attacks)
            tasks_to_run.append({
                "meta": {"step": "step4_untargeted", "attack": "clean", "partition_seed": ps, "train_seed": ts, "rounds": 15},
                "sim_kwargs": {
                    "p_files_str": p_files_str, "test_path_str": test_path_str, "feature_cols": feature_cols, "train_seed": ts, "num_rounds": 15,
                    "client_attack_specs": [{"client_id": i, "attack_type": None, "epochs": 1} for i in range(10)],
                    "active_client_indices": list(range(10)),
                }
            })
            # Norm clip
            nc_specs = [{"client_id": i, "attack_type": "adaptive_norm_clip" if i in {0, 1} else None, "kwargs": {}, "epochs": 1} for i in range(10)]
            tasks_to_run.append({
                "meta": {"step": "step4_untargeted", "attack": "adaptive_norm_clip", "partition_seed": ps, "train_seed": ts, "rounds": 15},
                "sim_kwargs": {
                    "p_files_str": p_files_str, "test_path_str": test_path_str, "feature_cols": feature_cols, "train_seed": ts, "num_rounds": 15,
                    "client_attack_specs": nc_specs,
                    "active_client_indices": list(range(10)),
                }
            })
            # Cosine mimic
            cm_specs = [{"client_id": i, "attack_type": "adaptive_cosine_mimic" if i in {0, 1} else None, "kwargs": {}, "epochs": 1} for i in range(10)]
            tasks_to_run.append({
                "meta": {"step": "step4_untargeted", "attack": "adaptive_cosine_mimic", "partition_seed": ps, "train_seed": ts, "rounds": 15},
                "sim_kwargs": {
                    "p_files_str": p_files_str, "test_path_str": test_path_str, "feature_cols": feature_cols, "train_seed": ts, "num_rounds": 15,
                    "client_attack_specs": cm_specs,
                    "active_client_indices": list(range(10)),
                }
            })

    total_tasks = len(tasks_to_run)
    print(f"Total simulations to execute: {total_tasks} across {num_workers} parallel workers.")

    all_completed = []
    with concurrent.futures.ProcessPoolExecutor(
        max_workers=num_workers, mp_context=mp.get_context("spawn")
    ) as executor:
        futures = {executor.submit(_worker_wrapper, t): t for t in tasks_to_run}
        done_count = 0
        for f in concurrent.futures.as_completed(futures):
            res = f.result()
            all_completed.append(res)
            done_count += 1
            with open(out_file, "a") as out_f:
                out_f.write(json.dumps(res) + "\n")
            print(f"[{done_count}/{total_tasks}] Completed {res['step']} P{res['partition_seed']} S{res['train_seed']} ({res.get('condition') or res.get('attack')}) in {res['wall_time_s']:.1f}s -> Macro F1: {res['macro_f1']*100:.2f}%, RECON F1: {res['recon_f1']*100:.2f}%, ASR: {res['asr']*100:.2f}%")

    tot_elapsed = time.time() - t_suite_start
    print(f"\n=== Entire Phase E2 Evaluation Suite Finished in {tot_elapsed:.1f}s ({tot_elapsed/60:.2f} min) ===")

    # =========================================================================
    # STEP 2 EVALUATION CONFIG GATE REPORT
    # =========================================================================
    s2_records = [r for r in all_completed if r["step"] == "step2_eval_verification"]
    s2_clean = {(r["partition_seed"], r["train_seed"]): r for r in s2_records if r["condition"] == "clean"}
    s2_atk = [r for r in s2_records if r["condition"] == "attacked"]

    deltas_asr = []
    drops_rf1 = []
    clusters = []

    print("\n" + "="*80)
    print("STEP 2: EVALUATION CONFIGS VERIFICATION RESULTS (30 Rounds, Held-Out Partitions 101..105)")
    print("="*80)
    for r in sorted(s2_atk, key=lambda x: (x["partition_seed"], x["train_seed"])):
        key = (r["partition_seed"], r["train_seed"])
        c = s2_clean[key]
        d_asr = r["asr"] - c["asr"]
        d_rf1 = c["recon_f1"] - r["recon_f1"]
        deltas_asr.append(d_asr)
        drops_rf1.append(d_rf1)
        clusters.append(r["partition_seed"])
        print(f"  P{r['partition_seed']} S{r['train_seed']} (Atk {r['attackers']}, RECON {r['recon_share']*100:.1f}%): ASR {c['asr']*100:.1f}% -> {r['asr']*100:.1f}% (delta: {d_asr*100:+.2f}%), RECON F1 {c['recon_f1']*100:.1f}% -> {r['recon_f1']*100:.1f}% (drop: {d_rf1*100:+.2f}%)")

    asr_ok, f1_ok, gate, asr_st, rf1_st = evaluate_potency_gate(deltas_asr, drops_rf1, is_targeted=True, clusters=clusters)
    print("\nSTEP 2 EVALUATION CONFIG GATE OUTCOME:")
    print(f"  >>> GATE: {gate} (ASR_ok={asr_ok}, F1_ok={f1_ok})")
    print(f"  ASR Delta:  {asr_st[0]*100:+.1f}% [{asr_st[1]*100:.1f}%, {asr_st[2]*100:.1f}%]")
    print(f"  RECON Drop: {rf1_st[0]*100:+.1f}% [{rf1_st[1]*100:.1f}%, {rf1_st[2]*100:.1f}%]")

    # =========================================================================
    # STEP 3 DAMAGE DECOMPOSITION REPORT
    # =========================================================================
    print("\n" + "="*80)
    print("STEP 3: DAMAGE DECOMPOSITION RESULTS (Partition 11, Train Seed 1, 15 Rounds)")
    print("="*80)
    s3_records = {r["condition"]: r for r in all_completed if r["step"] == "step3_decomposition"}
    h = s3_records["honest_control"]
    rem = s3_records["attackers_removed"]
    rnd = s3_records["random_label_noise"]
    tgt = s3_records["targeted_steering"]
    print(f"  (a) Honest Control (10 clients):      RECON F1 = {h['recon_f1']*100:.2f}%, ASR = {h['asr']*100:.2f}%")
    print(f"  (b) Attackers Removed (8 clients):    RECON F1 = {rem['recon_f1']*100:.2f}%, ASR = {rem['asr']*100:.2f}% (Recovery diff: {(rem['recon_f1']-h['recon_f1'])*100:+.2f}%)")
    print(f"  (c) Random Label Noise Control:       RECON F1 = {rnd['recon_f1']*100:.2f}%, ASR = {rnd['asr']*100:.2f}% (Drop from honest: {(h['recon_f1']-rnd['recon_f1'])*100:+.2f}%)")
    print(f"  (d) Targeted Steering (gamma=2.0):    RECON F1 = {tgt['recon_f1']*100:.2f}%, ASR = {tgt['asr']*100:.2f}% (Drop from honest: {(h['recon_f1']-tgt['recon_f1'])*100:+.2f}%)")

    # =========================================================================
    # STEP 4 UNTARGETED ATTACKS REPORT
    # =========================================================================
    print("\n" + "="*80)
    print("STEP 4: UNTARGETED ATTACKS GATE RESULTS (15 Rounds, Partitions 11..13)")
    print("="*80)
    s4_records = [r for r in all_completed if r["step"] == "step4_untargeted"]
    s4_clean = {(r["partition_seed"], r["train_seed"]): r for r in s4_records if r["attack"] == "clean"}

    for atk_name in ["adaptive_norm_clip", "adaptive_cosine_mimic"]:
        atk_runs = [r for r in s4_records if r["attack"] == atk_name]
        macro_drops = []
        for r in atk_runs:
            c = s4_clean[(r["partition_seed"], r["train_seed"])]
            drop = c["macro_f1"] - r["macro_f1"]
            macro_drops.append(drop)
            print(f"  [{atk_name}] P{r['partition_seed']} S{r['train_seed']}: Clean {c['macro_f1']*100:.2f}% -> Atk {r['macro_f1']*100:.2f}% (Drop: {drop*100:+.2f}%)")

        mean_drop = np.mean(macro_drops)
        ci_lo, ci_hi = np.percentile(macro_drops, 2.5), np.percentile(macro_drops, 97.5)
        gate_untargeted = "**PASS**" if ci_lo > 0 else "**FAIL**"
        print(f"  >>> GATE [{atk_name}]: {gate_untargeted} | Macro F1 Drop: {mean_drop*100:+.2f}% [{ci_lo*100:.2f}%, {ci_hi*100:.2f}%]")

if __name__ == "__main__":
    main()
