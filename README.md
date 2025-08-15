# Discord Bot Project

## Overview

This project is a Discord bot that interacts with users using the Ollama and OpenAI APIs. The bot processes messages, fetches content from URLs, and generates responses using AI models.

## Project Structure

```
.env
.env.example
.gitignore
docker-compose.yml
Dockerfile
README.md
requirements.txt
src/
    domain/
        entities.py
    frameworks_drivers/
        discord_bot.py
    interface_adapters/
        api_client.py
    main.py
    use_cases/
        image_processing.py
        message_processing.py
```

### Key Files and Directories

- `.env`: Environment variables for the project.
- `.env.example`: Example environment variable settings.
- `.gitignore`: Files and directories to be ignored by Git.
- `docker-compose.yml`: Docker Compose configuration.
- `Dockerfile`: Docker configuration for setting up the environment.
- `requirements.txt`: List of Python package dependencies.
- `src/`: Source code directory.
  - `domain/entities.py`: Contains the `ConversationHistory` class.
  - `frameworks_drivers/discord_bot.py`: Contains the Discord bot setup and event handling.
  - `interface_adapters/api_client.py`: Contains the `OllamaClient` and `OpenAIClient` classes for API interactions.
  - `main.py` Entry point for the application.
  - `use_cases/`: Contains use case logic for message and image processing.

## Setup

### Prerequisites

- recommend Python 3.12.1+
- Docker (optional, for containerized deployment)

### Installation

1. Clone the repository:

   ```sh
   git clone https://github.com/ncls-p/py-besto-bot.git
   cd py-besto-bot
   ```

2. Create a virtual environment and activate it:

   ```sh
   python -m venv .venv
   source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
   ```

3. Install the dependencies:

   ```sh
   pip install -r requirements.txt
   ```

4. Copy the example environment file and set your environment variables:
   ```sh
   cp .env.example .env
   # Edit .env and set your DISCORD_TOKEN, OLLAMA_API_KEY, and OPENAI_API_KEY
   ```

### Running the Bot

1. Run the bot:
   ```sh
   python src/main.py
   ```

### Using Docker

1. Docker compose:

   ```sh
   docker compose up -d --build
   ```

## Usage

- The bot listens for messages in Discord and processes them using the Ollama and OpenAI APIs.
- It can fetch content from URLs, images and generate responses based on the content.

## Contributing

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes.
4. Commit your changes (`git commit -m 'Add some feature'`).
5. Push to the branch (`git push origin feature-branch`).
6. Open a pull request.

## License

This project is licensed under the MIT License.
