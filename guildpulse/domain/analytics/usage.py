"""Usage analytics domain models."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class UsageTotals:
    """Aggregated usage for a guild or user on a given day."""

    guild_id: int
    recorded_on: date
    message_count: int
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    user_id: int | None = None

    @property
    def average_tokens_per_message(self) -> float:
        if self.message_count == 0:
            return 0.0
        return self.total_tokens / self.message_count


@dataclass(frozen=True)
class QuotaStatus:
    """Remaining quota for a guild on the current day."""

    guild_id: int
    recorded_on: date
    messages_used: int
    messages_limit: int
    tokens_used: int
    tokens_limit: int

    @property
    def messages_remaining(self) -> int:
        return max(0, self.messages_limit - self.messages_used)

    @property
    def tokens_remaining(self) -> int:
        return max(0, self.tokens_limit - self.tokens_used)

    @property
    def is_exhausted(self) -> bool:
        return self.messages_remaining == 0 or self.tokens_remaining == 0
