"""Usage analytics routes."""

from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, Query

from guildpulse.http.deps import get_root, verify_api_key
from guildpulse.http.schemas import QuotaStatusResponse, UsageReportResponse
from guildpulse.infrastructure.di.composition_root import CompositionRoot

router = APIRouter(dependencies=[Depends(verify_api_key)])


@router.get("/{guild_id}/daily", response_model=UsageReportResponse)
def guild_daily_usage(
    guild_id: int,
    day: date | None = Query(default=None),
    root: CompositionRoot = Depends(get_root),
) -> UsageReportResponse:
    totals = root.create_usage_report().execute(guild_id, day)
    return UsageReportResponse(
        guild_id=totals.guild_id,
        recorded_on=totals.recorded_on,
        message_count=totals.message_count,
        prompt_tokens=totals.prompt_tokens,
        completion_tokens=totals.completion_tokens,
        total_tokens=totals.total_tokens,
        average_tokens_per_message=totals.average_tokens_per_message,
    )


@router.get("/{guild_id}/users/{user_id}", response_model=UsageReportResponse)
def user_daily_usage(
    guild_id: int,
    user_id: int,
    day: date | None = Query(default=None),
    root: CompositionRoot = Depends(get_root),
) -> UsageReportResponse:
    totals = root.create_usage_report().for_user(guild_id, user_id, day)
    return UsageReportResponse(
        guild_id=totals.guild_id,
        recorded_on=totals.recorded_on,
        message_count=totals.message_count,
        prompt_tokens=totals.prompt_tokens,
        completion_tokens=totals.completion_tokens,
        total_tokens=totals.total_tokens,
        average_tokens_per_message=totals.average_tokens_per_message,
    )


@router.get("/{guild_id}/quota", response_model=QuotaStatusResponse)
def guild_quota(
    guild_id: int,
    root: CompositionRoot = Depends(get_root),
) -> QuotaStatusResponse:
    settings = root.create_get_guild_settings().execute(guild_id)
    status = root.create_quota_checker().execute(
        guild_id,
        settings.daily_message_quota,
        settings.daily_token_quota,
    )
    return QuotaStatusResponse(
        guild_id=status.guild_id,
        recorded_on=status.recorded_on,
        messages_used=status.messages_used,
        messages_limit=status.messages_limit,
        messages_remaining=status.messages_remaining,
        tokens_used=status.tokens_used,
        tokens_limit=status.tokens_limit,
        tokens_remaining=status.tokens_remaining,
        is_exhausted=status.is_exhausted,
    )
