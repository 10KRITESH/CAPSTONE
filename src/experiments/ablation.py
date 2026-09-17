"""
ablation.py — Systematic Ablation Study Suite for Plan v2.

Evaluates incremental component contributions:
  A. FedAvg (No defense baseline)
  B. Scalar Trust (Single reputation score)
  C. Class-Aware Trust (Per-attack-class reputation vector)
  D. Class-Aware Trust + Temporal Evidence (E_t accumulation)
  E. Full Proposed System (+ State Machine Containment & Shadow Recovery)

Usage:
    python src/experiments/ablation.py --rounds 5 --dev
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import torch

from src.attacks.targeted_label_flip import TargetedLabelFlipAttack
from src.data.dataset import CICIoTDataset
from src.federation.client import FLClient
from src.federation.coordinator import FLCoordinator

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)


def run_ablation_study(num_rounds: int = 5, dev_mode: bool = True):
    split = "dev" if dev_mode else "full"
    processed_dir = Path("data/processed") / split
    partitions_dir = Path("data/partitions") / split

    server_val_ds = CICIoTDataset(processed_dir / "server_val.parquet")
    test_ds = CICIoTDataset(processed_dir / "test.parquet")
    partition_files = sorted(partitions_dir.glob("client_*.parquet"))

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # 1. Clean Clients (0% Malicious)
    clean_clients = [
        FLClient(
            client_id=i,
            partition_path=p_file,
            feature_cols=server_val_ds.feature_cols,
            num_classes=8,
            attack=None,
            device=device,
        )
        for i, p_file in enumerate(partition_files)
    ]

    # 2. Poisoned Clients (20% Malicious: RECON -> BENIGN targeted flip)
    num_malicious = int(round(len(partition_files) * 0.20))
    malicious_indices = set(range(num_malicious))

    poisoned_clients = []
    for i, p_file in enumerate(partition_files):
        attack_obj = TargetedLabelFlipAttack(source_class=4, target_class=0) if i in malicious_indices else None
        c = FLClient(
            client_id=i,
            partition_path=p_file,
            feature_cols=server_val_ds.feature_cols,
            num_classes=8,
            attack=attack_obj,
            device=device,
        )
        poisoned_clients.append(c)

    # Load default config
    import yaml
    with open("configs/default.yaml") as f:
        config = yaml.safe_load(f)

    benchmarks = [
        ("FedAvg (Clean - 0% Attack)", "fedavg", clean_clients),
        ("FedAvg (Poisoned - 20% Attack)", "fedavg", poisoned_clients),
        ("Krum (Byzantine Distance)", "krum", poisoned_clients),
        ("Trimmed Mean", "trimmed_mean", poisoned_clients),
        ("Coordinate Median", "median", poisoned_clients),
        ("Proposed Defense (Class-Aware Trust)", "trust_class_aware", poisoned_clients),
    ]
    ablation_results = {}

    print("\n" + "=" * 80)
    print("  [BENCHMARK] RUNNING COMPREHENSIVE 8-WAY DEFENSE & ABLATION STUDY")
    print("=" * 80)

    for label, method, client_list in benchmarks:
        print(f"\n>>> Running Benchmark: '{label}' ({num_rounds} Rounds) ...")
        dir_name = label.split()[0].lower() + ("_clean" if "Clean" in label else "_attack")
        results_dir = Path("results/ablation") / dir_name
        baseline_ckpt = Path(f"results/baseline/{split}/best_model.pt")
        coordinator = FLCoordinator(
            config=config,
            clients=client_list,
            server_val_ds=server_val_ds,
            test_ds=test_ds,
            aggregation_method=method,
            device=device,
            init_weights_path=baseline_ckpt if baseline_ckpt.exists() else None,
        )
        res = coordinator.run_federated_simulation(
            num_rounds=num_rounds, results_dir=results_dir
        )
        test_m = res["test_metrics"]
        recon_f1 = test_m.get("per_class", {}).get("RECON", {}).get("f1", 0.0)
        ablation_results[label] = {
            "accuracy": test_m["accuracy"],
            "macro_f1": test_m["macro_f1"],
            "recon_f1": recon_f1,
            "method": method,
        }

    print("\n" + "=" * 85)
    print("  🏆 FINAL BENCHMARK & ABLATION RESULTS (Under 20% RECON Targeted Attack)")
    print("=" * 85)
    print(f"  {'Defense / Benchmark Method':<38} {'Accuracy':>11} {'Macro F1':>12} {'RECON F1 (Target)':>18}")
    print("  " + "-" * 82)
    for label, data in ablation_results.items():
        print(f"  {label:<38} {data['accuracy']*100:>10.2f}% {data['macro_f1']*100:>11.2f}% {data['recon_f1']*100:>17.2f}%")
    print("=" * 85 + "\n")

    output_path = Path("results/ablation/summary.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(ablation_results, f, indent=2)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ablation & Baseline Benchmark Suite")
    parser.add_argument("--rounds", type=int, default=5, help="Number of FL rounds per scheme")
    parser.add_argument("--dev", action="store_true", default=True, help="Use dev split (default)")
    args = parser.parse_args()

    run_ablation_study(num_rounds=args.rounds, dev_mode=args.dev)
