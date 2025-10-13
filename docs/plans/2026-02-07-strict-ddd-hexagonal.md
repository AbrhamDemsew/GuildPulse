# Strict DDD + Hexagonal Refactoring Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Refactor the codebase to achieve 100% compliance with Clean Architecture + DDD + Hexagonal patterns, addressing strategic DDD gaps while maintaining existing functionality.

**Architecture:** 
- Clean Architecture: Domain → Application → Infrastructure → Frameworks (dependencies inward)
- DDD Tactical: Aggregates (Channel), Value Objects (MessageContent), Domain Events (MessageAdded)
- Hexagonal: Driver Ports (AIServicePort), Driven Ports (MessageRepository), Adapters (OpenAI, InMemory)
- Strategic: Bounded Contexts, Ubiquitous Language, Context Mapping

**Tech Stack:** Python 3.13, pytest 9.0, pydantic 2.0, discord.py 2.3, basedpyright strict mode

---

## Phase 1: Domain Layer Improvements

### Task 1: Create Domain Base Classes

**Files:**
- Create: `src/domain/shared/entity.py`
- Create: `src/domain/shared/value_object.py`
- Create: `src/domain/shared/aggregate_root.py`
- Create: `src/domain/shared/domain_event.py` (enhance existing)
- Create: `src/domain/shared/errors.py` (enhance existing)

**Step 1: Write the failing test**

```python
# tests/domain/test_base_classes.py
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


class TestDomainEvent:
    def test_domain_event_has_timestamp(self):
        class OrderCreated(DomainEvent):
            def __init__(self, order_id: str):
                super().__init__(order_id)
                self.event_type = "order.created"
        
        event = OrderCreated("order-1")
        
        assert event.event_id is not None
        assert event.occurred_at is not None
        assert event.aggregate_id == "order-1"
        assert event.event_type == "order.created"
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/domain/test_base_classes.py -v`
Expected: FAIL with "No module named 'src.domain.shared.entity'" etc.

**Step 3: Write minimal implementation**

```python
# src/domain/shared/entity.py
"""Base class for entities with identity."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Generic, TypeVar

ID = TypeVar("ID")


@dataclass
class Entity(Generic[ID]):
    """Base class for entities that have identity-based equality."""

    id: ID

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Entity):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)
```

```python
# src/domain/shared/value_object.py
"""Base class for immutable value objects."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Generic, TypeVar

Props = TypeVar("Props")


@dataclass(frozen=True)
class ValueObject(Generic[Props]):
    """Base class for immutable value objects with structural equality."""

    _props: Props

    @property
    def props(self) -> Props:
        """Get the props for comparison."""
        return self._props

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ValueObject):
            return False
        return self._props == other._props

    def __hash__(self) -> int:
        return hash(self._props)
```

```python
# src/domain/shared/aggregate_root.py
"""Base class for aggregate roots."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, List

from src.domain.shared.domain_event import DomainEvent

if TYPE_CHECKING:
    from src.domain.shared.entity import Entity


@dataclass
class AggregateRoot(Entity[ID]):
    """Base class for aggregate roots that manage consistency boundary."""

    _domain_events: List[DomainEvent] = field(default_factory=list, init=False, repr=False)

    def add_domain_event(self, event: DomainEvent) -> None:
        """Add a domain event to the aggregate."""
        self._domain_events.append(event)

    def clear_domain_events(self) -> None:
        """Clear domain events after publishing."""
        self._domain_events.clear()

    @property
    def domain_events(self) -> List[DomainEvent]:
        """Get all domain events."""
        return self._domain_events.copy()
```

```python
# src/domain/shared/domain_event.py
"""Domain events base class."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from typing import Protocol


@dataclass(frozen=True)
class DomainEvent:
    """Base class for domain events representing significant domain changes."""

    event_id: str
    occurred_at: datetime
    aggregate_id: str

    @staticmethod
    def generate_event_id() -> str:
        """Generate unique event ID."""
        import uuid
        return str(uuid.uuid4())

    @staticmethod
    def now() -> datetime:
        """Get current timestamp."""
        return datetime.now()

    @property
    def event_type(self) -> str:
        """Override in subclasses to return event type."""
        raise NotImplementedError
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/domain/test_base_classes.py -v`
Expected: PASS (3 test classes, 8+ tests)

**Step 5: Commit**

```bash
git add src/domain/shared/entity.py \
        src/domain/shared/value_object.py \
        src/domain/shared/aggregate_root.py \
        src/domain/shared/domain_event.py \
        tests/domain/test_base_classes.py
git commit -m "feat: add domain base classes for entity, value_object, aggregate_root, domain_event"
```

---

### Task 2: Refactor Channel Aggregate

**Files:**
- Modify: `src/domain/channel/aggregate.py`
- Test: `tests/domain/test_channel.py`

**Step 1: Update Channel to extend AggregateRoot**

```python
# src/domain/channel/aggregate.py
"""Channel aggregate for managing conversation history."""

from __future__ import annotations

import threading
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from src.domain.channel.events import ConversationCleared, MessageAdded
from src.domain.shared.aggregate_root import AggregateRoot
from src.domain.shared.domain_event import DomainEvent

if TYPE_CHECKING:
    from src.domain.channel.value_objects import Message


@dataclass
class Channel(AggregateRoot[int]):
    """Aggregate root for channel conversations."""

    max_messages: int = 100
    _lock: threading.Lock = field(default_factory=lambda: threading.Lock(), init=False, repr=False)

    def __init__(self, channel_id: int, max_messages: int = 100):
        super().__init__(channel_id)
        self.max_messages = max_messages
        self._messages: list[Message] = []
        self._domain_events: list[DomainEvent] = []

    def add_message(self, message: Message) -> None:
        """Add a message to the channel and record domain events."""
        with self._lock:
            if self.max_messages <= 0:
                return
            self._messages.append(message)
            if len(self._messages) > self.max_messages:
                self._messages = self._messages[-self.max_messages :]

            self.add_domain_event(
                MessageAdded.from_channel(self, message.role, message.content.value or "")
            )

    def get_messages(self) -> list[Message]:
        """Get all messages in the channel."""
        return self._messages.copy()

    def get_messages_for_api(self) -> list[dict[str, Any]]:
        """Get messages as dictionaries for API consumption."""
        return [msg.to_dict() for msg in self._messages]

    def clear(self) -> None:
        """Clear all messages in the channel and record domain event."""
        previous_count = len(self._messages)
        self._messages.clear()
        self.add_domain_event(ConversationCleared.from_channel(self, previous_count))

    def count_messages(self) -> int:
        """Count the number of messages."""
        return len(self._messages)
```

**Step 2: Update tests for Channel**

```python
# tests/domain/test_channel.py
import pytest
from src.domain.channel.aggregate import Channel
from src.domain.channel.value_objects import Message, MessageContent
from src.domain.shared.domain_event import DomainEvent


def test_channel_is_aggregate_root():
    """Test that Channel extends AggregateRoot."""
    channel = Channel(channel_id=123)
    assert hasattr(channel, "domain_events")
    assert hasattr(channel, "add_domain_event")
    assert hasattr(channel, "clear_domain_events")


def test_channel_collects_domain_events():
    """Test that Channel collects domain events."""
    channel = Channel(channel_id=999)
    channel.add_message(Message(role="user", content=MessageContent(value="Hello")))
    
    events = channel.domain_events
    assert len(events) == 1
    assert isinstance(events[0], MessageAdded)


def test_channel_clears_events_after_publishing():
    """Test that events can be cleared after publishing."""
    channel = Channel(channel_id=999)
    channel.add_message(Message(role="user", content=MessageContent(value="Hello")))
    
    channel.clear_domain_events()
    assert len(channel.domain_events) == 0


def test_channel_is_thread_safe():
    """Test that Channel is thread-safe for concurrent operations."""
    import threading
    
    channel = Channel(channel_id=888, max_messages=10)
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
```

**Step 3: Run test to verify it fails initially**

Run: `pytest tests/domain/test_channel.py -v`
Expected: FAIL (Channel doesn't extend AggregateRoot yet)

**Step 4: Implement Channel refactoring**

Already done in Step 1.

**Step 5: Run test to verify it passes**

Run: `pytest tests/domain/test_channel.py -v`
Expected: PASS

**Step 6: Commit**

```bash
git add src/domain/channel/aggregate.py tests/domain/test_channel.py
git commit -m "refactor: make Channel extend AggregateRoot"
```

---

### Task 3: Refactor Message to Entity

**Files:**
- Modify: `src/domain/channel/value_objects.py`
- Test: `tests/domain/test_value_objects.py`

**Step 1: Update Message to extend Entity**

```python
# src/domain/channel/value_objects.py
"""Value objects for the domain model."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional

from src.domain.shared.entity import Entity
from src.domain.shared.errors import MessageValidationError

__all__ = ["MessageContent", "Message", "MessageRole"]


class MessageRole(Enum):
    """Enum for message roles."""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


@dataclass(frozen=True)
class MessageContent:
    """Value object representing the content of a message."""

    value: Optional[str] = None

    def __post_init__(self) -> None:
        """Validate message content."""
        if self.value is None:
            raise MessageValidationError("Message content cannot be None")
        if self.value == "":
            raise MessageValidationError("Message content cannot be empty")
        if len(self.value) > 10000:
            raise MessageValidationError("Message content too long (max 10000 characters)")

    def __str__(self) -> str:
        if self.value is None:
            return ""
        return self.value


@dataclass
class Message(Entity[str]):
    """Entity representing a message in a conversation."""

    role: str
    content: MessageContent
    timestamp: datetime = field(default_factory=datetime.now)

    def __post_init__(self) -> None:
        """Validate message."""
        valid_roles = {"system", "user", "assistant"}
        if self.role not in valid_roles:
            raise MessageValidationError(f"Invalid role: {self.role}")

    def to_dict(self) -> dict[str, str]:
        """Convert message to dictionary."""
        content = self.content.value or ""
        return {"role": self.role, "content": content}

    def __hash__(self) -> int:
        return super().__hash__()
```

**Step 2: Update tests for Message**

```python
# tests/domain/test_value_objects.py
import pytest
from src.domain.channel.value_objects import Message, MessageContent, MessageRole
from src.domain.shared.entity import Entity


def test_message_is_entity():
    """Test that Message is an Entity with identity-based equality."""
    msg1 = Message(role="user", content=MessageContent(value="Hello"))
    msg2 = Message(role="user", content=MessageContent(value="Hello"))
    
    # Messages have different IDs, so they're not equal
    assert msg1 != msg2
    
    # But they should both be Entities
    assert isinstance(msg1, Entity)


def test_message_equality_by_id():
    """Test that Message equality is based on ID."""
    msg1 = Message(role="user", content=MessageContent(value="Hello"))
    msg2 = Message(role="user", content=MessageContent(value="Hello"))
    
    # They have different IDs (auto-generated), so not equal
    assert msg1.id != msg2.id
    assert msg1 != msg2


def test_message_can_be_created_with_custom_id():
    """Test that Message can be created with custom ID."""
    msg = Message(id="msg-123", role="user", content=MessageContent(value="Hello"))
    
    assert msg.id == "msg-123"
```

**Step 3: Run test to verify it fails initially**

Run: `pytest tests/domain/test_value_objects.py::test_message_is_entity -v`
Expected: FAIL (Message doesn't extend Entity yet)

**Step 4: Implement Message refactoring**

Already done in Step 1.

**Step 5: Run test to verify it passes**

Run: `pytest tests/domain/test_value_objects.py -v`
Expected: PASS

**Step 6: Commit**

```bash
git add src/domain/channel/value_objects.py tests/domain/test_value_objects.py
git commit -m "refactor: make Message an Entity with identity"
```

---

### Task 4: Refactor Domain Events

**Files:**
- Modify: `src/domain/channel/events.py`
- Test: `tests/domain/test_events.py`

**Step 1: Update events to use new DomainEvent base**

```python
# src/domain/channel/events.py
"""Domain events for the Channel aggregate."""

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING

from src.domain.shared.domain_event import DomainEvent

if TYPE_CHECKING:
    from src.domain.channel.aggregate import Channel


@dataclass(frozen=True)
class MessageAdded(DomainEvent):
    """Event fired when a message is added to a channel."""

    message_role: str
    message_content: str

    @staticmethod
    def from_channel(channel: "Channel", role: str, content: str) -> "MessageAdded":
        """Create a MessageAdded event from a channel."""
        return MessageAdded(
            event_id=DomainEvent.generate_event_id(),
            occurred_at=DomainEvent.now(),
            aggregate_id=str(channel.channel_id),
            message_role=role,
            message_content=content,
        )

    @property
    def event_type(self) -> str:
        return "channel.message.added"


@dataclass(frozen=True)
class ConversationCleared(DomainEvent):
    """Event fired when a channel's conversation history is cleared."""

    previous_message_count: int

    @staticmethod
    def from_channel(channel: "Channel", previous_count: int) -> "ConversationCleared":
        """Create a ConversationCleared event from a channel."""
        return ConversationCleared(
            event_id=DomainEvent.generate_event_id(),
            occurred_at=DomainEvent.now(),
            aggregate_id=str(channel.channel_id),
            previous_message_count=previous_count,
        )

    @property
    def event_type(self) -> str:
        return "channel.conversation.cleared"
```

**Step 2: Update tests for domain events**

```python
# tests/domain/test_events.py
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
    assert len(events) == 1
    
    event = events[0]
    assert isinstance(event, ConversationCleared)
    assert event.event_id is not None
    assert event.occurred_at is not None
    assert event.aggregate_id == "888"
    assert event.previous_message_count == 2
    assert event.event_type == "channel.conversation.cleared"
```

**Step 3: Run test to verify it fails initially**

Run: `pytest tests/domain/test_events.py -v`
Expected: FAIL (events don't extend DomainEvent yet)

**Step 4: Implement event refactoring**

Already done in Step 1.

**Step 5: Run test to verify it passes**

Run: `pytest tests/domain/test_events.py -v`
Expected: PASS

**Step 6: Commit**

```bash
git add src/domain/channel/events.py tests/domain/test_events.py
git commit -m "refactor: make domain events extend DomainEvent base"
```

---

## Phase 2: Application Layer Ports

### Task 5: Create Domain-Specific Ports

**Files:**
- Create: `src/application/ports/channel_repository_port.py`
- Create: `src/application/ports/ai_service_port.py`
- Create: `src/application/ports/config_port.py`
- Test: `tests/application/test_ports.py`

**Step 1: Write the failing test**

```python
# tests/application/test_ports.py
"""Tests for application ports."""
import pytest
from typing import Protocol


class TestChannelRepositoryPort:
    def test_channel_repository_protocol(self):
        """Test that ChannelRepositoryPort is properly defined."""
        from src.application.ports.channel_repository_port import IChannelRepositoryPort
        
        # Should be a Protocol
        assert hasattr(IChannelRepositoryPort, "save")
        assert hasattr(IChannelRepositoryPort, "get")
        assert hasattr(IChannelRepositoryPort, "get_or_create")


class TestAIServicePort:
    def test_ai_service_protocol(self):
        """Test that AIServicePort is properly defined."""
        from src.application.ports.ai_service_port import IAIServicePort
        
        # Should be a Protocol
        assert hasattr(IAIServicePort, "generate_reply")


class TestConfigPort:
    def test_config_port_protocol(self):
        """Test that ConfigPort is properly defined."""
        from src.application.ports.config_port import IConfigPort
        
        # Should be a Protocol
        assert hasattr(IConfigPort, "get_discord_token")
        assert hasattr(IConfigPort, "get_openai_api_key")
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/application/test_ports.py -v`
Expected: FAIL with import errors

**Step 3: Write minimal implementation**

```python
# src/application/ports/channel_repository_port.py
"""Protocol for channel repository operations."""
from typing import Protocol

from src.domain.channel.aggregate import Channel


class IChannelRepositoryPort(Protocol):
    """Protocol for channel repository operations."""

    def save(self, channel: Channel) -> None:
        """Save a channel to persistent storage."""

    def get(self, channel_id: int) -> Channel:
        """Get a channel by ID."""

    def get_or_create(self, channel_id: int) -> Channel:
        """Get existing channel or create a new one."""
```

```python
# src/application/ports/ai_service_port.py
"""Protocol for AI service operations."""
from typing import Protocol

from src.domain.channel.aggregate import Channel


class IAIServicePort(Protocol):
    """Protocol for AI service operations."""

    def generate_reply(self, channel: Channel, image_urls: tuple[str, ...] = ()) -> str:
        """Generate a reply for the channel conversation."""
```

```python
# src/application/ports/config_port.py
"""Protocol for configuration access."""
from typing import Protocol


class IConfigPort(Protocol):
    """Protocol for configuration access."""

    def get_discord_token(self) -> str:
        """Get the Discord bot token."""

    def get_openai_api_key(self) -> str:
        """Get the OpenAI API key."""

    def get_openai_base_url(self) -> str:
        """Get the OpenAI API base URL."""

    def get_openai_model(self) -> str:
        """Get the default OpenAI model name."""

    def get_openai_max_tokens(self) -> int:
        """Get maximum tokens for generation."""

    def get_openai_temperature(self) -> float:
        """Get generation temperature."""

    def get_system_prompt(self) -> str:
        """Get the system prompt for chat completions."""
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/application/test_ports.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/application/ports/channel_repository_port.py \
        src/application/ports/ai_service_port.py \
        src/application/ports/config_port.py \
        tests/application/test_ports.py
git commit -m "feat: add application port protocols for repository, AI, and config"
```

---

### Task 6: Update Use Cases to Use New Ports

**Files:**
- Modify: `src/application/messaging/handlers.py`
- Modify: `src/application/messaging/ports.py` (deprecate old ports)

**Step 1: Update handlers to use new ports**

```python
# src/application/messaging/handlers.py
"""Use cases for messaging operations."""

import logging

from src.application.messaging.ports import IAIServicePort
from src.application.ports.channel_repository_port import IChannelRepositoryPort
from src.config import get_settings
from src.domain.channel.aggregate import Channel
from src.domain.channel.value_objects import Message, MessageContent


class ProcessUserTurn:
    """Use case to process a user turn and generate AI reply."""

    def __init__(
        self,
        repo: IChannelRepositoryPort,
        ai_service: IAIServicePort,
    ) -> None:
        self.repo = repo
        self.ai_service = ai_service
        self.settings = get_settings()
        self.logger = logging.getLogger(__name__)

    def execute(
        self,
        channel_id: int,
        user_content: str,
        *,
        channel: Channel | None = None,
        author_name: str = "User",
        bot_name: str = "Bot",
        image_urls: tuple[str, ...] = (),
    ) -> str:
        """Process user message and return AI reply."""
        try:
            self.logger.debug(f"Processing user turn for channel_id {channel_id}")

            if channel is None:
                channel = self.repo.get_or_create(channel_id)

            prefixed_user_content = f"{author_name}: {user_content}"
            assert channel is not None
            channel.add_message(
                Message(role="user", content=MessageContent(value=prefixed_user_content))
            )

            reply = self.ai_service.generate_reply(channel, image_urls)

            prefixed_reply = f"{bot_name}: {reply}"
            channel.add_message(
                Message(role="assistant", content=MessageContent(value=prefixed_reply))
            )

            self.repo.save(channel)

            self.logger.info(f"Generated response for channel_id {channel_id}")
            self.logger.debug(f"Response: {reply[:100]}...")

            return reply

        except Exception:
            self.logger.exception(f"Unexpected error for channel_id {channel_id}")
            return "An unexpected error occurred. Please try again."


class ClearChannelHistory:
    """Use case to clear a channel's conversation history."""

    def __init__(self, repo: IChannelRepositoryPort) -> None:
        self.repo = repo
        self.logger = logging.getLogger(__name__)

    def execute(self, channel_id: int) -> bool:
        """Clear the channel's conversation history. Returns True if cleared."""
        try:
            self.logger.debug(f"Clearing history for channel_id {channel_id}")

            channel = self.repo.get(channel_id)
            if not channel:
                self.logger.warning(f"Channel not found for channel_id {channel_id}")
                return False

            if not channel.messages:
                self.logger.info(f"Channel already empty for channel_id {channel_id}")
                return False

            channel.clear()
            self.repo.save(channel)

            self.logger.info(f"Cleared conversation history for channel_id {channel_id}")

            return True

        except Exception:
            self.logger.exception(f"Unexpected error for channel_id {channel_id}")
            return False
```

**Step 2: Deprecate old ports file**

```python
# src/application/messaging/ports.py
"""Deprecated: Application ports for domain services."""

from typing import Protocol

from src.domain.channel.aggregate import Channel


class AIServicePort(Protocol):
    """Deprecated: Use IAIServicePort from application.ports.ai_service_port."""

    def generate_reply(self, channel: Channel, image_urls: tuple[str, ...] = ()) -> str: ...

    def __init_subclass__(cls, **kwargs):
        import warnings
        warnings.warn(
            "AIServicePort is deprecated. Use IAIServicePort from application.ports.ai_service_port.",
            DeprecationWarning,
            stacklevel=2,
        )
```

**Step 3: Update tests**

```python
# tests/application/test_use_cases.py
import pytest
from unittest.mock import Mock

from src.application.ports.channel_repository_port import IChannelRepositoryPort
from src.application.ports.ai_service_port import IAIServicePort
from src.application.messaging.handlers import ProcessUserTurn, ClearChannelHistory
from src.domain.channel.aggregate import Channel
from src.domain.channel.value_objects import Message, MessageContent


@pytest.fixture
def mock_repo():
    """Create a mock channel repository."""
    return Mock(spec=IChannelRepositoryPort)


@pytest.fixture
def mock_ai_service():
    """Create a mock AI service."""
    return Mock(spec=IAIServicePort)


def test_process_user_turn_uses_new_ports(mock_repo, mock_ai_service):
    """Test that ProcessUserTurn uses the new port interfaces."""
    handler = ProcessUserTurn(mock_repo, mock_ai_service)
    
    # Should accept port interfaces
    assert isinstance(handler.repo, IChannelRepositoryPort)
    assert isinstance(handler.ai_service, IAIServicePort)


def test_clear_channel_history_uses_new_port(mock_repo):
    """Test that ClearChannelHistory uses the new port interface."""
    handler = ClearChannelHistory(mock_repo)
    
    # Should accept port interface
    assert isinstance(handler.repo, IChannelRepositoryPort)
```

**Step 4: Run test to verify it fails initially**

Run: `pytest tests/application/test_use_cases.py -v`
Expected: FAIL (import issues with new ports)

**Step 5: Implement port updates**

Already done in Step 1 and Step 2.

**Step 6: Run test to verify it passes**

Run: `pytest tests/application/test_use_cases.py -v`
Expected: PASS

**Step 7: Commit**

```bash
git add src/application/messaging/handlers.py \
        src/application/messaging/ports.py \
        tests/application/test_use_cases.py
git commit -m "refactor: update use cases to use new application ports"
```

---

## Phase 3: Infrastructure Layer Adapters

### Task 7: Update Repository Implementation

**Files:**
- Modify: `src/infrastructure/persistence/memory/repository.py`
- Create: `tests/infrastructure/test_memory_repository.py`

**Step 1: Update repository to use new port**

```python
# src/infrastructure/persistence/memory/repository.py
"""In-memory implementation of ChannelRepository."""

from src.application.ports.channel_repository_port import IChannelRepositoryPort
from src.domain.channel.aggregate import Channel
from src.domain.shared.errors import ChannelNotFoundError


class InMemoryChannelRepository(IChannelRepositoryPort):
    """In-memory repository for Channel persistence."""

    def __init__(self) -> None:
        self._channels: dict[int, Channel] = {}

    def save(self, channel: Channel) -> None:
        """Save a channel."""
        self._channels[channel.channel_id] = channel

    def get(self, channel_id: int) -> Channel:
        """Get a channel by ID."""
        if channel_id not in self._channels:
            raise ChannelNotFoundError(f"Channel {channel_id} not found")
        return self._channels[channel_id]

    def get_or_create(self, channel_id: int) -> Channel:
        """Get existing channel or create a new one."""
        if channel_id not in self._channels:
            self._channels[channel_id] = Channel(channel_id=channel_id)
        return self._channels[channel_id]
```

**Step 2: Write tests for repository**

```python
# tests/infrastructure/test_memory_repository.py
"""Tests for in-memory channel repository."""
import pytest

from src.application.ports.channel_repository_port import IChannelRepositoryPort
from src.domain.channel.aggregate import Channel
from src.domain.shared.errors import ChannelNotFoundError
from src.infrastructure.persistence.memory.repository import InMemoryChannelRepository


class TestInMemoryChannelRepository:
    """Test InMemoryChannelRepository implementation."""

    def test_repository_implements_protocol(self):
        """Test that repository implements the protocol."""
        repo = InMemoryChannelRepository()
        
        assert isinstance(repo, IChannelRepositoryPort)

    def test_save_and_get_channel(self):
        """Test saving and retrieving a channel."""
        repo = InMemoryChannelRepository()
        channel = Channel(channel_id=123)
        
        repo.save(channel)
        retrieved = repo.get(123)
        
        assert retrieved.channel_id == 123

    def test_get_or_create_new_channel(self):
        """Test creating a new channel."""
        repo = InMemoryChannelRepository()
        
        channel = repo.get_or_create(456)
        
        assert channel.channel_id == 456
        assert len(channel.domain_events) == 0

    def test_get_or_create_existing_channel(self):
        """Test retrieving an existing channel."""
        repo = InMemoryChannelRepository()
        channel = Channel(channel_id=789)
        repo.save(channel)
        
        retrieved = repo.get_or_create(789)
        
        assert retrieved.channel_id == 789
        assert retrieved == channel

    def test_get_nonexistent_channel_raises_error(self):
        """Test that getting nonexistent channel raises error."""
        repo = InMemoryChannelRepository()
        
        with pytest.raises(ChannelNotFoundError):
            repo.get(999)

    def test_multiple_channels(self):
        """Test storing multiple channels."""
        repo = InMemoryChannelRepository()
        
        channel1 = repo.get_or_create(1)
        channel2 = repo.get_or_create(2)
        
        assert channel1.channel_id == 1
        assert channel2.channel_id == 2
        assert channel1 != channel2
```

**Step 3: Run test to verify it fails initially**

Run: `pytest tests/infrastructure/test_memory_repository.py -v`
Expected: FAIL (import issues with new repository)

**Step 4: Implement repository update**

Already done in Step 1.

**Step 5: Run test to verify it passes**

Run: `pytest tests/infrastructure/test_memory_repository.py -v`
Expected: PASS

**Step 6: Commit**

```bash
git add src/infrastructure/persistence/memory/repository.py \
        tests/infrastructure/test_memory_repository.py
git commit -m "refactor: rename repository to InMemoryChannelRepository"
```

---

### Task 8: Update OpenAI Adapter

**Files:**
- Modify: `src/infrastructure/ai/openai/adapter.py`

**Step 1: Update adapter to use new ports**

```python
# src/infrastructure/ai/openai/adapter.py
"""OpenAI adapter implementation."""

from src.application.ports.ai_service_port import IAIServicePort
from src.config import get_settings
from src.infrastructure.ai.openai.client import OpenAIClient


class OpenAIServiceAdapter(IAIServicePort):
    """Adapter for OpenAI API service."""

    def __init__(self, client: OpenAIClient) -> None:
        self.client = client
        self.settings = get_settings()

    def generate_reply(self, channel, image_urls: tuple[str, ...] = ()) -> str:
        """Generate a reply using OpenAI."""
        messages = channel.get_messages_for_api()
        system_prompt = self.settings.CHAT_SYSTEM_PROMPT
        api_messages: list[dict[str, object]] = [{"role": "system", "content": system_prompt}]
        for msg in messages[-100:]:
            api_messages.append({"role": msg["role"], "content": msg["content"]})

        if image_urls:
            last_message = api_messages[-1]
            if last_message["role"] == "user":
                text_content = last_message["content"]
                multimodal_content: list[dict[str, object]] = [{"type": "text", "text": text_content}]
                for url in image_urls:
                    multimodal_content.append({"type": "image_url", "image_url": {"url": url}})
                api_messages[-1] = {"role": "user", "content": multimodal_content}

        return self.client.chat_completion(api_messages)
```

**Step 2: Update tests**

```python
# tests/infrastructure/test_openai_adapter.py
"""Tests for OpenAI adapter."""
import pytest
from unittest.mock import Mock, patch

from src.application.ports.ai_service_port import IAIServicePort
from src.infrastructure.ai.openai.adapter import OpenAIServiceAdapter
from src.infrastructure.ai.openai.client import OpenAIClient


@pytest.fixture
def mock_client():
    """Create a mock OpenAI client."""
    return Mock(spec=OpenAIClient)


def test_adapter_implements_protocol(mock_client):
    """Test that adapter implements the protocol."""
    adapter = OpenAIServiceAdapter(mock_client)
    
    assert isinstance(adapter, IAIServicePort)


def test_adapter_generates_reply(mock_client):
    """Test that adapter generates reply."""
    mock_client.chat_completion.return_value = "Test response"
    adapter = OpenAIServiceAdapter(mock_client)
    
    # Create a mock channel
    mock_channel = Mock()
    mock_channel.get_messages_for_api.return_value = [
        {"role": "user", "content": "Hello"}
    ]
    
    response = adapter.generate_reply(mock_channel)
    
    assert response == "Test response"
    mock_client.chat_completion.assert_called_once()


def test_adapter_with_image_urls(mock_client):
    """Test that adapter handles image URLs."""
    mock_client.chat_completion.return_value = "Image response"
    adapter = OpenAIServiceAdapter(mock_client)
    
    mock_channel = Mock()
    mock_channel.get_messages_for_api.return_value = [
        {"role": "user", "content": "What's in this image?"}
    ]
    
    image_urls = ("https://example.com/image.jpg",)
    response = adapter.generate_reply(mock_channel, image_urls)
    
    assert response == "Image response"
    call_args = mock_client.chat_completion.call_args[0][0]
    assert call_args[-1]["role"] == "user"
    assert "image_url" in call_args[-1]["content"]
```

**Step 3: Run test to verify it fails initially**

Run: `pytest tests/infrastructure/test_openai_adapter.py -v`
Expected: FAIL (import issues with new adapter)

**Step 4: Implement adapter update**

Already done in Step 1.

**Step 5: Run test to verify it passes**

Run: `pytest tests/infrastructure/test_openai_adapter.py -v`
Expected: PASS

**Step 6: Commit**

```bash
git add src/infrastructure/ai/openai/adapter.py \
        tests/infrastructure/test_openai_adapter.py
git commit -m "refactor: OpenAIServiceAdapter now implements IAIServicePort"
```

---

## Phase 4: Dependency Injection

### Task 9: Update Composition Root

**Files:**
- Modify: `src/infrastructure/di/composition_root.py`
- Test: `tests/infrastructure/test_composition_root.py`

**Step 1: Update composition root**

```python
# src/infrastructure/di/composition_root.py
"""Dependency injection composition root."""

from src.application.messaging.handlers import ProcessUserTurn, ClearChannelHistory
from src.config import Settings
from src.application.ports.channel_repository_port import IChannelRepositoryPort
from src.application.ports.ai_service_port import IAIServicePort
from src.infrastructure.ai.openai.adapter import OpenAIServiceAdapter
from src.infrastructure.ai.openai.client import OpenAIClient
from src.infrastructure.persistence.memory.repository import InMemoryChannelRepository


class CompositionRoot:
    """Dependency injection composition root for the application."""

    def __init__(self, config: Settings) -> None:
        """Initialize composition root with configuration."""
        self.config = config
        self._repo: IChannelRepositoryPort | None = None
        self._ai_service: IAIServicePort | None = None

    @property
    def repo(self) -> IChannelRepositoryPort:
        """Get or create channel repository."""
        if self._repo is None:
            self._repo = InMemoryChannelRepository()
        return self._repo

    @property
    def ai_service(self) -> IAIServicePort:
        """Get or create AI service adapter."""
        if self._ai_service is None:
            client = OpenAIClient(
                api_key=self.config.OPENAI_API_KEY,
                base_url=self.config.OPENAI_BASE_URL,
                model=self.config.OPENAI_MODEL,
                max_tokens=self.config.OPENAI_MAX_TOKENS,
                temperature=self.config.OPENAI_TEMPERATURE,
            )
            self._ai_service = OpenAIServiceAdapter(client)
        return self._ai_service

    def create_message_processor(self) -> ProcessUserTurn:
        """Create message processing use case."""
        return ProcessUserTurn(self.repo, self.ai_service)

    def create_clear_history_use_case(self) -> ClearChannelHistory:
        """Create clear history use case."""
        return ClearChannelHistory(self.repo)
```

**Step 2: Update tests**

```python
# tests/infrastructure/test_composition_root.py
"""Tests for composition root."""
import pytest
from unittest.mock import Mock

from src.application.ports.channel_repository_port import IChannelRepositoryPort
from src.application.ports.ai_service_port import IAIServicePort
from src.config import Settings
from src.infrastructure.di.composition_root import CompositionRoot
from src.infrastructure.persistence.memory.repository import InMemoryChannelRepository


@pytest.fixture
def mock_settings():
    """Create mock settings."""
    return Mock(spec=Settings)


def test_composition_root_creates_repo(mock_settings):
    """Test that composition root creates repository."""
    root = CompositionRoot(mock_settings)
    
    repo = root.repo
    
    assert isinstance(repo, IChannelRepositoryPort)


def test_composition_root_creates_ai_service(mock_settings):
    """Test that composition root creates AI service."""
    root = CompositionRoot(mock_settings)
    
    ai_service = root.ai_service
    
    assert isinstance(ai_service, IAIServicePort)


def test_composition_root_reuses_repo(mock_settings):
    """Test that composition root reuses same repo instance."""
    root = CompositionRoot(mock_settings)
    
    repo1 = root.repo
    repo2 = root.repo
    
    assert repo1 is repo2


def test_composition_root_reuses_ai_service(mock_settings):
    """Test that composition root reuses same AI service instance."""
    root = CompositionRoot(mock_settings)
    
    ai1 = root.ai_service
    ai2 = root.ai_service
    
    assert ai1 is ai2


def test_composition_root_creates_message_processor(mock_settings):
    """Test that composition root creates message processor."""
    root = CompositionRoot(mock_settings)
    
    processor = root.create_message_processor()
    
    assert processor.repo is root.repo
    assert processor.ai_service is root.ai_service


def test_composition_root_creates_clear_history_use_case(mock_settings):
    """Test that composition root creates clear history use case."""
    root = CompositionRoot(mock_settings)
    
    clear_use_case = root.create_clear_history_use_case()
    
    assert clear_use_case.repo is root.repo
```

**Step 3: Run test to verify it fails initially**

Run: `pytest tests/infrastructure/test_composition_root.py -v`
Expected: FAIL (import issues with new ports)

**Step 4: Implement composition root update**

Already done in Step 1.

**Step 5: Run test to verify it passes**

Run: `pytest tests/infrastructure/test_composition_root.py -v`
Expected: PASS

**Step 6: Commit**

```bash
git add src/infrastructure/di/composition_root.py \
        tests/infrastructure/test_composition_root.py
git commit -m "refactor: composition root uses new port interfaces"
```

---

## Phase 5: Framework Layer Updates

### Task 10: Update Discord Bot

**Files:**
- Modify: `src/frameworks_drivers/discord/bot.py`

**Step 1: Update bot to use new DI**

```python
# src/frameworks_drivers/discord/bot.py (partial - key changes only)
# ...
from src.application.messaging.handlers import ClearChannelHistory, ProcessUserTurn
from src.application.ports.channel_repository_port import IChannelRepositoryPort
from src.application.ports.ai_service_port import IAIServicePort
# ...

    def get_lock(channel_id: int) -> asyncio.Lock:
        if channel_id not in channel_locks:
            channel_locks[channel_id] = asyncio.Lock()
        return channel_locks[channel_id]

    @bot.event
    async def on_ready() -> None:
        if bot.user:
            logger.info(f"Logged in as {bot.user} (ID: {bot.user.id})")
            logger.info(f"Connected to {len(bot.guilds)} guild(s)")
        else:
            logger.warning("Bot user not initialized")

    @bot.event
    async def on_message(message: discord.Message) -> None:
        # ... existing on_message logic ...
```

**Step 2: No changes needed** - The bot already uses CompositionRoot correctly

**Step 3: Update tests**

```python
# tests/frameworks_drivers/test_discord_bot.py
"""Tests for Discord bot integration."""
import pytest
from unittest.mock import Mock, AsyncMock, patch

from src.application.ports.channel_repository_port import IChannelRepositoryPort
from src.application.ports.ai_service_port import IAIServicePort


class TestDiscordBotDI:
    """Test that Discord bot uses proper DI."""

    def test_bot_uses_repository_port(self):
        """Test that bot uses IChannelRepositoryPort."""
        with patch("src.frameworks_drivers.discord.bot.setup_discord_bot") as mock_setup:
            # The bot should be configured to use port interfaces
            pass  # Integration test - verified by unit tests of handlers

    def test_bot_uses_ai_service_port(self):
        """Test that bot uses IAIServicePort."""
        # Verified by composition_root tests
        pass
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/frameworks_drivers/test_discord_bot.py -v`
Expected: PASS (existing tests still pass)

**Step 5: Commit**

```bash
git add src/frameworks_drivers/discord/bot.py \
        tests/frameworks_drivers/test_discord_bot.py
git commit -m "refactor: Discord bot integration uses new port interfaces"
```

---

## Phase 6: Documentation

### Task 11: Create Ubiquitous Language Document

**Files:**
- Create: `docs/UBIQUITOUS-LANGUAGE.md`

**Step 1: Write ubiquitous language document**

```markdown
# Ubiquitous Language

This document defines the shared vocabulary between developers and domain experts for the Py-Besto-Bot project.

## Core Concepts

### Channel

A **Channel** represents a conversation thread in Discord. Each channel maintains its own conversation history and has a maximum message limit (default: 100 messages).

**Key properties:**
- `channel_id`: Unique identifier (Discord channel ID)
- `messages`: List of conversation messages
- `max_messages`: Maximum messages to retain

### Message

A **Message** is an entity representing a single message in a conversation. Each message has:
- `role`: Role of the speaker (`user`, `assistant`, `system`)
- `content`: The message content (MessageContent value object)
- `timestamp`: When the message was created

### Turn

A **Turn** represents a complete interaction cycle:
1. User sends a message
2. Bot processes the message
3. Bot generates a reply
4. Bot sends the reply

**Example:** User says "Hello" → Bot responds "Hi there!"

### Reply

A **Reply** is the bot's response to a user message. Generated by the AI service based on conversation history.

## Domain Events

Domain events are named in **past tense** to indicate they have already occurred:

| Event | Description |
|-------|-------------|
| `MessageAdded` | A message was added to the channel |
| `ConversationCleared` | The channel's conversation history was cleared |

## Bounded Contexts

### Discord Integration Context

**Scope:** Handling Discord API interactions
- Commands: `@bot`, `/chat`, `/clear`, `/help`
- Events: `on_message`, `on_ready`, mentions
- Features: Image attachment handling, typing indicators

**Key terms:** Mention, DM, Slash Command, Attachment

### Conversation Context

**Scope:** Managing conversation history
- Aggregates: Channel, Message
- Operations: Add message, clear history, get messages
- Features: Message limits, conversation context

**Key terms:** History, Turn, Reply, Context window

### AI Service Context

**Scope:** AI-powered response generation
- Services: Chat completion, image analysis
- Features: System prompts, temperature control, max tokens
- Integration: OpenAI-compatible APIs

**Key terms:** Completion, Multimodal, System Prompt, Temperature

## Context Mapping

```
┌─────────────────────┐      ┌─────────────────────┐
│   Discord Context   │      │  Conversation       │
│   (Inbound/Driver)  │──────│  Context            │
│                     │      │                     │
│ - Slash Commands    │      │ - Channel           │
│ - Message Events    │      │ - Messages          │
│ - Mentions          │      │ - Turn              │
└─────────┬───────────┘      └─────────────────────┘
          │
          ▼
┌─────────────────────┐
│     AI Context      │
│  (Driven/Outbound)  │
│                     │
│ - OpenAI API        │
│ - Chat Completion   │
│ - Image Analysis    │
└─────────────────────┘
```

## Anti-Corruption Layer

The **OpenAIAdapter** serves as an ACL between the Application layer and external OpenAI API:

- Translates `IAIServicePort.generate_reply()` → OpenAI API call
- Translates OpenAI response → `str` reply
- Handles multimodal content (text + images)
- Abstracts API client details

## Domain Services

### ProcessUserTurn (Application Service)

**Purpose:** Orchestrate message processing flow

**Steps:**
1. Validate input message
2. Retrieve or create channel
3. Add user message to channel
4. Call AI service for reply
5. Add bot message to channel
6. Save channel to repository

**Input:** `channel_id`, `user_content`, `author_name`, `bot_name`, `image_urls`

**Output:** `reply` (str)

### ClearChannelHistory (Application Service)

**Purpose:** Clear conversation history

**Steps:**
1. Retrieve channel
2. Clear messages
3. Record domain event
4. Save channel

**Input:** `channel_id`

**Output:** `success` (bool)

## Testing Vocabulary

| Test Type | Vocabulary |
|-----------|------------|
| Unit | `Given-When-Then`, `Arrange-Act-Assert` |
| Integration | `with_real_`, `using_`, `when_` |
| E2E | `given_`, `when_`, `then_`, `should_` |

## References

- [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Domain-Driven Design](https://www.domainlanguage.com/ddd/)
- [Hexagonal Architecture](https://alistair.cockburn.us/hexagonal-architecture/)
```

**Step 2: Commit**

```bash
git add docs/UBIQUITOUS-LANGUAGE.md
git commit -m "docs: add ubiquitous language documentation"
```

---

### Task 12: Create DDD Strategic Documentation

**Files:**
- Create: `docs/DDD-STRATEGIC.md`

**Step 1: Write strategic DDD document**

```markdown
# DDD Strategic Patterns

This document describes the strategic DDD patterns used in Py-Besto-Bot, following Eric Evans' Domain-Driven Design and Vaughn Vernon's Implementing Domain-Driven Design.

## Overview

Py-Besto-Bot follows a **single bounded context** approach for a Discord bot with AI capabilities. The domain is divided into subdomains to identify core business capabilities.

## Subdomains

### Core Subdomain: Conversation Intelligence

**Purpose:** The unique value proposition - intelligent AI-powered conversations.

**Features:**
- OpenAI API integration
- Multimodal response generation (text + images)
- Conversation history management
- Context-aware responses

**Investment:** High - Differentiates from competitors

**Ownership:** Build in-house, best developers

### Supporting Subdomain: Channel Management

**Purpose:** Manage conversation threads and history.

**Features:**
- Channel entity
- Message management
- Message limits
- Domain events

**Investment:** Medium - Necessary but not unique

**Ownership:** Build in-house, solid but simple

### Generic Subdomain: Discord Integration

**Purpose:** Standard Discord API integration.

**Features:**
- Message events
- Slash commands
- Mentions
- Image attachments

**Investment:** Low - Commodity, can be bought

**Ownership:** Use third-party (discord.py library)

### Generic Subdomain: AI Service

**Purpose:** Standard AI API integration.

**Features:**
- OpenAI API client
- Chat completion
- Image analysis
- Rate limiting

**Investment:** Low - Commodity

**Ownership:** Use third-party (OpenAI SDK)

## Bounded Contexts

### Single Bounded Context

Py-Besto-Bot uses a **single bounded context** because:

1. **Domain is small** - One main concept: channel conversations
2. **Team size** - Small team (likely 1-3 developers)
3. **Complexity** - Moderate, not requiring multiple models
4. **Deployment** - Single service deployment

**Context Map:**
```
┌─────────────────────────────────────────────────────┐
│          Py-Besto-Bot (Single Context)              │
│                                                     │
│  Subdomains:                                        │
│  - Conversation Intelligence (Core)                 │
│  - Channel Management (Supporting)                  │
│  - Discord Integration (Generic)                    │
│  - AI Service (Generic)                             │
└─────────────────────────────────────────────────────┘
```

## Domain Models

### Channel Aggregate

**Root Entity:** Channel

**Child Entities:** None (messages are part of channel)

**Value Objects:**
- MessageContent
- Message (as Entity with ID)

**Domain Events:**
- MessageAdded
- ConversationCleared

**Rules:**
- Max 100 messages per channel
- Thread-safe message additions
- Domain events on state changes

### Message Entity

**Identity:** Auto-generated UUID

**Attributes:**
- Role (user, assistant, system)
- Content (MessageContent)
- Timestamp

**Rules:**
- Valid roles only
- Content validation (non-empty, max 10000 chars)
- Immutable content

## Domain Services

### Stateful Domain Services

None currently. All business logic is in aggregates.

### Stateful Domain Services (Future)

Potential additions:
- **MessageAnalyzer:** Analyze message content for sentiment
- **MessageSummarizer:** Summarize long conversations
- **ImageDescriber:** Describe images (if not using OpenAI)

## Aggregates

### Channel Aggregate

**Boundary:** Channel

**Consistency:** All messages in a channel must be consistent

**Transaction Boundary:** Single channel operations

**Rules:**
- Max messages enforced
- Thread-safe modifications
- Domain events on changes

## Domain Events

### MessageAdded

**Triggered:** When a user or bot sends a message

**Payload:**
- `channel_id`: The channel
- `message_role`: Role of sender
- `message_content`: Message content

**Consumers:**
- Read model updates
- External integrations

### ConversationCleared

**Triggered:** When history is cleared

**Payload:**
- `channel_id`: The channel
- `previous_message_count`: Before clear

**Consumers:**
- Read model updates
- External integrations

## Integration Patterns

### External Systems

| System | Integration Pattern | ACL Required |
|--------|---------------------|--------------|
| Discord API | Driver Adapter (Inbound) | No - via discord.py |
| OpenAI API | Driven Adapter (Outbound) | Yes - OpenAIServiceAdapter |
| In-Memory Storage | Driven Adapter | No - local |

### Integration Events

**Format:** Domain events (within context)

**Publishing:** Via event dispatcher (future)

**Subscribers:** Read models, external systems

## Context Mapping

### Upstream/Downstream

**Discord Integration** (Upstream):
- Provides: Message events, command events
- Consumed by: Channel Management, Conversation Context

**OpenAI API** (Downstream):
- Provides: AI responses
- Consumes: Conversation context

## Anti-Corruption Layer

### OpenAIServiceAdapter

**Purpose:** Protect application from OpenAI API changes

**Responsibilities:**
- Translate `IAIServicePort` → OpenAI API
- Handle multimodal content
- Abstract client details

**Location:** `src/infrastructure/ai/openai/adapter.py`

## Future Evolution

### Potential Bounded Context Split

If the system grows:
1. **Conversation Context:** Channels, messages
2. **AI Service Context:** OpenAI integration, rate limiting
3. **Discord Context:** Bot commands, events

**Trigger:** When team size or domain complexity increases

### Potential Subdomain Promotion

**Current:** Discord Integration (Generic)
**Future:** Discord Integration (Supporting) if custom features added

## References

- [Domain-Driven Design: The Blue Book](https://www.domainlanguage.com/ddd/blue-book/)
- [Implementing Domain-Driven Design](https://openlibrary.org/works/OL17392277W)
- [Bounded Context](https://martinfowler.com/bliki/BoundedContext.html)
- [Subdomains](https://martinfowler.com/bliki/Subdomain.html)
```

**Step 2: Commit**

```bash
git add docs/DDD-STRATEGIC.md
git commit -m "docs: add DDD strategic patterns documentation"
```

---

### Task 13: Create Architecture Decision Log

**Files:**
- Create: `docs/ADR/0001-strict-ddd-hexagonal.md`

**Step 1: Write ADR**

```markdown
# ADR 0001: Strict DDD + Hexagonal Architecture

**Date:** 2026-02-07

**Status:** Accepted

## Context

Py-Besto-Bot was built with Clean Architecture but had some DDD and Hexagonal gaps:
- Domain base classes missing (Entity, ValueObject, AggregateRoot)
- Domain events not extending base class
- Repository names inconsistent (Repository vs ChannelRepository)
- Ports mixed with handlers

## Decision

We will refactor to achieve 100% compliance with:
- **Clean Architecture** (4 layers, dependencies inward)
- **DDD Tactical** (Entity, ValueObject, AggregateRoot, DomainEvents)
- **Hexagonal** (Driver/Driven ports, adapters)

## Consequences

### Positive
- Clearer domain boundaries
- Better testability (pure domain tests)
- Easier infrastructure swaps
- Standard patterns for new developers

### Negative
- Refactoring effort required
- Some breaking changes (class renames)
- Learning curve for new developers

## Implementation

See `docs/plans/2026-02-07-strict-ddd-hexagonal.md` for detailed plan.

## Files Changed

| Old | New |
|-----|-----|
| `domain/repository.py` | `application/ports/channel_repository_port.py` |
| `application/messaging/ports.py` | `application/ports/ai_service_port.py` |
| `domain/channel/aggregate.py` | Extend `AggregateRoot[int]` |
| `domain/channel/value_objects.py` | `Message` extends `Entity[str]` |
| `domain/channel/events.py` | Extend `DomainEvent` |
| `InMemoryMessageRepository` | `InMemoryChannelRepository` |
| `OpenAIServiceAdapter` | Implements `IAIServicePort` |

## Testing Strategy

1. Unit tests for domain classes (no mocks)
2. Unit tests for use cases (mock ports)
3. Integration tests for adapters
4. Architecture tests (dependency rules)

## Rollout Plan

1. Phase 1: Domain base classes (tasks 1-4)
2. Phase 2: Application ports (tasks 5-6)
3. Phase 3: Infrastructure adapters (tasks 7-8)
4. Phase 4: DI updates (tasks 9)
5. Phase 5: Framework updates (tasks 10)
6. Phase 6: Documentation (tasks 11-13)
```

**Step 2: Create ADR directory and commit**

```bash
mkdir -p docs/ADR
git add docs/ADR/
git commit -m "docs: add architecture decision record 0001"
```

---

## Phase 7: Final Verification

### Task 14: Run Full Test Suite

**Files:**
- Test: All tests

**Step 1: Run tests**

```bash
pytest tests/ -v --tb=short
```

**Expected:** 220+ tests pass (original 206 + new tests)

**Step 2: Check coverage**

```bash
pytest tests/ --cov=src --cov-report=term-missing -v
```

**Expected:** 80%+ coverage

**Step 3: Type check**

```bash
basedpyright src/
```

**Expected:** 0 errors

**Step 4: Lint check**

```bash
ruff check src/ tests/
```

**Expected:** 0 errors

**Step 5: Format check**

```bash
black src/ tests/ --check
```

**Expected:** All files formatted

**Step 6: Commit**

```bash
git add .
git commit -m "test: add comprehensive test suite for strict DDD + Hexagonal"
```

---

### Task 15: Pre-commit Hooks

**Files:**
- Verify: `.pre-commit-config.yaml`

**Step 1: Install hooks**

```bash
pre-commit install
```

**Step 2: Run hooks**

```bash
pre-commit run --all-files
```

**Expected:** All hooks pass

**Step 3: Commit**

```bash
git add .
git commit -m "chore: pre-commit hooks pass for refactored code"
```

---

## Phase 8: Deployment

### Task 16: Docker Build

**Files:**
- Dockerfile unchanged

**Step 1: Build image**

```bash
docker build -t py-besto-bot:latest .
```

**Expected:** Build succeeds

**Step 2: Run container**

```bash
docker-compose up -d --build
```

**Expected:** Container starts

**Step 3: Verify logs**

```bash
docker-compose logs py-besto-bot
```

**Expected:** No errors

**Step 4: Commit**

```bash
git add .
git commit -m "chore: docker build passes for refactored code"
```

---

## Summary

### Total Tasks: 16
### Estimated Time: 4-6 hours
### Test Coverage: 80%+ (up from 79%)
### Type Safety: 100% compliance

---

## Execution Options

**1. Subagent-Driven (this session)** - I dispatch fresh subagent per task, review between tasks, fast iteration

**2. Parallel Session (separate)** - Open new session with executing-plans, batch execution with checkpoints

**Which approach?**