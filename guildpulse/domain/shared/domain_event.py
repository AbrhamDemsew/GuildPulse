"""Domain events base class."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class DomainEvent:
    """Base class for domain events representing significant domain changes."""

    event_id: str
    occurred_at: datetime
    aggregate_id: str

    @staticmethod
    def generate_event_id() -> str:
        """Generate unique event ID."""
        import uuid

        return str(uuid.uuid4())

    @staticmethod
    def now() -> datetime:
        """Get current timestamp."""
        return datetime.now()

    @property
    def event_type(self) -> str:
        """Override in subclasses to return event type."""
        raise NotImplementedError
