"""
step_a_potency.py — Step A: Attack Potency Evaluation on Calibration Seeds.

Measures undefended FedAvg clean vs attacked (targeted label-flip RECON->BENIGN)
across 5 calibration seeds (train_seed 1..5) for three RECON-share bands:
  - Band 1: 5-15%
  - Band 2: 25-35%
  - Band 3: 40-55%

Outputs:
  - results/runs/step_a_potency/runs.jsonl
  - results/runs/step_a_potency/potency_summary.csv
"""

from __future__ import annotations

import copy
import json
import logging
import sys
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import numpy as np
import pandas as pd
import torch
import yaml
from torch.utils.data import DataLoader, TensorDataset

from src.attacks.targeted_label_flip import TargetedLabelFlipAttack
from src.data.dataset import CICIoTDataset
from src.experiments.aggregate_results import bootstrap_ci
from src.experiments.harness import AttackerSelector
from src.federation.client import FLClient
from src.federation.coordinator import FLCoordinator
from src.model.evaluate import evaluate
from src.model.mlp import IDS_MLP
from src.utils import save_run_metadata, seed_everything

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

CALIBRATION_SEEDS = [1, 2, 3, 4, 5]
NUM_ROUNDS = 10
BANDS = [
    ("band_5_15", (0.05, 0.15)),
    ("band_25_35", (0.25, 0.35)),
    ("band_40_55", (0.40, 0.55)),
]


def run_step_a(split: str = "dev", run_id: str = "step_a_potency"):
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

    selector = AttackerSelector(partition_files, source_class=4)

    # Load existing completed keys to support resume
    completed_keys = set()
    if jsonl_path.exists():
        with open(jsonl_path) as f:
            for line in f:
                if line.strip():
                    try:
                        d = json.loads(line)
                        completed_keys.add(f"{d['scenario']}__{d['train_seed']}")
                    except Exception:
                        pass

    log.info(f"Loaded {len(completed_keys)} previously completed runs in {jsonl_path}")

    save_run_metadata(
        run_dir=run_dir,
        config=config,
        seeds={"calibration_seeds": CALIBRATION_SEEDS},
        extra={"num_rounds": NUM_ROUNDS, "bands": [b[0] for b in BANDS]},
    )

    records = []

    for seed in CALIBRATION_SEEDS:
        torch.manual_seed(seed)
        init_model = IDS_MLP(in_features=len(feature_cols), num_classes=8)
        init_weights = copy.deepcopy(init_model.state_dict())

        # 1. Clean control for this seed
        clean_key = f"clean_control__{seed}"
        if clean_key in completed_keys:
            log.info(f"Skipping completed: {clean_key}")
        else:
            log.info(f"\n{'='*70}\n  RUN: Clean FedAvg Control | Seed: {seed}\n{'='*70}")
            seed_everything(seed)
            clients = [
                FLClient(
                    client_id=i, partition_path=pf, feature_cols=feature_cols,
                    num_classes=8, attack=None, device=device
                )
                for i, pf in enumerate(partition_files)
            ]
            coord = FLCoordinator(
                config=config, clients=clients, server_val_ds=server_val_ds, test_ds=test_ds,
                aggregation_method="fedavg", device=device,
                db_path=str(run_dir / f"audit_clean_{seed}.db"),
                ledger_path=str(run_dir / f"ledger_clean_{seed}.json"),
            )
            coord.global_model.load_state_dict(copy.deepcopy(init_weights))

            t0 = time.time()
            for r in range(1, NUM_ROUNDS + 1):
                coord.run_round(round_num=r)
            wall_time = time.time() - t0

            tm = evaluate(coord.global_model, coord.test_loader, device, class_names, asr_pair=(4, 0))
            core_classes = ["BENIGN", "DDOS", "DOS", "MIRAI", "RECON", "MITM"]
            core_f1 = float(np.mean([tm["per_class"][c]["f1"] for c in core_classes]))

            clean_rec = {
                "scenario": "clean_control",
                "band": "none",
                "train_seed": seed,
                "attacker_seed": None,
                "attacker_ids": [],
                "attacker_sample_share": 0.0,
                "attacker_source_share": 0.0,
                "accuracy_footnote": round(float(tm["accuracy"]), 4),
                "balanced_accuracy": round(float(tm["balanced_accuracy"]), 4),
                "macro_f1": round(float(tm["macro_f1"]), 4),
                "core_macro_f1": round(float(core_f1), 4),
                "recon_f1": round(float(tm["per_class"]["RECON"]["f1"]), 4),
                "asr": round(float(tm["attack_success_rate"]), 4) if tm["attack_success_rate"] is not None else 0.0,
                "wall_time_s": round(wall_time, 1),
            }
            with open(jsonl_path, "a") as f:
                f.write(json.dumps(clean_rec) + "\n")
            completed_keys.add(clean_key)
            records.append(clean_rec)

        # 2. Attacked runs across bands
        for band_idx, (b_name, b_interval) in enumerate(BANDS, start=1):
            atk_key = f"{b_name}__{seed}"
            if atk_key in completed_keys:
                log.info(f"Skipping completed: {atk_key}")
                continue

            # Vary attacker_seed across runs (never fixed)
            attacker_seed = seed * 100 + band_idx * 17
            atk_info = selector.select_stratified(target_band=b_interval, num_malicious=2, seed=attacker_seed)
            malicious_set = set(atk_info["attacker_ids"])

            log.info(
                f"\n{'='*70}\n  RUN: FedAvg Attacked ({b_name}) | Seed: {seed} | "
                f"Attackers: {atk_info['attacker_ids']} | RECON Share: {atk_info['source_sample_share']*100:.2f}%\n{'='*70}"
            )
            seed_everything(seed)
            clients = [
                FLClient(
                    client_id=i, partition_path=pf, feature_cols=feature_cols,
                    num_classes=8,
                    attack=TargetedLabelFlipAttack(source_class=4, target_class=0) if i in malicious_set else None,
                    device=device,
                )
                for i, pf in enumerate(partition_files)
            ]
            coord = FLCoordinator(
                config=config, clients=clients, server_val_ds=server_val_ds, test_ds=test_ds,
                aggregation_method="fedavg", device=device,
                db_path=str(run_dir / f"audit_{b_name}_{seed}.db"),
                ledger_path=str(run_dir / f"ledger_{b_name}_{seed}.json"),
            )
            coord.global_model.load_state_dict(copy.deepcopy(init_weights))

            t0 = time.time()
            for r in range(1, NUM_ROUNDS + 1):
                coord.run_round(round_num=r)
            wall_time = time.time() - t0

            tm = evaluate(coord.global_model, coord.test_loader, device, class_names, asr_pair=(4, 0))
            core_classes = ["BENIGN", "DDOS", "DOS", "MIRAI", "RECON", "MITM"]
            core_f1 = float(np.mean([tm["per_class"][c]["f1"] for c in core_classes]))

            atk_rec = {
                "scenario": b_name,
                "band": b_name,
                "train_seed": seed,
                "attacker_seed": attacker_seed,
                "attacker_ids": atk_info["attacker_ids"],
                "attacker_sample_share": atk_info["sample_share"],
                "attacker_source_share": atk_info["source_sample_share"],
                "accuracy_footnote": round(float(tm["accuracy"]), 4),
                "balanced_accuracy": round(float(tm["balanced_accuracy"]), 4),
                "macro_f1": round(float(tm["macro_f1"]), 4),
                "core_macro_f1": round(float(core_f1), 4),
                "recon_f1": round(float(tm["per_class"]["RECON"]["f1"]), 4),
                "asr": round(float(tm["attack_success_rate"]), 4) if tm["attack_success_rate"] is not None else 0.0,
                "wall_time_s": round(wall_time, 1),
            }
            with open(jsonl_path, "a") as f:
                f.write(json.dumps(atk_rec) + "\n")
            completed_keys.add(atk_key)
            records.append(atk_rec)

    # Statistical Aggregation
    df_all = pd.read_json(jsonl_path, lines=True)
    clean_df = df_all[df_all["scenario"] == "clean_control"]

    summary_rows = []

    # Clean control summary
    c_asr_m, c_asr_l, c_asr_h = bootstrap_ci(clean_df["asr"].tolist())
    c_rec_m, c_rec_l, c_rec_h = bootstrap_ci(clean_df["recon_f1"].tolist())
    c_core_m, c_core_l, c_core_h = bootstrap_ci(clean_df["core_macro_f1"].tolist())
    c_bal_m, c_bal_l, c_bal_h = bootstrap_ci(clean_df["balanced_accuracy"].tolist())

    summary_rows.append({
        "scenario": "Clean Control",
        "recon_share_mean": 0.0,
        "sample_share_mean": 0.0,
        "asr_mean": c_asr_m,
        "asr_ci": f"[{c_asr_l*100:.1f}, {c_asr_h*100:.1f}]",
        "recon_f1_mean": c_rec_m,
        "recon_f1_ci": f"[{c_rec_l*100:.1f}, {c_rec_h*100:.1f}]",
        "core_f1_mean": c_core_m,
        "core_f1_ci": f"[{c_core_l*100:.1f}, {c_core_h*100:.1f}]",
        "bal_acc_mean": c_bal_m,
        "bal_acc_ci": f"[{c_bal_l*100:.1f}, {c_bal_h*100:.1f}]",
        "recon_f1_drop": 0.0,
        "ci_half_width": (c_rec_h - c_rec_l) / 2.0,
        "passes_gate": False,
    })

    print("\n" + "=" * 95)
    print("  [STEP A: ATTACK POTENCY RESULTS ON UNDEFENDED FEDAVG] (5 Calibration Seeds, 10 Rounds)")
    print("=" * 95)
    print(f"  {'Scenario':<16} {'RECON Share':>12} {'ASR (95% CI)':>20} {'RECON F1 (95% CI)':>22} {'RECON Drop':>11} {'Pass Gate?':>11}")
    print("  " + "-" * 95)
    print(
        f"  {'Clean Control':<16} {'0.0%':>12} "
        f"{c_asr_m*100:>5.1f}% {f'[{c_asr_l*100:.1f}, {c_asr_h*100:.1f}]':>14} "
        f"{c_rec_m*100:>5.1f}% {f'[{c_rec_l*100:.1f}, {c_rec_h*100:.1f}]':>16} "
        f"{'0.0%':>11} {'CONTROL':>11}"
    )

    for b_name, _ in BANDS:
        b_df = df_all[df_all["scenario"] == b_name]
        asr_m, asr_l, asr_h = bootstrap_ci(b_df["asr"].tolist())
        rec_m, rec_l, rec_h = bootstrap_ci(b_df["recon_f1"].tolist())
        core_m, core_l, core_h = bootstrap_ci(b_df["core_macro_f1"].tolist())
        bal_m, bal_l, bal_h = bootstrap_ci(b_df["balanced_accuracy"].tolist())

        # Drop compared to matched clean seeds
        diffs_rec = []
        for s in CALIBRATION_SEEDS:
            c_val = clean_df[clean_df["train_seed"] == s]["recon_f1"].iloc[0]
            a_val = b_df[b_df["train_seed"] == s]["recon_f1"].iloc[0]
            diffs_rec.append(c_val - a_val)  # positive = degraded

        drop_mean, drop_low, drop_high = bootstrap_ci(diffs_rec)
        ci_half_width = (drop_high - drop_low) / 2.0

        # Potency gate: FedAvg attacked is worse than clean control by more than CI half width (drop_low > 0 or drop_mean > ci_half_width)
        passes_gate = (drop_low > 0.0) or (drop_mean > ci_half_width and drop_mean > 0.03)

        summary_rows.append({
            "scenario": b_name,
            "recon_share_mean": round(float(b_df["attacker_source_share"].mean()), 4),
            "sample_share_mean": round(float(b_df["attacker_sample_share"].mean()), 4),
            "asr_mean": asr_m,
            "asr_ci": f"[{asr_l*100:.1f}, {asr_h*100:.1f}]",
            "recon_f1_mean": rec_m,
            "recon_f1_ci": f"[{rec_l*100:.1f}, {rec_h*100:.1f}]",
            "core_f1_mean": core_m,
            "core_f1_ci": f"[{core_l*100:.1f}, {core_h*100:.1f}]",
            "bal_acc_mean": bal_m,
            "bal_acc_ci": f"[{bal_l*100:.1f}, {bal_h*100:.1f}]",
            "recon_f1_drop": drop_mean,
            "ci_half_width": ci_half_width,
            "passes_gate": bool(passes_gate),
        })

        print(
            f"  {b_name:<16} {b_df['attacker_source_share'].mean()*100:>11.1f}% "
            f"{asr_m*100:>5.1f}% {f'[{asr_l*100:.1f}, {asr_h*100:.1f}]':>14} "
            f"{rec_m*100:>5.1f}% {f'[{rec_l*100:.1f}, {rec_h*100:.1f}]':>16} "
            f"{drop_mean*100:>10.2f}% "
            f"{'PASS' if passes_gate else 'FAIL':>11}"
        )

    print("=" * 95 + "\n")

    summary_df = pd.DataFrame(summary_rows)
    summary_df.to_csv(run_dir / "potency_summary.csv", index=False)
    log.info(f"Saved potency summary to {run_dir / 'potency_summary.csv'}")


if __name__ == "__main__":
    run_step_a()
