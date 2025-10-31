"""SQLite moderation audit log repository."""

from __future__ import annotations

from guildpulse.domain.moderation.models import ModerationAction, ModerationRecord
from guildpulse.infrastructure.persistence.sqlite.database import Database


class SQLiteModerationLogRepository:
    def __init__(self, database: Database) -> None:
        self.database = database

    def append(self, record: ModerationRecord) -> ModerationRecord:
        with self.database.connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO moderation_log
                (guild_id, user_id, channel_id, action, reason, content_preview)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    record.guild_id,
                    record.user_id,
                    record.channel_id,
                    record.action.value,
                    record.reason,
                    record.content_preview,
                ),
            )
            conn.commit()
            record_id = int(cursor.lastrowid)
        return ModerationRecord(
            guild_id=record.guild_id,
            user_id=record.user_id,
            channel_id=record.channel_id,
            action=record.action,
            reason=record.reason,
            content_preview=record.content_preview,
            record_id=record_id,
        )

    def list_for_guild(self, guild_id: int, limit: int = 50) -> list[ModerationRecord]:
        with self.database.connection() as conn:
            rows = conn.execute(
                """
                SELECT id, guild_id, user_id, channel_id, action, reason, content_preview
                FROM moderation_log
                WHERE guild_id = ?
                ORDER BY id DESC
                LIMIT ?
                """,
                (guild_id, limit),
            ).fetchall()
        return [
            ModerationRecord(
                record_id=row["id"],
                guild_id=row["guild_id"],
                user_id=row["user_id"],
                channel_id=row["channel_id"],
                action=ModerationAction(row["action"]),
                reason=row["reason"],
                content_preview=row["content_preview"],
            )
            for row in rows
        ]

    def count_blocks_for_user(self, guild_id: int, user_id: int) -> int:
        with self.database.connection() as conn:
            row = conn.execute(
                """
                SELECT COUNT(*) AS total FROM moderation_log
                WHERE guild_id = ? AND user_id = ? AND action = ?
                """,
                (guild_id, user_id, ModerationAction.BLOCK.value),
            ).fetchone()
        return int(row["total"]) if row else 0
