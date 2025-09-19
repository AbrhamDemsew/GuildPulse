"""Test configuration and fixtures."""

from typing import Any

from unittest import mock

import pytest


@pytest.fixture(scope="session")
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

    with mock.patch.dict("os.environ", env_vars, clear=True):
        yield


@pytest.fixture
def mock_openai_client():
    """Create a mock OpenAI client with spec for better type checking."""
    from src.infrastructure.ai.openai.client import OpenAIClient

    mock_client = mock.Mock(spec=OpenAIClient)
    return mock_client


@pytest.fixture
def mock_channel():
    """Create a mock channel with one user message."""
    from src.domain.channel.aggregate import Channel
    from src.domain.channel.value_objects import Message, MessageContent

    channel = Channel(channel_id=123)
    channel.add_message(Message(role="user", content=MessageContent(value="Hello")))
    return channel


@pytest.fixture
def mock_ai_adapter() -> mock.Mock:
    """Create a mock AI service adapter."""
    adapter = mock.Mock()
    adapter.generate_reply.return_value = "Test response"
    return adapter


@pytest.fixture
def process_user_turn(mock_ai_adapter: mock.Mock) -> Any:
    """Create a ProcessUserTurn instance."""
    from src.application.messaging.handlers import ProcessUserTurn
    from src.infrastructure.persistence.memory.repository import (
        InMemoryMessageRepository,
    )

    repo = InMemoryMessageRepository()
    return ProcessUserTurn(repo, mock_ai_adapter)


@pytest.fixture
def clear_channel_history() -> Any:
    """Create a ClearChannelHistory instance."""
    from src.application.messaging.handlers import ClearChannelHistory
    from src.infrastructure.persistence.memory.repository import (
        InMemoryMessageRepository,
    )

    repo = InMemoryMessageRepository()
    return ClearChannelHistory(repo)


@pytest.fixture
def sample_channel() -> Any:
    """Create a sample channel with messages."""
    from src.domain.channel.aggregate import Channel
    from src.domain.channel.value_objects import Message, MessageContent

    channel = Channel(channel_id=999, max_messages=3)
    channel.add_message(Message(role="user", content=MessageContent(value="First")))
    channel.add_message(Message(role="assistant", content=MessageContent(value="Second")))
    return channel
