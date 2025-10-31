"""Repository port for usage analytics."""

from __future__ import annotations

from datetime import date
from typing import Protocol

from guildpulse.domain.analytics.usage import QuotaStatus, UsageTotals


class IUsageRepository(Protocol):
    def record(
        self,
        guild_id: int,
        user_id: int,
        channel_id: int,
        prompt_tokens: int,
        completion_tokens: int,
    ) -> None: ...

    def totals_for_guild(self, guild_id: int, recorded_on: date) -> UsageTotals: ...

    def totals_for_user(self, guild_id: int, user_id: int, recorded_on: date) -> UsageTotals: ...

    def quota_status(
        self,
        guild_id: int,
        messages_limit: int,
        tokens_limit: int,
        recorded_on: date,
    ) -> QuotaStatus: ...
