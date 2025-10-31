"""Tests for conversation orchestrator and onboarding."""

from __future__ import annotations

import os
import tempfile

import pytest

from guildpulse.domain.shared.completion_result import CompletionResult
from guildpulse.infrastructure.persistence.sqlite.database import Database
from guildpulse.services.conversation_orchestrator import ConversationOrchestrator, ConversationRequest
from guildpulse.config import Settings
from guildpulse.infrastructure.di.composition_root import CompositionRoot
from unittest.mock import Mock


@pytest.fixture
def root():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as handle:
        path = handle.name
    settings = Settings(OPENAI_API_KEY="test-key")
    composition = CompositionRoot(settings, db_path=path)
    ai = composition.ai_service
    ai.generate_reply = Mock(
        return_value=CompletionResult(content="Hello there", prompt_tokens=5, completion_tokens=3)
    )
    yield composition
    os.unlink(path)


class TestConversationOrchestrator:
    def test_handles_valid_message(self, root):
        orchestrator = root.create_conversation_orchestrator()
        result = orchestrator.handle(
            ConversationRequest(
                guild_id=10,
                channel_id=20,
                user_id=30,
                content="How do I get help?",
            )
        )
        assert result.reply == "Hello there"
        assert not result.blocked

    def test_blocks_moderated_content(self, root):
        orchestrator = root.create_conversation_orchestrator()
        result = orchestrator.handle(
            ConversationRequest(
                guild_id=10,
                channel_id=20,
                user_id=30,
                content="please kys",
            )
        )
        assert result.blocked


class TestOnboardingService:
    def test_initialize_guild(self, root):
        service = root.create_onboarding_service()
        plan = service.initialize_guild(55, owner_id=999)
        assert plan.guild_id == 55
        assert len(plan.steps_completed) >= 2
        docs = root.create_list_knowledge().execute(55)
        assert len(docs) >= 2
