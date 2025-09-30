# Clean Architecture + DDD Architecture

This project follows **Clean Architecture** with **Domain-Driven Design (DDD)** principles. The codebase is organized into layers with clear separation of concerns and dependency rules.

## Layer Structure

```
src/
├── config.py                         # Configuration management (Pydantic)
├── main.py                           # Application entry point
├── domain/                           # Core business logic (NO external dependencies)
│   └── entities.py                   # Domain entities (ConversationHistory)
├── frameworks_drivers/               # External frameworks (Discord, AI)
│   └── discord/
│       └── bot.py                    # Discord bot integration
├── interface_adapters/               # API clients and adapters
│   └── openai/
│       └── client.py                 # OpenAI API client
├── use_cases/                        # Business logic and orchestration
│   └── message_processing.py         # Use case for message processing
└── utils/                            # Utility functions
```

## Dependency Rules

The architecture follows strict dependency rules to maintain clean separation:

- **Domain Layer** (`domain/`): No external dependencies. Contains pure business logic and entities.
- **Application Layer** (`use_cases/`): Depends on domain layer. Contains use cases and orchestrates business logic.
- **Infrastructure Layer** (`interface_adapters/`): Depends on domain layer. Contains adapters for external systems (API clients).
- **Frameworks Layer** (`frameworks_drivers/`): Depends on application layer (via DI). Contains framework-specific code (Discord bot).

## Key Patterns

### Entities
- **ConversationHistory**: Represents the conversation state for a channel, containing message history and metadata.

### Value Objects
- **Message**: Immutable value object representing a single message with content, author, timestamp, and attachments.

### Ports & Adapters
- **AIServicePort**: Interface defining the contract for AI service operations (chat completion, image analysis).
- **ConfigPort**: Interface for configuration management.

### Use Cases
- **ProcessUserTurn**: Orchestrates the message processing flow from Discord message to AI response.
- **ClearChannelHistory**: Clears conversation history for a specific channel.

### Dependency Injection
- **CompositionRoot**: Central point for dependency injection, wiring up all components.

## Architecture Principles

### 1. Dependency Inversion
High-level modules should not depend on low-level modules. Both should depend on abstractions.

### 2. Single Responsibility
Each component has a single, well-defined responsibility.

### 3. Open/Closed Principle
Entities are open for extension but closed for modification.

### 4. Dependency Rules
Dependencies flow inward, from outer layers to inner layers.

## Component Details

### Domain Layer (`domain/`)

**Purpose**: Core business logic and entities that have no dependencies on external systems.

**Entities**:
- `ConversationHistory`: Manages conversation state including message history, timestamps, and metadata.

**Value Objects**:
- `Message`: Immutable representation of a Discord message.

### Application Layer (`use_cases/`)

**Purpose**: Contains business logic and orchestrates use cases.

**Use Cases**:
- `ProcessUserTurn`: Handles the main message processing flow:
  1. Validates input message
  2. Retrieves conversation history
  3. Calls AI service for response
  4. Updates conversation history
  5. Returns formatted response

- `ClearChannelHistory`: Clears the conversation history for a specific channel.

### Interface Adapters Layer (`interface_adapters/`)

**Purpose**: Adapters that connect the application to external systems.

**OpenAI Client**:
- Implements `AIServicePort` interface
- Handles API communication with OpenAI-compatible services
- Supports both text and vision (image analysis)
- Manages conversation context and token limits

### Frameworks Drivers Layer (`frameworks_drivers/`)

**Purpose**: Framework-specific code that uses the application layer.

**Discord Bot**:
- Integrates with discord.py for Discord functionality
- Implements Discord commands and slash commands
- Handles message events and interactions
- Manages conversation history per channel
- Implements rate limiting and error handling

### Configuration Layer

**Purpose**: Centralized configuration management.

**Configuration**:
- Uses Pydantic for type-safe configuration
- Loads from environment variables
- Supports multiple environments (dev, staging, prod)

### Utils Layer

**Purpose**: Shared utility functions.

**Utilities**:
- Logging configuration
- Helper functions for common operations

## Data Flow

```
User sends Discord message
         ↓
Discord Bot receives event
         ↓
on_message event handler
         ↓
ProcessUserTurn use case
         ↓
ConversationHistory (domain)
         ↓
OpenAI Client (adapter)
         ↓
OpenAI API
         ↓
ProcessUserTurn returns response
         ↓
Discord Bot formats and sends response
         ↓
ConversationHistory updated
```

## Testing Strategy

### Unit Tests
- Domain entities (ConversationHistory, Message)
- Pure functions and utilities
- Use case logic in isolation

### Integration Tests
- Use case with mocked dependencies
- OpenAI client with mocked API calls
- Discord bot integration

### End-to-End Tests
- Full message flow from Discord to response
- Docker container integration tests

## Docker Containerization

### Dockerfile
- Multi-stage build for optimization
- Installs uv for Python package management
- Runs as non-root user (botuser:1000)
- Health checks for monitoring

### docker-compose.yml
- Service definition with restart policy
- Health checks
- Logging configuration with rotation
- Network isolation
- Container labels for organization

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DISCORD_TOKEN` | Discord bot token | - |
| `OPENAI_API_KEY` | OpenAI API key | - |
| `OPENAI_BASE_URL` | Custom API base URL | `https://api.openai.com/v1` |
| `OPENAI_MODEL` | Default model name | `gemma-3-27b-it-qat` |
| `OPENAI_MAX_TOKENS` | Maximum tokens for response | `500` |
| `OPENAI_TEMPERATURE` | Generation temperature | `0.7` |
| `OPENAI_VISION_ENABLED` | Enable image analysis | `true` |
| `OPENAI_VISION_MAX_IMAGES` | Max images per message | `4` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `DEBUG` | Debug mode | `false` |

## Dependencies

### Python Libraries
- **discord.py** 2.0+: Discord bot framework
- **openai**: OpenAI API client
- **pydantic**: Data validation and settings management
- **python-dotenv**: Environment variable management
- **uv**: Fast Python package manager

### Development Tools
- **pytest**: Testing framework
- **pytest-asyncio**: Async test support
- **pytest-cov**: Code coverage
- **black**: Code formatter
- **ruff**/**flake8**: Linter
- **mypy**: Type checker
- **pre-commit**: Git hooks

## Best Practices

1. **Keep domain layer pure**: No external dependencies in domain entities.
2. **Use interfaces**: Define ports/interfaces for external dependencies.
3. **Test in isolation**: Unit test business logic separately from frameworks.
4. **Follow dependency rules**: Dependencies should only point inward.
5. **Containerize**: Use Docker for consistent deployment.
6. **Use uv**: Leverage uv for fast dependency management.

## Future Enhancements

- [ ] Database integration for persistent conversation history
- [ ] Rate limiting and API usage tracking
- [ ] Admin dashboard for bot management
- [ ] Plugin system for custom commands
- [ ] Multi-language support (i18n)
- [ ] Metrics and observability (Prometheus, Grafana)
- [ ] Webhook support for external integrations

## References

- [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Domain-Driven Design](https://domainlanguage.com/ddd/)
- [discord.py Documentation](https://discordpy.readthedocs.io/)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [uv Documentation](https://docs.astral.sh/uv/)
