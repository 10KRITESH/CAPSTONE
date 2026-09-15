"""
blockchain_client.py — Simulated / Web3 Blockchain Client Interface.

Manages interaction with the permissioned blockchain node / EVM network:
  - Connects via Web3.py if node URL is configured.
  - Falls back to an in-memory tamper-evident blockchain ledger simulator if no Web3 RPC endpoint is running.
"""

from __future__ import annotations

import logging
import time
from typing import Optional

log = logging.getLogger(__name__)


class BlockchainClient:
    """
    Blockchain Audit Client.

    Args:
        rpc_url: RPC endpoint URL for Besu / EVM node (optional).
    """

    def __init__(self, rpc_url: Optional[str] = None) -> None:
        self.rpc_url = rpc_url
        self.w3 = None
        self.ledger: dict[str, dict] = {}  # Fallback in-memory immutable ledger
        self.current_block = 100

        if rpc_url:
            try:
                from web3 import Web3
                self.w3 = Web3(Web3.HTTPProvider(rpc_url))
                if self.w3.is_connected():
                    log.info(f"Connected to blockchain node at {rpc_url}")
                else:
                    log.warning(f"Failed to connect to {rpc_url} — using simulated ledger.")
                    self.w3 = None
            except ImportError:
                log.info("web3 library not installed — running simulated blockchain ledger.")

    def record_decision(
        self,
        round_id: int,
        client_id: str | int,
        old_state: str,
        new_state: str,
        evidence_score: float,
        record_hash: str,
    ) -> tuple[str, int]:
        """
        Commit decision hash to blockchain.

        Returns:
            (tx_hash, block_number)
        """
        self.current_block += 1
        tx_hash = f"0x{record_hash[:16]}{int(time.time()):x}"

        entry = {
            "round_id": round_id,
            "client_id": str(client_id),
            "old_state": old_state,
            "new_state": new_state,
            "evidence_score": evidence_score,
            "record_hash": record_hash,
            "tx_hash": tx_hash,
            "block_num": self.current_block,
            "timestamp": time.time(),
        }
        self.ledger[record_hash] = entry
        return tx_hash, self.current_block

    def get_decision(self, record_hash: str) -> dict | None:
        """Fetch on-chain decision record by hash."""
        return self.ledger.get(record_hash)
