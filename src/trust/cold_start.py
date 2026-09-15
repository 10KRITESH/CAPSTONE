"""
cold_start.py — Cold-Start & New Participant Policy.

Manages newly joined FL clients:
  - Initializes reputation with a neutral prior R = 0.5 (instead of 1.0 or 0.0).
  - Enforces a mandatory observation window (e.g., K_obs = 3 rounds) before granting full TRUSTED status.
"""

from __future__ import annotations


class ColdStartManager:
    """
    Cold-Start Policy Manager.

    Args:
        observation_rounds: Number of rounds a new client must remain observed (default: 3).
        neutral_prior: Initial reputation score assigned to unobserved classes (default: 0.50).
    """

    def __init__(self, observation_rounds: int = 3, neutral_prior: float = 0.50) -> None:
        self.observation_rounds = observation_rounds
        self.neutral_prior = neutral_prior
        self.client_join_round: dict[str | int, int] = {}
        self.rounds_observed: dict[str | int, int] = {}

    def register_client(self, client_id: str | int, current_round: int) -> None:
        if client_id not in self.client_join_round:
            self.client_join_round[client_id] = current_round
            self.rounds_observed[client_id] = 0

    def record_round(self, client_id: str | int) -> None:
        if client_id in self.rounds_observed:
            self.rounds_observed[client_id] += 1

    def is_in_observation_window(self, client_id: str | int) -> bool:
        """Return True if client is still within mandatory observation window."""
        obs = self.rounds_observed.get(client_id, 0)
        return obs < self.observation_rounds

    def get_initial_reputation_vector(self, class_names: list[str]) -> dict[str, float]:
        """Return neutral prior vector R = 0.5 for all classes."""
        return {cls: self.neutral_prior for cls in class_names}
