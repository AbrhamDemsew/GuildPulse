"""Knowledge base domain models."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class KnowledgeChunk:
    """Searchable chunk derived from a knowledge document."""

    document_id: int
    guild_id: int
    chunk_index: int
    content: str
    token_estimate: int = 0
    chunk_id: int | None = None
    document_title: str = ""


@dataclass
class KnowledgeDocument:
    """Guild-owned reference document for retrieval-augmented replies."""

    guild_id: int
    title: str
    content: str
    source: str = "manual"
    created_by: int = 0
    document_id: int | None = None
    chunks: list[KnowledgeChunk] = field(default_factory=list)

    def validate(self) -> None:
        if not self.title.strip():
            raise ValueError("Document title is required")
        if len(self.content.strip()) < 20:
            raise ValueError("Document content must be at least 20 characters")
        if len(self.content) > 50_000:
            raise ValueError("Document content exceeds 50,000 characters")


@dataclass(frozen=True)
class KnowledgeSearchResult:
    """Ranked chunk returned from knowledge search."""

    chunk: KnowledgeChunk
    score: float
