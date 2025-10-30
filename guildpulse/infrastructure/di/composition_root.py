"""Dependency injection composition root."""

import os

from guildpulse.application.messaging.handlers import ClearChannelHistory, ProcessUserTurn
from guildpulse.application.ports.ai_service_port import IAIServicePort
from guildpulse.application.ports.channel_repository_port import IChannelRepositoryPort
from guildpulse.config import Settings
from guildpulse.infrastructure.ai.openai.adapter import OpenAIServiceAdapter
from guildpulse.infrastructure.ai.openai.client import OpenAIClient
from guildpulse.infrastructure.persistence.sqlite.repository import SQLiteChannelRepository


class CompositionRoot:
    """Dependency injection composition root for the application."""

    def __init__(self, config: Settings, db_path: str | None = None) -> None:
        """Initialize composition root with configuration."""
        self.config = config
        self.db_path = db_path or os.environ.get("DATABASE_PATH", "data/channels.db")
        self._repo: IChannelRepositoryPort | None = None
        self._ai_service: IAIServicePort | None = None

    @property
    def repo(self) -> IChannelRepositoryPort:
        """Get or create channel repository."""
        if self._repo is None:
            self._repo = SQLiteChannelRepository(db_path=self.db_path)  # type: ignore[assignment]
        return self._repo  # type: ignore[return-value]

    @property
    def ai_service(self) -> IAIServicePort:
        """Get or create AI service adapter."""
        if self._ai_service is None:
            client = OpenAIClient(
                api_key=self.config.OPENAI_API_KEY,
                base_url=self.config.OPENAI_BASE_URL,
                model=self.config.OPENAI_MODEL,
                max_tokens=self.config.OPENAI_MAX_TOKENS,
                temperature=self.config.OPENAI_TEMPERATURE,
            )
            self._ai_service = OpenAIServiceAdapter(client)
        return self._ai_service

    def create_message_processor(self) -> ProcessUserTurn:
        """Create message processing use case."""
        return ProcessUserTurn(self.repo, self.ai_service)

    def create_clear_history_use_case(self) -> ClearChannelHistory:
        """Create clear history use case."""
        return ClearChannelHistory(self.repo)
