"""Guild onboarding workflows."""

from __future__ import annotations

from dataclasses import dataclass

from guildpulse.application.guild.handlers import GetGuildSettings, UpdateGuildSettings
from guildpulse.domain.guild.aggregate import GuildSettings
from guildpulse.domain.knowledge.models import KnowledgeDocument
from guildpulse.application.knowledge.handlers import AddKnowledgeDocument


@dataclass(frozen=True)
class OnboardingPlan:
    guild_id: int
    steps_completed: list[str]
    recommended_documents: list[str]


class GuildOnboardingService:
    """Bootstrap new guilds with defaults and starter knowledge."""

    STARTER_DOCS: tuple[tuple[str, str], ...] = (
        (
            "Community Guidelines",
            "Be respectful. No harassment. Use support channels for help. "
            "Follow Discord Terms of Service and server-specific rules.",
        ),
        (
            "GuildPulse Usage",
            "Mention the bot or use /chat for questions. Admins can configure prompts "
            "with /config and upload FAQ entries with /kb add.",
        ),
    )

    def __init__(
        self,
        get_settings: GetGuildSettings,
        update_settings: UpdateGuildSettings,
        add_knowledge: AddKnowledgeDocument,
        default_prompt: str,
    ) -> None:
        self.get_settings = get_settings
        self.update_settings = update_settings
        self.add_knowledge = add_knowledge
        self.default_prompt = default_prompt

    def initialize_guild(self, guild_id: int, owner_id: int) -> OnboardingPlan:
        settings = self.get_settings.execute(guild_id)
        completed: list[str] = ["settings_loaded"]

        if settings.system_prompt == self.default_prompt:
            customized = (
                f"{self.default_prompt} You are assisting guild {guild_id}. "
                "Prioritize accurate, community-safe answers."
            )
            self.update_settings.update_prompt(guild_id, customized, self.default_prompt)
            completed.append("prompt_customized")

        for title, content in self.STARTER_DOCS:
            document = KnowledgeDocument(
                guild_id=guild_id,
                title=title,
                content=content,
                source="onboarding",
                created_by=owner_id,
            )
            self.add_knowledge.execute(document)
            completed.append(f"doc:{title}")

        return OnboardingPlan(
            guild_id=guild_id,
            steps_completed=completed,
            recommended_documents=[title for title, _ in self.STARTER_DOCS],
        )

    def readiness_checklist(self, settings: GuildSettings) -> dict[str, bool]:
        return {
            "custom_prompt": settings.system_prompt != self.default_prompt,
            "moderation_enabled": settings.moderation_enabled,
            "knowledge_enabled": settings.knowledge_enabled,
            "quotas_configured": settings.daily_message_quota > 0,
            "history_limit_set": settings.max_history >= 20,
        }
