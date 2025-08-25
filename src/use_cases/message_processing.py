from typing import Any, Dict, List
from domain.entities import ConversationHistory
from interface_adapters.api_client import OllamaClient, OpenAIClient
from use_cases.image_processing import ImageProcessor

class MessageProcessor:
    def __init__(
        self,
        conversation_history: ConversationHistory,
        ollama_api_client: OllamaClient,
        openai_api_client: OpenAIClient,
    ):
        self.conversation_history = conversation_history
        self.ollama_api_client = ollama_api_client
        self.image_processor = ImageProcessor(openai_api_client)

    def process_message(
        self, channel_id: int, messages: List[Dict[str, Any]], image_url: str = ""
    ) -> str:
        """
        Process the message and return the response.
        """
        if image_url:
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
        return self.ollama_api_client.generate_response(payload)
