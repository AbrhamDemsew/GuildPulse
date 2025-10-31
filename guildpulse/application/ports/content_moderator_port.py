"""Content moderation service port."""

from __future__ import annotations

from typing import Protocol

from guildpulse.domain.moderation.models import ModerationDecision


class IContentModerator(Protocol):
    def evaluate(self, content: str) -> ModerationDecision: ...

    def evaluate_user_rate(self, guild_id: int, user_id: int) -> ModerationDecision: ...

    def register_user_message(self, guild_id: int, user_id: int) -> None: ...
