"""Tests for EventPublisherPort protocol."""

import inspect
from src.application.shared.event_publisher import EventPublisherPort


def test_event_publisher_port_protocol():
    """Test EventPublisherPort protocol."""
    # Protocol should have required methods
    assert hasattr(EventPublisherPort, 'publish')
    assert hasattr(EventPublisherPort, 'publish_all')