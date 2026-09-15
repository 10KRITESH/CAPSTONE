"""
dataset.py — PyTorch Dataset for processed CICIoT2023 parquet files.

Deliberately minimal. Reads a pre-processed parquet file and returns
(feature_tensor, label_tensor) pairs. All heavy preprocessing is done
offline by preprocess.py.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from torch.utils.data import Dataset


class CICIoTDataset(Dataset):
    """
    Wraps a processed .parquet split (train / val / test / server_val).

    Args:
        parquet_path:  Path to the .parquet file.
        feature_cols:  Ordered list of feature column names to use as X.
                       If None, infers from feature_stats JSON in metadata_dir.
        metadata_dir:  Directory containing feature_stats_*.json.
                       Only used when feature_cols is None.
    """

    def __init__(
        self,
        parquet_path: str | Path,
        feature_cols: list[str] | None = None,
        metadata_dir: str | Path = "data/metadata",
    ) -> None:
        parquet_path = Path(parquet_path)
        if not parquet_path.exists():
            raise FileNotFoundError(f"Parquet file not found: {parquet_path}")

        df = pd.read_parquet(parquet_path)

        # Resolve feature columns
        if feature_cols is None:
            feature_cols = self._infer_feature_cols(parquet_path, Path(metadata_dir))
        self.feature_cols = feature_cols

        missing = [c for c in feature_cols if c not in df.columns]
        if missing:
            raise ValueError(f"Feature columns missing from parquet: {missing}")

        # Convert to numpy first (faster than direct tensor from DataFrame)
        # .copy() avoids the non-writable tensor UserWarning from PyTorch
        X = df[feature_cols].to_numpy(dtype=np.float32).copy()
        y = df["label"].to_numpy(dtype=np.int64).copy()

        self.X = torch.from_numpy(X)   # (N, F)
        self.y = torch.from_numpy(y)   # (N,)
        self.class_names: list[str] = df["class_name"].tolist() if "class_name" in df.columns else []

    # ── Private helpers ───────────────────────────────────────────────────────

    @staticmethod
    def _infer_feature_cols(parquet_path: Path, metadata_dir: Path) -> list[str]:
        """Try dev then full feature_stats JSON to resolve feature columns."""
        for suffix in ("dev", "full"):
            stats_path = metadata_dir / f"feature_stats_{suffix}.json"
            if stats_path.exists():
                with open(stats_path) as f:
                    return json.load(f)["feature_columns"]
        raise FileNotFoundError(
            "feature_cols not provided and no feature_stats JSON found in "
            f"{metadata_dir}. Pass feature_cols explicitly."
        )

    # ── Dataset API ───────────────────────────────────────────────────────────

    def __len__(self) -> int:
        return len(self.y)

    def __getitem__(self, idx: int) -> tuple[torch.Tensor, torch.Tensor]:
        return self.X[idx], self.y[idx]

    # ── Utilities ─────────────────────────────────────────────────────────────

    @property
    def num_features(self) -> int:
        return self.X.shape[1]

    @property
    def num_classes(self) -> int:
        return int(self.y.max().item()) + 1

    def class_weights(self, total_classes: int | None = None) -> torch.Tensor:
        """
        Inverse-frequency class weights for CrossEntropyLoss.

        Args:
            total_classes: Total number of classes in the project (e.g. 8).
                           Must match the model's num_classes so the weight
                           tensor shape aligns with CrossEntropyLoss expectations.
                           Defaults to the max label index seen in this split + 1.
        Handles missing classes gracefully (weight=1.0 so they get neutral weighting).
        """
        n = total_classes if total_classes is not None else self.num_classes
        counts = torch.bincount(self.y, minlength=n).float()
        # Classes present → inverse-frequency weight; absent → 1.0 (neutral)
        weights = torch.where(
            counts > 0,
            counts.sum() / (counts * n),
            torch.ones(n),
        )
        return weights

    def sample_weights(self, total_classes: int | None = None) -> torch.Tensor:
        """Per-sample weights for WeightedRandomSampler (inverse class freq)."""
        cw = self.class_weights(total_classes=total_classes)
        return cw[self.y]

    def __repr__(self) -> str:
        return (
            f"CICIoTDataset(n={len(self):,}, features={self.num_features}, "
            f"classes={self.num_classes})"
        )
