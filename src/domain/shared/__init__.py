"""Shared domain package."""

from src.domain.shared.errors import (
    ChannelNotFoundError,
    ConversationHistoryError,
    DomainError,
    MessageValidationError,
)
from src.domain.shared.events import MessageGenerated

__all__ = [
    "DomainError",
    "ChannelNotFoundError",
    "MessageValidationError",
    "ConversationHistoryError",
    "MessageGenerated",
]
