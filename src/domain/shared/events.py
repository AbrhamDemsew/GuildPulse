"""Domain events for the domain model."""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class MessageGenerated:
    """Event raised when a message is generated in a channel."""

    channel_id: int
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
