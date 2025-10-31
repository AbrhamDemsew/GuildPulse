"""Repository port for guild settings."""

from __future__ import annotations

from typing import Protocol

from guildpulse.domain.guild.aggregate import GuildSettings


class IGuildSettingsRepository(Protocol):
    def get(self, guild_id: int) -> GuildSettings | None: ...

    def save(self, settings: GuildSettings) -> None: ...

    def get_or_create_default(self, guild_id: int, default_prompt: str) -> GuildSettings: ...

    def delete(self, guild_id: int) -> bool: ...

    def list_guild_ids(self) -> list[int]: ...
