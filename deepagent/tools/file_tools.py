"""Minimal file tools: read a file, save the final report."""

from __future__ import annotations

from pathlib import Path


try:
    from langchain_core.tools import tool

    @tool("read_file")
    def read_file(path: str) -> str:
        """Read a local text file. Input: relative or absolute file path."""
        p = Path(path)
        if not p.exists():
            return f"File not found: {path}"
        return p.read_text(encoding="utf-8")[:20_000]

    @tool("write_report")
    def write_report(args: str) -> str:
        """Save the final research report. Input format: 'PATH|||MARKDOWN'."""
        if "|||" not in args:
            return "Usage: 'PATH|||MARKDOWN', e.g. 'report.md|||# Findings...'"
        raw_path, markdown = args.split("|||", 1)
        p = Path(raw_path.strip())
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(markdown, encoding="utf-8")
        return f"Report written to {p}"

except ImportError:  # langchain-core not installed yet
    def read_file(path: str) -> str:  # type: ignore
        return Path(path).read_text(encoding="utf-8")[:20_000]

    def write_report(args: str) -> str:  # type: ignore
        raw_path, _, markdown = args.partition("|||")
        p = Path(raw_path.strip())
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(markdown, encoding="utf-8")
        return f"Report written to {p}"
