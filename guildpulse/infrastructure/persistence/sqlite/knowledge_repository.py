"""SQLite knowledge base repository."""

from __future__ import annotations

import re

from guildpulse.domain.knowledge.models import KnowledgeChunk, KnowledgeDocument, KnowledgeSearchResult
from guildpulse.infrastructure.persistence.sqlite.database import Database


class SQLiteKnowledgeRepository:
    def __init__(self, database: Database) -> None:
        self.database = database

    def add_document(self, document: KnowledgeDocument) -> KnowledgeDocument:
        with self.database.connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO knowledge_documents (guild_id, title, source, content, created_by)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    document.guild_id,
                    document.title,
                    document.source,
                    document.content,
                    document.created_by,
                ),
            )
            document_id = int(cursor.lastrowid)
            saved_chunks: list[KnowledgeChunk] = []
            for chunk in document.chunks:
                chunk_cursor = conn.execute(
                    """
                    INSERT INTO knowledge_chunks
                    (document_id, guild_id, chunk_index, content, token_estimate)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        document_id,
                        document.guild_id,
                        chunk.chunk_index,
                        chunk.content,
                        chunk.token_estimate,
                    ),
                )
                saved_chunks.append(
                    KnowledgeChunk(
                        chunk_id=int(chunk_cursor.lastrowid),
                        document_id=document_id,
                        guild_id=document.guild_id,
                        chunk_index=chunk.chunk_index,
                        content=chunk.content,
                        token_estimate=chunk.token_estimate,
                        document_title=document.title,
                    )
                )
            conn.commit()

        document.document_id = document_id
        document.chunks = saved_chunks
        return document

    def get_document(self, guild_id: int, document_id: int) -> KnowledgeDocument | None:
        with self.database.connection() as conn:
            row = conn.execute(
                """
                SELECT id, guild_id, title, source, content, created_by
                FROM knowledge_documents
                WHERE guild_id = ? AND id = ?
                """,
                (guild_id, document_id),
            ).fetchone()
            if row is None:
                return None
            chunks = conn.execute(
                """
                SELECT id, document_id, guild_id, chunk_index, content, token_estimate
                FROM knowledge_chunks WHERE document_id = ? ORDER BY chunk_index
                """,
                (document_id,),
            ).fetchall()

        document = KnowledgeDocument(
            document_id=row["id"],
            guild_id=row["guild_id"],
            title=row["title"],
            source=row["source"],
            content=row["content"],
            created_by=row["created_by"],
        )
        document.chunks = [
            KnowledgeChunk(
                chunk_id=chunk["id"],
                document_id=chunk["document_id"],
                guild_id=chunk["guild_id"],
                chunk_index=chunk["chunk_index"],
                content=chunk["content"],
                token_estimate=chunk["token_estimate"],
                document_title=document.title,
            )
            for chunk in chunks
        ]
        return document

    def list_documents(self, guild_id: int) -> list[KnowledgeDocument]:
        with self.database.connection() as conn:
            rows = conn.execute(
                """
                SELECT id, guild_id, title, source, content, created_by
                FROM knowledge_documents WHERE guild_id = ? ORDER BY id DESC
                """,
                (guild_id,),
            ).fetchall()
        return [
            KnowledgeDocument(
                document_id=row["id"],
                guild_id=row["guild_id"],
                title=row["title"],
                source=row["source"],
                content=row["content"],
                created_by=row["created_by"],
            )
            for row in rows
        ]

    def delete_document(self, guild_id: int, document_id: int) -> bool:
        with self.database.connection() as conn:
            conn.execute("DELETE FROM knowledge_chunks WHERE document_id = ?", (document_id,))
            cursor = conn.execute(
                "DELETE FROM knowledge_documents WHERE guild_id = ? AND id = ?",
                (guild_id, document_id),
            )
            conn.commit()
            return cursor.rowcount > 0

    def search(self, guild_id: int, query: str, limit: int = 5) -> list[KnowledgeSearchResult]:
        terms = [term for term in re.findall(r"[a-zA-Z0-9]{3,}", query.lower()) if term]
        if not terms:
            return []

        with self.database.connection() as conn:
            rows = conn.execute(
                """
                SELECT c.id, c.document_id, c.guild_id, c.chunk_index, c.content,
                       c.token_estimate, d.title
                FROM knowledge_chunks c
                JOIN knowledge_documents d ON d.id = c.document_id
                WHERE c.guild_id = ?
                """,
                (guild_id,),
            ).fetchall()

        scored: list[KnowledgeSearchResult] = []
        for row in rows:
            content_lower = row["content"].lower()
            score = sum(content_lower.count(term) for term in terms)
            if score <= 0:
                continue
            chunk = KnowledgeChunk(
                chunk_id=row["id"],
                document_id=row["document_id"],
                guild_id=row["guild_id"],
                chunk_index=row["chunk_index"],
                content=row["content"],
                token_estimate=row["token_estimate"],
                document_title=row["title"],
            )
            scored.append(KnowledgeSearchResult(chunk=chunk, score=float(score)))

        scored.sort(key=lambda item: item.score, reverse=True)
        return scored[:limit]
