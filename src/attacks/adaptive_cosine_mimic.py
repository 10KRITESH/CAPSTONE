"""
adaptive_cosine_mimic.py — Adaptive Cosine-Mimicking Attack.

Blends a malicious target update direction with a clean reference direction
(e.g., global model update direction):
    Δ'_i = (1 - beta) * Δ_poison + beta * Δ_ref
This ensures cosine similarity against reference remains above the suspicion threshold
(e.g. >= 0.70) while still inserting targeted class degradation.
"""

from __future__ import annotations

import torch
from src.attacks.base import BaseAttack


class AdaptiveCosineMimicAttack(BaseAttack):
    """
    Adaptive Cosine-Mimicking Attack.

    Args:
        blend_factor: Weight beta given to the clean reference direction (0.0 to 1.0).
        base_scale: Poisoning scale factor for the malicious component.
    """

    def __init__(self, blend_factor: float = 0.4, base_scale: float = -1.0) -> None:
        super().__init__(name="adaptive_cosine_mimic")
        self.blend_factor = blend_factor
        self.base_scale = base_scale

    def poison_update(
        self, update: dict[str, torch.Tensor], round_num: int
    ) -> dict[str, torch.Tensor]:
        if not self.is_active_round(round_num):
            return update

        poisoned = {}
        for k, v in update.items():
            if torch.is_floating_point(v):
                # Blend clean direction with negated/poisoned direction
                clean_dir = v
                poison_dir = v * self.base_scale
                poisoned[k] = (1.0 - self.blend_factor) * poison_dir + self.blend_factor * clean_dir
            else:
                poisoned[k] = v.clone()

        return poisoned
