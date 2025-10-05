"""Tests for domain errors."""

from typing import Callable

import pytest

from src.domain.shared.errors import (
    ChannelNotFoundError,
    ConversationHistoryError,
    DomainError,
    MessageValidationError,
)

# ============================================================================
# TestDomainError - with parameterized tests
# ============================================================================


class TestDomainError:
    """Tests for DomainError base class."""

    def test_domain_error_is_exception(self):
        """Test that DomainError is a subclass of Exception."""
        assert issubclass(DomainError, Exception)

    @pytest.mark.parametrize(
        "error_message",
        [
            "Test error",
            "",
            "A" * 1000,
            "Error with unicode: 🎉",
            "Error with\nnewlines",
        ],
    )
    def test_domain_error_can_be_raised(self, error_message: str) -> None:
        """Test that DomainError can be raised and caught."""
        with pytest.raises(DomainError):
            raise DomainError(error_message)


# ============================================================================
# TestChannelNotFoundError - with parameterized tests
# ============================================================================


class TestChannelNotFoundError:
    """Tests for ChannelNotFoundError."""

    def test_channel_not_found_is_domain_error(self):
        """Test that ChannelNotFoundError inherits from DomainError."""
        assert issubclass(ChannelNotFoundError, DomainError)

    @pytest.mark.parametrize("channel_id", [123, 456, 0, -1, 9999])
    def test_channel_not_found_error_message(self, channel_id: int) -> None:
        """Test ChannelNotFoundError with custom message."""
        error = ChannelNotFoundError(f"Channel {channel_id} not found")
        assert str(error) == f"Channel {channel_id} not found"

    @pytest.mark.parametrize("channel_id", [123, 456, 0, 9999])
    def test_channel_not_found_error_in_message(self, channel_id: int) -> None:
        """Test that channel ID is in the error message."""
        error = ChannelNotFoundError(f"Channel {channel_id} not found")
        assert str(channel_id) in str(error)

    @pytest.mark.parametrize("channel_id", [123, 456, 0, 9999])
    def test_channel_not_found_can_be_caught_as_base(self, channel_id: int) -> None:
        """Test that ChannelNotFoundError can be caught as DomainError."""
        try:
            raise ChannelNotFoundError(f"Channel {channel_id} not found")
        except DomainError:
            pass


# ============================================================================
# TestMessageValidationError - with parameterized tests
# ============================================================================


class TestMessageValidationError:
    """Tests for MessageValidationError."""

    def test_message_validation_error_is_domain_error(self):
        """Test that MessageValidationError inherits from DomainError."""
        assert issubclass(MessageValidationError, DomainError)

    @pytest.mark.parametrize(
        "error_message",
        [
            "Invalid content",
            "",
            "A" * 1000,
        ],
    )
    def test_message_validation_error_message(self, error_message: str) -> None:
        """Test MessageValidationError with custom message."""
        error = MessageValidationError(error_message)
        assert str(error) == error_message


# ============================================================================
# TestConversationHistoryError - with parameterized tests
# ============================================================================


class TestConversationHistoryError:
    """Tests for ConversationHistoryError."""

    def test_conversation_history_error_is_domain_error(self) -> None:
        """Test that ConversationHistoryError inherits from DomainError."""
        assert issubclass(ConversationHistoryError, DomainError)

    @pytest.mark.parametrize(
        "error_message",
        [
            "History operation failed",
            "",
            "A" * 1000,
        ],
    )
    def test_conversation_history_error_message(self, error_message: str) -> None:
        """Test ConversationHistoryError with custom message."""
        error = ConversationHistoryError(error_message)
        assert str(error) == error_message


# ============================================================================
# TestErrorHierarchy - with parameterized tests
# ============================================================================


class TestErrorHierarchy:
    """Tests for exception hierarchy."""

    @pytest.mark.parametrize(
        "error_class",
        [
            DomainError,
            ChannelNotFoundError,
            MessageValidationError,
            ConversationHistoryError,
        ],
    )
    def test_all_errors_inherit_from_domain_error(self, error_class: type) -> None:
        """Test that all custom errors inherit from DomainError."""
        assert issubclass(error_class, DomainError)

    def test_errors_are_distinct(self):
        """Test that error types are distinct."""
        assert DomainError is not ChannelNotFoundError
        assert DomainError is not MessageValidationError
        assert DomainError is not ConversationHistoryError

    @pytest.mark.parametrize(
        "error_factory",
        [
            lambda: ChannelNotFoundError("test"),
            lambda: MessageValidationError("test"),
            lambda: ConversationHistoryError("test"),
        ],
    )
    def test_errors_can_be_caught_individually(
        self, error_factory: Callable[[], DomainError]
    ) -> None:
        """Test that errors can be caught individually."""
        with pytest.raises(DomainError):
            raise error_factory()

    def test_specific_catches_before_base(self):
        """Test that specific errors are caught before base class."""
        try:
            raise ChannelNotFoundError("test")
        except ChannelNotFoundError:
            caught = True
        except DomainError:
            caught = False
        assert caught


# ============================================================================
# Error handling patterns - with parameterized tests
# ============================================================================


@pytest.mark.parametrize(
    "error_class",
    [
        ChannelNotFoundError,
        MessageValidationError,
        ConversationHistoryError,
    ],
)
def test_specific_error_types(error_class: type) -> None:
    """Test that specific error types can be instantiated."""
    error = error_class("test message")
    assert isinstance(error, error_class)
    assert isinstance(error, DomainError)
    assert str(error) == "test message"


@pytest.mark.parametrize(
    "error_message",
    [
        "Error 1",
        "Error 2",
        "A" * 100,
    ],
)
def test_error_messages(error_message: str) -> None:
    """Test various error messages."""
    error = DomainError(error_message)
    assert str(error) == error_message
