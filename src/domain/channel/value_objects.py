"""Value objects for the domain model."""

from dataclasses import dataclass, field
from datetime import datetime

from src.domain.shared.errors import MessageValidationError

__all__ = ["MessageContent", "Message"]


@dataclass(frozen=True)
class MessageContent:
    """Value object representing the content of a message."""

    value: str

    def __post_init__(self) -> None:
        """Validate message content."""
        if not self.value:
            raise MessageValidationError("Message content cannot be empty")
        if len(self.value) > 10000:
            raise MessageValidationError("Message content too long (max 10000 characters)")

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class Message:
    """Value object representing a message in a conversation."""

    role: str
    content: MessageContent
    timestamp: datetime = field(default_factory=datetime.now)

    def __post_init__(self) -> None:
        """Validate message."""
        valid_roles = {"system", "user", "assistant"}
        if self.role not in valid_roles:
            raise MessageValidationError(f"Invalid role: {self.role}")

    def to_dict(self) -> dict[str, str]:
        """Convert message to dictionary."""
        return {"role": self.role, "content": self.content.value}

    def __eq__(self, other: object) -> bool:
        """Compare messages by value (not identity)."""
        if not isinstance(other, Message):
            return False
        return (self.role, self.content.value) == (
            other.role,
            other.content.value,
        )
