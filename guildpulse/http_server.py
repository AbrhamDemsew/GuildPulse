"""Run GuildPulse admin HTTP API."""

from __future__ import annotations

import uvicorn

from guildpulse.config import get_settings
from guildpulse.http.app import create_app


def main() -> None:
    settings = get_settings()
    app = create_app(settings)
    uvicorn.run(app, host=settings.HTTP_HOST, port=settings.HTTP_PORT, log_level=settings.LOG_LEVEL.lower())


if __name__ == "__main__":
    main()
