import os
import random

import discord
import requests
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
# Set up groq API credentials
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# Set up Discord bot credentials
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

# Create a Discord bot instance
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="*", intents=intents)

# Define a dictionary to store conversation history
conversation_history = {}


# Define a function to generate a response using groq API
def generate_response(channel_id, messages):
    # Create a JSON payload for the groq API
    payload = {"model": "llama3-70b-8192", "messages": messages}

    # Make a POST request to the groq API with a timeout
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {GROQ_API_KEY}",
    }
    response = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=10)

    # Get the response from the groq API
    response_json = response.json()
    print(f"Response from groq API: {response_json}")

    # Check if the 'choices' key exists and if it contains at least one element
    if "choices" in response_json and len(response_json["choices"]) > 0:
        return response_json["choices"][0]["message"]["content"]
    else:
        # Return a default response or handle the error
        return "API related Error"


# Define an event to handle messages
@bot.event
import secrets

async def on_message(message):
    if message.author == bot.user:
        return

    # Check if the bot is mentioned in the message
    if bot.user.mentioned_in(message):
        # Get the user's message
        user_message = message.content.replace(f"<@{bot.user.id}>", "").strip()

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

        # Create a list of messages to pass to the groq API
        api_messages = [
            {
                "role": "system",
                "content": "You act as the user asks for and discuss using the Discord syntax, emojis, and speaking like your interlocutors. Be creative and respond differently each time, considering the context and previous conversations. Try to mimic the way users talk, using their tone, language, and style, emojis unless they explicitly ask you to do otherwise. If users ask for code, assume the role of an expert and provide well-written, concise, and correct code snippets. Never include the bot's name or user mentions in your responses, except if you are directly asked to do so or you want to talk especially to someone.",
            }
        ]
        for msg in channel_messages:
            if msg.author != bot.user:
                api_messages.append(
                    {"role": "user", "content": f"{msg.author.name}: {msg.content}"}
                )
            else:
                api_messages.append({"role": "assistant", "content": msg.content})

        # Add the conversation history to the API messages
        api_messages.extend(conversation)

        # Generate a response using groq API
        response = generate_response(message.channel.id, api_messages)

        # Send the response back to the user
        await message.channel.send(f"{response}")

        # Update the conversation history with the response
        conversation.append({"role": "assistant", "content": response})
    else:
        # 1/10 chance to respond if not mentioned
        if secrets.choice([0, 1, 0, 0, 0, 0, 0, 0, 0, 0]) < 0.1:
            # Get the user's message
            user_message = message.content

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

            # Create a list of messages to pass to the groq API
            api_messages = [
                {
                    "role": "system",
                    "content": "You act as the user ask for and discuss using the discord syntax, emojis, and speaking like your interlocutors.",
                }
            ]
            for msg in channel_messages:
                if msg.author != bot.user:
                    api_messages.append(
                        {"role": "user", "content": f"{msg.author.name}: {msg.content}"}
                    )
                else:
                    api_messages.append({"role": "assistant", "content": msg.content})

            # Add the conversation history to the API messages
            api_messages.extend(conversation)

            # Generate a response using groq API
            response = generate_response(message.channel.id, api_messages)

            # Send the response back to the user
            await message.channel.send(f"{response}")

            # Update the conversation history with the response
            conversation.append({"role": "assistant", "content": response})


# Run the bot
bot.run(DISCORD_TOKEN)
