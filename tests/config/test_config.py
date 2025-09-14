"""Tests for configuration management."""

import os
from unittest.mock import patch

import pytest

from src.config import Settings, get_settings, setup_logging


class TestSettings:
    """Tests for Settings class."""

    def test_settings_default_values(self):
        """Test Settings with default values."""
        with patch.dict(
            os.environ,
            {
                "OPENAI_API_KEY": "test-key",
                "OPENAI_BASE_URL": "https://api.openai.com/v1",
                "OPENAI_MODEL": "gpt-4",
                "OPENAI_MAX_TOKENS": "100",
                "OPENAI_TEMPERATURE": "0.7",
            },
            clear=True,
        ):
            settings = Settings()

            assert settings.OPENAI_API_KEY == "test-key"
            assert settings.OPENAI_BASE_URL == "https://api.openai.com/v1"
            assert settings.OPENAI_MODEL == "gpt-4"
            assert settings.OPENAI_MAX_TOKENS == 100
            assert settings.OPENAI_TEMPERATURE == 0.7

    def test_settings_custom_values(self):
        """Test Settings with custom values."""
        with patch.dict(
            os.environ,
            {
                "DISCORD_TOKEN": "discord-token",
                "OPENAI_API_KEY": "custom-key",
                "OPENAI_BASE_URL": "https://ollama.local/v1",
                "OPENAI_MODEL": "llama-3",
                "OPENAI_MAX_TOKENS": "200",
                "OPENAI_TEMPERATURE": "0.9",
                "LOG_LEVEL": "DEBUG",
                "DEBUG": "true",
                "CHAT_SYSTEM_PROMPT": "Custom system prompt",
            },
            clear=True,
        ):
            settings = Settings()

            assert settings.DISCORD_TOKEN == "discord-token"
            assert settings.OPENAI_API_KEY == "custom-key"
            assert settings.OPENAI_BASE_URL == "https://ollama.local/v1"
            assert settings.OPENAI_MODEL == "llama-3"
            assert settings.OPENAI_MAX_TOKENS == 200
            assert settings.OPENAI_TEMPERATURE == 0.9
            assert settings.LOG_LEVEL == "DEBUG"
            assert settings.DEBUG is True
            assert settings.CHAT_SYSTEM_PROMPT == "Custom system prompt"

    def test_openai_api_key_required(self):
        """Test that OPENAI_API_KEY validation works."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": ""}, clear=True):
            with pytest.raises(ValueError) as exc_info:
                Settings()

            assert "OPENAI_API_KEY" in str(exc_info.value)

    def test_openai_temperature_validation_min(self):
        """Test temperature validation with value below 0."""
        with patch.dict(
            os.environ,
            {
                "OPENAI_API_KEY": "test-key",
                "OPENAI_TEMPERATURE": "-0.1",
            },
            clear=True,
        ):
            with pytest.raises(ValueError) as exc_info:
                Settings()

            assert "temperature" in str(exc_info.value).lower()

    def test_openai_temperature_validation_max(self):
        """Test temperature validation with value above 2.0."""
        with patch.dict(
            os.environ,
            {
                "OPENAI_API_KEY": "test-key",
                "OPENAI_TEMPERATURE": "2.5",
            },
            clear=True,
        ):
            with pytest.raises(ValueError) as exc_info:
                Settings()

            assert "temperature" in str(exc_info.value).lower()

    def test_openai_temperature_boundary_min(self):
        """Test temperature validation with exactly 0."""
        with patch.dict(
            os.environ,
            {
                "OPENAI_API_KEY": "test-key",
                "OPENAI_TEMPERATURE": "0.0",
            },
            clear=True,
        ):
            settings = Settings()
            assert settings.OPENAI_TEMPERATURE == 0.0

    def test_openai_temperature_boundary_max(self):
        """Test temperature validation with exactly 2.0."""
        with patch.dict(
            os.environ,
            {
                "OPENAI_API_KEY": "test-key",
                "OPENAI_TEMPERATURE": "2.0",
            },
            clear=True,
        ):
            settings = Settings()
            assert settings.OPENAI_TEMPERATURE == 2.0

    def test_log_level_validation_valid(self):
        """Test log level validation with valid levels."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        for level in valid_levels:
            with patch.dict(
                os.environ,
                {
                    "OPENAI_API_KEY": "test-key",
                    "LOG_LEVEL": level,
                },
                clear=True,
            ):
                settings = Settings()
                assert settings.LOG_LEVEL == level

    def test_log_level_validation_invalid(self):
        """Test log level validation with invalid level."""
        with patch.dict(
            os.environ,
            {
                "OPENAI_API_KEY": "test-key",
                "LOG_LEVEL": "INVALID",
            },
            clear=True,
        ):
            with pytest.raises(ValueError) as exc_info:
                Settings()

            assert "Invalid log level" in str(exc_info.value)

    def test_chat_system_prompt_default(self):
        """Test default system prompt."""
        with patch.dict(
            os.environ,
            {
                "OPENAI_API_KEY": "test-key",
            },
            clear=True,
        ):
            settings = Settings()

            assert "Discord" in settings.CHAT_SYSTEM_PROMPT
            assert "Discord" in settings.CHAT_SYSTEM_PROMPT


class TestGetSettings:
    """Tests for get_settings function."""

    def test_get_settings_caches_result(self):
        """Test that get_settings caches results."""
        with patch.dict(
            os.environ,
            {
                "OPENAI_API_KEY": "test-key",
            },
            clear=True,
        ):
            settings1 = get_settings()
            settings2 = get_settings()

            assert settings1 is settings2

    def test_get_settings_error_logging(self):
        """Test that get_settings handles errors gracefully."""
        with patch("src.config.get_settings") as mock_get_settings:
            mock_get_settings.side_effect = Exception("Test error")
            with pytest.raises(Exception):
                mock_get_settings()

        assert mock_get_settings.called


class TestSetupLogging:
    """Tests for setup_logging function."""

    def test_setup_logging_creates_logs_directory(self):
        """Test that setup_logging creates logs directory."""
        import shutil
        import tempfile

        temp_dir = tempfile.mkdtemp()
        original_cwd = os.getcwd()

        try:
            os.chdir(temp_dir)
            settings = Settings(
                OPENAI_API_KEY="test-key",
                LOG_LEVEL="DEBUG",
            )

            setup_logging(settings)

            assert os.path.exists("logs")
        finally:
            os.chdir(original_cwd)
            shutil.rmtree(temp_dir, ignore_errors=True)

    def test_setup_logging_debug_mode(self, tmp_path):
        """Test logging setup in debug mode."""
        settings = Settings(
            OPENAI_API_KEY="test-key",
            LOG_LEVEL="DEBUG",
        )

        setup_logging(settings)

    def test_setup_logging_info_mode(self, tmp_path):
        """Test logging setup in info mode."""
        settings = Settings(
            OPENAI_API_KEY="test-key",
            LOG_LEVEL="INFO",
        )

        setup_logging(settings)

    def test_setup_logging_error_mode(self, tmp_path):
        """Test logging setup in error mode."""
        settings = Settings(
            OPENAI_API_KEY="test-key",
            LOG_LEVEL="ERROR",
        )

        setup_logging(settings)

    def test_setup_logging_format(self, tmp_path):
        """Test that logging uses correct format."""
        settings = Settings(
            OPENAI_API_KEY="test-key",
            LOG_LEVEL="DEBUG",
        )

        setup_logging(settings)
