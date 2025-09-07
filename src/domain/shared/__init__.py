"""Shared domain package."""

from src.domain.shared.errors import (
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
