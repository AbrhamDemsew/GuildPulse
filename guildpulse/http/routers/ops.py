"""Operational metrics and audit routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from guildpulse.http.deps import get_root, verify_api_key
from guildpulse.infrastructure.di.composition_root import CompositionRoot
from guildpulse.ops.metrics_collector import GLOBAL_METRICS

router = APIRouter(dependencies=[Depends(verify_api_key)])


@router.get("/metrics")
def runtime_metrics() -> dict[str, float | int]:
    snapshot = GLOBAL_METRICS.snapshot()
    return {
        "messages_processed": snapshot.messages_processed,
        "messages_blocked": snapshot.messages_blocked,
        "tokens_generated": snapshot.tokens_generated,
        "knowledge_hits": snapshot.knowledge_hits,
        "api_errors": snapshot.api_errors,
        "average_latency_ms": round(snapshot.average_latency_ms, 2),
        "uptime_seconds": round(GLOBAL_METRICS.uptime_seconds(), 2),
    }


@router.get("/metrics/top-guilds")
def top_guilds(limit: int = 10) -> list[dict[str, int]]:
    return [{"guild_id": guild_id, "messages": count} for guild_id, count in GLOBAL_METRICS.top_guilds(limit)]


@router.get("/audit/{guild_id}")
def audit_entries(guild_id: int, root: CompositionRoot = Depends(get_root)) -> list[dict[str, object]]:
    entries = root.audit_log.list_for_guild(guild_id, limit=100)
    return [
        {
            "id": entry.entry_id,
            "action": entry.action.value,
            "guild_id": entry.guild_id,
            "actor_id": entry.actor_id,
            "details": entry.details,
            "created_at": entry.created_at.isoformat() if entry.created_at else None,
        }
        for entry in entries
    ]
