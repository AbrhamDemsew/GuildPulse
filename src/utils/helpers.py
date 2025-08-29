import re
from typing import Any


def extract_urls_from_text(text: str) -> list[str]:
    """Extract all URLs from text."""
    urls = re.findall(r"(https?://\S+)", text)
    return urls


def extract_image_urls_from_text(text: str) -> list[str]:
    """Extract image URLs from text based on extensions."""
    image_extensions = [".png", ".jpg", ".jpeg", ".gif", ".webp"]
    image_urls = []

    for url in extract_urls_from_text(text):
        if any(ext in url.lower() for ext in image_extensions):
            image_urls.append(url)

    return image_urls


def sanitize_input(text: str, max_length: int = 2000) -> str:
    """Sanitize user input by limiting length."""
    if len(text) > max_length:
        return text[:max_length] + "..."
    return text


def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text to max length with ellipsis."""
    if len(text) > max_length:
        return text[:max_length] + "..."
    return text


def clean_discord_mention(text: str, bot_id: int) -> str:
    """Remove Discord bot mentions from text."""
    return text.replace(f"<@{bot_id}>", "").strip()


def extract_command_from_text(text: str, prefix: str = "*") -> str | None:
    """Extract command from text."""
    if text.startswith(prefix) and len(text) > len(prefix):
        return text[len(prefix) :].strip()
    return None


def validate_url(url: str) -> bool:
    """Validate if string is a valid URL."""
    pattern = r"^(https?://)?([\da-z\.-]+)\.([a-z\.]{2,6})([/\w \.-]*)*/?$"
    return bool(re.match(pattern, url))


def format_error(error: Exception) -> str:
    """Format exception into a user-friendly error message."""
    return f"Erreur: {str(error)}"


def get_timestamp() -> str:
    """Get current timestamp in ISO format."""
    from datetime import datetime

    return datetime.utcnow().isoformat()


def safe_dict_get(data: dict[str, Any], key: str, default: Any = None) -> Any:
    """Safely get value from dictionary with default."""
    return data.get(key, default)


def safe_list_get(lst: list[Any], index: int, default: Any = None) -> Any:
    """Safely get value from list with default."""
    try:
        return lst[index]
    except (IndexError, TypeError):
        return default


def chunk_text(text: str, max_length: int = 4000) -> list[str]:
    """Split text into chunks of max_length."""
    chunks = []
    for i in range(0, len(text), max_length):
        chunks.append(text[i : i + max_length])
    return chunks


def mask_sensitive_data(text: str) -> str:
    """Mask sensitive data like API keys or tokens."""
    import re as re_module

    patterns = [
        (r"(Bearer\s+)?(sk-[a-zA-Z0-9]{32})", r"\1***HIDDEN***"),
        (r"(key=)([a-zA-Z0-9_-]+)", r"\1***HIDDEN***"),
        (r"(token=)([a-zA-Z0-9_-]+)", r"\1***HIDDEN***"),
    ]

    for pattern, replacement in patterns:
        text = re_module.sub(pattern, replacement, text)

    return text


def normalize_whitespace(text: str) -> str:
    """Normalize whitespace in text."""
    import re as re_module

    return re_module.sub(r"\s+", " ", text).strip()


def validate_email(email: str) -> bool:
    """Validate email format."""
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def validate_discord_id(discord_id: str) -> bool:
    """Validate Discord ID format."""
    return discord_id.isdigit() and 17 <= len(discord_id) <= 20


def convert_to_int(value: str, default: int = 0) -> int:
    """Convert string to int with default."""
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def convert_to_float(value: str, default: float = 0.0) -> float:
    """Convert string to float with default."""
    try:
        return float(value)
    except (ValueError, TypeError):
        return default
