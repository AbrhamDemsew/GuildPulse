import logging
from typing import Any, Dict, List

from domain.entities import ConversationHistory
from interface_adapters.api_client import OllamaClient, OpenAIClient
from use_cases.image_processing import ImageProcessor


class MessageProcessor:
    def __init__(
        self,
        history: ConversationHistory,
        ollama_client: OllamaClient,
        openai_client: OpenAIClient,
    ):
        self.history = history
        self.ollama_client = ollama_client
        self.image_processor = ImageProcessor(openai_client)
        logging.debug(
            "MessageProcessor initialized with history, ollama_client, and openai_client."
        )

    def process_message(
        self, channel_id: int, messages: List[Dict[str, Any]], image_url: str = ""
    ) -> str:
        """
        Process the message and return the response.
        """
        logging.debug(
            f"Processing message for channel_id: {channel_id} with messages: {messages} and image_url: {image_url}"
        )
        if image_url:
            logging.debug(f"Image URL provided: {image_url}")
            image_description = self.image_processor.describe_image(image_url)
            messages.append(
                {
                    "role": "system",
                    "content": f"description de l'image: {image_description}",
                }
            )

        payload = {
            "model": "mannix/gemma2-9b-sppo-iter3:latest",
            "messages": messages,
        }
        response = self.ollama_client.generate_response(payload)
        logging.info(f"Generated response: {response}")
        return response
