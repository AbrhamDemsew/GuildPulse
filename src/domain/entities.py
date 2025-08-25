from typing import Any, Dict, List

class ConversationHistory:
    def __init__(self):
        self.history: Dict[int, List[Dict[str, Any]]] = {}

    def add_message(self, channel_id: int, message: Dict[str, Any]):
        if channel_id not in self.history:
            self.history[channel_id] = []
        self.history[channel_id].append(message)

    def get_history(self, channel_id: int) -> List[Dict[str, Any]]:
        return self.history.get(channel_id, [])
