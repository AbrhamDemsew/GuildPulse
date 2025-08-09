import os
import random
import re

import discord
import requests
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
OLLAMA_API_URL = "https://owebui.nclsp.com/ollama/v1/chat/completions"
OLLAMA_API_KEY = os.getenv("OLLAMA_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
bot = commands.Bot(command_prefix="*", intents=intents)

conversation_history = {}


def generate_response(channel_id, messages):
    payload = {"model": "mannix/gemma2-9b-sppo-iter3:latest", "messages": messages}
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OLLAMA_API_KEY}",
        "accept": "application/json",
    }
    response = requests.post(
        OLLAMA_API_URL, headers=headers, json=payload, timeout=None
    )
    response_json = response.json()
    print(f"Response from Ollama API: {response_json}")
    if "choices" in response_json and len(response_json["choices"]) > 0:
        return response_json["choices"][0]["message"]["content"]
    else:
        return "API related Error"


def fetch_url_content(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text[:1000]
        else:
            return "Failed to fetch content from the URL."
    except Exception as e:
        return f"Error fetching content: {e}"


def describe_image(image_url):
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "What’s in this image?"},
                    {"type": "image_url", "image_url": {"url": image_url}},
                ],
            }
        ],
        "max_tokens": 300,
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}",
    }
    response = requests.post(
        "https://api.openai.com/v1/chat/completions", headers=headers, json=payload
    )
    response_json = response.json()
    if "choices" in response_json and len(response_json["choices"]) > 0:
        return response_json["choices"][0]["message"]["content"]
    else:
        return "Failed to describe the image."


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if bot.user.mentioned_in(message):
        user_message = message.content.replace(f"<@{bot.user.id}>", "").strip()
        urls = re.findall(r"(https?://\S+)", user_message)
        url_content = ""
        if urls:
            for url in urls:
                if message.embeds:
                    for embed in message.embeds:
                        if embed.description and len(embed.description.split()) > 10:
                            url_content += embed.description + "\n"
                        else:
                            url_content += fetch_url_content(url) + "\n"
                else:
                    url_content += fetch_url_content(url) + "\n"

        if message.channel.id not in conversation_history:
            conversation_history[message.channel.id] = []
        conversation = conversation_history[message.channel.id]

        conversation.append(
            {"role": "user", "content": f"{message.author.name}: {user_message}"}
        )

        channel_messages = [msg async for msg in message.channel.history(limit=10)]
        channel_messages.reverse()

        api_messages = [
            {
                "role": "system",
                "content": "Tu agis selon les demandes des utilisateurs et tu discutes en utilisant la syntaxe de Discord, des emojis, et en parlant comme tes interlocuteurs. Sois créatif et réponds différemment à chaque fois, en prenant en compte le contexte et les conversations précédentes. Imite la manière de parler des utilisateurs, en utilisant leur ton, leur langage et leur style, ainsi que des emojis, sauf s'ils te demandent explicitement de faire autrement. Si les utilisateurs demandent du code, adopte le rôle d'un expert et fournis des extraits de code bien écrits, concis et corrects. N'inclus jamais le nom du bot ou des mentions d'utilisateur dans tes réponses, sauf si c'est demandé directement ou si tu veux t'adresser spécifiquement à quelqu'un.",
            }
        ]
        for msg in channel_messages:
            if msg.author != bot.user:
                api_messages.append(
                    {"role": "user", "content": f"{msg.author.name}: {msg.content}"}
                )
            else:
                api_messages.append({"role": "assistant", "content": msg.content})

        api_messages.extend(conversation)
        if url_content:
            api_messages.append(
                {"role": "system", "content": f"URL content: {url_content}"}
            )

        if message.attachments:
            for attachment in message.attachments:
                if any(
                    ext in attachment.url.lower()
                    for ext in [".png", ".jpg", ".jpeg", ".gif"]
                ):
                    image_description = describe_image(attachment.url)
                    api_messages.append(
                        {
                            "role": "system",
                            "content": f"Image description: {image_description}",
                        }
                    )

        response = generate_response(message.channel.id, api_messages)
        await message.channel.send(f"{response}")
        conversation.append({"role": "assistant", "content": response})
    else:
        if random.random() < 0.05:
            user_message = message.content
            urls = re.findall(r"(https?://\S+)", user_message)
            url_content = ""
            if urls:
                for url in urls:
                    if message.embeds:
                        for embed in message.embeds:
                            if (
                                embed.description
                                and len(embed.description.split()) > 10
                            ):
                                url_content += embed.description + "\n"
                            else:
                                url_content += fetch_url_content(url) + "\n"
                    else:
                        url_content += fetch_url_content(url) + "\n"

            if message.channel.id not in conversation_history:
                conversation_history[message.channel.id] = []
            conversation = conversation_history[message.channel.id]

            conversation.append(
                {"role": "user", "content": f"{message.author.name}: {user_message}"}
            )

            channel_messages = [msg async for msg in message.channel.history(limit=20)]
            channel_messages.reverse()

            api_messages = [
                {
                    "role": "system",
                    "content": "You act as the user ask for and discuss using the discord syntax, emojis, and speaking like your interlocutors. You should never add 'User: <username> Message:' to your response",
                }
            ]
            for msg in channel_messages:
                if msg.author != bot.user:
                    api_messages.append(
                        {
                            "role": "user",
                            "content": f"User: {msg.author.name} Message: {msg.content}",
                        }
                    )
                else:
                    api_messages.append({"role": "assistant", "content": msg.content})

            api_messages.extend(conversation)
            if url_content:
                api_messages.append(
                    {"role": "system", "content": f"URL content: {url_content}"}
                )

            if message.attachments:
                for attachment in message.attachments:
                    if attachment.url.lower().endswith(
                        (".png", ".jpg", ".jpeg", ".gif")
                    ):
                        image_description = describe_image(attachment.url)
                        api_messages.append(
                            {
                                "role": "system",
                                "content": f"Image description: {image_description}",
                            }
                        )

            response = generate_response(message.channel.id, api_messages)
            await message.channel.send(f"{response}")
            conversation.append({"role": "assistant", "content": response})


bot.run(DISCORD_TOKEN)
