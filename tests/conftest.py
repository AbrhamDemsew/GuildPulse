"""Test configuration and fixtures."""

import os
from unittest import mock

import pytest


@pytest.fixture(autouse=True, scope="session")
def test_environment():
    """Set up clean test environment variables."""
    env_vars = {
        "DISCORD_TOKEN": "test-token",
        "OPENAI_API_KEY": "test-key",
        "OPENAI_BASE_URL": "https://test.com/v1",
        "OPENAI_MODEL": "test-model",
        "OPENAI_MAX_TOKENS": "100",
        "OPENAI_TEMPERATURE": "0.5",
        "LOG_LEVEL": "DEBUG",
        "DEBUG": "false",
        "CHAT_SYSTEM_PROMPT": "Test prompt",
    }

    with mock.patch.dict(os.environ, env_vars, clear=True):
        yield


@pytest.fixture
def mock_openai_client():
    """Create a mock OpenAI client."""
    from src.infrastructure.ai.openai.client import OpenAIClient

    return mock.Mock(spec=OpenAIClient)


@pytest.fixture
def mock_channel():
    """Create a mock channel."""

    from src.domain.channel.aggregate import Channel
    from src.domain.channel.value_objects import Message, MessageContent

    channel = Channel(channel_id=123)
    channel.add_message(Message(role="user", content=MessageContent(value="Hello")))
    return channel


@pytest.fixture
def mock_ai_adapter():
    """Create a mock AI service adapter."""
    adapter = mock.Mock()
    adapter.generate_reply.return_value = "Test response"
    return adapter


@pytest.fixture
def process_user_turn(mock_ai_adapter):
    """Create a ProcessUserTurn instance."""
    from src.application.messaging.handlers import ProcessUserTurn
    from src.infrastructure.persistence.memory.repository import (
        InMemoryMessageRepository,
    )

    repo = InMemoryMessageRepository()
    return ProcessUserTurn(repo, mock_ai_adapter)
