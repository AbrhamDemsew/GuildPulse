"""In-memory event publisher for development/testing."""

import logging
from src.application.shared.event_publisher import EventPublisherPort
from src.domain.shared.domain_event import DomainEvent

logger = logging.getLogger(__name__)


class InMemoryEventPublisher(EventPublisherPort):
    """In-memory event publisher for development/testing."""

    def __init__(self) -> None:
        self._events: list[DomainEvent] = []

    def publish(self, event: DomainEvent) -> None:
        """Publish a single domain event."""
        self._events.append(event)
        logger.debug(f"Published event: {event}")

    def publish_all(self, events: list[DomainEvent]) -> None:
        """Publish multiple domain events."""
        for event in events:
            self.publish(event)

    def get_events(self) -> list[DomainEvent]:
        """Get all published events (for testing)."""
        return self._events

    def clear(self) -> None:
        """Clear all published events."""
        self._events.clear()