import asyncio
import logging
from typing import Any, Literal

from openai import OpenAI


class OpenAIClient:
    """Unified OpenAI API client supporting chat completions, image description, and generation."""

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
                response_kwargs["extra_body"] = {
                    "chat_template_kwargs": {"enable_thinking": False}
                }

            response = self.client.chat.completions.create(**response_kwargs)

            content = response.choices[0].message.content
            if content is None:
                raise ValueError("No content returned from chat completion")
            self.logger.debug(f"Chat completion response: {content}")
            return content

        except Exception as e:
            self.logger.error(f"Error in chat completion: {e}")
            raise

    def describe_image(
        self,
        image_url: str,
        prompt: str = "Décris cette image de manière détaillée.",
        max_tokens: int = 300,
    ) -> str:
        """Describe an image using vision capabilities."""
        try:
            self.logger.debug(f"Describing image with URL: {image_url}")

            response_kwargs = {
                "model": self.model,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt,
                            },
                            {
                                "type": "image_url",
                                "image_url": {"url": image_url},
                            },
                        ],
                    }
                ],
                "max_tokens": max_tokens,
            }
            if "thinking" in self.model.lower():
                response_kwargs["extra_body"] = {
                    "chat_template_kwargs": {"enable_thinking": False}
                }

            response = self.client.chat.completions.create(**response_kwargs)

            description = response.choices[0].message.content
            if description is None:
                raise ValueError("No description returned from image description")
            self.logger.info(f"Image description: {description}")
            return description

        except Exception as e:
            self.logger.error(f"Error describing image: {e}")
            raise

    def generate_image(
        self,
        prompt: str,
        model: str | None = None,
        size: Literal[
            "auto", "1024x1024", "1536x1024", "1024x1536", "256x256",
            "512x512", "1792x1024", "1024x1792"
        ] = "1024x1024",
        quality: Literal[
            "standard", "hd", "low", "medium", "high", "auto"
        ] = "standard",
    ) -> str:
        """Generate an image based on the given prompt."""
        try:
            self.logger.debug(f"Generating image with prompt: {prompt}")

            response = self.client.images.generate(
                prompt=prompt,
                model=model or "dall-e-3",
                size=size,
                quality=quality,
                n=1,
            )

            if response.data is None or len(response.data) == 0:
                raise ValueError("No image data returned from generation")

            image_data = response.data[0]
            if image_data.url is None:
                raise ValueError("No image URL returned from generation")

            image_url = image_data.url
            self.logger.info(f"Generated image: {image_url}")
            return image_url

        except Exception as e:
            self.logger.error(f"Error generating image: {e}")
            raise

    async def chat_completion_async(
        self,
        messages: list[dict[str, str]],
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

    def health_check(self) -> bool:
        """Check if the API client is healthy."""
        try:
            self.client.models.list()
            self.logger.info("OpenAI client health check passed")
            return True
        except Exception as e:
            self.logger.error(f"OpenAI client health check failed: {e}")
            return False

    @property
    def api_key(self) -> str:
        """Return the API key."""
        return self.client.api_key
