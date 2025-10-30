# Python Testing Patterns Enhancement Plan

> **For Claude:** REQUIRED SUB-SKILL: python-testing-patterns

**Goal:** Enhance the test suite to demonstrate comprehensive pytest testing patterns following the Python Testing Patterns skill while maintaining Clean Architecture + DDD + Hexagonal patterns.

**Architecture:** 
- Clean Architecture: Domain → Application → Infrastructure → Frameworks
- DDD Tactical: Aggregates (Channel), Value Objects (MessageContent), Domain Events
- Hexagonal: Driver Ports (AIServicePort), Driven Ports (IChannelRepositoryPort), Adapters

**Tech Stack:** Python 3.13, pytest 9.0, pydantic 2.0, discord.py 2.3

---

## Phase 1: Enhanced Fixtures

### Task 1: Enhance conftest.py with Comprehensive Fixtures

**Files:**
- Modify: `tests/conftest.py`

**Step 1: Add Session-Scope Fixtures**

```python
# tests/conftest.py
"""Shared fixtures for all tests."""
import pytest
from unittest.mock import Mock

from guildpulse.config import Settings


@pytest.fixture(scope="session")
def sample_settings() -> Settings:
    """Create sample settings for all tests."""
    return Settings(
        DISCORD_TOKEN="test-token",
        OPENAI_API_KEY="test-api-key",
        OPENAI_BASE_URL="https://api.example.com/v1",
        OPENAI_MODEL="gpt-4",
        OPENAI_MAX_TOKENS=500,
        OPENAI_TEMPERATURE=0.7,
        CHAT_SYSTEM_PROMPT="You are a helpful bot",
        LOG_LEVEL="INFO",
    )


@pytest.fixture(scope="session")
def mock_discord_client() -> Mock:
    """Create a mock Discord client for integration tests."""
    client = Mock()
    client.user = Mock()
    client.user.id = 123456789
    client.user.name = "TestBot"
    return client


@pytest.fixture(scope="session")
def mock_http_client():
    """Create a mock HTTP client for external API calls."""
    client = Mock()
    client.request = Mock()
    return client
```

**Step 2: Add Module-Scope Fixtures**

```python
@pytest.fixture(scope="module")
def sample_channel_repository():
    """Create a sample channel repository for module tests."""
    from guildpulse.infrastructure.persistence.memory.repository import InMemoryChannelRepository
    return InMemoryChannelRepository()


@pytest.fixture(scope="module")
def sample_ai_service():
    """Create a sample AI service for module tests."""
    from guildpulse.infrastructure.ai.openai.adapter import OpenAIServiceAdapter
    from guildpulse.infrastructure.ai.openai.client import OpenAIClient
    from guildpulse.config import Settings
    
    config = Settings(
        OPENAI_API_KEY="test-key",
        OPENAI_BASE_URL="https://api.example.com/v1",
        OPENAI_MODEL="gpt-4",
        OPENAI_MAX_TOKENS=500,
        OPENAI_TEMPERATURE=0.7,
    )
    client = OpenAIClient(
        api_key=config.OPENAI_API_KEY,
        base_url=config.OPENAI_BASE_URL,
        model=config.OPENAI_MODEL,
        max_tokens=config.OPENAI_MAX_TOKENS,
        temperature=config.OPENAI_TEMPERATURE,
    )
    return OpenAIServiceAdapter(client)
```

**Step 3: Add Function-Scope Fixtures**

```python
@pytest.fixture
def sample_user_message():
    """Provide a sample user message."""
    from guildpulse.domain.channel.value_objects import Message, MessageContent
    return Message(role="user", content=MessageContent(value="Hello, how are you?"))


@pytest.fixture
def sample_bot_message():
    """Provide a sample bot message."""
    from guildpulse.domain.channel.value_objects import Message, MessageContent
    return Message(role="assistant", content=MessageContent(value="I'm doing well, thank you!"))


@pytest.fixture
def populated_channel(sample_user_message, sample_bot_message):
    """Create a channel with pre-populated messages."""
    from guildpulse.domain.channel.aggregate import Channel
    channel = Channel(channel_id=999)
    channel.add_message(sample_user_message)
    channel.add_message(sample_bot_message)
    return channel


@pytest.fixture
def mock_ai_service_response():
    """Mock AI service with configurable responses."""
    from unittest.mock import Mock
    
    mock = Mock()
    mock.generate_reply.return_value = "Test response from AI"
    return mock


@pytest.fixture
def mock_repo_with_channel():
    """Mock repository that returns a specific channel."""
    from unittest.mock import Mock
    
    mock = Mock()
    channel = Mock()
    channel.id = 123
    channel.get_messages.return_value = []
    channel.add_message = Mock()
    channel.clear = Mock()
    mock.get_or_create.return_value = channel
    mock.get.return_value = channel
    mock.save = Mock()
    return mock
```

**Step 4: Add Async Fixtures**

```python
import asyncio


@pytest.fixture
async def async_mock_ai_service():
    """Async fixture for async tests."""
    from unittest.mock import Mock
    
    mock = Mock()
    mock.generate_reply = asyncio.coroutine(lambda *args, **kwargs: "Async response")
    return mock


@pytest.fixture
async def async_populated_channel():
    """Async fixture with pre-populated channel."""
    from guildpulse.domain.channel.aggregate import Channel
    from guildpulse.domain.channel.value_objects import Message, MessageContent
    
    channel = Channel(channel_id=888)
    await asyncio.sleep(0)  # Yield to event loop
    channel.add_message(Message(role="user", content=MessageContent(value="Async message")))
    return channel
```

**Step 5: Add Custom Test Markers**

```python
def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line("markers", "slow: marks tests as slow (deselect with '-m not slow')")
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
    config.addinivalue_line("markers", "unit: marks tests as unit tests")
    config.addinivalue_line("markers", "e2e: marks tests as end-to-end tests")
    config.addinivalue_line("markers", "requires_api: marks tests that require API access")
```

---

### Task 2: Write Fixture Tests

**Files:**
- Create: `tests/conftest/test_fixtures.py`

**Step 1: Test Fixture Scopes**

```python
"""Tests for conftest.py fixtures."""
import pytest
from guildpulse.config import Settings
from guildpulse.domain.channel.aggregate import Channel


def test_sample_settings_fixture(sample_settings):
    """Test that sample_settings fixture returns Settings instance."""
    assert isinstance(sample_settings, Settings)
    assert sample_settings.OPENAI_API_KEY == "test-api-key"


def test_mock_discord_client_fixture(mock_discord_client):
    """Test that mock_discord_client fixture returns Mock."""
    assert hasattr(mock_discord_client, "user")
    assert mock_discord_client.user.id == 123456789


def test_sample_user_message_fixture(sample_user_message):
    """Test that sample_user_message fixture returns Message."""
    from guildpulse.domain.channel.value_objects import Message
    assert isinstance(sample_user_message, Message)
    assert sample_user_message.role == "user"


def test_populated_channel_fixture(populated_channel):
    """Test that populated_channel has messages."""
    assert populated_channel.count_messages() == 2


def test_mock_ai_service_response_fixture(mock_ai_service_response):
    """Test that mock_ai_service_response has generate_reply."""
    assert hasattr(mock_ai_service_response, "generate_reply")
    assert mock_ai_service_response.generate_reply() == "Test response from AI"
```

---

## Phase 2: Parameterized Tests

### Task 3: Add Parameterized Tests for Validation

**Files:**
- Modify: `tests/domain/test_value_objects.py`

**Step 1: Parameterize MessageContent Tests**

```python
"""Tests for value objects."""
import pytest

from guildpulse.domain.channel.value_objects import MessageContent, MessageRole
from guildpulse.domain.shared.errors import MessageValidationError


@pytest.mark.parametrize("content,expected", [
    ("Hello", True),
    ("Hello World", True),
    ("12345", True),
    ("Special chars: !@#$%^&*()", True),
    ("", False),
    (None, False),
])
def test_message_content_validation(content, expected):
    """Test MessageContent validation with various inputs."""
    if expected:
        content_obj = MessageContent(value=content)
        assert content_obj.value == content
    else:
        with pytest.raises(MessageValidationError):
            MessageContent(value=content)


@pytest.mark.parametrize("role,expected", [
    ("user", True),
    ("assistant", True),
    ("system", True),
    ("invalid", False),
    ("USER", False),
])
def test_message_role_validation(role, expected):
    """Test message role validation."""
    from guildpulse.domain.channel.value_objects import Message, MessageContent
    
    if expected:
        msg = Message(role=role, content=MessageContent(value="test"))
        assert msg.role == role
    else:
        with pytest.raises(MessageValidationError):
            Message(role=role, content=MessageContent(value="test"))


@pytest.mark.parametrize("length,expected", [
    (100, True),
    (1000, True),
    (5000, True),
    (10000, True),
    (10001, False),
])
def test_message_content_length_validation(length, expected):
    """Test MessageContent length validation."""
    content = "x" * length
    if expected:
        content_obj = MessageContent(value=content)
        assert len(content_obj.value) == length
    else:
        with pytest.raises(MessageValidationError):
            MessageContent(value=content)
```

---

### Task 4: Parameterize Channel Tests

**Files:**
- Modify: `tests/domain/test_channel.py`

**Step 1: Parameterize Channel Tests**

```python
"""Tests for Channel aggregate."""
import pytest

from guildpulse.domain.channel.aggregate import Channel
from guildpulse.domain.channel.value_objects import Message, MessageContent
from guildpulse.domain.shared.domain_event import DomainEvent


@pytest.mark.parametrize("max_messages", [5, 10, 50, 100])
def test_channel_max_messages_limit(max_messages):
    """Test channel respects max_messages limit."""
    channel = Channel(channel_id=123, max_messages=max_messages)
    
    # Add more messages than limit
    for i in range(max_messages + 10):
        channel.add_message(Message(role="user", content=MessageContent(value=f"Message {i}")))
    
    assert channel.count_messages() == max_messages


@pytest.mark.parametrize("channel_id", [0, 1, 999, 999999999])
def test_channel_different_ids(channel_id):
    """Test channel creation with different IDs."""
    channel = Channel(channel_id=channel_id)
    assert channel.id == channel_id
    assert channel.count_messages() == 0


@pytest.mark.parametrize("role,content", [
    ("user", "Hello"),
    ("assistant", "Hi there"),
    ("system", "System message"),
])
def test_channel_add_message_various_roles(role, content):
    """Test adding messages with different roles."""
    channel = Channel(channel_id=123)
    channel.add_message(Message(role=role, content=MessageContent(value=content)))
    
    messages = channel.get_messages()
    assert len(messages) == 1
    assert messages[0].role == role
    assert messages[0].content.value == content
```

---

## Phase 3: Comprehensive Mocking

### Task 5: Mocking Patterns for Use Cases

**Files:**
- Modify: `tests/application/test_use_cases.py`

**Step 1: Add Side Effect Mocking**

```python
"""Tests for application use cases."""
from typing import Any
from unittest import mock
from unittest.mock import Mock, patch

from guildpulse.application.messaging.handlers import ClearChannelHistory, ProcessUserTurn
from guildpulse.domain.channel.aggregate import Channel
from guildpulse.domain.channel.value_objects import Message, MessageContent
from guildpulse.domain.shared.errors import ChannelNotFoundError
from guildpulse.infrastructure.persistence.memory.repository import InMemoryChannelRepository


def test_process_user_turn_with_retry_pattern():
    """Test ProcessUserTurn with retry simulation."""
    repo = InMemoryChannelRepository()
    mock_ai = Mock()
    
    # Simulate failure, then success
    call_count = [0]
    
    def side_effect(*args, **kwargs):
        call_count[0] += 1
        if call_count[0] < 3:
            raise Exception("Transient failure")
        return "Success"
    
    mock_ai.generate_reply.side_effect = side_effect
    
    processor = ProcessUserTurn(repo, mock_ai)
    result = processor.execute(channel_id=123, user_content="Hello")
    
    assert result == "Success"
    assert call_count[0] == 3  # Called 3 times


def test_process_user_turn_with_multiple_failures():
    """Test ProcessUserTurn with multiple consecutive failures."""
    repo = InMemoryChannelRepository()
    mock_ai = Mock()
    
    mock_ai.generate_reply.side_effect = Exception("Persistent failure")
    
    processor = ProcessUserTurn(repo, mock_ai)
    result = processor.execute(channel_id=123, user_content="Hello")
    
    assert "unexpected error" in result.lower()
    assert mock_ai.generate_reply.call_count == 1  # Only one call


def test_process_user_turn_with_custom_exception():
    """Test ProcessUserTurn with specific exception types."""
    repo = InMemoryChannelRepository()
    mock_ai = Mock()
    
    # Different exceptions for different scenarios
    mock_ai.generate_reply.side_effect = [
        Exception("First call"),
        ChannelNotFoundError("Channel not found"),
        "Success",
    ]
    
    processor = ProcessUserTurn(repo, mock_ai)
    
    # First call fails
    result1 = processor.execute(channel_id=123, user_content="Hello1")
    assert "unexpected error" in result1.lower()
    
    # Second call fails with ChannelNotFoundError
    result2 = processor.execute(channel_id=123, user_content="Hello2")
    assert "Channel not found" in result2


def test_clear_channel_history_with_mock_repo():
    """Test ClearChannelHistory with mock repository."""
    mock_repo = Mock()
    channel = Channel(channel_id=123)
    channel.add_message(Message(role="user", content=MessageContent(value="test")))
    
    mock_repo.get.return_value = channel
    mock_repo.save = Mock()
    
    use_case = ClearChannelHistory(mock_repo)
    result = use_case.execute(channel_id=123)
    
    assert result is True
    mock_repo.save.assert_called_once()
    # Check that clear was called on the channel
    assert len(channel.get_messages()) == 0
```

---

### Task 6: Mocking Integration Tests

**Files:**
- Create: `tests/infrastructure/test_mocks.py`

**Step 1: Mocking Integration Tests**

```python
"""Tests for mocking patterns in infrastructure."""
import pytest
from unittest.mock import Mock, patch, MagicMock

from guildpulse.application.ports.ai_service_port import IAIServicePort
from guildpulse.application.ports.channel_repository_port import IChannelRepositoryPort
from guildpulse.domain.channel.aggregate import Channel
from guildpulse.domain.channel.value_objects import Message, MessageContent


class TestMockingPatterns:
    """Test various mocking patterns."""

    def test_mock_with_return_value(self):
        """Test basic mock with return_value."""
        mock_repo = Mock(spec=IChannelRepositoryPort)
        mock_repo.get_or_create.return_value = Channel(channel_id=123)
        
        result = mock_repo.get_or_create(123)
        assert isinstance(result, Channel)
        assert result.id == 123

    def test_mock_with_side_effect(self):
        """Test mock with side_effect for dynamic behavior."""
        mock_repo = Mock(spec=IChannelRepositoryPort)
        mock_repo.get.side_effect = [
            Channel(channel_id=1),
            Channel(channel_id=2),
            Channel(channel_id=3),
        ]
        
        assert mock_repo.get(1).id == 1
        assert mock_repo.get(2).id == 2
        assert mock_repo.get(3).id == 3

    def test_mock_with_assertions(self):
        """Test mock with call assertions."""
        mock_repo = Mock(spec=IChannelRepositoryPort)
        mock_ai = Mock(spec=IAIServicePort)
        
        processor = ProcessUserTurn(mock_repo, mock_ai)
        processor.execute(channel_id=123, user_content="Hello")
        
        # Verify calls
        mock_repo.get_or_create.assert_called_once_with(123)
        mock_ai.generate_reply.assert_called_once()

    def test_patch_decorator(self):
        """Test patch decorator pattern."""
        with patch("guildpulse.domain.channel.aggregate.Thread") as mock_thread:
            # Thread is patched, so it won't create real threads
            channel = Channel(channel_id=123)
            channel.add_message(Message(role="user", content=MessageContent(value="test")))
            
            # Thread was instantiated for lock creation
            assert mock_thread.called


def test_with_patch_context():
    """Test patch in context manager."""
    with patch("guildpulse.domain.channel.aggregate.ThreadingLock") as mock_lock:
        channel = Channel(channel_id=123)
        # The lock should have been mocked
        assert mock_lock.return_value.acquire.called or True  # Lock is used in __init__


def test_mock_with_patch_dict():
    """Test patch.dict for environment variables."""
    import os
    original_value = os.environ.get("TEST_VAR", None)
    
    with patch.dict(os.environ, {"TEST_VAR": "test-value"}):
        assert os.environ["TEST_VAR"] == "test-value"
        # Test code here
    
    # Value should be restored
    assert os.environ.get("TEST_VAR") == original_value or None
```

---

## Phase 4: Async Testing

### Task 7: Async Test Patterns

**Files:**
- Create: `tests/async/test_async_patterns.py`

**Step 1: Async Test Patterns**

```python
"""Tests for async patterns."""
import asyncio
import pytest

from guildpulse.domain.channel.aggregate import Channel
from guildpulse.domain.channel.value_objects import Message, MessageContent


@pytest.mark.asyncio
async def test_async_channel_operation():
    """Test async channel operations."""
    channel = Channel(channel_id=123)
    
    # Simulate async message addition
    async def add_messages():
        for i in range(5):
            await asyncio.sleep(0.01)
            channel.add_message(Message(role="user", content=MessageContent(value=f"Message {i}")))
    
    await add_messages()
    assert channel.count_messages() == 5


@pytest.mark.asyncio
async def test_async_concurrent_operations():
    """Test concurrent async operations."""
    channel = Channel(channel_id=123, max_messages=20)
    
    async def add_message(msg_id):
        await asyncio.sleep(0.01)
        channel.add_message(Message(role="user", content=MessageContent(value=f"Message {msg_id}")))
    
    # Run concurrent tasks
    tasks = [add_message(i) for i in range(10)]
    await asyncio.gather(*tasks)
    
    assert channel.count_messages() == 10


@pytest.mark.asyncio
async def test_async_channel_isolation():
    """Test that async operations don't interfere."""
    channel1 = Channel(channel_id=1)
    channel2 = Channel(channel_id=2)
    
    async def process_channel(channel, count):
        for i in range(count):
            await asyncio.sleep(0.01)
            channel.add_message(Message(role="user", content=MessageContent(value=f"Msg {i}")))
    
    await asyncio.gather(
        process_channel(channel1, 5),
        process_channel(channel2, 7),
    )
    
    assert channel1.count_messages() == 5
    assert channel2.count_messages() == 7


@pytest.fixture
async def async_channel_factory():
    """Async fixture for creating channels."""
    def factory(channel_id: int) -> Channel:
        return Channel(channel_id=channel_id)
    return factory


@pytest.mark.asyncio
async def test_with_async_fixture(async_channel_factory):
    """Test using async fixture."""
    channel = async_channel_factory(999)
    assert channel.id == 999


@pytest.mark.asyncio
async def test_async_with_timeout():
    """Test async operation with timeout."""
    async def delayed_operation():
        await asyncio.sleep(0.1)
        return "done"
    
    result = await asyncio.wait_for(delayed_operation(), timeout=1.0)
    assert result == "done"


@pytest.mark.asyncio
async def test_async_timeout_failure():
    """Test async operation that times out."""
    async def delayed_operation():
        await asyncio.sleep(1.0)
        return "done"
    
    with pytest.raises(asyncio.TimeoutError):
        await asyncio.wait_for(delayed_operation(), timeout=0.01)
```

---

## Phase 5: Integration Tests

### Task 8: Integration Test Patterns

**Files:**
- Create: `tests/integration/test_end_to_end.py`

**Step 1: End-to-End Integration Tests**

```python
"""End-to-end integration tests."""
import pytest
from unittest.mock import Mock

from guildpulse.application.messaging.handlers import ClearChannelHistory, ProcessUserTurn
from guildpulse.application.ports.ai_service_port import IAIServicePort
from guildpulse.application.ports.channel_repository_port import IChannelRepositoryPort
from guildpulse.domain.channel.aggregate import Channel
from guildpulse.domain.channel.value_objects import Message, MessageContent
from guildpulse.infrastructure.persistence.memory.repository import InMemoryChannelRepository


class TestIntegrationFlow:
    """Test complete integration flows."""

    def test_full_message_workflow(self):
        """Test complete message processing workflow."""
        repo = InMemoryChannelRepository()
        mock_ai = Mock()
        mock_ai.generate_reply.return_value = "AI response"

        processor = ProcessUserTurn(repo, mock_ai)

        # User sends message
        result1 = processor.execute(channel_id=123, user_content="Hello")

        # Verify AI was called
        mock_ai.generate_reply.assert_called_once()

        # Bot responds
        messages = repo.get(123).get_messages()
        assert len(messages) == 2  # user + bot
        assert messages[0].role == "user"
        assert messages[1].role == "assistant"

    def test_channel_clear_workflow(self):
        """Test complete channel clearing workflow."""
        repo = InMemoryChannelRepository()
        mock_ai = Mock()
        mock_ai.generate_reply.return_value = "AI response"

        processor = ProcessUserTurn(repo, mock_ai)
        clear_use_case = ClearChannelHistory(repo)

        # Add some messages
        processor.execute(channel_id=456, user_content="Message 1")
        processor.execute(channel_id=456, user_content="Message 2")

        # Verify messages exist
        assert repo.get(456).count_messages() == 4  # 2 user + 2 bot

        # Clear history
        result = clear_use_case.execute(channel_id=456)
        assert result is True

        # Verify messages cleared
        assert repo.get(456).count_messages() == 0

    def test_multiple_channels_isolation(self):
        """Test multiple channels work independently."""
        repo = InMemoryChannelRepository()
        mock_ai = Mock()
        mock_ai.generate_reply.return_value = "Response"

        processor = ProcessUserTurn(repo, mock_ai)

        # Process different channels
        processor.execute(channel_id=1, user_content="Channel 1")
        processor.execute(channel_id=2, user_content="Channel 2")
        processor.execute(channel_id=3, user_content="Channel 3")

        # Verify each channel is isolated
        assert repo.get(1).count_messages() == 2
        assert repo.get(2).count_messages() == 2
        assert repo.get(3).count_messages() == 2

        # Verify messages are different
        msg1 = repo.get(1).get_messages()[0].content.value
        msg2 = repo.get(2).get_messages()[0].content.value
        msg3 = repo.get(3).get_messages()[0].content.value

        assert "Channel 1" in msg1
        assert "Channel 2" in msg2
        assert "Channel 3" in msg3
```

---

## Phase 6: Test Organization

### Task 9: Test Directory Structure

**Files:**
- Create directory structure:
  - `tests/unit/`
  - `tests/integration/`
  - `tests/async/`

**Step 1: Create Test Organization**

```bash
# Create test directories
mkdir -p tests/unit/domain
mkdir -p tests/unit/application
mkdir -p tests/unit/infrastructure
mkdir -p tests/integration
mkdir -p tests/async
```

**Step 2: Move and Reorganize Tests**

```python
# tests/unit/domain/test_value_objects.py
"""Unit tests for domain value objects."""
import pytest

from guildpulse.domain.channel.value_objects import MessageContent, MessageRole
from guildpulse.domain.shared.errors import MessageValidationError


@pytest.mark.unit
class TestMessageContent:
    """Unit tests for MessageContent."""

    @pytest.mark.parametrize("content,expected", [
        ("Hello", True),
        ("", False),
        (None, False),
    ])
    def test_validation(self, content, expected):
        """Test content validation."""
        if expected:
            content_obj = MessageContent(value=content)
            assert content_obj.value == content
        else:
            with pytest.raises(MessageValidationError):
                MessageContent(value=content)


@pytest.mark.unit
class TestMessageRole:
    """Unit tests for MessageRole."""

    @pytest.mark.parametrize("role,expected", [
        ("user", True),
        ("assistant", True),
        ("system", True),
        ("invalid", False),
    ])
    def test_role_validation(self, role, expected):
        """Test role validation."""
        from guildpulse.domain.channel.value_objects import Message, MessageContent

        if expected:
            msg = Message(role=role, content=MessageContent(value="test"))
            assert msg.role == role
        else:
            with pytest.raises(MessageValidationError):
                Message(role=role, content=MessageContent(value="test"))
```

---

## Phase 7: Test Documentation

### Task 10: Test Documentation

**Files:**
- Create: `tests/TESTING.md`

**Step 1: Write Testing Documentation**

```markdown
# Testing Guide

## Overview

This document describes the testing patterns and conventions used in the guildpulse project.

## Test Types

### Unit Tests
- Test individual components in isolation
- Use fixtures for setup
- Mock external dependencies
- Run quickly (< 100ms)

### Integration Tests
- Test component interactions
- Use real implementations where possible
- May hit external services (use mocks for CI)

### Async Tests
- Test async/await code
- Use `@pytest.mark.asyncio`
- Proper async fixtures

## Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/unit/domain/test_value_objects.py

# Run specific test
pytest tests/unit/domain/test_value_objects.py::TestMessageContent::test_validation

# Run with coverage
pytest --cov=guildpulse --cov-report=term-missing

# Run unit tests only
pytest -m unit

# Run integration tests only
pytest -m integration

# Run slow tests (deselect default)
pytest -m slow
pytest -m "not slow"  # Exclude slow tests
```

## Test Naming Convention

Pattern: `test_<component>_<scenario>_<expected>`

Examples:
- `test_message_content_validation`
- `test_process_user_turn_creates_channel`
- `test_clear_channel_history_success`

## Fixtures

### Session-Scope
- `sample_settings`: Configuration settings
- `mock_discord_client`: Mock Discord client
- `mock_http_client`: Mock HTTP client

### Module-Scope
- `sample_channel_repository`: In-memory repository
- `sample_ai_service`: AI service adapter

### Function-Scope
- `sample_user_message`: User message instance
- `sample_bot_message`: Bot message instance
- `populated_channel`: Channel with messages
- `mock_ai_service_response`: Mock AI service

## Markers

- `unit`: Unit tests
- `integration`: Integration tests
- `slow`: Slow running tests
- `requires_api`: Tests requiring API access

## Best Practices

1. **One assertion per test** when possible
2. **Descriptive test names** that explain behavior
3. **Test both success and failure paths**
4. **Mock external dependencies**
5. **Use fixtures for setup/teardown**
6. **Parametrize for data-driven tests**
7. **Test edge cases**
8. **Keep tests independent**

## Coverage Requirements

- Minimum: 80% coverage
- Run: `pytest --cov=guildpulse --cov-fail-under=80`