"""Base class for aggregate roots."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, TypeVar

from src.domain.shared.entity import Entity
from src.domain.shared.domain_event import DomainEvent

ID = TypeVar("ID")


@dataclass
class AggregateRoot(Entity[ID]):
    """Base class for aggregate roots that manage consistency boundary."""

    _domain_events: List[DomainEvent] = field(default_factory=list, init=False, repr=False)

    def add_domain_event(self, event: DomainEvent) -> None:
        """Add a domain event to the aggregate."""
        self._domain_events.append(event)

    def clear_domain_events(self) -> None:
        """Clear domain events after publishing."""
        self._domain_events.clear()

    @property
    def domain_events(self) -> List[DomainEvent]:
        """Get all domain events."""
        return self._domain_events.copy()
