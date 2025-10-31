"""Dependency injection composition root."""

from __future__ import annotations

import os

from guildpulse.application.analytics.handlers import CheckGuildQuota, GetGuildUsageReport, RecordTokenUsage
from guildpulse.application.guild.handlers import (
    GetGuildSettings,
    ListConfiguredGuilds,
    ResetGuildSettings,
    UpdateGuildSettings,
)
from guildpulse.application.knowledge.handlers import (
    AddKnowledgeDocument,
    GetKnowledgeDocument,
    ListKnowledgeDocuments,
    RemoveKnowledgeDocument,
    SearchGuildKnowledge,
)
from guildpulse.application.messaging.handlers import ClearChannelHistory, ProcessUserTurn
from guildpulse.application.moderation.handlers import EvaluateIncomingMessage, ListModerationEvents
from guildpulse.application.ports.ai_service_port import IAIServicePort
from guildpulse.application.ports.channel_repository_port import IChannelRepositoryPort
from guildpulse.config import Settings
from guildpulse.infrastructure.ai.openai.adapter import OpenAIServiceAdapter
from guildpulse.infrastructure.ai.openai.client import OpenAIClient
from guildpulse.infrastructure.knowledge.chunker import TextChunker
from guildpulse.infrastructure.moderation.content_moderator import ContentModerator
from guildpulse.infrastructure.persistence.sqlite.database import Database
from guildpulse.infrastructure.persistence.sqlite.guild_repository import SQLiteGuildSettingsRepository
from guildpulse.infrastructure.persistence.sqlite.knowledge_repository import SQLiteKnowledgeRepository
from guildpulse.infrastructure.persistence.sqlite.moderation_repository import SQLiteModerationLogRepository
from guildpulse.infrastructure.persistence.sqlite.repository import SQLiteChannelRepository
from guildpulse.infrastructure.persistence.sqlite.usage_repository import SQLiteUsageRepository
from guildpulse.ops.audit import AuditLogStore
from guildpulse.plugins.registry import PluginRegistry, build_default_registry
from guildpulse.ops.metrics_collector import GLOBAL_METRICS
from guildpulse.services.conversation_orchestrator import ConversationOrchestrator
from guildpulse.services.guild_onboarding import GuildOnboardingService


class CompositionRoot:
    """Dependency injection composition root for the application."""

    def __init__(self, config: Settings, db_path: str | None = None) -> None:
        self.config = config
        self.db_path = db_path or os.environ.get("DATABASE_PATH", "data/channels.db")
        self.database = Database(self.db_path)
        self._repo: IChannelRepositoryPort | None = None
        self._ai_service: IAIServicePort | None = None
        self._guild_repo: SQLiteGuildSettingsRepository | None = None
        self._moderation_repo: SQLiteModerationLogRepository | None = None
        self._usage_repo: SQLiteUsageRepository | None = None
        self._knowledge_repo: SQLiteKnowledgeRepository | None = None
        self._moderator: ContentModerator | None = None
        self._audit_log: AuditLogStore | None = None
        self._plugin_registry: PluginRegistry | None = None

    @property
    def repo(self) -> IChannelRepositoryPort:
        if self._repo is None:
            self._repo = SQLiteChannelRepository(database=self.database)
        return self._repo

    @property
    def guild_repo(self) -> SQLiteGuildSettingsRepository:
        if self._guild_repo is None:
            self._guild_repo = SQLiteGuildSettingsRepository(self.database)
        return self._guild_repo

    @property
    def moderation_repo(self) -> SQLiteModerationLogRepository:
        if self._moderation_repo is None:
            self._moderation_repo = SQLiteModerationLogRepository(self.database)
        return self._moderation_repo

    @property
    def usage_repo(self) -> SQLiteUsageRepository:
        if self._usage_repo is None:
            self._usage_repo = SQLiteUsageRepository(self.database)
        return self._usage_repo

    @property
    def knowledge_repo(self) -> SQLiteKnowledgeRepository:
        if self._knowledge_repo is None:
            self._knowledge_repo = SQLiteKnowledgeRepository(self.database)
        return self._knowledge_repo

    @property
    def ai_service(self) -> IAIServicePort:
        if self._ai_service is None:
            client = OpenAIClient(
                api_key=self.config.OPENAI_API_KEY,
                base_url=self.config.OPENAI_BASE_URL,
                model=self.config.OPENAI_MODEL,
                max_tokens=self.config.OPENAI_MAX_TOKENS,
                temperature=self.config.OPENAI_TEMPERATURE,
            )
            self._ai_service = OpenAIServiceAdapter(client, self.config.CHAT_SYSTEM_PROMPT)
        return self._ai_service

    @property
    def audit_log(self) -> AuditLogStore:
        if self._audit_log is None:
            self._audit_log = AuditLogStore(self.database)
        return self._audit_log

    @property
    def plugin_registry(self) -> PluginRegistry:
        if self._plugin_registry is None:
            self._plugin_registry = build_default_registry(
                metrics_text_provider=lambda: str(GLOBAL_METRICS.snapshot().__dict__)
            )
        return self._plugin_registry

    @property
    def content_moderator(self) -> ContentModerator:
        if self._moderator is None:
            self._moderator = ContentModerator(self.usage_repo, per_minute_limit=12)
        return self._moderator

    def create_message_processor(self) -> ProcessUserTurn:
        moderation = EvaluateIncomingMessage(self.content_moderator, self.moderation_repo)
        knowledge = SearchGuildKnowledge(self.knowledge_repo)
        usage = RecordTokenUsage(self.usage_repo)
        quota = CheckGuildQuota(self.usage_repo)
        return ProcessUserTurn(
            self.repo,
            self.ai_service,
            guild_repo=self.guild_repo,
            default_prompt=self.config.CHAT_SYSTEM_PROMPT,
            moderation=moderation,
            knowledge_search=knowledge,
            usage_recorder=usage,
            quota_checker=quota,
        )

    def create_clear_history_use_case(self) -> ClearChannelHistory:
        return ClearChannelHistory(self.repo)

    def create_get_guild_settings(self) -> GetGuildSettings:
        return GetGuildSettings(self.guild_repo, self.config.CHAT_SYSTEM_PROMPT)

    def create_update_guild_settings(self) -> UpdateGuildSettings:
        return UpdateGuildSettings(self.guild_repo)

    def create_reset_guild_settings(self) -> ResetGuildSettings:
        return ResetGuildSettings(self.guild_repo)

    def create_list_guilds(self) -> ListConfiguredGuilds:
        return ListConfiguredGuilds(self.guild_repo)

    def create_usage_report(self) -> GetGuildUsageReport:
        return GetGuildUsageReport(self.usage_repo)

    def create_quota_checker(self) -> CheckGuildQuota:
        return CheckGuildQuota(self.usage_repo)

    def create_moderation_events(self) -> ListModerationEvents:
        return ListModerationEvents(self.moderation_repo)

    def create_add_knowledge(self) -> AddKnowledgeDocument:
        return AddKnowledgeDocument(self.knowledge_repo, TextChunker())

    def create_search_knowledge(self) -> SearchGuildKnowledge:
        return SearchGuildKnowledge(self.knowledge_repo)

    def create_list_knowledge(self) -> ListKnowledgeDocuments:
        return ListKnowledgeDocuments(self.knowledge_repo)

    def create_remove_knowledge(self) -> RemoveKnowledgeDocument:
        return RemoveKnowledgeDocument(self.knowledge_repo)

    def create_get_knowledge(self) -> GetKnowledgeDocument:
        return GetKnowledgeDocument(self.knowledge_repo)

    def create_conversation_orchestrator(self) -> ConversationOrchestrator:
        return ConversationOrchestrator(
            processor=self.create_message_processor(),
            get_settings=self.create_get_guild_settings(),
            quota_checker=self.create_quota_checker(),
            usage_recorder=RecordTokenUsage(self.usage_repo),
            knowledge_search=self.create_search_knowledge(),
            moderation=EvaluateIncomingMessage(self.content_moderator, self.moderation_repo),
        )

    def create_onboarding_service(self) -> GuildOnboardingService:
        return GuildOnboardingService(
            get_settings=self.create_get_guild_settings(),
            update_settings=self.create_update_guild_settings(),
            add_knowledge=self.create_add_knowledge(),
            default_prompt=self.config.CHAT_SYSTEM_PROMPT,
        )
