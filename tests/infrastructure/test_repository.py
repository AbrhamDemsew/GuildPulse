"""Tests for in-memory repository."""

import pytest

from src.domain.channel.aggregate import Channel
from src.domain.shared.errors import ChannelNotFoundError
from src.infrastructure.persistence.memory.repository import InMemoryMessageRepository


class TestInMemoryMessageRepository:
    """Tests for InMemoryMessageRepository."""

    def test_repository_creation(self):
        """Test repository instantiation."""
        repo = InMemoryMessageRepository()
        assert isinstance(repo, InMemoryMessageRepository)

    def test_save_channel(self):
        """Test saving a channel."""
        repo = InMemoryMessageRepository()
        channel = Channel(channel_id=123)
        repo.save(channel)

        assert repo.get(123).channel_id == 123

    def test_get_channel(self):
        """Test getting a channel by ID."""
        repo = InMemoryMessageRepository()
        channel = Channel(channel_id=456)
        repo.save(channel)

        retrieved = repo.get(456)

        assert retrieved.channel_id == 456
        assert retrieved is channel

    def test_get_channel_not_found(self):
        """Test getting non-existent channel."""
        repo = InMemoryMessageRepository()

        with pytest.raises(ChannelNotFoundError) as exc_info:
            repo.get(999)

        assert "999" in str(exc_info.value)

    def test_get_or_create_new_channel(self):
        """Test getting or creating a new channel."""
        repo = InMemoryMessageRepository()

        channel = repo.get_or_create(123)

        assert channel.channel_id == 123
        assert channel.count_messages() == 0
        assert repo.get(123).channel_id == 123

    def test_get_or_create_existing_channel(self):
        """Test getting existing channel with get_or_create."""
        repo = InMemoryMessageRepository()
        original_channel = Channel(channel_id=456, max_messages=50)
        repo.save(original_channel)

        retrieved_channel = repo.get_or_create(456)

        assert retrieved_channel.channel_id == 456
        assert retrieved_channel.max_messages == 50
        assert retrieved_channel is original_channel

    def test_save_overwrite_channel(self):
        """Test that saving same channel ID overwrites."""
        repo = InMemoryMessageRepository()
        channel1 = Channel(channel_id=123)
        channel2 = Channel(channel_id=123, max_messages=100)

        repo.save(channel1)
        repo.save(channel2)

        retrieved = repo.get(123)
        assert retrieved.max_messages == 100
        assert retrieved is channel2

    def test_multiple_channels(self):
        """Test handling multiple channels."""
        repo = InMemoryMessageRepository()

        repo.save(Channel(channel_id=1))
        repo.save(Channel(channel_id=2))
        repo.save(Channel(channel_id=3))

        assert repo.get(1).channel_id == 1
        assert repo.get(2).channel_id == 2
        assert repo.get(3).channel_id == 3


class TestRepositoryEdgeCases:
    """Tests for edge cases in repository."""

    def test_channel_id_zero(self):
        """Test using channel_id=0."""
        repo = InMemoryMessageRepository()
        channel = Channel(channel_id=0)
        repo.save(channel)

        assert repo.get(0).channel_id == 0

    def test_channel_id_large_number(self):
        """Test using large channel ID."""
        repo = InMemoryMessageRepository()
        channel = Channel(channel_id=999999999)
        repo.save(channel)

        assert repo.get(999999999).channel_id == 999999999

    def test_repository_after_many_operations(self):
        """Test repository state after many operations."""
        repo = InMemoryMessageRepository()

        for i in range(10):
            channel = repo.get_or_create(i)
            channel.add_message(None)

        for i in range(10):
            retrieved = repo.get(i)
            assert retrieved.channel_id == i
