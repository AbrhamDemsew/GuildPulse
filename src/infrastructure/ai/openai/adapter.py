"""OpenAI adapter implementation."""

from typing import TYPE_CHECKING, Any

from src.config import get_settings
from src.infrastructure.ai.openai.client import OpenAIClient

if TYPE_CHECKING:
    from src.domain.channel.aggregate import Channel


class OpenAIServiceAdapter:
    """Adapter for OpenAI API service."""

    def __init__(self, client: OpenAIClient) -> None:
        self.client = client
        self.settings = get_settings()

    def generate_reply(self, channel: "Channel", image_urls: tuple[str, ...] = ()) -> str:
        """Generate a reply using OpenAI."""
        messages = channel.get_messages_for_api()
        system_prompt = self.settings.CHAT_SYSTEM_PROMPT
        api_messages: list[dict[str, Any]] = [{"role": "system", "content": system_prompt}]
        for msg in messages[-100:]:
            api_messages.append({"role": msg["role"], "content": msg["content"]})

        if image_urls:
            last_message = api_messages[-1]
            if last_message["role"] == "user":
                text_content = last_message["content"]
                multimodal_content: list[dict[str, Any]] = [{"type": "text", "text": text_content}]
                for url in image_urls:
                    multimodal_content.append({"type": "image_url", "image_url": {"url": url}})
                api_messages[-1] = {"role": "user", "content": multimodal_content}

        return self.client.chat_completion(api_messages)
