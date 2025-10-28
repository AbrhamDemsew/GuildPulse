"""Tests for Channel aggregate."""

from src.domain.channel.aggregate import Channel
from src.domain.channel.events import MessageAdded
from src.domain.channel.value_objects import Message, MessageContent
from src.domain.shared.aggregate_root import AggregateRoot


def test_channel_is_aggregate_root():
    """Test that Channel extends AggregateRoot."""
    channel = Channel(id=123)
    assert isinstance(channel, AggregateRoot)
    assert hasattr(channel, "domain_events")
    assert hasattr(channel, "add_domain_event")
    assert hasattr(channel, "clear_domain_events")


def test_channel_collects_domain_events():
    """Test that Channel collects domain events."""
    channel = Channel(id=999)
    channel.add_message(Message(role="user", content=MessageContent(value="Hello")))

    events = channel.domain_events
    assert len(events) == 1
    assert isinstance(events[0], MessageAdded)


def test_channel_clears_events_after_publishing():
    """Test that events can be cleared after publishing."""
    channel = Channel(id=999)
    channel.add_message(Message(role="user", content=MessageContent(value="Hello")))

    channel.clear_domain_events()
    assert len(channel.domain_events) == 0


def test_channel_is_thread_safe():
    """Test that Channel is thread-safe for concurrent operations."""
    import threading

    channel = Channel(id=888, max_messages=10)
    errors = []

    def add_message(i):
        try:
            channel.add_message(Message(role="user", content=MessageContent(value=f"Message {i}")))
        except Exception as e:
            errors.append(e)

    threads = [threading.Thread(target=add_message, args=(i,)) for i in range(20)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert len(errors) == 0
    assert channel.count_messages() <= 10  # max_messages limit
