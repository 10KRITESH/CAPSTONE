"""
step_c_screen.py — Screen Detector Variants (D0-D4) on Calibration Seeds.

Evaluates candidate detector variants on CALIBRATION SEEDS (1..5) over 15 rounds
to measure:
  - Clean condition: Honest FPR (clients & data-weighted), time to first quarantine.
  - Attacked condition (Band 1: 5-15% RECON share, random attacker_seed):
    Attributable attacker detection (Probation / Quarantine), RECON F1, ASR.

Variants screened:
  - D0: Baseline absolute threshold
  - D1 (ORACLE): Support gating (sweep min_support: 30, 100, 300)
  - D2: Peer-relative MAD Z-scoring (sweep z_thresh: 2.0, 3.0, 4.0)
  - D3: Calibrated peer-relative (99th percentile honest threshold)
  - D4: Soft containment (continuous state factor)
  - D2+D4: Peer-relative z=3.0 combined with Soft containment
"""

from __future__ import annotations

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

CALIBRATION_SEEDS = [1, 2, 3, 4, 5]
NUM_ROUNDS = 15


def run_single_experiment(
    variant_name: str,
    scenario: str,  # 'clean' or 'attacked'
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
    d3_calibrated_z: float | None = None,
) -> dict:
    t0 = time.time()
    torch.manual_seed(seed)
    init_model = IDS_MLP(in_features=len(feature_cols), num_classes=8)
    init_weights = copy.deepcopy(init_model.state_dict())

    # Configure variant switches
    det_variant = "D0"
    d1_min_supp = 100
    d2_z = 3.0
    d3_z = None
    soft_containment = False
    oracle_support_to_pass = None

    if variant_name == "D0":
        det_variant = "D0"
    elif variant_name == "D1_30":
        det_variant = "D1"
        d1_min_supp = 30
        oracle_support_to_pass = oracle_client_support
    elif variant_name == "D1_100":
        det_variant = "D1"
        d1_min_supp = 100
        oracle_support_to_pass = oracle_client_support
    elif variant_name == "D1_300":
        det_variant = "D1"
        d1_min_supp = 300
        oracle_support_to_pass = oracle_client_support
    elif variant_name == "D2_z2":
        det_variant = "D2"
        d2_z = 2.0
    elif variant_name == "D2_z3":
        det_variant = "D2"
        d2_z = 3.0
    elif variant_name == "D2_z4":
        det_variant = "D2"
        d2_z = 4.0
    elif variant_name == "D3":
        det_variant = "D3"
        d3_z = d3_calibrated_z if d3_calibrated_z is not None else 3.0
    elif variant_name == "D4":
        det_variant = "D0"
        soft_containment = True
    elif variant_name == "D2_z3_D4":
        det_variant = "D2"
        d2_z = 3.0
        soft_containment = True

    # Setup attackers if scenario is attacked
    attacker_ids = []
    attacker_seed = None
    attacker_sample_share = 0.0
    attacker_recon_share = 0.0

    if scenario == "attacked":
        attacker_seed = seed + 5000  # Vary attacker seed across runs
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

    db_path = run_dir / f"audit_{variant_name}_{scenario}_{seed}.db"
    ledger_path = run_dir / f"ledger_{variant_name}_{scenario}_{seed}.json"

    coord = FLCoordinator(
        config=config,
        clients=clients,
        server_val_ds=server_val_ds,
        test_ds=test_ds,
        aggregation_method="trust_class_aware",
        device=device,
        db_path=str(db_path),
        ledger_path=str(ledger_path),
        detector_variant=det_variant,
        d1_min_support=d1_min_supp,
        d2_z_thresh=d2_z,
        d3_calibrated_z_thresh=d3_z,
        oracle_client_support=oracle_support_to_pass,
        soft_containment=soft_containment,
    )
    coord.global_model.load_state_dict(copy.deepcopy(init_weights))

    first_probation_round = None
    first_quarantine_round = None
    attacker_probation_rounds = {aid: None for aid in attacker_ids}
    attacker_quarantine_rounds = {aid: None for aid in attacker_ids}
    honest_quarantine_counts_by_round = []

    for r in range(1, NUM_ROUNDS + 1):
        coord.run_round(round_num=r)

        honest_quars = 0
        for cid in range(10):
            st = coord.state_machine.get_state(cid).value
            if cid in attacker_ids:
                if st == "PROBATION" and attacker_probation_rounds[cid] is None:
                    attacker_probation_rounds[cid] = r
                elif st == "QUARANTINED" and attacker_quarantine_rounds[cid] is None:
                    attacker_quarantine_rounds[cid] = r
            else:
                if st == "PROBATION" and first_probation_round is None:
                    first_probation_round = r
                elif st == "QUARANTINED":
                    honest_quars += 1
                    if first_quarantine_round is None:
                        first_quarantine_round = r
        honest_quarantine_counts_by_round.append(honest_quars)

    wall_time = time.time() - t0

    # Evaluate final global model
    tm = evaluate(coord.global_model, coord.test_loader, device, class_names, asr_pair=(4, 0))
    core_classes = ["BENIGN", "DDOS", "DOS", "MIRAI", "RECON", "MITM"]
    core_f1 = float(np.mean([tm["per_class"][c]["f1"] for c in core_classes]))
    recon_f1 = float(tm["per_class"]["RECON"]["f1"])
    asr = float(tm.get("attack_success_rate", 0.0))

    final_honest_quar = [
        c for c in range(10)
        if c not in attacker_ids and coord.state_machine.get_state(c).value == "QUARANTINED"
    ]
    final_honest_prob = [
        c for c in range(10)
        if c not in attacker_ids and coord.state_machine.get_state(c).value == "PROBATION"
    ]
    final_atk_quar = [
        c for c in attacker_ids
        if coord.state_machine.get_state(c).value == "QUARANTINED"
    ]
    final_atk_prob = [
        c for c in attacker_ids
        if coord.state_machine.get_state(c).value == "PROBATION"
    ]

    exc_honest_samples = sum(client_total_samples[c] for c in final_honest_quar)
    num_honest_clients = 10 - len(attacker_ids)

    return {
        "variant": variant_name,
        "scenario": scenario,
        "train_seed": seed,
        "rounds": NUM_ROUNDS,
        "attacker_seed": attacker_seed,
        "attacker_ids": attacker_ids,
        "attacker_sample_share": round(attacker_sample_share, 4),
        "attacker_recon_share": round(attacker_recon_share, 4),
        "honest_fpr_clients": round(len(final_honest_quar) / max(1, num_honest_clients), 4),
        "honest_fpr_data": round(exc_honest_samples / total_training_samples, 4),
        "honest_quar_clients": final_honest_quar,
        "honest_prob_clients": final_honest_prob,
        "attackers_detected_probation": len(final_atk_prob) + len(final_atk_quar),
        "attackers_detected_quarantine": len(final_atk_quar),
        "attacker_detection_rate": round(len(final_atk_quar) / max(1, len(attacker_ids)), 4) if attacker_ids else 0.0,
        "time_to_first_honest_quarantine": first_quarantine_round,
        "macro_f1": round(float(tm["macro_f1"]), 4),
        "core_macro_f1": round(core_f1, 4),
        "recon_f1": round(recon_f1, 4),
        "asr": round(asr, 4),
        "balanced_accuracy": round(float(tm["balanced_accuracy"]), 4),
        "wall_time_s": round(wall_time, 1),
    }


def run_step_c_screen(split: str = "dev", run_id: str = "step_c_screen"):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    run_dir = Path("results/runs") / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    jsonl_path = run_dir / "runs.jsonl"

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
                        completed_keys.add((d["variant"], d["scenario"], d["train_seed"]))
                    except Exception:
                        pass

    log.info(f"Loaded {len(completed_keys)} completed screen runs in {jsonl_path}")

    save_run_metadata(
        run_dir=run_dir,
        config=config,
        seeds={"calibration_seeds": CALIBRATION_SEEDS},
        extra={"rounds": NUM_ROUNDS},
    )

    variants_to_screen = [
        "D0",
        "D1_30",
        "D1_100",
        "D1_300",
        "D2_z2",
        "D2_z3",
        "D2_z4",
        "D4",
        "D2_z3_D4",
    ]

    for variant in variants_to_screen:
        for scenario in ["clean", "attacked"]:
            for seed in CALIBRATION_SEEDS:
                key = (variant, scenario, seed)
                if key in completed_keys:
                    continue

                log.info(f"Screening: {variant} | {scenario.upper()} | Seed {seed}")
                res = run_single_experiment(
                    variant_name=variant,
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
                completed_keys.add(key)

    # Summary table
    df_all = pd.read_json(jsonl_path, lines=True)
    summary_rows = []
    for var in variants_to_screen:
        clean_subset = df_all[(df_all["variant"] == var) & (df_all["scenario"] == "clean")]
        atk_subset = df_all[(df_all["variant"] == var) & (df_all["scenario"] == "attacked")]

        clean_fpr_client = clean_subset["honest_fpr_clients"].mean() * 100 if len(clean_subset) else 0.0
        clean_fpr_data = clean_subset["honest_fpr_data"].mean() * 100 if len(clean_subset) else 0.0
        atk_det_rate = atk_subset["attacker_detection_rate"].mean() * 100 if len(atk_subset) else 0.0
        atk_recon_f1 = atk_subset["recon_f1"].mean() * 100 if len(atk_subset) else 0.0
        atk_asr = atk_subset["asr"].mean() * 100 if len(atk_subset) else 0.0
        clean_f1 = clean_subset["macro_f1"].mean() * 100 if len(clean_subset) else 0.0

        summary_rows.append({
            "Variant": var,
            "Type": "ORACLE" if "D1" in var else "Deployable",
            "Clean Client FPR (%)": round(clean_fpr_client, 1),
            "Clean Data Exclusion (%)": round(clean_fpr_data, 1),
            "Attacker Detection (%)": round(atk_det_rate, 1),
            "Attacked RECON F1 (%)": round(atk_recon_f1, 1),
            "Attacked ASR (%)": round(atk_asr, 1),
            "Clean Macro-F1 (%)": round(clean_f1, 1),
        })

    df_summary = pd.DataFrame(summary_rows)
    df_summary.to_csv(run_dir / "screen_summary.csv", index=False)

    print("\n" + "=" * 90)
    print("  [STEP C: DETECTOR VARIANT SCREENING RESULTS] (Calibration Seeds 1..5, 15 Rounds)")
    print("=" * 90)
    print(df_summary.to_string(index=False))
    print("=" * 90 + "\n")


if __name__ == "__main__":
    run_step_c_screen()
