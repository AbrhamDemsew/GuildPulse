# Discord Bot with OpenAI Integration

A modern Discord bot built with Python 3.13, featuring OpenAI API integration for intelligent conversations. Production-ready with Docker support, comprehensive testing, and clean architecture.

## 🚀 Features

- **Intelligent Conversations**: Powered by OpenAI API
- **Vision Support**: Analyze images attached to Discord messages
- **Context-Aware Responses**: Maintains conversation history across channels
- **Smart Mention Detection**: Only responds when mentioned, in DM, or replying to the bot
- **Message Management**: Keeps track of the last 100 messages per channel
- **Async Architecture**: Non-blocking operations for optimal performance
- **Modern Stack**: Python 3.13, discord.py 2.0, Pydantic, standard logging
- **Production Ready**: Docker support, health checks, comprehensive logging
- **Well-Tested**: Complete test suite with pytest
- **Clean Architecture**: Separated concerns for maintainability

## 📋 Prerequisites

- Python 3.13 or higher
- Docker (optional, for containerized deployment)
- Discord Bot Token
- OpenAI API Key (or compatible API key)

## 🏗️ Architecture

The bot follows Clean Architecture principles with clear separation of concerns:

```
src/
├── config.py              # Configuration management (Pydantic)
├── domain/                # Core business entities
│   └── entities.py        # ConversationHistory
├── frameworks_drivers/    # External system integrations
│   └── discord_bot.py     # Discord bot implementation
├── interface_adapters/    # API clients
│   └── openai_client.py   # OpenAI API client
├── use_cases/             # Business logic
│   └── message_processing.py
└── main.py                # Application entry point
```

See [Architecture Documentation](docs/ARCHITECTURE.md) for detailed architecture information.

## 🔧 Installation

### Local Development

1. Clone the repository:
```bash
git clone https://github.com/ncls-p/py-besto-bot.git
cd py-besto-bot
```

2. Create a virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: `.venv\Scripts\activate`
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
cp .env.example .env
```

5. Edit `.env` and add your configuration:
```env
DISCORD_TOKEN="your-discord-token"
OPENAI_API_KEY="your-openai-api-key"
OPENAI_BASE_URL="https://api.openai.com/v1"
OPENAI_MODEL="gpt-4o-mini"
OPENAI_MAX_TOKENS=500
OPENAI_VISION_ENABLED=true
OPENAI_VISION_MAX_IMAGES=4
```

### Docker Deployment

1. Build the Docker image:
```bash
docker build -t py-besto-bot .
```

2. Run with Docker Compose:
```bash
docker-compose up -d
```

3. Check logs:
```bash
docker-compose logs -f
```

## ⚙️ Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DISCORD_TOKEN` | Yes | - | Discord bot token |
| `OPENAI_API_KEY` | Yes | - | OpenAI API key |
| `OPENAI_BASE_URL` | No | `https://api.openai.com/v1` | Custom API base URL |
| `OPENAI_MODEL` | No | `gpt-4o-mini` | Default model name |
| `OPENAI_MAX_TOKENS` | No | `500` | Maximum tokens for generation |
| `OPENAI_TEMPERATURE` | No | `0.7` | Generation temperature |
| `OPENAI_VISION_ENABLED` | No | `true` | Enable image analysis support |
| `OPENAI_VISION_MAX_IMAGES` | No | `4` | Maximum images per message |
| `LOG_LEVEL` | No | `INFO` | Logging level |
| `DEBUG` | No | `false` | Debug mode |

### Configuration Examples

#### Using Ollama (Local LLM)
```env
OPENAI_BASE_URL="http://localhost:11434/v1"
OPENAI_MODEL="llama2"
OPENAI_API_KEY="ollama"
```

#### Using a Custom API Proxy
```env
OPENAI_BASE_URL="https://your-proxy.com/v1"
OPENAI_MODEL="custom-model"
OPENAI_API_KEY="your-proxy-key"
```

## 📖 Usage

### Basic Commands

- **@bot**: Mention the bot to trigger a response
- **\*help**: Show help information
- **\*clear**: Clear conversation history (admin only)

### Vision (Image) Support

When you mention the bot or reply to its previous messages, it can now analyze images:

1. Attach one or more images to your Discord message
2. Add optional text with your question about the images
3. The bot will analyze the images and respond accordingly

Example:
```
User (@bot): Here's a screenshot of the error. What should I do?
[Attachment: error.png]
Bot: D'après l'image, il semble y avoir une exception non gérée...
```

You can configure vision support via environment variables:
- `OPENAI_VISION_ENABLED=true` (enabled by default)
- `OPENAI_VISION_MAX_IMAGES=4` (max 4 images per message)

### Example Usage

```
User: @bot Hello, how are you?
Bot: Salut ! Je vais bien, merci de demander ! Comment puis-je t'aider aujourd'hui ?

User: @bot Qu'est-ce que tu as fait aujourd'hui?
Bot: J'ai passé le temps à apprendre de nouvelles choses. Et toi ?
```

### Discord Slash Commands

The bot supports Discord slash commands:

- `/help` - Show help information
- `/clear` - Clear conversation history (admin only)

## 🧪 Testing

### Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_openai_client.py

# Run with verbose output
pytest -v
```

### Code Quality

```bash
# Format code with black
black src/

# Check code style with flake8
flake8 src/

# Type check with mypy
mypy src/

# Install and run pre-commit hooks
pre-commit install
pre-commit run --all-files
```

## 🚢 Docker

### Docker Compose

The `docker-compose.yml` file includes:

- Automatic restart policy
- Health checks
- JSON file logging with rotation
- Network isolation
- Container labels

### Docker Commands

```bash
# Build and start
docker-compose up -d --build

# View logs
docker-compose logs -f

# Stop container
docker-compose down

# Restart container
docker-compose restart

# Execute command in container
docker-compose exec bot python -c "print('Hello')"
```

## 📊 Development

### Project Structure

```
src/
├── config.py              # Configuration management
├── main.py                # Application entry point
├── domain/                # Domain entities
├── frameworks_drivers/    # Discord bot integration
├── interface_adapters/    # API clients
├── use_cases/             # Business logic
└── utils/                 # Utility functions
```

### Code Style

- **Language**: Python 3.13
- **Formatter**: Black (80 character lines)
- **Linter**: Flake8
- **Type Checker**: Mypy
- **Documentation**: Google style docstrings

### Running Locally

```bash
# Run the bot
python src/main.py

# Run with specific configuration
LOG_LEVEL=DEBUG DEBUG=true python src/main.py
```

## 🔐 Security

### Best Practices

1. **Never commit**: `.env` file with sensitive data
2. **Use environment variables**: Store API keys and tokens
3. **Input validation**: All inputs are validated
4. **Non-root user**: Docker containers run as non-root
5. **HTTPS**: Always use secure connections

### .gitignore

The `.gitignore` file includes:
- Environment variables (.env files)
- Virtual environments (.venv/)
- Logs (logs/)
- Python cache (__pycache__/)
- IDE files (.vscode/, .idea/)

## 📝 Logging

### Log Levels

- `DEBUG`: Detailed diagnostic information (development)
- `INFO`: General information about bot operations
- `WARNING`: Warning messages
- `ERROR`: Error messages
- `CRITICAL`: Critical errors

### Log Files

Logs are stored in `logs/` directory:
- `debug_YYYY-MM-DD.log` - Debug logs (development)
- `info_YYYY-MM-DD.log` - Info logs (production)
- Logs are rotated and compressed automatically

### Viewing Logs

```bash
# View current log
tail -f logs/info_$(date +%Y-%m-%d).log

# Search for errors
grep ERROR logs/*.log

# View debug logs
tail -f logs/debug_$(date +%Y-%m-%d).log
```

## 🐛 Troubleshooting

### Common Issues

**Bot won't start:**
```bash
# Check Discord token is set
echo $DISCORD_TOKEN

# Check OpenAI API key is set
echo $OPENAI_API_KEY

# Check logs for errors
docker-compose logs
```

**API connection issues:**
```bash
# Test OpenAI connection
curl -X POST https://api.openai.com/v1/chat/completions \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"gpt-4o-mini","messages":[{"role":"user","content":"Hello"}]}'
```

**Docker issues:**
```bash
# Rebuild Docker image
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Check container status
docker-compose ps
```

## 📚 Documentation

- [Architecture Documentation](docs/ARCHITECTURE.md) - Detailed system architecture
- [API Documentation](docs/API.md) - OpenAI API integration details
- [Development Guide](docs/DEVELOPMENT.md) - Development workflow and guidelines

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and code quality checks
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Development Workflow

```bash
# Install pre-commit hooks
pre-commit install

# Make changes and commit
git add .
git commit -m "feat: add new feature"

# Pre-commit checks will run automatically
```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- OpenAI for the incredible API
- discord.py team for the Discord library
- The Python community

## 🔗 Links

- [Discord API Documentation](https://discord.com/developers/docs)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)

## 📞 Support

For issues, questions, or contributions, please open an issue on GitHub.

## 🎯 Future Roadmap

- [ ] Database integration for conversation persistence
- [ ] Rate limiting and API usage tracking
- [ ] Admin dashboard and web interface
- [ ] Plugin system for custom commands
- [ ] Multi-language support (i18n)
- [ ] Webhook support for external integrations
- [ ] Metrics and observability (Prometheus, Grafana)

---

**Built with ❤️ using Python 3.13, discord.py 2.0, and OpenAI API**
