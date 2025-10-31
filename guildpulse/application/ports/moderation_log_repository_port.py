"""Repository port for moderation audit log."""

from __future__ import annotations

from typing import Protocol

from guildpulse.domain.moderation.models import ModerationRecord


class IModerationLogRepository(Protocol):
    def append(self, record: ModerationRecord) -> ModerationRecord: ...

    def list_for_guild(self, guild_id: int, limit: int = 50) -> list[ModerationRecord]: ...

    def count_blocks_for_user(self, guild_id: int, user_id: int) -> int: ...
