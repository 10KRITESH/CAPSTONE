"""
run_phase_e4_verification.py — Phase E4 Empirical Verification Benchmark.

Evaluates the Phase E4 defense fixes against baseline FedAvg and flawed legacy D0
across CALIBRATION configurations ({11, 12, 13} x {1, 2}, 30 rounds, 36 simulations).

Compares 6 Conditions:
  1. clean_fedavg: Undefended baseline under clean data.
  2. clean_d0: Legacy flawed detector (raw norms, no MAD floor, no head energy gate, no warmup).
  3. clean_fixed: Refined deployable defense with all 5 Phase E4 fixes active.
  4. attacked_fedavg: Undefended baseline under calibrated potent attack (Band [0.25, 0.40], gamma=2.0).
  5. attacked_d0: Legacy flawed detector under potent attack.
  6. attacked_fixed: Refined deployable defense under potent attack.

Directly Measures:
  - Flaw 1: Honest false degradation flags on minority classes (e.g. RECON).
  - Flaw 2: Norm Z correlation with client sample count (raw vs sample-scaled).
  - Flaw 3: Honest cosine divergence flag suppression under adaptive cohort bounds.
  - Flaw 4: Honest client false quarantine rate and warmup horizon lockout prevention.
  - Flaw 5: Majority monopolization resolution and clean Macro-F1 parity with FedAvg.
  - Attack Resilience: Attacked RECON F1 protection, ASR suppression, and attacker attribution.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import copy
import json
import logging
import multiprocessing as mp
from pathlib import Path
import sys
import time
from typing import Any

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import numpy as np
import pandas as pd
from scipy import stats
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset

from src.attacks.targeted_label_flip import TargetedLabelFlipAttack
from src.experiments.harness import AttackerSelector
from src.experiments.aggregate_results import bootstrap_ci
from src.federation.trust_aggregation import aggregate_trust_class_aware
from src.model.mlp import IDS_MLP
from src.trust.evidence import TemporalEvidenceTracker
from src.trust.reputation import PerClassReputationManager
from src.trust.state_machine import ClientState, ClientStateMachine
from src.trust.update_metrics import (
    compute_cosine_similarity,
    compute_geometric_median_reference,
    compute_robust_norm_score,
    flatten_update,
)
from src.trust.validator import UpdateValidator, ValidationResult

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)


# ══════════════════════════════════════════════════════════════════════════════
# Vectorized Fast GPU Evaluation
# ══════════════════════════════════════════════════════════════════════════════

def fast_evaluate(
    model: nn.Module,
    X_test: torch.Tensor,
    y_test: torch.Tensor,
    device: torch.device,
    num_classes: int = 8,
) -> dict[str, float]:
    """Computes exact accuracy, macro-F1, per-class F1, and ASR directly via confusion matrix."""
    model.eval()
    with torch.no_grad():
        X_dev = X_test if X_test.device == device else X_test.to(device)
        y_dev = y_test if y_test.device == device else y_test.to(device)
        logits = model(X_dev)
        preds = logits.argmax(dim=1)

        idx = num_classes * y_dev + preds
        cm = torch.bincount(idx, minlength=num_classes * num_classes).view(num_classes, num_classes).float()

        tp = cm.diag()
        fp = cm.sum(dim=0) - tp
        fn = cm.sum(dim=1) - tp

        prec = tp / (tp + fp + 1e-10)
        rec = tp / (tp + fn + 1e-10)
        f1 = 2 * prec * rec / (prec + rec + 1e-10)

        macro_f1 = f1.mean().item()
        acc = (preds == y_dev).float().mean().item()

        rec_per_class = tp / (cm.sum(dim=1) + 1e-10)
        bal_acc = rec_per_class.mean().item()

        recon_f1 = f1[4].item()
        recon_total = cm[4].sum().item()
        asr = (cm[4, 0].item() / recon_total) if recon_total > 0 else 0.0

    res = {
        "accuracy": acc,
        "balanced_accuracy": bal_acc,
        "macro_f1": macro_f1,
        "recon_f1": recon_f1,
        "asr": asr,
    }
    for c in range(num_classes):
        res[f"f1_class_{c}"] = f1[c].item()
    return res


def compute_client_skew_features(partition_dir: Path, num_classes: int = 8) -> dict[int, dict]:
    """Computes label distribution, KL divergence from global, majority share, and support."""
    counts = np.zeros((10, num_classes), dtype=int)
    for cid in range(10):
        df_c = pd.read_parquet(partition_dir / f"client_{cid:02d}.parquet")
        vc = df_c["label"].value_counts()
        for c, count in vc.items():
            counts[cid, int(c)] = count

    global_counts = counts.sum(axis=0)
    global_dist = global_counts / max(1, global_counts.sum())

    client_features = {}
    for cid in range(10):
        n_i = int(counts[cid].sum())
        p_i = counts[cid] / max(1, n_i)
        kl = float(np.sum(p_i * np.log((p_i + 1e-9) / (global_dist + 1e-9))))
        maj_c = int(np.argmax(p_i))
        maj_share = float(p_i[maj_c])
        low_support = [c for c in range(num_classes) if counts[cid, c] < 100]

        client_features[cid] = {
            "client_id": cid,
            "sample_count": n_i,
            "majority_class": maj_c,
            "majority_share": maj_share,
            "kl_divergence": kl,
            "recon_support": int(counts[cid, 4]),
            "low_support_classes": low_support,
            "per_class_counts": counts[cid].tolist(),
        }
    return client_features


# ══════════════════════════════════════════════════════════════════════════════
# Single Simulation Worker
# ══════════════════════════════════════════════════════════════════════════════

def run_single_simulation(
    mode: str, # "clean_fedavg", "clean_d0", "clean_fixed", "attacked_fedavg", "attacked_d0", "attacked_fixed"
    partition_seed: int,
    train_seed: int,
    num_rounds: int,
    partition_dir_str: str,
    test_path_str: str,
    server_val_path_str: str,
    feature_cols: list[str],
    class_names: list[str],
    batch_size: int = 1024,
) -> dict[str, Any]:
    t0 = time.time()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    torch.backends.cudnn.benchmark = True
    torch.manual_seed(train_seed)
    np.random.seed(train_seed)

    p_dir = Path(partition_dir_str)
    partition_files = [p_dir / f"client_{i:02d}.parquet" for i in range(10)]

    # Load validation and test tensors
    val_df = pd.read_parquet(server_val_path_str)
    X_val = torch.from_numpy(val_df[feature_cols].to_numpy(dtype="float32").copy())
    y_val = torch.from_numpy(val_df["label"].to_numpy(dtype="int64").copy())
    val_dataset = TensorDataset(X_val, y_val)
    val_loader = DataLoader(val_dataset, batch_size=batch_size * 2, shuffle=False)

    test_df = pd.read_parquet(test_path_str)
    X_test = torch.from_numpy(test_df[feature_cols].to_numpy(dtype="float32").copy()).to(device)
    y_test = torch.from_numpy(test_df["label"].to_numpy(dtype="int64").copy()).to(device)

    # Load client data into memory
    client_dfs = [pd.read_parquet(pf) for pf in partition_files]
    client_samples = [len(df) for df in client_dfs]
    client_recon = [int((df["label"] == 4).sum()) for df in client_dfs]
    total_samples = sum(client_samples)
    total_recon = sum(client_recon)

    is_attacked = mode.startswith("attacked_")
    malicious_set = set()
    attacks = {}
    attacker_recon_share = 0.0

    if is_attacked:
        selector = AttackerSelector(partition_files, source_class=4)
        strat = selector.select_stratified(
            target_band=(0.25, 0.40),
            num_malicious=2,
            seed=train_seed + partition_seed * 100,
        )
        malicious_set = set(strat["attacker_ids"])
        attacker_recon_share = strat["source_sample_share"]
        for aid in malicious_set:
            attacks[aid] = TargetedLabelFlipAttack(
                source_class=4,
                target_class=0,
                boost_factor=2.0,
            )

    # Initialize global model
    global_model = IDS_MLP(in_features=len(feature_cols), num_classes=8).to(device)

    # Trust Engine components
    is_fixed = ("fixed" in mode)
    is_d0 = ("d0" in mode)

    # Instantiate validator with appropriate configuration
    if is_fixed:
        validator = UpdateValidator(
            server_val_loader=val_loader,
            class_names=class_names,
            device=device,
            detector_variant="D2",
            d2_z_thresh=3.0,
            mad_floor=0.015,
            energy_share_gate=0.40,
            norm_scale_power=0.585,
        )
        state_machine = ClientStateMachine(
            probation_threshold=0.40,
            quarantine_threshold=0.70,
            probation_consecutive_bad_threshold=2,
            warmup_rounds=5, # 5-round warmup horizon
        )
        rep_manager = PerClassReputationManager(class_names=class_names)
        evidence_tracker = TemporalEvidenceTracker(warmup_rounds=5)
    elif is_d0:
        # Legacy flawed D0
        validator = UpdateValidator(
            server_val_loader=val_loader,
            class_names=class_names,
            device=device,
            detector_variant="D0",
            mad_floor=1e-5, # No MAD floor in legacy
            energy_share_gate=0.0, # No head energy gate in legacy
        )
        state_machine = ClientStateMachine(
            probation_threshold=0.40,
            quarantine_threshold=0.70,
            probation_consecutive_bad_threshold=2,
            warmup_rounds=0, # No warmup in legacy
        )
        rep_manager = PerClassReputationManager(class_names=class_names)
        evidence_tracker = TemporalEvidenceTracker()
    else:
        validator = None
        state_machine = None
        rep_manager = None
        evidence_tracker = None

    # Pre-build client training datasets and class weights
    client_datasets = []
    client_weights = []
    for cid in range(10):
        df_c = client_dfs[cid]
        if cid in malicious_set:
            df_train = attacks[cid].poison_data(df_c, round_num=1)
        else:
            df_train = df_c

        X_tensor = torch.from_numpy(df_train[feature_cols].to_numpy(dtype="float32").copy())
        y_tensor = torch.from_numpy(df_train["label"].to_numpy(dtype="int64").copy())

        class_counts = torch.bincount(y_tensor, minlength=8).float()
        cw = 1.0 / (class_counts + 1.0)
        c_weights = (cw / cw.mean()).to(device)

        client_datasets.append(TensorDataset(X_tensor, y_tensor))
        client_weights.append(c_weights)

    telemetry_records = []
    quarantine_schedule = []
    round_convergence = []

    for r in range(1, num_rounds + 1):
        # 1. Local Training
        client_updates = []
        for cid in range(10):
            dataset = client_datasets[cid]
            class_weights = client_weights[cid]

            gen = torch.Generator().manual_seed(train_seed + r * 1000 + cid)
            loader = DataLoader(
                dataset,
                batch_size=batch_size,
                shuffle=True,
                drop_last=(len(dataset) > batch_size),
                generator=gen,
                pin_memory=(device.type == "cuda"),
            )

            loc_model = IDS_MLP(in_features=len(feature_cols), num_classes=8).to(device)
            loc_model.load_state_dict(global_model.state_dict())
            opt = torch.optim.Adam(loc_model.parameters(), lr=1e-3, weight_decay=1e-4)
            crit = nn.CrossEntropyLoss(weight=class_weights)

            loc_model.train()
            for X_b, y_b in loader:
                X_b, y_b = X_b.to(device, non_blocking=True), y_b.to(device, non_blocking=True)
                opt.zero_grad(set_to_none=True)
                crit(loc_model(X_b), y_b).backward()
                opt.step()

            # Parameter delta
            u = {}
            for k, v in global_model.state_dict().items():
                if torch.is_floating_point(v):
                    delta = loc_model.state_dict()[k].cpu() - v.cpu()
                    u[k] = delta
                else:
                    u[k] = loc_model.state_dict()[k].cpu()

            if cid in malicious_set:
                u = attacks[cid].poison_update(u, round_num=r)

            client_updates.append(u)

        # 2. Validation & Defense State Tracking
        state_factors = {cid: 1.0 for cid in range(10)}
        num_quarantined_this_round = 0

        if is_fixed or is_d0:
            sample_counts_arg = client_samples if is_fixed else None
            val_results = validator.validate_updates(
                global_model=global_model,
                client_updates=client_updates,
                client_ids=list(range(10)),
                round_num=r,
                sample_counts=sample_counts_arg,
            )

            for cid, vr in enumerate(val_results):
                rep_vector = rep_manager.update_reputation(cid, vr)
                ev_rec = evidence_tracker.update_evidence(cid, vr, rep_vector)
                new_state, changed, reason = state_machine.update_state(cid, ev_rec, r)
                sf = state_machine.get_state_factor(cid, ev_rec.evidence_score)
                state_factors[cid] = sf

                if new_state == ClientState.QUARANTINED:
                    num_quarantined_this_round += 1

                # Head energy on RECON (class 4)
                hw = client_updates[cid].get("head.weight")
                recon_head_energy = 0.0
                if hw is not None and hw.ndim == 2:
                    row_sq = torch.sum(hw.float() ** 2, dim=1)
                    recon_head_energy = float(torch.sqrt(row_sq[4] + 1e-12) / (torch.norm(torch.sqrt(row_sq + 1e-12)) + 1e-8))

                # Also compute both raw and scaled norm Z-scores for confound verification
                telemetry_records.append({
                    "round": r,
                    "client_id": cid,
                    "partition_seed": partition_seed,
                    "train_seed": train_seed,
                    "mode": mode,
                    "is_attacker": 1 if cid in malicious_set else 0,
                    "sample_count": client_samples[cid],
                    "raw_norm": vr.norm_val,
                    "norm_z": vr.norm_z_score,
                    "cosine_sim": vr.cosine_sim,
                    "global_delta_f1": vr.global_f1_impact,
                    "recon_impact": vr.per_class_f1_impact.get("RECON", 0.0),
                    "recon_head_energy": recon_head_energy,
                    "peer_z_recon": vr.peer_z_scores.get("RECON", 0.0),
                    "evidence_score": ev_rec.evidence_score,
                    "state": new_state.value,
                    "state_factor": sf,
                    "flags_fired": "|".join(vr.suspicious_flags) if vr.suspicious_flags else "NONE",
                })

        quarantine_schedule.append(num_quarantined_this_round)

        # 3. Aggregation Update
        if mode in ("clean_fedavg", "attacked_fedavg"):
            # Plain sample-weighted FedAvg
            tot_w = sum(client_samples)
            new_state_dict = {}
            for k, v in global_model.state_dict().items():
                if torch.is_floating_point(v):
                    agg_delta = sum(client_updates[i][k].to(device) * (client_samples[i] / tot_w) for i in range(10))
                    new_state_dict[k] = v + agg_delta
                else:
                    new_state_dict[k] = v
            global_model.load_state_dict(new_state_dict)

        elif is_d0:
            # D0: Exclude quarantined clients (state_factor == 0), plain FedAvg over survivors
            active_cids = [i for i in range(10) if state_factors[i] > 0.0]
            if not active_cids:
                active_cids = list(range(10))
            tot_w = sum(client_samples[i] for i in active_cids)
            new_state_dict = {}
            for k, v in global_model.state_dict().items():
                if torch.is_floating_point(v):
                    agg_delta = sum(client_updates[i][k].to(device) * (client_samples[i] / tot_w) for i in active_cids)
                    new_state_dict[k] = v + agg_delta
                else:
                    new_state_dict[k] = v
            global_model.load_state_dict(new_state_dict)

        elif is_fixed:
            # Fixed Defense: Trust-Aware + Head Salience Aggregation
            agg_global, _ = aggregate_trust_class_aware(
                global_model=global_model,
                updates=client_updates,
                sample_counts=client_samples,
                client_ids=list(range(10)),
                reputation_table=rep_manager.reputation_table,
                state_factors=state_factors,
                class_names=class_names,
                trust_config={"trust": {"aggregation": {"use_head_salience": True, "head_weight_power": 0.5}}},
            )
            global_model.load_state_dict(agg_global)

        # Evaluate convergence on test set
        test_eval = fast_evaluate(global_model, X_test, y_test, device)
        round_convergence.append({
            "round": r,
            "macro_f1": test_eval["macro_f1"],
            "recon_f1": test_eval["recon_f1"],
            "asr": test_eval["asr"],
        })

    wall_time = time.time() - t0
    final_eval = fast_evaluate(global_model, X_test, y_test, device)

    # Compute client exclusion and detection statistics
    if is_fixed or is_d0:
        honest_quars = [cid for cid in range(10) if cid not in malicious_set and state_machine.get_state(cid) == ClientState.QUARANTINED]
        honest_quar_rate = len(honest_quars) / max(1, 10 - len(malicious_set))
        honest_excluded_samples = sum(client_samples[cid] for cid in honest_quars)
        honest_data_exclusion = honest_excluded_samples / max(1, total_samples)

        atk_quars = [cid for cid in malicious_set if state_machine.get_state(cid) == ClientState.QUARANTINED]
        atk_probs = [cid for cid in malicious_set if state_machine.get_state(cid) in (ClientState.PROBATION, ClientState.QUARANTINED)]
        atk_quar_rate = (len(atk_quars) / len(malicious_set)) if malicious_set else 0.0
        atk_prob_rate = (len(atk_probs) / len(malicious_set)) if malicious_set else 0.0
    else:
        honest_quars = []
        honest_quar_rate = 0.0
        honest_data_exclusion = 0.0
        atk_quars = []
        atk_quar_rate = 0.0
        atk_prob_rate = 0.0

    return {
        "mode": mode,
        "partition_seed": partition_seed,
        "train_seed": train_seed,
        "is_attacked": is_attacked,
        "attacker_recon_share": attacker_recon_share,
        "num_rounds": num_rounds,
        "macro_f1": final_eval["macro_f1"],
        "balanced_accuracy": final_eval["balanced_accuracy"],
        "accuracy": final_eval["accuracy"],
        "recon_f1": final_eval["recon_f1"],
        "asr": final_eval["asr"],
        "honest_quar_rate": honest_quar_rate,
        "honest_data_exclusion": honest_data_exclusion,
        "attacker_quar_rate": atk_quar_rate,
        "attacker_prob_rate": atk_prob_rate,
        "quarantined_honest_clients": honest_quars,
        "quarantined_attackers": atk_quars,
        "quarantine_schedule": quarantine_schedule,
        "wall_time_s": wall_time,
        "telemetry": telemetry_records,
        "convergence": round_convergence,
    }


def _simulation_task_wrapper(args_dict: dict) -> dict:
    return run_single_simulation(**args_dict)


# ══════════════════════════════════════════════════════════════════════════════
# Main Benchmark Orchestration
# ══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="Phase E4 Empirical Verification Benchmark")
    parser.add_argument("--rounds", type=int, default=30, help="FL rounds per simulation")
    parser.add_argument("--workers", type=int, default=4, help="Concurrent multiprocessing workers")
    parser.add_argument("--out-dir", type=str, default="results/runs/phase_e4_verification", help="Output directory")
    args = parser.parse_args()

    t_suite_start = time.time()
    run_dir = Path(args.out_dir)
    run_dir.mkdir(parents=True, exist_ok=True)

    test_path_str = "data/processed/dev/test.parquet"
    server_val_path_str = "data/processed/dev/server_val.parquet"

    test_df_cols = pd.read_parquet(test_path_str, columns=None)
    feature_cols = [c for c in test_df_cols.columns if c not in ("label", "class_name")]

    label_mapping_path = Path("configs/label_mapping.yaml")
    import yaml
    with open(label_mapping_path) as f:
        lm_cfg = yaml.safe_load(f)
    class_names = [lm_cfg["idx_to_class"][i] for i in range(len(lm_cfg["idx_to_class"]))]

    # Calibration configurations
    calibration_configs = [
        (11, 1), (11, 2),
        (12, 1), (12, 2),
        (13, 1), (13, 2),
    ]

    modes_to_evaluate = [
        "clean_fedavg",
        "clean_d0",
        "clean_fixed",
        "attacked_fedavg",
        "attacked_d0",
        "attacked_fixed",
    ]

    tasks = []
    for pse, tse in calibration_configs:
        common = {
            "partition_seed": pse,
            "train_seed": tse,
            "num_rounds": args.rounds,
            "partition_dir_str": f"data/partitions/dev/seed_{pse}",
            "test_path_str": test_path_str,
            "server_val_path_str": server_val_path_str,
            "feature_cols": feature_cols,
            "class_names": class_names,
            "batch_size": 1024,
        }
        for m in modes_to_evaluate:
            tasks.append({**common, "mode": m})

    log.info(f"Launching {len(tasks)} simulations across {len(calibration_configs)} configs with {args.workers} workers...")

    results_list = []
    if args.workers > 1 and len(tasks) > 1:
        with concurrent.futures.ProcessPoolExecutor(max_workers=args.workers, mp_context=mp.get_context("spawn")) as executor:
            futures = [executor.submit(_simulation_task_wrapper, t) for t in tasks]
            for f in concurrent.futures.as_completed(futures):
                res = f.result()
                results_list.append(res)
                log.info(f"[{res['mode']}] P{res['partition_seed']} S{res['train_seed']} done in {res['wall_time_s']:.1f}s | Macro F1: {res['macro_f1']*100:.2f}%, RECON F1: {res['recon_f1']*100:.2f}%, Honest Quar: {res['honest_quar_rate']*100:.1f}%")
    else:
        for t in tasks:
            res = run_single_simulation(**t)
            results_list.append(res)
            log.info(f"[{res['mode']}] P{res['partition_seed']} S{res['train_seed']} done in {res['wall_time_s']:.1f}s | Macro F1: {res['macro_f1']*100:.2f}%, RECON F1: {res['recon_f1']*100:.2f}%, Honest Quar: {res['honest_quar_rate']*100:.1f}%")

    # Serialize runs.jsonl
    runs_jsonl_path = run_dir / "runs.jsonl"
    with open(runs_jsonl_path, "w") as f:
        for r in results_list:
            clean_rec = {k: v for k, v in r.items() if k not in ("telemetry", "convergence")}
            f.write(json.dumps(clean_rec) + "\n")

    # Save telemetry
    all_telemetry = []
    for r in results_list:
        if "telemetry" in r:
            all_telemetry.extend(r["telemetry"])
    telemetry_df = pd.DataFrame(all_telemetry)
    telemetry_csv_path = run_dir / "client_telemetry.csv"
    telemetry_df.to_csv(telemetry_csv_path, index=False)

    # ══════════════════════════════════════════════════════════════════════════
    # Compute Comparison Matrix
    # ══════════════════════════════════════════════════════════════════════════
    df_runs = pd.DataFrame([ {k: v for k, v in r.items() if k not in ("telemetry", "convergence")} for r in results_list ])
    
    summary_rows = []
    for m in modes_to_evaluate:
        sub = df_runs[df_runs["mode"] == m]
        if len(sub) == 0:
            continue
        macro_mean, macro_lo, macro_hi = bootstrap_ci(sub["macro_f1"].tolist())
        recon_mean, recon_lo, recon_hi = bootstrap_ci(sub["recon_f1"].tolist())
        asr_mean, asr_lo, asr_hi = bootstrap_ci(sub["asr"].tolist())
        quar_mean = sub["honest_quar_rate"].mean() * 100
        excl_mean = sub["honest_data_exclusion"].mean() * 100
        atk_quar = sub["attacker_quar_rate"].mean() * 100
        atk_prob = sub["attacker_prob_rate"].mean() * 100

        summary_rows.append({
            "Mode": m,
            "Macro-F1 (%)": f"{macro_mean*100:.2f}% [{macro_lo*100:.2f}%, {macro_hi*100:.2f}%]",
            "RECON F1 (%)": f"{recon_mean*100:.2f}% [{recon_lo*100:.2f}%, {recon_hi*100:.2f}%]",
            "ASR (%)": f"{asr_mean*100:.2f}% [{asr_lo*100:.2f}%, {asr_hi*100:.2f}%]",
            "Honest Quarantine (%)": f"{quar_mean:.1f}%",
            "Honest Data Excluded (%)": f"{excl_mean:.1f}%",
            "Attacker Quar Det (%)": f"{atk_quar:.1f}%",
            "Attacker Prob Det (%)": f"{atk_prob:.1f}%",
        })

    summary_df = pd.DataFrame(summary_rows)
    summary_csv_path = run_dir / "comparison_summary.csv"
    summary_df.to_csv(summary_csv_path, index=False)

    # Norm Z Correlation Check (Flaw 2 Resolution)
    # Check correlation between norm Z and sample count for honest clients
    honest_telem = telemetry_df[telemetry_df["is_attacker"] == 0]
    corrs = {}
    if len(honest_telem) > 0:
        rho_norm_sample, p_val = stats.spearmanr(honest_telem["norm_z"], honest_telem["sample_count"])
        corrs["norm_z_spearman_with_sample_count"] = float(rho_norm_sample)
        corrs["p_value"] = float(p_val)

    summary_json_path = run_dir / "verification_summary.json"
    with open(summary_json_path, "w") as f:
        json.dump({
            "matrix": summary_rows,
            "correlations": corrs,
            "total_wall_time_s": time.time() - t_suite_start,
        }, f, indent=2)

    print("\n" + "═" * 100)
    print("  PHASE E4 EMPIRICAL VERIFICATION BENCHMARK COMPLETE")
    print("═" * 100)
    print(summary_df.to_string(index=False))
    print("═" * 100)
    if corrs:
        print(f"  Norm Z Spearman Correlation with Sample Count: rho = {corrs['norm_z_spearman_with_sample_count']:.4f}")
    print("═" * 100 + "\n")


if __name__ == "__main__":
    main()
