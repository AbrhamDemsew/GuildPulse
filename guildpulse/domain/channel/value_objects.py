"""Value objects for the domain model."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional

from guildpulse.domain.shared.errors import MessageValidationError

__all__ = ["MessageContent", "Message", "MessageRole"]


class MessageRole(Enum):
    """Enum for message roles."""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


@dataclass(frozen=True)
class MessageContent:
    """Value object representing the content of a message."""

    value: Optional[str] = None

    def __post_init__(self) -> None:
        """Validate message content."""
        if self.value is None:
            raise MessageValidationError("Message content cannot be None")
        if self.value == "":
            raise MessageValidationError("Message content cannot be empty")
        if len(self.value) > 10000:
            raise MessageValidationError("Message content too long (max 10000 characters)")

    def __str__(self) -> str:
        if self.value is None:
            return ""
        return self.value


def _generate_message_id() -> str:
    """Generate a unique message ID."""
    return str(id(object()))


@dataclass(frozen=True)
class Message:
    """Value object representing a message in a conversation."""

    role: str
    content: MessageContent
    timestamp: datetime = field(default_factory=datetime.now)
    id: str = field(default_factory=_generate_message_id)

    def __post_init__(self) -> None:
        """Validate message."""
        valid_roles = {"system", "user", "assistant"}
        if self.role not in valid_roles:
            raise MessageValidationError(f"Invalid role: {self.role}")

    def to_dict(self) -> dict[str, str]:
        """Convert message to dictionary."""
        content = self.content.value or ""
        return {"role": self.role, "content": content}

    def __eq__(self, other: object) -> bool:
        """Compare messages by value (not identity)."""
        if not isinstance(other, Message):
            return False
        return (self.role, self.content.value) == (
            other.role,
            other.content.value,
        )

    def __hash__(self) -> int:
        return hash((self.id, self.role, self.content.value))
