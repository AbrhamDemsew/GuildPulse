import requests
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
    def generate_image(self, prompt: str) -> str:
        url = "https://api.hyperbolic.xyz/v1/image/generation"
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJuY2xzcGllcnJvdEBnbWFpbC5jb20ifQ.DRTxzUIbTmif-4djHhODe84RJFnxN8Qi70WrCDlvxJA"
        }
        data = {
            "model_name": "FLUX.1-dev",
            "prompt": prompt,
            "steps": 30,
            "cfg_scale": 5,
            "enable_refiner": False,
            "height": 1024,
            "width": 1024,
            "backend": "auto"
        }
        response = requests.post(url, headers=headers, json=data)
        response_data = response.json()
        return response_data.get("image_url", "No image generated")
