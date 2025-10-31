"""SQLite usage analytics repository."""

from __future__ import annotations

from datetime import date, datetime

from guildpulse.domain.analytics.usage import QuotaStatus, UsageTotals
from guildpulse.infrastructure.persistence.sqlite.database import Database


class SQLiteUsageRepository:
    def __init__(self, database: Database) -> None:
        self.database = database

    def record(
        self,
        guild_id: int,
        user_id: int,
        channel_id: int,
        prompt_tokens: int,
        completion_tokens: int,
    ) -> None:
        total = prompt_tokens + completion_tokens
        today = date.today().isoformat()
        with self.database.connection() as conn:
            conn.execute(
                """
                INSERT INTO usage_records (
                    guild_id, user_id, channel_id,
                    prompt_tokens, completion_tokens, total_tokens,
                    message_count, recorded_on
                ) VALUES (?, ?, ?, ?, ?, ?, 1, ?)
                """,
                (guild_id, user_id, channel_id, prompt_tokens, completion_tokens, total, today),
            )
            conn.commit()

    def _aggregate(
        self,
        guild_id: int,
        recorded_on: date,
        user_id: int | None = None,
    ) -> UsageTotals:
        params: list[int | str] = [guild_id, recorded_on.isoformat()]
        user_clause = ""
        if user_id is not None:
            user_clause = " AND user_id = ?"
            params.append(user_id)

        with self.database.connection() as conn:
            row = conn.execute(
                f"""
                SELECT
                    COALESCE(SUM(message_count), 0) AS message_count,
                    COALESCE(SUM(prompt_tokens), 0) AS prompt_tokens,
                    COALESCE(SUM(completion_tokens), 0) AS completion_tokens,
                    COALESCE(SUM(total_tokens), 0) AS total_tokens
                FROM usage_records
                WHERE guild_id = ? AND recorded_on = ?{user_clause}
                """,
                tuple(params),
            ).fetchone()

        return UsageTotals(
            guild_id=guild_id,
            recorded_on=recorded_on,
            message_count=int(row["message_count"]),
            prompt_tokens=int(row["prompt_tokens"]),
            completion_tokens=int(row["completion_tokens"]),
            total_tokens=int(row["total_tokens"]),
            user_id=user_id,
        )

    def totals_for_guild(self, guild_id: int, recorded_on: date) -> UsageTotals:
        return self._aggregate(guild_id, recorded_on)

    def totals_for_user(self, guild_id: int, user_id: int, recorded_on: date) -> UsageTotals:
        return self._aggregate(guild_id, recorded_on, user_id=user_id)

    def quota_status(
        self,
        guild_id: int,
        messages_limit: int,
        tokens_limit: int,
        recorded_on: date,
    ) -> QuotaStatus:
        totals = self.totals_for_guild(guild_id, recorded_on)
        return QuotaStatus(
            guild_id=guild_id,
            recorded_on=recorded_on,
            messages_used=totals.message_count,
            messages_limit=messages_limit,
            tokens_used=totals.total_tokens,
            tokens_limit=tokens_limit,
        )

    def reset_user_rate_window(self, guild_id: int, user_id: int) -> None:
        with self.database.connection() as conn:
            conn.execute(
                "DELETE FROM user_rate_limits WHERE guild_id = ? AND user_id = ?",
                (guild_id, user_id),
            )
            conn.commit()

    def increment_user_rate(self, guild_id: int, user_id: int, window_seconds: int = 60) -> int:
        now = datetime.now()
        with self.database.connection() as conn:
            row = conn.execute(
                "SELECT window_start, message_count FROM user_rate_limits WHERE user_id = ? AND guild_id = ?",
                (user_id, guild_id),
            ).fetchone()
            if row is None:
                conn.execute(
                    """
                    INSERT INTO user_rate_limits (user_id, guild_id, window_start, message_count)
                    VALUES (?, ?, ?, 1)
                    """,
                    (user_id, guild_id, now.isoformat()),
                )
                conn.commit()
                return 1

            window_start = datetime.fromisoformat(row["window_start"])
            count = int(row["message_count"])
            elapsed = (now - window_start).total_seconds()
            if elapsed > window_seconds:
                conn.execute(
                    """
                    UPDATE user_rate_limits
                    SET window_start = ?, message_count = 1
                    WHERE user_id = ? AND guild_id = ?
                    """,
                    (now.isoformat(), user_id, guild_id),
                )
                conn.commit()
                return 1

            count += 1
            conn.execute(
                """
                UPDATE user_rate_limits SET message_count = ?
                WHERE user_id = ? AND guild_id = ?
                """,
                (count, user_id, guild_id),
            )
            conn.commit()
            return count
