# Testing Documentation

This document describes the testing strategy and patterns used in the guildpulse project.

## Overview

The test suite follows **Clean Architecture** principles with comprehensive coverage of all layers:

- **205+ tests** with **79% coverage**
- All tests pass with **0 errors, 0 warnings**
- Full type checking with **basedpyright**

## Test Organization

```
tests/
├── conftest.py                       # Shared fixtures and setup
├── domain/                           # Domain layer tests
│   ├── test_errors.py
│   ├── test_value_objects.py
│   └── test_channel.py
├── application/                      # Application layer tests
│   ├── test_config_port.py
│   └── test_use_cases.py
├── infrastructure/                   # Infrastructure layer tests
│   ├── test_openai_sync.py
│   └── test_repository.py
├── frameworks_drivers/               # Framework tests
│   └── test_discord_bot.py
├── test_message_processor.py         # Integration tests
└── test_new_architecture.py          # New architecture tests
```

## Test Coverage by Layer

| Layer | Coverage | Tests |
|-------|----------|-------|
| Domain | 100% | 45+ |
| Application | 100% | 35+ |
| Infrastructure | 100% | 40+ |
| Framework | 57% | 85+ |
| **Total** | **79%** | **205** |

## Test Patterns

### 1. Parameterized Tests

Used for testing multiple scenarios with different inputs:

```python
@pytest.mark.parametrize("value", ["test", "", "A" * 100])
def test_parameterized(value: str) -> None:
    """Test with multiple values."""
    result = some_function(value)
    assert result is not None
```

### 2. Fixture Factory Pattern

Used for creating complex test data:

```python
@pytest.fixture
def message_factory() -> Callable:
    """Create message fixtures."""
    def _create(content: str, role: str = "user") -> Message:
        return Message(content=content, role=role)
    return _create

def test_message_creation(message_factory: Callable) -> None:
    """Test message creation with factory."""
    msg = message_factory("Hello", "user")
    assert msg.content == "Hello"
```

### 3. Async Tests

Used for async/await patterns:

```python
@pytest.mark.asyncio
async def test_async_operation() -> None:
    """Test async operation."""
    result = await some_async_function()
    assert result is not None
```

### 4. Mock-Based Testing

Used for external dependencies:

```python
@patch("guildpulse.infrastructure.ai.OpenAIClient")
def test_with_mock(mock_client: Mock) -> None:
    """Test with mocked OpenAI client."""
    mock_client.return_value.chat_completion_async.return_value = "test"
    result = process_message("hello")
    assert result == "test"
```

### 5. Type Checking

All code is type-checked with basedpyright:

```bash
basedpyright guildpulse/ tests/
```

## Running Tests

### All Tests

```bash
pytest
```

### With Coverage

```bash
pytest --cov=guildpulse --cov-report=term-missing -v
```

### Specific Test Files

```bash
pytest tests/domain/test_errors.py
pytest tests/application/test_use_cases.py
pytest tests/infrastructure/test_repository.py
```

### Test Markers

```bash
pytest -m unit          # Run unit tests
pytest -m integration   # Run integration tests
pytest -m "not slow"    # Skip slow tests
pytest -m requires_api  # Tests requiring API access
```

### Verbose Output

```bash
pytest -v
pytest -vv
```

## Code Quality

### Formatting

```bash
black guildpulse/ tests/
black --check guildpulse/ tests/  # Check only
```

### Linting

```bash
ruff check guildpulse/ tests/
ruff check --fix guildpulse/ tests/  # Auto-fix
```

### Type Checking

```bash
basedpyright guildpulse/ tests/
```

### Pre-commit Hooks

```bash
pre-commit install
pre-commit run --all-files
```

## Test Fixture Reference

### Shared Fixtures (conftest.py)

| Fixture | Description |
|---------|-------------|
| `channel_factory` | Factory for creating channels |
| `message_factory` | Factory for creating messages |
| `discord_message` | Mock Discord message |
| `channel` | Default channel fixture |
| `bot` | Bot fixture |
| `message_processor` | Message processor fixture |

### Async Fixtures

| Fixture | Description |
|---------|-------------|
| `async_channel_factory` | Async channel factory |
| `async_message_factory` | Async message factory |

## Best Practices

1. **Test one thing per test**: Each test should focus on a single behavior
2. **Use descriptive names**: `test_<what>_<condition>_<expected>`
3. **Keep tests independent**: No shared state between tests
4. **Mock external dependencies**: Use fixtures and mocks
5. **Type all test functions**: Include return types
6. **Document with docstrings**: Explain what and why

## Troubleshooting

### Common Issues

**Test timeout:**
```bash
pytest --timeout=30  # Increase timeout
```

**Coverage too low:**
```bash
pytest --cov=guildpulse --cov-report=term-missing -v
```

**Type errors:**
```bash
basedpyright guildpulse/ tests/
```

## Contributing

1. Write tests for new features
2. Run `pytest` to ensure all tests pass
3. Run `black`, `ruff`, `basedpyright` for code quality
4. Commit tests with feature/bugfix