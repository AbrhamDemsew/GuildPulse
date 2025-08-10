import os

from dotenv import load_dotenv

from frameworks_drivers.discord_bot import setup_discord_bot

load_dotenv()


def main():
    DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
    OLLAMA_API_URL = "https://owebui.nclsp.com/ollama/v1/chat/completions"
    OLLAMA_API_KEY = os.getenv("OLLAMA_API_KEY")
    OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    setup_discord_bot(
        DISCORD_TOKEN, OLLAMA_API_URL, OLLAMA_API_KEY, OPENAI_API_URL, OPENAI_API_KEY
    )


if __name__ == "__main__":
    main()
