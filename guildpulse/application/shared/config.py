"""Application config port for dependency inversion."""

from typing import Protocol


class ConfigPort(Protocol):
    """Port for configuration access from domain and application layers."""

    @property
    def discord_token(self) -> str: ...

    @property
    def openai_api_key(self) -> str: ...

    @property
    def openai_base_url(self) -> str: ...

    @property
    def openai_model(self) -> str: ...

    @property
    def openai_max_tokens(self) -> int: ...

    @property
    def openai_temperature(self) -> float: ...

    @property
    def chat_system_prompt(self) -> str: ...

    @property
    def log_level(self) -> str: ...
