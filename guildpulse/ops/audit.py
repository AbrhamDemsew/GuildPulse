"""Operational audit trail for GuildPulse admin actions."""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Iterator

from guildpulse.infrastructure.persistence.sqlite.database import Database


class AuditAction(str, Enum):
    GUILD_SETTINGS_UPDATED = "guild_settings_updated"
    KNOWLEDGE_DOCUMENT_ADDED = "knowledge_document_added"
    KNOWLEDGE_DOCUMENT_REMOVED = "knowledge_document_removed"
    MODERATION_BLOCK = "moderation_block"
    QUOTA_EXCEEDED = "quota_exceeded"
    PLUGIN_ENABLED = "plugin_enabled"
    PLUGIN_DISABLED = "plugin_disabled"


@dataclass(frozen=True)
class AuditEntry:
    action: AuditAction
    guild_id: int
    actor_id: int
    details: dict[str, str | int | bool]
    entry_id: int | None = None
    created_at: datetime | None = None


class AuditLogStore:
    """SQLite-backed audit log for operational events."""

    def __init__(self, database: Database) -> None:
        self.database = database
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        with self.database.connection() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS audit_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    action TEXT NOT NULL,
                    guild_id INTEGER NOT NULL,
                    actor_id INTEGER NOT NULL,
                    details TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_audit_guild ON audit_log(guild_id, created_at DESC)"
            )
            conn.commit()

    def record(self, entry: AuditEntry) -> AuditEntry:
        payload = json.dumps(entry.details)
        with self.database.connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO audit_log (action, guild_id, actor_id, details)
                VALUES (?, ?, ?, ?)
                """,
                (entry.action.value, entry.guild_id, entry.actor_id, payload),
            )
            conn.commit()
            entry_id = int(cursor.lastrowid)
        return AuditEntry(
            action=entry.action,
            guild_id=entry.guild_id,
            actor_id=entry.actor_id,
            details=entry.details,
            entry_id=entry_id,
            created_at=datetime.utcnow(),
        )

    def list_for_guild(self, guild_id: int, limit: int = 100) -> list[AuditEntry]:
        with self.database.connection() as conn:
            rows = conn.execute(
                """
                SELECT id, action, guild_id, actor_id, details, created_at
                FROM audit_log WHERE guild_id = ?
                ORDER BY id DESC LIMIT ?
                """,
                (guild_id, limit),
            ).fetchall()
        entries: list[AuditEntry] = []
        for row in rows:
            entries.append(
                AuditEntry(
                    entry_id=row["id"],
                    action=AuditAction(row["action"]),
                    guild_id=row["guild_id"],
                    actor_id=row["actor_id"],
                    details=json.loads(row["details"]),
                    created_at=datetime.fromisoformat(row["created_at"])
                    if row["created_at"]
                    else None,
                )
            )
        return entries

    def export_guild_csv(self, guild_id: int, output_path: str) -> Path:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        lines = ["id,action,guild_id,actor_id,details,created_at"]
        for entry in self.list_for_guild(guild_id, limit=1000):
            details = json.dumps(entry.details).replace('"', '""')
            created = entry.created_at.isoformat() if entry.created_at else ""
            lines.append(
                f'{entry.entry_id},{entry.action.value},{entry.guild_id},'
                f'{entry.actor_id},"{details}",{created}'
            )
        path.write_text("\n".join(lines), encoding="utf-8")
        return path
