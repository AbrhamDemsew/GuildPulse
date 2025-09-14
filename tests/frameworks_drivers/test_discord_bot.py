"""Tests for Discord framework drivers."""

from unittest.mock import AsyncMock, Mock, patch

import pytest

from src.frameworks_drivers.discord.bot import (
    ConfirmClearView,
    handle_message_processing,
    setup_discord_bot,
)


class TestConfirmClearView:
    """Tests for ConfirmClearView component."""

    @pytest.mark.asyncio
    async def test_view_creation(self):
        """Test ConfirmClearView instantiation."""
        mock_use_case = Mock()
        view = ConfirmClearView(mock_use_case, channel_id=123, author_id=456)

        assert view.use_case == mock_use_case
        assert view.channel_id == 123
        assert view.author_id == 456
        assert view.timeout == 60

    @pytest.mark.asyncio
    async def test_confirm_button_author_match(self):
        """Test confirm button with matching author."""
        mock_use_case = Mock()
        mock_use_case.execute.return_value = True
        view = ConfirmClearView(mock_use_case, channel_id=123, author_id=456)

        interaction = Mock()
        interaction.user.id = 456
        interaction.response = Mock()
        interaction.response.edit_message = AsyncMock()

        confirm_btn = None
        for child in view.children:
            if child.label == "Confirm":
                confirm_btn = child
                break

        await confirm_btn.callback(interaction)

        assert mock_use_case.execute.called
        assert interaction.response.edit_message.called
        assert view.is_finished()

    @pytest.mark.asyncio
    async def test_confirm_button_author_mismatch(self):
        """Test confirm button with non-matching author."""
        mock_use_case = Mock()
        view = ConfirmClearView(mock_use_case, channel_id=123, author_id=456)

        interaction = Mock()
        interaction.user.id = 789
        interaction.response = Mock()
        interaction.response.send_message = AsyncMock()

        confirm_btn = None
        for child in view.children:
            if child.label == "Confirm":
                confirm_btn = child
                break

        await confirm_btn.callback(interaction)

        assert interaction.response.send_message.called
        assert not mock_use_case.execute.called
        assert not view.is_finished()

    @pytest.mark.asyncio
    async def test_cancel_button_author_match(self):
        """Test cancel button with matching author."""
        mock_use_case = Mock()
        view = ConfirmClearView(mock_use_case, channel_id=123, author_id=456)

        interaction = Mock()
        interaction.user.id = 456
        interaction.response = Mock()
        interaction.response.edit_message = AsyncMock()

        cancel_btn = None
        for child in view.children:
            if child.label == "Cancel":
                cancel_btn = child
                break

        await cancel_btn.callback(interaction)

        assert interaction.response.edit_message.called
        assert view.is_finished()

    @pytest.mark.asyncio
    async def test_cancel_button_author_mismatch(self):
        """Test cancel button with non-matching author."""
        mock_use_case = Mock()
        view = ConfirmClearView(mock_use_case, channel_id=123, author_id=456)

        interaction = Mock()
        interaction.user.id = 789
        interaction.response = Mock()
        interaction.response.send_message = AsyncMock()

        cancel_btn = None
        for child in view.children:
            if child.label == "Cancel":
                cancel_btn = child
                break

        await cancel_btn.callback(interaction)

        assert interaction.response.send_message.called
        assert not view.is_finished()

    @pytest.mark.asyncio
    async def test_timeout_handler(self):
        """Test timeout handler."""
        mock_use_case = Mock()
        view = ConfirmClearView(mock_use_case, channel_id=123, author_id=456)

        mock_message = Mock()

        view.message = mock_message
        mock_message.edit = AsyncMock()

        await view.on_timeout()

        assert all(child.disabled for child in view.children)
        assert mock_message.edit.called


class TestHandleMessageProcessing:
    """Tests for handle_message_processing function."""

    @pytest.mark.asyncio
    async def test_handle_message_basic(self):
        """Test basic message processing."""
        mock_message = Mock()
        mock_message.channel = Mock()
        mock_message.channel.id = 123
        mock_message.content = "Hello bot"
        mock_message.author.display_name = "Alice"
        mock_message.attachments = []
        mock_typing = AsyncMock()
        mock_message.channel.typing.return_value = mock_typing
        mock_message.channel.send = AsyncMock()

        mock_bot = Mock()
        mock_bot.user = Mock()
        mock_bot.user.name = "TestBot"

        mock_processor = Mock()
        mock_processor.execute.return_value = "Test response"

        mock_lock = Mock()
        mock_lock.__aenter__ = AsyncMock()
        mock_lock.__aexit__ = AsyncMock()

        with patch(
            "src.frameworks_drivers.discord.bot.asyncio.to_thread",
            side_effect=lambda func, *args, **kwargs: func(*args, **kwargs),
        ):
            await handle_message_processing(mock_message, mock_processor, mock_bot, mock_lock)

        assert mock_processor.execute.called

    @pytest.mark.asyncio
    async def test_handle_message_with_attachment(self):
        """Test message processing with attachment."""
        mock_message = Mock()
        mock_message.channel = Mock()
        mock_message.channel.id = 123
        mock_message.content = "Check this out"
        mock_message.author.display_name = "Bob"
        mock_typing = AsyncMock()
        mock_message.channel.typing.return_value = mock_typing
        mock_message.channel.send = AsyncMock()

        mock_attachment = Mock()
        mock_attachment.url = "https://example.com/image.jpg"
        mock_attachment.content_type = "image/jpeg"

        mock_message.attachments = [mock_attachment]

        mock_bot = Mock()
        mock_bot.user = Mock()
        mock_bot.user.name = "TestBot"

        mock_processor = Mock()
        mock_processor.execute.return_value = "Response to image"

        mock_lock = Mock()
        mock_lock.__aenter__ = AsyncMock()
        mock_lock.__aexit__ = AsyncMock()

        with patch(
            "src.frameworks_drivers.discord.bot.asyncio.to_thread",
            side_effect=lambda func, *args, **kwargs: func(*args, **kwargs),
        ):
            await handle_message_processing(mock_message, mock_processor, mock_bot, mock_lock)

        assert mock_processor.execute.called

    @pytest.mark.asyncio
    async def test_handle_message_mentions(self):
        """Test message with bot mentions."""
        mock_message = Mock()
        mock_message.channel = Mock()
        mock_message.channel.id = 123
        mock_message.content = "@TestBot help me"
        mock_message.author.display_name = "Charlie"
        mock_message.attachments = []
        mock_typing = AsyncMock()
        mock_message.channel.typing.return_value = mock_typing
        mock_message.channel.send = AsyncMock()

        mock_bot = Mock()
        mock_bot.user = Mock()
        mock_bot.user.name = "TestBot"

        mock_processor = Mock()
        mock_processor.execute.return_value = "Help response"

        mock_lock = Mock()
        mock_lock.__aenter__ = AsyncMock()
        mock_lock.__aexit__ = AsyncMock()

        with patch(
            "src.frameworks_drivers.discord.bot.asyncio.to_thread",
            side_effect=lambda func, *args, **kwargs: func(*args, **kwargs),
        ):
            await handle_message_processing(mock_message, mock_processor, mock_bot, mock_lock)

        assert mock_processor.execute.called


class TestSetupDiscordBot:
    """Tests for setup_discord_bot function."""

    def test_setup_discord_bot_creates_bot(self):
        """Test that setup_discord_bot creates a bot."""
        with patch("src.frameworks_drivers.discord.bot.setup_logging"):
            with patch("src.config.get_settings") as mock_get_settings:
                mock_settings = Mock(
                    DISCORD_TOKEN="test-token",
                    OPENAI_API_KEY="test-key",
                    OPENAI_BASE_URL="https://test.com",
                    OPENAI_MODEL="test-model",
                    OPENAI_MAX_TOKENS=100,
                    OPENAI_TEMPERATURE=0.5,
                    LOG_LEVEL="DEBUG",
                )
                mock_get_settings.return_value = mock_settings
                mock_settings.model_dump.return_value = {
                    "DISCORD_TOKEN": "test-token",
                    "OPENAI_API_KEY": "test-key",
                    "OPENAI_BASE_URL": "https://test.com",
                    "OPENAI_MODEL": "test-model",
                    "OPENAI_MAX_TOKENS": 100,
                    "OPENAI_TEMPERATURE": 0.5,
                    "CHAT_SYSTEM_PROMPT": "You are a bot",
                    "LOG_LEVEL": "DEBUG",
                    "DEBUG": False,
                }

                bot = setup_discord_bot()

                assert bot is not None
                assert hasattr(bot, "tree")
                assert hasattr(bot, "event")
                assert hasattr(bot, "command")

    @pytest.mark.skip(reason="discord library validation prevents mocking Intents")
    def test_setup_discord_bot_intents(self):
        """Test that setup_discord_bot configures correct intents."""
        pass
