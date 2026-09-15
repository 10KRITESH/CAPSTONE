"""
partition.py — IID & Non-IID Dataset Partitioning Engine for Federated Learning.

Simulates heterogeneous dataset distribution across FL clients:
  1. IID Partitioning:
     - Uniform random assignment of samples across all clients.
     - Clients have roughly identical class distributions.

  2. Non-IID Dirichlet Partitioning:
     - Uses Dirichlet distribution Dirichlet(alpha) over class probabilities for each client.
     - Lower alpha (e.g., 0.1, 0.5) = extreme Non-IID skew (clients specialize in specific attack types).
     - Higher alpha (e.g., 10.0) = approaches IID.

Output:
  data/partitions/{dev|full}/
    ├── client_00.parquet
    ├── client_01.parquet
    └── ...
    └── partition_summary.json

Usage:
    python src/data/partition.py --num-clients 20 --alpha 0.5 --dev
    python src/data/partition.py --num-clients 10 --iid --dev
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import numpy as np
import pandas as pd
import yaml

# ── Logging setup ─────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)


def load_config(config_path: str) -> dict:
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


# ══════════════════════════════════════════════════════════════════════════════
# IID Partitioning
# ══════════════════════════════════════════════════════════════════════════════

def partition_iid(df: pd.DataFrame, num_clients: int, seed: int) -> list[pd.DataFrame]:
    """Uniformly partition DataFrame across num_clients."""
    np.random.seed(seed)
    shuffled_df = df.sample(frac=1.0, random_state=seed).reset_index(drop=True)
    splits = np.array_split(shuffled_df, num_clients)
    return [split.reset_index(drop=True) for split in splits]


# ══════════════════════════════════════════════════════════════════════════════
# Non-IID Dirichlet Partitioning
# ══════════════════════════════════════════════════════════════════════════════

def partition_dirichlet(
    df: pd.DataFrame, num_clients: int, alpha: float, seed: int, min_samples_per_client: int = 50
) -> list[pd.DataFrame]:
    """
    Partition DataFrame using Dirichlet(alpha) distribution over classes.

    Args:
        df: Input training DataFrame containing 'label' column.
        num_clients: Number of FL clients.
        alpha: Concentration parameter for Dirichlet distribution.
        seed: Random seed for reproducibility.
        min_samples_per_client: Minimum samples required per client.
    """
    np.random.seed(seed)
    labels = df["label"].values
    num_classes = len(np.unique(labels))

    # Group indices by class
    class_indices = [np.where(labels == c)[0] for c in range(num_classes)]

    client_indices = [[] for _ in range(num_clients)]

    for c, indices in enumerate(class_indices):
        np.random.shuffle(indices)

        # Sample proportions from Dirichlet(alpha)
        proportions = np.random.dirichlet(np.repeat(alpha, num_clients))
        
        # Convert proportions to index split points
        proportions = (np.cumsum(proportions) * len(indices)).astype(int)[:-1]

        # Split class indices across clients
        split_indices = np.array_split(indices, proportions)

        for client_idx in range(num_clients):
            client_indices[client_idx].extend(split_indices[client_idx])

    # Assemble client DataFrames
    client_dfs = []
    for i, idxs in enumerate(client_indices):
        np.random.shuffle(idxs)
        c_df = df.iloc[idxs].reset_index(drop=True)
        if len(c_df) < min_samples_per_client:
            log.warning(f"Client {i} has only {len(c_df)} samples (below min threshold {min_samples_per_client}).")
        client_dfs.append(c_df)

    return client_dfs


# ══════════════════════════════════════════════════════════════════════════════
# Summary & Export
# ══════════════════════════════════════════════════════════════════════════════

def export_partitions(
    client_dfs: list[pd.DataFrame],
    output_dir: Path,
    partition_type: str,
    alpha: float | None,
    num_classes: int = 8,
) -> dict:
    """Save client DataFrames to parquet and generate detailed distribution statistics."""
    output_dir.mkdir(parents=True, exist_ok=True)

    summary = {
        "partition_type": partition_type,
        "alpha": alpha,
        "num_clients": len(client_dfs),
        "total_samples": sum(len(c_df) for c_df in client_dfs),
        "clients": {},
    }

    log.info(f"Exporting {len(client_dfs)} client partitions to {output_dir} ...")

    for i, c_df in enumerate(client_dfs):
        fname = f"client_{i:02d}.parquet"
        c_df.to_parquet(output_dir / fname, index=False, compression="snappy")

        # Compute per-class sample count and distribution
        class_counts = c_df["label"].value_counts().to_dict()
        full_counts = {int(cls): int(class_counts.get(cls, 0)) for cls in range(num_classes)}
        
        summary["clients"][f"client_{i:02d}"] = {
            "client_id": i,
            "sample_count": len(c_df),
            "class_counts": full_counts,
            "class_proportions": {
                cls: round(cnt / len(c_df), 4) if len(c_df) > 0 else 0.0
                for cls, cnt in full_counts.items()
            },
        }

    # Save summary JSON
    summary_path = output_dir / "partition_summary.json"
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)

    log.info(f"Partition summary saved to {summary_path}")

    # Print summary table
    print("\n" + "=" * 65)
    print(f"  PARTITIONING COMPLETE — {partition_type.upper()} (Clients: {len(client_dfs)})")
    if alpha is not None:
        print(f"  Dirichlet Alpha: {alpha}")
    print("=" * 65)
    print(f"  {'Client ID':<12} {'Total Rows':>12} {'Dominant Class':>18}")
    print("  " + "-" * 50)
    for c_id, info in summary["clients"].items():
        counts = info["class_counts"]
        dom_cls = max(counts, key=counts.get)
        dom_pct = (counts[dom_cls] / info["sample_count"] * 100) if info["sample_count"] > 0 else 0.0
        print(f"  {c_id:<12} {info['sample_count']:>12,} {f'Class {dom_cls} ({dom_pct:.1f}%)':>18}")
    print("=" * 65 + "\n")

    return summary


# ══════════════════════════════════════════════════════════════════════════════
# Entry Point
# ══════════════════════════════════════════════════════════════════════════════

def run_partitioning(
    config_path: str = "configs/default.yaml",
    num_clients: int | None = None,
    alpha: float | None = None,
    iid: bool = False,
    dev_mode: bool = True,
):
    cfg = load_config(config_path)
    seed = cfg["project"]["random_seed"]
    fed_cfg = cfg.get("federation", {})

    num_clients = num_clients or fed_cfg.get("num_clients", 20)
    alpha = alpha or fed_cfg.get("dirichlet_alpha", 0.5)

    split = "dev" if dev_mode else "full"
    train_parquet = Path(cfg["paths"]["processed_dir"]) / split / "train.parquet"
    out_dir = Path("data/partitions") / split

    if not train_parquet.exists():
        raise FileNotFoundError(
            f"Training data parquet not found at {train_parquet}. Run preprocess.py first."
        )

    log.info(f"Loading training data from {train_parquet} ...")
    df_train = pd.read_parquet(train_parquet)

    num_classes = cfg["model"]["num_classes"]

    if iid:
        log.info(f"Performing IID partitioning across {num_clients} clients ...")
        client_dfs = partition_iid(df_train, num_clients, seed)
        partition_type = "iid"
        alpha_val = None
    else:
        log.info(f"Performing Non-IID Dirichlet(alpha={alpha}) partitioning across {num_clients} clients ...")
        client_dfs = partition_dirichlet(df_train, num_clients, alpha, seed)
        partition_type = "non_iid"
        alpha_val = alpha

    export_partitions(client_dfs, out_dir, partition_type, alpha_val, num_classes=num_classes)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Partition training data for FL clients")
    parser.add_argument("--config", default="configs/default.yaml", help="Path to default.yaml")
    parser.add_argument("--num-clients", type=int, default=None, help="Number of FL clients (e.g. 5, 10, 20, 50)")
    parser.add_argument("--alpha", type=float, default=None, help="Dirichlet alpha for Non-IID skew")
    parser.add_argument("--iid", action="store_true", help="Force uniform IID partitioning")
    parser.add_argument("--dev", action="store_true", default=True, help="Use dev split (default)")
    parser.add_argument("--full", action="store_true", help="Use full split")
    args = parser.parse_args()

    dev_mode = not args.full
    run_partitioning(
        config_path=args.config,
        num_clients=args.num_clients,
        alpha=args.alpha,
        iid=args.iid,
        dev_mode=dev_mode,
    )
