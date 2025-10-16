"""Protocol for configuration access."""
from typing import Protocol


class IConfigPort(Protocol):
    """Protocol for configuration access."""

    def get_discord_token(self) -> str:
        """Get the Discord bot token."""

    def get_openai_api_key(self) -> str:
        """Get the OpenAI API key."""

    def get_openai_base_url(self) -> str:
        """Get the OpenAI API base URL."""

    def get_openai_model(self) -> str:
        """Get the default OpenAI model name."""

    def get_openai_max_tokens(self) -> int:
        """Get maximum tokens for generation."""

    def get_openai_temperature(self) -> float:
        """Get generation temperature."""

    def get_system_prompt(self) -> str:
        """Get the system prompt for chat completions."""
