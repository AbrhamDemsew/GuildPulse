from datetime import datetime
from typing import Protocol


class DomainEvent(Protocol):
    """Interface for domain events."""

    @property
    def timestamp(self) -> datetime:
        """Event timestamp."""
        ...
