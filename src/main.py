import logging
import os
from dotenv import load_dotenv
from frameworks_drivers.discord_bot import setup_discord_bot

load_dotenv()

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    discord_token = os.getenv("DISCORD_TOKEN", "")
    ollama_api_url = "https://owebui.nclsp.com/ollama/v1/chat/completions"
    ollama_api_key = os.getenv("OLLAMA_API_KEY", "")
    hyperbolic_url = "https://api.hyperbolic.xyz/v1/image/generation"
    hyperbolic_api_key = os.getenv("HYPERBOLIC_API_KEY", "")
    openai_api_url = "https://api.openai.com/v1/chat/completions"
    openai_api_key = os.getenv("OPENAI_API_KEY", "")

    logger.info("Starting the Discord bot...")
    setup_discord_bot(
        discord_token,
        ollama_api_url,
        ollama_api_key,
        hyperbolic_url,
        hyperbolic_api_key,
        openai_api_url,
        openai_api_key,
    )


if __name__ == "__main__":
    main()
