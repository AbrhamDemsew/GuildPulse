"""Tests for OpenAI client sync methods."""

from unittest.mock import Mock, patch

import pytest

from guildpulse.infrastructure.ai.openai.client import OpenAIClient

# ============================================================================
# TestOpenAIClientSync - Basic functionality tests
# ============================================================================


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

        with patch("guildpulse.infrastructure.ai.openai.client.OpenAI") as mock_openai:
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
        with patch("guildpulse.infrastructure.ai.openai.client.logging") as mock_logging:
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


# ============================================================================
# TestOpenAIClientSyncErrorHandling - Error handling tests
# ============================================================================


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
        with patch("guildpulse.infrastructure.ai.openai.client.logging") as mock_logging:
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


# ============================================================================
# TestOpenAIClientMultimodal - Multimodal content tests
# ============================================================================


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


# ============================================================================
# TestOpenAIClientEdgeCases - Edge case tests
# ============================================================================


class TestOpenAIClientEdgeCases:
    """Tests for edge cases in OpenAI client sync methods."""

    def test_empty_messages_list(self):
        """Test with empty messages list."""
        client = OpenAIClient(
            api_key="test",
            base_url="https://test.com",
            model="test-model",
        )

        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Response"
        client.client.chat.completions.create = Mock(return_value=mock_response)

        result = client.chat_completion([])

        assert result == "Response"

    def test_multiple_messages(self):
        """Test with multiple messages."""
        client = OpenAIClient(
            api_key="test",
            base_url="https://test.com",
            model="test-model",
        )

        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Response"
        client.client.chat.completions.create = Mock(return_value=mock_response)

        messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi"},
            {"role": "user", "content": "How are you?"},
        ]
        result = client.chat_completion(messages)

        assert result == "Response"

    def test_different_models(self):
        """Test with different model names."""
        models = [
            "gpt-3.5-turbo",
            "gpt-4",
            "gpt-4-turbo",
            "gpt-4o",
            "gemini-pro",
            "llama-3",
        ]

        for model in models:
            client = OpenAIClient(
                api_key="test",
                base_url="https://test.com",
                model=model,
            )

            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = f"Response from {model}"
            client.client.chat.completions.create = Mock(return_value=mock_response)

            result = client.chat_completion([{"role": "user", "content": "Test"}])

            assert result == f"Response from {model}"

    def test_max_tokens_edge_cases(self):
        """Test with different max token values."""
        for max_tokens in [1, 100, 500, 1000, 2000]:
            client = OpenAIClient(
                api_key="test",
                base_url="https://test.com",
                model="test-model",
                max_tokens=max_tokens,
            )

            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = "Response"
            client.client.chat.completions.create = Mock(return_value=mock_response)

            result = client.chat_completion([{"role": "user", "content": "Test"}])

            assert result == "Response"

    def test_temperature_edge_cases(self):
        """Test with different temperature values."""
        for temperature in [0.0, 0.5, 1.0, 1.5]:
            client = OpenAIClient(
                api_key="test",
                base_url="https://test.com",
                model="test-model",
                temperature=temperature,
            )

            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = "Response"
            client.client.chat.completions.create = Mock(return_value=mock_response)

            result = client.chat_completion([{"role": "user", "content": "Test"}])

            assert result == "Response"

    def test_long_content(self):
        """Test with very long content."""
        long_content = "A" * 10000

        client = OpenAIClient(
            api_key="test",
            base_url="https://test.com",
            model="test-model",
        )

        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Response"
        client.client.chat.completions.create = Mock(return_value=mock_response)

        result = client.chat_completion([{"role": "user", "content": long_content}])

        assert result == "Response"

    def test_special_characters_in_content(self):
        """Test with special characters in content."""
        special_content = "Hello\nWorld\tTabbed\u00a0NonBreaking\u200bZeroWidth"

        client = OpenAIClient(
            api_key="test",
            base_url="https://test.com",
            model="test-model",
        )

        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Response"
        client.client.chat.completions.create = Mock(return_value=mock_response)

        result = client.chat_completion([{"role": "user", "content": special_content}])

        assert result == "Response"

    def test_unicode_content(self):
        """Test with unicode content."""
        unicode_content = "Hello 世界 🌍 مرحبا"

        client = OpenAIClient(
            api_key="test",
            base_url="https://test.com",
            model="test-model",
        )

        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Response"
        client.client.chat.completions.create = Mock(return_value=mock_response)

        result = client.chat_completion([{"role": "user", "content": unicode_content}])

        assert result == "Response"
