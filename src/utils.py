from typing import Any, Dict
import requests
from bs4 import BeautifulSoup


def fetch_url_content(url: str) -> str:
    """
    Fetch the content of the URL.
    """
    try:
        logging.debug(f"Fetching URL content for: {url}")
        response = requests.get(url)
        logging.info(f"Fetched URL content: {response.text[:100]}")
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        content = soup.get_text()[:1000]
        logging.debug(f"Extracted content: {content}")
        return content
    except requests.RequestException as e:
        return f"Error fetching content: {e}"


def generate_response(api_url: str, api_key: str, payload: Dict[str, Any]) -> str:
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
        "accept": "application/json",
    }
    try:
        logging.debug(f"Generating response with payload: {payload}")
        response = requests.post(api_url, headers=headers, json=payload, timeout=None)
        logging.info(f"Generated response: {response.json()}")
        response.raise_for_status()
        response_json = response.json()
        if "choices" in response_json and len(response_json["choices"]) > 0:
            return response_json["choices"][0]["message"]["content"]
        else:
            return "No response from API."
    except requests.RequestException as e:
        return "Error: {}".format(e)
