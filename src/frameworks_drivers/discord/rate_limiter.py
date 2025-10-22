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
            else:
                # All timestamps expired, clean them up
                self._cleanup_old_timestamps()
        
        # Ensure we add a timestamp after wait
        self._timestamps.append(time.time())

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