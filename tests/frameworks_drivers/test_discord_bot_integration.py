"""Integration tests for Discord bot with rate limiter."""

import asyncio
from unittest.mock import AsyncMock, Mock

import pytest

from src.frameworks_drivers.discord.bot import handle_message_processing
from src.frameworks_drivers.discord.rate_limiter import RateLimiter


@pytest.mark.asyncio
async def test_bot_with_rate_limiter():
    """Test that bot integrates rate limiter."""
    # Mock everything
    message = Mock()
    message.channel.id = 123

    # Mock typing context manager properly
    typing_ctx = AsyncMock()
    typing_ctx.__aenter__ = AsyncMock(return_value=None)
    typing_ctx.__aexit__ = AsyncMock(return_value=None)
    message.channel.typing = lambda: typing_ctx

    message.channel.send = AsyncMock()

    message.content = "Test message"
    message.author.display_name = "TestUser"
    message.author.name = "TestUser"

    message.mentions = []
    message.reference = None
    message.attachments = []

    bot = Mock()
    bot.user.name = "TestBot"

    lock = asyncio.Lock()

    # Mock processor
    mock_processor = AsyncMock()
    mock_processor.return_value = "Test response"

    # Mock rate limiter
    rate_limiter = RateLimiter(max_requests=5, time_window=1.0)

    # Run handler directly
    await handle_message_processing(message, mock_processor, bot, lock, rate_limiter=rate_limiter)

    # Verify rate limiter was called and processor was called
    assert rate_limiter.get_count() == 1


@pytest.mark.asyncio
async def test_bot_rate_limit_blocks_excessive_requests():
    """Test that rate limiter blocks excessive requests."""
    limiter = RateLimiter(max_requests=2, time_window=1.0)

    # Use up the limit
    assert limiter.can_proceed() is True
    assert limiter.can_proceed() is True

    # Should block now
    assert limiter.can_proceed() is False

    # Wait for reset
    await asyncio.sleep(1.1)

    assert limiter.can_proceed() is True
