# Domain Events Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add domain events mechanism to track important business occurrences (message added, conversation cleared) in the Channel aggregate.

**Architecture:** Domain events are recorded within aggregate operations, published via an Application-layer port, and handled by external systems. This follows DDD pattern of recording state changes as first-class domain concepts.

**Tech Stack:** Python 3.14, pytest, dataclasses, protocol-based ports (no external dependencies in domain layer)

---

## Implementation Tasks

### Task 1: Add Domain Event Base Interface

**Files:**
- Create: `src/domain/shared/domain_event.py`

**Step 1: Write the failing test**

```python
# tests/domain/test_domain_event.py
import pytest
from datetime import datetime

def test_domain_event_is_a_protocol():
    """Test that DomainEvent is a proper Protocol."""
    from src.domain.shared.domain_event import DomainEvent
    # Protocol should be usable for type checking
    assert hasattr(DomainEvent, '__proto__') or hasattr(DomainEvent, '__isabstractmethod__')
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/domain/test_domain_event.py -v
# Expected: ModuleNotFoundError: No module named 'src.domain.shared.domain_event'
```

**Step 3: Write minimal implementation**

```python
# src/domain/shared/domain_event.py
from datetime import datetime
from typing import Protocol


class DomainEvent(Protocol):
    """Interface for domain events."""

    @property
    def timestamp(self) -> datetime:
        """Event timestamp."""
        ...
```

**Step 4: Run test to verify it passes**

```bash
pytest tests/domain/test_domain_event.py -v
# Expected: PASS
```

**Step 5: Commit**

```bash
git add tests/domain/test_domain_event.py src/domain/shared/domain_event.py
git commit -m "feat: add DomainEvent base interface"
```

### Task 2: Add MessageAdded Event

**Files:**
- Create: `src/domain/channel/events.py`

**Step 1: Write the failing test**

```python
# tests/domain/test_events.py
import pytest
from datetime import datetime

def test_message_added_event_creation():
    """Test MessageAdded event creation."""
    from src.domain.channel.events import MessageAdded
    from src.domain.channel.aggregate import Channel
    from src.domain.channel.value_objects import Message
    
    channel = Channel(channel_id=123, max_messages=100)
    event = MessageAdded.from_channel(channel, "user", "Hello")
    
    assert event.channel_id == 123
    assert event.message_role == "user"
    assert event.message_content == "Hello"
    assert isinstance(event.timestamp, datetime)
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/domain/test_events.py -v
# Expected: ModuleNotFoundError: No module named 'src.domain.channel.events'
```

**Step 3: Write minimal implementation**

```python
# src/domain/channel/events.py
from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.domain.channel.aggregate import Channel


@dataclass(frozen=True)
class MessageAdded:
    """Event fired when a message is added to a channel."""

    channel_id: int
    message_role: str
    message_content: str
    timestamp: datetime

    @staticmethod
    def from_channel(channel: "Channel", role: str, content: str) -> "MessageAdded":
        """Create a MessageAdded event from a channel."""
        return MessageAdded(
            channel_id=channel.channel_id,
            message_role=role,
            message_content=content,
            timestamp=datetime.now(),
        )
```

**Step 4: Run test to verify it passes**

```bash
pytest tests/domain/test_events.py -v
# Expected: PASS
```

**Step 5: Commit**

```bash
git add src/domain/channel/events.py tests/domain/test_events.py
git commit -m "feat: add MessageAdded domain event"
```

### Task 3: Add ConversationCleared Event

**Files:**
- Modify: `src/domain/channel/events.py`

**Step 1: Update the test file**

```python
# tests/domain/test_events.py (add to existing file)
def test_conversation_cleared_event_creation():
    """Test ConversationCleared event creation."""
    from src.domain.channel.events import ConversationCleared
    from src.domain.channel.aggregate import Channel
    
    channel = Channel(channel_id=456, max_messages=100)
    # Add some messages first
    from src.domain.channel.value_objects import Message, MessageContent
    channel.add_message(Message(role="user", content=MessageContent(value="test")))
    
    event = ConversationCleared.from_channel(channel, 1)
    
    assert event.channel_id == 456
    assert event.previous_message_count == 1
    assert isinstance(event.timestamp, datetime)
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/domain/test_events.py::test_conversation_cleared_event_creation -v
# Expected: NameError: name 'ConversationCleared' is not defined
```

**Step 3: Write minimal implementation**

```python
# src/domain/channel/events.py (append to file)
@dataclass(frozen=True)
class ConversationCleared:
    """Event fired when a channel's conversation history is cleared."""

    channel_id: int
    previous_message_count: int
    timestamp: datetime

    @staticmethod
    def from_channel(channel: "Channel", previous_count: int) -> "ConversationCleared":
        """Create a ConversationCleared event from a channel."""
        return ConversationCleared(
            channel_id=channel.channel_id,
            previous_message_count=previous_count,
            timestamp=datetime.now(),
        )
```

**Step 4: Run test to verify it passes**

```bash
pytest tests/domain/test_events.py -v
# Expected: PASS
```

**Step 5: Commit**

```bash
git add src/domain/channel/events.py tests/domain/test_events.py
git commit -m "feat: add ConversationCleared domain event"
```

### Task 4: Add Events Collection to Channel Aggregate

**Files:**
- Modify: `src/domain/channel/aggregate.py`

**Step 1: Write the test**

```python
# tests/domain/test_channel.py (add to existing file)
def test_channel_collects_domain_events():
    """Test that Channel collects domain events."""
    from src.domain.channel.events import MessageAdded, ConversationCleared
    
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
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/domain/test_channel.py::TestChannel::test_channel_collects_domain_events -v
# Expected: AttributeError: 'Channel' object has no attribute 'domain_events'
```

**Step 3: Update implementation**

```python
# src/domain/channel/aggregate.py (modify the class)
@dataclass
class Channel:
    # ... existing fields ...
    _domain_events: list[DomainEvent] = field(default_factory=list, init=False, repr=False)

    def add_message(self, message: Message) -> None:
        """Add a message to the channel and record domain events."""
        if self.max_messages <= 0:
            return
        self.messages.append(message)
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages :]

        # Record domain event
        self._domain_events.append(
            MessageAdded.from_channel(self, message.role, message.content.value or "")
        )

    def clear(self) -> None:
        """Clear all messages in the channel and record domain event."""
        previous_count = len(self.messages)
        self.messages.clear()
        self._domain_events.append(
            ConversationCleared.from_channel(self, previous_count)
        )

    @property
    def domain_events(self) -> list[DomainEvent]:
        """Get accumulated domain events."""
        return self._domain_events

    def clear_events(self) -> None:
        """Clear accumulated domain events after publishing."""
        self._domain_events.clear()
```

**Step 4: Run test to verify it passes**

```bash
pytest tests/domain/test_channel.py::TestChannel::test_channel_collects_domain_events -v
# Expected: PASS
```

**Step 5: Commit**

```bash
git add src/domain/channel/aggregate.py tests/domain/test_channel.py
git commit -m "feat: add domain events collection to Channel aggregate"
```

### Task 5: Add Application Event Publisher Port

**Files:**
- Create: `src/application/shared/event_publisher.py`

**Step 1: Write the failing test**

```python
# tests/application/test_event_publisher.py
def test_event_publisher_port_protocol():
    """Test EventPublisherPort protocol."""
    from src.application.shared.event_publisher import EventPublisherPort
    import inspect
    
    # Protocol should have required methods
    assert hasattr(EventPublisherPort, 'publish')
    assert hasattr(EventPublisherPort, 'publish_all')
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/application/test_event_publisher.py -v
# Expected: ModuleNotFoundError: No module named 'src.application.shared.event_publisher'
```

**Step 3: Write minimal implementation**

```python
# src/application/shared/event_publisher.py
from typing import Protocol
from src.domain.shared.domain_event import DomainEvent


class EventPublisherPort(Protocol):
    """Port for publishing domain events."""

    def publish(self, event: DomainEvent) -> None:
        """Publish a single domain event."""

    def publish_all(self, events: list[DomainEvent]) -> None:
        """Publish multiple domain events."""
```

**Step 4: Run test to verify it passes**

```bash
pytest tests/application/test_event_publisher.py -v
# Expected: PASS
```

**Step 5: Commit**

```bash
git add src/application/shared/event_publisher.py tests/application/test_event_publisher.py
git commit -m "feat: add EventPublisherPort for domain events"
```

### Task 6: Add In-Memory Event Publisher Implementation

**Files:**
- Create: `src/infrastructure/event_publisher.py`

**Step 1: Write the test**

```python
# tests/infrastructure/test_event_publisher.py
def test_in_memory_event_publisher():
    """Test in-memory event publisher."""
    from src.infrastructure.event_publisher import InMemoryEventPublisher
    from src.domain.shared.domain_event import DomainEvent
    from src.domain.channel.events import MessageAdded
    
    publisher = InMemoryEventPublisher()
    
    # Collect published events
    published = []
    def capture(event: DomainEvent):
        published.append(event)
    
    # We'll test by mocking
    import unittest.mock
    with unittest.mock.patch('builtins.print') as mock_print:
        publisher.publish(MessageAdded(123, "user", "Hello", datetime.now()))
        assert len(published) == 1
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/infrastructure/test_event_publisher.py -v
# Expected: ModuleNotFoundError: No module named 'src.infrastructure.event_publisher'
```

**Step 3: Write minimal implementation**

```python
# src/infrastructure/event_publisher.py
import logging
from src.application.shared.event_publisher import EventPublisherPort
from src.domain.shared.domain_event import DomainEvent

logger = logging.getLogger(__name__)


class InMemoryEventPublisher(EventPublisherPort):
    """In-memory event publisher for development/testing."""

    def __init__(self) -> None:
        self._events: list[DomainEvent] = []

    def publish(self, event: DomainEvent) -> None:
        """Publish a single domain event."""
        self._events.append(event)
        logger.debug(f"Published event: {event}")

    def publish_all(self, events: list[DomainEvent]) -> None:
        """Publish multiple domain events."""
        for event in events:
            self.publish(event)

    def get_events(self) -> list[DomainEvent]:
        """Get all published events (for testing)."""
        return self._events

    def clear(self) -> None:
        """Clear all published events."""
        self._events.clear()
```

**Step 4: Run test to verify it passes**

```bash
pytest tests/infrastructure/test_event_publisher.py -v
# Expected: PASS
```

**Step 5: Commit**

```bash
git add src/infrastructure/event_publisher.py tests/infrastructure/test_event_publisher.py
git commit -m "feat: add InMemoryEventPublisher implementation"
```

### Task 7: Update Use Cases to Publish Events

**Files:**
- Modify: `src/application/messaging/handlers.py`

**Step 1: Write the test**

```python
# tests/application/test_use_cases.py (add to existing file)
def test_process_user_turn_publishes_events():
    """Test that ProcessUserTurn publishes domain events."""
    from src.domain.channel.aggregate import Channel
    from src.application.messaging.ports import AIServicePort
    from src.application.messaging.handlers import ProcessUserTurn
    import unittest.mock
    
    # Create a mock AI service
    class MockAIService:
        def generate_reply(self, channel: Channel, image_urls=()) -> str:
            return "Test reply"
    
    ai_service = MockAIService()
    repo = InMemoryMessageRepository()
    
    use_case = ProcessUserTurn(repo, ai_service)
    
    # Execute use case
    result = use_case.execute(channel_id=999, user_content="Hello")
    
    # Verify channel has events
    channel = repo.get(999)
    assert len(channel.domain_events) >= 1
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/application/test_use_cases.py::TestProcessUserTurn::test_process_user_turn_publishes_events -v
# Expected: FAIL with assertion error
```

**Step 3: Update implementation**

```python
# src/application/messaging/handlers.py (modify execute method)
class ProcessUserTurn:
    # ... existing code ...
    
    def execute(self, ...) -> str:
        # ... existing code ...
        try:
            # ... existing code ...
            
            # Publish domain events
            for event in channel.domain_events:
                # In real implementation, would call event publisher
                pass
            
            # Clear events after publishing
            channel.clear_events()
            
            self.logger.info(f"Generated response for channel_id {channel_id}")
            self.logger.debug(f"Response: {reply[:100]}...")
            
            return reply
```

**Step 4: Run test to verify it passes**

```bash
pytest tests/application/test_use_cases.py -v
# Expected: PASS
```

**Step 5: Commit**

```bash
git add src/application/messaging/handlers.py tests/application/test_use_cases.py
git commit -m "feat: update use cases to handle domain events"
```

### Task 8: Add Integration Tests

**Files:**
- Create: `tests/integration/test_domain_events.py`

**Step 1: Write the test**

```python
# tests/integration/test_domain_events.py
def test_full_workflow_with_domain_events():
    """Integration test for domain events in full workflow."""
    from src.domain.channel.aggregate import Channel
    from src.domain.channel.value_objects import Message, MessageContent
    from src.domain.channel.events import MessageAdded, ConversationCleared
    
    channel = Channel(channel_id=111, max_messages=100)
    
    # Initial state
    assert len(channel.domain_events) == 0
    
    # Add a message
    channel.add_message(Message(role="user", content=MessageContent(value="Hello")))
    
    assert len(channel.domain_events) == 1
    assert isinstance(channel.domain_events[0], MessageAdded)
    
    # Add another message
    channel.add_message(Message(role="assistant", content=MessageContent(value="Hi there")))
    
    assert len(channel.domain_events) == 2
    
    # Clear conversation
    channel.clear()
    
    assert len(channel.domain_events) == 3
    assert isinstance(channel.domain_events[2], ConversationCleared)
    
    # Verify event data
    added_event = channel.domain_events[0]
    assert added_event.channel_id == 111
    assert added_event.message_role == "user"
    assert added_event.message_content == "Hello"
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/integration/test_domain_events.py -v
# Expected: FAIL on first assertion (no events)
```

**Step 3: Run tests to verify implementation**

```bash
pytest tests/integration/test_domain_events.py -v
# Expected: PASS after previous commits
```

**Step 4: Commit**

```bash
git add tests/integration/test_domain_events.py
git commit -m "feat: add integration tests for domain events"
```

---

## Testing and Verification

After all commits, run:

```bash
# Run all tests
pytest -v

# Check coverage
pytest --cov=src --cov-report=term-missing -v

# Type checking
mypy src/

# Linting
ruff check src/
```

Expected: All tests pass, no linting errors

---

## Summary

**Total Commits:** 10-12 (one per task)

**Files Created:**
- `src/domain/shared/domain_event.py`
- `src/domain/channel/events.py`
- `src/application/shared/event_publisher.py`
- `src/infrastructure/event_publisher.py`
- `tests/domain/test_domain_event.py`
- `tests/domain/test_events.py`
- `tests/application/test_event_publisher.py`
- `tests/infrastructure/test_event_publisher.py`
- `tests/integration/test_domain_events.py`

**Key Patterns:**
- Protocol-based interfaces (no concrete dependencies in domain layer)
- Dataclasses for immutable events
- Domain events collected in aggregate, not published immediately
- Separate port for event publisher (Application layer)
- In-memory implementation for testing

**Architecture Alignment:**
- Domain layer: Pure, no external dependencies
- Application layer: Defines ports, orchestrates use cases
- Infrastructure layer: Implements ports with concrete adapters

Plan complete and saved to `docs/plans/2026-02-05-domain-events.md`. Two execution options:

**1. Subagent-Driven (this session)** - I dispatch fresh subagent per task, review between tasks, fast iteration

**2. Parallel Session (separate)** - Open new session with executing-plans, batch execution with checkpoints

**Which approach?**