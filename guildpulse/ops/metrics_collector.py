"""Runtime metrics collection for GuildPulse."""

from __future__ import annotations

import threading
import time
from collections import defaultdict
from dataclasses import dataclass, field


@dataclass
class MetricSnapshot:
    messages_processed: int = 0
    messages_blocked: int = 0
    tokens_generated: int = 0
    knowledge_hits: int = 0
    api_errors: int = 0
    average_latency_ms: float = 0.0


class MetricsCollector:
    """Thread-safe in-process metrics for bot and HTTP runtimes."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._messages_processed = 0
        self._messages_blocked = 0
        self._tokens_generated = 0
        self._knowledge_hits = 0
        self._api_errors = 0
        self._latencies: list[float] = []
        self._guild_counters: dict[int, int] = defaultdict(int)
        self._started_at = time.time()

    def record_message(self, guild_id: int | None, blocked: bool, tokens: int = 0) -> None:
        with self._lock:
            if blocked:
                self._messages_blocked += 1
            else:
                self._messages_processed += 1
                self._tokens_generated += tokens
            if guild_id is not None:
                self._guild_counters[guild_id] += 1

    def record_knowledge_hit(self) -> None:
        with self._lock:
            self._knowledge_hits += 1

    def record_api_error(self) -> None:
        with self._lock:
            self._api_errors += 1

    def record_latency(self, elapsed_ms: float) -> None:
        with self._lock:
            self._latencies.append(elapsed_ms)
            if len(self._latencies) > 500:
                self._latencies = self._latencies[-500:]

    def snapshot(self) -> MetricSnapshot:
        with self._lock:
            avg = sum(self._latencies) / len(self._latencies) if self._latencies else 0.0
            return MetricSnapshot(
                messages_processed=self._messages_processed,
                messages_blocked=self._messages_blocked,
                tokens_generated=self._tokens_generated,
                knowledge_hits=self._knowledge_hits,
                api_errors=self._api_errors,
                average_latency_ms=avg,
            )

    def top_guilds(self, limit: int = 10) -> list[tuple[int, int]]:
        with self._lock:
            ranked = sorted(self._guild_counters.items(), key=lambda item: item[1], reverse=True)
        return ranked[:limit]

    def uptime_seconds(self) -> float:
        return time.time() - self._started_at


GLOBAL_METRICS = MetricsCollector()
