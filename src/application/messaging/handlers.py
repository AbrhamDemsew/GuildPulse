"""Use cases for messaging operations."""

import logging

from src.application.messaging.ports import AIServicePort
from src.config import get_settings
from src.domain.channel.aggregate import Channel
from src.domain.channel.value_objects import Message, MessageContent
from src.domain.repository import MessageRepository
from src.domain.shared.errors import ChannelNotFoundError, DomainError


class ProcessUserTurn:
    """Use case to process a user turn and generate AI reply."""

    def __init__(
        self,
        repo: MessageRepository,
        ai_service: AIServicePort,
    ) -> None:
        self.repo = repo
        self.ai_service = ai_service
        self.settings = get_settings()
        self.logger = logging.getLogger(__name__)

    def execute(
        self,
        channel_id: int,
        user_content: str,
        *,
        channel: Channel | None = None,
        author_name: str = "User",
        bot_name: str = "Bot",
    ) -> str:
        """Process user message and return AI reply."""
        try:
            self.logger.debug(f"Processing user turn for channel_id {channel_id}")

            if channel is None:
                channel = self.repo.get_or_create(channel_id)

            prefixed_user_content = f"{author_name}: {user_content}"
            assert channel is not None
            channel.add_message(
                Message(
                    role="user", content=MessageContent(value=prefixed_user_content)
                )
            )

            reply = self.ai_service.generate_reply(channel)

            prefixed_reply = f"{bot_name}: {reply}"
            channel.add_message(
                Message(role="assistant", content=MessageContent(value=prefixed_reply))
            )

            self.repo.save(channel)

            self.logger.info(f"Generated response for channel_id {channel_id}")
            self.logger.debug(f"Response: {reply[:100]}...")

            return reply

        except ChannelNotFoundError:
            self.logger.error(f"Channel not found for channel_id {channel_id}")
            return "Channel not found. Conversation history could not be retrieved."
        except DomainError:
            self.logger.error(f"Domain error for channel_id {channel_id}")
            return "An error occurred while processing your message."
        except Exception:
            self.logger.exception(f"Unexpected error for channel_id {channel_id}")
            return "An unexpected error occurred. Please try again."


class ClearChannelHistory:
    """Use case to clear a channel's conversation history."""

    def __init__(self, repo: MessageRepository) -> None:
        self.repo = repo
        self.logger = logging.getLogger(__name__)

    def execute(self, channel_id: int) -> bool:
        """Clear the channel's conversation history. Returns True if cleared."""
        try:
            self.logger.debug(f"Clearing history for channel_id {channel_id}")

            channel = self.repo.get(channel_id)
            if channel is None:
                self.logger.warning(f"Channel not found for channel_id {channel_id}")
                return False

            if not channel.messages:
                self.logger.info(f"Channel already empty for channel_id {channel_id}")
                return False

            channel.clear()
            self.repo.save(channel)

            self.logger.info(
                f"Cleared conversation history for channel_id {channel_id}"
            )

            return True

        except Exception:
            self.logger.exception(f"Unexpected error for channel_id {channel_id}")
            return False
