"""Tests for application ports."""


class TestChannelRepositoryPort:
    def test_channel_repository_protocol(self):
        """Test that ChannelRepositoryPort is properly defined."""
        from guildpulse.application.ports.channel_repository_port import IChannelRepositoryPort

        # Should be a Protocol
        assert hasattr(IChannelRepositoryPort, "save")
        assert hasattr(IChannelRepositoryPort, "get")
        assert hasattr(IChannelRepositoryPort, "get_or_create")


class TestAIServicePort:
    def test_ai_service_protocol(self):
        """Test that AIServicePort is properly defined."""
        from guildpulse.application.ports.ai_service_port import IAIServicePort

        # Should be a Protocol
        assert hasattr(IAIServicePort, "generate_reply")


class TestConfigPort:
    def test_config_port_protocol(self):
        """Test that ConfigPort is properly defined."""
        from guildpulse.application.ports.config_port import IConfigPort

        # Should be a Protocol
        assert hasattr(IConfigPort, "get_discord_token")
        assert hasattr(IConfigPort, "get_openai_api_key")
