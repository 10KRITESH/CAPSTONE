"""
client.py — Simulated FL Client.

Each client:
  - Manages its own local partition of CICIoT2023 data.
  - Receives global model parameters from the coordinator.
  - Optionally applies data-level or model-level attacks if configured as malicious.
  - Performs local SGD/Adam training for E epochs.
  - Computes parameter update Δ_i = w_local - w_global.
  - Returns update, sample count, and local metrics to the coordinator.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset

from src.attacks.base import BaseAttack
from src.model.mlp import IDS_MLP

log = logging.getLogger(__name__)


class FLClient:
    """
    Simulated FL Client.

    Args:
        client_id: Integer or string identifier (e.g., 0, 'client_00').
        partition_path: Path to client's local parquet file.
        feature_cols: List of ordered feature column names.
        num_classes: Number of classification targets (8).
        attack: Optional BaseAttack instance if client is malicious.
        device: PyTorch compute device (cpu / cuda).
    """

    def __init__(
        self,
        client_id: int | str,
        partition_path: str | Path,
        feature_cols: list[str],
        num_classes: int = 8,
        attack: Optional[BaseAttack] = None,
        device: torch.device | None = None,
    ) -> None:
        self.client_id = client_id
        self.partition_path = Path(partition_path)
        self.feature_cols = feature_cols
        self.num_classes = num_classes
        self.attack = attack
        self.device = device or torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # Load raw client data partition into memory
        if not self.partition_path.exists():
            raise FileNotFoundError(f"Client partition file not found: {self.partition_path}")
        self.df_raw = pd.read_parquet(self.partition_path)
        self.num_samples = len(self.df_raw)

    def train_local(
        self,
        global_model: IDS_MLP,
        local_epochs: int = 1,
        batch_size: int = 512,
        lr: float = 1e-3,
        weight_decay: float = 1e-4,
        round_num: int = 1,
    ) -> tuple[dict[str, torch.Tensor], int, dict]:
        """
        Perform local training and return parameter update.

        Returns:
            update: Dict mapping param_name -> Δ_i = (w_local - w_global)
            num_samples: Total training samples on this client
            metrics: Local training metrics (loss, accuracy)
        """
        # 1. Apply data-level attack if malicious
        df_train = self.df_raw
        if self.attack is not None:
            df_train = self.attack.poison_data(df_train, round_num=round_num)

        # 2. Build local PyTorch TensorDataset & DataLoader
        X_np = df_train[self.feature_cols].to_numpy(dtype="float32").copy()
        y_np = df_train["label"].to_numpy(dtype="int64").copy()

        X_tensor = torch.from_numpy(X_np)
        y_tensor = torch.from_numpy(y_np)

        # ── BUG FIX: GPU pre-load optimisation ───────────────────────────────
        # Move the client's partition to VRAM once instead of transferring each
        # batch through PCIe. Only when dataset fits comfortably in free VRAM.
        dataset_mb = (X_tensor.nelement() * 4) / 1e6
        vram_free_mb = (
            (torch.cuda.get_device_properties(0).total_memory - torch.cuda.memory_reserved(0)) / 1e6
            if self.device.type == "cuda" else 0
        )
        if self.device.type == "cuda" and dataset_mb < vram_free_mb * 0.20:
            X_tensor = X_tensor.to(self.device)
            y_tensor = y_tensor.to(self.device)
            dataset = TensorDataset(X_tensor, y_tensor)
            loader = DataLoader(
                dataset, batch_size=batch_size, shuffle=True,
                num_workers=0, drop_last=(len(dataset) > batch_size)
            )
        else:
            dataset = TensorDataset(X_tensor, y_tensor)
            loader = DataLoader(
                dataset, batch_size=batch_size, shuffle=True,
                drop_last=(len(dataset) > batch_size)
            )


        # 3. Instantiate local model initialized with global weights
        local_model = IDS_MLP(**global_model.config).to(self.device)
        local_model.load_state_dict(global_model.state_dict())
        global_weights = {k: v.clone().detach() for k, v in global_model.state_dict().items()}

        optimizer = torch.optim.Adam(local_model.parameters(), lr=lr, weight_decay=weight_decay)
        criterion = nn.CrossEntropyLoss()

        # 4. Local epoch training loop
        local_model.train()
        total_loss = 0.0
        correct = 0
        total = 0

        for epoch in range(local_epochs):
            for X_b, y_b in loader:
                X_b, y_b = X_b.to(self.device), y_b.to(self.device)
                optimizer.zero_grad(set_to_none=True)
                logits = local_model(X_b)
                loss = criterion(logits, y_b)
                loss.backward()
                optimizer.step()

                total_loss += loss.item() * len(y_b)
                correct += (logits.argmax(dim=1) == y_b).sum().item()
                total += len(y_b)

        avg_loss = total_loss / max(1, total)
        accuracy = correct / max(1, total)

        # 5. Compute update: Δ_i = w_local - w_global (for floating-point parameters)
        local_weights = local_model.state_dict()
        update = {}
        for k in global_weights.keys():
            if torch.is_floating_point(global_weights[k]):
                update[k] = (local_weights[k].cpu() - global_weights[k].cpu())
            else:
                update[k] = local_weights[k].cpu()

        # 6. Apply model-level attack if malicious
        if self.attack is not None:
            update = self.attack.poison_update(update, round_num=round_num)

        metrics = {
            "client_id": self.client_id,
            "loss": avg_loss,
            "accuracy": accuracy,
            "is_malicious": self.attack is not None,
            "attack_type": self.attack.name if self.attack else None,
        }

        return update, self.num_samples, metrics
