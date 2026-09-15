"""
src/trust — Multi-signal update validation, per-class reputation, temporal evidence, and client state machine modules.
"""

from src.trust.update_metrics import (
    compute_cosine_similarity,
    compute_robust_norm_score,
    compute_geometric_median_reference,
    flatten_update,
)
from src.trust.validator import UpdateValidator, ValidationResult
from src.trust.reputation import PerClassReputationManager
from src.trust.cold_start import ColdStartManager
from src.trust.evidence import TemporalEvidenceTracker, EvidenceRecord
from src.trust.state_machine import ClientStateMachine, ClientState

__all__ = [
    "compute_cosine_similarity",
    "compute_robust_norm_score",
    "compute_geometric_median_reference",
    "flatten_update",
    "UpdateValidator",
    "ValidationResult",
    "PerClassReputationManager",
    "ColdStartManager",
    "TemporalEvidenceTracker",
    "EvidenceRecord",
    "ClientStateMachine",
    "ClientState",
]
