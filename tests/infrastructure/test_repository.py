"""Tests for in-memory repository."""

from guildpulse.domain.channel.aggregate import Channel
from guildpulse.domain.channel.value_objects import Message, MessageContent
from guildpulse.domain.shared.errors import ChannelNotFoundError

import pytest

from guildpulse.infrastructure.persistence.memory.repository import InMemoryChannelRepository


class TestInMemoryChannelRepository:
    """Tests for InMemoryChannelRepository."""

    def test_repository_creation(self):
        """Test repository instantiation."""
        repo = InMemoryChannelRepository()
        assert isinstance(repo, InMemoryChannelRepository)

    def test_save_channel(self):
        """Test saving a channel."""
        repo = InMemoryChannelRepository()
        channel = Channel(id=123)
        repo.save(channel)

        assert repo.get(123).id == 123

    def test_get_channel(self):
        """Test getting a channel by ID."""
        repo = InMemoryChannelRepository()
        channel = Channel(id=456)
        repo.save(channel)

        retrieved = repo.get(456)

        assert retrieved.id == 456
        assert retrieved is channel

    def test_get_channel_not_found(self):
        """Test getting non-existent channel."""
        repo = InMemoryChannelRepository()

        with pytest.raises(ChannelNotFoundError) as exc_info:
            repo.get(999)

        assert "999" in str(exc_info.value)

    def test_get_or_create_new_channel(self):
        """Test getting or creating a new channel."""
        repo = InMemoryChannelRepository()

        channel = repo.get_or_create(123)

        assert channel.id == 123
        assert channel.count_messages() == 0
        assert repo.get(123).id == 123

    def test_get_or_create_existing_channel(self):
        """Test getting existing channel with get_or_create."""
        repo = InMemoryChannelRepository()
        original_channel = Channel(id=456, max_messages=50)
        repo.save(original_channel)

        retrieved_channel = repo.get_or_create(456)

        assert retrieved_channel.id == 456
        assert retrieved_channel.max_messages == 50
        assert retrieved_channel is original_channel

    def test_save_overwrite_channel(self):
        """Test that saving same channel ID overwrites."""
        repo = InMemoryChannelRepository()
        channel1 = Channel(id=123)
        channel2 = Channel(id=123, max_messages=100)

        repo.save(channel1)
        repo.save(channel2)

        retrieved = repo.get(123)
        assert retrieved.max_messages == 100
        assert retrieved is channel2

    def test_multiple_channels(self):
        """Test handling multiple channels."""
        repo = InMemoryChannelRepository()

        repo.save(Channel(id=1))
        repo.save(Channel(id=2))
        repo.save(Channel(id=3))

        assert repo.get(1).id == 1
        assert repo.get(2).id == 2
        assert repo.get(3).id == 3


class TestRepositoryEdgeCases:
    """Tests for edge cases in repository."""

    def test_channel_id_zero(self):
        """Test using channel_id=0."""
        repo = InMemoryChannelRepository()
        channel = Channel(id=0)
        repo.save(channel)

        assert repo.get(0).id == 0

    def test_channel_id_large_number(self):
        """Test using large channel ID."""
        repo = InMemoryChannelRepository()
        channel = Channel(id=999999999)
        repo.save(channel)

        assert repo.get(999999999).id == 999999999

    def test_repository_after_many_operations(self):
        """Test repository state after many operations."""
        repo = InMemoryChannelRepository()

        for i in range(10):
            channel = repo.get_or_create(i)
            message = Message(role="user", content=MessageContent(value="Test"))
            channel.add_message(message)

        for i in range(10):
            retrieved = repo.get(i)
            assert retrieved.id == i
