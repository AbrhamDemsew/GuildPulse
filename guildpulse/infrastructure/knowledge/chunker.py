"""Knowledge text chunking utilities."""

from __future__ import annotations

import re

from guildpulse.domain.knowledge.models import KnowledgeChunk, KnowledgeDocument


class TextChunker:
    """Split long documents into overlapping chunks for retrieval."""

    def __init__(self, chunk_size: int = 800, overlap: int = 120) -> None:
        self.chunk_size = chunk_size
        self.overlap = overlap

    def estimate_tokens(self, text: str) -> int:
        return max(1, len(re.findall(r"\S+", text)))

    def chunk_document(self, document: KnowledgeDocument) -> list[KnowledgeChunk]:
        paragraphs = [part.strip() for part in re.split(r"\n\s*\n", document.content) if part.strip()]
        if not paragraphs:
            paragraphs = [document.content.strip()]

        chunks: list[KnowledgeChunk] = []
        buffer = ""
        index = 0
        for paragraph in paragraphs:
            candidate = f"{buffer}\n\n{paragraph}".strip() if buffer else paragraph
            if len(candidate) <= self.chunk_size:
                buffer = candidate
                continue
            if buffer:
                chunks.append(self._make_chunk(document, index, buffer))
                index += 1
                buffer = self._tail_overlap(buffer) + paragraph
            else:
                for piece in self._split_long_paragraph(paragraph):
                    chunks.append(self._make_chunk(document, index, piece))
                    index += 1
                buffer = ""

        if buffer:
            chunks.append(self._make_chunk(document, index, buffer))
        return chunks

    def _split_long_paragraph(self, paragraph: str) -> list[str]:
        words = paragraph.split()
        pieces: list[str] = []
        current: list[str] = []
        current_len = 0
        for word in words:
            extra = len(word) + (1 if current else 0)
            if current_len + extra > self.chunk_size:
                pieces.append(" ".join(current))
                current = [word]
                current_len = len(word)
            else:
                current.append(word)
                current_len += extra
        if current:
            pieces.append(" ".join(current))
        return pieces

    def _tail_overlap(self, text: str) -> str:
        if len(text) <= self.overlap:
            return text
        return text[-self.overlap :]

    def _make_chunk(self, document: KnowledgeDocument, index: int, content: str) -> KnowledgeChunk:
        return KnowledgeChunk(
            document_id=document.document_id or 0,
            guild_id=document.guild_id,
            chunk_index=index,
            content=content.strip(),
            token_estimate=self.estimate_tokens(content),
            document_title=document.title,
        )
