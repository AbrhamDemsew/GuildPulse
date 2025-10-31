"""Pydantic schemas for HTTP API."""

from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = "ok"
    service: str = "guildpulse"
    version: str = "1.1.0"
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class GuildSettingsResponse(BaseModel):
    guild_id: int
    system_prompt: str
    model_name: str
    max_history: int
    max_tokens: int
    temperature: float
    moderation_enabled: bool
    knowledge_enabled: bool
    daily_message_quota: int
    daily_token_quota: int
    allowed_channel_ids: list[int]
    admin_role_ids: list[int]


class UpdatePromptRequest(BaseModel):
    system_prompt: str = Field(min_length=1, max_length=4000)


class UpdateModelRequest(BaseModel):
    model_name: str
    max_tokens: int = Field(ge=1, le=8192)
    temperature: float = Field(ge=0.0, le=2.0)


class UpdateQuotaRequest(BaseModel):
    daily_message_quota: int = Field(ge=1)
    daily_token_quota: int = Field(ge=100)


class UpdateChannelsRequest(BaseModel):
    allowed_channel_ids: list[int]


class UsageReportResponse(BaseModel):
    guild_id: int
    recorded_on: date
    message_count: int
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    average_tokens_per_message: float


class QuotaStatusResponse(BaseModel):
    guild_id: int
    recorded_on: date
    messages_used: int
    messages_limit: int
    messages_remaining: int
    tokens_used: int
    tokens_limit: int
    tokens_remaining: int
    is_exhausted: bool


class ModerationEventResponse(BaseModel):
    record_id: int | None
    guild_id: int
    user_id: int
    channel_id: int
    action: str
    reason: str
    content_preview: str


class KnowledgeDocumentRequest(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    content: str = Field(min_length=20, max_length=50000)
    source: str = "manual"
    created_by: int = 0


class KnowledgeDocumentResponse(BaseModel):
    document_id: int
    guild_id: int
    title: str
    source: str
    content: str
    created_by: int
    chunk_count: int


class KnowledgeSearchRequest(BaseModel):
    query: str = Field(min_length=3, max_length=500)
    limit: int = Field(default=5, ge=1, le=20)


class KnowledgeSearchHit(BaseModel):
    document_id: int
    document_title: str
    chunk_index: int
    content: str
    score: float
