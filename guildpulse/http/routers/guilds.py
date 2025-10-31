"""Guild configuration routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from guildpulse.http.deps import get_root, get_settings, verify_api_key
from guildpulse.http.schemas import (
    GuildSettingsResponse,
    UpdateChannelsRequest,
    UpdateModelRequest,
    UpdatePromptRequest,
    UpdateQuotaRequest,
)
from guildpulse.infrastructure.di.composition_root import CompositionRoot

router = APIRouter(dependencies=[Depends(verify_api_key)])


def _to_response(settings) -> GuildSettingsResponse:
    return GuildSettingsResponse(
        guild_id=settings.id,
        system_prompt=settings.system_prompt,
        model_name=settings.model_name,
        max_history=settings.max_history,
        max_tokens=settings.max_tokens,
        temperature=settings.temperature,
        moderation_enabled=settings.moderation_enabled,
        knowledge_enabled=settings.knowledge_enabled,
        daily_message_quota=settings.daily_message_quota,
        daily_token_quota=settings.daily_token_quota,
        allowed_channel_ids=settings.allowed_channel_ids,
        admin_role_ids=settings.admin_role_ids,
    )


@router.get("", response_model=list[int])
def list_guilds(root: CompositionRoot = Depends(get_root)) -> list[int]:
    return root.create_list_guilds().execute()


@router.get("/{guild_id}", response_model=GuildSettingsResponse)
def get_guild_settings(guild_id: int, root: CompositionRoot = Depends(get_root)) -> GuildSettingsResponse:
    settings = root.create_get_guild_settings().execute(guild_id)
    return _to_response(settings)


@router.put("/{guild_id}/prompt", response_model=GuildSettingsResponse)
def update_prompt(
    guild_id: int,
    payload: UpdatePromptRequest,
    root: CompositionRoot = Depends(get_root),
    settings=Depends(get_settings),
) -> GuildSettingsResponse:
    updated = root.create_update_guild_settings().update_prompt(
        guild_id, payload.system_prompt, settings.CHAT_SYSTEM_PROMPT
    )
    return _to_response(updated)


@router.put("/{guild_id}/model", response_model=GuildSettingsResponse)
def update_model(
    guild_id: int,
    payload: UpdateModelRequest,
    root: CompositionRoot = Depends(get_root),
    settings=Depends(get_settings),
) -> GuildSettingsResponse:
    updated = root.create_update_guild_settings().update_model(
        guild_id,
        payload.model_name,
        payload.max_tokens,
        payload.temperature,
        settings.CHAT_SYSTEM_PROMPT,
    )
    return _to_response(updated)


@router.put("/{guild_id}/quotas", response_model=GuildSettingsResponse)
def update_quotas(
    guild_id: int,
    payload: UpdateQuotaRequest,
    root: CompositionRoot = Depends(get_root),
    settings=Depends(get_settings),
) -> GuildSettingsResponse:
    updated = root.create_update_guild_settings().update_quotas(
        guild_id,
        payload.daily_message_quota,
        payload.daily_token_quota,
        settings.CHAT_SYSTEM_PROMPT,
    )
    return _to_response(updated)


@router.put("/{guild_id}/channels", response_model=GuildSettingsResponse)
def update_channels(
    guild_id: int,
    payload: UpdateChannelsRequest,
    root: CompositionRoot = Depends(get_root),
    settings=Depends(get_settings),
) -> GuildSettingsResponse:
    updated = root.create_update_guild_settings().update_allowed_channels(
        guild_id, payload.allowed_channel_ids, settings.CHAT_SYSTEM_PROMPT
    )
    return _to_response(updated)


@router.post("/{guild_id}/reset", response_model=GuildSettingsResponse)
def reset_guild(
    guild_id: int,
    root: CompositionRoot = Depends(get_root),
    settings=Depends(get_settings),
) -> GuildSettingsResponse:
    updated = root.create_reset_guild_settings().execute(guild_id, settings.CHAT_SYSTEM_PROMPT)
    return _to_response(updated)


@router.post("/{guild_id}/moderation/{enabled}", response_model=GuildSettingsResponse)
def toggle_moderation(
    guild_id: int,
    enabled: bool,
    root: CompositionRoot = Depends(get_root),
    settings=Depends(get_settings),
) -> GuildSettingsResponse:
    updated = root.create_update_guild_settings().toggle_moderation(
        guild_id, enabled, settings.CHAT_SYSTEM_PROMPT
    )
    return _to_response(updated)


@router.post("/{guild_id}/knowledge/{enabled}", response_model=GuildSettingsResponse)
def toggle_knowledge(
    guild_id: int,
    enabled: bool,
    root: CompositionRoot = Depends(get_root),
    settings=Depends(get_settings),
) -> GuildSettingsResponse:
    updated = root.create_update_guild_settings().toggle_knowledge(
        guild_id, enabled, settings.CHAT_SYSTEM_PROMPT
    )
    return _to_response(updated)


@router.get("/{guild_id}/history-limit")
def get_history_limit(guild_id: int, root: CompositionRoot = Depends(get_root)) -> dict[str, int]:
    settings = root.create_get_guild_settings().execute(guild_id)
    if settings.max_history < 1:
        raise HTTPException(status_code=500, detail="Invalid history configuration")
    return {"guild_id": guild_id, "max_history": settings.max_history}
