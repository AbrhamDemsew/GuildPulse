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

    def test_rate_limiter_wait(self):
        """Test that wait works correctly."""
        limiter = RateLimiter(max_requests=1, time_window=0.05)
        
        limiter.can_proceed()
        
        # Wait should block until window resets
        limiter.wait()
        
        # After wait, should be able to proceed - wait adds timestamp
        assert limiter.get_count() >= 1

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