import logging
import os
import sys
from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    DISCORD_TOKEN: str = Field(default="", description="Discord bot token")

    OPENAI_API_KEY: str = Field(default="", description="OpenAI API key")
    OPENAI_BASE_URL: str = Field(
        default="https://api.openai.com/v1",
        description=("OpenAI API base URL (supports proxies like Ollama)"),
    )
    OPENAI_MODEL: str = Field(default="gpt-4o-mini", description="Default model name")
    OPENAI_MAX_TOKENS: int = Field(default=500, description="Maximum tokens")
    OPENAI_TEMPERATURE: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="Temperature for generation",
    )

    ENABLE_IMAGE_GENERATION: bool = Field(
        default=True, description="Enable image generation feature"
    )
    ENABLE_IMAGE_DESCRIPTION: bool = Field(
        default=True, description="Enable image description feature"
    )

    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    DEBUG: bool = Field(default=False, description="Debug mode")

    IMAGE_DESCRIPTION_MODEL: str = Field(
        default="gpt-4o-mini", description="Model for image description"
    )
    IMAGE_GENERATION_MODEL: str = Field(
        default="dall-e-3", description="Model for image generation"
    )

    @field_validator("OPENAI_API_KEY")
    @classmethod
    def validate_api_key(cls, v: str) -> str:
        if not v and not cls.model_config.get("env_file"):
            raise ValueError("OPENAI_API_KEY is required")
        return v

    @field_validator("LOG_LEVEL")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if v.upper() not in valid_levels:
            raise ValueError(f"Invalid log level: {v}. Must be one of {valid_levels}")
        return v.upper()


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    logger = logging.getLogger(__name__)
    try:
        settings = Settings()
        logger.info("Settings loaded successfully")
        return settings
    except Exception as e:
        logger.error(f"Failed to load settings: {e}")
        raise


def setup_logging(settings: Settings) -> None:
    """Configure logging with standard library."""
    log_format = "%(asctime)s | %(levelname)s | %(name)s:%(funcName)s:%(lineno)d - %(message)s"
    log_file = "logs/info.log" if settings.LOG_LEVEL.upper() != "DEBUG" else "logs/debug.log"

    if not os.path.exists("logs"):
        os.makedirs("logs")

    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL.upper()),
        format=log_format,
        handlers=[logging.StreamHandler(sys.stdout), logging.FileHandler(log_file)],
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    logging.info("Logging configured successfully")
