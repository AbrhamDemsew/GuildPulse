"""Tests for infrastructure config adapter."""

import os
from unittest.mock import patch

from src.infrastructure.config.adapter import ConfigAdapter


class TestConfigAdapter:
    """Test ConfigAdapter implementation."""

    def test_discord_token(self):
        """Test discord_token returns correct value."""
        with patch.dict(os.environ, {"DISCORD_TOKEN": "test_discord_token"}):
            adapter = ConfigAdapter()
            assert adapter.discord_token == "test_discord_token"

    def test_openai_api_key(self):
        """Test openai_api_key returns correct value."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test-key"}):
            adapter = ConfigAdapter()
            assert adapter.openai_api_key == "sk-test-key"

    def test_openai_base_url_default(self):
        """Test openai_base_url has default value."""
        # Test that the adapter has the correct default value
        assert ConfigAdapter.model_fields["OPENAI_BASE_URL"].default == "https://api.openai.com/v1"

    def test_openai_model_default(self):
        """Test openai_model has default value."""
        # Test that the adapter has the correct default value
        assert ConfigAdapter.model_fields["OPENAI_MODEL"].default == "gpt-4o-mini"
