"""Tests for domain value objects."""
import pytest
from src.domain.channel.value_objects import Message, MessageContent, MessageRole, MessageValidationError


class TestMessageRole:
    def test_valid_roles(self):
        """Test valid message roles."""
        assert MessageRole.USER.value == "user"
        assert MessageRole.ASSISTANT.value == "assistant"
        assert MessageRole.SYSTEM.value == "system"

    def test_invalid_role_raises_error(self):
        """Test that invalid role raises validation error."""
        with pytest.raises(MessageValidationError):
            Message(role="invalid", content=MessageContent(value="test"))

        with pytest.raises(MessageValidationError):
            Message(role="", content=MessageContent(value="test"))

        with pytest.raises(MessageValidationError):
            Message(role="123", content=MessageContent(value="test"))

        with pytest.raises(MessageValidationError):
            Message(role="user ", content=MessageContent(value="test"))

        with pytest.raises(MessageValidationError):
            Message(role=" user", content=MessageContent(value="test"))


class TestMessageContent:
    def test_valid_content(self):
        """Test valid message content."""
        content = MessageContent(value="Hello")
        assert str(content) == "Hello"

    def test_empty_string_content_raises_error(self):
        """Test that empty string content raises error."""
        with pytest.raises(MessageValidationError):
            MessageContent(value="")

    def test_newline_content_is_valid(self):
        """Test that newline content is valid."""
        content = MessageContent(value="\n")
        assert str(content) == "\n"

    def test_tab_content_is_valid(self):
        """Test that tab content is valid."""
        content = MessageContent(value="\t")
        assert str(content) == "\t"

    def test_whitespace_content_is_valid(self):
        """Test that whitespace content is valid."""
        content = MessageContent(value="   ")
        assert str(content) == "   "

    def test_none_content_raises_message_validation_error(self):
        """Test that None content raises error."""
        with pytest.raises(MessageValidationError):
            MessageContent(value=None)

    def test_non_string_types_raise_type_error(self):
        """Test that non-string types raise type error."""
        with pytest.raises(TypeError):
            MessageContent(value=0)

        with pytest.raises(TypeError):
            MessageContent(value=False)


class TestMessage:
    def test_create_message(self):
        """Test creating a message."""
        msg = Message(role="user", content=MessageContent(value="Hello"))

        assert msg.role == "user"
        assert msg.content.value == "Hello"

    def test_message_equality(self):
        """Test message equality."""
        msg1 = Message(role="user", content=MessageContent(value="Hello"))
        msg2 = Message(role="user", content=MessageContent(value="Hello"))

        # Same value, so equal
        assert msg1 == msg2

    def test_message_inequality(self):
        """Test message inequality."""
        msg1 = Message(role="user", content=MessageContent(value="Hello"))
        msg2 = Message(role="user", content=MessageContent(value="World"))

        # Different values, not equal
        assert msg1 != msg2

    def test_message_to_dict(self):
        """Test converting message to dict."""
        msg = Message(role="user", content=MessageContent(value="Hello"))
        assert msg.to_dict() == {"role": "user", "content": "Hello"}

    def test_message_timestamp_is_set(self):
        """Test that message timestamp is set."""
        msg = Message(role="user", content=MessageContent(value="Hello"))
        assert msg.timestamp is not None

    def test_message_timestamp_can_be_custom(self):
        """Test that message timestamp can be custom."""
        from datetime import datetime

        custom_time = datetime(2024, 1, 1)
        msg = Message(role="user", content=MessageContent(value="Hello"), timestamp=custom_time)
        assert msg.timestamp == custom_time


def test_message_content_valid_cases():
    """Test various valid content values."""
    valid_cases = [
        "Hello",
        "Hello World",
        "A" * 256,
        "Hello\nWorld",
        "Hello\tWorld",
    ]

    for case in valid_cases:
        content = MessageContent(value=case)
        assert content.value == case


def test_message_content_various_lengths():
    """Test content with various lengths."""
    lengths = [1, 50, 100, 255, 256, 500, 1000]
    for length in lengths:
        content = MessageContent(value="A" * length)
        assert len(content.value) == length


def test_message_with_valid_roles():
    """Test messages with valid roles."""
    for role in ["user", "assistant", "system"]:
        msg = Message(role=role, content=MessageContent(value="test"))
        assert msg.role == role


def test_message_with_invalid_roles():
    """Test messages with invalid roles."""
    for role in ["admin", "bot", "human", "", "1", "2", "a", "b"]:
        with pytest.raises(MessageValidationError):
            Message(role=role, content=MessageContent(value="test"))


def test_message_timestamp_is_set():
    """Test that message timestamp is set."""
    msg = Message(role="user", content=MessageContent(value="Hello"))
    assert msg.timestamp is not None


def test_message_timestamp_can_be_custom():
    """Test that message timestamp can be custom."""
    from datetime import datetime

    custom_time = datetime(2024, 1, 1)
    msg = Message(role="user", content=MessageContent(value="Hello"), timestamp=custom_time)
    assert msg.timestamp == custom_time