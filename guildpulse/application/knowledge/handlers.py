"""Knowledge base use cases."""

from __future__ import annotations

import logging

from guildpulse.application.ports.knowledge_repository_port import IKnowledgeRepository
from guildpulse.domain.knowledge.models import KnowledgeDocument, KnowledgeSearchResult
from guildpulse.infrastructure.knowledge.chunker import TextChunker


class AddKnowledgeDocument:
    def __init__(self, repo: IKnowledgeRepository, chunker: TextChunker | None = None) -> None:
        self.repo = repo
        self.chunker = chunker or TextChunker()
        self.logger = logging.getLogger(__name__)

    def execute(self, document: KnowledgeDocument) -> KnowledgeDocument:
        document.validate()
        document.chunks = self.chunker.chunk_document(document)
        saved = self.repo.add_document(document)
        self.logger.info(
            "Added knowledge document '%s' with %s chunks for guild %s",
            saved.title,
            len(saved.chunks),
            saved.guild_id,
        )
        return saved


class SearchGuildKnowledge:
    def __init__(self, repo: IKnowledgeRepository) -> None:
        self.repo = repo

    def execute(self, guild_id: int, query: str, limit: int = 5) -> list[KnowledgeSearchResult]:
        cleaned = query.strip()
        if len(cleaned) < 3:
            return []
        return self.repo.search(guild_id, cleaned, limit=limit)

    def build_context(self, guild_id: int, query: str, limit: int = 3) -> str:
        results = self.execute(guild_id, query, limit=limit)
        if not results:
            return ""
        lines = ["Relevant guild knowledge:"]
        for result in results:
            title = result.chunk.document_title or f"Doc {result.chunk.document_id}"
            lines.append(f"- [{title}] {result.chunk.content}")
        return "\n".join(lines)


class ListKnowledgeDocuments:
    def __init__(self, repo: IKnowledgeRepository) -> None:
        self.repo = repo

    def execute(self, guild_id: int) -> list[KnowledgeDocument]:
        return self.repo.list_documents(guild_id)


class RemoveKnowledgeDocument:
    def __init__(self, repo: IKnowledgeRepository) -> None:
        self.repo = repo

    def execute(self, guild_id: int, document_id: int) -> bool:
        return self.repo.delete_document(guild_id, document_id)


class GetKnowledgeDocument:
    def __init__(self, repo: IKnowledgeRepository) -> None:
        self.repo = repo

    def execute(self, guild_id: int, document_id: int) -> KnowledgeDocument | None:
        return self.repo.get_document(guild_id, document_id)
