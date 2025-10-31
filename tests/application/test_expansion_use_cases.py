"""Tests for guild, moderation, analytics, and knowledge use cases."""

from __future__ import annotations

import os
import tempfile
from datetime import date

import pytest

from guildpulse.application.analytics.handlers import CheckGuildQuota, GetGuildUsageReport, RecordTokenUsage
from guildpulse.application.guild.handlers import GetGuildSettings, UpdateGuildSettings
from guildpulse.application.knowledge.handlers import AddKnowledgeDocument, SearchGuildKnowledge
from guildpulse.application.moderation.handlers import EvaluateIncomingMessage
from guildpulse.domain.knowledge.models import KnowledgeDocument
from guildpulse.infrastructure.knowledge.chunker import TextChunker
from guildpulse.infrastructure.moderation.content_moderator import ContentModerator
from guildpulse.infrastructure.persistence.sqlite.database import Database
from guildpulse.infrastructure.persistence.sqlite.guild_repository import SQLiteGuildSettingsRepository
from guildpulse.infrastructure.persistence.sqlite.knowledge_repository import SQLiteKnowledgeRepository
from guildpulse.infrastructure.persistence.sqlite.moderation_repository import SQLiteModerationLogRepository
from guildpulse.infrastructure.persistence.sqlite.usage_repository import SQLiteUsageRepository


@pytest.fixture
def temp_db():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as handle:
        path = handle.name
    db = Database(path)
    yield db
    os.unlink(path)


@pytest.fixture
def guild_repo(temp_db):
    return SQLiteGuildSettingsRepository(temp_db)


@pytest.fixture
def usage_repo(temp_db):
    return SQLiteUsageRepository(temp_db)


@pytest.fixture
def moderation_repo(temp_db):
    return SQLiteModerationLogRepository(temp_db)


@pytest.fixture
def knowledge_repo(temp_db):
    return SQLiteKnowledgeRepository(temp_db)


class TestGuildUseCases:
    def test_get_or_create_default(self, guild_repo):
        use_case = GetGuildSettings(guild_repo, "Default prompt")
        settings = use_case.execute(100)
        assert settings.id == 100
        assert settings.system_prompt == "Default prompt"

    def test_update_prompt(self, guild_repo):
        updater = UpdateGuildSettings(guild_repo)
        updated = updater.update_prompt(100, "Custom prompt", "Default prompt")
        assert updated.system_prompt == "Custom prompt"


class TestModerationUseCase:
    def test_blocks_policy_violation(self, usage_repo, moderation_repo):
        moderator = ContentModerator(usage_repo)
        use_case = EvaluateIncomingMessage(moderator, moderation_repo)
        decision = use_case.execute(
            guild_id=1,
            user_id=2,
            channel_id=3,
            content="please kys now",
        )
        assert decision.blocked
        events = moderation_repo.list_for_guild(1)
        assert len(events) == 1


class TestAnalyticsUseCases:
    def test_record_and_report(self, usage_repo):
        recorder = RecordTokenUsage(usage_repo)
        reporter = GetGuildUsageReport(usage_repo)
        recorder.execute(1, 2, 3, prompt_tokens=10, completion_tokens=5)
        totals = reporter.execute(1, date.today())
        assert totals.message_count == 1
        assert totals.total_tokens == 15


class TestQuotaUseCase:
    def test_quota_status(self, guild_repo, usage_repo):
        settings = guild_repo.get_or_create_default(1, "prompt")
        recorder = RecordTokenUsage(usage_repo)
        recorder.execute(1, 2, 3, 10, 5)
        checker = CheckGuildQuota(usage_repo)
        status = checker.execute(1, settings.daily_message_quota, settings.daily_token_quota)
        assert status.messages_used == 1
        assert not status.is_exhausted


class TestKnowledgeUseCases:
    def test_add_and_search(self, knowledge_repo):
        add = AddKnowledgeDocument(knowledge_repo, TextChunker(chunk_size=100, overlap=20))
        search = SearchGuildKnowledge(knowledge_repo)
        document = KnowledgeDocument(
            guild_id=1,
            title="Onboarding",
            content="Welcome to the guild. Be respectful. Use the support channel for help.",
        )
        saved = add.execute(document)
        assert saved.document_id is not None
        hits = search.execute(1, "support channel")
        assert hits
        context = search.build_context(1, "support channel")
        assert "Relevant guild knowledge" in context
