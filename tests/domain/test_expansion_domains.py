"""Tests for expanded GuildPulse domain modules."""

import pytest

from guildpulse.domain.analytics.usage import QuotaStatus, UsageTotals
from guildpulse.domain.guild.aggregate import GuildSettings
from guildpulse.domain.knowledge.models import KnowledgeDocument
from guildpulse.domain.moderation.models import ModerationAction, ModerationDecision


class TestGuildSettings:
    def test_default_for_guild(self):
        settings = GuildSettings.default_for(42, "Default prompt")
        assert settings.id == 42
        assert settings.system_prompt == "Default prompt"

    def test_update_prompt_validation(self):
        settings = GuildSettings(id=1)
        settings.update_prompt("New prompt")
        assert settings.system_prompt == "New prompt"
        with pytest.raises(ValueError):
            settings.update_prompt("")

    def test_update_model_validation(self):
        settings = GuildSettings(id=1)
        settings.update_model("gpt-4o-mini", 500, 0.5)
        assert settings.model_name == "gpt-4o-mini"
        with pytest.raises(ValueError):
            settings.update_model("", 500, 0.5)

    def test_channel_allowlist(self):
        settings = GuildSettings(id=1, allowed_channel_ids=[10, 20])
        assert settings.is_channel_allowed(10)
        assert not settings.is_channel_allowed(99)

    def test_set_quotas(self):
        settings = GuildSettings(id=1)
        settings.set_quotas(100, 5000)
        assert settings.daily_message_quota == 100
        assert settings.daily_token_quota == 5000


class TestModerationDecision:
    def test_allow(self):
        decision = ModerationDecision.allow()
        assert not decision.blocked

    def test_block(self):
        decision = ModerationDecision.block("bad content")
        assert decision.blocked
        assert decision.action == ModerationAction.BLOCK


class TestUsageTotals:
    def test_average_tokens(self):
        totals = UsageTotals(
            guild_id=1,
            recorded_on=__import__("datetime").date.today(),
            message_count=4,
            prompt_tokens=40,
            completion_tokens=20,
            total_tokens=60,
        )
        assert totals.average_tokens_per_message == 15.0


class TestQuotaStatus:
    def test_remaining_and_exhausted(self):
        status = QuotaStatus(
            guild_id=1,
            recorded_on=__import__("datetime").date.today(),
            messages_used=10,
            messages_limit=100,
            tokens_used=1000,
            tokens_limit=5000,
        )
        assert status.messages_remaining == 90
        assert not status.is_exhausted


class TestKnowledgeDocument:
    def test_validate_success(self):
        doc = KnowledgeDocument(guild_id=1, title="Rules", content="A" * 25)
        doc.validate()

    def test_validate_rejects_short_content(self):
        doc = KnowledgeDocument(guild_id=1, title="Rules", content="short")
        with pytest.raises(ValueError):
            doc.validate()
