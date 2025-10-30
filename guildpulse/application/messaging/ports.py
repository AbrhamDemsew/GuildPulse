"""Deprecated: Application ports for domain services."""

from typing import Protocol

from guildpulse.domain.channel.aggregate import Channel


class AIServicePort(Protocol):
    """Deprecated: Use IAIServicePort from application.ports.ai_service_port."""

    def generate_reply(self, channel: Channel, image_urls: tuple[str, ...] = ()) -> str: ...

    def __init_subclass__(cls, **kwargs):
        import warnings

        warnings.warn(
            "AIServicePort is deprecated. Use IAIServicePort from application.ports.ai_service_port.",
            DeprecationWarning,
            stacklevel=2,
        )
