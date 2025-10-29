"""SQLite repository implementation for channel persistence."""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

from src.domain.channel.aggregate import Channel
from src.domain.channel.value_objects import Message, MessageContent
from src.domain.repository import MessageRepository
from src.domain.shared.errors import ChannelNotFoundError
from src.infrastructure.persistence.sqlite.schema import MIGRATIONS

if TYPE_CHECKING:
    pass


class SQLiteChannelRepository(MessageRepository):
    """SQLite-based repository for channel persistence."""

    def __init__(self, db_path: str = "data/channels.db") -> None:
        """Initialize repository with database path."""
        self.db_path = db_path
        self._ensure_database_exists()

    def _ensure_database_exists(self) -> None:
        """Create database and run migrations if needed."""
        db_dir = Path(self.db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Run migrations
        cursor.execute("CREATE TABLE IF NOT EXISTS schema_migrations (version INTEGER PRIMARY KEY)")
        cursor.execute("SELECT version FROM schema_migrations")
        current_version = cursor.fetchone()

        if current_version is None:
            current_version = 0
        else:
            current_version = current_version[0]

        for version, sql in MIGRATIONS:
            if version > current_version:
                cursor.executescript(sql)
                cursor.execute("INSERT INTO schema_migrations (version) VALUES (?)", (version,))

        conn.commit()
        conn.close()

    def _serialize_messages(self, messages: list[Message]) -> str:
        """Serialize messages to JSON string."""
        return json.dumps([{"role": msg.role, "content": msg.content.value} for msg in messages])

    def _deserialize_messages(self, json_str: str) -> list[Message]:
        """Deserialize messages from JSON string."""
        data = json.loads(json_str)
        return [
            Message(role=msg["role"], content=MessageContent(value=msg["content"])) for msg in data
        ]

    def save(self, channel: Channel) -> None:
        """Save channel state to database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """INSERT OR REPLACE INTO channels 
               (channel_id, messages, created_at, updated_at) 
               VALUES (?, ?, ?, ?)""",
            (
                channel.id,
                self._serialize_messages(channel.get_messages()),
                channel.created_at if hasattr(channel, "created_at") else datetime.now(),
                datetime.now(),
            ),
        )

        conn.commit()
        conn.close()

    def get(self, channel_id: int) -> Channel | None:  # type: ignore[override]
        """Retrieve channel by ID, or None if not found."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT messages FROM channels WHERE channel_id = ?", (channel_id,))
        row = cursor.fetchone()

        conn.close()

        if row is None:
            raise ChannelNotFoundError(f"Channel {channel_id} not found")

        messages = self._deserialize_messages(row[0])
        channel = Channel(id=channel_id)
        channel._messages = messages
        return channel

    def get_or_create(self, channel_id: int) -> Channel:
        """Get existing channel or create new one."""
        try:
            return self.get(channel_id)  # type: ignore[return-value]
        except ChannelNotFoundError:
            channel = Channel(id=channel_id)
            self.save(channel)
            return channel
