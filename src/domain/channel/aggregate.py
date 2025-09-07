"""Channel aggregate for managing conversation history."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.domain.channel.value_objects import Message


@dataclass
class Channel:
    """Aggregate root for channel conversations."""

    channel_id: int
    messages: list[Message] = field(default_factory=list)
    max_messages: int = 100

    def add_message(self, message: Message) -> None:
        """Add a message to the channel."""
        self.messages.append(message)
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages :]

    def get_messages(self) -> list[Message]:
        """Get all messages in the channel."""
        return self.messages.copy()

    def get_messages_for_api(self) -> list[dict[str, str]]:
        """Get messages as dictionaries for API consumption."""
        return [msg.to_dict() for msg in self.messages]

    def clear(self) -> None:
        """Clear all messages in the channel."""
        self.messages.clear()

    def count_messages(self) -> int:
        """Count the number of messages."""
        return len(self.messages)
