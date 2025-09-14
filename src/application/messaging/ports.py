"""Application ports for domain services."""

from typing import Protocol

from src.domain.channel.aggregate import Channel


class AIServicePort(Protocol):
    """Port for AI service operations."""

    def generate_reply(self, channel: Channel, image_urls: tuple[str, ...] = ()) -> str: ...
