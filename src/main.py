import os

from dotenv import load_dotenv

from frameworks_drivers.discord_bot import setup_discord_bot

load_dotenv()


def main():
    discord_token = os.getenv("DISCORD_TOKEN", "")
    ollama_api_url = "https://owebui.nclsp.com/ollama/v1/chat/completions"
    ollama_api_key = os.getenv("OLLAMA_API_KEY", "")
    hyperbolic_url = "https://api.hyperbolic.xyz/v1/image/generation"
    hyperbolic_api_key = os.getenv("HYPERBOLIC_API_KEY", "")
    openai_api_url = "https://api.openai.com/v1/chat/completions"
    openai_api_key = os.getenv("OPENAI_API_KEY", "")

    setup_discord_bot(
        DISCORD_TOKEN,
        OLLAMA_API_URL,
        OLLAMA_API_KEY,
        HYPERBOLIC_URL,
        HYPERBOLIC_API_KEY,
        OPENAI_API_URL,
        OPENAI_API_KEY,
    )


if __name__ == "__main__":
    main()
