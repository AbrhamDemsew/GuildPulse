"""Tests for domain events."""
import pytest
from src.domain.channel.aggregate import Channel
from src.domain.channel.events import MessageAdded, ConversationCleared
from src.domain.channel.value_objects import Message, MessageContent
from src.domain.shared.domain_event import DomainEvent


def test_message_added_event_creation():
    """Test MessageAdded event creation."""
    channel = Channel(channel_id=999)
    channel.add_message(Message(role="user", content=MessageContent(value="Hello")))

    events = channel.domain_events
    assert len(events) == 1

    event = events[0]
    assert isinstance(event, MessageAdded)
    assert event.event_id is not None
    assert event.occurred_at is not None
    assert event.aggregate_id == "999"
    assert event.message_role == "user"
    assert event.message_content == "Hello"
    assert event.event_type == "channel.message.added"


def test_conversation_cleared_event_creation():
    """Test ConversationCleared event creation."""
    channel = Channel(channel_id=888)
    channel.add_message(Message(role="user", content=MessageContent(value="Message 1")))
    channel.add_message(Message(role="user", content=MessageContent(value="Message 2")))
    channel.clear()

    events = channel.domain_events
    assert len(events) == 3

    # Find the ConversationCleared event (should be the last one)
    cleared_event = None
    for event in events:
        if isinstance(event, ConversationCleared):
            cleared_event = event
            break

    assert cleared_event is not None
    assert cleared_event.event_id is not None
    assert cleared_event.occurred_at is not None
    assert cleared_event.aggregate_id == "888"
    assert cleared_event.previous_message_count == 2
    assert cleared_event.event_type == "channel.conversation.cleared"


class TestDomainEvent:
    def test_domain_event_has_timestamp(self):
        """Test that domain event has timestamp."""
        event = DomainEvent(
            event_id="evt-1",
            occurred_at=DomainEvent.now(),
            aggregate_id="agg-1",
        )

        assert event.event_id is not None
        assert event.occurred_at is not None
        assert event.aggregate_id == "agg-1"

    def test_domain_event_has_event_type_property(self):
        """Test that domain event has event_type property."""

        class TestEvent(DomainEvent):
            @property
            def event_type(self) -> str:
                return "test.event"

        event = TestEvent(
            event_id="evt-1",
            occurred_at=DomainEvent.now(),
            aggregate_id="agg-1",
        )

        assert event.event_type == "test.event"