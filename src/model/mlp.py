"""
mlp.py — IDS MLP model with explicit body / head separation.

The body / head split is a first-class design constraint, not an afterthought.
Phase 10 (class-aware aggregation) aggregates body layers by base trust and
head layers per-class by class-specific trust. Building this split now means
zero refactoring later.

Architecture:
    Input (F features)
      ↓
    body: Linear(F→H1) → BN → ReLU → Dropout
          Linear(H1→H2) → BN → ReLU → Dropout
      ↓
    head: Linear(H2→num_classes)

Default: F=32, H1=128, H2=64, num_classes=8, dropout=0.3
"""

from __future__ import annotations

from typing import Iterator

import torch
import torch.nn as nn


class IDS_MLP(nn.Module):
    """
    Intrusion Detection MLP with body/head split.

    Args:
        in_features:   Number of input features (default 32).
        hidden1:       Neurons in first hidden layer (default 128).
        hidden2:       Neurons in second hidden layer (default 64).
        num_classes:   Number of output classes (default 8).
        dropout:       Dropout probability applied after each hidden layer (default 0.3).
    """

    def __init__(
        self,
        in_features: int = 32,
        hidden1: int = 128,
        hidden2: int = 64,
        num_classes: int = 8,
        dropout: float = 0.3,
    ) -> None:
        super().__init__()

        # ── Body (shared representation layers) ───────────────────────────────
        self.body = nn.Sequential(
            nn.Linear(in_features, hidden1),
            nn.BatchNorm1d(hidden1),
            nn.ReLU(inplace=True),
            nn.Dropout(p=dropout),

            nn.Linear(hidden1, hidden2),
            nn.BatchNorm1d(hidden2),
            nn.ReLU(inplace=True),
            nn.Dropout(p=dropout),
        )

        # ── Head (class-specific classifier) ──────────────────────────────────
        self.head = nn.Linear(hidden2, num_classes)

        # Store config for serialisation
        self.config = {
            "in_features": in_features,
            "hidden1": hidden1,
            "hidden2": hidden2,
            "num_classes": num_classes,
            "dropout": dropout,
        }

        self._init_weights()

    # ── Initialisation ────────────────────────────────────────────────────────

    def _init_weights(self) -> None:
        """Kaiming uniform for linear layers, constant for BN."""
        for m in self.modules():
            if isinstance(m, nn.Linear):
                nn.init.kaiming_uniform_(m.weight, nonlinearity="relu")
                if m.bias is not None:
                    nn.init.zeros_(m.bias)
            elif isinstance(m, nn.BatchNorm1d):
                nn.init.ones_(m.weight)
                nn.init.zeros_(m.bias)

    # ── Forward pass ──────────────────────────────────────────────────────────

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Returns raw logits of shape (B, num_classes)."""
        return self.head(self.body(x))

    def encode(self, x: torch.Tensor) -> torch.Tensor:
        """Returns body embeddings of shape (B, hidden2). Used for cosine sim in Phase 6."""
        return self.body(x)

    # ── Parameter access (critical for Phase 10 aggregation) ─────────────────

    def body_parameters(self) -> Iterator[nn.Parameter]:
        """Iterate over body layer parameters only."""
        return self.body.parameters()

    def head_parameters(self) -> Iterator[nn.Parameter]:
        """Iterate over head (classifier) parameters only."""
        return self.head.parameters()

    def body_state_dict(self) -> dict:
        """State dict of body layers only."""
        return {k: v for k, v in self.state_dict().items() if k.startswith("body.")}

    def head_state_dict(self) -> dict:
        """State dict of head layer only."""
        return {k: v for k, v in self.state_dict().items() if k.startswith("head.")}

    def load_body_state_dict(self, state_dict: dict, strict: bool = True) -> None:
        """Load body weights from a body_state_dict."""
        current = self.state_dict()
        current.update(state_dict)
        self.load_state_dict(current, strict=strict)

    def load_head_state_dict(self, state_dict: dict, strict: bool = True) -> None:
        """Load head weights from a head_state_dict."""
        current = self.state_dict()
        current.update(state_dict)
        self.load_state_dict(current, strict=strict)

    # ── Serialisation helpers ─────────────────────────────────────────────────

    def get_flat_params(self) -> torch.Tensor:
        """Flatten all parameters into a 1-D tensor. Used for cosine similarity in Phase 6."""
        return torch.cat([p.data.view(-1) for p in self.parameters()])

    def set_flat_params(self, flat: torch.Tensor) -> None:
        """Restore parameters from a flat tensor produced by get_flat_params()."""
        offset = 0
        for p in self.parameters():
            numel = p.numel()
            p.data.copy_(flat[offset: offset + numel].view(p.shape))
            offset += numel

    # ── Repr ──────────────────────────────────────────────────────────────────

    def __repr__(self) -> str:
        cfg = self.config
        total = sum(p.numel() for p in self.parameters())
        return (
            f"IDS_MLP(in={cfg['in_features']}, H1={cfg['hidden1']}, "
            f"H2={cfg['hidden2']}, classes={cfg['num_classes']}, "
            f"dropout={cfg['dropout']}, params={total:,})"
        )


# ── Convenience factory ───────────────────────────────────────────────────────

def build_model(config: dict, device: torch.device) -> IDS_MLP:
    """
    Build IDS_MLP from a config dict (typically loaded from default.yaml).
    Expected keys under config['model']: in_features, hidden1, hidden2,
    num_classes, dropout.
    """
    m_cfg = config.get("model", {})
    model = IDS_MLP(
        in_features=m_cfg.get("in_features", 32),
        hidden1=m_cfg.get("hidden1", 128),
        hidden2=m_cfg.get("hidden2", 64),
        num_classes=m_cfg.get("num_classes", 8),
        dropout=m_cfg.get("dropout", 0.3),
    )
    return model.to(device)
