"""
overhead.py — Systems Overhead & Communication Cost Benchmarking Suite.

Measures per-round:
  - Transmitted Bytes Overhead (Communication cost)
  - Aggregation Latency (ms) across FedAvg, Krum, Trimmed Mean, Median, and Trust Aggregation
  - Multi-Signal Validation Latency (ms)

Usage:
    python src/experiments/overhead.py
"""

from __future__ import annotations

import json
import logging
import sys
import time
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import pandas as pd
import torch

from src.data.dataset import CICIoTDataset
from src.federation.client import FLClient
from src.federation.coordinator import FLCoordinator

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)


def measure_systems_overhead(num_rounds: int = 3):
    processed_dir = Path("data/processed/dev")
    partitions_dir = Path("data/partitions/dev")

    server_val_ds = CICIoTDataset(processed_dir / "server_val.parquet")
    test_ds = CICIoTDataset(processed_dir / "test.parquet")
    partition_files = sorted(partitions_dir.glob("client_*.parquet"))

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    clients = [
        FLClient(i, pf, server_val_ds.feature_cols, 8, device=device)
        for i, pf in enumerate(partition_files)
    ]

    import yaml
    with open("configs/default.yaml") as f:
        config = yaml.safe_load(f)

    methods = ["fedavg", "krum", "trimmed_mean", "median", "trust_class_aware"]
    overhead_summary = []

    print("\n" + "=" * 70)
    print("  [OVERHEAD] SYSTEMS OVERHEAD & LATENCY BENCHMARK")
    print("=" * 70)

    for method in methods:
        coordinator = FLCoordinator(
            config=config,
            clients=clients,
            server_val_ds=server_val_ds,
            test_ds=test_ds,
            aggregation_method=method,
            device=device,
        )
        res = coordinator.run_federated_simulation(num_rounds=num_rounds)
        hist = res["history"]

        avg_comm_mb = float(np.mean([h["comm_bytes"] for h in hist])) / (1024 * 1024)
        avg_agg_ms = float(np.mean([h["agg_time_ms"] for h in hist]))
        avg_val_ms = float(np.mean([h["val_time_ms"] for h in hist]))

        entry = {
            "Method": method,
            "Comm Size (MB)": round(avg_comm_mb, 2),
            "Agg Latency (ms)": round(avg_agg_ms, 2),
            "Val Latency (ms)": round(avg_val_ms, 2),
            "Total Round Latency (ms)": round(avg_agg_ms + avg_val_ms, 2),
        }
        overhead_summary.append(entry)

    df_ov = pd.DataFrame(overhead_summary)
    print("\n" + df_ov.to_string(index=False))
    print("=" * 70 + "\n")

    output_path = Path("results/overhead/summary.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(overhead_summary, f, indent=2)


if __name__ == "__main__":
    measure_systems_overhead(num_rounds=3)
