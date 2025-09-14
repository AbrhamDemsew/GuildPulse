"""Tests for message processor (legacy tests, kept for reference)."""

from unittest.mock import Mock, patch

import pytest

from src.application.messaging.handlers import ProcessUserTurn
from src.domain.channel.value_objects import Message, MessageContent
from src.infrastructure.ai.openai.adapter import OpenAIServiceAdapter
from src.infrastructure.ai.openai.client import OpenAIClient
from src.infrastructure.persistence.memory.repository import InMemoryMessageRepository


@pytest.fixture
def mock_client():
    """Create a mock OpenAI client."""
    with patch("src.infrastructure.ai.openai.client.OpenAI") as mock_openai:
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


@pytest.fixture
def message_processor():
    """Create a message processor with mock client."""
    from src.infrastructure.ai.openai.client import OpenAIClient

    with patch("src.infrastructure.ai.openai.client.OpenAI") as mock_openai:
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
        ai_service = OpenAIServiceAdapter(client)
        repo = InMemoryMessageRepository()
        return ProcessUserTurn(repo, ai_service)


@pytest.mark.asyncio
async def test_generate_reply(message_processor):
    """Test generating a reply with conversation history."""
    result = message_processor.execute(channel_id=123, user_content="Hello")
    assert result == "Test response"


@pytest.mark.asyncio
async def test_generate_reply_with_history(message_processor):
    """Test generating a reply with existing conversation history."""
    channel = message_processor.repo.get_or_create(456)
    channel.add_message(Message(role="user", content=MessageContent(value="Hello")))
    result = message_processor.execute(channel_id=456, user_content="Hello")
    assert result == "Test response"
