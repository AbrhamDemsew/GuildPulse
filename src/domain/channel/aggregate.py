"""Channel aggregate for managing conversation history."""

from __future__ import annotations

import threading
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from src.domain.channel.events import ConversationCleared, MessageAdded
from src.domain.shared.aggregate_root import AggregateRoot

if TYPE_CHECKING:
    from src.domain.channel.value_objects import Message


@dataclass
class Channel(AggregateRoot[int]):
    """Aggregate root for channel conversations."""

    max_messages: int = 100
    _messages: list[Message] = field(default_factory=list, init=False, repr=False)
    _lock: threading.Lock = field(default_factory=threading.Lock, init=False)

    def add_message(self, message: Message) -> None:
        """Add a message to the channel and record domain events."""
        with self._lock:
            if self.max_messages <= 0:
                return
            self._messages.append(message)
            if len(self._messages) > self.max_messages:
                self._messages = self._messages[-self.max_messages :]

            self.add_domain_event(
                MessageAdded.from_channel(self, message.role, message.content.value or "")
            )

    def get_messages(self) -> list[Message]:
        """Get all messages in the channel."""
        return self._messages.copy()

    def get_messages_for_api(self) -> list[dict[str, Any]]:
        """Get messages as dictionaries for API consumption."""
        return [msg.to_dict() for msg in self._messages]

    def clear(self) -> None:
        """Clear all messages in the channel and record domain event."""
        previous_count = len(self._messages)
        self._messages.clear()
        self.add_domain_event(ConversationCleared.from_channel(self, previous_count))

    def count_messages(self) -> int:
        """Count the number of messages."""
        return len(self._messages)
