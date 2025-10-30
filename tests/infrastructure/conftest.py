"""Test configuration for infrastructure tests."""

import os

import pytest


@pytest.fixture(scope="session")
def infrastructure_environment():
    """Set up infrastructure-specific test environment."""

    env_vars = {
        "CHAT_SYSTEM_PROMPT": "You are GuildPulse, a helpful Discord community assistant. Reply concisely and clearly. Match the user's language when possible.",
    }

    os.environ.update(env_vars)
    yield
    for key in env_vars:
        os.environ.pop(key, None)
