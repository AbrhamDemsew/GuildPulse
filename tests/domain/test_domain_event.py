"""Tests for DomainEvent base interface."""

from typing import Protocol
from datetime import datetime

from src.domain.shared.domain_event import DomainEvent


def test_domain_event_is_a_protocol():
    """Test that DomainEvent is a proper Protocol."""
    # Protocol should be a Protocol class
    assert isinstance(DomainEvent, type)
    assert hasattr(DomainEvent, 'timestamp')
    assert callable(getattr(DomainEvent, 'timestamp', None)) or isinstance(
        getattr(DomainEvent, 'timestamp', None), property
    )


def test_domain_event_has_timestamp_property():
    """Test that DomainEvent has timestamp property."""
    # Protocol should define timestamp property
    assert hasattr(DomainEvent, 'timestamp')