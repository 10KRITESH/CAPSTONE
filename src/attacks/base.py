"""
base.py — Abstract Base Class for FL Attack Strategies.

Attacks operate at two levels:
  1. Data Level (Poisoning local labels/features before local training)
  2. Model Level (Poisoning model parameter updates Δ after local training)
"""

from __future__ import annotations

from abc import ABC, abstractmethod
import torch
import pandas as pd


class BaseAttack(ABC):
    """Abstract base class for all simulated FL attacks."""

    def __init__(self, name: str, attack_config: dict | None = None) -> None:
        self.name = name
        self.config = attack_config or {}

    def is_active_round(self, round_num: int) -> bool:
        """Check if attack is active for the current FL round. Default: active every round."""
        return True

    def poison_data(self, df: pd.DataFrame, round_num: int) -> pd.DataFrame:
        """
        Apply data-level poisoning (e.g., label flipping) before local training.
        Default: return original DataFrame unmodified.
        """
        return df

    def poison_update(self, update: dict[str, torch.Tensor], round_num: int) -> dict[str, torch.Tensor]:
        """
        Apply update-level poisoning (e.g., scaling or gradient sign flipping) after local training.
        Args:
            update: Client parameter update dictionary Δ_i = w_local - w_global.
            round_num: Current FL round index.
        Default: return update unmodified.
        """
        return update

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}')"
