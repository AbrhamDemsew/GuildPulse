"""Tests for HTTP admin API."""

from __future__ import annotations

import os
import tempfile

import pytest
from fastapi.testclient import TestClient

from guildpulse.config import Settings
from guildpulse.http.app import create_app
from guildpulse.infrastructure.di.composition_root import CompositionRoot


@pytest.fixture
def api_client():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as handle:
        db_path = handle.name
    settings = Settings(
        OPENAI_API_KEY="test-key",
        HTTP_API_KEY="secret-key",
        HTTP_ENABLED=True,
    )
    root = CompositionRoot(settings, db_path=db_path)
    app = create_app(settings, root)
    client = TestClient(app)
    yield client, settings
    os.unlink(db_path)


class TestHttpApi:
    def test_health(self, api_client):
        client, _ = api_client
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"

    def test_guild_settings_requires_api_key(self, api_client):
        client, _ = api_client
        response = client.get("/api/v1/guilds/1")
        assert response.status_code == 401

    def test_guild_settings_flow(self, api_client):
        client, settings = api_client
        headers = {"X-API-Key": settings.HTTP_API_KEY}
        response = client.get("/api/v1/guilds/42", headers=headers)
        assert response.status_code == 200
        assert response.json()["guild_id"] == 42

        response = client.put(
            "/api/v1/guilds/42/prompt",
            headers=headers,
            json={"system_prompt": "Guild-specific prompt"},
        )
        assert response.status_code == 200
        assert "Guild-specific prompt" in response.json()["system_prompt"]

    def test_knowledge_api(self, api_client):
        client, settings = api_client
        headers = {"X-API-Key": settings.HTTP_API_KEY}
        response = client.post(
            "/api/v1/knowledge/7",
            headers=headers,
            json={
                "title": "FAQ",
                "content": "This guild uses GuildPulse for support and moderation guidance.",
            },
        )
        assert response.status_code == 200
        assert response.json()["chunk_count"] >= 1

        response = client.post(
            "/api/v1/knowledge/7/search",
            headers=headers,
            json={"query": "moderation guidance", "limit": 3},
        )
        assert response.status_code == 200
        assert response.json()

    def test_usage_quota_endpoint(self, api_client):
        client, settings = api_client
        headers = {"X-API-Key": settings.HTTP_API_KEY}
        response = client.get("/api/v1/analytics/42/quota", headers=headers)
        assert response.status_code == 200
        payload = response.json()
        assert payload["messages_limit"] > 0
