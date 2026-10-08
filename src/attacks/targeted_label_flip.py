"""
targeted_label_flip.py — Targeted Class Poisoning Attack.

Specifically targets a single attack class (e.g. Reconnaissance -> Benign)
while keeping all other classes clean. This simulates stealthy targeted class degradation,
which is the exact attack scenario class-aware reputation is designed to mitigate.
"""

from __future__ import annotations

import torch
import pandas as pd
from src.attacks.base import BaseAttack


class TargetedLabelFlipAttack(BaseAttack):
    """
    Targeted Label Flip Attack.
    Flips source_class label to target_class label.
    Example: source_class=4 (RECON) -> target_class=0 (BENIGN).
    """

    def __init__(
        self,
        source_class: int = 4,  # e.g., RECON
        target_class: int = 0,  # e.g., BENIGN
        poison_ratio: float = 1.0,
        boost_factor: float = 1.0,
    ) -> None:
        super().__init__(name="targeted_label_flip")
        self.source_class = source_class
        self.target_class = target_class
        self.poison_ratio = poison_ratio
        self.boost_factor = float(boost_factor)

    def poison_update(self, update: dict[str, torch.Tensor], round_num: int) -> dict[str, torch.Tensor]:
        if not self.is_active_round(round_num) or self.boost_factor == 1.0:
            return update

        boosted = {}
        for k, v in update.items():
            if torch.is_floating_point(v):
                boosted[k] = v * self.boost_factor
            else:
                boosted[k] = v
        return boosted

    def poison_data(self, df: pd.DataFrame, round_num: int) -> pd.DataFrame:
        if not self.is_active_round(round_num) or self.poison_ratio <= 0.0:
            return df

        df_poisoned = df.copy()
        mask = df_poisoned["label"] == self.source_class
        source_indices = df_poisoned[mask].index

        if len(source_indices) == 0:
            return df_poisoned

        if self.poison_ratio < 1.0:
            n_flip = int(round(len(source_indices) * self.poison_ratio))
            flip_indices = source_indices[:n_flip]
        else:
            flip_indices = source_indices

        df_poisoned.loc[flip_indices, "label"] = self.target_class
        return df_poisoned
