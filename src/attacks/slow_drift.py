"""
slow_drift.py — Slow-Drift Adaptive Poisoning Attack.

Applies tiny, cumulative parameter shifts across multiple FL rounds.
The update magnitude per round remains within normal variance, making single-round validation
detectors pass, but causes progressive degradation over time. Directly tests the temporal
evidence accumulation mechanism.
"""

from __future__ import annotations

import torch
from src.attacks.base import BaseAttack


class SlowDriftAttack(BaseAttack):
    """
    Slow-Drift Poisoning Attack.

    Args:
        drift_magnitude: Small scale factor applied per round (e.g. 0.05 to 0.15).
    """

    def __init__(self, drift_magnitude: float = 0.10) -> None:
        super().__init__(name="slow_drift")
        self.drift_magnitude = drift_magnitude

    def poison_update(
        self, update: dict[str, torch.Tensor], round_num: int
    ) -> dict[str, torch.Tensor]:
        if not self.is_active_round(round_num):
            return update

        poisoned = {}
        for k, v in update.items():
            if torch.is_floating_point(v):
                # Add a small persistent adversarial perturbation
                drift = torch.sign(v) * self.drift_magnitude * (v.abs().mean() + 1e-6)
                poisoned[k] = v - drift
            else:
                poisoned[k] = v.clone()

        return poisoned
