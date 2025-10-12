"""Base class for immutable value objects."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Generic, TypeVar

Props = TypeVar("Props")


@dataclass(frozen=True)
class ValueObject(Generic[Props]):
    """Base class for immutable value objects with structural equality."""

    _props: Props

    @property
    def props(self) -> Props:
        """Get the props for comparison."""
        return self._props

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ValueObject):
            return False
        return self._props == other._props

    def __hash__(self) -> int:
        return hash(self._props)