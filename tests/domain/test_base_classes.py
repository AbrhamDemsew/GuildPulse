"""Tests for domain base classes."""

import pytest
from src.domain.shared.entity import Entity
from src.domain.shared.value_object import ValueObject
from src.domain.shared.aggregate_root import AggregateRoot
from src.domain.shared.domain_event import DomainEvent


class TestEntity:
    def test_entity_has_identity(self):
        class TestEntity(Entity[str]):
            def __init__(self, id: str, value: str):
                super().__init__(id)
                self.value = value

        e1 = TestEntity("id-1", "test")
        e2 = TestEntity("id-1", "different")
        e3 = TestEntity("id-2", "test")

        assert e1 == e2  # Same ID
        assert e1 != e3  # Different ID

    def test_entity_equality_by_id(self):
        class User(Entity[str]):
            def __init__(self, user_id: str, name: str):
                super().__init__(user_id)
                self.name = name

        user1 = User("user-1", "Alice")
        user2 = User("user-1", "Bob")

        assert user1 == user2  # Same user ID


class TestValueObject:
    def test_value_object_equality_by_attributes(self):
        class Money(ValueObject[dict]):
            def __init__(self, amount: float, currency: str):
                super().__init__({"amount": amount, "currency": currency})

            @property
            def amount(self) -> float:
                return self._props["amount"]

            @property
            def currency(self) -> str:
                return self._props["currency"]

        m1 = Money(100.0, "USD")
        m2 = Money(100.0, "USD")
        m3 = Money(200.0, "USD")

        assert m1 == m2  # Same attributes
        assert m1 != m3  # Different attributes

    def test_value_object_immutable(self):
        class Email(ValueObject[str]):
            def __init__(self, address: str):
                super().__init__(address)

            @property
            def address(self) -> str:
                return self._props

        email = Email("test@example.com")
        with pytest.raises(AttributeError):
            email._props = "new@example.com"


class TestAggregateRoot:
    def test_aggregate_root_has_domain_events(self):
        class TestAggregate(AggregateRoot[str]):
            def __init__(self, id: str):
                super().__init__(id)
                self.value = "test"

        agg = TestAggregate("agg-1")
        assert len(agg.domain_events) == 0

    def test_aggregate_root_can_add_events(self):
        class TestAggregate(AggregateRoot[str]):
            def __init__(self, id: str):
                super().__init__(id)
                self.value = "test"

        agg = TestAggregate("agg-1")
        event = DomainEvent(event_id="evt-1", occurred_at=DomainEvent.now(), aggregate_id="agg-1")
        agg.add_domain_event(event)

        assert len(agg.domain_events) == 1
        assert agg.domain_events[0] == event

    def test_aggregate_root_can_clear_events(self):
        class TestAggregate(AggregateRoot[str]):
            def __init__(self, id: str):
                super().__init__(id)
                self.value = "test"

        agg = TestAggregate("agg-1")
        event = DomainEvent(event_id="evt-1", occurred_at=DomainEvent.now(), aggregate_id="agg-1")
        agg.add_domain_event(event)

        agg.clear_domain_events()
        assert len(agg.domain_events) == 0


class TestDomainEvent:
    def test_domain_event_has_timestamp(self):
        event = DomainEvent(event_id="evt-1", occurred_at=DomainEvent.now(), aggregate_id="agg-1")

        assert event.event_id is not None
        assert event.occurred_at is not None
        assert event.aggregate_id == "agg-1"

    def test_domain_event_generates_unique_event_id(self):
        event1 = DomainEvent(
            event_id=DomainEvent.generate_event_id(),
            occurred_at=DomainEvent.now(),
            aggregate_id="agg-1",
        )
        event2 = DomainEvent(
            event_id=DomainEvent.generate_event_id(),
            occurred_at=DomainEvent.now(),
            aggregate_id="agg-1",
        )

        assert event1.event_id != event2.event_id
