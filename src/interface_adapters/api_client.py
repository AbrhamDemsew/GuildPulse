from typing import Any, Dict, Optional

import requests


class OllamaClient:
    def __init__(self, api_url: str, api_key: str):
        self.api_url = api_url
        self.api_key = api_key

    def generate_response(self, payload: Dict[str, Any]) -> Optional[str]:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "accept": "application/json",
        }
        try:
            response = requests.post(
                self.api_url, headers=headers, json=payload, timeout=None
            )
            response.raise_for_status()
            response_json = response.json()
            if "choices" in response_json and len(response_json["choices"]) > 0:
                return response_json["choices"][0]["message"]["content"]
            else:
                return None
        except requests.RequestException as e:
            return None


class OpenAIClient(OllamaClient):
    def __init__(self, api_url, api_key: str):
        super().__init__(api_url, api_key)
