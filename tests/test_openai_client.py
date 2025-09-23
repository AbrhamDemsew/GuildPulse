"""Tests for OpenAI client (infrastructure layer)."""

from typing import Any

from unittest.mock import Mock, patch

import pytest

from src.infrastructure.ai.openai.client import OpenAIClient


@pytest.fixture
def mock_openai_client() -> Any:
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


@pytest.mark.asyncio
async def test_chat_completion_async(mock_openai_client: Any) -> Any:
    """Test chat completion async method."""
    messages = [{"role": "user", "content": "Hello"}]
    response = await mock_openai_client.chat_completion_async(messages)

    assert response == "Test response"
    mock_openai_client.client.chat.completions.create.assert_called_once()


@pytest.mark.asyncio
async def test_chat_completion_with_custom_params(mock_openai_client: Any) -> Any:
    """Test chat completion with custom parameters."""
    messages = [{"role": "user", "content": "Test"}]
    response = await mock_openai_client.chat_completion_async(
        messages, model="custom-model", max_tokens=200, temperature=0.8
    )

    assert response == "Test response"
    mock_openai_client.client.chat.completions.create.assert_called_once_with(
        model="custom-model", messages=messages, max_tokens=200, temperature=0.8
    )
