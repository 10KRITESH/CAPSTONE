"""
collusion_detector.py — Sub-Cluster Collusion Detection Engine.

Detects coordinated Byzantine adversaries who submit mutually correlated model updates
designed to jointly steer the global model while evading single-update anomaly checks.

Core Mechanics:
  1. Construct pairwise cosine similarity graph S_ij = cos(Δw_i, Δw_j) across all clients.
  2. Identify dense sub-groups where pairwise similarity exceeds intra-cohort spread.
  3. Track sub-cluster persistence across rounds.
  4. Compute a calibrated collusion penalty u_i in [0, 1] for flagged participants.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
import numpy as np
import torch

from src.trust.update_metrics import flatten_update

log = logging.getLogger(__name__)


@dataclass
class CollusionGroup:
    group_id: str
    member_client_ids: set[int | str]
    avg_pairwise_sim: float
    rounds_persisted: int = 1
    divergence_from_ref: float = 0.0


class SubClusterCollusionDetector:
    """
    Cross-Client Sub-Cluster Collusion Detector.

    Args:
        similarity_threshold: Minimum pairwise cosine similarity to consider two updates correlated (default: 0.88).
        min_group_size: Minimum number of colluding clients to form a suspicious group (default: 2).
        divergence_threshold: Maximum cosine similarity to geometric median to trigger collusion flag (default: 0.65).
        decay_factor: Temporal memory decay for collusion persistence (default: 0.85).
    """

    def __init__(
        self,
        similarity_threshold: float = 0.88,
        min_group_size: int = 2,
        divergence_threshold: float = 0.65,
        decay_factor: float = 0.85,
    ) -> None:
        self.similarity_threshold = similarity_threshold
        self.min_group_size = min_group_size
        self.divergence_threshold = divergence_threshold
        self.decay_factor = decay_factor

        self.persisted_groups: dict[str, CollusionGroup] = {}
        self.client_collusion_scores: dict[int | str, float] = {}
        self.pairwise_matrix_cache: np.ndarray | None = None

    def analyze_updates(
        self,
        updates: list[dict[str, torch.Tensor]],
        client_ids: list[int | str],
        reference_flat: torch.Tensor,
        round_num: int,
    ) -> dict[int | str, float]:
        """
        Analyze submitted client updates for coordinated multi-client collusion.

        Returns:
            dict mapping client_id -> collusion_penalty u_i in [0.0, 1.0]
        """
        num_clients = len(client_ids)
        if num_clients < self.min_group_size:
            return {c_id: 0.0 for c_id in client_ids}

        # 1. Flatten all updates into 1D vectors
        flat_updates = [flatten_update(u) for u in updates]

        # 2. Compute full pairwise cosine similarity matrix S_ij
        S = np.ones((num_clients, num_clients), dtype=np.float32)
        ref_sims = np.zeros(num_clients, dtype=np.float32)
        ref_norm = torch.norm(reference_flat).item()

        for i in range(num_clients):
            u_i = flat_updates[i]
            norm_i = torch.norm(u_i).item()

            if norm_i > 1e-8 and ref_norm > 1e-8:
                cos_ref = (torch.dot(u_i, reference_flat) / (norm_i * ref_norm)).item()
                ref_sims[i] = float(np.clip(cos_ref, -1.0, 1.0))
            else:
                ref_sims[i] = 1.0

            for j in range(i + 1, num_clients):
                u_j = flat_updates[j]
                norm_j = torch.norm(u_j).item()
                if norm_i > 1e-8 and norm_j > 1e-8:
                    cos_ij = (torch.dot(u_i, u_j) / (norm_i * norm_j)).item()
                    cos_ij = float(np.clip(cos_ij, -1.0, 1.0))
                else:
                    cos_ij = 0.0
                S[i, j] = cos_ij
                S[j, i] = cos_ij

        self.pairwise_matrix_cache = S

        # 3. Find connected components (tight sub-clusters) among suspicious diverging clients
        visited = set()
        candidate_groups: list[set[int]] = []

        for i in range(num_clients):
            if i in visited:
                continue
            # A client is a candidate for collusion analysis if its direction diverges from the median reference
            if ref_sims[i] < self.divergence_threshold:
                group = {i}
                for j in range(num_clients):
                    if i != j and S[i, j] >= self.similarity_threshold:
                        group.add(j)

                if len(group) >= self.min_group_size:
                    visited.update(group)
                    candidate_groups.append(group)

        # 4. Calculate per-client collusion penalty u_i
        current_penalties: dict[int | str, float] = {c_id: 0.0 for c_id in client_ids}

        for group_indices in candidate_groups:
            group_cids = [client_ids[idx] for idx in group_indices]
            
            # Compute average intra-group similarity
            pair_sims = []
            for i in group_indices:
                for j in group_indices:
                    if i < j:
                        pair_sims.append(S[i, j])
            avg_sim = float(np.mean(pair_sims)) if pair_sims else 1.0
            avg_div = float(np.mean([1.0 - ref_sims[idx] for idx in group_indices]))

            # Base penalty derived from similarity tightness + divergence from reference
            raw_penalty = min(1.0, 0.6 * avg_sim + 0.4 * avg_div)

            for cid in group_cids:
                # Accumulate with temporal persistence
                prev_score = self.client_collusion_scores.get(cid, 0.0)
                score = self.decay_factor * prev_score + (1.0 - self.decay_factor) * raw_penalty
                self.client_collusion_scores[cid] = float(np.clip(score, 0.0, 1.0))
                current_penalties[cid] = self.client_collusion_scores[cid]
                log.warning(
                    f"[Collusion Alert] Round {round_num}: Client {cid} flagged in collusion group "
                    f"(Intra-Group Sim={avg_sim:.3f}, Penalty={score:.3f})"
                )

        # Decay scores for clients not in any collusion group this round
        for idx, cid in enumerate(client_ids):
            if cid not in [client_ids[i] for g in candidate_groups for i in g]:
                prev_score = self.client_collusion_scores.get(cid, 0.0)
                self.client_collusion_scores[cid] = prev_score * self.decay_factor
                current_penalties[cid] = self.client_collusion_scores[cid]

        return current_penalties
