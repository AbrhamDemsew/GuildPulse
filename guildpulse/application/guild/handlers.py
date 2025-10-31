"""Guild configuration use cases."""

from __future__ import annotations

import logging

from guildpulse.application.ports.guild_settings_repository_port import IGuildSettingsRepository
from guildpulse.domain.guild.aggregate import GuildSettings


class GetGuildSettings:
    def __init__(self, repo: IGuildSettingsRepository, default_prompt: str) -> None:
        self.repo = repo
        self.default_prompt = default_prompt
        self.logger = logging.getLogger(__name__)

    def execute(self, guild_id: int) -> GuildSettings:
        settings = self.repo.get_or_create_default(guild_id, self.default_prompt)
        self.logger.debug("Loaded guild settings for guild_id=%s", guild_id)
        return settings


class UpdateGuildSettings:
    def __init__(self, repo: IGuildSettingsRepository) -> None:
        self.repo = repo
        self.logger = logging.getLogger(__name__)

    def update_prompt(self, guild_id: int, prompt: str, default_prompt: str) -> GuildSettings:
        settings = self.repo.get_or_create_default(guild_id, default_prompt)
        settings.update_prompt(prompt)
        self.repo.save(settings)
        self.logger.info("Updated system prompt for guild_id=%s", guild_id)
        return settings

    def update_model(
        self,
        guild_id: int,
        model_name: str,
        max_tokens: int,
        temperature: float,
        default_prompt: str,
    ) -> GuildSettings:
        settings = self.repo.get_or_create_default(guild_id, default_prompt)
        settings.update_model(model_name, max_tokens, temperature)
        self.repo.save(settings)
        return settings

    def update_history(self, guild_id: int, max_history: int, default_prompt: str) -> GuildSettings:
        settings = self.repo.get_or_create_default(guild_id, default_prompt)
        settings.set_history_limit(max_history)
        self.repo.save(settings)
        return settings

    def update_quotas(
        self,
        guild_id: int,
        daily_messages: int,
        daily_tokens: int,
        default_prompt: str,
    ) -> GuildSettings:
        settings = self.repo.get_or_create_default(guild_id, default_prompt)
        settings.set_quotas(daily_messages, daily_tokens)
        self.repo.save(settings)
        return settings

    def update_allowed_channels(
        self,
        guild_id: int,
        channel_ids: list[int],
        default_prompt: str,
    ) -> GuildSettings:
        settings = self.repo.get_or_create_default(guild_id, default_prompt)
        settings.set_allowed_channels(channel_ids)
        self.repo.save(settings)
        return settings

    def toggle_moderation(self, guild_id: int, enabled: bool, default_prompt: str) -> GuildSettings:
        settings = self.repo.get_or_create_default(guild_id, default_prompt)
        settings.moderation_enabled = enabled
        self.repo.save(settings)
        return settings

    def toggle_knowledge(self, guild_id: int, enabled: bool, default_prompt: str) -> GuildSettings:
        settings = self.repo.get_or_create_default(guild_id, default_prompt)
        settings.knowledge_enabled = enabled
        self.repo.save(settings)
        return settings


class ResetGuildSettings:
    def __init__(self, repo: IGuildSettingsRepository) -> None:
        self.repo = repo

    def execute(self, guild_id: int, default_prompt: str) -> GuildSettings:
        self.repo.delete(guild_id)
        return self.repo.get_or_create_default(guild_id, default_prompt)


class ListConfiguredGuilds:
    def __init__(self, repo: IGuildSettingsRepository) -> None:
        self.repo = repo

    def execute(self) -> list[int]:
        return self.repo.list_guild_ids()
