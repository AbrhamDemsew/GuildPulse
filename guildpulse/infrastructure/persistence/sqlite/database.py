"""Shared SQLite database access for GuildPulse persistence."""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from guildpulse.infrastructure.persistence.sqlite.schema import MIGRATIONS


class Database:
    """SQLite database with schema migrations."""

    def __init__(self, db_path: str = "data/channels.db") -> None:
        self.db_path = db_path
        self._ensure_database_exists()

    def _ensure_database_exists(self) -> None:
        db_dir = Path(self.db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)

        with self.connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "CREATE TABLE IF NOT EXISTS schema_migrations (version INTEGER PRIMARY KEY)"
            )
            cursor.execute("SELECT MAX(version) FROM schema_migrations")
            row = cursor.fetchone()
            current_version = row[0] if row and row[0] is not None else 0

            for version, sql in MIGRATIONS:
                if version > current_version:
                    cursor.executescript(sql)
                    cursor.execute(
                        "INSERT INTO schema_migrations (version) VALUES (?)",
                        (version,),
                    )
            conn.commit()

    @contextmanager
    def connection(self) -> Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
