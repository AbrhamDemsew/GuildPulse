"""Shared domain package."""

from guildpulse.domain.shared.errors import (
    ChannelNotFoundError,
    ConversationHistoryError,
    DomainError,
    MessageValidationError,
)

__all__ = [
    "DomainError",
    "ChannelNotFoundError",
    "MessageValidationError",
    "ConversationHistoryError",
]
