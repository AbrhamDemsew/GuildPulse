"""Repository port for guild knowledge base."""

from __future__ import annotations

from typing import Protocol

from guildpulse.domain.knowledge.models import KnowledgeDocument, KnowledgeSearchResult


class IKnowledgeRepository(Protocol):
    def add_document(self, document: KnowledgeDocument) -> KnowledgeDocument: ...

    def get_document(self, guild_id: int, document_id: int) -> KnowledgeDocument | None: ...

    def list_documents(self, guild_id: int) -> list[KnowledgeDocument]: ...

    def delete_document(self, guild_id: int, document_id: int) -> bool: ...

    def search(self, guild_id: int, query: str, limit: int = 5) -> list[KnowledgeSearchResult]: ...
