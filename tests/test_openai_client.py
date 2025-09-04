"""Tests for OpenAI client."""

from unittest.mock import AsyncMock, Mock, patch

import pytest

from src.domain.entities import ConversationHistory
from src.interface_adapters.openai_client import OpenAIClient
from src.use_cases.message_processing import MessageProcessor


@pytest.fixture
def mock_openai_client():
    """Create a mock OpenAI client."""
    with patch("src.interface_adapters.openai_client.OpenAI") as mock_openai:
        mock_client_instance = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Test response"
        mock_response.choices[0].message.role = "assistant"
        mock_client_instance.chat.completions.create = Mock(return_value=mock_response)
        mock_openai.return_value = mock_client_instance

        client = OpenAIClient(
            api_key="test_key",
            base_url="https://test.com/v1",
            model="test-model",
            max_tokens=100,
            temperature=0.5,
        )
        return client


@pytest.mark.asyncio
async def test_chat_completion_async(mock_openai_client):
    """Test chat completion async method."""
    messages = [{"role": "user", "content": "Hello"}]
    response = await mock_openai_client.chat_completion_async(messages)

    assert response == "Test response"
    mock_openai_client.client.chat.completions.create.assert_called_once()


@pytest.mark.asyncio
async def test_chat_completion_with_custom_params(mock_openai_client):
    """Test chat completion with custom parameters."""
    messages = [{"role": "user", "content": "Test"}]
    response = await mock_openai_client.chat_completion_async(
        messages, model="custom-model", max_tokens=200, temperature=0.8
    )

    assert response == "Test response"
    mock_openai_client.client.chat.completions.create.assert_called_once_with(
        model="custom-model", messages=messages, max_tokens=200, temperature=0.8
    )


@pytest.mark.asyncio
async def test_chat_completion_with_consecutive_user_messages(mock_openai_client):
    """Test chat completion with consecutive user messages (should be sanitized)."""
    processor = MessageProcessor(ConversationHistory(), mock_openai_client)

    history = processor.history
    history.add_message(123, {"role": "user", "content": "First message"})
    history.add_message(123, {"role": "user", "content": "Second message"})

    response = await processor.process_user_turn(123, "Third message")

    assert response == "Test response"
    call_args = mock_openai_client.client.chat.completions.create.call_args

    sent_messages = call_args[1]["messages"]

    assert len(sent_messages) == 2
    assert sent_messages[0]["role"] == "system"
    assert sent_messages[1]["role"] == "user"
    assert sent_messages[1]["content"] == "First message\n\nSecond message\n\nThird message"


def test_health_check(mock_openai_client):
    """Test health check method."""
    mock_client = mock_openai_client.client
    mock_client.models.list = Mock(return_value=Mock())

    assert mock_openai_client.health_check() is True
    mock_client.models.list.assert_called_once()


def test_health_check_failure(mock_openai_client):
    """Test health check with failure."""
    mock_client = mock_openai_client.client
    mock_client.models.list = Mock(side_effect=Exception("API Error"))

    assert mock_openai_client.health_check() is False
