"""OpenAI adapter implementation."""

from typing import TYPE_CHECKING

from src.application.messaging.ports import AIServicePort
from src.config import get_settings
from src.infrastructure.ai.openai.client import OpenAIClient

if TYPE_CHECKING:
    from src.domain.channel.aggregate import Channel


class OpenAIServiceAdapter(AIServicePort):
    """Adapter for OpenAI API service."""

    def __init__(self, client: OpenAIClient) -> None:
        self.client = client
        self.settings = get_settings()

    def generate_reply(self, channel: "Channel") -> str:
        """Generate a reply using OpenAI."""
        messages = channel.get_messages_for_api()
        system_prompt = self.settings.CHAT_SYSTEM_PROMPT
        api_messages = [{"role": "system", "content": system_prompt}]
        for msg in messages[-100:]:
            api_messages.append({"role": msg["role"], "content": msg["content"]})
        return self.client.chat_completion(api_messages)

    def describe_image(self, image_url: str, prompt: str = "Describe this image.") -> str:
        """Describe an image."""
        return self.client.describe_image(image_url, prompt)

    def generate_image(self, prompt: str) -> str:
        """Generate an image."""
        return self.client.generate_image(prompt)
