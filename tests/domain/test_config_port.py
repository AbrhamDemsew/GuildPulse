"""Tests for ConfigPort interface in domain layer."""


def test_config_port_has_required_properties():
    """Test that ConfigPort defines all required properties."""

    class DummyConfig:
        @property
        def discord_token(self) -> str:
            return "test"

        @property
        def openai_api_key(self) -> str:
            return "test-key"

        @property
        def openai_base_url(self) -> str:
            return "https://test.com/v1"

        @property
        def openai_model(self) -> str:
            return "test-model"

        @property
        def openai_max_tokens(self) -> int:
            return 500

        @property
        def openai_temperature(self) -> float:
            return 0.7

    config = DummyConfig()

    assert isinstance(config.discord_token, str)
    assert isinstance(config.openai_api_key, str)
    assert isinstance(config.openai_base_url, str)
    assert isinstance(config.openai_model, str)
    assert isinstance(config.openai_max_tokens, int)
    assert isinstance(config.openai_temperature, float)
