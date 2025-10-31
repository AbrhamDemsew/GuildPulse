"""Moderation audit routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from guildpulse.http.deps import get_root, verify_api_key
from guildpulse.http.schemas import ModerationEventResponse
from guildpulse.infrastructure.di.composition_root import CompositionRoot

router = APIRouter(dependencies=[Depends(verify_api_key)])


@router.get("/{guild_id}", response_model=list[ModerationEventResponse])
def list_events(
    guild_id: int,
    limit: int = Query(default=50, ge=1, le=200),
    root: CompositionRoot = Depends(get_root),
) -> list[ModerationEventResponse]:
    events = root.create_moderation_events().execute(guild_id, limit=limit)
    return [
        ModerationEventResponse(
            record_id=event.record_id,
            guild_id=event.guild_id,
            user_id=event.user_id,
            channel_id=event.channel_id,
            action=event.action.value,
            reason=event.reason,
            content_preview=event.content_preview,
        )
        for event in events
    ]
