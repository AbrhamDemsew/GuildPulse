import asyncio
import logging
import re
from typing import Any

import discord
from discord import app_commands
from discord.ext import commands

from src.config import get_settings, setup_logging
from src.domain.entities import ConversationHistory
from src.interface_adapters.openai_client import OpenAIClient
from src.use_cases.message_processing import MessageProcessor

logger = logging.getLogger(__name__)


def setup_discord_bot() -> commands.Bot:
    """Setup and configure the Discord bot with modern discord.py 2.0."""
    settings = get_settings()

    setup_logging(settings)

    logger.info("Starting Discord bot initialization...")

    intents = discord.Intents.default()
    intents.message_content = True
    intents.messages = True

    bot = commands.Bot(command_prefix=commands.when_mentioned_or("*"), intents=intents)

    history = ConversationHistory()
    openai_client = OpenAIClient(
        api_key=settings.OPENAI_API_KEY,
        base_url=settings.OPENAI_BASE_URL,
        model=settings.OPENAI_MODEL,
        max_tokens=settings.OPENAI_MAX_TOKENS,
        temperature=settings.OPENAI_TEMPERATURE,
    )
    message_processor = MessageProcessor(history, openai_client)

    logger.info("Discord bot initialized with OpenAI client")

    @bot.event
    async def on_ready() -> None:
        if bot.user:
            logger.info(f"Logged in as {bot.user} (ID: {bot.user.id})")
            logger.info(f"Connected to {len(bot.guilds)} guild(s)")
            try:
                synced = await bot.tree.sync()
                logger.info(f"Synced {len(synced)} application commands")
            except Exception as e:
                logger.error(f"Error syncing commands: {e}")
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
        elif message.reference and message.reference.message_id and message.reference.resolved:
            referenced_message = message.reference.resolved
            if (
                isinstance(referenced_message, discord.Message)
                and referenced_message.author == bot.user
            ):
                should_respond = True
                logger.info(f"Reply to bot from {message.author.name}")

        if not should_respond:
            return

        await handle_message_processing(message, message_processor, settings)

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
            name="/clear",
            value="Clear conversation history (admin only)",
            inline=False,
        )
        await interaction.response.send_message(embed=embed)

    @bot.tree.command(name="clear", description="Clear conversation history")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def clear_history(interaction: discord.Interaction) -> None:
        if interaction.channel is None:
            await interaction.response.send_message("Error: Could not determine channel.")
            return
        channel_id = interaction.channel.id
        history.clear_history(channel_id)
        await interaction.response.send_message("Conversation history cleared!")

    @bot.event
    async def on_error(event: str, *args: Any, **kwargs: Any) -> None:
        logger.error(f"Error in event {event}: {args}, {kwargs}")

    return bot


async def handle_message_processing(
    message: discord.Message, message_processor: MessageProcessor, _settings: Any
) -> None:
    """Handle message processing for bot responses."""
    try:
        channel = message.channel
        channel_id = channel.id
        author_name = message.author.display_name

        user_message = message.content

        logger.debug(f"Processing user message from {author_name}: {user_message}")

        clean_message = user_message.replace(f"<@{message.author.id}>", "").strip()
        clean_message = re.sub(r"<@!?(\d+)>", "", clean_message).strip()

        if len(clean_message) > 500:
            clean_message = clean_message[:500] + "..."

        if not clean_message:
            clean_message = "[attachment]"

        message_processor.add_to_conversation(channel_id, "user", f"{author_name}: {clean_message}")

        async with channel.typing():
            response = await message_processor.generate_reply(channel_id)

        if response:
            await channel.send(response)
            message_processor.add_to_conversation(channel_id, "assistant", response)
        else:
            logger.warning("No response generated")

    except Exception as e:
        logger.error(f"Error processing message: {e}")
        await message.channel.send(f"Error processing your message: {e}")


async def main() -> None:
    """Main entry point for the Discord bot."""
    settings = get_settings()
    bot = setup_discord_bot()

    if not settings.DISCORD_TOKEN:
        logger.error("DISCORD_TOKEN not found in environment variables")
        raise ValueError("DISCORD_TOKEN is required")

    await bot.start(settings.DISCORD_TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
