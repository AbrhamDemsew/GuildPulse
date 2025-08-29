from __future__ import annotations

import logging
from collections import deque


class ConversationHistory:
    """Manages conversation history across Discord channels with name handling."""

    def __init__(self) -> None:
        self.conversations: dict[int, deque[dict[str, str]]] = {}
        self.logger = logging.getLogger(__name__)
        self.logger.debug("ConversationHistory initialized")

    def add_message(self, channel_id: int, message: dict[str, str]) -> None:
        """Add a message to the conversation history for a channel."""
        if channel_id not in self.conversations:
            self.conversations[channel_id] = deque(maxlen=100)
        self.conversations[channel_id].append(message)
        self.logger.debug(f"Added message to channel_id {channel_id}: {message}")

    def get_history(self, channel_id: int) -> list[dict[str, str]]:
        """Get the conversation history for a channel (returns a copy)."""
        history = list(self.conversations.get(channel_id, deque(maxlen=100)))
        self.logger.debug(f"Retrieved history for channel_id {channel_id}: {len(history)} messages")
        return history

    def clear_history(self, channel_id: int) -> None:
        """Clear the conversation history for a channel."""
        if channel_id in self.conversations:
            del self.conversations[channel_id]
            self.logger.debug(f"Cleared history for channel_id {channel_id}")

    def get_all_channels(self) -> list[int]:
        """Get all channel IDs with conversation history."""
        return list(self.conversations.keys())
