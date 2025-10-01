"""Tests for InMemoryEventPublisher."""

from datetime import datetime
from src.domain.channel.events import MessageAdded
from src.infrastructure.event_publisher import InMemoryEventPublisher


def test_in_memory_event_publisher():
    """Test in-memory event publisher."""
    publisher = InMemoryEventPublisher()
    
    # Publish an event
    event = MessageAdded(
        channel_id=123,
        message_role="user",
        message_content="Hello",
        timestamp=datetime.now()
    )
    
    publisher.publish(event)
    
    # Verify event was stored
    events = publisher.get_events()
    assert len(events) == 1
    assert events[0] == event
    
    # Clear events
    publisher.clear()
    assert len(publisher.get_events()) == 0