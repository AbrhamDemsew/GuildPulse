"""In-memory implementation of ChannelRepository."""

from src.application.ports.channel_repository_port import IChannelRepositoryPort
from src.domain.channel.aggregate import Channel
from src.domain.shared.errors import ChannelNotFoundError


class InMemoryChannelRepository(IChannelRepositoryPort):
    """In-memory repository for Channel persistence."""

    def __init__(self) -> None:
        self._channels: dict[int, Channel] = {}

    def save(self, channel: Channel) -> None:
        """Save a channel."""
        self._channels[channel.id] = channel

    def get(self, channel_id: int) -> Channel:
        """Get a channel by ID."""
        if channel_id not in self._channels:
            raise ChannelNotFoundError(f"Channel {channel_id} not found")
        return self._channels[channel_id]

    def get_or_create(self, channel_id: int) -> Channel:
        """Get existing channel or create a new one."""
        if channel_id not in self._channels:
            self._channels[channel_id] = Channel(channel_id=channel_id)
        return self._channels[channel_id]
