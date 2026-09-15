"""
src/attacks — Malicious client attack simulation module.
Includes naive, adaptive, and collusive attack strategies.
"""

from src.attacks.base import BaseAttack
from src.attacks.label_flip import UntargetedLabelFlipAttack
from src.attacks.targeted_label_flip import TargetedLabelFlipAttack
from src.attacks.model_poisoning import ModelPoisoningAttack
from src.attacks.on_off import OnOffAttackWrapper
from src.attacks.adaptive_norm_clip import AdaptiveNormClipAttack
from src.attacks.adaptive_cosine_mimic import AdaptiveCosineMimicAttack
from src.attacks.slow_drift import SlowDriftAttack
from src.attacks.collusion import CollusionGroupAttack

__all__ = [
    "BaseAttack",
    "UntargetedLabelFlipAttack",
    "TargetedLabelFlipAttack",
    "ModelPoisoningAttack",
    "OnOffAttackWrapper",
    "AdaptiveNormClipAttack",
    "AdaptiveCosineMimicAttack",
    "SlowDriftAttack",
    "CollusionGroupAttack",
]
