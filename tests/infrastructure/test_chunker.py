"""Tests for knowledge chunker."""

from guildpulse.domain.knowledge.models import KnowledgeDocument
from guildpulse.infrastructure.knowledge.chunker import TextChunker


class TestTextChunker:
    def test_chunks_long_document(self):
        chunker = TextChunker(chunk_size=80, overlap=10)
        content = "\n\n".join(f"Paragraph {index} with enough words to split." for index in range(10))
        document = KnowledgeDocument(guild_id=1, title="Guide", content=content)
        chunks = chunker.chunk_document(document)
        assert len(chunks) > 1
        assert all(chunk.token_estimate > 0 for chunk in chunks)

    def test_estimate_tokens(self):
        chunker = TextChunker()
        assert chunker.estimate_tokens("one two three") >= 3
