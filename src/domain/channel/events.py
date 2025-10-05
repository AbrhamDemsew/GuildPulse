"""Domain events for the Channel aggregate."""

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.domain.channel.aggregate import Channel


@dataclass(frozen=True)
class MessageAdded:
    """Event fired when a message is added to a channel."""

    channel_id: int
    message_role: str
    message_content: str
    timestamp: datetime

    @staticmethod
    def from_channel(channel: "Channel", role: str, content: str) -> "MessageAdded":
        """Create a MessageAdded event from a channel."""
        return MessageAdded(
            channel_id=channel.channel_id,
            message_role=role,
            message_content=content,
            timestamp=datetime.now(),
        )


@dataclass(frozen=True)
class ConversationCleared:
    """Event fired when a channel's conversation history is cleared."""

    channel_id: int
    previous_message_count: int
    timestamp: datetime

    @staticmethod
    def from_channel(channel: "Channel", previous_count: int) -> "ConversationCleared":
        """Create a ConversationCleared event from a channel."""
        return ConversationCleared(
            channel_id=channel.channel_id,
            previous_message_count=previous_count,
            timestamp=datetime.now(),
        )
