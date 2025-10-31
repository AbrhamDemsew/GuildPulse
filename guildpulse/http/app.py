"""FastAPI application factory for GuildPulse admin API."""

from __future__ import annotations

from fastapi import FastAPI

from guildpulse.config import Settings
from guildpulse.http.routers import analytics, guilds, health, knowledge, moderation, onboarding, ops, plugins
from guildpulse.infrastructure.di.composition_root import CompositionRoot


def create_app(settings: Settings, root: CompositionRoot | None = None) -> FastAPI:
    composition = root or CompositionRoot(settings)
    app = FastAPI(
        title="GuildPulse Admin API",
        description="Operational API for guild configuration, moderation, analytics, and knowledge.",
        version="1.1.0",
    )
    app.state.settings = settings
    app.state.root = composition

    app.include_router(health.router, tags=["health"])
    app.include_router(guilds.router, prefix="/api/v1/guilds", tags=["guilds"])
    app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["analytics"])
    app.include_router(moderation.router, prefix="/api/v1/moderation", tags=["moderation"])
    app.include_router(knowledge.router, prefix="/api/v1/knowledge", tags=["knowledge"])
    app.include_router(ops.router, prefix="/api/v1/ops", tags=["ops"])
    app.include_router(plugins.router, prefix="/api/v1/plugins", tags=["plugins"])
    app.include_router(onboarding.router, prefix="/api/v1/onboarding", tags=["onboarding"])
    return app
