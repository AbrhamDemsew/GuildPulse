"""Application ports for domain services."""

from typing import Protocol

from src.domain.channel.aggregate import Channel


class AIServicePort(Protocol):
    """Port for AI service operations."""

    def generate_reply(self, channel: Channel) -> str: ...

    def describe_image(self, image_url: str, prompt: str = "Describe this image.") -> str: ...

    def generate_image(self, prompt: str) -> str: ...
