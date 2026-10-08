"""
run_phase_e3_diagnosis.py — Phase E3 Diagnostic Suite (Calibration Configs, 30 Rounds).

Objectives (Pure Diagnosis; Detector Untouched):
1. Per-signal AUC for attacker vs honest (cosine, norm Z, global delta F1, every class probe impact,
   RECON-specific impact, collusion similarity), overall and support-matched.
2. Skew confound: compute client skew features (KL from global, majority share, per-class support, sample count).
   Regress each signal on skew features plus attacker indicator (variance explained by skew vs attacker beta).
   Compute Spearman rank correlations.
3. Table of which honest clients get flagged, how often, with skew features, per partition.
4. FedAvg aggregation controls:
   (a) random exclusion at D0's per-round exclusion rate
   (b) drop k largest clients
   (c) class-balanced aggregation weights
   Question: is D0's macro-F1 parity with FedAvg explained by exclusion itself?
5. Convergence: per-round test macro-F1 for clean FedAvg; rounds until within 1 point of final.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import copy
import json
import logging
import math
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
from sklearn.metrics import roc_auc_score
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset

from src.model.mlp import IDS_MLP
from src.attacks.targeted_label_flip import TargetedLabelFlipAttack
from src.experiments.harness import AttackerSelector
from src.experiments.aggregate_results import bootstrap_ci

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)


# ══════════════════════════════════════════════════════════════════════════════
# Vectorized Evaluation on GPU / CPU
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
        logits = model(X_test.to(device))
        preds = logits.argmax(dim=1)
        y_dev = y_test.to(device)

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

        # Balanced accuracy = macro recall
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


# ══════════════════════════════════════════════════════════════════════════════
# Skew Features Computation
# ══════════════════════════════════════════════════════════════════════════════

def compute_client_skew_features(partition_dir: Path, num_classes: int = 8) -> dict[int, dict[str, Any]]:
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
# Single Simulation Worker (Handles detector_log_only, D0, and controls)
# ══════════════════════════════════════════════════════════════════════════════

def run_single_simulation(
    mode: str, # "clean_detector_log", "attacked_detector_log", "clean_d0", "control_random_exclusion", "control_drop_largest", "control_class_balanced"
    partition_seed: int,
    train_seed: int,
    num_rounds: int,
    partition_dir_str: str,
    test_path_str: str,
    server_val_path_str: str,
    feature_cols: list[str],
    d0_exclusion_schedule: list[int] | None = None, # used for control_random_exclusion
    batch_size: int = 1024,
) -> dict[str, Any]:
    t0 = time.time()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    torch.backends.cudnn.benchmark = True
    torch.manual_seed(train_seed)
    np.random.seed(train_seed)

    p_dir = Path(partition_dir_str)
    partition_files = [str(p_dir / f"client_{i:02d}.parquet") for i in range(10)]

    # Load validation and test tensors
    val_df = pd.read_parquet(server_val_path_str)
    X_val = torch.from_numpy(val_df[feature_cols].to_numpy(dtype="float32").copy())
    y_val = torch.from_numpy(val_df["label"].to_numpy(dtype="int64").copy())

    test_df = pd.read_parquet(test_path_str)
    X_test = torch.from_numpy(test_df[feature_cols].to_numpy(dtype="float32").copy())
    y_test = torch.from_numpy(test_df["label"].to_numpy(dtype="int64").copy())

    # Load client data into memory
    client_dfs = [pd.read_parquet(pf) for pf in partition_files]
    client_samples = [len(df) for df in client_dfs]

    # Malicious client selection for attacked mode
    malicious_set = set()
    attacker_share = 0.0
    if "attacked" in mode:
        sel = AttackerSelector(partition_files, source_class=4)
        meta = sel.select_stratified((0.25, 0.40), num_malicious=2, seed=train_seed)
        malicious_set = set(meta["attacker_ids"])
        attacker_share = meta["source_sample_share"]

    # Attack instances
    attacks = {}
    for cid in malicious_set:
        attacks[cid] = TargetedLabelFlipAttack(
            source_class=4,
            target_class=0,
            poison_ratio=1.0,
            boost_factor=2.0,
        )

    # Initialize global model
    global_model = IDS_MLP(in_features=len(feature_cols), num_classes=8).to(device)

    # State tracking for detector
    evidence_scores = {cid: 0.0 for cid in range(10)}
    consecutive_bad = {cid: 0 for cid in range(10)}
    client_states = {cid: "TRUSTED" for cid in range(10)} # "TRUSTED", "PROBATION", "QUARANTINED"
    quarantine_rounds = [] # per-round count of quarantined clients

    telemetry_records = []
    round_convergence = []

    for r in range(1, num_rounds + 1):
        # 1. Local Training
        client_updates = []
        flat_updates = []

        for cid in range(10):
            df_c = client_dfs[cid]
            if cid in malicious_set:
                df_train = attacks[cid].poison_data(df_c, round_num=r)
            else:
                df_train = df_c

            X_tensor = torch.from_numpy(df_train[feature_cols].to_numpy(dtype="float32").copy())
            y_tensor = torch.from_numpy(df_train["label"].to_numpy(dtype="int64").copy())

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
            # Flatten floating point weights into 1D
            flat_u = torch.cat([v.flatten() for v in u.values() if torch.is_floating_point(v)])
            flat_updates.append(flat_u)

        # 2. Multi-Signal Validation (for detector_log_only and clean_d0)
        num_quarantined_this_round = 0

        # Baseline evaluation on server_val
        val_base = fast_evaluate(global_model, X_val, y_val, device)
        base_macro = val_base["macro_f1"]

        # Geometric median reference update
        stacked_flats = torch.stack(flat_updates) # shape: (10, D)
        # Coordinate median approximation for fast reference
        ref_flat = torch.median(stacked_flats, dim=0).values

        # Pairwise cosine similarities for collusion detection
        norm_flats = stacked_flats / (torch.norm(stacked_flats, dim=1, keepdim=True) + 1e-10)
        cos_matrix = torch.mm(norm_flats, norm_flats.t()).cpu().numpy()

        # Update norms and robust MAD Z-scores
        norms = [float(f.norm().item()) for f in flat_updates]
        norms_arr = np.array(norms, dtype=np.float32)
        med_norm = float(np.median(norms_arr))
        mad_norm = float(np.median(np.abs(norms_arr - med_norm)))
        norm_std = 1.4826 * mad_norm if mad_norm > 1e-6 else 1.0

        for cid in range(10):
            flat_u = flat_updates[cid]
            cos_sim = float(torch.dot(flat_u, ref_flat).item() / (flat_u.norm().item() * ref_flat.norm().item() + 1e-10))
            norm_z = (norms[cid] - med_norm) / norm_std

            # Collusion sim: max pairwise cosine to other clients
            other_cos = [cos_matrix[cid, j] for j in range(10) if j != cid]
            max_collusion_sim = float(max(other_cos)) if other_cos else 0.0

            # Candidate model evaluation on server_val
            probe_model = IDS_MLP(in_features=len(feature_cols), num_classes=8).to(device)
            probe_dict = {}
            for k, v in global_model.state_dict().items():
                if torch.is_floating_point(v):
                    probe_dict[k] = v + (client_updates[cid][k].to(device) * 0.1)
                else:
                    probe_dict[k] = v
            probe_model.load_state_dict(probe_dict)
            val_cand = fast_evaluate(probe_model, X_val, y_val, device)

            global_delta_f1 = val_cand["macro_f1"] - base_macro
            per_class_deltas = {c: val_cand[f"f1_class_{c}"] - val_base[f"f1_class_{c}"] for c in range(8)}

            # Flag checks under D0 rules
            flags = []
            if cos_sim < 0.25:
                flags.append("COSINE_DIVERGENT")
            if abs(norm_z) > 3.0:
                flags.append("NORM_EXTREME")

            for c in range(8):
                if val_base[f"f1_class_{c}"] >= 0.15 and per_class_deltas[c] < -0.025:
                    flags.append(f"DEGRADATION_CLASS_{c}")

            is_bad = 1 if len(flags) > 0 else 0

            # Evidence accumulation
            rho = 0.80
            e_prev = evidence_scores[cid]
            e_new = rho * e_prev + (1.0 - rho) * is_bad
            evidence_scores[cid] = e_new

            if is_bad:
                consecutive_bad[cid] += 1
            else:
                consecutive_bad[cid] = 0

            # State transition
            old_state = client_states[cid]
            new_state = old_state
            if e_new >= 0.70 or (old_state == "PROBATION" and consecutive_bad[cid] >= 2):
                new_state = "QUARANTINED"
            elif e_new >= 0.40:
                if old_state == "TRUSTED":
                    new_state = "PROBATION"
            client_states[cid] = new_state

            if new_state == "QUARANTINED":
                num_quarantined_this_round += 1

            # Log client round telemetry
            telemetry_records.append({
                "round": r,
                "client_id": cid,
                "partition_seed": partition_seed,
                "train_seed": train_seed,
                "mode": mode,
                "is_attacker": 1 if cid in malicious_set else 0,
                "cosine_sim": cos_sim,
                "norm_z": norm_z,
                "global_delta_f1": global_delta_f1,
                "recon_impact": per_class_deltas[4],
                "collusion_sim": max_collusion_sim,
                "evidence_score": e_new,
                "consecutive_bad": consecutive_bad[cid],
                "state": new_state,
                "flags_fired": "|".join(flags) if flags else "NONE",
                **{f"probe_impact_{c}": per_class_deltas[c] for c in range(8)},
            })

        quarantine_rounds.append(num_quarantined_this_round)

        # 3. Model Aggregation depending on mode
        active_indices = list(range(10))
        agg_weights = [client_samples[i] for i in range(10)]

        if mode == "clean_d0":
            # Exclude quarantined clients
            active_indices = [i for i in range(10) if client_states[i] != "QUARANTINED"]
            if not active_indices:
                active_indices = list(range(10))
            agg_weights = [client_samples[i] for i in active_indices]

        elif mode == "control_random_exclusion":
            # Match D0's exclusion count for this round
            k_exclude = d0_exclusion_schedule[r - 1] if d0_exclusion_schedule is not None and len(d0_exclusion_schedule) >= r else 0
            if k_exclude > 0 and k_exclude < 10:
                rng_ctrl = np.random.RandomState(train_seed + r * 500)
                excluded_cids = set(rng_ctrl.choice(range(10), size=k_exclude, replace=False))
                active_indices = [i for i in range(10) if i not in excluded_cids]
            agg_weights = [client_samples[i] for i in active_indices]

        elif mode == "control_drop_largest":
            # Exclude top 2 largest clients
            sorted_by_size = sorted(range(10), key=lambda i: client_samples[i], reverse=True)
            drop_set = set(sorted_by_size[:2])
            active_indices = [i for i in range(10) if i not in drop_set]
            agg_weights = [client_samples[i] for i in active_indices]

        elif mode == "control_class_balanced":
            # Uniform / class-balanced weights: w_i = 1 / K
            active_indices = list(range(10))
            agg_weights = [1.0 for _ in range(10)]

        # Apply aggregation update
        tot_w = sum(agg_weights)
        new_state = {}
        for k in global_model.state_dict():
            if torch.is_floating_point(global_model.state_dict()[k]):
                w_delta = sum(
                    client_updates[idx][k].to(device) * (agg_weights[i] / tot_w)
                    for i, idx in enumerate(active_indices)
                )
                new_state[k] = global_model.state_dict()[k] + w_delta
            else:
                new_state[k] = global_model.state_dict()[k]
        global_model.load_state_dict(new_state)

        # Track per-round test evaluation for convergence
        test_eval = fast_evaluate(global_model, X_test, y_test, device)
        round_convergence.append({
            "round": r,
            "macro_f1": test_eval["macro_f1"],
            "accuracy": test_eval["accuracy"],
            "balanced_accuracy": test_eval["balanced_accuracy"],
            "recon_f1": test_eval["recon_f1"],
            "asr": test_eval["asr"],
        })

    # Final test evaluation
    final_eval = fast_evaluate(global_model, X_test, y_test, device)
    wall_time = time.time() - t0

    return {
        "mode": mode,
        "partition_seed": partition_seed,
        "train_seed": train_seed,
        "num_rounds": num_rounds,
        "accuracy": final_eval["accuracy"],
        "balanced_accuracy": final_eval["balanced_accuracy"],
        "macro_f1": final_eval["macro_f1"],
        "recon_f1": final_eval["recon_f1"],
        "asr": final_eval["asr"],
        "wall_time_s": wall_time,
        "quarantine_schedule": quarantine_rounds,
        "telemetry": telemetry_records,
        "convergence": round_convergence,
    }


def _simulation_task_wrapper(arg: dict) -> dict:
    return run_single_simulation(**arg)


# ══════════════════════════════════════════════════════════════════════════════
# Statistical Diagnostic Analysis Functions
# ══════════════════════════════════════════════════════════════════════════════

def analyze_per_signal_auc(telemetry_df: pd.DataFrame, client_features: dict[int, dict[int, dict]]) -> dict:
    """Requirement 1: ROC AUC for attacker vs honest (overall and support-matched)."""
    atk_df = telemetry_df[telemetry_df["mode"] == "attacked_detector_log"].copy()

    signals = [
        ("cosine_sim", False), # lower = suspicious -> negate
        ("norm_z", True),      # higher/extreme = suspicious -> abs
        ("global_delta_f1", False), # lower = suspicious -> negate
        ("recon_impact", False),    # lower = suspicious -> negate
        ("collusion_sim", True),    # higher = suspicious
    ]
    for c in range(8):
        signals.append((f"probe_impact_{c}", False))

    auc_results = {}
    for sig_name, higher_is_suspicious in signals:
        if sig_name not in atk_df.columns:
            continue
        scores = atk_df[sig_name].values
        if not higher_is_suspicious:
            scores = -scores
        elif sig_name == "norm_z":
            scores = np.abs(scores)

        y_true = atk_df["is_attacker"].values

        # Overall AUC
        try:
            auc_overall = float(roc_auc_score(y_true, scores))
        except Exception:
            auc_overall = float("nan")

        # Support-matched AUC (for per-class probe impacts)
        auc_supp_matched = float("nan")
        if sig_name.startswith("probe_impact_") or sig_name == "recon_impact":
            cls_idx = 4 if sig_name == "recon_impact" else int(sig_name.split("_")[-1])
            # Filter honest clients to those with support >= 100
            matched_mask = []
            for _, row in atk_df.iterrows():
                if row["is_attacker"] == 1:
                    matched_mask.append(True)
                else:
                    pse = int(row["partition_seed"])
                    cid = int(row["client_id"])
                    cnt = client_features[pse][cid]["per_class_counts"][cls_idx]
                    matched_mask.append(cnt >= 100)
            matched_mask = np.array(matched_mask)
            if len(np.unique(y_true[matched_mask])) > 1:
                try:
                    auc_supp_matched = float(roc_auc_score(y_true[matched_mask], scores[matched_mask]))
                except Exception:
                    pass

        auc_results[sig_name] = {
            "overall_auc": auc_overall,
            "support_matched_auc": auc_supp_matched,
        }

    return auc_results


def analyze_skew_confound(telemetry_df: pd.DataFrame, client_features: dict[int, dict[int, dict]]) -> dict:
    """Requirement 2: Regress signals on skew features + attacker indicator; Spearman correlation."""
    # Annotate telemetry with skew features
    df = telemetry_df[telemetry_df["mode"].isin(["clean_detector_log", "attacked_detector_log"])].copy()

    df["sample_count"] = df.apply(lambda r: client_features[int(r["partition_seed"])][int(r["client_id"])]["sample_count"], axis=1)
    df["majority_share"] = df.apply(lambda r: client_features[int(r["partition_seed"])][int(r["client_id"])]["majority_share"], axis=1)
    df["kl_div"] = df.apply(lambda r: client_features[int(r["partition_seed"])][int(r["client_id"])]["kl_divergence"], axis=1)
    df["recon_support"] = df.apply(lambda r: client_features[int(r["partition_seed"])][int(r["client_id"])]["recon_support"], axis=1)

    signals = ["recon_impact", "probe_impact_6", "probe_impact_7", "cosine_sim", "norm_z", "global_delta_f1"]
    skew_cols = ["sample_count", "majority_share", "kl_div", "recon_support"]

    reg_results = {}
    spearman_results = {}

    for sig in signals:
        if sig not in df.columns:
            continue
        sub = df[[sig, "is_attacker"] + skew_cols].dropna()
        y = sub[sig].values

        # Model 1: Skew features only
        X_skew = sub[skew_cols].values
        X_skew_b = np.column_stack([np.ones(len(sub)), X_skew])
        try:
            beta_skew, _, _, _ = np.linalg.lstsq(X_skew_b, y, rcond=None)
            y_pred_skew = X_skew_b @ beta_skew
            ss_tot = np.sum((y - np.mean(y)) ** 2)
            r2_skew = 1.0 - (np.sum((y - y_pred_skew) ** 2) / (ss_tot + 1e-10))
        except Exception:
            r2_skew = 0.0

        # Model 2: Skew + attacker indicator
        X_full = sub[skew_cols + ["is_attacker"]].values
        X_full_b = np.column_stack([np.ones(len(sub)), X_full])
        try:
            beta_full, _, _, _ = np.linalg.lstsq(X_full_b, y, rcond=None)
            y_pred_full = X_full_b @ beta_full
            r2_full = 1.0 - (np.sum((y - y_pred_full) ** 2) / (ss_tot + 1e-10))
            beta_atk = float(beta_full[-1])
        except Exception:
            r2_full = 0.0
            beta_atk = 0.0

        delta_r2 = max(0.0, r2_full - r2_skew)

        reg_results[sig] = {
            "r2_skew": float(r2_skew),
            "r2_full": float(r2_full),
            "delta_r2_attacker": float(delta_r2),
            "beta_attacker": float(beta_atk),
        }

        # Spearman rank correlations
        spearman_results[sig] = {}
        for feat in skew_cols:
            rho, pval = stats.spearmanr(sub[sig].values, sub[feat].values)
            spearman_results[sig][feat] = {"rho": float(rho), "p_value": float(pval)}

    return {"regressions": reg_results, "spearman": spearman_results}


def analyze_honest_flagging(telemetry_df: pd.DataFrame, client_features: dict[int, dict[int, dict]]) -> list[dict]:
    """Requirement 3: Summary table of which honest clients get flagged, how often, with skew features."""
    clean_df = telemetry_df[telemetry_df["mode"] == "clean_detector_log"].copy()

    records = []
    for pse in [11, 12, 13]:
        for cid in range(10):
            sub = clean_df[(clean_df["partition_seed"] == pse) & (clean_df["client_id"] == cid)]
            if sub.empty:
                continue

            feats = client_features[pse][cid]
            total_rounds = len(sub)
            bad_rounds = int((sub["consecutive_bad"] > 0).sum())
            max_evidence = float(sub["evidence_score"].max())
            prob_rounds = int((sub["state"] == "PROBATION").sum())
            quar_rounds = int((sub["state"] == "QUARANTINED").sum())

            # First round quarantined
            quar_sub = sub[sub["state"] == "QUARANTINED"]
            first_quar = int(quar_sub["round"].min()) if not quar_sub.empty else None

            # Breakdown of flags fired
            flag_counts = {}
            for flags_str in sub["flags_fired"]:
                if flags_str != "NONE":
                    for f in flags_str.split("|"):
                        flag_counts[f] = flag_counts.get(f, 0) + 1

            records.append({
                "partition_seed": pse,
                "client_id": cid,
                "sample_count": feats["sample_count"],
                "majority_class": feats["majority_class"],
                "majority_share": feats["majority_share"],
                "kl_div": feats["kl_divergence"],
                "low_support_classes": feats["low_support_classes"],
                "bad_rounds": bad_rounds,
                "max_evidence": max_evidence,
                "probation_rounds": prob_rounds,
                "quarantine_rounds": quar_rounds,
                "first_quarantine_round": first_quar,
                "flag_counts": flag_counts,
            })
    return records


# ══════════════════════════════════════════════════════════════════════════════
# Main Execution Entry Point
# ══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="Run Phase E3 Diagnostic Suite")
    parser.add_argument("--rounds", type=int, default=30, help="FL rounds per simulation")
    parser.add_argument("--workers", type=int, default=4, help="Concurrent worker processes")
    parser.add_argument("--run-dir", type=str, default="results/runs/phase_e3_diagnosis")
    args = parser.parse_args()

    run_dir = Path(args.run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)

    test_path_str = "data/processed/dev/test.parquet"
    server_val_path_str = "data/processed/dev/server_val.parquet"

    test_df = pd.read_parquet(test_path_str)
    feature_cols = [c for c in test_df.columns if c not in ("label", "class_name")]

    log.info(f"Feature columns: {len(feature_cols)}, Rounds: {args.rounds}, Workers: {args.workers}")

    # Compute client skew features for calibration partitions
    client_features = {}
    for pse in [11, 12, 13]:
        p_dir = Path(f"data/partitions/dev/seed_{pse}")
        client_features[pse] = compute_client_skew_features(p_dir)

    calibration_configs = [
        (11, 1), (11, 2),
        (12, 1), (12, 2),
        (13, 1), (13, 2),
    ]

    t_suite_start = time.time()
    results_list = []
    runs_jsonl_path = run_dir / "runs.jsonl"

    # Stage 1: Run clean_d0 first to obtain the empirical D0 exclusion schedule per config
    log.info("=== STAGE 1: Executing clean_d0 simulations to obtain exclusion schedules ===")
    d0_tasks = []
    for pse, tse in calibration_configs:
        d0_tasks.append({
            "mode": "clean_d0",
            "partition_seed": pse,
            "train_seed": tse,
            "num_rounds": args.rounds,
            "partition_dir_str": f"data/partitions/dev/seed_{pse}",
            "test_path_str": test_path_str,
            "server_val_path_str": server_val_path_str,
            "feature_cols": feature_cols,
            "d0_exclusion_schedule": None,
            "batch_size": 1024,
        })

    d0_results = {}
    if args.workers > 1 and len(d0_tasks) > 1:
        with concurrent.futures.ProcessPoolExecutor(max_workers=args.workers, mp_context=mp.get_context("spawn")) as executor:
            futures = [executor.submit(_simulation_task_wrapper, t) for t in d0_tasks]
            for f in concurrent.futures.as_completed(futures):
                res = f.result()
                key = (res["partition_seed"], res["train_seed"])
                d0_results[key] = res
                results_list.append(res)
                log.info(f"[clean_d0] P{res['partition_seed']} S{res['train_seed']} done in {res['wall_time_s']:.1f}s | Macro F1 = {res['macro_f1']*100:.2f}%")
    else:
        for t in d0_tasks:
            res = run_single_simulation(**t)
            key = (res["partition_seed"], res["train_seed"])
            d0_results[key] = res
            results_list.append(res)
            log.info(f"[clean_d0] P{res['partition_seed']} S{res['train_seed']} done in {res['wall_time_s']:.1f}s | Macro F1 = {res['macro_f1']*100:.2f}%")

    # Stage 2: Build all remaining tasks (clean/attacked detector_log and aggregation controls)
    log.info("=== STAGE 2: Executing remaining diagnostic and control simulations ===")
    remaining_tasks = []
    for pse, tse in calibration_configs:
        d0_sched = d0_results[(pse, tse)]["quarantine_schedule"]
        common_kwargs = {
            "partition_seed": pse,
            "train_seed": tse,
            "num_rounds": args.rounds,
            "partition_dir_str": f"data/partitions/dev/seed_{pse}",
            "test_path_str": test_path_str,
            "server_val_path_str": server_val_path_str,
            "feature_cols": feature_cols,
            "batch_size": 1024,
        }
        # 1. Clean detector_log_only
        remaining_tasks.append({**common_kwargs, "mode": "clean_detector_log", "d0_exclusion_schedule": None})
        # 2. Attacked detector_log_only
        remaining_tasks.append({**common_kwargs, "mode": "attacked_detector_log", "d0_exclusion_schedule": None})
        # 3. Control (a): Random exclusion
        remaining_tasks.append({**common_kwargs, "mode": "control_random_exclusion", "d0_exclusion_schedule": d0_sched})
        # 4. Control (b): Drop 2 largest clients
        remaining_tasks.append({**common_kwargs, "mode": "control_drop_largest", "d0_exclusion_schedule": None})
        # 5. Control (c): Class-balanced aggregation
        remaining_tasks.append({**common_kwargs, "mode": "control_class_balanced", "d0_exclusion_schedule": None})

    if args.workers > 1 and len(remaining_tasks) > 1:
        with concurrent.futures.ProcessPoolExecutor(max_workers=args.workers, mp_context=mp.get_context("spawn")) as executor:
            futures = [executor.submit(_simulation_task_wrapper, t) for t in remaining_tasks]
            for f in concurrent.futures.as_completed(futures):
                res = f.result()
                results_list.append(res)
                log.info(f"[{res['mode']}] P{res['partition_seed']} S{res['train_seed']} done in {res['wall_time_s']:.1f}s | Macro F1 = {res['macro_f1']*100:.2f}%")
    else:
        for t in remaining_tasks:
            res = run_single_simulation(**t)
            results_list.append(res)
            log.info(f"[{res['mode']}] P{res['partition_seed']} S{res['train_seed']} done in {res['wall_time_s']:.1f}s | Macro F1 = {res['macro_f1']*100:.2f}%")

    # Serialize runs.jsonl
    with open(runs_jsonl_path, "w") as f:
        for r in results_list:
            clean_rec = {k: v for k, v in r.items() if k not in ("telemetry", "convergence")}
            f.write(json.dumps(clean_rec) + "\n")
    log.info(f"Saved {len(results_list)} simulation run records to {runs_jsonl_path}")

    # Combine all telemetry records
    all_telemetry = []
    for r in results_list:
        if "telemetry" in r:
            all_telemetry.extend(r["telemetry"])
    telemetry_df = pd.DataFrame(all_telemetry)
    telemetry_csv_path = run_dir / "client_telemetry.csv"
    telemetry_df.to_csv(telemetry_csv_path, index=False)
    log.info(f"Saved {len(telemetry_df)} round telemetry rows to {telemetry_csv_path}")

    # Execute Diagnostic Analysis
    log.info("=== STAGE 3: Computing Diagnostic Analysis & Reporting Tables ===")
    auc_data = analyze_per_signal_auc(telemetry_df, client_features)
    skew_data = analyze_skew_confound(telemetry_df, client_features)
    flag_data = analyze_honest_flagging(telemetry_df, client_features)

    # Save summary metrics
    summary_path = run_dir / "summary_metrics.json"
    with open(summary_path, "w") as f:
        json.dump({
            "auc": auc_data,
            "skew_confound": skew_data,
            "honest_flagging": flag_data,
        }, f, indent=2)
    log.info(f"Saved diagnostic summary to {summary_path}")

    print("\n" + "=" * 80)
    print("PHASE E3 DIAGNOSTIC EXECUTION COMPLETE")
    print(f"Total Wall Time: {time.time() - t_suite_start:.1f}s")
    print("=" * 80)


if __name__ == "__main__":
    main()
