"""Base class for entities with identity."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, TypeVar

ID = TypeVar("ID")


@dataclass
class Entity(Generic[ID]):
    """Base class for entities that have identity-based equality."""

    id: ID

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Entity):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)
