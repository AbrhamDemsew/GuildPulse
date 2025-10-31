"""OpenAI adapter implementation."""

from typing import TYPE_CHECKING, Any

from guildpulse.domain.shared.completion_result import CompletionResult
from guildpulse.infrastructure.ai.openai.client import OpenAIClient

if TYPE_CHECKING:
    from guildpulse.domain.channel.aggregate import Channel


class OpenAIServiceAdapter:
    """Adapter for OpenAI API service."""

    def __init__(self, client: OpenAIClient, default_system_prompt: str = "") -> None:
        self.client = client
        self.default_system_prompt = default_system_prompt

    def generate_reply(
        self,
        channel: "Channel",
        image_urls: tuple[str, ...] = (),
        *,
        system_prompt: str | None = None,
        knowledge_context: str | None = None,
        model_name: str | None = None,
        max_tokens: int | None = None,
        temperature: float | None = None,
    ) -> CompletionResult:
        messages = channel.get_messages_for_api()
        prompt = system_prompt or self.default_system_prompt
        if knowledge_context:
            prompt = f"{prompt}\n\n{knowledge_context}"

        api_messages: list[dict[str, Any]] = [{"role": "system", "content": prompt}]
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

        prompt_estimate = sum(len(str(item.get("content", ""))) for item in api_messages) // 4
        content = self.client.chat_completion(
            api_messages,
            model=model_name,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        completion_estimate = max(1, len(content) // 4)
        return CompletionResult(
            content=content,
            prompt_tokens=prompt_estimate,
            completion_tokens=completion_estimate,
        )
