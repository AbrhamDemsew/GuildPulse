"""Moderation domain models."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ModerationAction(str, Enum):
    ALLOW = "allow"
    BLOCK = "block"
    WARN = "warn"
    RATE_LIMIT = "rate_limit"


@dataclass(frozen=True)
class ModerationDecision:
    """Result of evaluating user content before AI processing."""

    action: ModerationAction
    reason: str
    blocked: bool = False

    @classmethod
    def allow(cls) -> ModerationDecision:
        return cls(action=ModerationAction.ALLOW, reason="Content allowed", blocked=False)

    @classmethod
    def block(cls, reason: str) -> ModerationDecision:
        return cls(action=ModerationAction.BLOCK, reason=reason, blocked=True)

    @classmethod
    def rate_limited(cls) -> ModerationDecision:
        return cls(
            action=ModerationAction.RATE_LIMIT,
            reason="User exceeded per-minute message limit",
            blocked=True,
        )


@dataclass(frozen=True)
class ModerationRecord:
    """Persisted moderation audit entry."""

    guild_id: int
    user_id: int
    channel_id: int
    action: ModerationAction
    reason: str
    content_preview: str
    record_id: int | None = None
