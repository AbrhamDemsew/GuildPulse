"""Use cases for messaging operations."""

from __future__ import annotations

import logging
from dataclasses import dataclass

from guildpulse.application.analytics.handlers import CheckGuildQuota, RecordTokenUsage
from guildpulse.application.knowledge.handlers import SearchGuildKnowledge
from guildpulse.application.moderation.handlers import EvaluateIncomingMessage
from guildpulse.application.ports.ai_service_port import IAIServicePort
from guildpulse.application.ports.channel_repository_port import IChannelRepositoryPort
from guildpulse.application.ports.guild_settings_repository_port import IGuildSettingsRepository
from guildpulse.domain.channel.aggregate import Channel
from guildpulse.domain.channel.value_objects import Message, MessageContent
from guildpulse.domain.guild.aggregate import GuildSettings
from guildpulse.domain.shared.errors import ChannelNotFoundError, DomainError


@dataclass(frozen=True)
class MessageProcessingResult:
    reply: str
    blocked: bool = False
    block_reason: str = ""


class ProcessUserTurn:
    """Use case to process a user turn and generate AI reply."""

    def __init__(
        self,
        repo: IChannelRepositoryPort,
        ai_service: IAIServicePort,
        guild_repo: IGuildSettingsRepository | None = None,
        default_prompt: str = "",
        moderation: EvaluateIncomingMessage | None = None,
        knowledge_search: SearchGuildKnowledge | None = None,
        usage_recorder: RecordTokenUsage | None = None,
        quota_checker: CheckGuildQuota | None = None,
    ) -> None:
        self.repo = repo
        self.ai_service = ai_service
        self.guild_repo = guild_repo
        self.default_prompt = default_prompt
        self.moderation = moderation
        self.knowledge_search = knowledge_search
        self.usage_recorder = usage_recorder
        self.quota_checker = quota_checker
        self.logger = logging.getLogger(__name__)

    def _load_guild_settings(self, guild_id: int | None) -> GuildSettings | None:
        if guild_id is None or self.guild_repo is None:
            return None
        return self.guild_repo.get_or_create_default(guild_id, self.default_prompt)

    def execute(
        self,
        channel_id: int,
        user_content: str,
        *,
        channel: Channel | None = None,
        author_name: str = "User",
        bot_name: str = "Bot",
        image_urls: tuple[str, ...] = (),
        guild_id: int | None = None,
        user_id: int | None = None,
    ) -> str:
        result = self.execute_detailed(
            channel_id,
            user_content,
            channel=channel,
            author_name=author_name,
            bot_name=bot_name,
            image_urls=image_urls,
            guild_id=guild_id,
            user_id=user_id,
        )
        return result.reply

    def execute_detailed(
        self,
        channel_id: int,
        user_content: str,
        *,
        channel: Channel | None = None,
        author_name: str = "User",
        bot_name: str = "Bot",
        image_urls: tuple[str, ...] = (),
        guild_id: int | None = None,
        user_id: int | None = None,
    ) -> MessageProcessingResult:
        try:
            settings = self._load_guild_settings(guild_id)
            if settings and not settings.is_channel_allowed(channel_id):
                return MessageProcessingResult(
                    reply="This channel is not enabled for GuildPulse.",
                    blocked=True,
                    block_reason="channel_not_allowed",
                )

            if settings and self.quota_checker:
                allowed = self.quota_checker.can_process_message(
                    guild_id=settings.id,
                    messages_limit=settings.daily_message_quota,
                    tokens_limit=settings.daily_token_quota,
                )
                if not allowed:
                    return MessageProcessingResult(
                        reply="Daily usage quota reached for this guild. Try again tomorrow.",
                        blocked=True,
                        block_reason="quota_exhausted",
                    )

            if guild_id is not None and user_id is not None and self.moderation:
                decision = self.moderation.execute(
                    guild_id=guild_id,
                    user_id=user_id,
                    channel_id=channel_id,
                    content=user_content,
                    moderation_enabled=settings.moderation_enabled if settings else True,
                )
                if decision.blocked:
                    return MessageProcessingResult(
                        reply=decision.reason,
                        blocked=True,
                        block_reason=decision.action.value,
                    )

            if channel is None:
                channel = self.repo.get_or_create(channel_id)

            if settings:
                channel.max_messages = settings.max_history

            prefixed_user_content = f"{author_name}: {user_content}"
            assert channel is not None
            channel.add_message(
                Message(role="user", content=MessageContent(value=prefixed_user_content))
            )

            knowledge_context = None
            if settings and settings.knowledge_enabled and self.knowledge_search and guild_id is not None:
                knowledge_context = self.knowledge_search.build_context(guild_id, user_content)

            completion = self.ai_service.generate_reply(
                channel,
                image_urls,
                system_prompt=settings.system_prompt if settings else self.default_prompt,
                knowledge_context=knowledge_context,
                model_name=settings.model_name if settings else None,
                max_tokens=settings.max_tokens if settings else None,
                temperature=settings.temperature if settings else None,
            )

            prefixed_reply = f"{bot_name}: {completion.content}"
            channel.add_message(
                Message(role="assistant", content=MessageContent(value=prefixed_reply))
            )
            self.repo.save(channel)

            if guild_id is not None and user_id is not None and self.usage_recorder:
                self.usage_recorder.execute(
                    guild_id=guild_id,
                    user_id=user_id,
                    channel_id=channel_id,
                    prompt_tokens=completion.prompt_tokens,
                    completion_tokens=completion.completion_tokens,
                )

            self.logger.info("Generated response for channel_id %s", channel_id)
            return MessageProcessingResult(reply=completion.content)

        except ChannelNotFoundError:
            self.logger.error("Channel not found for channel_id %s", channel_id)
            return MessageProcessingResult(
                reply="Channel not found. Conversation history could not be retrieved."
            )
        except DomainError:
            self.logger.error("Domain error for channel_id %s", channel_id)
            return MessageProcessingResult(
                reply="An error occurred while processing your message."
            )
        except Exception:
            self.logger.exception("Unexpected error for channel_id %s", channel_id)
            return MessageProcessingResult(
                reply="An unexpected error occurred. Please try again."
            )


class ClearChannelHistory:
    """Use case to clear a channel's conversation history."""

    def __init__(self, repo: IChannelRepositoryPort) -> None:
        self.repo = repo
        self.logger = logging.getLogger(__name__)

    def execute(self, channel_id: int) -> bool:
        """Clear the channel's conversation history. Returns True if cleared."""
        try:
            self.logger.debug("Clearing history for channel_id %s", channel_id)

            channel = self.repo.get(channel_id)
            if not channel:
                self.logger.warning("Channel not found for channel_id %s", channel_id)
                return False

            if not channel.get_messages():
                self.logger.info("Channel already empty for channel_id %s", channel_id)
                return False

            channel.clear()
            self.repo.save(channel)

            self.logger.info("Cleared conversation history for channel_id %s", channel_id)

            return True

        except Exception:
            self.logger.exception("Unexpected error for channel_id %s", channel_id)
            return False
