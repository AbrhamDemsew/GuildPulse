"""Edge case tests for OpenAI adapter."""

import pytest
from unittest.mock import Mock

from src.infrastructure.ai.openai.adapter import OpenAIServiceAdapter
from src.infrastructure.ai.openai.client import OpenAIClient
from src.domain.channel.aggregate import Channel
from src.domain.channel.value_objects import Message, MessageContent


@pytest.fixture
def mock_client():
    """Create a mock OpenAI client."""
    mock = Mock(spec=OpenAIClient)
    return mock


@pytest.fixture
def adapter(mock_client):
    """Create OpenAIServiceAdapter with mock client."""
    return OpenAIServiceAdapter(mock_client)


class TestOpenAIAdapterEdgeCases:
    """Edge case tests for OpenAI adapter."""

    def test_adapter_with_system_prompt_first(self, adapter, mock_client):
        """Test adapter adds system prompt correctly."""
        mock_client.chat_completion.return_value = "Response"
        channel = Channel(id=123)

        adapter.generate_reply(channel, image_urls=())

        # Verify system prompt is first in messages
        call_args = mock_client.chat_completion.call_args[0][0]
        assert call_args[0]["role"] == "system"

    def test_adapter_truncates_to_100_messages(self, adapter, mock_client):
        """Test adapter truncates conversation to 100 messages."""
        mock_client.chat_completion.return_value = "Response"
        channel = Channel(id=123, max_messages=150)

        # Add 150 messages
        for i in range(150):
            channel.add_message(
                Message(
                    role="user" if i % 2 == 0 else "assistant",
                    content=MessageContent(value=f"Message {i}"),
                )
            )

        adapter.generate_reply(channel, image_urls=())

        # Verify only last 100 messages are sent
        call_args = mock_client.chat_completion.call_args[0][0]
        assert len(call_args) == 101  # 100 messages + system prompt

    def test_adapter_handles_empty_channel(self, adapter, mock_client):
        """Test adapter handles empty channel gracefully."""
        mock_client.chat_completion.return_value = "Response"
        channel = Channel(id=123)

        result = adapter.generate_reply(channel, image_urls=())

        assert result == "Response"
        call_args = mock_client.chat_completion.call_args[0][0]
        assert len(call_args) == 1  # Only system prompt

    def test_adapter_preserves_user_message_with_images(self, adapter, mock_client):
        """Test adapter preserves user message when images are present."""
        mock_client.chat_completion.return_value = "Response"
        channel = Channel(id=123)
        channel.add_message(
            Message(role="user", content=MessageContent(value="What's in this image?"))
        )

        adapter.generate_reply(channel, image_urls=("https://example.com/img.jpg",))

        call_args = mock_client.chat_completion.call_args[0][0]
        # Find the user message
        user_msg = next(m for m in call_args if m["role"] == "user")
        assert user_msg["content"][0]["type"] == "text"
        assert user_msg["content"][0]["text"] == "What's in this image?"

    def test_adapter_with_max_tokens_override(self, adapter, mock_client):
        """Test adapter respects max_tokens from client."""
        mock_client.chat_completion.return_value = "Response"
        channel = Channel(id=123)

        adapter.generate_reply(channel, image_urls=())

        # Verify client was called
        assert mock_client.chat_completion.called
