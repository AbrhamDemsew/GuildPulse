"""Health and readiness routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from guildpulse.http.deps import get_root, get_settings
from guildpulse.http.schemas import HealthResponse
from guildpulse.infrastructure.di.composition_root import CompositionRoot

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    return HealthResponse()


@router.get("/ready")
def readiness(root: CompositionRoot = Depends(get_root)) -> dict[str, str | int]:
    guild_count = len(root.create_list_guilds().execute())
    return {"status": "ready", "configured_guilds": guild_count}


@router.get("/version")
def version(settings=Depends(get_settings)) -> dict[str, str | int | bool]:
    return {
        "service": "guildpulse",
        "http_enabled": settings.HTTP_ENABLED,
        "model": settings.OPENAI_MODEL,
    }
