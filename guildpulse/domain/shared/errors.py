"""Domain errors for the domain model."""


class DomainError(Exception):
    """Base class for domain errors."""


class ChannelNotFoundError(DomainError):
    """Raised when a channel is not found."""


class MessageValidationError(DomainError):
    """Raised when a message is invalid."""


class ConversationHistoryError(DomainError):
    """Raised when conversation history operations fail."""
