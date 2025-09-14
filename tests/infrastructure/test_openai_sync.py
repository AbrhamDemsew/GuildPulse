"""Tests for OpenAI client sync methods."""

from unittest.mock import Mock, patch

import pytest

from src.infrastructure.ai.openai.client import OpenAIClient


class TestOpenAIClientSync:
    """Tests for OpenAIClient sync chat_completion method."""

    def test_chat_completion_success(self):
        """Test successful sync chat completion."""
        client = OpenAIClient(
            api_key="test",
            base_url="https://test.com",
            model="test-model",
            max_tokens=100,
            temperature=0.5,
        )

        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Test response"
        mock_response.choices[0].message.role = "assistant"
        client.client.chat.completions.create = Mock(return_value=mock_response)

        result = client.chat_completion([{"role": "user", "content": "Hello"}])

        assert result == "Test response"
        client.client.chat.completions.create.assert_called_once()

    def test_chat_completion_with_custom_params(self):
        """Test sync chat completion with custom parameters."""
        client = OpenAIClient(
            api_key="test",
            base_url="https://test.com",
            model="test-model",
        )

        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Custom response"
        client.client.chat.completions.create = Mock(return_value=mock_response)

        result = client.chat_completion(
            [{"role": "user", "content": "Test"}],
            model="custom-model",
            max_tokens=200,
            temperature=0.8,
        )

        assert result == "Custom response"
        client.client.chat.completions.create.assert_called_once_with(
            model="custom-model",
            messages=[{"role": "user", "content": "Test"}],
            max_tokens=200,
            temperature=0.8,
        )

    def test_chat_completion_thinking_model(self):
        """Test sync chat completion with thinking model."""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Thinking response"

        with patch("src.infrastructure.ai.openai.client.OpenAI") as mock_openai:
            mock_client_instance = Mock()
            mock_client_instance.chat.completions.create = Mock(return_value=mock_response)
            mock_openai.return_value = mock_client_instance

            client = OpenAIClient(
                api_key="test",
                base_url="https://test.com",
                model="qwen-2.5-thinking-preview",
                max_tokens=100,
            )

            result = client.chat_completion([{"role": "user", "content": "Test"}])

            assert result == "Thinking response"
            call_args = mock_client_instance.chat.completions.create.call_args
            assert call_args.kwargs["extra_body"] == {
                "chat_template_kwargs": {"enable_thinking": False}
            }

    def test_chat_completion_none_content_raises(self):
        """Test that None content raises ValueError."""
        client = OpenAIClient(
            api_key="test",
            base_url="https://test.com",
            model="test-model",
        )

        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = None
        client.client.chat.completions.create = Mock(return_value=mock_response)

        with pytest.raises(ValueError) as exc_info:
            client.chat_completion([{"role": "user", "content": "Test"}])

        assert "No content returned" in str(exc_info.value)

    def test_chat_completion_error_logging(self):
        """Test error logging in sync method."""
        with patch("src.infrastructure.ai.openai.client.logging") as mock_logging:
            mock_logger = Mock()
            mock_logging.getLogger.return_value = mock_logger

            client = OpenAIClient(
                api_key="test",
                base_url="https://test.com",
                model="test-model",
            )

            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = "Test"
            client.client.chat.completions.create = Mock(return_value=mock_response)

            client.chat_completion([{"role": "user", "content": "Test"}])

            assert mock_logger.debug.called
            assert mock_logger.info.called


class TestOpenAIClientSyncErrorHandling:
    """Tests for error handling in sync methods."""

    def test_chat_completion_api_error(self):
        """Test sync method with API error."""
        client = OpenAIClient(
            api_key="test",
            base_url="https://test.com",
            model="test-model",
        )

        with patch.object(
            client.client.chat.completions, "create", side_effect=Exception("API Error")
        ):
            with pytest.raises(Exception) as exc_info:
                client.chat_completion([{"role": "user", "content": "Test"}])

            assert "API Error" in str(exc_info.value)

    def test_chat_completion_logging_on_error(self):
        """Test that errors are logged."""
        with patch("src.infrastructure.ai.openai.client.logging") as mock_logging:
            mock_logger = Mock()
            mock_logging.getLogger.return_value = mock_logger

            client = OpenAIClient(
                api_key="test",
                base_url="https://test.com",
                model="test-model",
            )

            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = "Test"
            client.client.chat.completions.create = Mock(return_value=mock_response)

            client.chat_completion([{"role": "user", "content": "Test"}])

            assert mock_logger.debug.called


class TestOpenAIClientMultimodal:
    """Tests for multimodal content handling in sync method."""

    def test_chat_completion_multimodal_content(self):
        """Test sync method with multimodal content."""
        client = OpenAIClient(
            api_key="test",
            base_url="https://test.com",
            model="gpt-4-turbo",
            max_tokens=100,
            temperature=0.5,
        )

        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Image description"
        client.client.chat.completions.create = Mock(return_value=mock_response)

        multimodal_messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "What's in this image?"},
                    {
                        "type": "image_url",
                        "image_url": {"url": "https://example.com/image.jpg"},
                    },
                ],
            }
        ]

        result = client.chat_completion(multimodal_messages)

        assert result == "Image description"
        client.client.chat.completions.create.assert_called_once_with(
            model="gpt-4-turbo",
            messages=multimodal_messages,
            max_tokens=100,
            temperature=0.5,
        )
