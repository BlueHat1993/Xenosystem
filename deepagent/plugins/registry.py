"""Plugin registry. Drop a module with a `register()` fn in plugins/ and list it here."""

from __future__ import annotations

# Draft: no built-in plugins enabled. Example:
# ENABLED = ["plugins.example_plugin"]
ENABLED: list[str] = []


def load_plugin_tools() -> list:
    tools: list = []
    for dotted in ENABLED:
        try:
            mod = __import__(dotted, fromlist=["register"])
            tools.extend(mod.register() or [])
        except Exception as exc:
            print(f"[plugins] failed to load {dotted}: {exc}")
    return tools
