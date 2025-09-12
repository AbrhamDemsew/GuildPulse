# Clean Architecture + DDD Architecture

This project follows Clean Architecture with Domain-Driven Design principles.

## Layer Structure

```
src/
├── domain/                    # Core business logic (NO external dependencies)
│   ├── channel/
│   │   ├── aggregate.py       # Aggregate root (Channel)
│   │   └── value_objects.py   # Value objects (Message, MessageContent)
│   ├── shared/
│   │   └── errors.py          # Domain exceptions
│   └── repository.py          # Repository interfaces (ports)
├── application/               # Use cases / Application services
│   ├── messaging/
│   │   ├── handlers.py        # Use case implementations
│   │   ├── ports.py           # Application ports (AI service)
│   │   └── config.py          # Configuration port
│   └── shared/
│       └── config.py          # Shared configuration port
├── infrastructure/            # Adapters (external systems)
│   ├── config/
│   │   └── adapter.py         # Configuration adapter
│   ├── ai/
│   │   └── openai/
│   │       ├── client.py      # OpenAI API client
│   │       └── adapter.py     # AI service adapter
│   └── persistence/
│       └── memory/
│           └── repository.py  # In-memory repository
├── frameworks_drivers/        # External frameworks (Discord)
│   └── discord/
│       └── bot.py             # Discord bot integration
└── di/                        # Dependency injection
    └── composition_root.py    # DI composition root
```

## Dependency Rules

- **Domain layer**: No external dependencies
- **Application layer**: Depends on domain layer
- **Infrastructure layer**: Depends on domain and application (adapters)
- **Frameworks layer**: Depends on application (DI through CompositionRoot)

## Key Patterns

- **Entities**: `Channel` - has identity (channel_id)
- **Value Objects**: `Message`, `MessageContent` - immutable, value equality
- **Ports & Adapters**: `AIServicePort`, `ConfigPort` - interfaces
- **Use Cases**: `ProcessUserTurn`, `ClearChannelHistory` - business orchestration
- **DI**: `CompositionRoot` - single point of dependency injection

## Testing Strategy

- Unit tests for domain objects (entities, value objects)
- Integration tests for use cases
- Mock adapters for infrastructure
- DI composition root for integration tests