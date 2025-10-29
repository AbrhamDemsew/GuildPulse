"""Tests for SQLite repository implementation."""

import os
import tempfile
from typing import Generator

import pytest

from src.domain.channel.aggregate import Channel
from src.domain.channel.value_objects import Message, MessageContent
from src.infrastructure.persistence.sqlite.repository import SQLiteChannelRepository


@pytest.fixture
def temp_db_path() -> Generator[str, None, None]:
    """Create temporary database path."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        path = f.name
    yield path
    os.unlink(path)


@pytest.fixture
def repo(temp_db_path: str) -> SQLiteChannelRepository:
    """Create repository with temp database."""
    return SQLiteChannelRepository(db_path=temp_db_path)


class TestSQLiteRepository:
    """Tests for SQLiteChannelRepository."""

    def test_save_and_get_channel(self, repo: SQLiteChannelRepository) -> None:
        """Test saving and retrieving a channel."""
        channel = Channel(id=123)
        channel.add_message(Message(role="user", content=MessageContent(value="Hello")))

        repo.save(channel)

        retrieved = repo.get(123)
        assert retrieved is not None
        assert retrieved.id == 123
        assert len(retrieved.get_messages()) == 1

    def test_get_nonexistent_channel(self, repo: SQLiteChannelRepository) -> None:
        """Test getting a non-existent channel raises ChannelNotFoundError."""
        from src.domain.shared.errors import ChannelNotFoundError

        with pytest.raises(ChannelNotFoundError) as exc_info:
            repo.get(999)

        assert "999" in str(exc_info.value)

    def test_get_or_create_new_channel(self, repo: SQLiteChannelRepository) -> None:
        """Test get_or_create creates new channel if not exists."""
        channel = repo.get_or_create(456)

        assert channel.id == 456
        assert len(channel.get_messages()) == 0

    def test_get_or_create_existing_channel(self, repo: SQLiteChannelRepository) -> None:
        """Test get_or_create returns existing channel."""
        # First save
        channel = Channel(id=789)
        channel.add_message(Message(role="user", content=MessageContent(value="Test")))
        repo.save(channel)

        # Get again
        retrieved = repo.get_or_create(789)

        assert retrieved.id == 789
        assert len(retrieved.get_messages()) == 1

    def test_multiple_channels(self, repo: SQLiteChannelRepository) -> None:
        """Test storing multiple channels independently."""
        repo.save(Channel(id=1))
        repo.save(Channel(id=2))
        repo.save(Channel(id=3))

        assert repo.get(1) is not None
        assert repo.get(2) is not None
        assert repo.get(3) is not None

    def test_persistence_across_repositories(self, temp_db_path: str) -> None:
        """Test data persists when creating new repository instance."""
        # First repo
        repo1 = SQLiteChannelRepository(db_path=temp_db_path)
        channel = repo1.get_or_create(111)
        channel.add_message(Message(role="user", content=MessageContent(value="Msg1")))
        repo1.save(channel)

        # Second repo (simulates restart)
        repo2 = SQLiteChannelRepository(db_path=temp_db_path)
        retrieved = repo2.get(111)

        assert retrieved is not None
        assert len(retrieved.get_messages()) == 1
        assert retrieved.get_messages()[0].content.value == "Msg1"

    def test_clear_channel_in_db(self, repo: SQLiteChannelRepository) -> None:
        """Test clearing a channel works correctly."""
        channel = Channel(id=222)
        channel.add_message(Message(role="user", content=MessageContent(value="Msg1")))
        channel.add_message(Message(role="assistant", content=MessageContent(value="Msg2")))
        repo.save(channel)

        channel.clear()
        repo.save(channel)

        retrieved = repo.get(222)
        assert retrieved is not None
        assert len(retrieved.get_messages()) == 0


class TestSQLiteRepositoryEdgeCases:
    """Tests for edge cases in SQLite repository."""

    def test_channel_id_zero(self, repo: SQLiteChannelRepository) -> None:
        """Test using channel_id=0."""
        channel = Channel(id=0)
        repo.save(channel)

        assert repo.get(0).id == 0  # type: ignore[union-attr]

    def test_channel_id_large_number(self, repo: SQLiteChannelRepository) -> None:
        """Test using large channel ID."""
        channel = Channel(id=999999999)
        repo.save(channel)

        assert repo.get(999999999).id == 999999999  # type: ignore[union-attr]

    def test_repository_after_many_operations(self, repo: SQLiteChannelRepository) -> None:
        """Test repository state after many operations."""
        for i in range(10):
            channel = repo.get_or_create(i)
            message = Message(role="user", content=MessageContent(value="Test"))
            channel.add_message(message)

        for i in range(10):
            retrieved = repo.get(i)
            assert retrieved.id == i  # type: ignore[union-attr]
