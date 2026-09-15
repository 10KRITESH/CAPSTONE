"""
on_off.py — Intermittent / On-Off Attacker Wrapper.

Wraps any base attack strategy (label flip, targeted, model poisoning)
and toggles attack behavior on scheduled FL rounds (e.g., active for 2 rounds, clean for 3 rounds).
Tests whether temporal evidence tracking can detect deceptive / fluctuating attackers.
"""

from __future__ import annotations

import pandas as pd
import torch
from src.attacks.base import BaseAttack


class OnOffAttackWrapper(BaseAttack):
    """
    On-Off Intermittent Attack Wrapper.

    Args:
        wrapped_attack: Instance of BaseAttack to trigger when active.
        active_rounds: List of specific round numbers where attack is active,
                       OR pattern string like 'periodic', 'probability'.
        period: Round interval for periodic attack (e.g. active every Nth round).
    """

    def __init__(
        self,
        wrapped_attack: BaseAttack,
        active_rounds: list[int] | None = None,
        period: int = 3,
    ) -> None:
        super().__init__(name=f"on_off_{wrapped_attack.name}")
        self.wrapped_attack = wrapped_attack
        self.active_rounds = set(active_rounds) if active_rounds is not None else None
        self.period = period

    def is_active_round(self, round_num: int) -> bool:
        if self.active_rounds is not None:
            return round_num in self.active_rounds
        # Default periodic schedule: active on rounds matching round_num % period == 0
        return (round_num % self.period) == 0

    def poison_data(self, df: pd.DataFrame, round_num: int) -> pd.DataFrame:
        if self.is_active_round(round_num):
            return self.wrapped_attack.poison_data(df, round_num)
        return df

    def poison_update(
        self, update: dict[str, torch.Tensor], round_num: int
    ) -> dict[str, torch.Tensor]:
        if self.is_active_round(round_num):
            return self.wrapped_attack.poison_update(update, round_num)
        return update
