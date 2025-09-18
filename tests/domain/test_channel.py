"""Tests for Channel aggregate."""

from src.domain.channel.aggregate import Channel
from src.domain.channel.value_objects import Message, MessageContent


class TestChannel:
    """Tests for Channel aggregate."""

    def test_channel_creation(self):
        """Test basic channel creation."""
        channel = Channel(channel_id=123)
        assert channel.channel_id == 123
        assert len(channel.messages) == 0
        assert channel.count_messages() == 0

    def test_channel_creation_with_max_messages(self):
        """Test channel creation with custom max_messages."""
        channel = Channel(channel_id=456, max_messages=5)
        assert channel.max_messages == 5

    def test_add_message(self):
        """Test adding a message to channel."""
        channel = Channel(channel_id=123)
        message = Message(role="user", content=MessageContent(value="Hello"))
        channel.add_message(message)
        assert channel.count_messages() == 1
        assert len(channel.messages) == 1

    def test_add_multiple_messages(self):
        """Test adding multiple messages to channel."""
        channel = Channel(channel_id=123)
        channel.add_message(Message(role="user", content=MessageContent(value="1")))
        channel.add_message(Message(role="assistant", content=MessageContent(value="2")))
        channel.add_message(Message(role="user", content=MessageContent(value="3")))
        assert channel.count_messages() == 3

    def test_add_messages_exceeding_limit(self):
        """Test that channel respects max_messages limit."""
        channel = Channel(channel_id=123, max_messages=3)
        channel.add_message(Message(role="user", content=MessageContent(value="1")))
        channel.add_message(Message(role="assistant", content=MessageContent(value="2")))
        channel.add_message(Message(role="user", content=MessageContent(value="3")))
        channel.add_message(Message(role="assistant", content=MessageContent(value="4")))
        channel.add_message(Message(role="user", content=MessageContent(value="5")))

        assert channel.count_messages() == 3
        messages = channel.get_messages()
        assert messages[0].content.value == "3"
        assert messages[1].content.value == "4"
        assert messages[2].content.value == "5"

    def test_get_messages(self):
        """Test getting messages from channel."""
        channel = Channel(channel_id=123)
        msg1 = Message(role="user", content=MessageContent(value="First"))
        msg2 = Message(role="assistant", content=MessageContent(value="Second"))
        channel.add_message(msg1)
        channel.add_message(msg2)
        messages = channel.get_messages()
        assert len(messages) == 2
        assert messages[0] == msg1
        assert messages[1] == msg2

    def test_get_messages_returns_copy(self):
        """Test that get_messages returns a copy, not the original list."""
        channel = Channel(channel_id=123)
        channel.add_message(Message(role="user", content=MessageContent(value="Test")))
        messages = channel.get_messages()
        messages.append(Message(role="user", content=MessageContent(value="Extra")))
        assert channel.count_messages() == 1

    def test_get_messages_for_api(self):
        """Test getting messages as dictionaries for API."""
        channel = Channel(channel_id=123)
        channel.add_message(Message(role="user", content=MessageContent(value="First")))
        channel.add_message(Message(role="assistant", content=MessageContent(value="Second")))
        api_messages = channel.get_messages_for_api()
        assert len(api_messages) == 2
        assert api_messages[0] == {"role": "user", "content": "First"}
        assert api_messages[1] == {"role": "assistant", "content": "Second"}

    def test_clear(self):
        """Test clearing all messages from channel."""
        channel = Channel(channel_id=123)
        channel.add_message(Message(role="user", content=MessageContent(value="1")))
        channel.add_message(Message(role="assistant", content=MessageContent(value="2")))
        channel.clear()
        assert channel.count_messages() == 0
        assert len(channel.messages) == 0

    def test_channel_is_dataclass(self):
        """Test that Channel is a dataclass."""
        import dataclasses

        assert dataclasses.is_dataclass(Channel)


class TestChannelEdgeCases:
    """Tests for edge cases in Channel."""

    def test_channel_with_zero_max_messages(self):
        """Test channel with max_messages=0."""
        channel = Channel(channel_id=123, max_messages=0)
        channel.add_message(Message(role="user", content=MessageContent(value="Test")))
        assert channel.count_messages() == 0
        assert len(channel.messages) == 0

    def test_channel_add_empty_list(self):
        """Test that channel can have an empty messages list initially."""
        channel = Channel(channel_id=123)
        assert channel.messages == []

    def test_channel_with_large_max_messages(self):
        """Test channel with very large max_messages."""
        channel = Channel(channel_id=123, max_messages=10000)
        assert channel.max_messages == 10000
