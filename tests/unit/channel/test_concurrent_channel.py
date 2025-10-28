"""Tests for concurrent access to Channel aggregate."""

import threading
from src.domain.channel.aggregate import Channel
from src.domain.channel.value_objects import Message, MessageContent


def test_concurrent_message_additions():
    """Test that concurrent message additions don't corrupt the history."""
    channel = Channel(id=123)

    errors = []

    def add_message(role: str):
        try:
            channel.add_message(Message(role=role, content=MessageContent(value="test")))
        except Exception as e:
            errors.append((role, e))

    # Simulate concurrent access with threads
    threads = [
        threading.Thread(target=add_message, args=("user",)),
        threading.Thread(target=add_message, args=("user",)),
    ]

    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert len(errors) == 0, f"Errors occurred: {errors}"

    # Verify the channel has the messages
    messages = channel.get_messages()
    assert len(messages) == 2
