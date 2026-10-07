"""
adaptive_cosine_mimic.py — Adaptive Cosine-Mimicking Attack.

Blends a malicious poisoning direction with a clean reference direction (geometric
median of benign updates approximated by the current round's update mean) so that
the cosine similarity vs. the reference stays above a suspicion threshold while still
inserting targeted class degradation:

    Δ'_i = normalize((1 - beta) * Δ_poison + beta * Δ_ref)  ×  ||Δ_ref||

The attack is instantiated once per round at the coordinator level, which must call
`set_reference(ref_flat)` with the flattened mean of *all* updates before this
client's update is processed.  When no reference has been injected (e.g., in an
offline test), the attack degrades gracefully to signed negation with norm matching.

Design rationale:
  - beta = 0.40 keeps cosine sim ≥ ~0.70 against the reference for most model depths.
  - base_scale = -1.0 inverts gradient direction in the poisoned component.
  - Final output is re-normalised to the reference norm so the update does NOT
    trigger norm-anomaly detectors either (mimicking both direction AND magnitude).
"""

from __future__ import annotations

import torch
from src.attacks.base import BaseAttack


class AdaptiveCosineMimicAttack(BaseAttack):
    """
    Adaptive Cosine-Mimicking Poisoning Attack.

    Args:
        blend_factor: Weight beta given to the clean reference direction (0.0–1.0).
            Higher = safer (looks cleaner) but weaker poisoning effect.
            Default 0.40 keeps cosine similarity ≈ 0.70 against reference.
        base_scale: Poisoning scale applied to the malicious component before blending.
            Negative = gradient inversion (targets RECON→BENIGN confusion).
    """

    def __init__(self, blend_factor: float = 0.40, base_scale: float = -1.0) -> None:
        super().__init__(name="adaptive_cosine_mimic")
        self.blend_factor = blend_factor
        self.base_scale = base_scale
        # Set externally each round by the simulator / coordinator
        self._ref_flat: torch.Tensor | None = None

    # ── Reference injection ───────────────────────────────────────────────────

    def set_reference(self, ref_flat: torch.Tensor) -> None:
        """
        Inject the round's reference direction (flattened mean of all updates).
        Must be called BEFORE poison_update() for each round.

        Args:
            ref_flat: 1-D float tensor of the geometric median / mean update.
        """
        self._ref_flat = ref_flat.detach().clone().float()

    # ── Attack core ───────────────────────────────────────────────────────────

    def poison_update(
        self, update: dict[str, torch.Tensor], round_num: int
    ) -> dict[str, torch.Tensor]:
        if not self.is_active_round(round_num):
            return update

        # ── Flatten the client's own update ──────────────────────────────────
        keys_float = [k for k, v in update.items() if torch.is_floating_point(v)]
        keys_int   = [k for k, v in update.items() if not torch.is_floating_point(v)]

        update_flat = torch.cat([update[k].reshape(-1).float() for k in keys_float])

        # ── Poisoned direction: negated (or scaled) gradient ─────────────────
        poison_flat = update_flat * self.base_scale

        # ── Reference direction (clean population mean) ───────────────────────
        if self._ref_flat is not None and self._ref_flat.numel() == update_flat.numel():
            ref_flat = self._ref_flat
        else:
            # Fallback: use the original update itself as reference
            # (attack still runs but won't mimic a true population mean)
            ref_flat = update_flat.clone()

        # ── Blend: Δ' = (1-β)·Δ_poison + β·Δ_ref ───────────────────────────
        blended_flat = (1.0 - self.blend_factor) * poison_flat + self.blend_factor * ref_flat

        # ── Re-scale output to reference norm (evades norm anomaly detector) ─
        ref_norm = ref_flat.norm(p=2).item()
        blended_norm = blended_flat.norm(p=2).item()
        if blended_norm > 1e-9 and ref_norm > 1e-9:
            blended_flat = blended_flat * (ref_norm / blended_norm)

        # ── Unflatten back into the update dict ──────────────────────────────
        poisoned: dict[str, torch.Tensor] = {}
        offset = 0
        for k in keys_float:
            numel = update[k].numel()
            poisoned[k] = blended_flat[offset: offset + numel].reshape(update[k].shape).to(update[k].dtype)
            offset += numel

        for k in keys_int:
            poisoned[k] = update[k].clone()

        return poisoned
