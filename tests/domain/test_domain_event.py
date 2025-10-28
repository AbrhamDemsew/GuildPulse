"""Tests for DomainEvent base interface."""

from src.domain.shared.domain_event import DomainEvent


def test_domain_event_is_a_protocol():
    """Test that DomainEvent follows the Protocol pattern."""
    # DomainEvent should be a class
    assert isinstance(DomainEvent, type)
    # Create an instance to check attributes
    event = DomainEvent(event_id="test", occurred_at=DomainEvent.now(), aggregate_id="agg")
    assert hasattr(event, "event_id")
    assert hasattr(event, "occurred_at")
    assert hasattr(event, "aggregate_id")


def test_domain_event_has_timestamp_property():
    """Test that DomainEvent has occurred_at attribute."""
    event = DomainEvent(event_id="test", occurred_at=DomainEvent.now(), aggregate_id="agg")
    assert hasattr(event, "occurred_at")
    assert event.occurred_at is not None
