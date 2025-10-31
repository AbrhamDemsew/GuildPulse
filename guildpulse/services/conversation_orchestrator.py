"""High-level conversation orchestration service."""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass

from guildpulse.application.analytics.handlers import CheckGuildQuota, RecordTokenUsage
from guildpulse.application.guild.handlers import GetGuildSettings
from guildpulse.application.knowledge.handlers import SearchGuildKnowledge
from guildpulse.application.messaging.handlers import MessageProcessingResult, ProcessUserTurn
from guildpulse.application.moderation.handlers import EvaluateIncomingMessage
from guildpulse.ops.metrics_collector import GLOBAL_METRICS


@dataclass(frozen=True)
class ConversationRequest:
    guild_id: int | None
    channel_id: int
    user_id: int
    content: str
    author_name: str = "User"
    bot_name: str = "GuildPulse"
    image_urls: tuple[str, ...] = ()


class ConversationOrchestrator:
    """Coordinates moderation, quotas, knowledge retrieval, and AI replies."""

    def __init__(
        self,
        processor: ProcessUserTurn,
        get_settings: GetGuildSettings,
        quota_checker: CheckGuildQuota,
        usage_recorder: RecordTokenUsage,
        knowledge_search: SearchGuildKnowledge,
        moderation: EvaluateIncomingMessage,
    ) -> None:
        self.processor = processor
        self.get_settings = get_settings
        self.quota_checker = quota_checker
        self.usage_recorder = usage_recorder
        self.knowledge_search = knowledge_search
        self.moderation = moderation
        self.logger = logging.getLogger(__name__)

    def handle(self, request: ConversationRequest) -> MessageProcessingResult:
        started = time.perf_counter()
        settings = None
        if request.guild_id is not None:
            settings = self.get_settings.execute(request.guild_id)

        if settings and not settings.is_channel_allowed(request.channel_id):
            result = MessageProcessingResult(
                reply="This channel is not enabled for GuildPulse.",
                blocked=True,
                block_reason="channel_not_allowed",
            )
            GLOBAL_METRICS.record_message(request.guild_id, blocked=True)
            return result

        if settings and not self.quota_checker.can_process_message(
            settings.id,
            settings.daily_message_quota,
            settings.daily_token_quota,
        ):
            result = MessageProcessingResult(
                reply="Daily usage quota reached for this guild.",
                blocked=True,
                block_reason="quota_exhausted",
            )
            GLOBAL_METRICS.record_message(request.guild_id, blocked=True)
            return result

        if request.guild_id is not None:
            moderation = self.moderation.execute(
                guild_id=request.guild_id,
                user_id=request.user_id,
                channel_id=request.channel_id,
                content=request.content,
                moderation_enabled=settings.moderation_enabled if settings else True,
            )
            if moderation.blocked:
                GLOBAL_METRICS.record_message(request.guild_id, blocked=True)
                return MessageProcessingResult(
                    reply=moderation.reason,
                    blocked=True,
                    block_reason=moderation.action.value,
                )

        if settings and settings.knowledge_enabled and request.guild_id is not None:
            hits = self.knowledge_search.execute(request.guild_id, request.content, limit=1)
            if hits:
                GLOBAL_METRICS.record_knowledge_hit()

        result = self.processor.execute_detailed(
            request.channel_id,
            request.content,
            author_name=request.author_name,
            bot_name=request.bot_name,
            image_urls=request.image_urls,
            guild_id=request.guild_id,
            user_id=request.user_id,
        )
        elapsed_ms = (time.perf_counter() - started) * 1000
        GLOBAL_METRICS.record_latency(elapsed_ms)
        GLOBAL_METRICS.record_message(request.guild_id, blocked=result.blocked)
        self.logger.info(
            "Conversation handled channel=%s guild=%s blocked=%s latency_ms=%.1f",
            request.channel_id,
            request.guild_id,
            result.blocked,
            elapsed_ms,
        )
        return result
