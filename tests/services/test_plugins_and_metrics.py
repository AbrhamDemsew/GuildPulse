"""Tests for plugin registry and metrics."""

from guildpulse.ops.metrics_collector import MetricsCollector
from guildpulse.plugins.registry import PluginRegistry, StatsPlugin, WelcomePlugin


class TestMetricsCollector:
    def test_record_message_and_snapshot(self):
        metrics = MetricsCollector()
        metrics.record_message(1, blocked=False, tokens=20)
        metrics.record_message(1, blocked=True)
        snapshot = metrics.snapshot()
        assert snapshot.messages_processed == 1
        assert snapshot.messages_blocked == 1
        assert snapshot.tokens_generated == 20


class TestPluginRegistry:
    def test_register_enable_dispatch(self):
        registry = PluginRegistry()
        registry.register(WelcomePlugin())
        registry.enable("welcome", 42)
        response = registry.dispatch("welcome", 42, 7, "")
        assert "onboarding" in response.lower()
        assert "welcome" in registry.enabled_for_guild(42)

    def test_stats_plugin_without_provider(self):
        plugin = StatsPlugin()
        assert "no metrics provider" in plugin.handle(1, 2, "")
