"""Test configuration for infrastructure tests."""

import os

import pytest


@pytest.fixture(scope="session")
def infrastructure_environment():
    """Set up infrastructure-specific test environment."""

    env_vars = {
        "CHAT_SYSTEM_PROMPT": "Tu es un bot Discord amical, intelligent et utile. Réponds de manière concise, claire et bienveillante. Utilise le français si la conversation est en français.",
    }

    os.environ.update(env_vars)
    yield
    for key in env_vars:
        os.environ.pop(key, None)
