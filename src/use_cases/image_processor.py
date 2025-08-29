import logging

from src.domain.entities import ConversationHistory
from src.interface_adapters.openai_client import OpenAIClient


class ImageProcessor:
    """Processes images using OpenAI API."""

    def __init__(
        self,
        client: OpenAIClient,
        history: ConversationHistory | None = None,
    ):
        self.client = client
        self.history = history
        self.logger = logging.getLogger(__name__)
        self.logger.info("ImageProcessor initialized")

    def describe_image(
        self,
        image_url: str,
        prompt: str | None = None,
        max_tokens: int = 300,
    ) -> str:
        """Describe an image using the OpenAI client."""
        try:
            if prompt is None:
                prompt = "Décris cette image de manière détaillée."

            self.logger.debug(f"Describing image with URL: {image_url}")

            description = self.client.describe_image(
                image_url=image_url, prompt=prompt, max_tokens=max_tokens
            )

            if description is None:
                raise ValueError("Image description returned None")

            self.logger.info(f"Image description: {description}")
            return description

        except Exception as e:
            self.logger.error(f"Error describing image: {e}")
            raise ValueError(f"Failed to describe image: {e}") from e

    async def describe_image_async(
        self,
        image_url: str,
        prompt: str | None = None,
        max_tokens: int = 300,
    ) -> str:
        """Asynchronously describe an image using the OpenAI client."""
        try:
            if prompt is None:
                prompt = "Décris cette image de manière détaillée."

            self.logger.debug(f"Async describing image with URL: {image_url}")

            description = await self.client.describe_image(
                image_url=image_url, prompt=prompt, max_tokens=max_tokens
            )

            if description is None:
                raise ValueError("Image description returned None")

            self.logger.info(f"Async image description: {description}")
            return description

        except Exception as e:
            self.logger.error(f"Error in async image description: {e}")
            raise ValueError(f"Failed to describe image asynchronously: {e}") from e

    def generate_image(
        self, prompt: str, size: str = "1024x1024", quality: str = "standard"
    ) -> str:
        """Generate an image based on the given prompt using OpenAI client."""
        try:
            self.logger.debug(f"Generating image with prompt: {prompt}")

            image_url = self.client.generate_image(prompt=prompt, size=size, quality=quality)

            if image_url is None:
                raise ValueError("Image generation returned None")

            self.logger.info(f"Generated image URL: {image_url}")
            return image_url

        except Exception as e:
            self.logger.error(f"Error generating image: {e}")
            raise ValueError(f"Failed to generate image: {e}") from e

    async def generate_image_async(
        self, prompt: str, size: str = "1024x1024", quality: str = "standard"
    ) -> str:
        """Asynchronously generate an image using OpenAI client."""
        try:
            self.logger.debug(f"Async generating image with prompt: {prompt}")

            image_url = await self.client.generate_image(prompt=prompt, size=size, quality=quality)

            if image_url is None:
                raise ValueError("Image generation returned None")

            self.logger.info(f"Async generated image URL: {image_url}")
            return image_url

        except Exception as e:
            self.logger.error(f"Error in async image generation: {e}")
            raise ValueError(f"Failed to generate image asynchronously: {e}") from e
