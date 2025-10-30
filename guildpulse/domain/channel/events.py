"""Domain events for the Channel aggregate."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from guildpulse.domain.shared.domain_event import DomainEvent

if TYPE_CHECKING:
    from guildpulse.domain.channel.aggregate import Channel


@dataclass(frozen=True)
class MessageAdded(DomainEvent):
    """Event fired when a message is added to a channel."""

    message_role: str
    message_content: str

    @staticmethod
    def from_channel(channel: "Channel", role: str, content: str) -> "MessageAdded":
        """Create a MessageAdded event from a channel."""
        return MessageAdded(
            event_id=DomainEvent.generate_event_id(),
            occurred_at=DomainEvent.now(),
            aggregate_id=str(channel.id),
            message_role=role,
            message_content=content,
        )

    @property
    def event_type(self) -> str:
        return "channel.message.added"


@dataclass(frozen=True)
class ConversationCleared(DomainEvent):
    """Event fired when a channel's conversation history is cleared."""

    previous_message_count: int

    @staticmethod
    def from_channel(channel: "Channel", previous_count: int) -> "ConversationCleared":
        """Create a ConversationCleared event from a channel."""
        return ConversationCleared(
            event_id=DomainEvent.generate_event_id(),
            occurred_at=DomainEvent.now(),
            aggregate_id=str(channel.id),
            previous_message_count=previous_count,
        )

    @property
    def event_type(self) -> str:
        return "channel.conversation.cleared"
