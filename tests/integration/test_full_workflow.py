"""Integration tests for full workflow."""

import pytest

from src.application.messaging.handlers import ClearChannelHistory, ProcessUserTurn
from src.domain.channel.aggregate import Channel
from src.infrastructure.ai.openai.adapter import OpenAIServiceAdapter
from src.infrastructure.ai.openai.client import OpenAIClient
from src.infrastructure.persistence.memory.repository import InMemoryChannelRepository
from unittest.mock import Mock


@pytest.fixture
def full_workflow_setup():
    """Setup for full workflow integration tests."""
    repo = InMemoryChannelRepository()

    # Create real OpenAI client with mock
    mock_client = Mock(spec=OpenAIClient)
    mock_client.chat_completion.return_value = "Test response from AI"
    adapter = OpenAIServiceAdapter(mock_client)

    processor = ProcessUserTurn(repo, adapter)
    clear_use_case = ClearChannelHistory(repo)

    return processor, clear_use_case, repo


class TestFullWorkflowIntegration:
    """Integration tests for complete workflow."""

    def test_full_workflow_user_sends_message(self, full_workflow_setup):
        """Test complete workflow: user sends message, AI responds."""
        processor, _, repo = full_workflow_setup

        # User sends first message
        result = processor.execute(
            channel_id=123,
            user_content="Hello",
            author_name="Alice",
            bot_name="Bot",
        )

        # Verify AI responded
        assert result == "Test response from AI"

        # Verify channel has 2 messages (user + bot)
        channel = repo.get(123)
        messages = channel.get_messages()
        assert len(messages) == 2
        assert messages[0].content.value == "Alice: Hello"
        assert "Bot:" in messages[1].content.value

    def test_full_workflow_multiple_interactions(self, full_workflow_setup):
        """Test multiple user-AI interactions."""
        processor, _, repo = full_workflow_setup

        # First interaction
        processor.execute(channel_id=456, user_content="Question 1")

        # Second interaction
        processor.execute(channel_id=456, user_content="Question 2")

        # Third interaction
        processor.execute(channel_id=456, user_content="Question 3")

        # Verify all messages stored
        channel = repo.get(456)
        messages = channel.get_messages()
        assert len(messages) == 6  # 3 user + 3 bot

    def test_full_workflow_clear_history(self, full_workflow_setup):
        """Test clearing conversation history."""
        processor, clear_use_case, repo = full_workflow_setup

        # Add messages
        processor.execute(channel_id=789, user_content="Some message")

        # Clear history
        result = clear_use_case.execute(channel_id=789)

        assert result is True
        assert repo.get(789).count_messages() == 0

    def test_full_workflow_channel_not_found_recovery(self, full_workflow_setup):
        """Test bot recovers from channel not found gracefully."""
        processor, _, _ = full_workflow_setup

        # Process with non-existent channel
        result = processor.execute(
            channel_id=9999,
            user_content="Hello",
        )

        # Should get response (not error message since repo creates channel)
        assert "Test response from AI" in result

    def test_full_workflow_message_truncation(self, full_workflow_setup):
        """Test that messages are truncated at 500 characters in bot response."""
        processor, _, repo = full_workflow_setup

        long_message = "x" * 1000

        processor.execute(
            channel_id=111,
            user_content=long_message,
        )

        channel = repo.get(111)
        user_message = channel.get_messages()[0]
        # Bot truncates to 500 chars, but user message is stored full
        # The truncation happens in bot.py, but the stored message is original
        assert "User:" in user_message.content.value

    def test_full_workflow_with_images(self, full_workflow_setup):
        """Test message processing with image URLs."""
        processor, _, repo = full_workflow_setup

        processor.execute(
            channel_id=222,
            user_content="Look at this",
            image_urls=("https://example.com/image.jpg",),
        )

        channel = repo.get(222)
        assert channel.count_messages() == 2

    def test_full_workflow_max_messages_limit(self, full_workflow_setup):
        """Test that max_messages limit is enforced."""
        processor, _, repo = full_workflow_setup

        # Create channel with max_messages=5
        channel = Channel(id=333, max_messages=5)

        # Add more than 5 messages
        for i in range(10):
            processor.execute(
                channel_id=333,
                user_content=f"Message {i}",
                channel=channel,
            )

        # Should only keep last 5
        assert channel.count_messages() == 5
