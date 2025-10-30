"""Protocol for channel repository operations."""

from typing import Protocol

from guildpulse.domain.channel.aggregate import Channel


class IChannelRepositoryPort(Protocol):
    """Protocol for channel repository operations."""

    def save(self, channel: Channel) -> None:
        """Save a channel to persistent storage."""

    def get(self, channel_id: int) -> Channel:
        """Get a channel by ID."""

    def get_or_create(self, channel_id: int) -> Channel:
        """Get existing channel or create a new one."""
