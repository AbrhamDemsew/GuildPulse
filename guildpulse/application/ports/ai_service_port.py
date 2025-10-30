"""Protocol for AI service operations."""

from typing import Protocol

from guildpulse.domain.channel.aggregate import Channel


class IAIServicePort(Protocol):
    """Protocol for AI service operations."""

    def generate_reply(self, channel: Channel, image_urls: tuple[str, ...] = ()) -> str:
        """Generate a reply for the channel conversation."""
