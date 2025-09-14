"""Configuration adapter for infrastructure layer."""

import logging

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


class ConfigAdapter(BaseSettings):
    """Adapter for configuration with Pydantic."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    DISCORD_TOKEN: str = Field(default="", description="Discord bot token")
    OPENAI_API_KEY: str = Field(default="", description="OpenAI API key")
    OPENAI_BASE_URL: str = Field(
        default="https://api.openai.com/v1",
        description="OpenAI API base URL",
    )
    OPENAI_MODEL: str = Field(default="gpt-4o-mini", description="Default model")
    OPENAI_MAX_TOKENS: int = Field(default=500, description="Maximum tokens")
    OPENAI_TEMPERATURE: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="Temperature for generation",
    )
    CHAT_SYSTEM_PROMPT: str = Field(
        default=(
            "Tu es un bot Discord amical, intelligent et utile. "
            "Réponds de manière concise, claire et bienveillante. "
            "Utilise le français si la conversation est en français."
        ),
        description="System prompt for chat completions",
    )
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    DEBUG: bool = Field(default=False, description="Debug mode")

    @field_validator("DISCORD_TOKEN")
    @classmethod
    def validate_discord_token(cls, v: str) -> str:
        if not v:
            logger.warning("DISCORD_TOKEN is empty - bot will not start")
        return v

    @field_validator("OPENAI_API_KEY")
    @classmethod
    def validate_openai_key(cls, v: str) -> str:
        if not v:
            raise ValueError("OPENAI_API_KEY is required")
        return v

    @field_validator("LOG_LEVEL")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if v.upper() not in valid_levels:
            raise ValueError(f"Invalid log level: {v}")
        return v.upper()

    # Port implementation properties
    @property
    def discord_token(self) -> str:
        return self.DISCORD_TOKEN

    @property
    def openai_api_key(self) -> str:
        return self.OPENAI_API_KEY

    @property
    def openai_base_url(self) -> str:
        return self.OPENAI_BASE_URL

    @property
    def openai_model(self) -> str:
        return self.OPENAI_MODEL

    @property
    def openai_max_tokens(self) -> int:
        return self.OPENAI_MAX_TOKENS

    @property
    def openai_temperature(self) -> float:
        return self.OPENAI_TEMPERATURE

    @property
    def chat_system_prompt(self) -> str:
        return self.CHAT_SYSTEM_PROMPT

    @property
    def log_level(self) -> str:
        return self.LOG_LEVEL
