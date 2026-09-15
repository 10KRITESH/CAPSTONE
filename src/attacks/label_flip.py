"""
label_flip.py — Untargeted Label Flipping Attack.

Flips local dataset labels according to a deterministic or random permutation.
For example: y_poisoned = (y + flip_offset) % num_classes
"""

from __future__ import annotations

import pandas as pd
from src.attacks.base import BaseAttack


class UntargetedLabelFlipAttack(BaseAttack):
    """
    Untargeted Label Flipping Attack.
    Modifies local labels by shifting class indices: y_new = (y + offset) % num_classes.
    """

    def __init__(
        self,
        num_classes: int = 8,
        flip_offset: int = 1,
        attack_ratio: float = 1.0,
        seed: int = 42,
    ) -> None:
        super().__init__(name="untargeted_label_flip")
        self.num_classes = num_classes
        self.flip_offset = flip_offset
        self.attack_ratio = attack_ratio
        self.seed = seed

    def poison_data(self, df: pd.DataFrame, round_num: int) -> pd.DataFrame:
        if not self.is_active_round(round_num) or self.attack_ratio <= 0.0:
            return df

        df_poisoned = df.copy()
        if self.attack_ratio >= 1.0:
            df_poisoned["label"] = (df_poisoned["label"] + self.flip_offset) % self.num_classes
        else:
            # Sample a subset of rows to flip labels
            sample_idx = df_poisoned.sample(
                frac=self.attack_ratio, random_state=self.seed + round_num
            ).index
            df_poisoned.loc[sample_idx, "label"] = (
                df_poisoned.loc[sample_idx, "label"] + self.flip_offset
            ) % self.num_classes

        return df_poisoned
