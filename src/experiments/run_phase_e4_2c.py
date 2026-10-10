"""
src/experiments/run_phase_e4_2c.py — Master Benchmark Runner for Phase E4.2c.

Covers:
  - Hash assertion for frozen candidates C0 through C9 in configs/candidates/*.yaml
  - Step B: Valid-Validator References on 15 configs (clean & attacked, 30 rounds):
      legacy_d0, d2_z3, fixed_e4 (E4 design: p=0.50, gate=0.04, probe=-0.025, no clean slate)
  - Step D: Mechanism Checks:
      D1: C5b (norm_z removed entirely) on 15 configs clean & attacked + gamma=1 stress test
      D2: Quarantine-then-collapse weight and reputation analysis on P11_S1 and P12_S1 (C4 vs Oracle T=10)
      D3: Factorial 2x2 isolation rerun on P11_S1, P12_S1, P13_S1 (old/new loop x old/fast validator)
  - Step C: Stress Tests of frozen candidates C0, C1, C2, C5, C7, legacy_d0 (15 configs):
      (i) targeted flip with boost gamma=1 (no update inflation)
      (ii) adaptive_norm_clip (norm-matched to median honest norm)
      (iii) adaptive_cosine_mimic (blended with honest mean reference, norm-matched)
      (iv) boosted_head_poisoning (clean local data, RECON head scaled by 2.0)
      (v) attacker RECON share 5-15% (Band 1)
      (vi) 3 attackers (30% malicious fraction)
"""
from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import logging
import os
from pathlib import Path
import sys
import time
from typing import Any

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.attacks.adaptive_cosine_mimic import AdaptiveCosineMimicAttack
from src.attacks.adaptive_norm_clip import AdaptiveNormClipAttack
from src.attacks.targeted_label_flip import TargetedLabelFlipAttack
from src.experiments.harness import AttackerSelector
from src.federation.krum import aggregate_krum
from src.federation.median import aggregate_coordinate_median
from src.federation.trimmed_mean import aggregate_trimmed_mean
from src.federation.trust_aggregation import aggregate_trust_class_aware
from src.model.evaluate import evaluate
from src.model.mlp import IDS_MLP
from src.trust.evidence import TemporalEvidenceTracker
from src.trust.reputation import PerClassReputationManager
from src.trust.state_machine import ClientState, ClientStateMachine
from src.trust.validator import UpdateValidator, ValidationResult

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("e4_2c_runner")

FROZEN_CANDIDATE_HASHES = {
    "C0_fedavg": "b15e9bac0c140f17eedf1fddffb2ac0140615eacc1bb37bc1c44ba5d9ab7dd92",
    "C1_median": "60a9007b0c171c6cb7b46b5b1c1ec96609728f0f0389cbe3502230e6001fa498",
    "C2_krum": "d003d673c04ccf150b922936e3bdfe3db366d9cd814269dd9eaf2a92519c7180",
    "C3_trimmed_mean": "557aa463896787ad55fb0697a4acfaf86148e5d52777b64372e1fa663e321d99",
    "C4_fixed_e4_1": "bbbaa5828ad96e8969af3041ecd8afe7b68666352f123477af4fec4da7bc79dd",
    "C5_fixed_no_norm_scaling": "2961a123a2e42b79e76bacfd4806e456bc722f0dccae189023464d5868269b2a",
    "C6_oracle_d1": "ae8bfaca18b713fb44808cefa9f5227209ebd46524a3a5211f709d1ddc6e7ff0",
    "C7_hybrid_median": "6c31c15a72ccd274350d8b10b49f62ca6415843cd0422f2ea5eaae2f8aef93fe",
    "C8_hybrid_trimmed": "e20d7459311c14eaa3b9935ca5295aec8cd653a6687de4225754e897e69b30f8",
    "C9_detector_log_only": "0d3d23f4b62eb259efeb59ebb5040d5fbbec6b8f78967fba9f5c774aa5cd93ba",
}


def assert_candidate_hashes():
    cand_dir = Path("configs/candidates")
    for name, expected in FROZEN_CANDIDATE_HASHES.items():
        file_path = cand_dir / f"{name}.yaml"
        assert file_path.exists(), f"Missing frozen candidate config: {file_path}"
        actual = hashlib.sha256(file_path.read_bytes()).hexdigest()
        assert actual == expected, (
            f"FROZEN CONFIG INTEGRITY VIOLATION for {name}: Expected {expected}, got {actual}!"
        )
    logger.info("Assertion passed: All 10 candidate configs are verified frozen and untampered.")


# ──────────────────────────────────────────────────────────────────────────────
# In-Memory Cache
# ──────────────────────────────────────────────────────────────────────────────
_PROCESS_DATA_CACHE: dict[str, Any] = {}


def get_cached_dataset(
    partition_dir_str: str,
    test_path_str: str,
    server_val_path_str: str,
    feature_cols: list[str],
) -> tuple[dict[str, Any], dict[str, Any]]:
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


def fast_evaluate(
    model: nn.Module,
    X_test_gpu: torch.Tensor,
    y_test_gpu: torch.Tensor,
    device: torch.device,
) -> dict[str, float]:
    model.eval()
    with torch.no_grad():
        logits = model(X_test_gpu)
        preds = torch.argmax(logits, dim=1)

    conf = torch.bincount(y_test_gpu * 8 + preds, minlength=64).reshape(8, 8).float()
    diag = torch.diag(conf)
    col_sum = conf.sum(dim=0)  # TP + FP
    row_sum = conf.sum(dim=1)  # TP + FN

    prec = torch.where(col_sum > 0, diag / col_sum, torch.zeros_like(diag))
    rec = torch.where(row_sum > 0, diag / row_sum, torch.zeros_like(diag))
    denom = prec + rec
    f1s_gpu = torch.where(denom > 0, (2.0 * prec * rec) / denom, torch.zeros_like(diag))

    macro_f1 = float(f1s_gpu.mean().item())
    bal_acc = float(rec.mean().item())
    acc = float((diag.sum() / conf.sum()).item())
    recon_f1 = float(f1s_gpu[4].item())

    recon_total = row_sum[4].item()
    if recon_total > 0:
        asr = float((conf[4, 0] / recon_total).item())
    else:
        asr = 0.0

    return {
        "macro_f1": macro_f1,
        "balanced_accuracy": bal_acc,
        "accuracy": acc,
        "recon_f1": recon_f1,
        "asr": asr,
    }


# ──────────────────────────────────────────────────────────────────────────────
# Universal Simulation Function for Phase E4.2c
# ──────────────────────────────────────────────────────────────────────────────

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

    X_val = eval_data["X_val"]
    y_val = eval_data["y_val"]
    val_loader = DataLoader(TensorDataset(X_val, y_val), batch_size=batch_size * 2, shuffle=False)

    X_test = eval_data["X_test"].to(device, non_blocking=True)
    y_test = eval_data["y_test"].to(device, non_blocking=True)

    is_attacked = config.get("is_attacked", False)
    attack_type = config.get("attack_type", "targeted_label_flip" if is_attacked else "none")
    num_malicious = config.get("num_malicious", 2)
    target_band = config.get("target_band", (0.25, 0.40))
    boost_factor = config.get("boost_factor", 2.0)

    malicious_set = set()
    attacks = {}
    attacker_recon_share = 0.0
    attacker_recon_counts = {}

    if is_attacked and attack_type != "none":
        selector = AttackerSelector(partition_files, source_class=4)
        strat = selector.select_stratified(
            target_band=target_band,
            num_malicious=num_malicious,
            seed=train_seed + partition_seed * 100,
        )
        malicious_set = set(strat["attacker_ids"])
        attacker_recon_share = strat["source_sample_share"]
        for aid in malicious_set:
            attacker_recon_counts[aid] = client_recon[aid]
            if attack_type in ("targeted_label_flip", "adaptive_norm_clip", "adaptive_cosine_mimic"):
                attacks[aid] = TargetedLabelFlipAttack(
                    source_class=4,
                    target_class=0,
                    boost_factor=boost_factor,
                )

    global_model = IDS_MLP(in_features=len(feature_cols), num_classes=8).to(device)

    # Trust Engine setup
    has_validator = defense_type in (
        "legacy_d0", "fixed", "fixed_e4", "fixed_e4_1", "d2_z3", "detector_log_only",
        "fixed_no_norm_scaling", "c5b_no_norm_z", "hybrid_median", "hybrid_trimmed"
    ) or defense_type.startswith("ablation_") or defense_type.startswith("sweep_")

    validator = None
    state_machine = None
    rep_manager = None
    evidence_tracker = None

    if has_validator:
        is_legacy = (defense_type == "legacy_d0" or custom_params.get("legacy_d0", False))
        is_e4_init = (defense_type == "fixed_e4")
        is_c5 = defense_type in ("fixed_no_norm_scaling", "c5b_no_norm_z", "hybrid_median", "hybrid_trimmed", "detector_log_only")
        is_c5b = (defense_type == "c5b_no_norm_z" or custom_params.get("no_norm_z", False))

        det_variant = custom_params.get("detector_variant", "D0" if is_legacy else "D2")
        d2_z = custom_params.get("d2_z_thresh", 3.0)
        mad_f = custom_params.get("mad_floor", 1e-5 if is_legacy else 0.015)
        energy_gate = custom_params.get("energy_share_gate", 0.0 if is_legacy else (0.04 if is_e4_init else 0.40))
        norm_power = custom_params.get(
            "norm_scale_power",
            0.0 if (is_legacy or custom_params.get("no_norm_scaling") or is_c5)
            else (0.50 if is_e4_init else 0.585)
        )
        probe_thresh = custom_params.get(
            "target_class_degradation_threshold",
            -0.025 if (is_legacy or is_e4_init or custom_params.get("probe_thresh_0025")) else -0.05
        )
        probation_th = custom_params.get("probation_threshold", 0.40)
        quarantine_th = custom_params.get("quarantine_threshold", 0.70)
        warmup_r = 0 if (is_legacy or custom_params.get("no_warmup")) else custom_params.get("warmup_rounds", 5)

        use_cohort_cos = not custom_params.get("no_cohort_cosine", False)
        # In E4 design, clean slate is disabled
        enable_reset = False if is_e4_init else (not custom_params.get("no_round6_reset", False))

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

        if is_c5b:
            # Completely remove norm_z from validator and reputation
            validator.norm_z_extreme = 1e9
            validator.norm_z_anomaly = 1e9

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

        rep_manager = PerClassReputationManager(class_names=class_names)
        evidence_tracker = TemporalEvidenceTracker(warmup_rounds=warmup_r)

    # Pre-build GPU resident data tensors
    client_X_gpu = []
    client_y_gpu = []
    client_weights = []
    for cid in range(10):
        X_t, y_t = client_tensors[cid]
        if cid in malicious_set and attack_type in ("targeted_label_flip", "adaptive_norm_clip", "adaptive_cosine_mimic"):
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
    d2_logging_records = []

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
                    elif attack_type in ("adaptive_norm_clip", "adaptive_cosine_mimic"):
                        # Apply base targeted label flip with boost factor
                        u = attacks[cid].poison_update(u, round_num=r)

                client_updates.append(u)

        else: # old_dataloader
            for cid in range(10):
                df_c = client_dfs[cid]
                if cid in malicious_set and attack_type in ("targeted_label_flip", "adaptive_norm_clip", "adaptive_cosine_mimic"):
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

                if cid in malicious_set:
                    if attack_type == "targeted_label_flip":
                        u = attacks[cid].poison_update(u, round_num=r)
                    elif attack_type == "boosted_head_poisoning":
                        if "head.weight" in u:
                            u["head.weight"][4] = u["head.weight"][4] * 2.0
                    elif attack_type in ("adaptive_norm_clip", "adaptive_cosine_mimic"):
                        u = attacks[cid].poison_update(u, round_num=r)

                client_updates.append(u)

        # 1.1 Post-processing for Adaptive Attacks (Norm-Clipping & Cosine-Mimicking)
        if is_attacked and attack_type == "adaptive_norm_clip":
            honest_cids = [i for i in range(10) if i not in malicious_set]
            honest_norms = []
            for h in honest_cids:
                tot_sq = sum(v.pow(2).sum().item() for v in client_updates[h].values() if torch.is_floating_point(v))
                honest_norms.append(tot_sq ** 0.5)
            target_norm = float(np.median(honest_norms)) if honest_norms else 1.5

            for aid in malicious_set:
                tot_sq = sum(v.pow(2).sum().item() for v in client_updates[aid].values() if torch.is_floating_point(v))
                atk_norm = tot_sq ** 0.5
                if atk_norm > 1e-8:
                    scale = target_norm / atk_norm
                    for k in client_updates[aid]:
                        if torch.is_floating_point(client_updates[aid][k]):
                            client_updates[aid][k] = client_updates[aid][k] * scale

        elif is_attacked and attack_type == "adaptive_cosine_mimic":
            honest_cids = [i for i in range(10) if i not in malicious_set]
            keys_float = [k for k, v in client_updates[0].items() if torch.is_floating_point(v)]
            ref_flat = torch.zeros(sum(client_updates[0][k].numel() for k in keys_float), device=client_updates[0][keys_float[0]].device)
            for h in honest_cids:
                h_flat = torch.cat([client_updates[h][k].reshape(-1).float() for k in keys_float])
                ref_flat += h_flat / len(honest_cids)
            ref_norm = ref_flat.norm(p=2).item()

            beta = 0.40
            for aid in malicious_set:
                u_atk_flat = torch.cat([client_updates[aid][k].reshape(-1).float() for k in keys_float])
                blended = (1.0 - beta) * u_atk_flat + beta * ref_flat
                blended_norm = blended.norm(p=2).item()
                if blended_norm > 1e-8 and ref_norm > 1e-8:
                    blended = blended * (ref_norm / blended_norm)
                offset = 0
                for k in keys_float:
                    numel = client_updates[aid][k].numel()
                    client_updates[aid][k] = blended[offset : offset + numel].reshape(client_updates[aid][k].shape)
                    offset += numel

        # 2. Validation & Trust Engine
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
                if is_c5b:
                    vr.norm_z_score = 0.0

                rep_vector = rep_manager.update_reputation(cid, vr)
                ev_rec = evidence_tracker.update_evidence(cid, vr, rep_vector)

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
        cutoff_T = config.get("oracle_cutoff_round", None)
        oracle_mode = config.get("oracle_mode", "exclude_clients")

        if cutoff_T is not None and r >= cutoff_T:
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

            # Log D2 data if requested
            if config.get("log_d2_weights", False):
                d2_logging_records.append({
                    "round": r,
                    "config": config["run_name"],
                    "oracle": True,
                    "attacker_weights": [0.0 if cid in malicious_set else (client_samples[cid] / tot_w) for cid in range(10)],
                    "recon_reputations": [1.0 for _ in range(10)],
                    "r_effective": [1.0 for _ in range(10)],
                })

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

        elif defense_type in ("coordinate_median", "median"):
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
            new_state, _ = aggregate_krum(client_updates, global_model.state_dict(), f=num_malicious, m=1)
            global_model.load_state_dict(new_state)

        elif defense_type == "oracle_d1":
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
            # Fixed Defense, C4, C5, C5b, d2_z3, or fixed_e4
            use_hs = not custom_params.get("no_head_salience", False)
            agg_global, agg_time = aggregate_trust_class_aware(
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

            if config.get("log_d2_weights", False):
                # Calculate body weights
                body_weights = []
                for c_id, n_i in zip(range(10), client_samples):
                    sf = state_factors.get(c_id, 1.0)
                    rep_dict = rep_manager.reputation_table.get(c_id, {cls: 1.0 for cls in class_names})
                    base_trust = sum(rep_dict.values()) / max(1, len(rep_dict))
                    min_rep = min(rep_dict.values()) if rep_dict else 1.0
                    body_trust = base_trust * (min_rep ** 3.0) if min_rep < 0.70 else base_trust
                    w = (n_i ** 0.5) * body_trust * sf
                    body_weights.append(w)
                sum_bw = sum(body_weights)
                norm_bw = [w / sum_bw for w in body_weights] if sum_bw > 1e-8 else [0.1] * 10

                # Calculate head weights for class 4 (RECON)
                client_head_saliences = []
                for update in client_updates:
                    head_w = update.get("head.weight")
                    head_b = update.get("head.bias")
                    if head_w is not None and head_w.ndim == 2:
                        row_sq = torch.sum(head_w.float() ** 2, dim=1)
                        if head_b is not None:
                            row_sq = row_sq + (head_b.float() ** 2)
                        row_norms = torch.sqrt(row_sq + 1e-12)
                        total_head = torch.norm(row_norms) + 1e-8
                        normed = (row_norms / total_head).cpu().numpy()
                        sal = float(normed[4])
                    else:
                        sal = 1.0 / len(class_names)
                    client_head_saliences.append(sal)

                c_weights = []
                for idx, (c_id, n_i) in enumerate(zip(range(10), client_samples)):
                    sf = state_factors.get(c_id, 1.0)
                    r_ic = rep_manager.reputation_table.get(c_id, {}).get("RECON", 1.0)
                    r_effective = (r_ic ** 3.0) if r_ic >= 0.65 else 0.0
                    salience = (client_head_saliences[idx] + 0.05) if use_hs else 1.0
                    w = (n_i ** 0.5) * salience * r_effective * sf
                    c_weights.append(w)
                sum_hw = sum(c_weights)
                if sum_hw > 1e-8:
                    norm_hw = [w / sum_hw for w in c_weights]
                else:
                    best_idx = max(range(10), key=lambda idx: rep_manager.reputation_table.get(idx, {}).get("RECON", 0.0))
                    norm_hw = [0.0] * 10
                    norm_hw[best_idx] = 1.0

                rep_r4 = [rep_manager.reputation_table.get(cid, {}).get("RECON", 1.0) for cid in range(10)]
                r_eff = [max(0.0, (r_val - 0.65) / 0.35) for r_val in rep_r4]
                d2_logging_records.append({
                    "round": r,
                    "config": config["run_name"],
                    "oracle": False,
                    "body_weights": norm_bw,
                    "head_weights_recon": norm_hw,
                    "attacker_weights": [norm_hw[aid] for aid in malicious_set],
                    "honest_weights": [norm_hw[hid] for hid in range(10) if hid not in malicious_set],
                    "recon_reputations": rep_r4,
                    "r_effective": r_eff,
                    "state_factors": [state_factors.get(cid, 1.0) for cid in range(10)],
                })

        track_all = config.get("track_every_round", False) or config.get("step") in ("step4", "step8", "stress_test")
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

        total_quarantined = len(honest_quars) + len(atk_quars)
        atk_precision = (len(atk_quars) / total_quarantined) if total_quarantined > 0 else None
    else:
        honest_quars = []
        honest_quar_rate = 0.0
        honest_data_exclusion = 0.0
        atk_quars = []
        atk_quar_rate = 0.0
        atk_prob_rate = 0.0
        atk_precision = None

    # Trajectory AUC (mean RECON F1 over all evaluated rounds)
    if round_convergence:
        traj_auc = float(np.mean([rc["recon_f1"] for rc in round_convergence]))
    else:
        traj_auc = final_eval["recon_f1"]

    return {
        "run_name": config.get("run_name", "sim"),
        "step": config.get("step", "general"),
        "defense_type": defense_type,
        "partition_seed": partition_seed,
        "train_seed": train_seed,
        "is_attacked": is_attacked,
        "attack_type": attack_type,
        "num_malicious": num_malicious,
        "attacker_recon_share": attacker_recon_share,
        "attacker_recon_counts": attacker_recon_counts,
        "first_caught_round": first_caught_round,
        "num_rounds": num_rounds,
        "macro_f1": final_eval["macro_f1"],
        "balanced_accuracy": final_eval["balanced_accuracy"],
        "accuracy": final_eval["accuracy"],
        "recon_f1": final_eval["recon_f1"],
        "asr": final_eval["asr"],
        "traj_auc": traj_auc,
        "honest_quar_rate": honest_quar_rate,
        "honest_data_exclusion": honest_data_exclusion,
        "quarantined_honest_clients": honest_quars,
        "attacker_quar_rate": atk_quar_rate,
        "attacker_prob_rate": atk_prob_rate,
        "attacker_precision": atk_precision,
        "quarantined_attackers": atk_quars,
        "quarantine_schedule": quarantine_schedule,
        "round_convergence": round_convergence,
        "telemetry_records": telemetry_records,
        "d2_logging_records": d2_logging_records,
        "wall_time_s": wall_time,
    }


# ──────────────────────────────────────────────────────────────────────────────
# Config Builders for Phase E4.2c
# ──────────────────────────────────────────────────────────────────────────────

def get_calibration_seeds() -> list[tuple[int, int]]:
    partitions = [11, 12, 13]
    train_seeds = [1, 2, 3, 4, 5]
    return [(p, s) for p in partitions for s in train_seeds]


def build_step_b_configs() -> list[dict[str, Any]]:
    """Step B: Valid-Validator References on 15 configs (clean & attacked, 30 rounds)."""
    configs = []
    seeds = get_calibration_seeds()
    references = [
        ("legacy_d0", "legacy_d0", {"legacy_d0": True}),
        ("d2_z3", "d2_z3", {}),
        ("fixed_e4", "fixed_e4", {"no_round6_reset": True}),
    ]

    for ref_tag, d_type, c_params in references:
        for is_atk in (False, True):
            for p_seed, t_seed in seeds:
                configs.append({
                    "run_name": f"e4_2c_stepB_{ref_tag}_{'atk' if is_atk else 'clean'}_p{p_seed}_s{t_seed}",
                    "step": "stepB_references",
                    "candidate": ref_tag,
                    "partition_seed": p_seed,
                    "train_seed": t_seed,
                    "num_rounds": 30,
                    "is_attacked": is_atk,
                    "attack_type": "targeted_label_flip" if is_atk else "none",
                    "loop_env": "new_vram",
                    "val_env": "fast_val",
                    "defense_type": d_type,
                    "custom_params": c_params,
                    "track_every_round": True,
                })
    return configs


def build_step_d1_configs() -> list[dict[str, Any]]:
    """Step D1: C5b (norm_z removed entirely) on 15 configs clean & attacked + gamma=1 stress test."""
    configs = []
    seeds = get_calibration_seeds()

    # 1. C5b Clean (15 runs)
    for p_seed, t_seed in seeds:
        configs.append({
            "run_name": f"e4_2c_stepD1_C5b_clean_p{p_seed}_s{t_seed}",
            "step": "stepD1_c5b",
            "candidate": "C5b_no_norm_z",
            "partition_seed": p_seed,
            "train_seed": t_seed,
            "num_rounds": 30,
            "is_attacked": False,
            "attack_type": "none",
            "loop_env": "new_vram",
            "val_env": "fast_val",
            "defense_type": "c5b_no_norm_z",
            "custom_params": {"no_norm_scaling": True, "no_norm_z": True},
            "track_every_round": True,
        })

    # 2. C5b Attacked Standard (gamma=2.0) (15 runs)
    for p_seed, t_seed in seeds:
        configs.append({
            "run_name": f"e4_2c_stepD1_C5b_atk_p{p_seed}_s{t_seed}",
            "step": "stepD1_c5b",
            "candidate": "C5b_no_norm_z",
            "partition_seed": p_seed,
            "train_seed": t_seed,
            "num_rounds": 30,
            "is_attacked": True,
            "attack_type": "targeted_label_flip",
            "boost_factor": 2.0,
            "loop_env": "new_vram",
            "val_env": "fast_val",
            "defense_type": "c5b_no_norm_z",
            "custom_params": {"no_norm_scaling": True, "no_norm_z": True},
            "track_every_round": True,
        })

    # 3. C5b Attacked Gamma=1.0 (15 runs)
    for p_seed, t_seed in seeds:
        configs.append({
            "run_name": f"e4_2c_stepD1_C5b_gamma1_p{p_seed}_s{t_seed}",
            "step": "stepD1_c5b",
            "candidate": "C5b_no_norm_z",
            "partition_seed": p_seed,
            "train_seed": t_seed,
            "num_rounds": 30,
            "is_attacked": True,
            "attack_type": "targeted_label_flip",
            "boost_factor": 1.0,
            "loop_env": "new_vram",
            "val_env": "fast_val",
            "defense_type": "c5b_no_norm_z",
            "custom_params": {"no_norm_scaling": True, "no_norm_z": True},
            "track_every_round": True,
        })

    return configs


def build_step_d2_configs() -> list[dict[str, Any]]:
    """Step D2: Quarantine-then-collapse logging for P11_S1 and P12_S1 (C4 vs Oracle T=10)."""
    configs = []
    target_configs = [(11, 1), (12, 1)]

    # C4 runs with deep weight logging
    for p_seed, t_seed in target_configs:
        configs.append({
            "run_name": f"e4_2c_stepD2_C4_collapse_p{p_seed}_s{t_seed}",
            "step": "stepD2_collapse",
            "candidate": "C4_fixed_e4_1",
            "partition_seed": p_seed,
            "train_seed": t_seed,
            "num_rounds": 30,
            "is_attacked": True,
            "attack_type": "targeted_label_flip",
            "loop_env": "new_vram",
            "val_env": "fast_val",
            "defense_type": "fixed_e4_1",
            "custom_params": {},
            "log_d2_weights": True,
            "track_every_round": True,
        })

    # Oracle delay T=10 runs for comparison
    for p_seed, t_seed in target_configs:
        configs.append({
            "run_name": f"e4_2c_stepD2_oracle_T10_p{p_seed}_s{t_seed}",
            "step": "stepD2_collapse",
            "candidate": "oracle_delay_T10",
            "partition_seed": p_seed,
            "train_seed": t_seed,
            "num_rounds": 30,
            "is_attacked": True,
            "attack_type": "targeted_label_flip",
            "loop_env": "new_vram",
            "val_env": "fast_val",
            "defense_type": "fedavg",
            "oracle_cutoff_round": 10,
            "oracle_mode": "exclude_clients",
            "custom_params": {},
            "log_d2_weights": True,
            "track_every_round": True,
        })

    return configs


def build_step_d3_configs() -> list[dict[str, Any]]:
    """Step D3: Factorial 2x2 isolation rerun on P11_S1, P12_S1, P13_S1."""
    configs = []
    target_configs = [(11, 1), (12, 1), (13, 1)]
    envs = [
        ("A_old_loop_old_val", "old_dataloader", "old_val"),
        ("B_old_loop_fast_val", "old_dataloader", "fast_val"),
        ("C_new_loop_old_val", "new_vram", "old_val"),
        ("D_new_loop_fast_val", "new_vram", "fast_val"),
    ]

    for env_name, l_env, v_env in envs:
        for p_seed, t_seed in target_configs:
            configs.append({
                "run_name": f"e4_2c_stepD3_iso_{env_name}_p{p_seed}_s{t_seed}",
                "step": "stepD3_factorial",
                "candidate": f"legacy_d0_{env_name}",
                "partition_seed": p_seed,
                "train_seed": t_seed,
                "num_rounds": 30,
                "is_attacked": False,
                "attack_type": "none",
                "loop_env": l_env,
                "val_env": v_env,
                "defense_type": "legacy_d0",
                "custom_params": {"legacy_d0": True},
                "track_every_round": True,
            })
    return configs


def build_step_c_configs() -> list[dict[str, Any]]:
    """
    Step C: Stress Tests of frozen candidates C0, C1, C2, C5, C7, legacy_d0 (15 configs).
    Scenarios:
      (i) gamma1: targeted flip boost_factor=1.0
      (ii) norm_clip: adaptive_norm_clip (norm-matched)
      (iii) cosine_mimic: adaptive_cosine_mimic (cos-sim & norm-matched)
      (iv) head_boost: boosted_head_poisoning (gamma=2.0 on head.weight[4])
      (v) share_5_15: targeted flip with attacker RECON share 5-15%
      (vi) three_attackers: 3 attackers (30%)
    """
    configs = []
    seeds = get_calibration_seeds()

    scenarios = [
        ("gamma1", {"attack_type": "targeted_label_flip", "boost_factor": 1.0, "target_band": (0.25, 0.40), "num_malicious": 2}),
        ("norm_clip", {"attack_type": "adaptive_norm_clip", "boost_factor": 2.0, "target_band": (0.25, 0.40), "num_malicious": 2}),
        ("cosine_mimic", {"attack_type": "adaptive_cosine_mimic", "boost_factor": 2.0, "target_band": (0.25, 0.40), "num_malicious": 2}),
        ("head_boost", {"attack_type": "boosted_head_poisoning", "boost_factor": 2.0, "target_band": (0.25, 0.40), "num_malicious": 2}),
        ("share_5_15", {"attack_type": "targeted_label_flip", "boost_factor": 2.0, "target_band": (0.05, 0.15), "num_malicious": 2}),
        ("three_attackers", {"attack_type": "targeted_label_flip", "boost_factor": 2.0, "target_band": (0.25, 0.45), "num_malicious": 3}),
    ]

    candidates = [
        ("C0_fedavg", "fedavg", {}),
        ("C1_median", "coordinate_median", {}),
        ("C2_krum", "krum", {}),
        ("C5_fixed_no_norm_scaling", "fixed_no_norm_scaling", {}),
        ("C7_hybrid_median", "hybrid_median", {}),
        ("legacy_d0", "legacy_d0", {"legacy_d0": True}),
    ]

    for scen_name, scen_params in scenarios:
        for c_tag, d_type, c_params in candidates:
            for p_seed, t_seed in seeds:
                configs.append({
                    "run_name": f"e4_2c_stress_{scen_name}_{c_tag}_p{p_seed}_s{t_seed}",
                    "step": "stepC_stress",
                    "scenario": scen_name,
                    "candidate": c_tag,
                    "partition_seed": p_seed,
                    "train_seed": t_seed,
                    "num_rounds": 30,
                    "is_attacked": True,
                    "attack_type": scen_params["attack_type"],
                    "boost_factor": scen_params["boost_factor"],
                    "target_band": scen_params["target_band"],
                    "num_malicious": scen_params["num_malicious"],
                    "loop_env": "new_vram",
                    "val_env": "fast_val",
                    "defense_type": d_type,
                    "custom_params": c_params,
                    "track_every_round": True,
                })
    return configs


def main():
    parser = argparse.ArgumentParser(description="Phase E4.2c Full Master Benchmark Harness")
    parser.add_argument("--shard", type=str, default="all", choices=["all", "part1", "part2", "part3"], help="Fleet shard to execute")
    parser.add_argument("--stage", type=str, default="all", choices=["all", "step_b", "step_c", "step_d"], help="Stage to execute")
    parser.add_argument("--workers", type=int, default=4, help="Parallel worker processes")
    parser.add_argument("--force-workers", action="store_true", help="Force exact worker count regardless of CPU core count")
    parser.add_argument("--output-dir", type=str, default="results/runs/phase_e4_2c", help="Output directory")
    args = parser.parse_args()

    # Step 0: Integrity Check
    assert_candidate_hashes()

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    runs_file = out_dir / "runs.jsonl"
    telem_file = out_dir / "telemetry.csv"

    # Datasets
    test_path_str = "data/processed/dev/test.parquet"
    server_val_path_str = "data/processed/dev/server_val.parquet"
    test_df = pd.read_parquet(test_path_str)
    feature_cols = [c for c in test_df.columns if c not in ("label", "class_name")]
    with open("configs/label_mapping.yaml") as f:
        lm = yaml.safe_load(f)
    class_names = [lm["idx_to_class"][i] for i in range(len(lm["idx_to_class"]))]

    # Collect configurations based on shard or stage
    all_configs = []
    if args.shard == "part1":
        # Shard 1: References (Step B) + Mechanism Checks (Step D) = 151 runs
        all_configs.extend(build_step_b_configs())
        all_configs.extend(build_step_d1_configs())
        all_configs.extend(build_step_d2_configs())
        all_configs.extend(build_step_d3_configs())
    elif args.shard == "part2":
        # Shard 2: Stress tests scenarios 1, 2, 3 (gamma1, norm_clip, cosine_mimic) = 270 runs
        all_stress = build_step_c_configs()
        all_configs.extend([c for c in all_stress if c.get("scenario") in ("gamma1", "norm_clip", "cosine_mimic")])
    elif args.shard == "part3":
        # Shard 3: Stress tests scenarios 4, 5, 6 (head_boost, share_5_15, three_attackers) = 270 runs
        all_stress = build_step_c_configs()
        all_configs.extend([c for c in all_stress if c.get("scenario") in ("head_boost", "share_5_15", "three_attackers")])
    else:
        # Full suite or stage-filtered
        if args.stage in ("all", "step_b"):
            all_configs.extend(build_step_b_configs())
        if args.stage in ("all", "step_d"):
            all_configs.extend(build_step_d1_configs())
            all_configs.extend(build_step_d2_configs())
            all_configs.extend(build_step_d3_configs())
        if args.stage in ("all", "step_c"):
            all_configs.extend(build_step_c_configs())

    # Load existing runs for resumption
    completed_runs = set()
    if runs_file.exists():
        with open(runs_file, "r") as f:
            for line in f:
                if line.strip():
                    try:
                        record = json.loads(line)
                        completed_runs.add(record["run_name"])
                    except Exception:
                        pass
        logger.info(f"Resuming: found {len(completed_runs)} already completed runs in {runs_file}.")

    pending_configs = [c for c in all_configs if c["run_name"] not in completed_runs]
    logger.info(f"Total benchmark configurations: {len(all_configs)} (Pending: {len(pending_configs)})")

    if not pending_configs:
        logger.info("All configurations already completed! Nothing to run.")
        return

    telem_header_written = telem_file.exists() and telem_file.stat().st_size > 0

    t0 = time.time()
    completed_count = len(completed_runs)
    total_count = len(all_configs)

    num_gpus = torch.cuda.device_count()
    cpu_cores = os.cpu_count() or 4
    if not args.force_workers and args.workers > cpu_cores:
        logger.warning(
            f"Requested {args.workers} workers on a machine with {cpu_cores} CPUs. "
            f"Auto-tuning workers to {cpu_cores} to prevent CPU context-switch starvation and GPU idling. "
            f"(Use --force-workers to override)."
        )
        effective_workers = cpu_cores
    else:
        effective_workers = args.workers

    logger.info(f"Launching pool with {effective_workers} workers across {num_gpus} available GPUs...")

    with concurrent.futures.ProcessPoolExecutor(max_workers=effective_workers) as executor:
        futures = {}
        for idx, cfg in enumerate(pending_configs):
            p_dir_str = f"data/partitions/dev/seed_{cfg['partition_seed']}"
            dev_str = f"cuda:{idx % num_gpus}" if num_gpus > 0 else "cpu"
            f = executor.submit(
                run_simulation, cfg, p_dir_str, test_path_str, server_val_path_str, feature_cols, class_names, device_str=dev_str
            )
            futures[f] = cfg

        for fut in concurrent.futures.as_completed(futures):
            cfg = futures[fut]
            try:
                res = fut.result()
                completed_count += 1

                # 1. Append to runs.jsonl
                with open(runs_file, "a") as f:
                    f.write(json.dumps(res) + "\n")

                # 2. Append telemetry
                records = res.get("telemetry_records", [])
                if records:
                    df_tel = pd.DataFrame(records)
                    df_tel.to_csv(telem_file, mode="a", index=False, header=not telem_header_written)
                    telem_header_written = True

                elapsed = time.time() - t0
                pct = (completed_count / total_count) * 100
                logger.info(
                    f"[{completed_count}/{total_count} ({pct:.1f}%)] Finished {cfg['run_name']}: "
                    f"Macro-F1={res['macro_f1']:.4f}, RECON-F1={res['recon_f1']:.4f}, ASR={res['asr']:.4f}, "
                    f"HQ={res['honest_quar_rate']*100:.1f}%, AtkQ={res.get('attacker_quar_rate', 0)*100:.1f}% "
                    f"({elapsed:.1f}s elapsed)"
                )
            except Exception as e:
                logger.error(f"Failed configuration {cfg['run_name']}: {e}", exc_info=True)

    total_time = time.time() - t0
    logger.info(f"Phase E4.2c execution finished in {total_time:.2f}s ({total_time/60:.2f} min).")


if __name__ == "__main__":
    main()
