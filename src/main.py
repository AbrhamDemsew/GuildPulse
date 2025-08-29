#!/usr/bin/env python3
"""Main entry point for the Discord bot."""

import asyncio

from src.frameworks_drivers.discord_bot import main as discord_main


async def main() -> None:
    """Main entry point for the Discord bot."""
    await discord_main()


if __name__ == "__main__":
    asyncio.run(main())
