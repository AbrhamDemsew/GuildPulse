from typing import Any, Dict

from utils import generate_response


class OllamaClient:
    def __init__(self, api_url: str, api_key: str):
        self.api_url = api_url
        self.api_key = api_key

    def generate_response(self, payload: Dict[str, Any]) -> str:
        return generate_response(self.api_url, self.api_key, payload)


class OpenAIClient(OllamaClient):
    def __init__(self, api_url: str, api_key: str):
        super().__init__(api_url, api_key)
