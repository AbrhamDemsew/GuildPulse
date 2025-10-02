"""Tests for DI composition root."""

from unittest.mock import Mock

from src.application.messaging.handlers import ClearChannelHistory, ProcessUserTurn
from src.config import Settings
from src.domain.channel.aggregate import Channel
from src.infrastructure.ai.openai.adapter import OpenAIServiceAdapter
from src.infrastructure.di.composition_root import CompositionRoot


class TestCompositionRoot:
    """Test CompositionRoot DI container."""

    def test_create_message_processor(self):
        """Test creating message processor through DI."""
        config = Mock(spec=Settings)
        config.OPENAI_API_KEY = "test-key"
        config.OPENAI_BASE_URL = "https://api.example.com/v1"
        config.OPENAI_MODEL = "gpt-4"
        config.OPENAI_MAX_TOKENS = 500
        config.OPENAI_TEMPERATURE = 0.7
        config.CHAT_SYSTEM_PROMPT = "You are a helpful bot"
        config.LOG_LEVEL = "INFO"

        root = CompositionRoot(config)
        processor = root.create_message_processor()

        assert isinstance(processor, ProcessUserTurn)

    def test_create_clear_history_use_case(self):
        """Test creating clear history use case through DI."""
        config = Mock(spec=Settings)
        config.OPENAI_API_KEY = "test-key"
        config.OPENAI_BASE_URL = "https://api.example.com/v1"
        config.OPENAI_MODEL = "gpt-4"
        config.OPENAI_MAX_TOKENS = 500
        config.OPENAI_TEMPERATURE = 0.7
        config.CHAT_SYSTEM_PROMPT = "You are a helpful bot"
        config.LOG_LEVEL = "INFO"

        root = CompositionRoot(config)
        use_case = root.create_clear_history_use_case()

        assert isinstance(use_case, ClearChannelHistory)

    def test_message_processor_has_ai_service(self):
        """Test that message processor has AI service adapter."""
        config = Mock(spec=Settings)
        config.OPENAI_API_KEY = "test-key"
        config.OPENAI_BASE_URL = "https://api.example.com/v1"
        config.OPENAI_MODEL = "gpt-4"
        config.OPENAI_MAX_TOKENS = 500
        config.OPENAI_TEMPERATURE = 0.7
        config.CHAT_SYSTEM_PROMPT = "You are a helpful bot"
        config.LOG_LEVEL = "INFO"

        root = CompositionRoot(config)
        processor = root.create_message_processor()

        # Check that AI service is properly configured
        assert processor.ai_service is not None
        assert isinstance(processor.ai_service, OpenAIServiceAdapter)

    def test_full_workflow_integration(self):
        """Test complete workflow through DI root with mocked AI service."""
        config = Mock(spec=Settings)
        config.OPENAI_API_KEY = "test-key"
        config.OPENAI_BASE_URL = "https://api.example.com/v1"
        config.OPENAI_MODEL = "gpt-4"
        config.OPENAI_MAX_TOKENS = 500
        config.OPENAI_TEMPERATURE = 0.7
        config.CHAT_SYSTEM_PROMPT = "You are a helpful bot"
        config.LOG_LEVEL = "INFO"

        root = CompositionRoot(config)

        # Get the AI service and mock it
        ai_service = root.ai_service
        ai_service.generate_reply = Mock(return_value="Test response")

        # Create all use cases
        message_processor = root.create_message_processor()

        # Test message processing
        message_processor.execute(
            channel_id=123, user_content="Hello", channel=Channel(channel_id=123)
        )

        ai_service.generate_reply.assert_called_once()

    def test_multiple_channels_independent(self):
        """Test that multiple channels work independently with mocked AI service."""
        config = Mock(spec=Settings)
        config.OPENAI_API_KEY = "test-key"
        config.OPENAI_BASE_URL = "https://api.example.com/v1"
        config.OPENAI_MODEL = "gpt-4"
        config.OPENAI_MAX_TOKENS = 500
        config.OPENAI_TEMPERATURE = 0.7
        config.CHAT_SYSTEM_PROMPT = "You are a helpful bot"
        config.LOG_LEVEL = "INFO"

        root = CompositionRoot(config)

        processor = root.create_message_processor()

        # Get the AI service and mock it
        ai_service = root.ai_service
        ai_service.generate_reply = Mock(return_value="Test response")

        # Add message to channel 1
        processor.execute(channel_id=1, user_content="Channel 1")

        # Add message to channel 2
        processor.execute(channel_id=2, user_content="Channel 2")

        # Verify separate channels
        channel1 = processor.repo.get(1)
        channel2 = processor.repo.get(2)

        assert len(channel1.messages) == 2  # user + bot
        assert len(channel2.messages) == 2
        assert channel1.messages[0].content.value == "User: Channel 1"
        assert channel2.messages[0].content.value == "User: Channel 2"