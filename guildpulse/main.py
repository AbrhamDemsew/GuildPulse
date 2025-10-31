#!/usr/bin/env python3
"""Main entry point for GuildPulse bot and admin API."""

from __future__ import annotations

import asyncio
import logging
import threading

import uvicorn

from guildpulse.config import get_settings
from guildpulse.frameworks_drivers.discord import main as discord_main
from guildpulse.http.app import create_app
from guildpulse.infrastructure.di.composition_root import CompositionRoot

logger = logging.getLogger(__name__)


def _run_http_server(settings, root: CompositionRoot) -> None:
    app = create_app(settings, root)
    uvicorn.run(
        app,
        host=settings.HTTP_HOST,
        port=settings.HTTP_PORT,
        log_level=settings.LOG_LEVEL.lower(),
    )


async def main() -> None:
    settings = get_settings()
    root = CompositionRoot(settings)

    if settings.HTTP_ENABLED:
        thread = threading.Thread(
            target=_run_http_server,
            args=(settings, root),
            daemon=True,
            name="guildpulse-http",
        )
        thread.start()
        logger.info("Admin HTTP API listening on %s:%s", settings.HTTP_HOST, settings.HTTP_PORT)

    await discord_main()


if __name__ == "__main__":
    asyncio.run(main())
