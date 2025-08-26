import requests
from interface_adapters.api_client import OpenAIClient


class ImageProcessor:
    def __init__(self, api_client: OpenAIClient):
        self.client = api_client
        logging.debug("ImageProcessor initialized with api_client.")

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

        logging.debug(f"Describing image with URL: {image_url}")
        response = self.client.generate_response(payload)
        logging.info(f"Image description response: {response}")

        if response is None:
            raise ValueError("The API client returned None, which is not expected.")
        return response

    def generate_image(self, prompt: str) -> str:
        """
        Generate an image based on the given prompt.
        """
        url = self.client.api_url
        logging.debug(f"Generating image with prompt: {prompt}")
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {self.client.api_key}"}
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
        logging.info(f"Generated image response: {response.json()}")
        response_data = response.json()
        return response_data["images"][0]["image"]
