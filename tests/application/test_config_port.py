"""Tests for application config port."""

from unittest.mock import Mock

import pytest


class TestConfigPort:
    """Test the config port contract."""

    def test_config_port_has_discord_token(self):
        """Port must provide discord_token property."""
        mock_config = Mock()
        mock_config.discord_token = "test_token"
        
        assert mock_config.discord_token == "test_token"

    def test_config_port_has_openai_api_key(self):
        """Port must provide openai_api_key property."""
        mock_config = Mock()
        mock_config.openai_api_key = "sk-test"
        
        assert mock_config.openai_api_key == "sk-test"

    def test_config_port_has_openai_base_url(self):
        """Port must provide openai_base_url property."""
        mock_config = Mock()
        mock_config.openai_base_url = "https://api.example.com/v1"
        
        assert mock_config.openai_base_url == "https://api.example.com/v1"

    def test_config_port_has_openai_model(self):
        """Port must provide openai_model property."""
        mock_config = Mock()
        mock_config.openai_model = "gpt-4"
        
        assert mock_config.openai_model == "gpt-4"