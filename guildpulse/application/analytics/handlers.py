"""Usage analytics use cases."""

from __future__ import annotations

import logging
from datetime import date

from guildpulse.application.ports.usage_repository_port import IUsageRepository
from guildpulse.domain.analytics.usage import QuotaStatus, UsageTotals


class RecordTokenUsage:
    def __init__(self, repo: IUsageRepository) -> None:
        self.repo = repo
        self.logger = logging.getLogger(__name__)

    def execute(
        self,
        guild_id: int,
        user_id: int,
        channel_id: int,
        prompt_tokens: int,
        completion_tokens: int,
    ) -> None:
        self.repo.record(guild_id, user_id, channel_id, prompt_tokens, completion_tokens)
        self.logger.debug(
            "Recorded usage guild=%s user=%s tokens=%s",
            guild_id,
            user_id,
            prompt_tokens + completion_tokens,
        )


class GetGuildUsageReport:
    def __init__(self, repo: IUsageRepository) -> None:
        self.repo = repo

    def execute(self, guild_id: int, recorded_on: date | None = None) -> UsageTotals:
        day = recorded_on or date.today()
        return self.repo.totals_for_guild(guild_id, day)

    def for_user(
        self,
        guild_id: int,
        user_id: int,
        recorded_on: date | None = None,
    ) -> UsageTotals:
        day = recorded_on or date.today()
        return self.repo.totals_for_user(guild_id, user_id, day)


class CheckGuildQuota:
    def __init__(self, repo: IUsageRepository) -> None:
        self.repo = repo

    def execute(
        self,
        guild_id: int,
        messages_limit: int,
        tokens_limit: int,
        recorded_on: date | None = None,
    ) -> QuotaStatus:
        day = recorded_on or date.today()
        return self.repo.quota_status(guild_id, messages_limit, tokens_limit, day)

    def can_process_message(self, guild_id: int, messages_limit: int, tokens_limit: int) -> bool:
        status = self.execute(guild_id, messages_limit, tokens_limit)
        return not status.is_exhausted
