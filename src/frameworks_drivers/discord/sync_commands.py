#!/usr/bin/env python3
"""Script to sync slash commands to Discord.

Usage (development with guild-specific commands):
    python -m src.frameworks_drivers.discord.sync_commands

Usage (production with global commands):
    DISCORD_SYNC_GLOBAL=true python -m src.frameworks_drivers.discord.sync_commands
"""

import asyncio
import os

import discord
from discord.ext import commands

from src.config import get_settings
from src.frameworks_drivers.discord.bot import setup_discord_bot


async def main() -> None:
    """Sync application commands to Discord."""
    settings = get_settings()

    if not settings.DISCORD_TOKEN:
        raise ValueError("DISCORD_TOKEN is required")

    bot = commands.Bot(
        command_prefix=commands.when_mentioned_or("*"), intents=discord.Intents.default()
    )
    bot = setup_discord_bot()

    sync_global = os.environ.get("DISCORD_SYNC_GLOBAL", "false").lower() == "true"

    print(f"Syncing commands... (global: {sync_global})")
    if sync_global:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} global command(s)")
    else:
        guild_id = os.environ.get("DISCORD_DEV_GUILD_ID")
        if guild_id:
            guild = discord.Object(id=int(guild_id))
            synced = await bot.tree.sync(guild=guild)
            print(f"Synced {len(synced)} guild command(s) for guild {guild_id}")
        else:
            print("DISCORD_DEV_GUILD_ID not set. Use DISCORD_SYNC_GLOBAL=true for global commands")

    await bot.close()
    print("Commands synced successfully")


if __name__ == "__main__":
    asyncio.run(main())
