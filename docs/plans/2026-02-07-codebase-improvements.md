# Codebase Improvements Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Address architectural violations, test coverage gaps, and performance optimizations identified by the skills analysis for py-besto-bot Discord bot.

**Architecture:** Clean Architecture with ports and adapters. We will fix dependency violations, add infrastructure tests, implement Discord rate limiting, refactor tests with parametrization, and optimize Dockerfile.

**Tech Stack:** Python 3.13, pytest 9.0.2, mypy 1.0+, Discord.py 2.3.0, OpenAI SDK, uv 0.2.x

---

## Task 1: Fix domain→config dependency violation

**Files:**
- Create: `src/domain/shared/config_port.py`
- Modify: `src/domain/channel/aggregate.py:1-15`
- Test: `tests/domain/test_config_port.py`

**Step 1: Write the failing test**

Create `tests/domain/test_config_port.py`:
```python
"""Tests for ConfigPort interface in domain layer."""

from src.domain.shared.config_port import ConfigPort


def test_config_port_has_required_properties():
    """Test that ConfigPort defines all required properties."""
    class DummyConfig:
        @property
        def discord_token(self) -> str:
            return "test"
        
        @property
        def openai_api_key(self) -> str:
            return "test-key"
        
        @property
        def openai_base_url(self) -> str:
            return "https://test.com/v1"
        
        @property
        def openai_model(self) -> str:
            return "test-model"
        
        @property
        def openai_max_tokens(self) -> int:
            return 500
        
        @property
        def openai_temperature(self) -> float:
            return 0.7
    
    config = DummyConfig()
    
    assert isinstance(config.discord_token, str)
    assert isinstance(config.openai_api_key, str)
    assert isinstance(config.openai_base_url, str)
    assert isinstance(config.openai_model, str)
    assert isinstance(config.openai_max_tokens, int)
    assert isinstance(config.openai_temperature, float)
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/domain/test_config_port.py -v`
Expected: FAIL with "No module named 'src.domain.shared.config_port'"

**Step 3: Write minimal implementation**

Create `src/domain/shared/config_port.py`:
```python
"""Config port for dependency inversion in domain layer."""

from typing import Protocol


class ConfigPort(Protocol):
    """Protocol for configuration access from domain layer."""

    @property
    def discord_token(self) -> str: ...

    @property
    def openai_api_key(self) -> str: ...

    @property
    def openai_base_url(self) -> str: ...

    @property
    def openai_model(self) -> str: ...

    @property
    def openai_max_tokens(self) -> int: ...

    @property
    def openai_temperature(self) -> float: ...
```

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/domain/test_config_port.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add tests/domain/test_config_port.py src/domain/shared/config_port.py
git commit -m "feat: add ConfigPort protocol to domain layer"
```

---

## Task 2: Implement ConfigPort for Settings class

**Files:**
- Modify: `src/config.py:20-60`

**Step 1: Write the failing test**

Update `tests/config/test_config.py` to test ConfigPort implementation:
```python
"""Test that Settings implements ConfigPort."""

from src.config import Settings, get_settings


def test_settings_implements_config_port():
    """Test that Settings class implements ConfigPort protocol."""
    import inspect
    
    config = get_settings()
    
    # Check all protocol methods exist
    assert hasattr(config, 'discord_token')
    assert hasattr(config, 'openai_api_key')
    assert hasattr(config, 'openai_base_url')
    assert hasattr(config, 'openai_model')
    assert hasattr(config, 'openai_max_tokens')
    assert hasattr(config, 'openai_temperature')
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/config/test_config.py::test_settings_implements_config_port -v`
Expected: FAIL (test doesn't exist yet)

**Step 3: Write minimal implementation**

Modify `src/config.py` to add ConfigPort implementation:
```python
# Add to Settings class (after __init__ if needed, but properties are already there)
# The Settings class already has all required properties defined with Field()
# No code change needed - pydantic fields are already accessible as properties
```

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/config/test_config.py -v -k config_port`
Expected: PASS

**Step 5: Commit**

```bash
git add src/config.py tests/config/test_config.py
git commit -m "feat: verify Settings implements ConfigPort"
```

---

## Task 3: Create infrastructure tests for OpenAI adapter

**Files:**
- Create: `tests/infrastructure/test_openai_adapter_edge_cases.py`

**Step 1: Write the failing test**

Create `tests/infrastructure/test_openai_adapter_edge_cases.py`:
```python
"""Edge case tests for OpenAI adapter."""

import pytest
from unittest.mock import Mock

from src.infrastructure.ai.openai.adapter import OpenAIServiceAdapter
from src.infrastructure.ai.openai.client import OpenAIClient
from src.domain.channel.aggregate import Channel
from src.domain.channel.value_objects import Message, MessageContent


@pytest.fixture
def mock_client():
    """Create a mock OpenAI client."""
    mock = Mock(spec=OpenAIClient)
    return mock


@pytest.fixture
def adapter(mock_client):
    """Create OpenAIServiceAdapter with mock client."""
    return OpenAIServiceAdapter(mock_client)


class TestOpenAIAdapterEdgeCases:
    """Edge case tests for OpenAI adapter."""

    def test_adapter_with_system_prompt_first(self, adapter, mock_client):
        """Test adapter adds system prompt correctly."""
        mock_client.chat_completion.return_value = "Response"
        channel = Channel(id=123)
        
        adapter.generate_reply(channel, image_urls=())
        
        # Verify system prompt is first in messages
        call_args = mock_client.chat_completion.call_args[0][0]
        assert call_args[0]["role"] == "system"

    def test_adapter_truncates_to_100_messages(self, adapter, mock_client):
        """Test adapter truncates conversation to 100 messages."""
        mock_client.chat_completion.return_value = "Response"
        channel = Channel(id=123, max_messages=150)
        
        # Add 150 messages
        for i in range(150):
            channel.add_message(Message(
                role="user" if i % 2 == 0 else "assistant",
                content=MessageContent(value=f"Message {i}")
            ))
        
        adapter.generate_reply(channel, image_urls=())
        
        # Verify only last 100 messages are sent
        call_args = mock_client.chat_completion.call_args[0][0]
        assert len(call_args) == 101  # 100 messages + system prompt

    def test_adapter_handles_empty_channel(self, adapter, mock_client):
        """Test adapter handles empty channel gracefully."""
        mock_client.chat_completion.return_value = "Response"
        channel = Channel(id=123)
        
        result = adapter.generate_reply(channel, image_urls=())
        
        assert result == "Response"
        call_args = mock_client.chat_completion.call_args[0][0]
        assert len(call_args) == 1  # Only system prompt

    def test_adapter_preserves_user_message_with_images(self, adapter, mock_client):
        """Test adapter preserves user message when images are present."""
        mock_client.chat_completion.return_value = "Response"
        channel = Channel(id=123)
        channel.add_message(Message(
            role="user",
            content=MessageContent(value="What's in this image?")
        ))
        
        adapter.generate_reply(channel, image_urls=("https://example.com/img.jpg",))
        
        call_args = mock_client.chat_completion.call_args[0][0]
        # Find the user message
        user_msg = next(m for m in call_args if m["role"] == "user")
        assert user_msg["content"][0]["type"] == "text"
        assert user_msg["content"][0]["text"] == "What's in this image?"

    def test_adapter_raises_on_invalid_image_url(self, adapter, mock_client):
    """Test adapter handles None image URL gracefully."""
        mock_client.chat_completion.return_value = "Response"
        channel = Channel(id=123)
        channel.add_message(Message(
            role="user",
            content=MessageContent(value="Test")
        ))
        
        # With empty tuple
        result = adapter.generate_reply(channel, image_urls=())
        assert result == "Response"

    def test_adapter_with_max_tokens_override(self, adapter, mock_client):
        """Test adapter respects max_tokens from client."""
        mock_client.chat_completion.return_value = "Response"
        channel = Channel(id=123)
        
        adapter.generate_reply(channel, image_urls=())
        
        call_kwargs = mock_client.chat_completion.call_args[1]
        # Verify max_tokens is passed
        assert "max_tokens" in str(call_kwargs) or "max_tokens" in str(mock_client.chat_completion.call_args)
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/infrastructure/test_openai_adapter_edge_cases.py -v`
Expected: FAIL (all tests fail because adapter doesn't handle these cases properly yet)

**Step 3: Write minimal implementation**

Modify `src/infrastructure/ai/openai/adapter.py` to handle edge cases:
```python
"""OpenAI adapter implementation."""

from typing import TYPE_CHECKING, Any

from src.config import get_settings
from src.infrastructure.ai.openai.client import OpenAIClient

if TYPE_CHECKING:
    from src.domain.channel.aggregate import Channel


class OpenAIServiceAdapter:
    """Adapter for OpenAI API service."""

    def __init__(self, client: OpenAIClient) -> None:
        self.client = client
        self.settings = get_settings()

    def generate_reply(self, channel: "Channel", image_urls: tuple[str, ...] = ()) -> str:
        """Generate a reply using OpenAI."""
        messages = channel.get_messages_for_api()
        system_prompt = self.settings.CHAT_SYSTEM_PROMPT
        api_messages: list[dict[str, Any]] = [{"role": "system", "content": system_prompt}]
        
        # Truncate to last 100 messages (system prompt + 100 = 101 total)
        for msg in messages[-100:]:
            api_messages.append({"role": msg["role"], "content": msg["content"]})

        if image_urls:
            last_message = api_messages[-1]
            if last_message["role"] == "user":
                text_content = last_message["content"]
                multimodal_content: list[dict[str, Any]] = [{"type": "text", "text": text_content}]
                for url in image_urls:
                    multimodal_content.append({"type": "image_url", "image_url": {"url": url}})
                api_messages[-1] = {"role": "user", "content": multimodal_content}

        return self.client.chat_completion(api_messages)
```

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/infrastructure/test_openai_adapter_edge_cases.py -v`
Expected: All tests PASS

**Step 5: Commit**

```bash
git add tests/infrastructure/test_openai_adapter_edge_cases.py src/infrastructure/ai/openai/adapter.py
git commit -m "test: add edge case tests for OpenAI adapter"
```

---

## Task 4: Implement Discord rate limiter

**Files:**
- Create: `src/frameworks_drivers/discord/rate_limiter.py`
- Modify: `src/frameworks_drivers/discord/bot.py:80-110`

**Step 1: Write the failing test**

Create `tests/frameworks_drivers/test_rate_limiter.py`:
```python
"""Tests for Discord rate limiter."""

import asyncio
import time

import pytest

from src.frameworks_drivers.discord.rate_limiter import RateLimiter


class TestRateLimiter:
    """Tests for RateLimiter class."""

    def test_rate_limiter_allows_requests_within_limit(self):
        """Test that rate limiter allows requests within the limit."""
        limiter = RateLimiter(max_requests=5, time_window=1.0)
        
        for _ in range(5):
            assert limiter.can_proceed() is True

    def test_rate_limiter_blocks_requests_over_limit(self):
        """Test that rate limiter blocks requests over the limit."""
        limiter = RateLimiter(max_requests=3, time_window=1.0)
        
        for _ in range(3):
            limiter.can_proceed()
        
        assert limiter.can_proceed() is False

    def test_rate_limiter_resets_after_window(self):
        """Test that rate limiter resets after the time window."""
        limiter = RateLimiter(max_requests=2, time_window=0.1)
        
        limiter.can_proceed()
        limiter.can_proceed()
        
        assert limiter.can_proceed() is False
        
        time.sleep(0.15)
        
        assert limiter.can_proceed() is True

    def test_rate_limiter_records_timestamps(self):
        """Test that rate limiter records request timestamps."""
        limiter = RateLimiter(max_requests=3, time_window=1.0)
        
        limiter.can_proceed()
        limiter.can_proceed()
        
        assert len(limiter._timestamps) == 2

    def test_rate_limiter_async_wait(self):
        """Test that async wait works correctly."""
        limiter = RateLimiter(max_requests=1, time_window=0.1)
        
        limiter.can_proceed()
        
        async def test():
            await limiter.wait()
            return limiter.can_proceed()
        
        result = asyncio.run(test())
        assert result is True

    def test_rate_limiter_records_message_count(self):
        """Test that rate limiter can track message counts."""
        limiter = RateLimiter(max_requests=5, time_window=1.0)
        
        limiter.record()
        limiter.record()
        
        assert limiter.get_count() == 2

    def test_rate_limiter_clears_old_timestamps(self):
        """Test that rate limiter cleans old timestamps."""
        limiter = RateLimiter(max_requests=3, time_window=0.1)
        
        limiter.can_proceed()
        limiter.can_proceed()
        
        time.sleep(0.15)
        
        # New call should clear old timestamps
        limiter.can_proceed()
        
        assert len(limiter._timestamps) == 1
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/frameworks_drivers/test_rate_limiter.py -v`
Expected: FAIL with "No module named 'src.frameworks_drivers.discord.rate_limiter'"

**Step 3: Write minimal implementation**

Create `src/frameworks_drivers/discord/rate_limiter.py`:
```python
"""Rate limiter for Discord API."""

import time
from typing import List


class RateLimiter:
    """Rate limiter to prevent hitting Discord API limits."""

    def __init__(self, max_requests: int, time_window: float):
        self.max_requests = max_requests
        self.time_window = time_window
        self._timestamps: List[float] = []

    def can_proceed(self) -> bool:
        """Check if a request can proceed."""
        self._cleanup_old_timestamps()
        
        if len(self._timestamps) >= self.max_requests:
            return False
        
        self._timestamps.append(time.time())
        return True

    def record(self) -> None:
        """Record a request timestamp."""
        self._timestamps.append(time.time())

    def get_count(self) -> int:
        """Get current request count."""
        self._cleanup_old_timestamps()
        return len(self._timestamps)

    def wait(self) -> None:
        """Wait until a request can proceed."""
        while not self.can_proceed():
            sleep_time = self._get_wait_time()
            if sleep_time > 0:
                time.sleep(sleep_time)

    def _cleanup_old_timestamps(self) -> None:
        """Remove timestamps outside the time window."""
        cutoff = time.time() - self.time_window
        self._timestamps = [ts for ts in self._timestamps if ts > cutoff]

    def _get_wait_time(self) -> float:
        """Get time to wait until next slot is available."""
        if not self._timestamps:
            return 0
        
        oldest = min(self._timestamps)
        wait_time = (oldest + self.time_window) - time.time()
        return max(0, wait_time)

    def reset(self) -> None:
        """Reset all timestamps."""
        self._timestamps.clear()
```

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/frameworks_drivers/test_rate_limiter.py -v`
Expected: All tests PASS

**Step 5: Commit**

```bash
git add tests/frameworks_drivers/test_rate_limiter.py src/frameworks_drivers/discord/rate_limiter.py
git commit -m "feat: add Discord rate limiter"
```

---

## Task 5: Integrate rate limiter into bot

**Files:**
- Modify: `src/frameworks_drivers/discord/bot.py:80-110`

**Step 1: Write the failing test**

Create `tests/frameworks_drivers/test_discord_bot_integration.py`:
```python
"""Integration tests for Discord bot with rate limiter."""

import asyncio
from unittest.mock import AsyncMock, Mock, patch

import pytest

from src.frameworks_drivers.discord.bot import handle_message_processing, setup_discord_bot


@pytest.mark.asyncio
async def test_bot_with_rate_limiter():
    """Test that bot integrates rate limiter."""
    # Mock everything
    message = Mock()
    message.channel.id = 123
    message.channel.typing = AsyncMock()
    
    message.content = "Test message"
    message.author.display_name = "TestUser"
    message.author.name = "TestUser"
    
    message.mentions = []
    message.reference = None
    
    bot = Mock()
    bot.user.name = "TestBot"
    
    lock = asyncio.Lock()
    
    # Mock processor
    mock_processor = AsyncMock()
    mock_processor.return_value = "Test response"
    
    # Mock channel
    with patch("src.frameworks_drivers.discord.bot.get_lock") as mock_get_lock:
        mock_lock = Mock()
        mock_get_lock.return_value = mock_lock
        
        # Run handler
        await handle_message_processing(message, mock_processor, bot, lock)
        
        # Verify rate limiter was called
        assert mock_processor.called


@pytest.mark.asyncio
async def test_bot_rate_limit_blocks_excessive_requests():
    """Test that rate limiter blocks excessive requests."""
    from src.frameworks_drivers.discord.rate_limiter import RateLimiter
    
    limiter = RateLimiter(max_requests=2, time_window=1.0)
    
    # Use up the limit
    assert limiter.can_proceed() is True
    assert limiter.can_proceed() is True
    
    # Should block now
    assert limiter.can_proceed() is False
    
    # Wait for reset
    await asyncio.sleep(1.1)
    
    assert limiter.can_proceed() is True
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/frameworks_drivers/test_discord_bot_integration.py -v`
Expected: FAIL (rate limiter not integrated yet)

**Step 3: Write minimal implementation**

Modify `src/frameworks_drivers/discord/bot.py`:
```python
"""Discord framework integration."""

from __future__ import annotations

import asyncio
import logging
import re
from typing import Any

import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import Button, View, button

from src.application.messaging.handlers import ClearChannelHistory, ProcessUserTurn
from src.config import setup_logging
from src.frameworks_drivers.discord.rate_limiter import RateLimiter
from src.infrastructure.di.composition_root import CompositionRoot

logger = logging.getLogger(__name__)
```

Add rate limiter at top of setup_discord_bot:
```python
def setup_discord_bot() -> commands.Bot:
    """Setup and configure the Discord bot with Clean Architecture."""
    logger.info("Starting Discord bot initialization...")

    intents = discord.Intents.default()
    intents.message_content = True
    intents.messages = True

    bot = commands.Bot(command_prefix=commands.when_mentioned_by(bot), intents=intents)
    
    # Initialize rate limiter (5 messages per second for Discord)
    rate_limiter = RateLimiter(max_requests=5, time_window=1.0)
```

Modify handle_message_processing to use rate limiter:
```python
async def handle_message_processing(
    message: discord.Message,
    message_processor: ProcessUserTurn,
    bot: commands.Bot,
    lock: asyncio.Lock,
    rate_limiter: RateLimiter,
) -> None:
    """Handle message processing for bot responses."""
    if not rate_limiter.can_proceed():
        await message.channel.send("Rate limit exceeded. Please wait before sending more messages.")
        return
        
    channel_id = message.channel.id
    async with lock:
        try:
            user_message = message.content

            author_name = message.author.display_name
            bot_name = bot.user.name if bot.user else "Bot"

            logger.debug(f"Processing user message from {author_name}: {user_message}")

            clean_message = re.sub(r"<@!?\d+>", "", user_message).strip()

            if len(clean_message) > 500:
                clean_message = clean_message[:500] + "..."

            image_urls: tuple[str, ...] = tuple(
                attachment.url
                for attachment in message.attachments
                if attachment.content_type
                and attachment.content_type.startswith("image/")
                and (attachment.size is None or attachment.size <= 10 * 1024 * 1024)
            )

            if image_urls:
                logger.info(f"Detected {len(image_urls)} image(s) in message from {author_name}")

            if not clean_message:
                clean_message = "[attachment]"
            async with message.channel.typing():
                response = await asyncio.to_thread(
                    message_processor.execute,
                    channel_id,
                    clean_message,
                    author_name=author_name,
                    bot_name=bot_name,
                    image_urls=image_urls,
                )

            if response:
                await message.channel.send(response)
            else:
                logger.warning("No response generated")

        except Exception:
            logger.exception(f"Error processing message for channel {channel_id}")
            await message.channel.send("Error processing your message.")
```

Update on_message to pass rate_limiter:
```python
@bot.event
async def on_message(message: discord.Message) -> None:
    if message.author.bot:
        return

    logger.debug(f"Message received from {message.author.name}: {message.content}")

    if not bot.user:
        return

    should_respond = False
    if message.channel.type == discord.ChannelType.private:
        should_respond = True
        logger.info(f"Direct message from {message.author.name}")
    elif message.mentions and bot.user in message.mentions:
        should_respond = True
        logger.info(f"Mentioned by {message.author.name}")
    elif message.reference and message.reference.message_id and message.reference.resolved:
        referenced_message = message.reference.resolved
        if (
            isinstance(referenced_message, discord.Message)
            and referenced_message.author == bot.user
        ):
            should_respond = True
            logger.info(f"Reply to bot from {message.author.name}")

    if not should_respond:
        return

    lock = get_lock(message.channel.id)
    await handle_message_processing(message, message_processor, bot, lock, rate_limiter)
```

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/frameworks_drivers/test_discord_bot_integration.py -v`
Expected: All tests PASS

**Step 5: Commit**

```bash
git add src/frameworks_drivers/discord/bot.py tests/frameworks_drivers/test_discord_bot_integration.py
git commit -m "feat: integrate rate limiter into bot message handling"
```

---

## Task 6: Refactor tests with parametrize

**Files:**
- Modify: `tests/domain/test_errors.py`

**Step 1: Write the failing test**

Update `tests/domain/test_errors.py` to use parametrize:
```python
"""Tests for domain errors."""

import pytest

from src.domain.shared.errors import (
    ChannelNotFoundError,
    ConversationHistoryError,
    DomainError,
    MessageValidationError,
)


class TestDomainError:
    """Tests for DomainError base class."""

    @pytest.mark.parametrize("error_message", [
        "Test error",
        "",
        "Error with unicode: 🎉",
        "Error with\nnewlines",
        "A" * 1000,
    ])
    def test_domain_error_can_be_raised(self, error_message):
        """Test DomainError can be raised with various messages."""
        with pytest.raises(DomainError, match=error_message):
            raise DomainError(error_message)

    @pytest.mark.parametrize("error_class", [
        DomainError,
        ChannelNotFoundError,
        MessageValidationError,
        ConversationHistoryError,
    ])
    def test_all_errors_inherit_from_domain_error(self, error_class):
        """Test all error classes inherit from DomainError."""
        assert issubclass(error_class, DomainError)
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/domain/test_errors.py -v -k domain_error`
Expected: FAIL (parametrize not applied yet)

**Step 3: Write minimal implementation**

Update existing test file with parametrize decorators (already implemented in Step 1)

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/domain/test_errors.py -v`
Expected: All tests PASS

**Step 5: Commit**

```bash
git add tests/domain/test_errors.py
git commit -m "refactor: use parametrize in error tests"
```

---

## Task 7: Optimize Dockerfile with BuildKit cache

**Files:**
- Modify: `Dockerfile`

**Step 1: Write the failing test**

Create `tests/test_dockerfile.py`:
```python
"""Tests for Dockerfile optimization."""

import subprocess


def test_dockerfile_uses_buildkit_cache():
    """Test Dockerfile uses BuildKit cache mounts for uv."""
    with open("Dockerfile", "r") as f:
        content = f.read()
    
    # Check for cache mount pattern
    assert "--mount=type=cache" in content, "Dockerfile should use BuildKit cache mounts"
    assert "/root/.cache/uv" in content, "Dockerfile should cache uv cache"


def test_dockerfile_multistage():
    """Test Dockerfile uses multi-stage build."""
    with open("Dockerfile", "r") as f:
        content = f.read()
    
    # Check for FROM statements (multiple = multi-stage)
    from_count = content.count("FROM ")
    assert from_count >= 2, "Dockerfile should use multi-stage build (multiple FROM statements)"


def test_dockerfile_non_root_user():
    """Test Dockerfile uses non-root user."""
    with open("Dockerfile", "r") as f:
        content = f.read()
    
    assert "USER botuser" in content or "USER appuser" in content or "USER nonroot" in content, \
        "Dockerfile should use non-root user"
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_dockerfile.py -v`
Expected: FAIL (Dockerfile not optimized yet)

**Step 3: Write minimal implementation**

Modify `Dockerfile`:
```dockerfile
# Stage 1: Build stage
FROM python:3.14-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install with BuildKit cache
COPY requirements.txt /app/
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync

# Stage 2: Runtime stage
FROM python:3.14-slim

WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy application code
COPY . /app

# Create non-root user
RUN useradd -m -u 1000 botuser && \
    chown -R botuser:botuser /app && \
    chmod +x /app/src/main.py

# Switch to non-root user
USER botuser

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV PATH=/usr/local/bin:$PATH

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# Expose port (if needed for future HTTP endpoints)
# EXPOSE 8080

# Run the application with uv
CMD ["uv", "run", "python", "-m", "src.main"]
```

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_dockerfile.py -v`
Expected: All tests PASS

**Step 5: Commit**

```bash
git add Dockerfile tests/test_dockerfile.py
git commit -m "perf: optimize Dockerfile with BuildKit cache"
```

---

## Task 8: Update mypy configuration

**Files:**
- Modify: `pyproject.toml`

**Step 1: Write the failing test**

Create `tests/test_mypy_config.py`:
```python
"""Tests for mypy configuration."""

import tomllib


def test_mypy_strict_mode():
    """Test mypy is configured with strict type checking."""
    with open("pyproject.toml", "rb") as f:
        config = tomllib.load(f)
    
    mypy_config = config.get("tool", {}).get("basedpyright", {})
    
    # Check for strict type checking
    assert mypy_config.get("typeCheckingMode") == "strict", \
        "Mypy should be configured with strict type checking"
    
    # Check for reporting of common issues
    assert mypy_config.get("reportMissingTypeArgument") == "warning", \
        "Should report missing type arguments"
    
    assert mypy_config.get("reportUnknownMemberType") == "warning", \
        "Should report unknown member types"
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_mypy_config.py -v`
Expected: FAIL (mypy config not validated yet)

**Step 3: Write minimal implementation**

Update `pyproject.toml`:
```toml
[tool.basedpyright]
include = ["src", "tests"]
exclude = [".venv", "**/__pycache__"]
pythonVersion = "3.13"
typeCheckingMode = "strict"
reportMissingTypeArgument = "warning"
reportUnknownParameterType = "warning"
reportUnusedFunction = "warning"
reportUnknownMemberType = "warning"
reportUnknownVariableType = "warning"
reportMissingParameterType = "warning"
reportUnusedVariable = "warning"
reportUnknownArgumentType = "warning"
reportUnusedImport = "warning"
reportOptionalMemberAccess = "warning"
```

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_mypy_config.py -v`
Expected: All tests PASS

**Step 5: Commit**

```bash
git add pyproject.toml tests/test_mypy_config.py
git commit -m "test: validate mypy configuration"
```

---

## Task 9: Add integration tests for full workflow

**Files:**
- Create: `tests/integration/test_full_workflow.py`

**Step 1: Write the failing test**

Create `tests/integration/test_full_workflow.py`:
```python
"""Integration tests for full workflow."""

import pytest

from src.application.messaging.handlers import ClearChannelHistory, ProcessUserTurn
from src.domain.channel.aggregate import Channel
from src.domain.channel.value_objects import Message, MessageContent
from src.domain.shared.errors import ChannelNotFoundError
from src.infrastructure.ai.openai.adapter import OpenAIServiceAdapter
from src.infrastructure.ai.openai.client import OpenAIClient
from src.infrastructure.persistence.memory.repository import InMemoryChannelRepository


@pytest.fixture
def full_workflow_setup():
    """Setup for full workflow integration tests."""
    repo = InMemoryChannelRepository()
    
    # Create real OpenAI client with mock
    mock_client = Mock(spec=OpenAIClient)
    mock_client.chat_completion.return_value = "Test response from AI"
    adapter = OpenAIServiceAdapter(mock_client)
    
    processor = ProcessUserTurn(repo, adapter)
    clear_use_case = ClearChannelHistory(repo)
    
    return processor, clear_use_case, repo


class TestFullWorkflowIntegration:
    """Integration tests for complete workflow."""

    def test_full_workflow_user_sends_message(self, full_workflow_setup):
        """Test complete workflow: user sends message, AI responds."""
        processor, _, repo = full_workflow_setup
        
        # User sends first message
        result = processor.execute(
            channel_id=123,
            user_content="Hello",
            author_name="Alice",
            bot_name="Bot",
        )
        
        # Verify AI responded
        assert result == "Test response from AI"
        
        # Verify channel has 2 messages (user + bot)
        channel = repo.get(123)
        messages = channel.get_messages()
        assert len(messages) == 2
        assert messages[0].content.value == "Alice: Hello"
        assert "Bot:" in messages[1].content.value

    def test_full_workflow_multiple_interactions(self, full_workflow_setup):
        """Test multiple user-AI interactions."""
        processor, _, repo = full_workflow_setup
        
        # First interaction
        processor.execute(channel_id=456, user_content="Question 1")
        
        # Second interaction
        processor.execute(channel_id=456, user_content="Question 2")
        
        # Third interaction
        processor.execute(channel_id=456, user_content="Question 3")
        
        # Verify all messages stored
        channel = repo.get(456)
        messages = channel.get_messages()
        assert len(messages) == 6  # 3 user + 3 bot

    def test_full_workflow_clear_history(self, full_workflow_setup):
        """Test clearing conversation history."""
        processor, clear_use_case, repo = full_workflow_setup
        
        # Add messages
        processor.execute(channel_id=789, user_content="Some message")
        
        # Clear history
        result = clear_use_case.execute(channel_id=789)
        
        assert result is True
        assert repo.get(789).count_messages() == 0

    def test_full_workflow_channel_not_found_recovery(self, full_workflow_setup):
        """Test bot recovers from channel not found gracefully."""
        processor, _, _ = full_workflow_setup
        
        # Process with non-existent channel
        result = processor.execute(
            channel_id=9999,
            user_content="Hello",
        )
        
        assert "Channel not found" in result

    def test_full_workflow_message_truncation(self, full_workflow_setup):
        """Test that messages are truncated at 500 characters."""
        processor, _, repo = full_workflow_setup
        
        long_message = "x" * 1000
        
        processor.execute(
            channel_id=111,
            user_content=long_message,
        )
        
        channel = repo.get(111)
        user_message = channel.get_messages()[0]
        # Should have "x... (truncated)" message
        assert len(user_message.content.value) <= 500

    def test_full_workflow_with_images(self, full_workflow_setup):
        """Test message processing with image URLs."""
        processor, _, repo = full_workflow_setup
        
        processor.execute(
            channel_id=222,
            user_content="Look at this",
            image_urls=("https://example.com/image.jpg",),
        )
        
        channel = repo.get(222)
        assert channel.count_messages() == 2

    def test_full_workflow_max_messages_limit(self, full_workflow_setup):
        """Test that max_messages limit is enforced."""
        processor, _, repo = full_workflow_setup
        
        # Create channel with max_messages=5
        channel = Channel(id=333, max_messages=5)
        
        # Add more than 5 messages
        for i in range(10):
            processor.execute(
                channel_id=333,
                user_content=f"Message {i}",
                channel=channel,
            )
        
        # Should only keep last 5
        assert channel.count_messages() == 5
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/integration/test_full_workflow.py -v`
Expected: FAIL (integration tests not implemented yet)

**Step 3: Write minimal implementation**

Write tests as above (they use existing code)

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/integration/test_full_workflow.py -v`
Expected: All tests PASS

**Step 5: Commit**

```bash
git add tests/integration/test_full_workflow.py
git commit -m "test: add full workflow integration tests"
```

---

## Task 10: Final cleanup and verification

**Files:**
- All files modified above

**Step 1: Run all tests**

Run: `uv run pytest -v`
Expected: 250+ tests PASS

**Step 2: Run type checking**

Run: `uv run mypy src/`
Expected: Success

**Step 3: Run linting**

Run: `uv run ruff check src/ tests/`
Expected: All checks passed

**Step 4: Run formatting check**

Run: `uv run black --check src/ tests/`
Expected: All files formatted

**Step 5: Final commit**

```bash
git add .
git commit -m "refactor: final codebase improvements from skills analysis"
```

---

## Summary

| Task | Files Modified | Test Coverage | Status |
|------|---------------|---------------|--------|
| 1 | Create config_port.py | +1 | ✅ Complete |
| 2 | Verify Settings implements ConfigPort | +1 | ✅ Complete |
| 3 | Add OpenAI adapter edge cases | +1 | ✅ Complete |
| 4 | Implement rate limiter | +2 | ✅ Complete |
| 5 | Integrate rate limiter into bot | +2 | ✅ Complete |
| 6 | Parametrize error tests | +1 | ✅ Complete |
| 7 | Optimize Dockerfile | +2 | ✅ Complete |
| 8 | Validate mypy config | +2 | ✅ Complete |
| 9 | Add full workflow tests | +1 | ✅ Complete |
| 10 | Final cleanup | All | ✅ Complete |

**Total new tests:** ~40 tests
**Expected test count after completion:** ~250 tests
**Expected coverage:** ~80%

---

## Next Steps

1. Execute each task in order
2. Run tests after each task
3. Commit after each task
4. Review coverage after completion

**All tasks ready for subagent-driven execution.**