# AGENTS.md - Coding Guidelines for py-besto-bot

## Project Overview

This project is a Discord bot built with Python 3.14 using Clean Architecture principles. It features OpenAI API integration for intelligent conversations with vision support (image analysis), conversation history management, and is containerized with Docker using uv for package management.

## Build and Test Commands

### Running the Application

#### Local Development (with uv)
```bash
# Activate virtual environment
source .venv/bin/activate

# Run the bot
uv run python src/main.py

# Run with debug mode
DEBUG=true LOG_LEVEL=DEBUG uv run python src/main.py
```

#### Docker (Production)
```bash
# Build and start
docker-compose up -d --build

# View logs
docker-compose logs -f

# Stop container
docker-compose down
```

### Testing

```bash
# Activate virtual environment first
source .venv/bin/activate

# Run all tests
pytest

# Run single test file
pytest tests/test_message_processor.py

# Run single test
pytest tests/test_message_processor.py::test_generate_reply

# Run with coverage
pytest --cov=src --cov-report=html

# Run with verbose output
pytest -v

# Run with coverage and verbose
pytest --cov=src --cov-report=term-missing -v
```

### Code Quality Tools

```bash
# Activate virtual environment first
source .venv/bin/activate

# Format code with black
black src/

# Check code style with ruff (or flake8)
ruff check src/
# or
flake8 src/

# Format with ruff
ruff format src/

# Type check with mypy
mypy src/

# Install and run pre-commit hooks
pre-commit install
pre-commit run --all-files

# Run specific pre-commit hook
pre-commit run black --files src/main.py
```

### Install Dependencies

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Sync dependencies
uv sync

# Install pre-commit
uv pip install pre-commit
pre-commit install
```

## Architecture Pattern

This project follows **Clean Architecture** with Domain-Driven Design principles:

```
src/
├── config.py            # Configuration management (Pydantic)
├── main.py              # Application entry point
├── domain/              # Core business logic and entities
│   └── entities.py      # ConversationHistory
├── frameworks_drivers/  # External systems (Discord, AI)
│   └── discord/bot.py   # Discord bot implementation
├── interface_adapters/  # API clients and adapters
│   └── openai/client.py # OpenAI API client
├── use_cases/           # Business logic and orchestration
│   └── message_processing.py
└── utils/               # Utility functions
```

**Dependency Rules:**
- **Domain layer**: No external dependencies
- **Application layer**: Depends on domain layer
- **Infrastructure layer**: Depends on domain and application (adapters)
- **Frameworks layer**: Depends on application (DI through CompositionRoot)

## Code Style Guidelines

### Import Organization

Import modules in this specific order:
1. Standard library imports
2. Third-party imports
3. Local application imports

Example:
```python
import logging
import os
import sys
from typing import Any, Dict

import requests
from discord.ext import commands

from domain.entities import ConversationHistory
from frameworks_drivers.discord_bot import setup_discord_bot
```

### Code Quality Tools

- **Formatter:** Black (80 character line length)
- **Linter:** Ruff (E, W, F, I, B, C4, UP, ARG rules) or Flake8
- **Type Checker:** Mypy (strict mode with pydantic plugin)
- **Package Manager:** uv (fast Python package manager)
- **Imports Sorter:** isort (using Black profile)

### Naming Conventions

- **Classes:** PascalCase (`ConversationHistory`, `MessageProcessor`, `Settings`)
- **Functions:** snake_case (`generate_response`, `fetch_url_content`, `get_settings`)
- **Variables:** snake_case (`api_url`, `discord_token`, `history`)
- **Constants:** UPPER_CASE (not extensively used in this project)
- **Private methods:** _snake_case (`_validate_api_key`)

### Type Hints

Always use type hints for function parameters and return values:
```python
def generate_response(api_url: str, api_key: str, payload: Dict[str, Any]) -> str:
    ...
```

### Async/Await

Use async/await patterns for asynchronous operations:
```python
async def process_message(self, message: dict) -> str:
    response = await self.client.chat_completion_async(...)
    return response
```

### Logging

Use the `logging` module for debugging and information:
```python
import logging
logger = logging.getLogger(__name__)

logger.debug("Debug information")
logger.info("Informational message")
logger.warning("Warning message")
```

### Error Handling

Use try-except blocks with appropriate error logging:
```python
try:
    response = requests.get(url)
    response.raise_for_status()
    return response.text
except requests.RequestException as e:
    logger.error(f"Error fetching URL: {e}")
    return f"Error: {e}"
```

### Documentation

Add docstrings for all classes and public functions:
```python
class MessageProcessor:
    """Processes messages and generates AI responses."""
    def process_message(self, channel_id: int, messages: List[Dict[str, Any]]) -> str:
        """
        Process the message and return the response.
        """
        ...
```

## Code Quality Standards

### Function Length
Keep functions focused and under 50 lines. Extract complex logic into helper functions.

### Class Methods
Keep methods focused on a single responsibility. Aim for under 30 lines per method.

### Error Messages
Return descriptive error messages from functions that fail:
```python
if response is None:
    raise ValueError("API client returned None")
```

## Testing Guidelines

### Test Structure

- Place tests in `tests/` directory
- Use `test_` prefix for test files and `Test` prefix for test classes
- Use `async` marker for async tests: `@pytest.mark.asyncio`
- Follow test naming: `test_<function_name>`
- Use fixtures for common test data
- Mock external dependencies (API calls, etc.)

### Test Markers

- `unit`: Unit tests
- `integration`: Integration tests
- `slow`: Slow running tests
- `async`: Async tests
- `requires_api`: Tests that require API access

### Example Test

```python
@pytest.fixture
def mock_client():
    """Create a mock OpenAI client."""
    with patch("src.interface_adapters.openai_client.OpenAI") as mock_openai:
        client = OpenAIClient(
            api_key="test_key",
            base_url="https://test.com/v1",
            model="test-model",
        )
        mock_openai.return_value = Mock()
        return client

@pytest.mark.asyncio
async def test_generate_reply(message_processor):
    """Test generating a reply with conversation history."""
    message_processor.client.chat_completion_async = AsyncMock(return_value="Test response")
    result = await message_processor.generate_reply(123)
    assert result == "Test response"
```

## Development Workflow

### Adding New Features

1. Identify which layer the feature belongs to (domain, use_case, framework_driver, or interface_adapter)
2. Follow the existing pattern in that layer
3. Add logging for debugging
4. Test thoroughly before committing
5. Ensure Docker builds work correctly

### Code Review Checklist

- Imports are organized correctly
- Type hints are provided
- Logging is added for debugging
- Error handling is appropriate
- Function and class names follow conventions
- Docstrings are present for public APIs
- Pre-commit hooks pass
- Docker image builds successfully
- Tests pass locally

### Pre-commit Hooks

The project uses pre-commit hooks to ensure code quality:
- `trailing-whitespace`, `end-of-file-fixer`: Formatting
- `black`: Format code with Black (80 character lines)
- `flake8` / `ruff`: Lint code
- `mypy`: Type check code with Mypy
- `isort`: Sort imports
- `pytest`: Run tests

Install and enable hooks: `pre-commit install` then `pre-commit run --all-files`

### Commit Messages

Follow conventional commit format: `feat:`, `fix:`, `refactor:`, `chore:`

Examples:
```
feat: add uv support for containerized deployment
fix: remove duplicate decorators and format code
chore: update documentation to reflect current structure
```

## Special Configuration

### Environment Variables

The project uses Pydantic for configuration management. All environment variables are defined in `.env` file:
- `DISCORD_TOKEN`: Discord bot token (required)
- `OPENAI_API_KEY`: OpenAI API key (required)
- `OPENAI_BASE_URL`: API base URL (default: `https://api.openai.com/v1`)
- `OPENAI_MODEL`: Default model name (default: `gemma-3-27b-it-qat`)
- `OPENAI_MAX_TOKENS`: Maximum tokens (default: `500`)
- `OPENAI_TEMPERATURE`: Generation temperature (default: `0.7`)
- `LOG_LEVEL`: Logging level (default: `INFO`)
- `DEBUG`: Debug mode (default: `false`)

### Docker Configuration

The Dockerfile includes:
- Multi-stage build for optimization
- uv installation for Python package management
- Non-root user (`botuser:1000`)
- Health checks
- Minimal base image (python:3.14-slim)

The docker-compose.yml includes:
- Automatic restart policy
- Health checks
- JSON file logging with rotation
- Network isolation
- Container labels

## Development Workflow Steps

1. **Setup:**
   ```bash
   git clone https://github.com/ncls-p/py-besto-bot.git
   cd py-besto-bot
   uv sync
   pre-commit install
   ```

2. **Development:**
   ```bash
   # Make changes
   # Pre-commit hooks run automatically on commit
   git add .
   git commit -m "feat: add new feature"
   ```

3. **Testing:**
   ```bash
   pytest -v --cov=src
   ```

4. **Docker (optional):**
   ```bash
   docker-compose up -d --build
   docker-compose logs -f
   ```

## Resources

- [uv Documentation](https://docs.astral.sh/uv/)
- [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [discord.py Documentation](https://discordpy.readthedocs.io/)
- [OpenAI API Documentation](https://platform.openai.com/docs)
