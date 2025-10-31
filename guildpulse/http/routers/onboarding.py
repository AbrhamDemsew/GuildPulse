"""Guild onboarding HTTP routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from guildpulse.http.deps import get_root, get_settings, verify_api_key
from guildpulse.infrastructure.di.composition_root import CompositionRoot

router = APIRouter(dependencies=[Depends(verify_api_key)])


@router.post("/{guild_id}/initialize")
def initialize_guild(
    guild_id: int,
    owner_id: int = 0,
    root: CompositionRoot = Depends(get_root),
) -> dict[str, object]:
    plan = root.create_onboarding_service().initialize_guild(guild_id, owner_id)
    return {
        "guild_id": plan.guild_id,
        "steps_completed": plan.steps_completed,
        "recommended_documents": plan.recommended_documents,
    }


@router.get("/{guild_id}/readiness")
def readiness_check(guild_id: int, root: CompositionRoot = Depends(get_root), settings=Depends(get_settings)):
    service = root.create_onboarding_service()
    guild_settings = root.create_get_guild_settings().execute(guild_id)
    checklist = service.readiness_checklist(guild_settings)
    return {"guild_id": guild_id, "checklist": checklist, "default_prompt": settings.CHAT_SYSTEM_PROMPT}
