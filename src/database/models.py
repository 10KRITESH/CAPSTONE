"""
models.py — SQLite Audit Database Schemas.

Database models for storing client metadata, round metrics, reputation vectors,
state transitions, audit records, and blockchain transaction receipts.
"""

from __future__ import annotations

import sqlite3
import json
from pathlib import Path


def init_db(db_path: str | Path = "data/audit.db") -> sqlite3.Connection:
    """Initialize SQLite audit database tables."""
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))

    with conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS federation_rounds (
                round INTEGER PRIMARY KEY,
                val_accuracy REAL,
                val_macro_f1 REAL,
                client_loss REAL,
                aggregation_method TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS state_transitions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                round INTEGER,
                client_id TEXT,
                old_state TEXT,
                new_state TEXT,
                evidence_score REAL,
                reason TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS audit_records (
                round INTEGER,
                client_id TEXT,
                record_json TEXT,
                record_hash TEXT PRIMARY KEY,
                tx_hash TEXT,
                block_num INTEGER,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            );
        """)
    return conn
