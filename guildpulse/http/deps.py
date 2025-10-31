"""HTTP dependency helpers."""

from __future__ import annotations

from fastapi import Header, HTTPException, Request

from guildpulse.config import Settings
from guildpulse.infrastructure.di.composition_root import CompositionRoot


def get_settings(request: Request) -> Settings:
    return request.app.state.settings


def get_root(request: Request) -> CompositionRoot:
    return request.app.state.root


def verify_api_key(
    request: Request,
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
) -> None:
    settings: Settings = request.app.state.settings
    if settings.HTTP_API_KEY and x_api_key != settings.HTTP_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
