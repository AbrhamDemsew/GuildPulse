"""Tests for Channel aggregate."""

from src.domain.channel.aggregate import Channel
from src.domain.channel.value_objects import Message, MessageContent
from src.domain.channel.events import ConversationCleared, MessageAdded


def test_channel_collects_domain_events():
    """Test that Channel collects domain events."""
    channel = Channel(channel_id=789, max_messages=100)

    # Add a message - should generate event
    channel.add_message(Message(role="user", content=MessageContent(value="Hello")))

    assert len(channel.domain_events) == 1
    assert isinstance(channel.domain_events[0], MessageAdded)
    assert channel.domain_events[0].channel_id == 789

    # Clear - should generate event
    channel.clear()

    assert len(channel.domain_events) == 2
    assert isinstance(channel.domain_events[1], ConversationCleared)

    # Clear events after publishing
    channel.clear_events()
    assert len(channel.domain_events) == 0
