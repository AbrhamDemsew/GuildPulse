from typing import Any, Dict, List

class ConversationHistory:
    def __init__(self):
        self.conversations: Dict[int, List[Dict[str, Any]]] = {}
        logging.debug("ConversationHistory initialized.")

    def add_message(self, channel_id: int, message: Dict[str, Any]):
        if channel_id not in self.conversations:
            self.conversations[channel_id] = []
        self.conversations[channel_id].append(message)
        logging.debug(f"Added message to channel_id {channel_id}: {message}")

    def get_history(self, channel_id: int) -> List[Dict[str, Any]]:
        history = self.conversations.get(channel_id, [])
        logging.debug(f"Retrieved history for channel_id {channel_id}: {history}")
        return history
