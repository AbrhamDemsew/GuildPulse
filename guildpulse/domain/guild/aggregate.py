"""Guild configuration aggregate."""

from __future__ import annotations

import json
from dataclasses import dataclass, field

from guildpulse.domain.shared.aggregate_root import AggregateRoot


@dataclass
class GuildSettings(AggregateRoot[int]):
    """Per-guild configuration for AI behavior, moderation, and quotas."""

    system_prompt: str = (
        "You are GuildPulse, a helpful Discord community assistant. "
        "Reply concisely and clearly. Match the user's language when possible."
    )
    model_name: str = "gpt-4o-mini"
    max_history: int = 100
    max_tokens: int = 500
    temperature: float = 0.7
    moderation_enabled: bool = True
    knowledge_enabled: bool = True
    daily_message_quota: int = 500
    daily_token_quota: int = 100_000
    allowed_channel_ids: list[int] = field(default_factory=list)
    admin_role_ids: list[int] = field(default_factory=list)

    def update_prompt(self, prompt: str) -> None:
        cleaned = prompt.strip()
        if not cleaned:
            raise ValueError("System prompt cannot be empty")
        if len(cleaned) > 4000:
            raise ValueError("System prompt exceeds 4000 characters")
        self.system_prompt = cleaned

    def update_model(self, model_name: str, max_tokens: int, temperature: float) -> None:
        if not model_name.strip():
            raise ValueError("Model name is required")
        if max_tokens < 1 or max_tokens > 8192:
            raise ValueError("max_tokens must be between 1 and 8192")
        if temperature < 0.0 or temperature > 2.0:
            raise ValueError("temperature must be between 0 and 2")
        self.model_name = model_name.strip()
        self.max_tokens = max_tokens
        self.temperature = temperature

    def set_history_limit(self, max_history: int) -> None:
        if max_history < 1 or max_history > 500:
            raise ValueError("max_history must be between 1 and 500")
        self.max_history = max_history

    def set_quotas(self, daily_messages: int, daily_tokens: int) -> None:
        if daily_messages < 1:
            raise ValueError("daily_message_quota must be positive")
        if daily_tokens < 100:
            raise ValueError("daily_token_quota must be at least 100")
        self.daily_message_quota = daily_messages
        self.daily_token_quota = daily_tokens

    def set_allowed_channels(self, channel_ids: list[int]) -> None:
        self.allowed_channel_ids = sorted(set(channel_ids))

    def set_admin_roles(self, role_ids: list[int]) -> None:
        self.admin_role_ids = sorted(set(role_ids))

    def is_channel_allowed(self, channel_id: int) -> bool:
        if not self.allowed_channel_ids:
            return True
        return channel_id in self.allowed_channel_ids

    def to_json_lists(self) -> tuple[str, str]:
        return json.dumps(self.allowed_channel_ids), json.dumps(self.admin_role_ids)

    @classmethod
    def from_row(
        cls,
        guild_id: int,
        system_prompt: str,
        model_name: str,
        max_history: int,
        max_tokens: int,
        temperature: float,
        moderation_enabled: int,
        knowledge_enabled: int,
        daily_message_quota: int,
        daily_token_quota: int,
        allowed_channel_ids: str,
        admin_role_ids: str,
    ) -> GuildSettings:
        return cls(
            id=guild_id,
            system_prompt=system_prompt,
            model_name=model_name,
            max_history=max_history,
            max_tokens=max_tokens,
            temperature=temperature,
            moderation_enabled=bool(moderation_enabled),
            knowledge_enabled=bool(knowledge_enabled),
            daily_message_quota=daily_message_quota,
            daily_token_quota=daily_token_quota,
            allowed_channel_ids=json.loads(allowed_channel_ids or "[]"),
            admin_role_ids=json.loads(admin_role_ids or "[]"),
        )

    @classmethod
    def default_for(cls, guild_id: int, default_prompt: str) -> GuildSettings:
        return cls(id=guild_id, system_prompt=default_prompt)
