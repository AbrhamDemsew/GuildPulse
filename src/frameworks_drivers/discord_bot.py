import random
import re
from typing import List

import discord
import requests
from bs4 import BeautifulSoup
from discord.ext import commands

from domain.entities import ConversationHistory
from interface_adapters.api_client import OllamaClient, OpenAIClient
from use_cases.message_processing import MessageProcessor


def setup_discord_bot(
    discord_token: str,
    ollama_api_url: str,
    ollama_api_key: str,
    openai_url,
    openai_api_key: str,
):
    intents = discord.Intents.default()
    intents.messages = True
    intents.message_content = True
    bot = commands.Bot(command_prefix="*", intents=intents)

    conversation_history = ConversationHistory()
    ollama_api_client = OllamaClient(ollama_api_url, ollama_api_key)
    openai_api_client = OpenAIClient(openai_url, openai_api_key)
    message_processor = MessageProcessor(
        conversation_history, ollama_api_client, openai_api_client
    )

    @bot.event
    async def on_message(message: discord.Message) -> None:
        if message.author == bot.user:
            return

        user_message = (
            message.content.replace(f"<@{bot.user.id}>", "").strip()
            if bot.user.mentioned_in(message)
            else message.content
        )
        urls = re.findall(r"(https?://\\S+)", user_message)
        url_content = ""
        if urls:
            for url in urls:
                url_content += fetch_url_content(url) + "\\n"

        image_url = None
        if message.attachments:
            for attachment in message.attachments:
                if any(
                    ext in attachment.url.lower()
                    for ext in [".png", ".jpg", ".jpeg", ".gif"]
                ):
                    image_url = attachment.url
                    break

        if bot.user.mentioned_in(message) or random.random() < 0.05:
            await message.channel.typing()
            await process_message(message, user_message, urls, url_content, image_url)

    async def process_message(
        message: discord.Message,
        user_message: str,
        urls: List[str],
        url_content: str,
        image_url: str = None,
    ) -> None:
        channel_id = message.channel.id
        conversation = conversation_history.get_history(channel_id)

        conversation.append(
            {"role": "user", "content": f"{message.author.name}: {user_message}"}
        )

        api_messages = [
            {
                "role": "system",
                "content": (
                    "Tu agis selon les demandes des utilisateurs et tu discutes en utilisant la syntaxe de Discord, "
                    "des emojis, et en parlant comme tes interlocuteurs. Sois créatif et réponds différemment à chaque "
                    "fois, en prenant en compte le contexte et les conversations précédentes. Imite la manière de parler des "
                    "utilisateurs, en utilisant leur ton, leur langage et leur style, ainsi que des emojis, sauf s'ils te "
                    "demandent explicitement de faire autrement. Si les utilisateurs demandent du code, adopte le rôle "
                    "d'un expert et fournis des extraits de code bien écrits, concis et corrects. N'inclus jamais le nom du bot "
                    "ou des mentions d'utilisateur dans tes réponses, sauf si c'est demandé directement ou si tu veux "
                    "t'adresser spécifiquement à quelqu'un."
                ),
            }
        ]

        api_messages.extend(conversation)
        if url_content:
            api_messages.append(
                {"role": "system", "content": f"URL content: {url_content}"}
            )

        recent_messages = [msg async for msg in message.channel.history(limit=2)]
        if recent_messages and recent_messages[0].attachments:
            for attachment in recent_messages[0].attachments:
                if any(
                    ext in attachment.url.lower()
                    for ext in [".png", ".jpg", ".jpeg", ".gif"]
                ):
                    image_url = attachment.url
                    break

        response = message_processor.process_message(
            channel_id, api_messages, image_url
        )
        await message.channel.send(f"{response}")
        conversation_history.add_message(
            channel_id, {"role": "assistant", "content": response}
        )

    def fetch_url_content(url: str) -> str:
        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            return soup.get_text()[:1000]
        except requests.RequestException as e:
            return f"Error fetching content: {e}"

    bot.run(discord_token)
