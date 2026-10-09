"""
run_phase_e4_2a.py — Phase E4.2a Comprehensive Diagnosis, Controls, and Baseline Benchmark.

Covers Steps 1 through 8 of Phase E4.2a (Revised):
  Step 1: Factorial Comparability Test (Old vs New environment x D0/Fixed/FedAvg)
  Step 2: Leave-One-Out Ablation of Fixed Defense (8 variants)
  Step 3: Missing Baselines (Coordinate Median, Trimmed Mean, Krum, D2_z3, Oracle D1, Log-only)
  Step 4: Operating-Point ROC Curves (Sweeping probe degradation and probation thresholds)
  Step 5: New Signal AUCs (Head update energy, EWMA probe impact, Peer Z, Ec)
  Step 6: Oracle Detection-Delay Tolerance (Cutoff round T in {1, 3, 5, 10, 20})
  Step 7: Bimodal Outcomes Diagnosis (Partition row shares, collapse triggers)
  Step 8: Convergence Tracking and Wall-Time Reconciliation (30 and 60 rounds)
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

# Ensure project root in sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

import numpy as np
import pandas as pd
from scipy import stats
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
import yaml

from src.attacks.targeted_label_flip import TargetedLabelFlipAttack
from src.attacks.model_poisoning import ModelPoisoningAttack
from src.experiments.harness import AttackerSelector
from src.federation.median import aggregate_coordinate_median
from src.federation.trimmed_mean import aggregate_trimmed_mean
from src.federation.krum import aggregate_krum
from src.federation.trust_aggregation import aggregate_trust_class_aware
from src.model.mlp import IDS_MLP
from src.model.evaluate import evaluate
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
log = logging.getLogger("phase_e4_2a")


# ══════════════════════════════════════════════════════════════════════════════
# Fast Vectorized GPU Confusion-Matrix Evaluation
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


# ══════════════════════════════════════════════════════════════════════════════
# High-Throughput In-Memory Shared Tensor Caching
# ══════════════════════════════════════════════════════════════════════════════

_PROCESS_DATA_CACHE: dict[str, Any] = {}

def get_cached_dataset(
    partition_dir_str: str,
    test_path_str: str,
    server_val_path_str: str,
    feature_cols: list[str],
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Loads and caches datasets in worker memory to eliminate repeated disk I/O."""
    if "eval" not in _PROCESS_DATA_CACHE:
        val_df = pd.read_parquet(server_val_path_str)
        X_val = torch.from_numpy(val_df[feature_cols].to_numpy(dtype="float32").copy()).contiguous()
        y_val = torch.from_numpy(val_df["label"].to_numpy(dtype="int64").copy()).contiguous()

        test_df = pd.read_parquet(test_path_str)
        X_test = torch.from_numpy(test_df[feature_cols].to_numpy(dtype="float32").copy()).contiguous()
        y_test = torch.from_numpy(test_df["label"].to_numpy(dtype="int64").copy()).contiguous()

        _PROCESS_DATA_CACHE["eval"] = {
            "X_val": X_val,
            "y_val": y_val,
            "X_test": X_test,
            "y_test": y_test,
        }

    if partition_dir_str not in _PROCESS_DATA_CACHE:
        p_dir = Path(partition_dir_str)
        partition_files = [p_dir / f"client_{i:02d}.parquet" for i in range(10)]
        client_dfs = [pd.read_parquet(pf) for pf in partition_files]
        client_samples = [len(df) for df in client_dfs]
        client_recon = [int((df["label"] == 4).sum()) for df in client_dfs]

        client_tensors = []
        for df in client_dfs:
            X_t = torch.from_numpy(df[feature_cols].to_numpy(dtype="float32").copy()).contiguous()
            y_t = torch.from_numpy(df["label"].to_numpy(dtype="int64").copy()).contiguous()
            client_tensors.append((X_t, y_t))

        _PROCESS_DATA_CACHE[partition_dir_str] = {
            "partition_files": partition_files,
            "client_dfs": client_dfs,
            "client_tensors": client_tensors,
            "client_samples": client_samples,
            "client_recon": client_recon,
            "total_samples": sum(client_samples),
            "total_recon": sum(client_recon),
        }

    return _PROCESS_DATA_CACHE[partition_dir_str], _PROCESS_DATA_CACHE["eval"]


# ══════════════════════════════════════════════════════════════════════════════
# Core Universal Simulation Engine
# ══════════════════════════════════════════════════════════════════════════════

def run_simulation(
    config: dict[str, Any],
    partition_dir_str: str,
    test_path_str: str,
    server_val_path_str: str,
    feature_cols: list[str],
    class_names: list[str],
    batch_size: int = 1024,
    device_str: str | None = None,
) -> dict[str, Any]:
    """
    Executes a single federated learning simulation according to config.
    Config parameters:
      - run_name: descriptive name
      - step: "step1", "step2", etc.
      - partition_seed: int
      - train_seed: int
      - num_rounds: int (typically 30)
      - is_attacked: bool
      - attack_type: "targeted_label_flip" or "boosted_head_poisoning" or "none"
      - loop_env: "new_vram" or "old_dataloader"
      - val_env: "fast_val" or "old_val"
      - defense_type: "fedavg", "legacy_d0", "fixed", "fixed_e4", "median", "trimmed_mean", "krum",
                      "d2_z3", "oracle_d1", "detector_log_only", or custom ablation dict
      - oracle_cutoff_round: Optional[int] (for Step 6 delay tolerance)
      - oracle_mode: "exclude_clients" or "zero_recon_head"
      - custom_params: Optional dict of overrides (e.g. thresholds)
    """
    t0 = time.time()
    torch.set_num_threads(1)
    if device_str is not None:
        device = torch.device(device_str)
    else:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    train_seed = config["train_seed"]
    partition_seed = config["partition_seed"]
    num_rounds = config.get("num_rounds", 30)
    loop_env = config.get("loop_env", "new_vram")
    val_env = config.get("val_env", "fast_val")
    defense_type = config.get("defense_type", "fixed")
    custom_params = config.get("custom_params", {}) or {}

    torch.backends.cudnn.benchmark = True
    torch.manual_seed(train_seed)
    np.random.seed(train_seed)

    p_data, eval_data = get_cached_dataset(
        partition_dir_str, test_path_str, server_val_path_str, feature_cols
    )
    partition_files = p_data["partition_files"]
    client_dfs = p_data["client_dfs"]
    client_tensors = p_data["client_tensors"]
    client_samples = p_data["client_samples"]
    client_recon = p_data["client_recon"]
    total_samples = p_data["total_samples"]
    total_recon = p_data["total_recon"]

    X_val = eval_data["X_val"]
    y_val = eval_data["y_val"]
    val_loader = DataLoader(TensorDataset(X_val, y_val), batch_size=batch_size * 2, shuffle=False)

    X_test = eval_data["X_test"].to(device, non_blocking=True)
    y_test = eval_data["y_test"].to(device, non_blocking=True)

    is_attacked = config.get("is_attacked", False)
    attack_type = config.get("attack_type", "targeted_label_flip" if is_attacked else "none")
    malicious_set = set()
    attacks = {}
    attacker_recon_share = 0.0
    attacker_recon_counts = {}

    if is_attacked and attack_type != "none":
        selector = AttackerSelector(partition_files, source_class=4)
        strat = selector.select_stratified(
            target_band=(0.25, 0.40),
            num_malicious=2,
            seed=train_seed + partition_seed * 100,
        )
        malicious_set = set(strat["attacker_ids"])
        attacker_recon_share = strat["source_sample_share"]
        for aid in malicious_set:
            attacker_recon_counts[aid] = client_recon[aid]
            if attack_type == "targeted_label_flip":
                attacks[aid] = TargetedLabelFlipAttack(
                    source_class=4,
                    target_class=0,
                    boost_factor=2.0,
                )
            elif attack_type == "boosted_head_poisoning":
                # Clean local data, but head weights on class 4 scaled by gamma=2.0
                pass

    global_model = IDS_MLP(in_features=len(feature_cols), num_classes=8).to(device)

    # Build Trust Engine components according to defense_type & custom_params
    has_validator = defense_type in (
        "legacy_d0", "fixed", "fixed_e4", "fixed_e4_1", "d2_z3", "detector_log_only",
        "fixed_no_norm_scaling", "hybrid_median", "hybrid_trimmed"
    ) or defense_type.startswith("ablation_") or defense_type.startswith("sweep_")

    validator = None
    state_machine = None
    rep_manager = None
    evidence_tracker = None

    if has_validator:
        # Determine parameters
        is_legacy = (defense_type == "legacy_d0" or custom_params.get("legacy_d0", False))
        is_e4_init = (defense_type == "fixed_e4")
        is_c5 = defense_type in ("fixed_no_norm_scaling", "hybrid_median", "hybrid_trimmed", "detector_log_only")

        det_variant = custom_params.get("detector_variant", "D0" if is_legacy else "D2")
        d2_z = custom_params.get("d2_z_thresh", 3.0)
        mad_f = custom_params.get("mad_floor", 1e-5 if is_legacy else 0.015)
        energy_gate = custom_params.get("energy_share_gate", 0.0 if is_legacy else (0.04 if is_e4_init else 0.40))
        norm_power = custom_params.get(
            "norm_scale_power",
            0.0 if (is_legacy or custom_params.get("no_norm_scaling") or is_c5)
            else (0.50 if is_e4_init else 0.585)
        )
        probe_thresh = custom_params.get("target_class_degradation_threshold", -0.025 if (is_legacy or is_e4_init or custom_params.get("probe_thresh_0025")) else -0.05)
        probation_th = custom_params.get("probation_threshold", 0.40)
        quarantine_th = custom_params.get("quarantine_threshold", 0.70)
        warmup_r = 0 if (is_legacy or custom_params.get("no_warmup")) else custom_params.get("warmup_rounds", 5)

        use_cohort_cos = not custom_params.get("no_cohort_cosine", False)
        enable_reset = not custom_params.get("no_round6_reset", False)

        validator = UpdateValidator(
            server_val_loader=val_loader,
            class_names=class_names,
            device=device,
            detector_variant=det_variant,
            d2_z_thresh=d2_z,
            mad_floor=mad_f,
            energy_share_gate=energy_gate,
            norm_scale_power=norm_power,
            target_class_degradation_thresh=probe_thresh,
            use_cohort_cosine=use_cohort_cos,
        )

        if custom_params.get("no_cohort_cosine"):
            assert validator.use_cohort_cosine is False, "no_cohort_cosine failed to deactivate!"
        if custom_params.get("no_norm_scaling"):
            assert validator.norm_scale_power == 0.0, "no_norm_scaling failed to set norm_scale_power to 0.0!"

        if val_env == "old_val":
            def slow_eval(m_eval: nn.Module):
                res = evaluate(m_eval, val_loader, device, class_names)
                return res["macro_f1"], {cls: m["f1"] for cls, m in res["per_class"].items()}
            validator._evaluate_fast = slow_eval

        state_machine = ClientStateMachine(
            probation_threshold=probation_th,
            quarantine_threshold=quarantine_th,
            probation_consecutive_bad_threshold=2,
            warmup_rounds=warmup_r,
            enable_clean_slate=enable_reset,
        )

        if custom_params.get("no_round6_reset"):
            assert state_machine.enable_clean_slate is False, "no_round6_reset failed to deactivate!"
        if custom_params.get("no_warmup"):
            assert state_machine.warmup_rounds == 0, "no_warmup failed to set warmup_rounds to 0!"

        rep_manager = PerClassReputationManager(class_names=class_names)
        evidence_tracker = TemporalEvidenceTracker(warmup_rounds=warmup_r)

    # Pre-build GPU resident data tensors
    client_X_gpu = []
    client_y_gpu = []
    client_weights = []
    for cid in range(10):
        X_t, y_t = client_tensors[cid]
        if cid in malicious_set and attack_type == "targeted_label_flip":
            y_train = y_t.clone()
            y_train[y_train == 4] = 0
        else:
            y_train = y_t

        X_tensor = X_t.to(device, non_blocking=True)
        y_tensor = y_train.to(device, non_blocking=True)

        class_counts = torch.bincount(y_tensor, minlength=8).float()
        cw = 1.0 / (class_counts + 1.0)
        c_weights = (cw / cw.mean()).to(device, non_blocking=True)

        client_X_gpu.append(X_tensor)
        client_y_gpu.append(y_tensor)
        client_weights.append(c_weights)

    loc_model = IDS_MLP(in_features=len(feature_cols), num_classes=8).to(device)
    try:
        opt = torch.optim.Adam(
            loc_model.parameters(),
            lr=1e-3,
            weight_decay=1e-4,
            fused=(device.type == "cuda"),
        )
    except TypeError:
        opt = torch.optim.Adam(loc_model.parameters(), lr=1e-3, weight_decay=1e-4)

    telemetry_records = []
    quarantine_schedule = []
    round_convergence = []
    first_caught_round = {aid: None for aid in malicious_set}

    # Pre-allocated shuffle buffers, loss criterions, and RNG generator to eliminate per-round memory churn
    client_criterions = [nn.CrossEntropyLoss(weight=client_weights[c]) for c in range(10)]
    client_X_buf = [torch.empty_like(ct) for ct in client_X_gpu]
    client_y_buf = [torch.empty_like(ct) for ct in client_y_gpu]
    rng_gen = torch.Generator(device=device if device.type == "cuda" else None)

    for r in range(1, num_rounds + 1):
        g_state = global_model.state_dict()
        client_updates = []

        # 1. Local Training
        if loop_env == "new_vram":
            for cid in range(10):
                Xc = client_X_gpu[cid]
                yc = client_y_gpu[cid]
                crit = client_criterions[cid]
                N = Xc.shape[0]

                with torch.no_grad():
                    for p_loc, p_glob in zip(loc_model.parameters(), global_model.parameters()):
                        p_loc.copy_(p_glob)
                opt.state.clear()

                rng_gen.manual_seed(train_seed + r * 1000 + cid)
                perm = torch.randperm(N, generator=rng_gen, device=device)
                torch.index_select(Xc, 0, perm, out=client_X_buf[cid])
                torch.index_select(yc, 0, perm, out=client_y_buf[cid])
                Xc_shuff = client_X_buf[cid]
                yc_shuff = client_y_buf[cid]

                loc_model.train()
                num_batches = (N // batch_size) if N > batch_size else 1
                step_size = batch_size if N > batch_size else N
                for b in range(num_batches):
                    sb = b * step_size
                    eb = sb + step_size
                    opt.zero_grad(set_to_none=True)
                    crit(loc_model(Xc_shuff[sb:eb]), yc_shuff[sb:eb]).backward()
                    opt.step()

                u = {}
                with torch.no_grad():
                    for (k, p_loc), p_glob in zip(loc_model.named_parameters(), global_model.parameters()):
                        u[k] = p_loc - p_glob

                if cid in malicious_set:
                    if attack_type == "targeted_label_flip":
                        u = attacks[cid].poison_update(u, round_num=r)
                    elif attack_type == "boosted_head_poisoning":
                        if "head.weight" in u:
                            u["head.weight"][4] = u["head.weight"][4] * 2.0

                client_updates.append(u)

        else: # old_dataloader loop
            for cid in range(10):
                df_c = client_dfs[cid]
                if cid in malicious_set and attack_type == "targeted_label_flip":
                    df_train = attacks[cid].poison_data(df_c, round_num=r)
                else:
                    df_train = df_c

                Xt = torch.from_numpy(df_train[feature_cols].to_numpy(dtype="float32").copy())
                yt = torch.from_numpy(df_train["label"].to_numpy(dtype="int64").copy())
                cc = torch.bincount(yt, minlength=8).float()
                cw = 1.0 / (cc + 1.0)
                class_weights = (cw / cw.mean()).to(device)

                dataset = TensorDataset(Xt, yt)
                gen = torch.Generator().manual_seed(train_seed + r * 1000 + cid)
                loader = DataLoader(
                    dataset,
                    batch_size=batch_size,
                    shuffle=True,
                    drop_last=(len(dataset) > batch_size),
                    generator=gen,
                    pin_memory=(device.type == "cuda"),
                )

                loc_m = IDS_MLP(in_features=len(feature_cols), num_classes=8).to(device)
                loc_m.load_state_dict(global_model.state_dict())
                opt = torch.optim.Adam(loc_m.parameters(), lr=1e-3, weight_decay=1e-4)
                crit = nn.CrossEntropyLoss(weight=class_weights)

                loc_m.train()
                for X_b, y_b in loader:
                    X_b, y_b = X_b.to(device, non_blocking=True), y_b.to(device, non_blocking=True)
                    opt.zero_grad(set_to_none=True)
                    crit(loc_m(X_b), y_b).backward()
                    opt.step()

                u = {}
                for k, v in global_model.state_dict().items():
                    if torch.is_floating_point(v):
                        u[k] = loc_m.state_dict()[k] - v
                    else:
                        u[k] = loc_m.state_dict()[k]

                if cid in malicious_set and attack_type == "targeted_label_flip":
                    u = attacks[cid].poison_update(u, round_num=r)

                client_updates.append(u)

        # 2. Validation & Trust Engine (if active)
        state_factors = {cid: 1.0 for cid in range(10)}
        num_quarantined_this_round = 0

        if has_validator:
            sample_counts_arg = None if (is_legacy or custom_params.get("no_norm_scaling")) else client_samples
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

                # Round 6 clean slate check if not disabled
                if not custom_params.get("no_round6_reset", False):
                    pass # state_machine internally applies clean slate if enabled

                new_state, changed, reason = state_machine.update_state(cid, ev_rec, r)
                sf = state_machine.get_state_factor(cid, ev_rec.evidence_score)
                state_factors[cid] = sf

                if new_state == ClientState.QUARANTINED:
                    num_quarantined_this_round += 1
                    if cid in malicious_set and first_caught_round[cid] is None:
                        first_caught_round[cid] = r

                # Compute per-class head energy
                hw = client_updates[cid].get("head.weight")
                recon_head_energy = 0.0
                if hw is not None and hw.ndim == 2:
                    row_sq = torch.sum(hw.float() ** 2, dim=1)
                    recon_head_energy = float(torch.sqrt(row_sq[4] + 1e-12) / (torch.norm(torch.sqrt(row_sq + 1e-12)) + 1e-8))

                telemetry_records.append({
                    "round": r,
                    "client_id": cid,
                    "partition_seed": partition_seed,
                    "train_seed": train_seed,
                    "config_name": config.get("run_name", "sim"),
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
        # Oracle Cutoff handling for Step 6:
        cutoff_T = config.get("oracle_cutoff_round", None)
        oracle_mode = config.get("oracle_mode", "exclude_clients")

        if cutoff_T is not None and r >= cutoff_T:
            if oracle_mode == "exclude_clients":
                # Exclude true attackers from aggregation
                survivor_cids = [i for i in range(10) if i not in malicious_set]
                tot_w = sum(client_samples[i] for i in survivor_cids)
                new_state_dict = {}
                for k, v in global_model.state_dict().items():
                    if torch.is_floating_point(v):
                        agg_delta = sum(client_updates[i][k].to(device) * (client_samples[i] / tot_w) for i in survivor_cids)
                        new_state_dict[k] = v + agg_delta
                    else:
                        new_state_dict[k] = v
                global_model.load_state_dict(new_state_dict)

            elif oracle_mode == "zero_recon_head":
                # Zero out attackers' RECON head slice (index 4)
                for aid in malicious_set:
                    if "head.weight" in client_updates[aid]:
                        client_updates[aid]["head.weight"][4] = 0.0
                    if "head.bias" in client_updates[aid]:
                        client_updates[aid]["head.bias"][4] = 0.0
                tot_w = sum(client_samples)
                new_state_dict = {}
                for k, v in global_model.state_dict().items():
                    if torch.is_floating_point(v):
                        agg_delta = sum(client_updates[i][k].to(device) * (client_samples[i] / tot_w) for i in range(10))
                        new_state_dict[k] = v + agg_delta
                    else:
                        new_state_dict[k] = v
                global_model.load_state_dict(new_state_dict)

        elif defense_type in ("fedavg", "detector_log_only"):
            tot_w = sum(client_samples)
            new_state_dict = {}
            for k, v in global_model.state_dict().items():
                if torch.is_floating_point(v):
                    agg_delta = sum(client_updates[i][k].to(device) * (client_samples[i] / tot_w) for i in range(10))
                    new_state_dict[k] = v + agg_delta
                else:
                    new_state_dict[k] = v
            global_model.load_state_dict(new_state_dict)

        elif defense_type == "legacy_d0":
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

        elif defense_type == "coordinate_median":
            new_state, _ = aggregate_coordinate_median(client_updates, global_model.state_dict())
            global_model.load_state_dict(new_state)

        elif defense_type == "hybrid_median":
            active_cids = [i for i in range(10) if state_factors[i] > 0.0]
            if not active_cids:
                active_cids = list(range(10))
            active_updates = [client_updates[i] for i in active_cids]
            new_state, _ = aggregate_coordinate_median(active_updates, global_model.state_dict())
            global_model.load_state_dict(new_state)

        elif defense_type == "trimmed_mean":
            new_state, _ = aggregate_trimmed_mean(client_updates, global_model.state_dict(), beta=0.20)
            global_model.load_state_dict(new_state)

        elif defense_type == "hybrid_trimmed":
            active_cids = [i for i in range(10) if state_factors[i] > 0.0]
            if not active_cids:
                active_cids = list(range(10))
            active_updates = [client_updates[i] for i in active_cids]
            b = 0.20 if len(active_updates) >= 5 else 0.10
            new_state, _ = aggregate_trimmed_mean(active_updates, global_model.state_dict(), beta=b)
            global_model.load_state_dict(new_state)

        elif defense_type == "krum":
            new_state, _ = aggregate_krum(client_updates, global_model.state_dict(), f=2, m=1)
            global_model.load_state_dict(new_state)

        elif defense_type == "oracle_d1":
            # Completely excludes attackers
            honest_cids = [i for i in range(10) if i not in malicious_set]
            tot_w = sum(client_samples[i] for i in honest_cids)
            new_state_dict = {}
            for k, v in global_model.state_dict().items():
                if torch.is_floating_point(v):
                    agg_delta = sum(client_updates[i][k].to(device) * (client_samples[i] / tot_w) for i in honest_cids)
                    new_state_dict[k] = v + agg_delta
                else:
                    new_state_dict[k] = v
            global_model.load_state_dict(new_state_dict)

        else:
            # Fixed Defense, C5 (fixed_no_norm_scaling), or Ablation
            use_hs = not custom_params.get("no_head_salience", False)
            agg_global, _ = aggregate_trust_class_aware(
                global_model=global_model,
                updates=client_updates,
                sample_counts=client_samples,
                client_ids=list(range(10)),
                reputation_table=rep_manager.reputation_table if rep_manager else None,
                state_factors=state_factors,
                class_names=class_names,
                trust_config={"trust": {"aggregation": {"use_head_salience": use_hs, "head_weight_power": 0.5}}},
            )
            global_model.load_state_dict(agg_global)

        # Track round convergence (every round for Step 4, Step 8, and Phase E4.2b operational curves)
        track_all = config.get("track_every_round", False) or config.get("step") in ("step4", "step8", "phase_e4_2b")
        if track_all or r == num_rounds:
            test_eval = fast_evaluate(global_model, X_test, y_test, device)
            round_convergence.append({
                "round": r,
                "macro_f1": test_eval["macro_f1"],
                "balanced_accuracy": test_eval["balanced_accuracy"],
                "accuracy": test_eval["accuracy"],
                "recon_f1": test_eval["recon_f1"],
                "asr": test_eval["asr"],
            })

    wall_time = time.time() - t0
    final_eval = round_convergence[-1] if round_convergence else fast_evaluate(global_model, X_test, y_test, device)

    # Post-run metrics
    if has_validator:
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
        "run_name": config.get("run_name", "sim"),
        "step": config.get("step", "general"),
        "defense_type": defense_type,
        "partition_seed": partition_seed,
        "train_seed": train_seed,
        "is_attacked": is_attacked,
        "attack_type": attack_type,
        "attacker_recon_share": attacker_recon_share,
        "attacker_recon_counts": attacker_recon_counts,
        "first_caught_round": first_caught_round,
        "num_rounds": num_rounds,
        "macro_f1": final_eval["macro_f1"],
        "balanced_accuracy": final_eval["balanced_accuracy"],
        "accuracy": final_eval["accuracy"],
        "recon_f1": final_eval["recon_f1"],
        "asr": final_eval["asr"],
        "honest_quar_rate": honest_quar_rate,
        "honest_data_exclusion": honest_data_exclusion,
        "quarantined_honest_clients": honest_quars,
        "attacker_quar_rate": atk_quar_rate,
        "attacker_prob_rate": atk_prob_rate,
        "quarantine_schedule": quarantine_schedule,
        "round_convergence": round_convergence,
        "telemetry_records": telemetry_records,
        "wall_time_s": wall_time,
    }


# ══════════════════════════════════════════════════════════════════════════════
# Experiment Suite Definitions
# ══════════════════════════════════════════════════════════════════════════════

def build_step1_configs() -> list[dict[str, Any]]:
    """Step 1: 2 x 3 design + FedAvg across 6 calibration configs (clean and attacked)."""
    configs = []
    # Loop and Validator combinations (2x3 design)
    envs = [
        ("old_env", "old_dataloader", "old_val"),
        ("new_env", "new_vram", "fast_val"),
    ]
    detectors = ["fedavg", "legacy_d0", "fixed_e4", "fixed_e4_1"]
    seeds = [(p, s) for p in (11, 12, 13) for s in (1, 2)]

    for env_name, l_env, v_env in envs:
        for det in detectors:
            for is_atk in (False, True):
                for p_seed, t_seed in seeds:
                    configs.append({
                        "run_name": f"step1_{env_name}_{det}_{'atk' if is_atk else 'clean'}_p{p_seed}_s{t_seed}",
                        "step": "step1",
                        "partition_seed": p_seed,
                        "train_seed": t_seed,
                        "num_rounds": 30,
                        "is_attacked": is_atk,
                        "attack_type": "targeted_label_flip" if is_atk else "none",
                        "loop_env": l_env,
                        "val_env": v_env,
                        "defense_type": det,
                    })
    return configs


def build_step2_configs() -> list[dict[str, Any]]:
    """Step 2: Leave-one-out ablation of the Fixed defense."""
    ablations = [
        ("fixed_baseline", {}),
        ("no_head_salience", {"no_head_salience": True}),
        ("no_norm_scaling", {"no_norm_scaling": True}),
        ("no_cohort_cosine", {"no_cohort_cosine": True}),
        ("no_warmup", {"no_warmup": True}),
        ("probation_040", {"probation_threshold": 0.40}),
        ("probe_thresh_0025", {"probe_thresh_0025": True}),
        ("no_round6_reset", {"no_round6_reset": True}),
    ]
    seeds = [(p, s) for p in (11, 12, 13) for s in (1, 2)]
    configs = []

    for abl_name, c_params in ablations:
        for is_atk in (False, True):
            for p_seed, t_seed in seeds:
                configs.append({
                    "run_name": f"step2_{abl_name}_{'atk' if is_atk else 'clean'}_p{p_seed}_s{t_seed}",
                    "step": "step2",
                    "partition_seed": p_seed,
                    "train_seed": t_seed,
                    "num_rounds": 30,
                    "is_attacked": is_atk,
                    "attack_type": "targeted_label_flip" if is_atk else "none",
                    "loop_env": "new_vram",
                    "val_env": "fast_val",
                    "defense_type": f"ablation_{abl_name}",
                    "custom_params": c_params,
                })
    return configs


def build_step3_configs() -> list[dict[str, Any]]:
    """Step 3: Missing Baselines under potent attack & clean."""
    baselines = [
        "coordinate_median",
        "trimmed_mean",
        "krum",
        "d2_z3",
        "oracle_d1",
        "detector_log_only",
        "fedavg",
        "legacy_d0",
        "fixed",
    ]
    seeds = [(p, s) for p in (11, 12, 13) for s in (1, 2)]
    configs = []

    for base in baselines:
        for is_atk in (False, True):
            for p_seed, t_seed in seeds:
                configs.append({
                    "run_name": f"step3_{base}_{'atk' if is_atk else 'clean'}_p{p_seed}_s{t_seed}",
                    "step": "step3",
                    "partition_seed": p_seed,
                    "train_seed": t_seed,
                    "num_rounds": 30,
                    "is_attacked": is_atk,
                    "attack_type": "targeted_label_flip" if is_atk else "none",
                    "loop_env": "new_vram",
                    "val_env": "fast_val",
                    "defense_type": base,
                })
    return configs


def build_step4_configs() -> list[dict[str, Any]]:
    """Step 4: Operating-point sweeps for D0 and Fixed."""
    probe_thresholds = [-0.015, -0.025, -0.05, -0.08]
    probation_thresholds = [0.40, 0.50, 0.60]
    seeds = [(p, s) for p in (11, 12, 13) for s in (1, 2)]
    configs = []

    for det in ("legacy_d0", "fixed"):
        for probe_th in probe_thresholds:
            for prob_th in probation_thresholds:
                for is_atk in (False, True):
                    for p_seed, t_seed in seeds:
                        configs.append({
                            "run_name": f"step4_roc_{det}_probe{abs(probe_th):.3f}_prob{prob_th:.2f}_{'atk' if is_atk else 'clean'}_p{p_seed}_s{t_seed}",
                            "step": "step4",
                            "partition_seed": p_seed,
                            "train_seed": t_seed,
                            "num_rounds": 30,
                            "is_attacked": is_atk,
                            "attack_type": "targeted_label_flip" if is_atk else "none",
                            "loop_env": "new_vram",
                            "val_env": "fast_val",
                            "defense_type": f"sweep_{det}",
                            "custom_params": {
                                "legacy_d0": (det == "legacy_d0"),
                                "target_class_degradation_threshold": probe_th,
                                "probation_threshold": prob_th,
                            },
                        })
    return configs


def build_step5_configs() -> list[dict[str, Any]]:
    """Step 5: Signal evaluation using detector_log_only + boosted head poisoning."""
    seeds = [(p, s) for p in (11, 12, 13) for s in (1, 2)]
    configs = []

    # 1. Targeted Label Flip with Log Only
    for p_seed, t_seed in seeds:
        configs.append({
            "run_name": f"step5_logonly_labelflip_p{p_seed}_s{t_seed}",
            "step": "step5",
            "partition_seed": p_seed,
            "train_seed": t_seed,
            "num_rounds": 30,
            "is_attacked": True,
            "attack_type": "targeted_label_flip",
            "loop_env": "new_vram",
            "val_env": "fast_val",
            "defense_type": "detector_log_only",
        })

    # 2. Boosted Head Poisoning (gamma=2.0) with Log Only
    for p_seed, t_seed in seeds:
        configs.append({
            "run_name": f"step5_logonly_headboost_p{p_seed}_s{t_seed}",
            "step": "step5",
            "partition_seed": p_seed,
            "train_seed": t_seed,
            "num_rounds": 30,
            "is_attacked": True,
            "attack_type": "boosted_head_poisoning",
            "loop_env": "new_vram",
            "val_env": "fast_val",
            "defense_type": "detector_log_only",
        })
    return configs


def build_step6_configs() -> list[dict[str, Any]]:
    """Step 6: Oracle Detection-Delay Tolerance sweep."""
    T_cutoffs = [1, 3, 5, 10, 20]
    oracle_modes = ["exclude_clients", "zero_recon_head"]
    seeds = [(p, s) for p in (11, 12, 13) for s in (1, 2)]
    configs = []

    for T in T_cutoffs:
        for mode in oracle_modes:
            for p_seed, t_seed in seeds:
                configs.append({
                    "run_name": f"step6_delay_{mode}_T{T}_p{p_seed}_s{t_seed}",
                    "step": "step6",
                    "partition_seed": p_seed,
                    "train_seed": t_seed,
                    "num_rounds": 30,
                    "is_attacked": True,
                    "attack_type": "targeted_label_flip",
                    "loop_env": "new_vram",
                    "val_env": "fast_val",
                    "defense_type": "fedavg",
                    "oracle_cutoff_round": T,
                    "oracle_mode": mode,
                })
    return configs


def build_step8_configs() -> list[dict[str, Any]]:
    """Step 8: 60-round convergence and timing run."""
    configs = [
        {
            "run_name": "step8_convergence_fedavg_60r",
            "step": "step8",
            "partition_seed": 11,
            "train_seed": 1,
            "num_rounds": 60,
            "is_attacked": True,
            "attack_type": "targeted_label_flip",
            "loop_env": "new_vram",
            "val_env": "fast_val",
            "defense_type": "fedavg",
        },
        {
            "run_name": "step8_convergence_fixed_60r",
            "step": "step8",
            "partition_seed": 11,
            "train_seed": 1,
            "num_rounds": 60,
            "is_attacked": True,
            "attack_type": "targeted_label_flip",
            "loop_env": "new_vram",
            "val_env": "fast_val",
            "defense_type": "fixed",
        },
    ]
    return configs


# ══════════════════════════════════════════════════════════════════════════════
# Main Orchestration and Multiprocessing Worker Pool
# ══════════════════════════════════════════════════════════════════════════════

def _sim_worker(args: tuple) -> dict[str, Any]:
    torch.set_num_threads(1)
    if len(args) == 8:
        cfg, p_dir, test_p, val_p, feats, classes, bs, dev_str = args
        return run_simulation(cfg, p_dir, test_p, val_p, feats, classes, bs, device_str=dev_str)
    else:
        cfg, p_dir, test_p, val_p, feats, classes, bs = args
        return run_simulation(cfg, p_dir, test_p, val_p, feats, classes, bs)


def main():
    parser = argparse.ArgumentParser(description="Phase E4.2a Benchmark Harness")
    parser.add_argument("--steps", type=str, default="all", help="Comma-separated steps to run (e.g. '1,2,3' or 'all')")
    parser.add_argument("--workers", type=int, default=4, help="Parallel worker processes")
    parser.add_argument("--rounds", type=int, default=30, help="FL rounds per simulation")
    parser.add_argument("--output-dir", type=str, default="results/runs/phase_e4_2a", help="Output directory")
    args = parser.parse_args()

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Locate dataset files
    test_path = Path("data/processed/dev/test.parquet")
    server_val_path = Path("data/processed/dev/server_val.parquet")

    if not test_path.exists() or not server_val_path.exists():
        log.error(f"Required datasets not found at {test_path} or {server_val_path}")
        sys.exit(1)

    test_df = pd.read_parquet(test_path)
    feature_cols = [c for c in test_df.columns if c not in ("label", "class_name")]

    with open("configs/label_mapping.yaml") as f:
        lm = yaml.safe_load(f)
    class_names = [lm["idx_to_class"][i] for i in range(len(lm["idx_to_class"]))]

    # Detect multi-GPU acceleration capabilities
    num_gpus = torch.cuda.device_count()
    if num_gpus > 0:
        gpu_names = [torch.cuda.get_device_name(i) for i in range(num_gpus)]
        log.info(f"Detected {num_gpus} CUDA GPU devices: {gpu_names}")
    else:
        log.info("No CUDA GPU detected; executing on CPU.")

    if num_gpus >= 2 and args.workers <= 8:
        effective_workers = min(12, 6 * num_gpus)
        log.info(f"Multi-GPU detected ({num_gpus} GPUs). Scaling worker pool from {args.workers} to {effective_workers} processes ({effective_workers // num_gpus} per GPU).")
    else:
        effective_workers = args.workers

    # Gather requested experiment configs
    selected_steps = [s.strip() for s in args.steps.split(",")] if args.steps != "all" else ["1", "2", "3", "4", "5", "6", "8"]
    all_configs = []

    if "1" in selected_steps or "all" in args.steps:
        all_configs.extend(build_step1_configs())
    if "2" in selected_steps or "all" in args.steps:
        all_configs.extend(build_step2_configs())
    if "3" in selected_steps or "all" in args.steps:
        all_configs.extend(build_step3_configs())
    if "4" in selected_steps or "all" in args.steps:
        all_configs.extend(build_step4_configs())
    if "5" in selected_steps or "all" in args.steps:
        all_configs.extend(build_step5_configs())
    if "6" in selected_steps or "all" in args.steps:
        all_configs.extend(build_step6_configs())
    if "8" in selected_steps or "all" in args.steps:
        all_configs.extend(build_step8_configs())

    log.info(f"Loaded {len(all_configs)} simulations to execute across steps: {selected_steps}")

    worker_args = [
        (
            cfg,
            f"data/partitions/dev/seed_{cfg['partition_seed']}",
            str(test_path),
            str(server_val_path),
            feature_cols,
            class_names,
            1024,
            f"cuda:{i % num_gpus}" if (torch.cuda.is_available() and num_gpus > 0) else "cpu",
        )
        for i, cfg in enumerate(all_configs)
    ]

    runs_file = out_dir / "runs.jsonl"
    telemetry_file = out_dir / "client_telemetry.csv"

    existing_run_names = set()
    if runs_file.exists():
        try:
            with open(runs_file, "r") as rf:
                for line in rf:
                    line_s = line.strip()
                    if line_s:
                        r_data = json.loads(line_s)
                        if "run_name" in r_data:
                            existing_run_names.add(r_data["run_name"])
            log.info(f"Found {len(existing_run_names)} existing runs in {runs_file}. Resuming remaining tasks...")
        except Exception as e:
            log.warning(f"Could not parse existing runs.jsonl: {e}")

    worker_args = [arg for arg in worker_args if arg[0]["run_name"] not in existing_run_names]
    log.info(f"{len(worker_args)} simulations remaining to execute out of {len(all_configs)} planned.")

    start_t = time.time()
    completed_runs = []
    all_telemetry = []

    # Execute in multiprocessing worker pool
    if worker_args:
        ctx = mp.get_context("spawn")
        with ctx.Pool(processes=effective_workers) as pool:
            for i, res in enumerate(pool.imap_unordered(_sim_worker, worker_args), 1):
                completed_runs.append(res)
                # Log progress
                log.info(
                    f"[{i}/{len(worker_args)}] Finished {res['run_name']} in {res['wall_time_s']:.1f}s | "
                    f"Macro-F1: {res['macro_f1']*100:.2f}%, RECON-F1: {res['recon_f1']*100:.2f}%, "
                    f"ASR: {res['asr']*100:.2f}%, HQ: {res['honest_quar_rate']*100:.1f}%"
                )

                # Resumable persistence: append run record
                run_rec = {k: v for k, v in res.items() if k not in ("telemetry_records", "round_convergence")}
                with open(runs_file, "a") as rf:
                    rf.write(json.dumps(run_rec) + "\n")

                if res.get("telemetry_records"):
                    all_telemetry.extend(res["telemetry_records"])
    else:
        log.info("All planned simulations are already completed!")

    # Write out telemetry CSV
    if all_telemetry:
        tdf = pd.DataFrame(all_telemetry)
        tdf.to_csv(telemetry_file, index=False)
        log.info(f"Persisted {len(tdf)} telemetry records to {telemetry_file}")

    total_wall_s = time.time() - start_t
    log.info(f"All {len(completed_runs)} simulations complete in {total_wall_s:.1f}s!")

    # Write overall execution summary
    summary_path = out_dir / "summary_e4_2a.json"
    with open(summary_path, "w") as sf:
        json.dump({
            "total_simulations": len(completed_runs),
            "total_wall_time_s": total_wall_s,
            "steps_executed": selected_steps,
            "workers": args.workers,
        }, sf, indent=2)


if __name__ == "__main__":
    main()
