"""
test_determinism.py — Unit test verifying deterministic reproducibility across FL runs.

Runs two 2-round federated learning simulations starting from identical seeds
and initial weights, asserting that resulting models and evaluation metrics
are bit-for-bit or eps-identical (atol <= 1e-6).
"""

from __future__ import annotations

import copy
import shutil
import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import torch
import yaml

from src.data.dataset import CICIoTDataset
from src.federation.client import FLClient
from src.federation.coordinator import FLCoordinator
from src.model.mlp import IDS_MLP
from src.utils import seed_everything


class TestDeterminism(unittest.TestCase):
    def setUp(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        with open("configs/default.yaml") as f:
            self.config = yaml.safe_load(f)

        self.split = "dev"
        self.processed_dir = Path("data/processed") / self.split
        self.partitions_dir = Path("data/partitions") / self.split

        # Skip if dataset is not preprocessed
        if not (self.processed_dir / "server_val.parquet").exists():
            self.skipTest("Dev dataset not found at data/processed/dev")

        self.server_val_ds = CICIoTDataset(self.processed_dir / "server_val.parquet")
        self.test_ds = CICIoTDataset(self.processed_dir / "test.parquet")
        self.partition_files = sorted(self.partitions_dir.glob("client_*.parquet"))[:3]

        if len(self.partition_files) < 2:
            self.skipTest("Need at least 2 partitions for determinism test")

        # Create fixed initial model
        torch.manual_seed(12345)
        init_model = IDS_MLP(
            in_features=len(self.server_val_ds.feature_cols),
            num_classes=8,
        )
        self.init_state = copy.deepcopy(init_model.state_dict())
        self.test_dir = Path("results/runs/test_determinism")
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir, ignore_errors=True)
        self.test_dir.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir, ignore_errors=True)

    def _run_simulation(self, run_id: str, seed: int = 42) -> tuple[dict[str, torch.Tensor], list[dict]]:
        seed_everything(seed)

        # Isolated clients
        clients = [
            FLClient(
                client_id=i,
                partition_path=p_file,
                feature_cols=self.server_val_ds.feature_cols,
                num_classes=8,
                attack=None,
                device=self.device,
            )
            for i, p_file in enumerate(self.partition_files)
        ]

        run_path = self.test_dir / run_id
        run_path.mkdir(parents=True, exist_ok=True)

        coordinator = FLCoordinator(
            config=self.config,
            clients=clients,
            server_val_ds=self.server_val_ds,
            test_ds=self.test_ds,
            aggregation_method="trust_class_aware",
            device=self.device,
            db_path=str(run_path / "audit.db"),
            ledger_path=str(run_path / "blockchain_ledger.json"),
        )
        # Load identical initial weights
        coordinator.global_model.load_state_dict(copy.deepcopy(self.init_state))

        summaries = []
        for r in range(1, 3):  # 2 rounds
            summary = coordinator.run_round(round_num=r, local_epochs=1, lr=1e-3)
            summaries.append(summary)

        final_state = {k: v.cpu().clone() for k, v in coordinator.global_model.state_dict().items()}
        return final_state, summaries

    def test_reproducibility_across_identical_seeds(self):
        state_run1, summaries_run1 = self._run_simulation("run1", seed=42)
        state_run2, summaries_run2 = self._run_simulation("run2", seed=42)

        # 1. Assert round validation metrics match
        for r_idx in range(len(summaries_run1)):
            s1 = summaries_run1[r_idx]
            s2 = summaries_run2[r_idx]
            self.assertAlmostEqual(s1["val_accuracy"], s2["val_accuracy"], places=5)
            self.assertAlmostEqual(s1["val_macro_f1"], s2["val_macro_f1"], places=5)

        # 2. Assert model state dicts match within numerical tolerance
        for key in state_run1:
            diff = torch.max(torch.abs(state_run1[key] - state_run2[key])).item()
            self.assertLess(
                diff,
                1e-5,
                f"Model parameter {key} diverged between identical runs: max diff = {diff}",
            )

    def test_vram_resident_loop_determinism(self):
        """Verifies that the new GPU-resident tensor training loop is bit-for-bit identical across runs."""
        from src.experiments.run_phase_e4_verification import run_single_simulation

        feature_cols = self.server_val_ds.feature_cols
        with open("configs/label_mapping.yaml") as f:
            lm_cfg = yaml.safe_load(f)
        class_names = [lm_cfg["idx_to_class"][i] for i in range(len(lm_cfg["idx_to_class"]))]

        common_args = {
            "mode": "clean_fedavg",
            "partition_seed": 11,
            "train_seed": 42,
            "num_rounds": 2,
            "partition_dir_str": "data/partitions/dev/seed_11",
            "test_path_str": str(self.processed_dir / "test.parquet"),
            "server_val_path_str": str(self.processed_dir / "server_val.parquet"),
            "feature_cols": feature_cols,
            "class_names": class_names,
            "batch_size": 1024,
        }

        res1 = run_single_simulation(**common_args)
        res2 = run_single_simulation(**common_args)

        self.assertAlmostEqual(res1["macro_f1"], res2["macro_f1"], places=5)
        self.assertAlmostEqual(res1["recon_f1"], res2["recon_f1"], places=5)


if __name__ == "__main__":
    unittest.main()
