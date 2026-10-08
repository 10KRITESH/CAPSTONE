"""
step_d_evaluate.py — Comprehensive 30-Round Benchmark Evaluation.

Executes 30 rounds across 10 evaluation seeds (101..110) for:
  - Baseline defenses: fedavg, median, trimmed_mean, krum, proposed_trust_off
  - Proposed defense variants: D0, D1_100 (ORACLE), D2_z3 (deployable), D4, D2_z3_D4
  - Under Clean condition (0%) and Attacked condition (Band 1: 5-15% RECON share, random attacker_seed)

Tracks:
  - Honest FPR (clients & data-weighted) at rounds 5, 10, 20, 30
  - Attributable attacker detection (Probation & Quarantine) and time-to-detection
  - Quarantine precision (with clear handling of 0-quarantine runs)
  - Core macro-F1, balanced accuracy, ASR (with clean control), and validation overhead
"""

from __future__ import annotations

import argparse
import copy
import json
import logging
from pathlib import Path
import sys
import time
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import numpy as np
import pandas as pd
import torch

from src.attacks.targeted_label_flip import TargetedLabelFlipAttack
from src.data.dataset import CICIoTDataset
from src.federation.client import FLClient
from src.federation.coordinator import FLCoordinator
from src.model.evaluate import evaluate
from src.model.mlp import IDS_MLP
from src.utils import save_run_metadata, seed_everything
from src.experiments.harness import AttackerSelector

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

EVALUATION_SEEDS = [101, 102, 103, 104, 105, 106, 107, 108, 109, 110]
NUM_ROUNDS = 30


def run_single_eval_experiment(
    method_name: str,
    scenario: str,
    seed: int,
    config: dict,
    partition_files: list[Path],
    feature_cols: list[str],
    server_val_ds: CICIoTDataset,
    test_ds: CICIoTDataset,
    class_names: list[str],
    client_total_samples: dict[int, int],
    client_recon_samples: dict[int, int],
    oracle_client_support: dict[int, dict[str, int]],
    total_training_samples: int,
    total_recon_samples: int,
    attacker_selector: AttackerSelector,
    device: torch.device,
    run_dir: Path,
) -> tuple[dict, list[dict]]:
    t0 = time.time()
    torch.manual_seed(seed)
    init_model = IDS_MLP(in_features=len(feature_cols), num_classes=8)
    init_weights = copy.deepcopy(init_model.state_dict())

    # Map method to coordinator aggregation and variant flags
    aggregation_method = "trust_class_aware"
    disable_split = False
    disable_state = False
    det_variant = "D0"
    d1_min_supp = 100
    d2_z = 3.0
    soft_containment = False
    oracle_support_to_pass = None

    if method_name == "fedavg":
        aggregation_method = "fedavg"
    elif method_name == "median":
        aggregation_method = "median"
    elif method_name == "trimmed_mean":
        aggregation_method = "trimmed_mean"
    elif method_name == "krum":
        aggregation_method = "krum"
    elif method_name == "proposed_trust_off":
        aggregation_method = "trust_class_aware"
        disable_split = True
        disable_state = True
    elif method_name == "proposed_d0":
        det_variant = "D0"
    elif method_name == "proposed_d1_100":
        det_variant = "D1"
        d1_min_supp = 100
        oracle_support_to_pass = oracle_client_support
    elif method_name == "proposed_d2_z3":
        det_variant = "D2"
        d2_z = 3.0
    elif method_name == "proposed_d4":
        det_variant = "D0"
        soft_containment = True
    elif method_name == "proposed_d2_z3_d4":
        det_variant = "D2"
        d2_z = 3.0
        soft_containment = True
    else:
        raise ValueError(f"Unknown method name: {method_name}")

    attacker_ids = []
    attacker_seed = None
    attacker_sample_share = 0.0
    attacker_recon_share = 0.0

    if scenario == "attacked":
        attacker_seed = seed + 5000
        atk_info = attacker_selector.select_stratified(
            target_band=(0.05, 0.15), num_malicious=2, seed=attacker_seed
        )
        attacker_ids = atk_info["attacker_ids"]
        attacker_sample_share = atk_info["sample_share"]
        attacker_recon_share = atk_info["source_sample_share"]

    seed_everything(seed)
    clients = []
    for cid, pf in enumerate(partition_files):
        atk = None
        if cid in attacker_ids:
            atk = TargetedLabelFlipAttack(
                source_class=4, target_class=0, poison_ratio=1.0
            )
        clients.append(
            FLClient(
                client_id=cid,
                partition_path=pf,
                feature_cols=feature_cols,
                num_classes=8,
                attack=atk,
                device=device,
            )
        )

    db_path = run_dir / f"audit_{method_name}_{scenario}_{seed}.db"
    ledger_path = run_dir / f"ledger_{method_name}_{scenario}_{seed}.json"

    coord = FLCoordinator(
        config=config,
        clients=clients,
        server_val_ds=server_val_ds,
        test_ds=test_ds,
        aggregation_method=aggregation_method,
        device=device,
        disable_head_body_split=disable_split,
        disable_state_factor=disable_state,
        db_path=str(db_path),
        ledger_path=str(ledger_path),
        detector_variant=det_variant,
        d1_min_support=d1_min_supp,
        d2_z_thresh=d2_z,
        oracle_client_support=oracle_support_to_pass,
        soft_containment=soft_containment,
    )
    coord.global_model.load_state_dict(copy.deepcopy(init_weights))

    round_telemetry = []
    first_honest_probation_round = None
    first_honest_quarantine_round = None
    attacker_probation_rounds = {aid: None for aid in attacker_ids}
    attacker_quarantine_rounds = {aid: None for aid in attacker_ids}

    checkpoints_rounds = [5, 10, 20, 30]
    quar_by_checkpoint = {}
    exc_samples_by_checkpoint = {}

    for r in range(1, NUM_ROUNDS + 1):
        coord.run_round(round_num=r)

        honest_quar = []
        honest_prob = []
        for cid in range(10):
            st = coord.state_machine.get_state(cid).value if hasattr(coord, "state_machine") else "TRUSTED"
            if cid in attacker_ids:
                if st == "PROBATION" and attacker_probation_rounds[cid] is None:
                    attacker_probation_rounds[cid] = r
                elif st == "QUARANTINED" and attacker_quarantine_rounds[cid] is None:
                    attacker_quarantine_rounds[cid] = r
            else:
                if st == "PROBATION":
                    honest_prob.append(cid)
                    if first_honest_probation_round is None:
                        first_honest_probation_round = r
                elif st == "QUARANTINED":
                    honest_quar.append(cid)
                    if first_honest_quarantine_round is None:
                        first_honest_quarantine_round = r

            round_telemetry.append({
                "method": method_name,
                "scenario": scenario,
                "seed": seed,
                "round": r,
                "client_id": cid,
                "is_attacker": cid in attacker_ids,
                "state": st,
            })

        if r in checkpoints_rounds:
            exc_s = sum(client_total_samples[c] for c in honest_quar)
            quar_by_checkpoint[f"honest_quar_r{r}"] = len(honest_quar)
            exc_samples_by_checkpoint[f"honest_exc_data_r{r}"] = round(exc_s / total_training_samples, 4)

    wall_time = time.time() - t0

    # Evaluate final global model
    tm = evaluate(coord.global_model, coord.test_loader, device, class_names, asr_pair=(4, 0))
    core_classes = ["BENIGN", "DDOS", "DOS", "MIRAI", "RECON", "MITM"]
    core_f1 = float(np.mean([tm["per_class"][c]["f1"] for c in core_classes]))
    recon_f1 = float(tm["per_class"]["RECON"]["f1"])
    asr = float(tm.get("attack_success_rate", 0.0))

    final_honest_quar = [
        c for c in range(10)
        if c not in attacker_ids and hasattr(coord, "state_machine") and coord.state_machine.get_state(c).value == "QUARANTINED"
    ]
    final_honest_prob = [
        c for c in range(10)
        if c not in attacker_ids and hasattr(coord, "state_machine") and coord.state_machine.get_state(c).value == "PROBATION"
    ]
    final_atk_quar = [
        c for c in attacker_ids
        if hasattr(coord, "state_machine") and coord.state_machine.get_state(c).value == "QUARANTINED"
    ]
    final_atk_prob = [
        c for c in attacker_ids
        if hasattr(coord, "state_machine") and coord.state_machine.get_state(c).value == "PROBATION"
    ]

    exc_honest_samples = sum(client_total_samples[c] for c in final_honest_quar)
    exc_honest_recon = sum(client_recon_samples[c] for c in final_honest_quar)
    num_honest_clients = 10 - len(attacker_ids)

    # Quarantine Precision = TP / (TP + FP)
    tp_quar = len(final_atk_quar)
    fp_quar = len(final_honest_quar)
    total_quars = tp_quar + fp_quar
    # Note: If total_quars == 0, defined as 1.0 (no false alarms)
    quar_precision = round(tp_quar / total_quars, 4) if total_quars > 0 else 1.0

    run_summary = {
        "method": method_name,
        "scenario": scenario,
        "train_seed": seed,
        "rounds": NUM_ROUNDS,
        "attacker_seed": attacker_seed,
        "attacker_ids": attacker_ids,
        "attacker_sample_share": round(attacker_sample_share, 4),
        "attacker_recon_share": round(attacker_recon_share, 4),
        "final_quarantined_clients": [c for c in range(10) if hasattr(coord, "state_machine") and coord.state_machine.get_state(c).value == "QUARANTINED"],
        "final_quarantined_count": len([c for c in range(10) if hasattr(coord, "state_machine") and coord.state_machine.get_state(c).value == "QUARANTINED"]),
        "honest_quar_clients": final_honest_quar,
        "honest_prob_clients": final_honest_prob,
        "honest_fpr_clients": round(len(final_honest_quar) / max(1, num_honest_clients), 4),
        "honest_fpr_data": round(exc_honest_samples / total_training_samples, 4),
        "honest_recon_exclusion_pct": round(exc_honest_recon / total_recon_samples, 4),
        "attackers_detected_probation": len(final_atk_prob) + len(final_atk_quar),
        "attackers_detected_quarantine": len(final_atk_quar),
        "quarantine_precision": quar_precision,
        "time_to_first_honest_quarantine": first_honest_quarantine_round,
        "attacker_quarantine_times": [attacker_quarantine_rounds[aid] for aid in attacker_ids],
        "macro_f1": round(float(tm["macro_f1"]), 4),
        "core_macro_f1": round(core_f1, 4),
        "recon_f1": round(recon_f1, 4),
        "asr": round(asr, 4),
        "balanced_accuracy": round(float(tm["balanced_accuracy"]), 4),
        "accuracy_footnote": round(float(tm["accuracy"]), 4),
        "wall_time_s": round(wall_time, 1),
    }
    run_summary.update(quar_by_checkpoint)
    run_summary.update(exc_samples_by_checkpoint)

    return run_summary, round_telemetry


def run_step_d_evaluation(split: str = "dev", run_id: str = "step_d_evaluate"):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    run_dir = Path("results/runs") / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    jsonl_path = run_dir / "runs.jsonl"
    rounds_csv_path = run_dir / "client_rounds.csv"

    with open("configs/default.yaml") as f:
        config = yaml.safe_load(f)

    processed_dir = Path("data/processed") / split
    partitions_dir = Path("data/partitions") / split
    partition_files = sorted(partitions_dir.glob("client_*.parquet"))

    server_val_ds = CICIoTDataset(processed_dir / "server_val.parquet")
    test_ds = CICIoTDataset(processed_dir / "test.parquet")
    feature_cols = server_val_ds.feature_cols

    with open(config["paths"]["label_mapping"]) as f:
        lm_cfg = yaml.safe_load(f)
    class_names = [lm_cfg["idx_to_class"][i] for i in range(len(lm_cfg["idx_to_class"]))]

    client_total_samples = {}
    client_recon_samples = {}
    oracle_client_support = {}
    for i, pf in enumerate(partition_files):
        df = pd.read_parquet(pf, columns=["label"])
        client_total_samples[i] = len(df)
        client_recon_samples[i] = int((df["label"] == 4).sum())
        oracle_client_support[i] = {
            c_name: int((df["label"] == c_idx).sum())
            for c_idx, c_name in enumerate(class_names)
        }

    total_training_samples = sum(client_total_samples.values())
    total_recon_samples = sum(client_recon_samples.values())
    attacker_selector = AttackerSelector(partition_files, source_class=4)

    # Resume support
    completed_keys = set()
    if jsonl_path.exists():
        with open(jsonl_path) as f:
            for line in f:
                if line.strip():
                    try:
                        d = json.loads(line)
                        completed_keys.add((d["method"], d["scenario"], d["train_seed"]))
                    except Exception:
                        pass

    log.info(f"Loaded {len(completed_keys)} completed runs in {jsonl_path}")

    save_run_metadata(
        run_dir=run_dir,
        config=config,
        seeds={"evaluation_seeds": EVALUATION_SEEDS},
        extra={"rounds": NUM_ROUNDS},
    )

    methods_to_evaluate = [
        "fedavg",
        "median",
        "trimmed_mean",
        "krum",
        "proposed_trust_off",
        "proposed_d0",
        "proposed_d1_100",  # ORACLE
        "proposed_d2_z3",   # Deployable Peer-Relative
        "proposed_d4",      # Deployable Soft Containment
        "proposed_d2_z3_d4" # Combined Deployable
    ]

    for method in methods_to_evaluate:
        for scenario in ["clean", "attacked"]:
            for seed in EVALUATION_SEEDS:
                key = (method, scenario, seed)
                if key in completed_keys:
                    continue

                log.info(f"Evaluating: {method} | {scenario.upper()} | Seed {seed}")
                res, telem = run_single_eval_experiment(
                    method_name=method,
                    scenario=scenario,
                    seed=seed,
                    config=config,
                    partition_files=partition_files,
                    feature_cols=feature_cols,
                    server_val_ds=server_val_ds,
                    test_ds=test_ds,
                    class_names=class_names,
                    client_total_samples=client_total_samples,
                    client_recon_samples=client_recon_samples,
                    oracle_client_support=oracle_client_support,
                    total_training_samples=total_training_samples,
                    total_recon_samples=total_recon_samples,
                    attacker_selector=attacker_selector,
                    device=device,
                    run_dir=run_dir,
                )
                with open(jsonl_path, "a") as f:
                    f.write(json.dumps(res) + "\n")

                if telem:
                    df_t = pd.DataFrame(telem)
                    header = not rounds_csv_path.exists()
                    df_t.to_csv(rounds_csv_path, mode="a", index=False, header=header)

                completed_keys.add(key)

    log.info(f"Completed all Step D evaluations in {run_dir}")


if __name__ == "__main__":
    run_step_d_evaluation()
