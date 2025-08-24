from typing import Any, Dict

import requests
from bs4 import BeautifulSoup


def fetch_url_content(url: str) -> str:
    """
    Fetch the content of the URL.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        return soup.get_text()[:1000]
    except requests.RequestException as e:
        return f"Error fetching content: {e}"


def generate_response(api_url: str, api_key: str, payload: Dict[str, Any]) -> str:
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
        "accept": "application/json",
    }
    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=None)
        response.raise_for_status()
        response_json = response.json()
        if "choices" in response_json and len(response_json["choices"]) > 0:
            return response_json["choices"][0]["message"]["content"]
        else:
            return "No response from API."
    except requests.RequestException as e:
        return "Error: {}".format(e)
