"""SQLite guild settings repository."""

from __future__ import annotations

from datetime import datetime

from guildpulse.domain.guild.aggregate import GuildSettings
from guildpulse.infrastructure.persistence.sqlite.database import Database


class SQLiteGuildSettingsRepository:
    def __init__(self, database: Database) -> None:
        self.database = database

    def get(self, guild_id: int) -> GuildSettings | None:
        with self.database.connection() as conn:
            row = conn.execute(
                "SELECT * FROM guild_settings WHERE guild_id = ?",
                (guild_id,),
            ).fetchone()
        if row is None:
            return None
        return GuildSettings.from_row(
            guild_id=row["guild_id"],
            system_prompt=row["system_prompt"],
            model_name=row["model_name"],
            max_history=row["max_history"],
            max_tokens=row["max_tokens"],
            temperature=row["temperature"],
            moderation_enabled=row["moderation_enabled"],
            knowledge_enabled=row["knowledge_enabled"],
            daily_message_quota=row["daily_message_quota"],
            daily_token_quota=row["daily_token_quota"],
            allowed_channel_ids=row["allowed_channel_ids"],
            admin_role_ids=row["admin_role_ids"],
        )

    def save(self, settings: GuildSettings) -> None:
        allowed_json, admin_json = settings.to_json_lists()
        with self.database.connection() as conn:
            conn.execute(
                """
                INSERT INTO guild_settings (
                    guild_id, system_prompt, model_name, max_history, max_tokens,
                    temperature, moderation_enabled, knowledge_enabled,
                    daily_message_quota, daily_token_quota,
                    allowed_channel_ids, admin_role_ids, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(guild_id) DO UPDATE SET
                    system_prompt=excluded.system_prompt,
                    model_name=excluded.model_name,
                    max_history=excluded.max_history,
                    max_tokens=excluded.max_tokens,
                    temperature=excluded.temperature,
                    moderation_enabled=excluded.moderation_enabled,
                    knowledge_enabled=excluded.knowledge_enabled,
                    daily_message_quota=excluded.daily_message_quota,
                    daily_token_quota=excluded.daily_token_quota,
                    allowed_channel_ids=excluded.allowed_channel_ids,
                    admin_role_ids=excluded.admin_role_ids,
                    updated_at=excluded.updated_at
                """,
                (
                    settings.id,
                    settings.system_prompt,
                    settings.model_name,
                    settings.max_history,
                    settings.max_tokens,
                    settings.temperature,
                    int(settings.moderation_enabled),
                    int(settings.knowledge_enabled),
                    settings.daily_message_quota,
                    settings.daily_token_quota,
                    allowed_json,
                    admin_json,
                    datetime.now().isoformat(),
                ),
            )
            conn.commit()

    def get_or_create_default(self, guild_id: int, default_prompt: str) -> GuildSettings:
        existing = self.get(guild_id)
        if existing:
            return existing
        settings = GuildSettings.default_for(guild_id, default_prompt)
        self.save(settings)
        return settings

    def delete(self, guild_id: int) -> bool:
        with self.database.connection() as conn:
            cursor = conn.execute("DELETE FROM guild_settings WHERE guild_id = ?", (guild_id,))
            conn.commit()
            return cursor.rowcount > 0

    def list_guild_ids(self) -> list[int]:
        with self.database.connection() as conn:
            rows = conn.execute("SELECT guild_id FROM guild_settings ORDER BY guild_id").fetchall()
        return [int(row["guild_id"]) for row in rows]
