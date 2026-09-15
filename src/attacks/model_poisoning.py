"""
model_poisoning.py — Model Update Poisoning Attack.

Poisons model update vector Δ_i = w_local - w_global directly after local training.
Supports:
  - Sign inversion attack: Δ' = -gamma * Δ
  - Update scaling attack: Δ' = gamma * Δ (large magnitude disruption)
"""

from __future__ import annotations

import torch
from src.attacks.base import BaseAttack


class ModelPoisoningAttack(BaseAttack):
    """
    Model Update Poisoning Attack.
    Modifies local model update Δ_i: Δ' = scale_factor * Δ_i.
    If scale_factor is negative (e.g. -1.0, -2.0), performs sign inversion (gradient negation).
    If scale_factor > 1.0 (e.g. 5.0, 10.0), scales up the update to dominate aggregation.
    """

    def __init__(self, scale_factor: float = -1.0) -> None:
        super().__init__(name="model_update_poisoning")
        self.scale_factor = scale_factor

    def poison_update(
        self, update: dict[str, torch.Tensor], round_num: int
    ) -> dict[str, torch.Tensor]:
        if not self.is_active_round(round_num):
            return update

        poisoned_update = {}
        for k, v in update.items():
            poisoned_update[k] = v * self.scale_factor
        return poisoned_update
