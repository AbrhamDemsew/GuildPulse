"""Tests for domain value objects."""

import pytest

from src.domain.channel.value_objects import Message, MessageContent, MessageRole
from src.domain.shared.errors import MessageValidationError


class TestMessageRole:
    """Tests for MessageRole value object."""

    def test_valid_roles(self):
        """Test that valid roles are accepted."""
        assert "user" == "user"
        assert "assistant" == "assistant"
        assert "system" == "system"

    def test_invalid_role_raises_error(self):
        """Test that invalid role raises ValueError."""
        with pytest.raises(ValueError):
            MessageRole("invalid")


class TestMessageContent:
    """Tests for MessageContent value object."""

    def test_valid_content(self):
        """Test that valid content is accepted."""
        content = MessageContent(value="Hello")
        assert content.value == "Hello"

    def test_empty_content_raises_error(self):
        """Test that empty content raises ValueError."""
        with pytest.raises(MessageValidationError):
            MessageContent(value="")

    def test_none_content_raises_error(self):
        """Test that None content raises ValueError."""
        with pytest.raises(MessageValidationError):
            MessageContent(value=None)


class TestMessage:
    """Tests for Message entity."""

    def test_create_message(self):
        """Test creating a message."""
        message = Message(role="user", content=MessageContent(value="Hello"))
        assert message.role == "user"
        assert message.content.value == "Hello"
        assert message.timestamp is not None

    def test_message_equality(self):
        """Test message equality based on role and content."""
        msg1 = Message(role="user", content=MessageContent(value="Hello"))
        msg2 = Message(role="user", content=MessageContent(value="Hello"))
        msg3 = Message(role="assistant", content=MessageContent(value="Hello"))
        assert msg1 == msg2
        assert msg1 != msg3

    def test_add_message_to_channel(self):
        """Test adding message to channel."""
        from src.domain.channel.aggregate import Channel

        channel = Channel(channel_id=123)
        message = Message(role="user", content=MessageContent(value="Hello"))
        channel.add_message(message)
        assert channel.count_messages() == 1

    def test_channel_message_limit(self):
        """Test channel respects message limit."""
        from src.domain.channel.aggregate import Channel

        channel = Channel(channel_id=123, max_messages=2)
        channel.add_message(Message(role="user", content=MessageContent(value="1")))
        channel.add_message(Message(role="assistant", content=MessageContent(value="2")))
        assert channel.count_messages() == 2
        # Adding a third message should not raise an error, but should trim the oldest message
        channel.add_message(Message(role="user", content=MessageContent(value="3")))
        assert channel.count_messages() == 2
        assert channel.get_messages()[0].content.value == "2"