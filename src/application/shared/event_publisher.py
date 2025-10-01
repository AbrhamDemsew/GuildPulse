from typing import Protocol
from src.domain.shared.domain_event import DomainEvent


class EventPublisherPort(Protocol):
    """Port for publishing domain events."""

    def publish(self, event: DomainEvent) -> None:
        """Publish a single domain event."""

    def publish_all(self, events: list[DomainEvent]) -> None:
        """Publish multiple domain events."""