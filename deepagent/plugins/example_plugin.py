"""Example plugin — shows how to add a custom tool.

To enable: add "plugins.example_plugin" to ENABLED in plugins/registry.py.
"""

from __future__ import annotations


def register() -> list:
    try:
        from langchain_core.tools import tool
    except ImportError:
        return []

    @tool("word_count")
    def word_count(text: str) -> str:
        """Count words in a draft report. Input: markdown text."""
        n = len(text.split())
        return f"{n} words"

    return [word_count]
