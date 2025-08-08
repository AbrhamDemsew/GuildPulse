import os
import random
import re

import discord
import requests
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
# Set up groq API credentials
# GROQ_API_KEY = os.getenv("GROQ_API_KEY")
# GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
OLLAMA_API_URL = "https://owebui.nclsp.com/ollama/v1/chat/completions"
OLLAMA_API_KEY = os.getenv("OLLAMA_API_KEY")

# Set up Discord bot credentials
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

# Create a Discord bot instance
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
bot = commands.Bot(command_prefix="*", intents=intents)

# Define a dictionary to store conversation history
conversation_history = {}


# Define a function to generate a response using Ollama API
def generate_response(channel_id, messages):
    # Create a JSON payload for the Ollama API
    payload = {"model": "mannix/gemma2-9b-sppo-iter3:latest", "messages": messages}

    # Make a POST request to the Ollama API
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OLLAMA_API_KEY}",
        "accept": "application/json",
    }
    response = requests.post(
        OLLAMA_API_URL, headers=headers, json=payload, timeout=None
    )

    # Get the response from the Ollama API
    response_json = response.json()
    print(f"Response from Ollama API: {response_json}")

    # Check if the 'choices' key exists and if it contains at least one element
    if "choices" in response_json and len(response_json["choices"]) > 0:
        return response_json["choices"][0]["message"]["content"]
    else:
        # Return a default response or handle the error
        return "API related Error"


# Define a function to fetch content from a URL
def fetch_url_content(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text[:1000]  # Limit content to 1000 characters
        else:
            return "Failed to fetch content from the URL."
    except Exception as e:
        return f"Error fetching content: {e}"


# Define an event to handle messages
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # Check if the bot is mentioned in the message
    if bot.user.mentioned_in(message):
        # Get the user's message
        user_message = message.content.replace(f"<@{bot.user.id}>", "").strip()

        # Check for links in the message
        urls = re.findall(r"(https?://\S+)", user_message)
        url_content = ""
        if urls:
            for url in urls:
                # Check if the message has embeds
                if message.embeds:
                    for embed in message.embeds:
                        if embed.description and len(embed.description.split()) > 10:
                            url_content += embed.description + "\n"
                        else:
                            url_content += fetch_url_content(url) + "\n"
                else:
                    url_content += fetch_url_content(url) + "\n"

        # Get the conversation history for the channel
        if message.channel.id not in conversation_history:
            conversation_history[message.channel.id] = []
        conversation = conversation_history[message.channel.id]

        # Add the user's message to the conversation history
        conversation.append(
            {"role": "user", "content": f"{message.author.name}: {user_message}"}
        )

        # Get the last 10 messages of the channel
        channel_messages = [msg async for msg in message.channel.history(limit=10)]
        channel_messages.reverse()

        # Create a list of messages to pass to the Ollama API
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

        # Add the conversation history and URL content to the API messages
        api_messages.extend(conversation)
        if url_content:
            api_messages.append(
                {"role": "system", "content": f"URL content: {url_content}"}
            )

        # Generate a response using Ollama API
        response = generate_response(message.channel.id, api_messages)

        # Send the response back to the user
        await message.channel.send(f"{response}")

        # Update the conversation history with the response
        conversation.append({"role": "assistant", "content": response})
    else:
        # 1/20 chance to respond if not mentioned
        if random.random() < 0.05:
            # Get the user's message
            user_message = message.content

            # Check for links in the message
            urls = re.findall(r"(https?://\S+)", user_message)
            url_content = ""
            if urls:
                for url in urls:
                    # Check if the message has embeds
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

            # Get the conversation history for the channel
            if message.channel.id not in conversation_history:
                conversation_history[message.channel.id] = []
            conversation = conversation_history[message.channel.id]

            # Add the user's message to the conversation history
            conversation.append(
                {"role": "user", "content": f"{message.author.name}: {user_message}"}
            )

            # Get the last 10 messages of the channel
            channel_messages = [msg async for msg in message.channel.history(limit=20)]
            channel_messages.reverse()

            # Create a list of messages to pass to the Ollama API
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

            # Add the conversation history and URL content to the API messages
            api_messages.extend(conversation)
            if url_content:
                api_messages.append(
                    {"role": "system", "content": f"URL content: {url_content}"}
                )

            # Generate a response using Ollama API
            response = generate_response(message.channel.id, api_messages)

            # Send the response back to the user
            await message.channel.send(f"{response}")

            # Update the conversation history with the response
            conversation.append({"role": "assistant", "content": response})


# Run the bot
bot.run(DISCORD_TOKEN)
