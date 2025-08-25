import requests
from interface_adapters.api_client import OpenAIClient


class ImageProcessor:
    def __init__(self, api_client: OpenAIClient):
        self.api_client = api_client

    def describe_image(self, image_url: str) -> str:
        """
        Describe the image using the API client.
        """
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

        response = self.api_client.generate_response(payload)

        if response is None:
            raise ValueError("The API client returned None, which is not expected.")
        return response

    def generate_image(self, prompt: str) -> str:
        """
        Generate an image based on the given prompt.
        """
        url = self.api_client.api_url
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + self.api_client.api_key,
        }
        data = {
            "model_name": "FLUX.1-dev",
            "prompt": prompt,
            "steps": 8,
            "cfg_scale": 5,
            "enable_refiner": False,
            "height": 1024,
            "width": 1024,
            "backend": "auto",
        }
        response = requests.post(url, headers=headers, json=data)
        response_data = response.json()
        return response_data["images"][0]["image"]
