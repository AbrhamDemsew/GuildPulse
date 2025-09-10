"""Dependency injection composition root."""

from src.application.messaging.handlers import ClearChannelHistory, ProcessUserTurn
from src.domain.repository import MessageRepository
from src.infrastructure.ai.openai.adapter import OpenAIServiceAdapter
from src.infrastructure.ai.openai.client import OpenAIClient
from src.infrastructure.config.adapter import ConfigAdapter
from src.infrastructure.persistence.memory.repository import InMemoryMessageRepository


class CompositionRoot:
    """Dependency injection composition root for the application."""
    
    def __init__(self, config: ConfigAdapter) -> None:
        """Initialize composition root with configuration."""
        self.config = config
        self._repo: MessageRepository | None = None
        self._ai_service: OpenAIServiceAdapter | None = None
    
    @property
    def repo(self) -> MessageRepository:
        """Get or create message repository."""
        if self._repo is None:
            self._repo = InMemoryMessageRepository()
        return self._repo
    
    @property
    def ai_service(self) -> OpenAIServiceAdapter:
        """Get or create AI service adapter."""
        if self._ai_service is None:
            client = OpenAIClient(
                api_key=self.config.openai_api_key,
                base_url=self.config.openai_base_url,
                model=self.config.openai_model,
                max_tokens=self.config.openai_max_tokens,
                temperature=self.config.openai_temperature,
            )
            self._ai_service = OpenAIServiceAdapter(client)
        return self._ai_service
    
    def create_message_processor(self) -> ProcessUserTurn:
        """Create message processing use case."""
        return ProcessUserTurn(self.repo, self.ai_service)
    
    def create_clear_history_use_case(self) -> ClearChannelHistory:
        """Create clear history use case."""
        return ClearChannelHistory(self.repo)