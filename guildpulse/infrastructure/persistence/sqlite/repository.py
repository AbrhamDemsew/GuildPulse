"""SQLite repository implementation for channel persistence."""

from __future__ import annotations

import json
from datetime import datetime

from guildpulse.domain.channel.aggregate import Channel
from guildpulse.domain.channel.value_objects import Message, MessageContent
from guildpulse.domain.repository import MessageRepository
from guildpulse.domain.shared.errors import ChannelNotFoundError
from guildpulse.infrastructure.persistence.sqlite.database import Database


class SQLiteChannelRepository(MessageRepository):
    """SQLite-based repository for channel persistence."""

    def __init__(self, db_path: str | None = None, database: Database | None = None) -> None:
        self.database = database or Database(db_path or "data/channels.db")

    def _serialize_messages(self, messages: list[Message]) -> str:
        return json.dumps([{"role": msg.role, "content": msg.content.value} for msg in messages])

    def _deserialize_messages(self, json_str: str) -> list[Message]:
        data = json.loads(json_str)
        return [
            Message(role=msg["role"], content=MessageContent(value=msg["content"])) for msg in data
        ]

    def save(self, channel: Channel) -> None:
        with self.database.connection() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO channels
                (channel_id, messages, created_at, updated_at)
                VALUES (?, ?, ?, ?)
                """,
                (
                    channel.id,
                    self._serialize_messages(channel.get_messages()),
                    datetime.now().isoformat(),
                    datetime.now().isoformat(),
                ),
            )
            conn.commit()

    def get(self, channel_id: int) -> Channel | None:
        with self.database.connection() as conn:
            row = conn.execute(
                "SELECT messages FROM channels WHERE channel_id = ?",
                (channel_id,),
            ).fetchone()

        if row is None:
            raise ChannelNotFoundError(f"Channel {channel_id} not found")

        messages = self._deserialize_messages(row["messages"])
        channel = Channel(id=channel_id)
        channel._messages = messages
        return channel

    def get_or_create(self, channel_id: int) -> Channel:
        try:
            return self.get(channel_id)  # type: ignore[return-value]
        except ChannelNotFoundError:
            channel = Channel(id=channel_id)
            self.save(channel)
            return channel
