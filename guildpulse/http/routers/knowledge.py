"""Knowledge base routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from guildpulse.domain.knowledge.models import KnowledgeDocument
from guildpulse.http.deps import get_root, verify_api_key
from guildpulse.http.schemas import (
    KnowledgeDocumentRequest,
    KnowledgeDocumentResponse,
    KnowledgeSearchHit,
    KnowledgeSearchRequest,
)
from guildpulse.infrastructure.di.composition_root import CompositionRoot

router = APIRouter(dependencies=[Depends(verify_api_key)])


def _doc_response(document: KnowledgeDocument) -> KnowledgeDocumentResponse:
    return KnowledgeDocumentResponse(
        document_id=document.document_id or 0,
        guild_id=document.guild_id,
        title=document.title,
        source=document.source,
        content=document.content,
        created_by=document.created_by,
        chunk_count=len(document.chunks),
    )


@router.get("/{guild_id}", response_model=list[KnowledgeDocumentResponse])
def list_documents(
    guild_id: int,
    root: CompositionRoot = Depends(get_root),
) -> list[KnowledgeDocumentResponse]:
    docs = root.create_list_knowledge().execute(guild_id)
    return [_doc_response(doc) for doc in docs]


@router.post("/{guild_id}", response_model=KnowledgeDocumentResponse)
def add_document(
    guild_id: int,
    payload: KnowledgeDocumentRequest,
    root: CompositionRoot = Depends(get_root),
) -> KnowledgeDocumentResponse:
    document = KnowledgeDocument(
        guild_id=guild_id,
        title=payload.title,
        content=payload.content,
        source=payload.source,
        created_by=payload.created_by,
    )
    saved = root.create_add_knowledge().execute(document)
    return _doc_response(saved)


@router.get("/{guild_id}/{document_id}", response_model=KnowledgeDocumentResponse)
def get_document(
    guild_id: int,
    document_id: int,
    root: CompositionRoot = Depends(get_root),
) -> KnowledgeDocumentResponse:
    document = root.create_get_knowledge().execute(guild_id, document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return _doc_response(document)


@router.delete("/{guild_id}/{document_id}")
def delete_document(
    guild_id: int,
    document_id: int,
    root: CompositionRoot = Depends(get_root),
) -> dict[str, bool]:
    deleted = root.create_remove_knowledge().execute(guild_id, document_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"deleted": True}


@router.post("/{guild_id}/search", response_model=list[KnowledgeSearchHit])
def search_documents(
    guild_id: int,
    payload: KnowledgeSearchRequest,
    root: CompositionRoot = Depends(get_root),
) -> list[KnowledgeSearchHit]:
    hits = root.create_search_knowledge().execute(guild_id, payload.query, payload.limit)
    return [
        KnowledgeSearchHit(
            document_id=hit.chunk.document_id,
            document_title=hit.chunk.document_title,
            chunk_index=hit.chunk.chunk_index,
            content=hit.chunk.content,
            score=hit.score,
        )
        for hit in hits
    ]
