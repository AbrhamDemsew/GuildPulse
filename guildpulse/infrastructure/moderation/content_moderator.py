"""Rule-based content moderation."""

from __future__ import annotations

import re

from guildpulse.domain.moderation.models import ModerationDecision
from guildpulse.infrastructure.persistence.sqlite.usage_repository import SQLiteUsageRepository


class ContentModerator:
    """Lightweight moderation pipeline for guild messages."""

    BLOCKED_PATTERNS = (
        r"\b(kill yourself|kys)\b",
        r"\b(nazi|hitler)\b",
        r"\b(racial slur)\b",
        r"(https?://\S*(?:grabify|iplogger)\S*)",
    )

    def __init__(
        self,
        usage_repo: SQLiteUsageRepository,
        per_minute_limit: int = 12,
    ) -> None:
        self.usage_repo = usage_repo
        self.per_minute_limit = per_minute_limit
        self._compiled = [re.compile(pattern, re.IGNORECASE) for pattern in self.BLOCKED_PATTERNS]

    def evaluate(self, content: str) -> ModerationDecision:
        normalized = content.strip()
        if not normalized:
            return ModerationDecision.block("Empty messages are not processed")
        if len(normalized) > 4000:
            return ModerationDecision.block("Message exceeds maximum length")
        for pattern in self._compiled:
            if pattern.search(normalized):
                return ModerationDecision.block("Message matched moderation policy")
        return ModerationDecision.allow()

    def evaluate_user_rate(self, guild_id: int, user_id: int) -> ModerationDecision:
        count = self.usage_repo.increment_user_rate(guild_id, user_id)
        if count > self.per_minute_limit:
            return ModerationDecision.rate_limited()
        return ModerationDecision.allow()

    def register_user_message(self, guild_id: int, user_id: int) -> None:
        _ = guild_id
        _ = user_id
