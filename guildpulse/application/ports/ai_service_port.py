"""Protocol for AI service operations."""

from typing import Protocol

from guildpulse.domain.channel.aggregate import Channel
from guildpulse.domain.shared.completion_result import CompletionResult


class IAIServicePort(Protocol):
    """Protocol for AI service operations."""

    def generate_reply(
        self,
        channel: Channel,
        image_urls: tuple[str, ...] = (),
        *,
        system_prompt: str | None = None,
        knowledge_context: str | None = None,
        model_name: str | None = None,
        max_tokens: int | None = None,
        temperature: float | None = None,
    ) -> CompletionResult:
        """Generate a reply for the channel conversation."""
