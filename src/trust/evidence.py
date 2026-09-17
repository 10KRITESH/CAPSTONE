"""
evidence.py — Participant-Level Temporal Evidence Accumulator.

Calculates persistent evidence score E_t(i):
    E_t(i) = rho * E_{t-1}(i) + (1 - rho) * bad_round(i, t)
where:
    bad_round = 1 if suspicious_flags present or reputation drops below threshold, else 0.

Also tracks:
  - Consecutive clean rounds
  - Consecutive bad rounds
  - Total suspicious rounds
  - Total participating rounds
"""

from __future__ import annotations

from dataclasses import dataclass
from src.trust.validator import ValidationResult


@dataclass
class EvidenceRecord:
    client_id: str | int
    evidence_score: float = 0.0
    consecutive_bad: int = 0
    consecutive_clean: int = 0
    total_bad: int = 0
    total_rounds: int = 0
    last_suspicious_round: int = -1


class TemporalEvidenceTracker:
    """
    Temporal Evidence Accumulator.

    Args:
        rho: Memory retention factor (default: 0.80).
        reputation_drop_threshold: Reputation score below which a class triggers bad_round (default: 0.40).
    """

    def __init__(self, rho: float = 0.80, reputation_drop_threshold: float = 0.40) -> None:
        self.rho = rho
        self.reputation_drop_threshold = reputation_drop_threshold
        self.records: dict[str | int, EvidenceRecord] = {}

    def get_record(self, client_id: str | int) -> EvidenceRecord:
        if client_id not in self.records:
            self.records[client_id] = EvidenceRecord(client_id=client_id)
        return self.records[client_id]

    def update_evidence(
        self,
        client_id: str | int,
        val_result: ValidationResult,
        reputation_vector: dict[str, float],
    ) -> EvidenceRecord:
        rec = self.get_record(client_id)
        rec.total_rounds += 1

        # Critical anomaly flags (indicative of active poisoning / scaling / sign-inversion attacks)
        is_adversarial_cosine = (val_result.cosine_sim < -0.60) and (val_result.global_f1_impact < -0.03)
        has_critical_flags = any(
            f in val_result.suspicious_flags
            for f in ["ABNORMAL_UPDATE_NORM", "GLOBAL_PERFORMANCE_DEGRADATION"]
        ) or is_adversarial_cosine
        has_class_flags = any(f.startswith("TARGET_CLASS_DEGRADATION_") for f in val_result.suspicious_flags)

        past_observation = rec.total_rounds > 3
        has_overall_low_rep = (
            past_observation
            and (sum(reputation_vector.values()) / max(1, len(reputation_vector))) < self.reputation_drop_threshold
        )
        has_flagged_class_drop = (
            past_observation
            and any(
                reputation_vector.get(f.replace("TARGET_CLASS_DEGRADATION_", ""), 1.0) < self.reputation_drop_threshold
                for f in val_result.suspicious_flags if f.startswith("TARGET_CLASS_DEGRADATION_")
            )
        )

        # In observation window (rounds 1-3), only critical anomalies trigger bad_round.
        # After observation window, targeted degradation with low reputation or global low reputation also triggers.
        if past_observation:
            is_bad = 1 if (has_critical_flags or has_flagged_class_drop or has_overall_low_rep) else 0
        else:
            is_bad = 1 if has_critical_flags else 0

        # Update EWMA evidence score: E_t = rho * E_{t-1} + (1 - rho) * bad_round
        rec.evidence_score = round(
            (self.rho * rec.evidence_score) + ((1.0 - self.rho) * is_bad), 4
        )

        if is_bad:
            rec.consecutive_bad += 1
            rec.consecutive_clean = 0
            rec.total_bad += 1
            rec.last_suspicious_round = val_result.round_num
        else:
            rec.consecutive_clean += 1
            rec.consecutive_bad = 0

        return rec
