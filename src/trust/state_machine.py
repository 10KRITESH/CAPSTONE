"""
state_machine.py — Client Security State Machine & Shadow Recovery Lifecycle.

States:
  - TRUSTED: Normal full participation (state_factor = 1.0).
  - PROBATION: Reduced aggregation weight based on evidence score (state_factor ∈ [0.2, 0.7]).
  - QUARANTINED: Update evaluated & logged, but NOT aggregated (state_factor = 0.0).

Transitions:
  - Evidence E < 0.40          → TRUSTED
  - 0.40 ≤ E < 0.70            → PROBATION
  - E ≥ 0.70                   → QUARANTINED

Shadow Recovery Lifecycle:
  - QUARANTINED client submits updates for K1 clean rounds → PROBATION.
  - PROBATION client submits updates for K2 clean rounds → TRUSTED.
  - If suspicious behavior recurs, recovery is reset or client is re-quarantined.
"""

from __future__ import annotations

from enum import Enum
import logging
from src.trust.evidence import EvidenceRecord

log = logging.getLogger(__name__)


class ClientState(str, Enum):
    TRUSTED = "TRUSTED"
    PROBATION = "PROBATION"
    QUARANTINED = "QUARANTINED"


class ClientStateMachine:
    """
    Client Security State Machine & Recovery Coordinator.

    Args:
        probation_threshold: Evidence threshold E for entering PROBATION (default: 0.40).
        quarantine_threshold: Evidence threshold E for entering QUARANTINED (default: 0.70).
        k1_recovery_rounds: Clean rounds required to move QUARANTINED → PROBATION (default: 3).
        k2_recovery_rounds: Clean rounds required to move PROBATION → TRUSTED (default: 3).
    """

    def __init__(
        self,
        probation_threshold: float = 0.40,
        quarantine_threshold: float = 0.70,
        k1_recovery_rounds: int = 3,
        k2_recovery_rounds: int = 3,
    ) -> None:
        self.probation_threshold = probation_threshold
        self.quarantine_threshold = quarantine_threshold
        self.k1_recovery_rounds = k1_recovery_rounds
        self.k2_recovery_rounds = k2_recovery_rounds

        self.client_states: dict[str | int, ClientState] = {}
        self.transition_history: list[dict] = []

    def get_state(self, client_id: str | int) -> ClientState:
        return self.client_states.get(client_id, ClientState.TRUSTED)

    def get_state_factor(self, client_id: str | int, evidence_score: float) -> float:
        """
        Return participation weight multiplier [0.0, 1.0].
        - TRUSTED: 1.0
        - PROBATION: gradual state factor = max(0.20, 1.0 - evidence_score)
        - QUARANTINED: 0.0 (excluded from aggregation)
        """
        state = self.get_state(client_id)
        if state == ClientState.TRUSTED:
            return 1.0
        elif state == ClientState.QUARANTINED:
            return 0.0
        else:
            # PROBATION: gradual state factor proportional to evidence
            return max(0.20, round(1.0 - evidence_score, 4))

    def update_state(
        self,
        client_id: str | int,
        evidence_rec: EvidenceRecord,
        round_num: int,
    ) -> tuple[ClientState, bool, str]:
        """
        Evaluate evidence and recovery conditions to update client state.

        Returns:
            (new_state, state_changed, reason)
        """
        current_state = self.get_state(client_id)
        E = evidence_rec.evidence_score
        clean = evidence_rec.consecutive_clean
        bad = evidence_rec.consecutive_bad

        new_state = current_state
        reason = "NO_CHANGE"

        # 1. Check demotion / escalation triggers
        if E >= self.quarantine_threshold:
            new_state = ClientState.QUARANTINED
            reason = f"HIGH_EVIDENCE_SCORE_E={E:.2f}"
        elif E >= self.probation_threshold and current_state == ClientState.TRUSTED:
            new_state = ClientState.PROBATION
            reason = f"EVIDENCE_ELEVATED_E={E:.2f}"

        # 2. Check Shadow Recovery triggers for QUARANTINED or PROBATION clients
        if current_state == ClientState.QUARANTINED:
            if clean >= self.k1_recovery_rounds and E < self.quarantine_threshold:
                new_state = ClientState.PROBATION
                reason = f"SHADOW_RECOVERY_K1_PASSED ({clean} clean rounds)"
            elif bad > 0:
                reason = "RECOVERY_RESET_DUE_TO_SUSPICIOUS_ROUND"

        elif current_state == ClientState.PROBATION:
            if clean >= self.k2_recovery_rounds and E < self.probation_threshold:
                new_state = ClientState.TRUSTED
                reason = f"SHADOW_RECOVERY_K2_PASSED ({clean} clean rounds)"

        state_changed = (new_state != current_state)
        if state_changed:
            self.client_states[client_id] = new_state
            transition_record = {
                "round": round_num,
                "client_id": client_id,
                "old_state": current_state.value,
                "new_state": new_state.value,
                "evidence_score": E,
                "reason": reason,
            }
            self.transition_history.append(transition_record)
            log.info(
                f"Round {round_num} | Client {client_id} State Transition: "
                f"{current_state.value} → {new_state.value} ({reason})"
            )

        return new_state, state_changed, reason
