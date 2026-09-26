"""Workspace-scoped file tools for local environment research."""

from __future__ import annotations

from pathlib import Path
from langchain_core.tools import tool


def _resolve_path(path: str, workspace_root: Path) -> Path:
    candidate = Path(path).expanduser()
    if not candidate.is_absolute():
        candidate = workspace_root / candidate
    resolved = candidate.resolve()
    try:
        resolved.relative_to(workspace_root)
    except ValueError as exc:
        raise ValueError(f"Path is outside the configured workspace: {path}") from exc
    return resolved


def make_file_tools(settings) -> list:
    """Create file tools constrained to the configured workspace root."""
    workspace_root = settings.workspace_path

    @tool("read_file")
    def read_file(path: str) -> str:
        """Read a UTF-8 text file inside the configured workspace."""
        try:
            resolved = _resolve_path(path, workspace_root)
        except ValueError as exc:
            return f"Permission denied: {exc}"
        if not resolved.exists():
            return f"File not found: {path}"
        if not resolved.is_file():
            return f"Not a file: {path}"
        try:
            return resolved.read_text(encoding="utf-8")[:20_000]
        except Exception as exc:
            return f"Error reading file: {exc}"

    tools = [read_file]
    if getattr(settings, "allow_report_writes", True):

        @tool("write_report")
        def write_report(args: str) -> str:
            """Save a markdown report inside the configured workspace."""
            if "|||" not in args:
                return "Usage: 'PATH|||MARKDOWN', e.g. 'report.md|||# Findings...'"
            raw_path, markdown = args.split("|||", 1)
            try:
                resolved = _resolve_path(raw_path.strip(), workspace_root)
            except ValueError as exc:
                return f"Permission denied: {exc}"
            resolved.parent.mkdir(parents=True, exist_ok=True)
            resolved.write_text(markdown, encoding="utf-8")
            return f"Report written to {resolved}"

        tools.append(write_report)
    return tools
