"""SQLite-backed optimization attempt memory."""

from __future__ import annotations

import json
import sqlite3
import time
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class OptimizationAttempt:
    attempt_id: str
    timestamp: float
    change_description: str
    config_diff: str
    status: str  # "accepted", "rejected_invalid", "rejected_safety", "rejected_no_improvement", "rejected_regression"
    score_before: float = 0.0
    score_after: float = 0.0
    health_context: str = ""  # JSON string of health metrics that triggered this


class OptimizationMemory:
    """Persistent store for optimization attempts using SQLite."""

    def __init__(self, db_path: str = "optimizer_memory.db") -> None:
        self.db_path = db_path
        self._init_db()

    def _init_db(self) -> None:
        """Create the attempts table if it doesn't exist."""
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS attempts (
                    attempt_id TEXT PRIMARY KEY,
                    timestamp REAL NOT NULL,
                    change_description TEXT NOT NULL,
                    config_diff TEXT NOT NULL,
                    status TEXT NOT NULL,
                    score_before REAL DEFAULT 0.0,
                    score_after REAL DEFAULT 0.0,
                    health_context TEXT DEFAULT ''
                )
                """
            )
            conn.commit()
        finally:
            conn.close()

    def log(self, attempt: OptimizationAttempt) -> None:
        """Insert an optimization attempt into the database."""
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute(
                """
                INSERT OR REPLACE INTO attempts
                    (attempt_id, timestamp, change_description, config_diff, status,
                     score_before, score_after, health_context)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    attempt.attempt_id,
                    attempt.timestamp,
                    attempt.change_description,
                    attempt.config_diff,
                    attempt.status,
                    attempt.score_before,
                    attempt.score_after,
                    attempt.health_context,
                ),
            )
            conn.commit()
        finally:
            conn.close()

    def recent(self, limit: int = 20) -> list[OptimizationAttempt]:
        """Get the most recent attempts ordered by timestamp descending."""
        conn = sqlite3.connect(self.db_path)
        try:
            rows = conn.execute(
                "SELECT * FROM attempts ORDER BY timestamp DESC LIMIT ?", (limit,)
            ).fetchall()
            return [self._row_to_attempt(row) for row in rows]
        finally:
            conn.close()

    def accepted(self, limit: int = 10) -> list[OptimizationAttempt]:
        """Get recently accepted attempts."""
        conn = sqlite3.connect(self.db_path)
        try:
            rows = conn.execute(
                "SELECT * FROM attempts WHERE status = 'accepted' ORDER BY timestamp DESC LIMIT ?",
                (limit,),
            ).fetchall()
            return [self._row_to_attempt(row) for row in rows]
        finally:
            conn.close()

    def get_all(self) -> list[OptimizationAttempt]:
        """Get all attempts ordered by timestamp descending."""
        conn = sqlite3.connect(self.db_path)
        try:
            rows = conn.execute(
                "SELECT * FROM attempts ORDER BY timestamp DESC"
            ).fetchall()
            return [self._row_to_attempt(row) for row in rows]
        finally:
            conn.close()

    def clear(self) -> None:
        """Delete all attempts (for testing)."""
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute("DELETE FROM attempts")
            conn.commit()
        finally:
            conn.close()

    @staticmethod
    def _row_to_attempt(row: tuple) -> OptimizationAttempt:
        """Convert a database row tuple to an OptimizationAttempt."""
        return OptimizationAttempt(
            attempt_id=row[0],
            timestamp=row[1],
            change_description=row[2],
            config_diff=row[3],
            status=row[4],
            score_before=row[5],
            score_after=row[6],
            health_context=row[7],
        )
