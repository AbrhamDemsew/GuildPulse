"""Comprehensive tests for the new Clean Architecture."""

from typing import Any

from unittest.mock import Mock

import pytest

from src.application.messaging.handlers import ProcessUserTurn
from src.domain.channel.aggregate import Channel
from src.domain.channel.value_objects import Message, MessageContent
from src.domain.shared.errors import MessageValidationError
from src.infrastructure.ai.openai.adapter import OpenAIServiceAdapter
from src.infrastructure.persistence.memory.repository import InMemoryChannelRepository


@pytest.fixture
def mock_ai_service() -> Any:
    """Create a mock AI service."""
    mock = Mock(spec=OpenAIServiceAdapter)
    mock.generate_reply.return_value = "Test response"
    mock.generate_reply.return_value = "Test response"
    return mock


@pytest.fixture
def test_channel():
    """Create a test channel."""
    channel = Channel(channel_id=123)
    return channel


def test_channel_creation():
    """Test channel creation."""
    channel = Channel(channel_id=123)
    assert channel.id == 123
    assert channel.count_messages() == 0


def test_process_user_turn(mock_ai_service: Any) -> Any:
    """Test ProcessUserTurn use case."""
    repo = InMemoryChannelRepository()
    processor = ProcessUserTurn(repo, mock_ai_service)
    result = processor.execute(channel_id=123, user_content="Hello")
    assert result == "Test response"


def test_process_user_turn_channel_exists(mock_ai_service: Any) -> Any:
    """Test ProcessUserTurn with existing channel."""
    repo = InMemoryChannelRepository()
    processor = ProcessUserTurn(repo, mock_ai_service)
    channel = repo.get_or_create(456)
    channel.add_message(Message(role="user", content=MessageContent(value="Existing")))
    result = processor.execute(channel_id=456, user_content="Hello")
    assert result == "Test response"


def test_channel_add_message():
    """Test adding messages to a channel."""
    channel = Channel(channel_id=123)
    message = Message(role="user", content=MessageContent(value="Hello"))
    channel.add_message(message)
    assert channel.count_messages() == 1


def test_channel_max_messages():
    """Test channel message limit."""
    channel = Channel(channel_id=123, max_messages=3)
    for i in range(5):
        message = Message(role="user", content=MessageContent(value=f"Message {i}"))
        channel.add_message(message)
    assert channel.count_messages() == 3


def test_channel_get_messages():
    """Test getting messages from channel."""
    channel = Channel(channel_id=123)
    msg1 = Message(role="user", content=MessageContent(value="First"))
    msg2 = Message(role="assistant", content=MessageContent(value="Second"))
    channel.add_message(msg1)
    channel.add_message(msg2)
    messages = channel.get_messages()
    assert len(messages) == 2


def test_channel_clear():
    """Test clearing channel messages."""
    channel = Channel(channel_id=123)
    channel.add_message(Message(role="user", content=MessageContent(value="Test")))
    channel.clear()
    assert channel.count_messages() == 0


def test_message_creation():
    """Test message creation."""
    content = MessageContent(value="Hello")
    message = Message(role="user", content=content)
    assert message.role == "user"
    assert message.content.value == "Hello"


def test_message_to_dict():
    """Test converting message to dict."""
    content = MessageContent(value="Hello")
    message = Message(role="user", content=content)
    msg_dict = message.to_dict()
    assert msg_dict == {"role": "user", "content": "Hello"}


def test_message_validation():
    """Test message role validation."""
    content = MessageContent(value="Hello")

    with pytest.raises(MessageValidationError):
        Message(role="invalid", content=content)


def test_message_content_validation():
    """Test message content validation."""
    from src.domain.shared.errors import MessageValidationError

    with pytest.raises(MessageValidationError):
        MessageContent(value="")


def test_in_memory_repository():
    """Test in-memory repository."""
    repo = InMemoryChannelRepository()
    channel = Channel(channel_id=123)
    repo.save(channel)
    retrieved = repo.get(123)
    assert retrieved.id == 123


def test_in_memory_repository_not_found():
    """Test repository error handling."""
    from src.domain.shared.errors import ChannelNotFoundError

    repo = InMemoryChannelRepository()
    with pytest.raises(ChannelNotFoundError):
        repo.get(999)


class TestOpenAIIntegration:
    """Tests for OpenAI integration scenarios."""

    def test_full_openai_flow(self):
        """Test complete OpenAI client flow."""
        from src.infrastructure.ai.openai.client import OpenAIClient

        client = OpenAIClient(
            api_key="test-key",
            base_url="https://test.com/v1",
            model="test-model",
            max_tokens=100,
            temperature=0.5,
        )

        assert client.client is not None


class TestRepositoryEdgeCases:
    """Tests for repository edge cases."""

    def test_repository_get_or_create_with_messages(self):
        """Test get_or_create preserves messages."""
        repo = InMemoryChannelRepository()
        channel = Channel(channel_id=123)
        channel.add_message(Message(role="user", content=MessageContent(value="Existing")))
        repo.save(channel)

        retrieved = repo.get_or_create(123)
        assert retrieved.count_messages() == 1

    def test_repository_multiple_channels(self):
        """Test handling multiple channels."""
        repo = InMemoryChannelRepository()

        for i in range(5):
            channel = Channel(channel_id=i)
            channel.add_message(Message(role="user", content=MessageContent(value=f"Msg {i}")))
            repo.save(channel)

        for i in range(5):
            retrieved = repo.get(i)
            assert retrieved.id == i
            assert retrieved.count_messages() == 1


class TestMessageProcessingEdgeCases:
    """Tests for edge cases in message processing."""

    def test_process_user_turn_with_empty_content(self, mock_ai_service: Any) -> Any:
        """Test processing empty user content."""
        repo = InMemoryChannelRepository()
        processor = ProcessUserTurn(repo, mock_ai_service)
        result = processor.execute(channel_id=123, user_content="")
        assert result == "Test response"

    def test_process_user_turn_with_long_content(self, mock_ai_service: Any) -> Any:
        """Test processing long user content."""
        repo = InMemoryChannelRepository()
        processor = ProcessUserTurn(repo, mock_ai_service)
        long_content = "x" * 1000
        result = processor.execute(channel_id=123, user_content=long_content)
        assert result == "Test response"
