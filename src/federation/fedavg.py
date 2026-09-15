"""
fedavg.py — Baseline Federated Averaging (FedAvg) Simulation Runner (Phase 3 & Phase 5).

Executes FedAvg simulation across partitioned clients:
  - Clean FL baseline (no attackers)
  - Poisoned FL baseline (with untargeted, targeted, or model update poisoning attackers)

Usage:
    python src/federation/fedavg.py                                # Clean FedAvg (20 rounds)
    python src/federation/fedavg.py --num-rounds 10 --dev         # 10 rounds on dev split
    python src/federation/fedavg.py --attack label_flip --malicious-ratio 0.20
    python src/federation/fedavg.py --attack targeted --source 4 --target 0
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import torch
import yaml

from src.attacks.label_flip import UntargetedLabelFlipAttack
from src.attacks.model_poisoning import ModelPoisoningAttack
from src.attacks.targeted_label_flip import TargetedLabelFlipAttack
from src.data.dataset import CICIoTDataset
from src.data.partition import run_partitioning
from src.federation.client import FLClient
from src.federation.coordinator import FLCoordinator

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


def main():
    parser = argparse.ArgumentParser(description="FedAvg Baseline FL Runner")
    parser.add_argument("--config", default="configs/default.yaml", help="Path to config file")
    parser.add_argument("--num-rounds", type=int, default=20, help="Number of FL rounds (default: 20)")
    parser.add_argument("--local-epochs", type=int, default=1, help="Local client epochs per round")
    parser.add_argument("--lr", type=float, default=1e-3, help="Local learning rate")
    parser.add_argument("--dev", action="store_true", default=True, help="Use dev split (default)")
    parser.add_argument("--full", action="store_true", help="Use full split")
    
    # Attack configurations
    parser.add_argument(
        "--attack",
        choices=["none", "label_flip", "targeted", "model_poisoning"],
        default="none",
        help="Type of attack to inject into FL round",
    )
    parser.add_argument(
        "--malicious-ratio",
        type=float,
        default=0.0,
        help="Fraction of clients configured as malicious (e.g., 0.10, 0.20)",
    )
    parser.add_argument("--source-class", type=int, default=4, help="Source attack class for targeted attack (4=RECON)")
    parser.add_argument("--target-class", type=int, default=0, help="Target attack class for targeted attack (0=BENIGN)")
    parser.add_argument("--scale-factor", type=float, default=-1.0, help="Update scale factor for model poisoning")

    args = parser.parse_args()

    config = load_config(args.config)
    dev_mode = not args.full
    split = "dev" if dev_mode else "full"

    # Paths
    processed_dir = Path(config["paths"]["processed_dir"]) / split
    partitions_dir = Path("data/partitions") / split
    server_val_path = processed_dir / "server_val.parquet"
    test_path = processed_dir / "test.parquet"

    # Ensure dataset is preprocessed and partitioned
    if not server_val_path.exists() or not test_path.exists():
        log.error(f"Processed datasets not found at {processed_dir}. Run preprocess.py first.")
        sys.exit(1)

    if not partitions_dir.exists() or not list(partitions_dir.glob("client_*.parquet")):
        log.info(f"No partitions found in {partitions_dir}. Triggering auto-partitioning ...")
        run_partitioning(config_path=args.config, dev_mode=dev_mode)

    # 1. Load Server Validation & Test Datasets
    log.info("Loading server validation and test datasets ...")
    server_val_ds = CICIoTDataset(server_val_path)
    test_ds = CICIoTDataset(test_path)

    # 2. Discover Client Partitions
    partition_files = sorted(partitions_dir.glob("client_*.parquet"))
    num_total_clients = len(partition_files)
    log.info(f"Discovered {num_total_clients} client partitions in {partitions_dir}")

    # Determine malicious clients
    num_malicious = int(round(num_total_clients * args.malicious_ratio))
    malicious_indices = set(range(num_malicious)) if num_malicious > 0 else set()

    if num_malicious > 0:
        log.info(f"Configuring {num_malicious}/{num_total_clients} clients as MALICIOUS ({args.attack} attack)")

    # 3. Instantiate FL Clients
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    feature_cols = server_val_ds.feature_cols
    num_classes = config["model"]["num_classes"]

    clients: list[FLClient] = []
    for i, p_file in enumerate(partition_files):
        attack_obj = None
        if i in malicious_indices and args.attack != "none":
            if args.attack == "label_flip":
                attack_obj = UntargetedLabelFlipAttack(num_classes=num_classes)
            elif args.attack == "targeted":
                attack_obj = TargetedLabelFlipAttack(
                    source_class=args.source_class, target_class=args.target_class
                )
            elif args.attack == "model_poisoning":
                attack_obj = ModelPoisoningAttack(scale_factor=args.scale_factor)

        client = FLClient(
            client_id=i,
            partition_path=p_file,
            feature_cols=feature_cols,
            num_classes=num_classes,
            attack=attack_obj,
            device=device,
        )
        clients.append(client)

    # 4. Initialize Coordinator & Run Simulation
    exp_name = "fedavg_clean" if args.attack == "none" else f"fedavg_{args.attack}_ratio{int(args.malicious_ratio*100)}"
    results_dir = Path("results/federated") / exp_name

    coordinator = FLCoordinator(
        config=config,
        clients=clients,
        server_val_ds=server_val_ds,
        test_ds=test_ds,
        device=device,
    )

    coordinator.run_federated_simulation(
        num_rounds=args.num_rounds,
        local_epochs=args.local_epochs,
        lr=args.lr,
        results_dir=results_dir,
    )


if __name__ == "__main__":
    main()
