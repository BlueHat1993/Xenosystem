"""Stub for a local docs MCP server.

Draft placeholder — replace with a real MCP server (e.g. built with the
`mcp` Python SDK or `langchain-mcp-adapters`) that exposes project docs,
DeepSeek notes, and skill cards as resources/tools.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def list_resources() -> list[str]:
    """Return draft resource paths this server *would* expose."""
    return [
        "instructions://system_prompt",
        "skills://researcher/SKILL.md",
        "skills://deepseek-notes/SKILL.md",
    ]


if __name__ == "__main__":
    for r in list_resources():
        print(r)
