"""Stub file for discord.py event handlers.

These functions are called by the discord.py client at runtime,
so they appear as unused to static analysis tools.
"""

import discord
from typing import Any

# Event handlers - called by discord.Client.event decorator
async def on_ready() -> None: ...

async def on_message(message: discord.Message) -> None: ...

async def on_error(event: str, *args: Any, **kwargs: Any) -> None: ...

# Slash commands - called by discord.app_commands.tree
async def help_command(interaction: discord.Interaction) -> None: ...

async def chat(interaction: discord.Interaction, query: str) -> None: ...

async def clear(interaction: discord.Interaction) -> None: ...
