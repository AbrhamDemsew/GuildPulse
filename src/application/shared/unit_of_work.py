"""Shared application utilities."""

from src.domain.channel.aggregate import Channel


class UnitOfWork:
    """Basic unit of work for consistency."""

    def __init__(self) -> None:
        self.changes: list[Channel] = []

    def register_mutation(self, channel: Channel) -> None:
        """Register a channel that has been modified."""
        self.changes.append(channel)

    def commit(self) -> None:
        """Commit changes."""
        self.changes.clear()

    def rollback(self) -> None:
        """Rollback changes."""
        self.changes.clear()
