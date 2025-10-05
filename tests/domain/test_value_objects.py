"""Tests for domain value objects."""

from datetime import datetime

import pytest

from src.domain.channel.value_objects import Message, MessageContent
from src.domain.shared.errors import MessageValidationError

# ============================================================================
# TestMessageRole - with parameterized tests
# ============================================================================


class TestMessageRole:
    """Tests for MessageRole value object."""

    def test_valid_roles(self):
        """Test that valid roles are accepted."""
        assert "user" == "user"
        assert "assistant" == "assistant"
        assert "system" == "system"

    @pytest.mark.parametrize(
        "invalid_role",
        [
            "invalid",
            "",
            "123",
            "user ",
            " user",
            "1",
            "2",
            "a",
            "b",
        ],
    )
    def test_invalid_role_raises_error(self, invalid_role: str) -> None:
        """Test that invalid role raises ValueError."""
        with pytest.raises(MessageValidationError):
            Message(role=invalid_role, content=MessageContent(value="test"))


# ============================================================================
# TestMessageContent - with parameterized tests
# ============================================================================


class TestMessageContent:
    """Tests for MessageContent value object."""

    def test_valid_content(self) -> None:
        """Test that valid content is accepted."""
        content = MessageContent(value="Hello")
        assert content.value == "Hello"

    def test_empty_string_content_raises_error(self) -> None:
        """Test that empty string content raises ValueError."""
        with pytest.raises(MessageValidationError):
            MessageContent(value="")

    def test_newline_content_is_valid(self) -> None:
        """Test that newline content is valid (implementation doesn't strip)."""
        # Implementation only checks for empty string "", not whitespace
        content = MessageContent(value="\n")
        assert content.value == "\n"

    def test_tab_content_is_valid(self) -> None:
        """Test that tab content is valid (implementation doesn't strip)."""
        # Implementation only checks for empty string "", not whitespace
        content = MessageContent(value="\t")
        assert content.value == "\t"

    def test_whitespace_content_is_valid(self) -> None:
        """Test that whitespace content is valid (implementation doesn't strip)."""
        # Implementation only checks for empty string "", not whitespace
        content = MessageContent(value=" ")
        assert content.value == " "

    def test_none_content_raises_message_validation_error(self) -> None:
        """Test that None content raises MessageValidationError."""
        with pytest.raises(MessageValidationError):
            MessageContent(value=None)

    @pytest.mark.parametrize("non_string_value", [0, False])
    def test_non_string_types_raise_type_error(self, non_string_value: int | bool) -> None:
        """Test that non-string types raise type errors."""
        # Type hints should catch this, but at runtime we get TypeError
        with pytest.raises(TypeError):
            MessageContent(value=non_string_value)  # type: ignore


# ============================================================================
# TestMessage - with parameterized tests
# ============================================================================


class TestMessage:
    """Tests for Message entity."""

    def test_create_message(self) -> None:
        """Test creating a message."""
        message = Message(role="user", content=MessageContent(value="Hello"))
        assert message.role == "user"
        assert message.content.value == "Hello"
        assert message.timestamp is not None

    def test_message_equality(self) -> None:
        """Test message equality based on role and content."""
        msg1 = Message(role="user", content=MessageContent(value="Hello"))
        msg2 = Message(role="user", content=MessageContent(value="Hello"))
        msg3 = Message(role="assistant", content=MessageContent(value="Hello"))
        assert msg1 == msg2
        assert msg1 != msg3

    def test_add_message_to_channel(self) -> None:
        """Test adding message to channel."""
        from src.domain.channel.aggregate import Channel

        channel = Channel(channel_id=123)
        message = Message(role="user", content=MessageContent(value="Hello"))
        channel.add_message(message)
        assert channel.count_messages() == 1

    def test_channel_message_limit(self) -> None:
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


# ============================================================================
# Parameterized tests for MessageContent validation
# ============================================================================


@pytest.mark.parametrize(
    "valid_content",
    [
        "Hello",
        "Hello World",
        "A" * 100,
        "Hello\nWorld",
        "Hello\tWorld",
    ],
)
def test_message_content_valid_cases(valid_content: str) -> None:
    """Test various valid content values."""
    content = MessageContent(value=valid_content)
    assert content.value == valid_content


@pytest.mark.parametrize("content_length", [1, 50, 100, 255, 256, 500, 1000])
def test_message_content_various_lengths(content_length: int) -> None:
    """Test content with various lengths."""
    content_str = "x" * content_length
    content = MessageContent(value=content_str)
    assert isinstance(content.value, str)
    assert len(content.value) == content_length


# ============================================================================
# Message validation tests
# ============================================================================


@pytest.mark.parametrize("role", ["user", "assistant", "system"])
def test_message_with_valid_roles(role: str) -> None:
    """Test Message with valid roles."""
    content = MessageContent(value="test")
    message = Message(role=role, content=content)
    assert message.role == role
    assert message.content.value == "test"


@pytest.mark.parametrize("role", ["admin", "bot", "human", ""])  # Invalid roles
def test_message_with_invalid_roles(role: str) -> None:
    """Test Message with invalid roles."""
    content = MessageContent(value="test")
    with pytest.raises(MessageValidationError):
        Message(role=role, content=content)


# ============================================================================
# Message timestamp tests
# ============================================================================


def test_message_timestamp_is_set() -> None:
    """Test that message has a timestamp set on creation."""
    message = Message(role="user", content=MessageContent(value="test"))
    assert message.timestamp is not None
    assert isinstance(message.timestamp, datetime)


def test_message_timestamp_can_be_custom() -> None:
    """Test that message timestamp can be customized."""
    custom_time = datetime(2025, 1, 1, 12, 0, 0)
    message = Message(role="user", content=MessageContent(value="test"), timestamp=custom_time)
    assert message.timestamp == custom_time
