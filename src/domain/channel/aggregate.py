"""Channel aggregate for managing conversation history."""

from __future__ import annotations

import threading
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from src.domain.channel.events import ConversationCleared, MessageAdded
from src.domain.shared.domain_event import DomainEvent

if TYPE_CHECKING:
    from src.domain.channel.value_objects import Message


@dataclass
class Channel:
    """Aggregate root for channel conversations."""

    channel_id: int
    messages: list[Message] = field(default_factory=list)
    max_messages: int = 100
    _domain_events: list[DomainEvent] = field(default_factory=list, init=False, repr=False)
    _lock: threading.Lock = field(default_factory=lambda: threading.Lock(), init=False, repr=False)

    def add_message(self, message: Message) -> None:
        """Add a message to the channel and record domain events."""
        with self._lock:
            if self.max_messages <= 0:
                return
            self.messages.append(message)
            if len(self.messages) > self.max_messages:
                self.messages = self.messages[-self.max_messages :]

            # Record domain event
            self._domain_events.append(
                MessageAdded.from_channel(self, message.role, message.content.value or "")
            )

    def get_messages(self) -> list[Message]:
        """Get all messages in the channel."""
        return self.messages.copy()

    def get_messages_for_api(self) -> list[dict[str, Any]]:
        """Get messages as dictionaries for API consumption."""
        return [msg.to_dict() for msg in self.messages]

    def clear(self) -> None:
        """Clear all messages in the channel and record domain event."""
        previous_count = len(self.messages)
        self.messages.clear()
        self._domain_events.append(ConversationCleared.from_channel(self, previous_count))

    def count_messages(self) -> int:
        """Count the number of messages."""
        return len(self.messages)

    @property
    def domain_events(self) -> list[DomainEvent]:
        """Get accumulated domain events."""
        return self._domain_events

    def clear_events(self) -> None:
        """Clear accumulated domain events after publishing."""
        self._domain_events.clear()
