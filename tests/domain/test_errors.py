"""Tests for domain errors."""

import pytest

from src.domain.shared.errors import (
    ChannelNotFoundError,
    ConversationHistoryError,
    DomainError,
    MessageValidationError,
)


class TestDomainError:
    """Tests for DomainError base class."""

    def test_domain_error_is_exception(self):
        """Test that DomainError is a subclass of Exception."""
        assert issubclass(DomainError, Exception)

    def test_domain_error_can_be_raised(self):
        """Test that DomainError can be raised and caught."""
        with pytest.raises(DomainError):
            raise DomainError("Test error")


class TestChannelNotFoundError:
    """Tests for ChannelNotFoundError."""

    def test_channel_not_found_is_domain_error(self):
        """Test that ChannelNotFoundError inherits from DomainError."""
        assert issubclass(ChannelNotFoundError, DomainError)

    def test_channel_not_found_error_message(self):
        """Test ChannelNotFoundError with custom message."""
        error = ChannelNotFoundError("Channel 123 not found")
        assert str(error) == "Channel 123 not found"

    def test_channel_not_found_error_in_message(self):
        """Test that channel ID is in the error message."""
        error = ChannelNotFoundError("Channel 456 not found")
        assert "456" in str(error)

    def test_channel_not_found_can_be_caught_as_base(self):
        """Test that ChannelNotFoundError can be caught as DomainError."""
        try:
            raise ChannelNotFoundError("Test")
        except DomainError:
            pass


class TestMessageValidationError:
    """Tests for MessageValidationError."""

    def test_message_validation_error_is_domain_error(self):
        """Test that MessageValidationError inherits from DomainError."""
        assert issubclass(MessageValidationError, DomainError)

    def test_message_validation_error_message(self):
        """Test MessageValidationError with custom message."""
        error = MessageValidationError("Invalid content")
        assert str(error) == "Invalid content"


class TestConversationHistoryError:
    """Tests for ConversationHistoryError."""

    def test_conversation_history_error_is_domain_error(self):
        """Test that ConversationHistoryError inherits from DomainError."""
        assert issubclass(ConversationHistoryError, DomainError)

    def test_conversation_history_error_message(self):
        """Test ConversationHistoryError with custom message."""
        error = ConversationHistoryError("History operation failed")
        assert str(error) == "History operation failed"


class TestErrorHierarchy:
    """Tests for exception hierarchy."""

    def test_all_errors_inherit_from_domain_error(self):
        """Test that all custom errors inherit from DomainError."""
        errors = [
            DomainError,
            ChannelNotFoundError,
            MessageValidationError,
            ConversationHistoryError,
        ]
        for error_class in errors:
            assert issubclass(error_class, DomainError)

    def test_errors_are_distinct(self):
        """Test that error types are distinct."""
        assert DomainError is not ChannelNotFoundError
        assert DomainError is not MessageValidationError
        assert DomainError is not ConversationHistoryError

    def test_errors_can_be_caught_individually(self):
        """Test that errors can be caught individually."""
        with pytest.raises(ChannelNotFoundError):
            raise ChannelNotFoundError("test")

        with pytest.raises(MessageValidationError):
            raise MessageValidationError("test")

        with pytest.raises(ConversationHistoryError):
            raise ConversationHistoryError("test")

    def test_specific_catches_before_base(self):
        """Test that specific errors are caught before base class."""
        try:
            raise ChannelNotFoundError("test")
        except ChannelNotFoundError:
            caught = True
        except DomainError:
            caught = False
        assert caught
