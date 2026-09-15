"""
repository.py — Audit Database Repository Operations.

Provides CRUD methods for recording rounds, state transitions, and audit records.
"""

from __future__ import annotations

import sqlite3
import json
from pathlib import Path
from src.database.models import init_db


class AuditRepository:
    """Repository for querying and updating audit records in SQLite."""

    def __init__(self, db_path: str | Path = "data/audit.db") -> None:
        self.db_path = Path(db_path)
        self.conn = init_db(self.db_path)

    def save_round_metrics(
        self, round_num: int, val_acc: float, val_f1: float, client_loss: float, method: str = "FedAvg"
    ) -> None:
        with self.conn:
            self.conn.execute(
                """
                INSERT OR REPLACE INTO federation_rounds (round, val_accuracy, val_macro_f1, client_loss, aggregation_method)
                VALUES (?, ?, ?, ?, ?)
                """,
                (round_num, val_acc, val_f1, client_loss, method),
            )

    def save_state_transition(
        self, round_num: int, client_id: str | int, old_state: str, new_state: str, evidence: float, reason: str
    ) -> None:
        with self.conn:
            self.conn.execute(
                """
                INSERT INTO state_transitions (round, client_id, old_state, new_state, evidence_score, reason)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (round_num, str(client_id), old_state, new_state, evidence, reason),
            )

    def save_audit_record(
        self, round_num: int, client_id: str | int, record_dict: dict, record_hash: str, tx_hash: str = "", block_num: int = 0
    ) -> None:
        with self.conn:
            self.conn.execute(
                """
                INSERT OR REPLACE INTO audit_records (round, client_id, record_json, record_hash, tx_hash, block_num)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (round_num, str(client_id), json.dumps(record_dict, sort_keys=True), record_hash, tx_hash, block_num),
            )

    def get_audit_record(self, record_hash: str) -> dict | None:
        cursor = self.conn.cursor()
        cursor.execute("SELECT record_json, tx_hash, block_num FROM audit_records WHERE record_hash = ?", (record_hash,))
        row = cursor.fetchone()
        if row:
            return {"record": json.loads(row[0]), "tx_hash": row[1], "block_num": row[2]}
        return None
