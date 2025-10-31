"""Plugin management routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from guildpulse.http.deps import get_root, verify_api_key
from guildpulse.infrastructure.di.composition_root import CompositionRoot

router = APIRouter(dependencies=[Depends(verify_api_key)])


class PluginDispatchRequest(BaseModel):
    guild_id: int
    user_id: int
    payload: str = Field(default="")


@router.get("")
def list_plugins(root: CompositionRoot = Depends(get_root)) -> list[dict[str, str]]:
    return [
        {"name": name, "description": description}
        for name, description in root.plugin_registry.list_plugins()
    ]


@router.get("/{guild_id}/enabled")
def enabled_plugins(guild_id: int, root: CompositionRoot = Depends(get_root)) -> dict[str, list[str]]:
    return {"guild_id": guild_id, "enabled": root.plugin_registry.enabled_for_guild(guild_id)}


@router.post("/{name}/enable/{guild_id}")
def enable_plugin(name: str, guild_id: int, root: CompositionRoot = Depends(get_root)) -> dict[str, str]:
    try:
        root.plugin_registry.enable(name, guild_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"status": "enabled", "plugin": name, "guild_id": str(guild_id)}


@router.post("/{name}/disable/{guild_id}")
def disable_plugin(name: str, guild_id: int, root: CompositionRoot = Depends(get_root)) -> dict[str, str]:
    try:
        root.plugin_registry.disable(name, guild_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"status": "disabled", "plugin": name, "guild_id": str(guild_id)}


@router.post("/{name}/dispatch")
def dispatch_plugin(
    name: str,
    payload: PluginDispatchRequest,
    root: CompositionRoot = Depends(get_root),
) -> dict[str, str]:
    try:
        response = root.plugin_registry.dispatch(
            name,
            payload.guild_id,
            payload.user_id,
            payload.payload,
        )
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"response": response}
