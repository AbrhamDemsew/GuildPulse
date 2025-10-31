"""Tests for application use cases."""

from typing import Any

from unittest import mock
from unittest.mock import Mock, patch

from guildpulse.application.messaging.handlers import ClearChannelHistory, ProcessUserTurn
from guildpulse.domain.channel.aggregate import Channel
from guildpulse.domain.channel.value_objects import Message, MessageContent
from guildpulse.domain.shared.completion_result import CompletionResult
from guildpulse.domain.shared.errors import ChannelNotFoundError
from guildpulse.infrastructure.persistence.memory.repository import InMemoryChannelRepository


class TestProcessUserTurn:
    """Tests for ProcessUserTurn use case."""

    def test_process_user_turn_creates_channel(self, mock_ai_adapter: mock.Mock):
        """Test that ProcessUserTurn creates channel if not exists."""
        repo = InMemoryChannelRepository()
        processor = ProcessUserTurn(repo, mock_ai_adapter)

        result = processor.execute(channel_id=123, user_content="Hello")

        assert result == "Test response"
        assert repo.get(123).count_messages() == 2

    def test_process_user_turn_with_existing_channel(
        self, mock_ai_adapter: mock.Mock, sample_channel: mock.Mock
    ):
        """Test ProcessUserTurn with an existing channel."""
        repo = InMemoryChannelRepository()
        repo.save(sample_channel)
        processor = ProcessUserTurn(repo, mock_ai_adapter)

        result = processor.execute(channel_id=999, user_content="New message")

        assert result == "Test response"
        assert repo.get(999).count_messages() == 3

    def test_process_user_turn_adds_user_message(
        self, mock_ai_adapter: mock.Mock, sample_channel: mock.Mock
    ):
        """Test that user message is added correctly."""
        repo = InMemoryChannelRepository()
        repo.save(sample_channel)
        processor = ProcessUserTurn(repo, mock_ai_adapter)

        processor.execute(channel_id=999, user_content="Test message")

        messages = repo.get(999).get_messages()
        assert messages[-2].role == "user"
        assert messages[-2].content.value is not None
        assert "Test message" in messages[-2].content.value

    def test_process_user_turn_adds_bot_message(
        self, mock_ai_adapter: mock.Mock, sample_channel: mock.Mock
    ):
        """Test that bot message is added correctly."""
        repo = InMemoryChannelRepository()
        repo.save(sample_channel)
        processor = ProcessUserTurn(repo, mock_ai_adapter)

        processor.execute(channel_id=999, user_content="Test")

        messages = repo.get(999).get_messages()
        assert messages[-1].role == "assistant"
        assert messages[-1].content.value is not None
        assert "Test response" in messages[-1].content.value

    def test_process_user_turn_with_custom_names(self, mock_ai_adapter: mock.Mock):
        """Test ProcessUserTurn with custom author and bot names."""
        repo = InMemoryChannelRepository()
        processor = ProcessUserTurn(repo, mock_ai_adapter)

        processor.execute(
            channel_id=123,
            user_content="Hello",
            author_name="Alice",
            bot_name="Bob",
        )

        messages = repo.get(123).get_messages()
        assert messages[0].content.value is not None
        assert "Alice:" in messages[0].content.value
        assert messages[1].content.value is not None
        assert "Bob:" in messages[1].content.value

    def test_process_user_turn_with_image_urls(self, mock_ai_adapter: mock.Mock):
        """Test ProcessUserTurn with image URLs."""
        repo = InMemoryChannelRepository()
        processor = ProcessUserTurn(repo, mock_ai_adapter)

        result = processor.execute(
            channel_id=123,
            user_content="Test",
            image_urls=("https://example.com/image.jpg",),
        )

        assert result == "Test response"

    def test_process_user_turn_channel_not_found(self):
        """Test ProcessUserTurn when channel not found (should not raise)."""
        repo = InMemoryChannelRepository()
        mock_adapter = Mock()  # type: ignore[assignment]
        mock_adapter.generate_reply.side_effect = ChannelNotFoundError("test")
        processor = ProcessUserTurn(repo, mock_adapter)

        result = processor.execute(channel_id=999, user_content="Hello")

        assert "Channel not found" in result

    def test_process_user_turn_domain_error(self):
        """Test ProcessUserTurn with DomainError."""
        repo = InMemoryChannelRepository()
        mock_adapter = Mock()
        mock_adapter.generate_reply.side_effect = ChannelNotFoundError("test")
        processor = ProcessUserTurn(repo, mock_adapter)

        result = processor.execute(channel_id=123, user_content="Hello")

        assert "Channel not found" in result

    def test_process_user_turn_generic_exception(self):
        """Test ProcessUserTurn with unexpected exception."""
        repo = InMemoryChannelRepository()
        mock_adapter = Mock()
        mock_adapter.generate_reply.side_effect = Exception("Unexpected error")
        processor = ProcessUserTurn(repo, mock_adapter)

        result = processor.execute(channel_id=123, user_content="Hello")

        assert "unexpected error" in result.lower()

    def test_process_user_turn_logging(self, mock_ai_adapter: mock.Mock):
        """Test that ProcessUserTurn logs correctly."""
        repo = InMemoryChannelRepository()
        processor = ProcessUserTurn(repo, mock_ai_adapter)

        with patch.object(processor, "logger") as mock_logger:
            processor.execute(channel_id=123, user_content="Hello")

            assert mock_logger.info.called


class TestProcessUserTurnEdgeCases:
    """Tests for edge cases in ProcessUserTurn."""

    def test_process_user_turn_with_empty_content(self, mock_ai_adapter: mock.Mock):
        """Test ProcessUserTurn with empty user content."""
        repo = InMemoryChannelRepository()
        processor = ProcessUserTurn(repo, mock_ai_adapter)

        result = processor.execute(channel_id=123, user_content="")

        assert result == "Test response"

    def test_process_user_turn_with_very_long_content(self, mock_ai_adapter: mock.Mock):
        """Test ProcessUserTurn with very long content."""
        repo = InMemoryChannelRepository()
        processor = ProcessUserTurn(repo, mock_ai_adapter)
        long_content = "x" * 10000

        result = processor.execute(channel_id=123, user_content=long_content)

        assert "An error occurred" in result

    def test_process_user_turn_passes_channel_explicitly(
        self, mock_ai_adapter: mock.Mock, sample_channel: Any
    ):
        """Test ProcessUserTurn with channel passed explicitly."""
        repo = InMemoryChannelRepository()
        processor = ProcessUserTurn(repo, mock_ai_adapter)

        result = processor.execute(
            channel_id=123,
            user_content="Test",
            channel=sample_channel,
        )

        assert result == "Test response"
        assert sample_channel.count_messages() == 3


class TestClearChannelHistory:
    """Tests for ClearChannelHistory use case."""

    def test_clear_channel_history_success(self, sample_channel: Any):
        """Test clearing channel history successfully."""
        repo = InMemoryChannelRepository()
        repo.save(sample_channel)
        use_case = ClearChannelHistory(repo)

        result = use_case.execute(channel_id=999)

        assert result is True
        assert repo.get(999).count_messages() == 0

    def test_clear_channel_history_not_found(self):
        """Test clearing non-existent channel."""
        repo = InMemoryChannelRepository()
        use_case = ClearChannelHistory(repo)

        result = use_case.execute(channel_id=999)

        assert result is False

    def test_clear_channel_history_already_empty(self):
        """Test clearing empty channel."""
        repo = InMemoryChannelRepository()
        repo.save(Channel(id=123))
        use_case = ClearChannelHistory(repo)

        result = use_case.execute(channel_id=123)

        assert result is False

    def test_clear_channel_history_logging(self):
        """Test that ClearChannelHistory logs correctly."""
        repo = InMemoryChannelRepository()
        channel = Channel(id=123)

        channel.add_message(Message(role="user", content=MessageContent(value="test")))
        repo.save(channel)
        use_case = ClearChannelHistory(repo)

        with patch.object(use_case, "logger") as mock_logger:
            result = use_case.execute(channel_id=123)

            assert result is True
            assert mock_logger.info.called

    def test_clear_channel_history_generic_exception(self):
        """Test ClearChannelHistory with unexpected exception."""
        repo = InMemoryChannelRepository()
        channel = Channel(id=123)
        repo.save(channel)

        use_case = ClearChannelHistory(repo)

        with patch.object(repo, "get", side_effect=Exception("Error")):
            result = use_case.execute(channel_id=123)

            assert result is False


class TestUseCaseIntegration:
    """Integration tests for use cases."""

    def test_full_workflow(self):
        """Test complete workflow: user message -> AI response -> clear."""
        repo = InMemoryChannelRepository()
        mock_adapter: Any = Mock()
        mock_adapter.generate_reply.return_value = CompletionResult(
            content="AI response",
            prompt_tokens=8,
            completion_tokens=4,
        )
        processor = ProcessUserTurn(repo, mock_adapter)
        clear_use_case = ClearChannelHistory(repo)

        processor.execute(channel_id=123, user_content="Hello")
        assert repo.get(123).count_messages() == 2

        clear_use_case.execute(channel_id=123)
        assert repo.get(123).count_messages() == 0

        processor.execute(channel_id=123, user_content="New message")
        assert repo.get(123).count_messages() == 2
