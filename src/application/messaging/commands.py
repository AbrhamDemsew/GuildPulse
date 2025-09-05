"""Commands for messaging operations."""

from dataclasses import dataclass


@dataclass(frozen=True)
class AddMessageCommand:
    """Command to add a message to a channel."""

    channel_id: int
    role: str
    content: str


@dataclass(frozen=True)
class GenerateReplyCommand:
    """Command to generate a reply for a channel."""

    channel_id: int
    user_content: str


@dataclass(frozen=True)
class ClearChannelCommand:
    """Command to clear a channel's conversation history."""

    channel_id: int
