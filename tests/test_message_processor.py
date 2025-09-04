"""Tests for MessageProcessor."""

from unittest.mock import AsyncMock, Mock, patch

import pytest

from src.domain.entities import ConversationHistory
from src.interface_adapters.openai_client import OpenAIClient
from src.use_cases.message_processing import MessageProcessor


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


@pytest.fixture
def message_processor(mock_client):
    """Create a MessageProcessor instance."""
    history = ConversationHistory()
    return MessageProcessor(history, mock_client)


@pytest.mark.asyncio
async def test_process_user_turn(message_processor):
    """Test processing a complete user turn with conversation history."""
    message_processor.client.chat_completion_async = AsyncMock(return_value="Test response")

    result = await message_processor.process_user_turn(123, "Test message")

    assert result == "Test response"
    message_processor.client.chat_completion_async.assert_called_once()

    history = message_processor.history.get_history(123)
    assert len(history) == 2
    assert history[0]["role"] == "user"
    assert history[0]["content"] == "Test message"
    assert history[1]["role"] == "assistant"
    assert history[1]["content"] == "Test response"


@pytest.mark.asyncio
async def test_process_user_turn_with_assistant_history(message_processor):
    """Test that user message is included in API call even when history ends with assistant."""
    message_processor.client.chat_completion_async = AsyncMock(return_value="Test response")

    # Simulate conversation where previous message was from assistant
    message_processor.history.add_message(
        123, {"role": "assistant", "content": "Previous response"}
    )

    result = await message_processor.process_user_turn(123, "New user message")

    assert result == "Test response"

    # Verify the API was called with messages ending with user role
    call_args = message_processor.client.chat_completion_async.call_args
    messages = call_args[1]["messages"]

    assert messages[-1]["role"] == "user"
    assert messages[-1]["content"] == "New user message"


@pytest.mark.asyncio
async def test_process_user_turn_error_handling(message_processor):
    """Test error handling in user turn processing."""
    message_processor.client.chat_completion_async = AsyncMock(side_effect=Exception("API Error"))

    result = await message_processor.process_user_turn(123, "Test message")

    assert result.startswith("Erreur")
    assert "API Error" in result


def test_conversation_history_management():
    """Test conversation history management."""
    history = ConversationHistory()
    assert history.get_all_channels() == []

    history.add_message(123, {"role": "user", "content": "Hello"})
    history.add_message(456, {"role": "user", "content": "Hi"})

    assert history.get_all_channels() == [123, 456]
    assert len(history.get_history(123)) == 1
    assert len(history.get_history(456)) == 1


def test_conversation_history_clear():
    """Test clearing conversation history."""
    history = ConversationHistory()
    history.add_message(123, {"role": "user", "content": "Hello"})
    history.clear_history(123)

    assert history.get_history(123) == []
    assert 123 not in history.get_all_channels()


@pytest.mark.asyncio
async def test_channel_locking(message_processor):
    """Test that channel locks are created and used."""
    message_processor.client.chat_completion_async = AsyncMock(return_value="Response")

    await message_processor.process_user_turn(123, "First message")
    await message_processor.process_user_turn(123, "Second message")

    assert message_processor.get_lock(123) is not None


def test_add_to_conversation(message_processor):
    """Test adding messages to conversation."""
    message_processor.add_to_conversation(123, "user", "Test message")
    message_processor.add_to_conversation(123, "assistant", "Test response")

    history = message_processor.get_conversation_history(123)
    assert len(history) == 2
    assert history[0]["role"] == "user"
    assert history[0]["content"] == "Test message"
    assert history[1]["role"] == "assistant"
    assert history[1]["content"] == "Test response"


def test_consecutive_user_messages_sanitization(message_processor):
    """Test sanitization of consecutive user messages."""
    messages = [
        {"role": "user", "content": "First message"},
        {"role": "user", "content": "Second message"},
        {"role": "assistant", "content": "First assistant"},
        {"role": "assistant", "content": "Second assistant"},
    ]

    sanitized = message_processor._sanitize_messages(messages)

    assert len(sanitized) == 2
    assert sanitized[0]["role"] == "user"
    assert sanitized[0]["content"] == "First message\n\nSecond message"
    assert sanitized[1]["role"] == "assistant"
    assert sanitized[1]["content"] == "First assistant\n\nSecond assistant"


def test_system_message_preserved(message_processor):
    """Test that system message is preserved in sanitization."""
    messages = [
        {"role": "system", "content": "System prompt"},
        {"role": "user", "content": "User message"},
        {"role": "assistant", "content": "Assistant response"},
    ]

    sanitized = message_processor._sanitize_messages(messages)

    assert len(sanitized) == 3
    assert sanitized[0]["role"] == "system"
    assert sanitized[1]["role"] == "user"
    assert sanitized[2]["role"] == "assistant"


def test_mixed_role_sequence(message_processor):
    """Test sanitization of mixed role sequence."""
    messages = [
        {"role": "user", "content": "First user"},
        {"role": "assistant", "content": "First assistant"},
        {"role": "user", "content": "Second user"},
        {"role": "assistant", "content": "Second assistant"},
        {"role": "user", "content": "Third user"},
        {"role": "assistant", "content": "Third assistant"},
    ]

    sanitized = message_processor._sanitize_messages(messages)

    assert len(sanitized) == 6
    assert all(msg["role"] in ["user", "assistant"] for msg in sanitized)
