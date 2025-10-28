"""Test configuration and fixtures."""

from __future__ import annotations

from typing import Any, Generator

from unittest import mock

import pytest

from src.domain.channel.aggregate import Channel
from src.domain.channel.value_objects import Message, MessageContent

# ============================================================================
# Session-scoped fixtures (expensive setup)
# ============================================================================


@pytest.fixture(scope="session")
def test_environment():
    """Set up clean test environment variables.

    This fixture runs once per test session and sets up all environment variables.
    """
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


# ============================================================================
# Channel fixtures
# ============================================================================


@pytest.fixture
def channel_factory() -> Generator[Any, None, None]:
    """Factory fixture for creating channels with varying configurations.

    Usage:
        def test_with_custom_channel(channel_factory):
            channel = channel_factory(channel_id=123, max_messages=10)
            ...
    """

    def create_channel(channel_id: int = 123, max_messages: int = 100) -> Channel:
        return Channel(id=channel_id, max_messages=max_messages)

    yield create_channel
    # Cleanup if needed


@pytest.fixture
def sample_channel() -> Channel:
    """Create a sample channel with messages."""
    channel = Channel(id=999, max_messages=3)
    channel.add_message(Message(role="user", content=MessageContent(value="First")))
    channel.add_message(Message(role="assistant", content=MessageContent(value="Second")))
    return channel


@pytest.fixture
def empty_channel() -> Channel:
    """Create an empty channel."""
    return Channel(id=0, max_messages=100)


@pytest.fixture
def channel_with_many_messages() -> Channel:
    """Create a channel with many messages (100+)."""
    channel = Channel(id=888, max_messages=200)
    for i in range(150):
        channel.add_message(Message(role="user", content=MessageContent(value=f"Message {i}")))
    return channel


# ============================================================================
# AI adapter fixtures
# ============================================================================


@pytest.fixture
def mock_openai_client():
    """Create a mock OpenAI client with spec for better type checking."""
    from src.infrastructure.ai.openai.client import OpenAIClient

    mock_client = mock.Mock(spec=OpenAIClient)
    return mock_client


@pytest.fixture
def mock_ai_adapter(mock_openai_client: mock.Mock) -> mock.Mock:
    """Create a mock AI service adapter with response configured."""
    from src.infrastructure.ai.openai.adapter import OpenAIServiceAdapter

    adapter = mock.Mock(spec=OpenAIServiceAdapter)
    adapter.generate_reply.return_value = "Test response"
    return adapter


# ============================================================================
# Message fixtures
# ============================================================================


@pytest.fixture
def message_factory() -> Generator[Any, None, None]:
    """Factory fixture for creating messages with various configurations.

    Usage:
        def test_with_message(message_factory):
            msg = message_factory(role="user", content="Hello")
            ...
    """

    def create_message(role: str = "user", content: str = "Hello") -> Message:
        return Message(role=role, content=MessageContent(value=content))

    yield create_message
    # Cleanup if needed


@pytest.fixture
def user_message() -> Message:
    """Create a user message."""
    return Message(role="user", content=MessageContent(value="Hello"))


@pytest.fixture
def assistant_message() -> Message:
    """Create an assistant message."""
    return Message(role="assistant", content=MessageContent(value="Hi there"))


@pytest.fixture
def image_message() -> Message:
    """Create a message with image content."""
    from src.domain.channel.value_objects import MessageContent

    # Using Any for complex nested dict types that can't be precisely typed
    content: Any = [
        {"type": "text", "text": "What's in this image?"},
        {"type": "image_url", "image_url": {"url": "https://example.com/image.jpg"}},
    ]
    return Message(role="user", content=MessageContent(value=content))  # type: ignore


# ============================================================================
# ProcessUserTurn fixtures
# ============================================================================


@pytest.fixture
def process_user_turn(mock_ai_adapter: mock.Mock) -> Any:
    """Create a ProcessUserTurn instance."""
    from src.application.messaging.handlers import ProcessUserTurn
    from src.infrastructure.persistence.memory.repository import (
        InMemoryChannelRepository,
    )

    repo = InMemoryChannelRepository()
    return ProcessUserTurn(repo, mock_ai_adapter)


@pytest.fixture
def clear_channel_history() -> Any:
    """Create a ClearChannelHistory instance."""
    from src.application.messaging.handlers import ClearChannelHistory
    from src.infrastructure.persistence.memory.repository import (
        InMemoryChannelRepository,
    )

    repo = InMemoryChannelRepository()
    return ClearChannelHistory(repo)


# ============================================================================
# Async fixtures
# ============================================================================


@pytest.fixture
async def async_openai_client():
    """Create an async OpenAI client for async tests."""
    from src.infrastructure.ai.openai.client import OpenAIClient

    client = OpenAIClient(
        api_key="test-key",
        base_url="https://test.com/v1",
        model="test-model",
        max_tokens=100,
        temperature=0.5,
    )
    yield client


# ============================================================================
# Temporary files and directories
# ============================================================================


@pytest.fixture
def temp_file_content() -> Generator[str, None, None]:
    """Provide a temporary file path for file operations."""
    import tempfile

    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
        f.write("test content")
        temp_path = f.name

    yield temp_path

    # Cleanup
    import os

    os.unlink(temp_path)


@pytest.fixture
def temp_directory() -> Generator[Any, None, None]:
    """Provide a temporary directory for file operations."""
    import tempfile
    import shutil

    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)
