"""Tests for the new Clean Architecture."""

import pytest

from src.domain.channel.aggregate import Channel
from src.domain.channel.value_objects import Message, MessageContent
from src.infrastructure.persistence.memory.repository import InMemoryMessageRepository


@pytest.fixture
def test_channel():
    """Create a test channel."""
    channel = Channel(channel_id=123)
    return channel


def test_channel_creation():
    """Test channel creation."""
    channel = Channel(channel_id=123)
    assert channel.channel_id == 123
    assert channel.count_messages() == 0


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
    from src.domain.shared.errors import MessageValidationError

    with pytest.raises(MessageValidationError):
        Message(role="invalid", content=content)


def test_message_content_validation():
    """Test message content validation."""
    from src.domain.shared.errors import MessageValidationError

    with pytest.raises(MessageValidationError):
        MessageContent(value="")


def test_in_memory_repository():
    """Test in-memory repository."""
    repo = InMemoryMessageRepository()
    channel = Channel(channel_id=123)
    repo.save(channel)
    retrieved = repo.get(123)
    assert retrieved.channel_id == 123


def test_in_memory_repository_not_found():
    """Test repository error handling."""
    from src.domain.shared.errors import ChannelNotFoundError

    repo = InMemoryMessageRepository()
    with pytest.raises(ChannelNotFoundError):
        repo.get(999)


def test_channel_id():
    """Test ChannelId value object."""
    from src.domain.channel.value_objects import ChannelId

    channel_id = ChannelId(value=123)
    assert int(channel_id) == 123


def test_channel_id_validation():
    """Test ChannelId validation."""
    from src.domain.channel.value_objects import ChannelId
    from src.domain.shared.errors import MessageValidationError

    with pytest.raises(MessageValidationError):
        ChannelId(value=-1)
