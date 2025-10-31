"""Moderation use cases."""

from __future__ import annotations

import logging

from guildpulse.application.ports.content_moderator_port import IContentModerator
from guildpulse.application.ports.moderation_log_repository_port import IModerationLogRepository
from guildpulse.domain.moderation.models import ModerationDecision, ModerationRecord


class EvaluateIncomingMessage:
    """Run moderation checks before AI processing."""

    def __init__(
        self,
        moderator: IContentModerator,
        log_repo: IModerationLogRepository,
    ) -> None:
        self.moderator = moderator
        self.log_repo = log_repo
        self.logger = logging.getLogger(__name__)

    def execute(
        self,
        guild_id: int,
        user_id: int,
        channel_id: int,
        content: str,
        moderation_enabled: bool = True,
    ) -> ModerationDecision:
        if not moderation_enabled:
            return ModerationDecision.allow()

        rate_decision = self.moderator.evaluate_user_rate(guild_id, user_id)
        if rate_decision.blocked:
            self._log(guild_id, user_id, channel_id, rate_decision, content)
            return rate_decision

        content_decision = self.moderator.evaluate(content)
        if content_decision.blocked:
            self._log(guild_id, user_id, channel_id, content_decision, content)
            return content_decision

        self.moderator.register_user_message(guild_id, user_id)
        return ModerationDecision.allow()

    def _log(
        self,
        guild_id: int,
        user_id: int,
        channel_id: int,
        decision: ModerationDecision,
        content: str,
    ) -> None:
        preview = content[:200]
        record = ModerationRecord(
            guild_id=guild_id,
            user_id=user_id,
            channel_id=channel_id,
            action=decision.action,
            reason=decision.reason,
            content_preview=preview,
        )
        self.log_repo.append(record)
        self.logger.warning(
            "Moderation %s for user %s in guild %s: %s",
            decision.action.value,
            user_id,
            guild_id,
            decision.reason,
        )


class ListModerationEvents:
    def __init__(self, log_repo: IModerationLogRepository) -> None:
        self.log_repo = log_repo

    def execute(self, guild_id: int, limit: int = 50) -> list[ModerationRecord]:
        return self.log_repo.list_for_guild(guild_id, limit=limit)
