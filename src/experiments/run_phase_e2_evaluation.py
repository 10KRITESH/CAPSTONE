"""
run_phase_e2_evaluation.py — Comprehensive Phase E2 Execution Script.

Executes on Cloud / Kaggle GPU:
1. Step 2: Verification of calibrated attack on EVALUATION configs
   - Partition seeds: {101, 102, 103, 104, 105}
   - Train seeds: {201, 202}
   - Horizon: 30 rounds
   - Calibrated knob: Band [0.25, 0.40], boost_factor=2.0, local_epochs=1, undefended FedAvg
   - Gate: evaluate_potency_gate (ASR_ok, F1_ok)

2. Step 3: Damage Decomposition
   - Attacker set: Partition 11, Train seed 1, Attacker IDs [3, 9] (RECON share 32.6%)
   - Horizon: 15 rounds
   - Conditions:
     (i)   Honest control (10 clients honest)
     (ii)  Attackers removed (FedAvg on 8 remaining clients)
     (iii) Random label noise (flip 100% of attacker RECON rows to random class)
     (iv)  Targeted label-flip attack (RECON -> BENIGN, boost_factor=2.0)

3. Step 4: Untargeted Attacks
   - Attacks: adaptive_norm_clip, adaptive_cosine_mimic
   - Calibration partitions: {11, 12, 13} x Train seeds: {1, 2}
   - Horizon: 15 rounds
   - Gate: Macro-F1 drop gate (clean macro-F1 - attacked macro-F1 > 0)

All results saved to results/runs/phase_e2_evaluation/runs.jsonl
"""

import sys
import copy
import json
import time
import yaml
import torch
import torch.nn as nn
import numpy as np
import pandas as pd
from pathlib import Path
from torch.utils.data import DataLoader, TensorDataset

from src.model.mlp import IDS_MLP
from src.data.dataset import CICIoTDataset
from src.federation.client import FLClient
from src.attacks.targeted_label_flip import TargetedLabelFlipAttack
from src.attacks.adaptive_norm_clip import AdaptiveNormClipAttack
from src.attacks.adaptive_cosine_mimic import AdaptiveCosineMimicAttack
from src.attacks.base import BaseAttack
from src.model.evaluate import evaluate
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

def run_simulation(
    p_files: list[Path],
    feature_cols: list[str],
    class_names: list[str],
    test_loader: DataLoader,
    device: torch.device,
    train_seed: int,
    num_rounds: int,
    client_configs: list[dict], # list of dicts: {"client_id": int, "attack": BaseAttack or None, "epochs": int}
    active_client_indices: list[int] | None = None,
) -> dict:
    start_t = time.time()
    torch.manual_seed(train_seed)
    global_model = IDS_MLP(in_features=len(feature_cols), num_classes=8).to(device)

    if active_client_indices is None:
        active_client_indices = list(range(len(p_files)))

    clients = {}
    for idx in active_client_indices:
        cfg = client_configs[idx]
        c = FLClient(
            client_id=idx,
            partition_path=p_files[idx],
            feature_cols=feature_cols,
            num_classes=8,
            attack=cfg.get("attack", None),
            device=device,
        )
        clients[idx] = c

    for r in range(1, num_rounds + 1):
        updates, samples = [], []
        for idx in active_client_indices:
            c = clients[idx]
            cfg = client_configs[idx]
            lep = cfg.get("epochs", 1)
            u, s, _ = c.train_local(
                global_model=global_model,
                local_epochs=lep,
                batch_size=512,
                lr=1e-3,
                round_num=r,
                train_seed=train_seed,
            )
            updates.append(u)
            samples.append(s)

        tot_s = sum(samples)
        new_state = {}
        for k in global_model.state_dict():
            if torch.is_floating_point(global_model.state_dict()[k]):
                w_delta = sum(updates[i][k].to(device) * (samples[i] / tot_s) for i in range(len(active_client_indices)))
                new_state[k] = global_model.state_dict()[k] + w_delta
            else:
                new_state[k] = global_model.state_dict()[k]
        global_model.load_state_dict(new_state)

    metrics = evaluate(global_model, test_loader, device, class_names, asr_pair=(4, 0))
    wall_time = time.time() - start_t
    return {
        "macro_f1": float(metrics["macro_f1"]),
        "recon_f1": float(metrics["per_class"]["RECON"]["f1"]),
        "asr": float(metrics["attack_success_rate"]),
        "wall_time_s": wall_time,
    }

def main():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"=== Starting Phase E2 Evaluation Suite on {device} ===")

    run_dir = Path("results/runs/phase_e2_evaluation")
    run_dir.mkdir(parents=True, exist_ok=True)
    out_file = run_dir / "runs.jsonl"
    with open(out_file, "w") as f:
        pass # truncate

    with open("configs/label_mapping.yaml") as f:
        lm = yaml.safe_load(f)
    class_names = [lm["idx_to_class"][i] for i in range(len(lm["idx_to_class"]))]

    test_ds = CICIoTDataset("data/processed/dev/test.parquet")
    test_loader = DataLoader(test_ds, batch_size=512, shuffle=False)
    feature_cols = test_ds.feature_cols

    # =========================================================================
    # STEP 2: Evaluation Config Verification (30 rounds, Eval partitions 101..105)
    # =========================================================================
    print("\n" + "="*80)
    print("STEP 2: Evaluating Calibrated Attack on EVALUATION Configs (30 Rounds)")
    print("Knobs: Band [0.25, 0.40], boost_factor=2.0, local_epochs=1, FedAvg")
    print("="*80)

    eval_partition_seeds = [101, 102, 103, 104, 105]
    eval_train_seeds = [201, 202]
    eval_rounds = 30
    eval_band = (0.25, 0.40)
    boost_gamma = 2.0

    eval_step2_records = []

    for ps in eval_partition_seeds:
        p_dir = Path(f"data/partitions/dev/seed_{ps}")
        p_files = sorted(p_dir.glob("client_*.parquet"))
        assert len(p_files) == 10, f"Expected 10 files in {p_dir}"
        selector = AttackerSelector(p_files, source_class=4)

        for ts in eval_train_seeds:
            atk_info = selector.select_stratified(target_band=eval_band, seed=ts)
            atk_ids = set(atk_info["attacker_ids"])

            # 1. Clean run
            clean_client_cfgs = [{"client_id": i, "attack": None, "epochs": 1} for i in range(10)]
            print(f"\nRunning Eval P{ps} S{ts} CLEAN (30 rounds)...")
            res_clean = run_simulation(
                p_files=p_files,
                feature_cols=feature_cols,
                class_names=class_names,
                test_loader=test_loader,
                device=device,
                train_seed=ts,
                num_rounds=eval_rounds,
                client_configs=clean_client_cfgs,
            )
            print(f"  CLEAN: Macro F1={res_clean['macro_f1']*100:.2f}%, RECON F1={res_clean['recon_f1']*100:.2f}%, ASR={res_clean['asr']*100:.2f}% ({res_clean['wall_time_s']:.1f}s)")

            # Log clean record
            clean_rec = {
                "step": "step2_eval_verification",
                "condition": "clean",
                "partition_seed": ps,
                "train_seed": ts,
                "rounds": eval_rounds,
                "method": "fedavg",
                "macro_f1": res_clean["macro_f1"],
                "recon_f1": res_clean["recon_f1"],
                "asr": res_clean["asr"],
                "wall_time_s": res_clean["wall_time_s"],
            }
            with open(out_file, "a") as f:
                f.write(json.dumps(clean_rec) + "\n")

            # 2. Attacked run
            atk_client_cfgs = []
            for i in range(10):
                if i in atk_ids:
                    atk_obj = TargetedLabelFlipAttack(source_class=4, target_class=0, poison_ratio=1.0, boost_factor=boost_gamma)
                    atk_client_cfgs.append({"client_id": i, "attack": atk_obj, "epochs": 1})
                else:
                    atk_client_cfgs.append({"client_id": i, "attack": None, "epochs": 1})

            print(f"Running Eval P{ps} S{ts} ATTACKED (Atks {sorted(list(atk_ids))}, RECON {atk_info['source_sample_share']*100:.1f}%, 30 rounds)...")
            res_atk = run_simulation(
                p_files=p_files,
                feature_cols=feature_cols,
                class_names=class_names,
                test_loader=test_loader,
                device=device,
                train_seed=ts,
                num_rounds=eval_rounds,
                client_configs=atk_client_cfgs,
            )
            print(f"  ATTACKED: Macro F1={res_atk['macro_f1']*100:.2f}%, RECON F1={res_atk['recon_f1']*100:.2f}%, ASR={res_atk['asr']*100:.2f}% ({res_atk['wall_time_s']:.1f}s)")

            d_asr = res_atk["asr"] - res_clean["asr"]
            d_rf1 = res_clean["recon_f1"] - res_atk["recon_f1"]
            print(f"  -> Delta ASR: {d_asr*100:+.2f}%, Drop RECON F1: {d_rf1*100:+.2f}%")

            atk_rec = {
                "step": "step2_eval_verification",
                "condition": "attacked",
                "partition_seed": ps,
                "train_seed": ts,
                "rounds": eval_rounds,
                "method": "fedavg",
                "attackers": sorted(list(atk_ids)),
                "recon_share": atk_info["source_sample_share"],
                "macro_f1": res_atk["macro_f1"],
                "recon_f1": res_atk["recon_f1"],
                "asr": res_atk["asr"],
                "delta_asr": d_asr,
                "drop_recon_f1": d_rf1,
                "wall_time_s": res_atk["wall_time_s"],
            }
            with open(out_file, "a") as f:
                f.write(json.dumps(atk_rec) + "\n")

            eval_step2_records.append(atk_rec)

    # Evaluate Gate on Step 2 Evaluation configs
    all_d_asr = [r["delta_asr"] for r in eval_step2_records]
    all_d_rf1 = [r["drop_recon_f1"] for r in eval_step2_records]
    all_clusters = [r["partition_seed"] for r in eval_step2_records]

    asr_ok, f1_ok, gate, asr_st, rf1_st = evaluate_potency_gate(
        paired_asr_deltas=all_d_asr,
        paired_recon_drops=all_d_rf1,
        is_targeted=True,
        clusters=all_clusters,
    )
    print("\n" + "="*80)
    print(f"STEP 2 EVALUATION CONFIGS GATE OUTCOME: {gate}")
    print(f"  ASR Criterion: {asr_st[0]*100:+.1f}% [{asr_st[1]*100:.1f}%, {asr_st[2]*100:.1f}%] -> ASR_ok={asr_ok}")
    print(f"  F1  Criterion: {rf1_st[0]*100:+.1f}% [{rf1_st[1]*100:.1f}%, {rf1_st[2]*100:.1f}%] -> F1_ok={f1_ok}")
    print("="*80)

    # =========================================================================
    # STEP 3: Damage Decomposition
    # =========================================================================
    print("\n" + "="*80)
    print("STEP 3: Damage Decomposition Controls (Partition 11, Train Seed 1, 15 rounds)")
    print("="*80)

    p11_dir = Path("data/partitions/dev/seed_11")
    p11_files = sorted(p11_dir.glob("client_*.parquet"))
    selector_11 = AttackerSelector(p11_files, source_class=4)
    atk_info_11 = selector_11.select_stratified(target_band=(0.25, 0.40), seed=1)
    atk_ids_11 = set(atk_info_11["attacker_ids"]) # [3, 9] holding 32.6% RECON
    honest_ids_11 = [i for i in range(10) if i not in atk_ids_11]
    print(f"Selected Attackers: {sorted(list(atk_ids_11))} (RECON Share: {atk_info_11['source_sample_share']*100:.1f}%)")

    # (a) Honest Control (all 10 clients honest)
    cfgs_honest = [{"client_id": i, "attack": None, "epochs": 1} for i in range(10)]
    res_honest = run_simulation(p11_files, feature_cols, class_names, test_loader, device, 1, 15, cfgs_honest)
    print(f"Condition (a) Honest Control (10 clients): RECON F1={res_honest['recon_f1']*100:.2f}%, ASR={res_honest['asr']*100:.2f}%")

    # (b) Attackers Removed (FedAvg on 8 remaining honest clients)
    cfgs_removed = [{"client_id": i, "attack": None, "epochs": 1} for i in range(10)]
    res_removed = run_simulation(p11_files, feature_cols, class_names, test_loader, device, 1, 15, cfgs_removed, active_client_indices=honest_ids_11)
    print(f"Condition (b) Attackers Removed (8 clients): RECON F1={res_removed['recon_f1']*100:.2f}%, ASR={res_removed['asr']*100:.2f}%")

    # (c) Random Label Noise (flip attacker RECON to random classes)
    cfgs_random = []
    for i in range(10):
        if i in atk_ids_11:
            cfgs_random.append({"client_id": i, "attack": RandomLabelNoiseAttack(source_class=4, seed=42), "epochs": 1})
        else:
            cfgs_random.append({"client_id": i, "attack": None, "epochs": 1})
    res_random = run_simulation(p11_files, feature_cols, class_names, test_loader, device, 1, 15, cfgs_random)
    print(f"Condition (c) Random Label Noise Control:   RECON F1={res_random['recon_f1']*100:.2f}%, ASR={res_random['asr']*100:.2f}%")

    # (d) Malicious Targeted Steering (RECON -> BENIGN, gamma=2.0)
    cfgs_targeted = []
    for i in range(10):
        if i in atk_ids_11:
            cfgs_targeted.append({"client_id": i, "attack": TargetedLabelFlipAttack(source_class=4, target_class=0, boost_factor=2.0), "epochs": 1})
        else:
            cfgs_targeted.append({"client_id": i, "attack": None, "epochs": 1})
    res_targeted = run_simulation(p11_files, feature_cols, class_names, test_loader, device, 1, 15, cfgs_targeted)
    print(f"Condition (d) Targeted Steering (gamma=2.0): RECON F1={res_targeted['recon_f1']*100:.2f}%, ASR={res_targeted['asr']*100:.2f}%")

    decomp_summary = {
        "step": "step3_damage_decomposition",
        "partition_seed": 11,
        "train_seed": 1,
        "attackers": sorted(list(atk_ids_11)),
        "recon_share": atk_info_11["source_sample_share"],
        "honest_control": res_honest,
        "attackers_removed": res_removed,
        "random_noise": res_random,
        "targeted_steering": res_targeted,
    }
    with open(out_file, "a") as f:
        f.write(json.dumps(decomp_summary) + "\n")

    # =========================================================================
    # STEP 4: Untargeted Attacks (norm_clip, cosine_mimic)
    # =========================================================================
    print("\n" + "="*80)
    print("STEP 4: Untargeted Attacks Gate Evaluation (15 rounds, Calibration Partitions)")
    print("="*80)

    untargeted_attacks = [
        ("adaptive_norm_clip", AdaptiveNormClipAttack),
        ("adaptive_cosine_mimic", AdaptiveCosineMimicAttack),
    ]

    for atk_name, atk_cls in untargeted_attacks:
        print(f"\n--- Testing Untargeted Attack: {atk_name} ---")
        deltas_macro = []
        clusters_list = []

        for ps in [11, 12, 13]:
            p_dir = Path(f"data/partitions/dev/seed_{ps}")
            p_files = sorted(p_dir.glob("client_*.parquet"))

            for ts in [1, 2]:
                # Pick arbitrary 20% adversaries (clients 0 and 1)
                atks = {0, 1}

                # Clean
                cfgs_c = [{"client_id": i, "attack": None, "epochs": 1} for i in range(10)]
                r_c = run_simulation(p_files, feature_cols, class_names, test_loader, device, ts, 15, cfgs_c)

                # Attacked
                cfgs_a = [{"client_id": i, "attack": atk_cls() if i in atks else None, "epochs": 1} for i in range(10)]
                r_a = run_simulation(p_files, feature_cols, class_names, test_loader, device, ts, 15, cfgs_a)

                # Macro F1 drop = clean - attacked
                drop_macro = r_c["macro_f1"] - r_a["macro_f1"]
                deltas_macro.append(drop_macro)
                clusters_list.append(ps)

                print(f"  P{ps} S{ts}: Clean Macro F1={r_c['macro_f1']*100:.2f}% -> Attacked Macro F1={r_a['macro_f1']*100:.2f}% (Drop: {drop_macro*100:+.2f}%)")

                rec = {
                    "step": "step4_untargeted",
                    "attack": atk_name,
                    "partition_seed": ps,
                    "train_seed": ts,
                    "clean_macro_f1": r_c["macro_f1"],
                    "atk_macro_f1": r_a["macro_f1"],
                    "macro_f1_drop": drop_macro,
                }
                with open(out_file, "a") as f:
                    f.write(json.dumps(rec) + "\n")

        # Untargeted Gate: macro_f1 drop lower CI > 0
        mean_d, ci_lo, ci_hi = np.mean(deltas_macro), float(np.percentile(deltas_macro, 2.5)), float(np.percentile(deltas_macro, 97.5))
        gate_pass = ci_lo > 0
        print(f"  >>> GATE [{atk_name}]: {'PASS' if gate_pass else 'FAIL'} | Macro F1 Drop: {mean_d*100:+.2f}% [{ci_lo*100:.2f}%, {ci_hi*100:.2f}%]")

    print("\n=== Phase E2 Evaluation Suite Successfully Completed ===")

if __name__ == "__main__":
    main()
