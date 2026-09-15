"""
adaptive_norm_clip.py — Adaptive Norm-Clipping Attack.

An attacker that attempts to bypass naive update magnitude (norm) anomaly detectors.
Calculates the target poisoning update Δ_i, measures its ||Δ_i||_2 norm, and clips/scales
it so that its norm equals a target benchmark (e.g. population median norm), maintaining
poisoning direction while avoiding magnitude outlier detection.
"""

from __future__ import annotations

import torch
from src.attacks.base import BaseAttack


class AdaptiveNormClipAttack(BaseAttack):
    """
    Adaptive Norm-Clipping Poisoning Attack.

    Args:
        target_norm: Maximum allowed L2 norm for the update tensor.
        base_poison_scale: Initial scale factor before norm constraint.
    """

    def __init__(self, target_norm: float = 1.5, base_poison_scale: float = -1.0) -> None:
        super().__init__(name="adaptive_norm_clip")
        self.target_norm = target_norm
        self.base_poison_scale = base_poison_scale

    def poison_update(
        self, update: dict[str, torch.Tensor], round_num: int
    ) -> dict[str, torch.Tensor]:
        if not self.is_active_round(round_num):
            return update

        # 1. Apply base poisoning update (e.g., gradient negation)
        poisoned = {k: v * self.base_poison_scale for k, v in update.items()}

        # 2. Compute total L2 norm of the update
        total_sq = sum(v.pow(2).sum().item() for v in poisoned.values() if torch.is_floating_point(v))
        total_norm = total_sq ** 0.5

        # 3. Clip norm if it exceeds target_norm
        if total_norm > self.target_norm and total_norm > 1e-8:
            scaling = self.target_norm / total_norm
            for k, v in poisoned.items():
                if torch.is_floating_point(v):
                    poisoned[k] = v * scaling

        return poisoned
