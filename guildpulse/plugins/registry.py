"""Plugin registry for optional guild command extensions."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Protocol


class GuildPlugin(Protocol):
    name: str
    description: str

    def is_enabled(self, guild_id: int) -> bool: ...

    def on_enable(self, guild_id: int) -> None: ...

    def on_disable(self, guild_id: int) -> None: ...

    def handle(self, guild_id: int, user_id: int, payload: str) -> str: ...


@dataclass
class RegisteredPlugin:
    plugin: GuildPlugin
    enabled_guilds: set[int] = field(default_factory=set)

    def enable(self, guild_id: int) -> None:
        self.enabled_guilds.add(guild_id)
        self.plugin.on_enable(guild_id)

    def disable(self, guild_id: int) -> None:
        self.enabled_guilds.discard(guild_id)
        self.plugin.on_disable(guild_id)

    def is_enabled(self, guild_id: int) -> bool:
        return guild_id in self.enabled_guilds


class PluginRegistry:
    """Central registry for guild-scoped plugins."""

    def __init__(self) -> None:
        self._plugins: dict[str, RegisteredPlugin] = {}

    def register(self, plugin: GuildPlugin) -> None:
        if plugin.name in self._plugins:
            raise ValueError(f"Plugin already registered: {plugin.name}")
        self._plugins[plugin.name] = RegisteredPlugin(plugin=plugin)

    def list_plugins(self) -> list[tuple[str, str]]:
        return [(item.plugin.name, item.plugin.description) for item in self._plugins.values()]

    def enable(self, name: str, guild_id: int) -> None:
        entry = self._get(name)
        entry.enable(guild_id)

    def disable(self, name: str, guild_id: int) -> None:
        entry = self._get(name)
        entry.disable(guild_id)

    def dispatch(self, name: str, guild_id: int, user_id: int, payload: str) -> str:
        entry = self._get(name)
        if not entry.is_enabled(guild_id):
            return f"Plugin '{name}' is not enabled for this guild."
        return entry.plugin.handle(guild_id, user_id, payload)

    def enabled_for_guild(self, guild_id: int) -> list[str]:
        return [name for name, entry in self._plugins.items() if entry.is_enabled(guild_id)]

    def _get(self, name: str) -> RegisteredPlugin:
        if name not in self._plugins:
            raise KeyError(f"Unknown plugin: {name}")
        return self._plugins[name]


@dataclass
class StatsPlugin:
    """Reports simple runtime stats for administrators."""

    name: str = "stats"
    description: str = "Show GuildPulse runtime statistics"
    metrics_provider: Callable[[], str] | None = None

    def is_enabled(self, guild_id: int) -> bool:
        return True

    def on_enable(self, guild_id: int) -> None:
        return None

    def on_disable(self, guild_id: int) -> None:
        return None

    def handle(self, guild_id: int, user_id: int, payload: str) -> str:
        if self.metrics_provider:
            return self.metrics_provider()
        return f"Guild {guild_id}: no metrics provider configured."


@dataclass
class WelcomePlugin:
    """Generates welcome guidance for newly configured guilds."""

    name: str = "welcome"
    description: str = "Show onboarding steps for guild admins"
    steps: tuple[str, ...] = (
        "Set a custom system prompt with /config prompt.",
        "Add FAQ documents with /kb add.",
        "Review daily usage with /usage.",
        "Enable moderation in guild settings.",
    )

    def is_enabled(self, guild_id: int) -> bool:
        return True

    def on_enable(self, guild_id: int) -> None:
        return None

    def on_disable(self, guild_id: int) -> None:
        return None

    def handle(self, guild_id: int, user_id: int, payload: str) -> str:
        lines = [f"GuildPulse onboarding for guild {guild_id}:"]
        lines.extend(f"{index + 1}. {step}" for index, step in enumerate(self.steps))
        return "\n".join(lines)


def build_default_registry(metrics_text_provider: Callable[[], str] | None = None) -> PluginRegistry:
    registry = PluginRegistry()
    registry.register(StatsPlugin(metrics_provider=metrics_text_provider))
    registry.register(WelcomePlugin())
    return registry
