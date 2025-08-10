from interface_adapters.api_client import OpenAIClient


class ImageProcessor:
    def __init__(self, api_client: OpenAIClient):
        self.api_client = api_client

    def describe_image(self, image_url: str) -> str:
        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Décris cette image de manière détaillée.",
                        },
                        {"type": "image_url", "image_url": {"url": image_url}},
                    ],
                }
            ],
            "max_tokens": 300,
        }
        return self.api_client.generate_response(payload)
