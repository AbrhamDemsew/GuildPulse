# GuildPulse

GuildPulse is a production-oriented Discord community assistant with OpenAI integration, built on clean architecture and domain-driven design. It manages per-channel conversation history, supports vision attachments, slash commands, and SQLite-backed persistence for guild deployments.

## Features

- AI-powered replies when mentioned, in DMs, or when replying to the bot
- Vision support for image attachments in guild channels
- Rolling conversation history with configurable retention
- Slash commands (`/chat`, `/help`, `/clear`, `/usage`, `/config`, `/kb`)
- Per-guild settings: custom prompts, models, quotas, channel allowlists
- Moderation pipeline with audit logging and per-user rate limits
- Knowledge base with chunking and retrieval-augmented replies
- Usage analytics with daily token/message quotas
- FastAPI admin API for guilds, analytics, moderation, knowledge, plugins, and ops
- Plugin registry for extensible guild commands
- SQLite persistence across channels, settings, usage, and knowledge
- Rate limiting, structured logging, and Docker deployment
- 200+ pytest tests with layered coverage (domain, application, infrastructure, Discord adapters)

## Architecture

```
guildpulse/
├── config.py                 # Pydantic settings
├── main.py                   # Entry point
├── domain/                   # Aggregates, value objects, domain events
├── application/              # Use cases and ports
├── infrastructure/           # OpenAI adapter, SQLite/memory repos, DI
└── frameworks_drivers/       # discord.py integration
```

See [docs/architecture.md](docs/architecture.md) and [docs/TESTING.md](docs/TESTING.md).

## Requirements

- Python 3.12+
- Discord bot token
- OpenAI-compatible API key

## Local setup

```bash
pip install -r requirements.txt
cp .env.example .env
# edit .env with DISCORD_TOKEN and OPENAI_API_KEY
python -m guildpulse.main
```

## Docker

```bash
docker build -t guildpulse .
docker compose up -d
docker compose logs -f
```

## Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DISCORD_TOKEN` | Yes | — | Discord bot token |
| `OPENAI_API_KEY` | Yes | — | OpenAI or compatible API key |
| `OPENAI_BASE_URL` | No | `https://api.openai.com/v1` | API base URL |
| `OPENAI_MODEL` | No | `gpt-4o-mini` | Model name |
| `OPENAI_MAX_TOKENS` | No | `500` | Max generation tokens |
| `OPENAI_TEMPERATURE` | No | `0.7` | Sampling temperature |
| `LOG_LEVEL` | No | `INFO` | Log level |
| `DEBUG` | No | `false` | Debug mode |

## Testing

```bash
pytest
pytest --cov=guildpulse --cov-report=term-missing -v
pytest -m unit
pytest -m integration
```

## Author

Abrham — eyobsmart3@gmail.com

## License

MIT
