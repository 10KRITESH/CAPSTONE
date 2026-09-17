"""
reputation.py — Per-Attack-Class Reputation Engine.

Maintains a reputation vector R_t(i, c) ∈ [0, 1] for each client i across each attack class c.
Uses EWMA (Exponentially Weighted Moving Average) update:
    Q_t(i, c) = wp * performance_quality + ws * similarity_quality + wn * norm_quality
    R_t(i, c) = (1 - eta) * R_{t-1}(i, c) + eta * Q_t(i, c)

Also dampens updates on low-support attack classes to avoid penalizing clients unfairly
when server validation sample size for a class is statistically small.
"""

from __future__ import annotations

import logging
from typing import Optional

from src.trust.validator import ValidationResult

log = logging.getLogger(__name__)


class PerClassReputationManager:
    """
    Per-Attack-Class Reputation Manager.

    Args:
        class_names: List of class names (8).
        eta: EWMA update weight (default: 0.20).
        wp: Weight for semantic performance impact signal (default: 0.60).
        ws: Weight for cosine similarity signal (default: 0.25).
        wn: Weight for update norm Z-score signal (default: 0.15).
        low_support_classes: Optional set of class names flagged as low support.
        low_support_dampening: Penalty dampening factor for low support classes (default: 0.30).
    """

    def __init__(
        self,
        class_names: list[str],
        eta: float = 0.20,
        wp: float = 0.60,
        ws: float = 0.25,
        wn: float = 0.15,
        low_support_classes: Optional[set[str]] = None,
        low_support_dampening: float = 0.30,
    ) -> None:
        self.class_names = class_names
        self.eta = eta
        self.wp = wp
        self.ws = ws
        self.wn = wn
        self.low_support_classes = low_support_classes or set()
        self.low_support_dampening = low_support_dampening

        # Reputation table: client_id -> {class_name: score_in_[0, 1]}
        self.reputation_table: dict[str | int, dict[str, float]] = {}

    def get_reputation(self, client_id: str | int) -> dict[str, float]:
        """Return reputation vector for client_id. Defaults to 1.0 (trusted) or neutral prior."""
        if client_id not in self.reputation_table:
            self.reputation_table[client_id] = {cls: 1.0 for cls in self.class_names}
        return self.reputation_table[client_id].copy()

    def get_base_trust(self, client_id: str | int) -> float:
        """Scalar base trust = mean reputation across all attack classes."""
        rep = self.get_reputation(client_id)
        return float(sum(rep.values()) / max(1, len(rep)))

    def update_reputation(
        self, client_id: str | int, val_result: ValidationResult
    ) -> dict[str, float]:
        """Update client's per-attack-class reputation vector using round validation result."""
        current_rep = self.get_reputation(client_id)

        # 1. Cosine similarity quality: cos_sim in [-1, 1] mapped to [0, 1]
        sim_q = max(0.0, min(1.0, (val_result.cosine_sim + 1.0) / 2.0))

        # 2. Update norm quality: Penalize large Z-scores (|Z| > 2)
        norm_q = max(0.0, min(1.0, 1.0 - min(1.0, abs(val_result.norm_z_score) / 4.0)))

        updated_rep = {}
        for cls in self.class_names:
            # 3. Per-class performance quality: impact in [-1, 1] mapped to [0, 1]
            imp = val_result.per_class_f1_impact.get(cls, 0.0)

            # Dampen negative impact penalty if class is low-support
            if cls in self.low_support_classes and imp < 0:
                imp *= self.low_support_dampening

            if imp < 0:
                perf_q = max(0.0, min(1.0, 0.5 + 3.0 * imp))
            else:
                perf_q = max(0.0, min(1.0, 0.5 + imp))

            # Quality composite score Q(i, c)
            q_score = (self.wp * perf_q) + (self.ws * sim_q) + (self.wn * norm_q)
            q_score = max(0.0, min(1.0, q_score))

            # EWMA update: R_t(i, c) = (1 - eta) * R_{t-1} + eta * Q_t
            r_prev = current_rep[cls]
            effective_eta = 0.35 if imp < -0.05 else self.eta
            r_new = (1.0 - effective_eta) * r_prev + effective_eta * q_score
            updated_rep[cls] = round(max(0.0, min(1.0, r_new)), 4)

        self.reputation_table[client_id] = updated_rep
        return updated_rep.copy()
