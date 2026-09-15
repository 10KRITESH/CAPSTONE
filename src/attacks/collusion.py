"""
collusion.py — Collusion Group Attack.

Coordinates a group of K malicious clients to attack the exact same target class
in synchronized rounds with correlated magnitudes to test defense resistance against
coordinated adversarial pressure.
"""

from __future__ import annotations

import pandas as pd
import torch
from src.attacks.base import BaseAttack


class CollusionGroupAttack(BaseAttack):
    """
    Collusion Group Attack.

    Args:
        collusion_group_ids: List of client IDs participating in the collusion group.
        source_class: Target attack class to poison (e.g. 4 = RECON).
        target_class: Target label to flip to (e.g. 0 = BENIGN).
        scale_factor: Update scaling factor for group members.
    """

    def __init__(
        self,
        collusion_group_ids: list[int | str],
        source_class: int = 4,
        target_class: int = 0,
        scale_factor: float = -1.5,
    ) -> None:
        super().__init__(name="collusion_group")
        self.collusion_group_ids = set(collusion_group_ids)
        self.source_class = source_class
        self.target_class = target_class
        self.scale_factor = scale_factor

    def poison_data(self, df: pd.DataFrame, round_num: int) -> pd.DataFrame:
        if not self.is_active_round(round_num):
            return df

        df_poisoned = df.copy()
        mask = df_poisoned["label"] == self.source_class
        df_poisoned.loc[mask, "label"] = self.target_class
        return df_poisoned

    def poison_update(
        self, update: dict[str, torch.Tensor], round_num: int
    ) -> dict[str, torch.Tensor]:
        if not self.is_active_round(round_num):
            return update

        poisoned = {}
        for k, v in update.items():
            if torch.is_floating_point(v):
                poisoned[k] = v * self.scale_factor
            else:
                poisoned[k] = v.clone()
        return poisoned
