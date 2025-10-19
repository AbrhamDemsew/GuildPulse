"""Tests for domain value objects."""
import pytest
from src.domain.channel.value_objects import Message, MessageContent, MessageRole, MessageValidationError


class TestMessageRole:
    def test_valid_roles(self):
        """Test valid message roles."""
        assert MessageRole.USER.value == "user"
        assert MessageRole.ASSISTANT.value == "assistant"
        assert MessageRole.SYSTEM.value == "system"


@pytest.mark.parametrize("role,expected", [
    ("user", True),
    ("assistant", True),
    ("system", True),
    ("invalid", False),
    ("", False),
    ("123", False),
    ("user ", False),
    (" user", False),
])
def test_message_role_validation(role, expected):
    """Test message role validation with parameterized test."""
    if expected:
        msg = Message(role=role, content=MessageContent(value="test"))
        assert msg.role == role
    else:
        with pytest.raises(MessageValidationError):
            Message(role=role, content=MessageContent(value="test"))


class TestMessageContent:
    def test_valid_content(self):
        """Test valid message content."""
        content = MessageContent(value="Hello")
        assert str(content) == "Hello"

    def test_empty_string_content_raises_error(self):
        """Test that empty string content raises error."""
        with pytest.raises(MessageValidationError):
            MessageContent(value="")

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


@pytest.mark.parametrize("content,expected", [
    ("Hello", True),
    ("Hello World", True),
    ("A" * 256, True),
    ("Hello\nWorld", True),
    ("Hello\tWorld", True),
    ("", False),
    (None, False),
])
def test_message_content_validation(content, expected):
    """Test MessageContent validation with parameterized test."""
    if expected:
        content_obj = MessageContent(value=content)
        assert content_obj.value == content
    else:
        with pytest.raises((MessageValidationError, TypeError)):
            MessageContent(value=content)


@pytest.mark.parametrize("length,expected", [
    (1, True),
    (50, True),
    (100, True),
    (255, True),
    (256, True),
    (500, True),
    (1000, True),
    (10000, True),
    (10001, False),
])
def test_message_content_length_validation(length, expected):
    """Test MessageContent length validation with parameterized test."""
    content = "A" * length
    if expected:
        content_obj = MessageContent(value=content)
        assert len(content_obj.value) == length
    else:
        with pytest.raises(MessageValidationError):
            MessageContent(value=content)


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

        assert msg1 == msg2

    def test_message_inequality(self):
        """Test message inequality."""
        msg1 = Message(role="user", content=MessageContent(value="Hello"))
        msg2 = Message(role="user", content=MessageContent(value="World"))

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


@pytest.mark.parametrize("role", ["user", "assistant", "system"])
def test_message_with_valid_roles(role):
    """Test messages with valid roles using parameterized test."""
    msg = Message(role=role, content=MessageContent(value="test"))
    assert msg.role == role


@pytest.mark.parametrize("role", ["admin", "bot", "human", "1", "2", "a", "b"])
def test_message_with_invalid_roles(role):
    """Test messages with invalid roles using parameterized test."""
    with pytest.raises(MessageValidationError):
        Message(role=role, content=MessageContent(value="test"))


@pytest.mark.parametrize("content", [
    "Hello",
    "Hello World",
    "A" * 256,
    "Hello\nWorld",
    "Hello\tWorld",
])
def test_message_content_valid_cases(content):
    """Test various valid content values using parameterized test."""
    content_obj = MessageContent(value=content)
    assert content_obj.value == content


@pytest.mark.parametrize("length", [1, 50, 100, 255, 256, 500, 1000])
def test_message_content_various_lengths(length):
    """Test content with various lengths using parameterized test."""
    content_obj = MessageContent(value="A" * length)
    assert len(content_obj.value) == length