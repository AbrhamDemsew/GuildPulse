"""Repository protocols for domain."""

from typing import Protocol

from guildpulse.domain.channel.aggregate import Channel


class MessageRepository(Protocol):
    """Repository interface for Channel persistence."""

    def save(self, channel: Channel) -> None:
        """Save a channel to persistent storage."""

    def get(self, channel_id: int) -> Channel: ...

    def get_or_create(self, channel_id: int) -> Channel: ...
