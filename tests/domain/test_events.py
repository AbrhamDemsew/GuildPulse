"""Tests for domain events."""

from datetime import datetime

from src.domain.channel.events import ConversationCleared, MessageAdded
from src.domain.channel.aggregate import Channel
from src.domain.channel.value_objects import Message, MessageContent


def test_message_added_event_creation():
    """Test MessageAdded event creation."""
    channel = Channel(channel_id=123, max_messages=100)
    event = MessageAdded.from_channel(channel, "user", "Hello")
    
    assert event.channel_id == 123
    assert event.message_role == "user"
    assert event.message_content == "Hello"
    assert isinstance(event.timestamp, datetime)


def test_conversation_cleared_event_creation():
    """Test ConversationCleared event creation."""
    channel = Channel(channel_id=456, max_messages=100)
    # Add some messages first
    channel.add_message(Message(role="user", content=MessageContent(value="test")))
    
    event = ConversationCleared.from_channel(channel, 1)
    
    assert event.channel_id == 456
    assert event.previous_message_count == 1
    assert isinstance(event.timestamp, datetime)