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
async def test_generate_reply(message_processor):
    """Test generating a reply with conversation history."""
    message_processor.client.chat_completion_async = AsyncMock(return_value="Test response")

    result = await message_processor.generate_reply(123)

    assert result == "Test response"
    message_processor.client.chat_completion_async.assert_called_once()


@pytest.mark.asyncio
async def test_generate_reply_error_handling(message_processor):
    """Test error handling in reply generation."""
    message_processor.client.chat_completion_async = AsyncMock(side_effect=Exception("API Error"))

    result = await message_processor.generate_reply(123)

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
async def test_channel_locking():
    """Test that channel locks are created and used."""
    history = ConversationHistory()
    client = OpenAIClient(
        api_key="test_key",
        base_url="https://test.com/v1",
        model="test-model",
    )
    processor = MessageProcessor(history, client)

    processor.client.chat_completion_async = AsyncMock(return_value="Response")

    await processor.generate_reply(123)
    await processor.generate_reply(123)

    assert processor.get_lock(123) is not None


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
