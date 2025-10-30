# Clean Architecture + DDD Architecture

This project follows **Clean Architecture** with **Domain-Driven Design (DDD)** principles. The codebase is organized into layers with clear separation of concerns and dependency rules.

## Layer Structure

```
guildpulse/
├── config.py                         # Configuration management (Pydantic)
├── main.py                           # Application entry point
├── domain/                           # Core business logic (NO external dependencies)
│   ├── channel/                      # Channel domain (Channel, Message, MessageRole)
│   ├── shared/                       # Shared domain entities (errors, events)
│   └── repository.py                 # Domain repository interface
├── frameworks_drivers/               # External frameworks (Discord, AI)
│   └── discord/
│       ├── bot.py                    # Discord bot integration
│       └── sync_commands.py          # Sync slash commands
├── application/                      # Application layer
│   ├── messaging/
│   │   ├── handlers.py               # Use case handlers (ProcessUserTurn, ClearChannelHistory)
│   │   └── ports.py                  # Application ports (ConfigPort, etc.)
│   └── shared/                       # Shared application code
└── infrastructure/                   # Infrastructure layer
    ├── ai/                           # AI infrastructure
    │   └── openai/
    │       ├── adapter.py            # OpenAI service adapter
    │       └── client.py             # OpenAI API client
    ├── di/                           # Dependency injection
    │   └── composition_root.py       # Composition root for DI
    └── persistence/                  # Persistence layer
        └── memory/                   # In-memory repository implementation
```

## Dependency Rules

The architecture follows strict dependency rules to maintain clean separation:

- **Domain Layer** (`domain/`): No external dependencies. Contains pure business logic and entities.
- **Application Layer** (`application/`): Depends on domain layer. Contains use cases and orchestrates business logic.
- **Infrastructure Layer** (`infrastructure/`): Depends on domain layer. Contains adapters for external systems (API clients, repositories).
- **Frameworks Layer** (`frameworks_drivers/`): Depends on application layer (via DI). Contains framework-specific code (Discord bot).

## Key Patterns

### Entities
- **Channel**: Represents a conversation channel with message history and limits
- **Message**: Immutable value object representing a single message
- **MessageRole**: Enum for message roles (user, assistant, system)

### Value Objects
- **MessageContent**: Value object for message content with validation

### Ports & Adapters
- **AIServicePort**: Interface defining the contract for AI service operations (chat completion, image analysis).
- **ConfigPort**: Interface for configuration management.

### Use Cases
- **ProcessUserTurn**: Handles the message processing flow:
  1. Validates input message
  2. Retrieves or creates channel
  3. Updates conversation history
  4. Calls AI service for response
  5. Updates conversation history with response
  6. Returns formatted response
- **ClearChannelHistory**: Clears the conversation history for a specific channel

### Test Suite
- **205+ tests** with **79% coverage**
- **Parameterized tests** for edge cases
- **Fixtures** for dependency injection
- **Mock-based testing** for external dependencies
- **Type checking** with basedpyright (0 errors)

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
- `Channel`: Aggregates conversation state with message history, limits, and metadata
- `Message`: Immutable value object with content, role, and optional attachments
- `MessageRole`: Enum (USER, ASSISTANT, SYSTEM) for message roles

**Value Objects**:
- `MessageContent`: Wraps message content with validation (max 256 chars)

**Errors**:
- `DomainError`: Base error for all domain errors
- `ChannelNotFoundError`: Raised when channel not found
- `MessageValidationError`: Raised for invalid message content

**Events**:
- `ChannelCreated`, `ChannelUpdated`, `MessageAdded`, `ConversationCleared`

### Application Layer (`application/`)

### Application Layer (`application/`)

**Purpose**: Contains business logic and orchestrates use cases.

**Use Cases**:
- `ProcessUserTurn`: Handles the main message processing flow:
  1. Validates input message
  2. Retrieves or creates channel
  3. Updates conversation history with user message
  4. Calls AI service for response
  5. Updates conversation history with bot response
  6. Returns formatted response

- `ClearChannelHistory`: Clears the conversation history for a specific channel

**Ports**:
- `AIServicePort`: Interface for AI service operations
- `ConfigPort`: Interface for configuration management
- `RepositoryPort`: Interface for data persistence

### AI Infrastructure Layer (`infrastructure/ai/`)

**Purpose**: Adapters that connect the application to external systems.

**OpenAI Adapter**:
- Implements `AIServicePort` interface
- Handles API communication with OpenAI-compatible services
- Supports both text and vision (image analysis)
- Manages conversation context and token limits

**Infrastructure**:
- `Repository`: In-memory repository for channels
- `CompositionRoot`: Dependency injection container

### Frameworks Drivers Layer (`frameworks_drivers/`)

**Purpose**: Framework-specific code that uses the application layer.

**Discord Bot**:
- Integrates with discord.py for Discord functionality
- Implements Discord commands (slash commands, traditional commands)
- Handles message events (on_message)
- Manages conversation history per channel
- Implements rate limiting and error handling
- Supports DMs and mentions

**Services**:
- `SyncCommands`: Synchronous slash command registration
- `Bot`: Main bot class with event handlers

### Image Handling

**Purpose**: Process and validate images attached to Discord messages for AI analysis.

**Components**:
- **Bot Layer** (`guildpulse/frameworks_drivers/discord/bot.py`): Extracts image URLs from attachments
- **Validation**: Max 10MB per image (OpenAI recommended limit)
- **Logging**: Reports detected image count for debugging
- **OpenAI Adapter** (`guildpulse/infrastructure/ai/openai/adapter.py`): Formats multimodal messages

**Flow**:
1. Discord message received with attachments
2. Filter attachments by content type (`image/*`)
3. Validate image size (≤10MB)
4. Extract URLs to `image_urls` tuple
5. Pass to `ProcessUserTurn.execute()` with `image_urls` parameter
6. OpenAI adapter formats multimodal content (text + image URLs)
7. OpenAI API analyzes images and generates response

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
Discord Bot receives event (on_message)
         ↓
[Image Processing] Extract and validate image URLs (max 10MB)
         ↓
[Logging] Report detected image count
         ↓
ProcessUserTurn use case
         ↓
Channel aggregate (domain)
         ↓
OpenAI Service Adapter (interface adapters)
         ↓
[Multimodal Format] Add images to user message as image_url entries
         ↓
OpenAI API (external dependency)
         ↓
ProcessUserTurn returns response
         ↓
Discord Bot formats and sends response
         ↓
Channel updated with conversation history
```

## Testing Strategy

### Test Organization by Layer
- **Domain Tests**: `tests/domain/` - Entities, value objects, errors
- **Application Tests**: `tests/application/` - Use cases, ports
- **Infrastructure Tests**: `tests/infrastructure/` - Adapters, repositories
- **Framework Tests**: `tests/frameworks_drivers/` - Discord integration

### Test Types
- **Unit Tests**: Pure business logic in isolation
- **Parameterized Tests**: Edge cases and boundary conditions
- **Fixture-Based Tests**: Complex test data with factories
- **Async Tests**: Async/await patterns with pytest-asyncio
- **Integration Tests**: With mocked external dependencies

### Test Coverage
- **Total**: 79% (target: 90%+)
- **Domain**: 100%
- **Application**: 100%
- **Infrastructure**: 100%
- **Framework**: 57% ( Discord bot events)

### Test Markers
- `unit`: Unit tests
- `integration`: Integration tests
- `slow`: Slow running tests
- `async`: Async tests
- `requires_api`: Tests requiring external API access

## Docker Containerization

### Dockerfile Features
- **Multi-stage build**: Optimized image size
- **uv integration**: Fast Python package manager
- **Non-root user**: Runs as `botuser:1000` for security
- **Health checks**: Built-in health monitoring
- **Minimal base**: python:3.14-slim image
- **Cache optimization**: Layer caching for dependencies

### docker-compose.yml Features
- **Automatic restart**: Always restart policy
- **Health checks**: HTTP health endpoint
- **Logging**: JSON file logging with rotation (10MB, 5 files)
- **Network isolation**: Custom network for security
- **Container labels**: Organization and metadata

## Configuration

### Environment Variables

All configuration is managed via Pydantic's `Settings` class with type validation.

| Variable | Description | Default |
|----------|-------------|---------|
| `DISCORD_TOKEN` | Discord bot token (required) | - |
| `OPENAI_API_KEY` | OpenAI API key (required) | - |
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

## Testing

### Test Organization

Tests follow the Clean Architecture layers:

```
tests/
├── conftest.py                       # Shared fixtures and setup
├── domain/                           # Domain layer tests
│   ├── test_errors.py
│   ├── test_value_objects.py
│   └── test_channel.py
├── application/                      # Application layer tests
│   └── test_use_cases.py
├── infrastructure/                   # Infrastructure layer tests
│   ├── test_openai_sync.py
│   └── test_repository.py
├── frameworks_drivers/               # Framework tests
│   └── test_discord_bot.py
├── test_message_processor.py         # Integration tests
└── test_new_architecture.py          # New architecture tests
```

### Test Patterns

- **Parameterized tests**: `@pytest.mark.parametrize`
- **Fixtures**: Factory pattern for test data
- **Async tests**: `@pytest.mark.asyncio`
- **Mocking**: `unittest.mock` for external dependencies
- **Type checking**: `basedpyright` for all code

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
