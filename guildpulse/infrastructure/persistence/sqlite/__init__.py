"""SQLite persistence module."""

from guildpulse.infrastructure.persistence.sqlite.repository import SQLiteChannelRepository
from guildpulse.infrastructure.persistence.sqlite.schema import SCHEMA_VERSION

__all__ = ["SCHEMA_VERSION", "SQLiteChannelRepository"]
