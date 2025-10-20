"""Config port for dependency inversion in domain layer."""

from typing import Protocol


class ConfigPort(Protocol):
    """Protocol for configuration access from domain layer."""

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