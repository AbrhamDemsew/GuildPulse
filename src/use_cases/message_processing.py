import asyncio
import logging

from src.domain.entities import ConversationHistory
from src.interface_adapters.openai_client import OpenAIClient


class MessageProcessor:
    """Processes messages using OpenAI API."""

    def __init__(
        self,
        history: ConversationHistory,
        client: OpenAIClient,
    ):
        self.history = history
        self.client = client
        self.logger = logging.getLogger(__name__)
        self.logger.info("MessageProcessor initialized")
        self.channel_locks: dict[int, asyncio.Lock] = {}

    def get_lock(self, channel_id: int) -> asyncio.Lock:
        """Get or create a lock for a specific channel."""
        if channel_id not in self.channel_locks:
            self.channel_locks[channel_id] = asyncio.Lock()
        return self.channel_locks[channel_id]

    async def generate_reply(self, channel_id: int) -> str:
        """Generate a reply using conversation history."""
        async with self.get_lock(channel_id):
            try:
                history = self.history.get_history(channel_id)
                system_prompt = {
                    "role": "system",
                    "content": "Tu es un assistant Discord utile et amical. Réponds de manière conversationnelle et naturelle en français. Ne réponds jamais avec du code Python, sauf si l'utilisateur demande explicitement du code. Sois concis, amical et engageant.",
                }
                messages = [system_prompt] + history
                response = await self.client.chat_completion_async(messages=messages)
                self.logger.info(f"Generated response for channel_id {channel_id}")
                return response

            except Exception as e:
                self.logger.error(f"Error generating reply: {e}")
                return f"Erreur lors de la génération de la réponse: {e}"

    def add_to_conversation(self, channel_id: int, role: str, content: str) -> None:
        """Add a message to the conversation history."""
        message = {"role": role, "content": content}
        self.history.add_message(channel_id, message)
        self.logger.debug(f"Added message to channel_id {channel_id}")

    def get_conversation_history(self, channel_id: int) -> list[dict[str, str]]:
        """Get conversation history for a channel."""
        return self.history.get_history(channel_id)
