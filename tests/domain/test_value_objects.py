"""Tests for domain value objects (Message, MessageContent)."""

import pytest

from src.domain.channel.value_objects import Message, MessageContent
from src.domain.shared.errors import MessageValidationError


class TestMessageContent:
    """Tests for MessageContent value object."""

    def test_valid_content_creation(self):
        """Test creating valid message content."""
        content = MessageContent(value="Hello, World!")
        assert content.value == "Hello, World!"

    def test_empty_content_raises_error(self):
        """Test that empty content raises MessageValidationError."""
        with pytest.raises(MessageValidationError) as exc_info:
            MessageContent(value="")
        assert "cannot be empty" in str(exc_info.value)

    @pytest.mark.parametrize("length", [1, 5000, 10000])
    def test_content_at_valid_lengths(self, length):
        """Test content creation with valid lengths."""
        content = MessageContent(value="x" * length)
        assert len(content.value) == length

    @pytest.mark.parametrize("length", [10001, 20000])
    def test_content_too_long_raises_error(self, length):
        """Test that content exceeding 10000 characters raises error."""
        with pytest.raises(MessageValidationError) as exc_info:
            MessageContent(value="x" * length)
        assert "too long" in str(exc_info.value)

    def test_content_string_representation(self):
        """Test string representation of content."""
        content = MessageContent(value="Test content")
        assert str(content) == "Test content"


class TestMessage:
    """Tests for Message value object."""

    def test_valid_message_creation(self):
        """Test creating valid message."""
        content = MessageContent(value="Hello")
        message = Message(role="user", content=content)
        assert message.role == "user"
        assert message.content.value == "Hello"
        assert message.timestamp is not None

    @pytest.mark.parametrize("role", ["system", "user", "assistant"])
    def test_valid_message_roles(self, role):
        """Test all valid message roles."""
        content = MessageContent(value="test")
        message = Message(role=role, content=content)
        assert message.role == role

    @pytest.mark.parametrize("role", ["admin", "moderator", "invalid", ""])
    def test_invalid_message_roles(self, role):
        """Test that invalid roles raise MessageValidationError."""
        content = MessageContent(value="test")
        with pytest.raises(MessageValidationError) as exc_info:
            Message(role=role, content=content)
        assert "Invalid role" in str(exc_info.value)

    def test_message_to_dict(self):
        """Test converting message to dictionary."""
        content = MessageContent(value="Hello")
        message = Message(role="user", content=content)
        msg_dict = message.to_dict()
        assert msg_dict == {"role": "user", "content": "Hello"}

    def test_message_equality(self):
        """Test message equality comparison."""
        content1 = MessageContent(value="Same")
        content2 = MessageContent(value="Same")
        msg1 = Message(role="user", content=content1)
        msg2 = Message(role="user", content=content2)
        assert msg1 == msg2

    def test_message_inequality(self):
        """Test message inequality comparison."""
        content1 = MessageContent(value="Different")
        content2 = MessageContent(value="Same")
        msg1 = Message(role="user", content=content1)
        msg2 = Message(role="user", content=content2)
        assert msg1 != msg2

    def test_message_inequality_different_roles(self):
        """Test messages with different roles are not equal."""
        content = MessageContent(value="Same")
        msg1 = Message(role="user", content=content)
        msg2 = Message(role="assistant", content=content)
        assert msg1 != msg2

    def test_message_not_equal_to_other_type(self):
        """Test message not equal to non-message objects."""
        content = MessageContent(value="test")
        message = Message(role="user", content=content)
        assert message != "not a message"
        assert message != 42
        assert message is not None

    def test_message_timestamp_generation(self):
        """Test that timestamp is auto-generated."""
        content = MessageContent(value="test")
        message = Message(role="user", content=content)
        assert message.timestamp is not None
        assert isinstance(message.timestamp, type(message.timestamp))

    def test_message_frozen(self):
        """Test that message is immutable (frozen dataclass)."""
        content = MessageContent(value="test")
        message = Message(role="user", content=content)
        with pytest.raises(AttributeError):
            message.role = "assistant"


class TestValueObjectEdgeCases:
    """Tests for edge cases in value objects."""

    def test_message_content_with_special_characters(self):
        """Test content with special characters."""
        content = MessageContent(value="Hello\nWorld\tTabbed!")
        assert content.value == "Hello\nWorld\tTabbed!"

    def test_message_content_unicode(self):
        """Test content with Unicode characters."""
        content = MessageContent(value="Hello, 世界! 🎉")
        assert "世界" in content.value
        assert "🎉" in content.value

    def test_message_with_long_content(self):
        """Test message with content at max length."""
        long_text = "x" * 10000
        content = MessageContent(value=long_text)
        assert len(content.value) == 10000

    def test_message_content_whitespace_only(self):
        """Test that whitespace-only content is valid."""
        content = MessageContent(value="   ")
        assert content.value == "   "
