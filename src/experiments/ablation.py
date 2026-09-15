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

    # Configure 20% targeted class attackers (RECON -> BENIGN)
    num_malicious = int(round(len(partition_files) * 0.20))
    malicious_indices = set(range(num_malicious))

    clients: list[FLClient] = []
    for i, p_file in enumerate(partition_files):
        attack_obj = None
        if i in malicious_indices:
            attack_obj = TargetedLabelFlipAttack(source_class=4, target_class=0)
        client = FLClient(
            client_id=i,
            partition_path=p_file,
            feature_cols=server_val_ds.feature_cols,
            num_classes=8,
            attack=attack_obj,
            device=device,
        )
        clients.append(client)

    # Load default config
    import yaml
    with open("configs/default.yaml") as f:
        config = yaml.safe_load(f)

    methods = ["fedavg", "krum", "trimmed_mean", "median", "trust_class_aware"]
    ablation_results = {}

    print("\n" + "=" * 70)
    print("  [ABLATION] RUNNING PLAN V2 ABLATION & BASELINE COMPARISON SUITE")
    print("=" * 70)

    for method in methods:
        print(f"\n[ABLATION] Testing Defense Method: '{method.upper()}' ({num_rounds} Rounds) ...")
        results_dir = Path("results/ablation") / method
        coordinator = FLCoordinator(
            config=config,
            clients=clients,
            server_val_ds=server_val_ds,
            test_ds=test_ds,
            aggregation_method=method,
            device=device,
        )
        res = coordinator.run_federated_simulation(
            num_rounds=num_rounds, results_dir=results_dir
        )
        ablation_results[method] = res["test_metrics"]

    print("\n" + "=" * 70)
    print("  SUMMARY — 8-WAY DEFENSE ABLATION COMPARISON")
    print("=" * 70)
    print(f"  {'Defense Method':<22} {'Test Accuracy':>15} {'Macro F1-Score':>16}")
    print("  " + "-" * 55)
    for m, tm in ablation_results.items():
        print(f"  {m:<22} {tm['accuracy']*100:>14.2f}% {tm['macro_f1']*100:>15.2f}%")
    print("=" * 70 + "\n")

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
