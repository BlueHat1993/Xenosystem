"""Example plugin — shows how to add a custom tool.

To enable: add "plugins.example_plugin" to ENABLED in plugins/registry.py.
"""

from __future__ import annotations

from langchain_core.tools import tool


def register() -> list:
    @tool("word_count")
    def word_count(text: str) -> str:
        """Count words in a draft report. Input: markdown text."""
        return f"{len(text.split())} words"

    return [word_count]
