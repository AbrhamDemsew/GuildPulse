import asyncio
import logging
from typing import Any

from openai import OpenAI
from openai.types.chat import ChatCompletion


class OpenAIClient:
    """Unified OpenAI API client supporting chat completions."""

    def __init__(
        self,
        api_key: str,
        base_url: str,
        model: str,
        max_tokens: int = 500,
        temperature: float = 0.7,
    ) -> None:
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"OpenAI client initialized with model: {model}, base_url: {base_url}")

    def chat_completion(
        self,
        messages: list[dict[str, Any]],
        model: str | None = None,
        max_tokens: int | None = None,
        temperature: float | None = None,
    ) -> str:
        """Generate a chat completion response."""
        try:
            self.logger.debug(f"Chat completion with messages: {messages}")

            response_kwargs: dict[str, Any] = {
                "model": model or self.model,
                "messages": messages,
                "max_tokens": max_tokens or self.max_tokens,
                "temperature": temperature or self.temperature,
            }
            if "thinking" in (model or self.model).lower():
                response_kwargs["extra_body"] = {"chat_template_kwargs": {"enable_thinking": False}}

            response: ChatCompletion = self.client.chat.completions.create(**response_kwargs)

            message = response.choices[0].message
            content = message.content
            if content is None:
                raise ValueError("No content returned from chat completion")
            self.logger.debug(f"Chat completion response: {content}")
            return content

        except Exception as e:
            self.logger.error(f"Error in chat completion: {e}")
            raise

    async def chat_completion_async(
        self,
        messages: list[dict[str, Any]],
        model: str | None = None,
        max_tokens: int | None = None,
        temperature: float | None = None,
    ) -> str:
        """Asynchronously generate a chat completion response."""
        try:
            return await asyncio.to_thread(
                self.chat_completion,
                messages,
                model,
                max_tokens,
                temperature,
            )

        except Exception as e:
            self.logger.error(f"Error in async chat completion: {e}")
            raise
