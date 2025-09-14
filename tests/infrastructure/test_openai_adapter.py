"""Tests for OpenAI adapter."""

from unittest.mock import Mock

from src.domain.channel.aggregate import Channel
from src.domain.channel.value_objects import Message, MessageContent
from src.infrastructure.ai.openai.adapter import OpenAIServiceAdapter
from src.infrastructure.ai.openai.client import OpenAIClient


class TestOpenAIServiceAdapter:
    """Tests for OpenAIServiceAdapter."""

    def test_generate_reply_basic(self):
        """Test basic reply generation."""
        mock_client = Mock(spec=OpenAIClient)
        mock_client.chat_completion.return_value = "Test reply"

        adapter = OpenAIServiceAdapter(mock_client)
        channel = Channel(channel_id=123)

        result = adapter.generate_reply(channel)

        assert result == "Test reply"
        mock_client.chat_completion.assert_called_once()

    def test_generate_reply_with_system_prompt(self, infrastructure_environment):
        """Test that system prompt is included in messages."""
        mock_client = Mock(spec=OpenAIClient)
        mock_client.chat_completion.return_value = "Test reply"

        adapter = OpenAIServiceAdapter(mock_client)
        channel = Channel(channel_id=123)

        adapter.generate_reply(channel)

        call_args = mock_client.chat_completion.call_args[0][0]
        assert call_args[0]["role"] == "system"
        assert "Discord" in call_args[0]["content"]

    def test_generate_reply_with_existing_messages(self):
        """Test reply generation with existing channel messages."""
        mock_client = Mock(spec=OpenAIClient)
        mock_client.chat_completion.return_value = "Test reply"

        adapter = OpenAIServiceAdapter(mock_client)
        channel = Channel(channel_id=123)
        channel.add_message(Message(role="user", content=MessageContent(value="Hello")))
        channel.add_message(Message(role="assistant", content=MessageContent(value="Hi")))

        adapter.generate_reply(channel)

        call_args = mock_client.chat_completion.call_args[0][0]
        assert len(call_args) == 3
        assert call_args[1]["role"] == "user"
        assert call_args[1]["content"] == "Hello"
        assert call_args[2]["role"] == "assistant"
        assert call_args[2]["content"] == "Hi"

    def test_generate_reply_respects_max_messages(self):
        """Test that only last 100 messages are used."""
        mock_client = Mock(spec=OpenAIClient)
        mock_client.chat_completion.return_value = "Test reply"

        adapter = OpenAIServiceAdapter(mock_client)
        channel = Channel(channel_id=123, max_messages=200)

        for i in range(150):
            channel.add_message(Message(role="user", content=MessageContent(value=f"Message {i}")))

        adapter.generate_reply(channel)

        call_args = mock_client.chat_completion.call_args[0][0]
        assert len(call_args) == 101

    def test_generate_reply_with_image_urls(self):
        """Test reply generation with image URLs."""
        mock_client = Mock(spec=OpenAIClient)
        mock_client.chat_completion.return_value = "Image response"

        adapter = OpenAIServiceAdapter(mock_client)
        channel = Channel(channel_id=123)
        channel.add_message(Message(role="user", content=MessageContent(value="What's this?")))
        image_urls = ("https://example.com/image1.jpg", "https://example.com/image2.jpg")

        adapter.generate_reply(channel, image_urls=image_urls)

        call_args = mock_client.chat_completion.call_args[0][0]
        last_message = call_args[-1]
        assert last_message["role"] == "user"
        assert isinstance(last_message["content"], list)
        assert len(last_message["content"]) == 3
        assert last_message["content"][0]["type"] == "text"
        assert last_message["content"][1]["type"] == "image_url"

    def test_generate_reply_single_image_url(self):
        """Test reply generation with single image URL."""
        mock_client = Mock(spec=OpenAIClient)
        mock_client.chat_completion.return_value = "Single image response"

        adapter = OpenAIServiceAdapter(mock_client)
        channel = Channel(channel_id=123)
        channel.add_message(Message(role="user", content=MessageContent(value="Show me")))

        adapter.generate_reply(channel, image_urls=("https://example.com/image.jpg",))

        call_args = mock_client.chat_completion.call_args[0][0]
        last_message = call_args[-1]
        assert isinstance(last_message["content"], list)

    def test_generate_reply_empty_image_urls(self):
        """Test reply generation with empty image_urls tuple."""
        mock_client = Mock(spec=OpenAIClient)
        mock_client.chat_completion.return_value = "Regular response"

        adapter = OpenAIServiceAdapter(mock_client)
        channel = Channel(channel_id=123)
        channel.add_message(Message(role="user", content=MessageContent(value="Test")))

        adapter.generate_reply(channel, image_urls=())

        call_args = mock_client.chat_completion.call_args[0][0]
        last_message = call_args[-1]
        assert last_message["content"] == "Test"

    def test_generate_reply_no_user_message_last(self):
        """Test that last message must be user for image URLs to work."""
        mock_client = Mock(spec=OpenAIClient)
        mock_client.chat_completion.return_value = "Test response"

        adapter = OpenAIServiceAdapter(mock_client)
        channel = Channel(channel_id=123)
        channel.add_message(Message(role="user", content=MessageContent(value="First")))
        channel.add_message(Message(role="assistant", content=MessageContent(value="Second")))

        adapter.generate_reply(channel, image_urls=("https://example.com/image.jpg",))

        call_args = mock_client.chat_completion.call_args[0][0]
        last_message = call_args[-1]
        assert last_message["role"] == "assistant"
        assert not isinstance(last_message["content"], list)


class TestOpenAIServiceAdapterEdgeCases:
    """Tests for edge cases in OpenAIServiceAdapter."""

    def test_adapter_with_no_messages(self):
        """Test adapter with empty channel."""
        mock_client = Mock(spec=OpenAIClient)
        mock_client.chat_completion.return_value = "Test reply"

        adapter = OpenAIServiceAdapter(mock_client)
        channel = Channel(channel_id=123)

        result = adapter.generate_reply(channel)

        assert result == "Test reply"
        call_args = mock_client.chat_completion.call_args[0][0]
        assert len(call_args) == 1

    def test_adapter_with_exactly_100_messages(self):
        """Test adapter with exactly 100 messages."""
        mock_client = Mock(spec=OpenAIClient)
        mock_client.chat_completion.return_value = "Test reply"

        adapter = OpenAIServiceAdapter(mock_client)
        channel = Channel(channel_id=123, max_messages=200)

        for i in range(100):
            channel.add_message(Message(role="user", content=MessageContent(value=str(i))))

        adapter.generate_reply(channel)

        call_args = mock_client.chat_completion.call_args[0][0]
        assert len(call_args) == 101
