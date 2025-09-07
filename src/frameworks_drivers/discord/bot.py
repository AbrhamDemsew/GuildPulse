"""Discord framework integration."""

import asyncio
import logging
import re
from typing import Any

import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import Button, View, button

from src.application.messaging.handlers import ClearChannelHistory, ProcessUserTurn
from src.config import get_settings, setup_logging
from src.infrastructure.ai.openai.adapter import OpenAIServiceAdapter
from src.infrastructure.ai.openai.client import OpenAIClient
from src.infrastructure.persistence.memory.repository import InMemoryMessageRepository

logger = logging.getLogger(__name__)


class ConfirmClearView(View):
    """View with confirm/cancel buttons for clearing channel history."""

    def __init__(
        self, use_case: ClearChannelHistory, channel_id: int, author_id: int
    ):
        super().__init__(timeout=60)
        self.use_case = use_case
        self.channel_id = channel_id
        self.author_id = author_id

    @button(label="Confirm", style=discord.ButtonStyle.danger)
    async def confirm_button(
        self, interaction: discord.Interaction, _button: Button
    ) -> None:
        if interaction.user.id != self.author_id:
            await interaction.response.send_message(
                "You cannot confirm this action.", ephemeral=True
            )
            return
        success = self.use_case.execute(self.channel_id)
        if success:
            await interaction.response.edit_message(
                content="Conversation history cleared!", embed=None, view=None
            )
        else:
            await interaction.response.edit_message(
                content="No conversation history to clear.", embed=None, view=None
            )
        self.stop()

    @button(label="Cancel", style=discord.ButtonStyle.secondary)
    async def cancel_button(
        self, interaction: discord.Interaction, _button: Button
    ) -> None:
        if interaction.user.id != self.author_id:
            await interaction.response.send_message(
                "You cannot cancel this action.", ephemeral=True
            )
            return
        await interaction.response.edit_message(
            content="Clearing cancelled.", embed=None, view=None
        )
        self.stop()

    async def on_timeout(self) -> None:
        if self.message:  # type: ignore[attr-defined]
            for child in self.children:
                child.disabled = True  # type: ignore[attr-defined]
            await self.message.edit(view=self)  # type: ignore[attr-defined]


async def handle_message_processing(
    message: discord.Message,
    message_processor: ProcessUserTurn,
    bot: commands.Bot,
    lock: asyncio.Lock,
) -> None:
    """Handle message processing for bot responses."""
    channel_id = message.channel.id
    async with lock:
        try:
            user_message = message.content

            author_name = message.author.display_name
            bot_name = bot.user.name if bot.user else "Bot"

            logger.debug(f"Processing user message from {author_name}: {user_message}")

            clean_message = re.sub(r"<@!?(\d+)>", "", user_message).strip()

            if len(clean_message) > 500:
                clean_message = clean_message[:500] + "..."

            if not clean_message:
                clean_message = "[attachment]"
            async with message.channel.typing():
                response = await asyncio.to_thread(
                    message_processor.execute,
                    channel_id,
                    clean_message,
                    author_name=author_name,
                    bot_name=bot_name,
                )

            if response:
                await message.channel.send(response)
            else:
                logger.warning("No response generated")

        except Exception:
            logger.exception(f"Error processing message for channel {channel_id}")
            await message.channel.send("Error processing your message.")


def setup_discord_bot() -> commands.Bot:
    """Setup and configure the Discord bot with Clean Architecture."""
    settings = get_settings()

    setup_logging(settings)

    logger.info("Starting Discord bot initialization...")

    intents = discord.Intents.default()
    intents.message_content = True
    intents.messages = True

    bot = commands.Bot(command_prefix=commands.when_mentioned_or("*"), intents=intents)

    repo = InMemoryMessageRepository()
    openai_client = OpenAIClient(
        api_key=settings.OPENAI_API_KEY,
        base_url=settings.OPENAI_BASE_URL,
        model=settings.OPENAI_MODEL,
        max_tokens=settings.OPENAI_MAX_TOKENS,
        temperature=settings.OPENAI_TEMPERATURE,
    )
    ai_service = OpenAIServiceAdapter(openai_client)

    message_processor = ProcessUserTurn(repo, ai_service)
    clear_history_use_case = ClearChannelHistory(repo)

    logger.info("Discord bot initialized with Clean Architecture")

    channel_locks: dict[int, asyncio.Lock] = {}

    def get_lock(channel_id: int) -> asyncio.Lock:
        if channel_id not in channel_locks:
            channel_locks[channel_id] = asyncio.Lock()
        return channel_locks[channel_id]

    @bot.event
    async def on_ready() -> None:
        if bot.user:
            logger.info(f"Logged in as {bot.user} (ID: {bot.user.id})")
            logger.info(f"Connected to {len(bot.guilds)} guild(s)")
            logger.info(
                "Slash commands are synced via src/frameworks_drivers/discord/sync_commands.py"
            )
        else:
            logger.warning("Bot user not initialized")

    @bot.event
    async def on_message(message: discord.Message) -> None:
        if message.author.bot:
            return

        logger.debug(f"Message received from {message.author.name}: {message.content}")

        if not bot.user:
            return

        should_respond = False
        if message.channel.type == discord.ChannelType.private:
            should_respond = True
            logger.info(f"Direct message from {message.author.name}")
        elif message.mentions and bot.user in message.mentions:
            should_respond = True
            logger.info(f"Mentioned by {message.author.name}")
        elif (
            message.reference
            and message.reference.message_id
            and message.reference.resolved
        ):
            referenced_message = message.reference.resolved
            if (
                isinstance(referenced_message, discord.Message)
                and referenced_message.author == bot.user
            ):
                should_respond = True
                logger.info(f"Reply to bot from {message.author.name}")

        if not should_respond:
            return

        lock = get_lock(message.channel.id)
        await handle_message_processing(message, message_processor, bot, lock)

    @bot.tree.command(name="help", description="Show help information")
    async def help_command(interaction: discord.Interaction) -> None:
        embed = discord.Embed(
            title="Help",
            description="Available commands:",
            color=discord.Color.blue(),
        )
        embed.add_field(
            name="@bot",
            value="Trigger the bot to respond to your message",
            inline=False,
        )
        embed.add_field(
            name="/help",
            value="Show this help message",
            inline=False,
        )
        embed.add_field(
            name="/chat <query>",
            value="Ask the bot a question via slash command",
            inline=False,
        )
        embed.add_field(
            name="/clear",
            value="Clear conversation history (admin only)",
            inline=False,
        )
        await interaction.response.send_message(embed=embed)

    @bot.tree.command(name="chat", description="Ask the bot a question")
    async def chat(interaction: discord.Interaction, query: str) -> None:
        if interaction.channel is None:
            await interaction.response.send_message(
                "Error: Could not determine channel."
            )
            return
        channel_id = interaction.channel.id
        lock = get_lock(channel_id)
        await interaction.response.defer(ephemeral=False)
        async with lock:
            response = await asyncio.to_thread(
                message_processor.execute,
                channel_id,
                query,
                author_name=interaction.user.name,
                bot_name=bot.user.name if bot.user else "Bot",
            )
        await interaction.followup.send(response)

    @bot.tree.command(
        name="clear", description="Clear conversation history"
    )
    @app_commands.checks.has_permissions(manage_messages=True)
    async def clear(interaction: discord.Interaction) -> None:
        if interaction.channel is None:
            await interaction.response.send_message(
                "Error: Could not determine channel."
            )
            return
        channel_id = interaction.channel.id
        view = ConfirmClearView(clear_history_use_case, channel_id, interaction.user.id)
        embed = discord.Embed(
            title="Confirm Clear",
            description=f"Are you sure you want to clear the conversation history in <#{channel_id}>?",
            color=discord.Color.orange(),
        )
        msg = await interaction.response.send_message(embed=embed, view=view)
        view.message = msg  # type: ignore[attr-defined]
        await view.wait()

    @bot.event
    async def on_error(event: str, *args: Any, **kwargs: Any) -> None:
        logger.error(f"Error in event {event}: {args}, {kwargs}")

    return bot


async def main() -> None:
    """Main entry point for the Discord bot."""
    settings = get_settings()
    bot = setup_discord_bot()

    if not settings.DISCORD_TOKEN:
        logger.error("DISCORD_TOKEN not found in environment variables")
        raise ValueError("DISCORD_TOKEN is required")

    await bot.start(settings.DISCORD_TOKEN)
