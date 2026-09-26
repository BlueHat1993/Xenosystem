"""Workspace-scoped file tools for local environment research."""

from __future__ import annotations

from pathlib import Path


try:
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
            return resolved.read_text(encoding="utf-8")[:20_000]

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

    def _legacy_settings():
        from deepagent.config import Settings

        return Settings(workspace_root=".")

    def read_file(path: str) -> str:  # type: ignore
        """Compatibility wrapper using the current directory as workspace root."""
        return make_file_tools(_legacy_settings())[0].invoke(path)

    def write_report(args: str) -> str:  # type: ignore
        """Compatibility wrapper using the current directory as workspace root."""
        tools = make_file_tools(_legacy_settings())
        return tools[1].invoke(args) if len(tools) > 1 else "Report writing is disabled."

except ImportError:  # langchain-core not installed yet
    def make_file_tools(settings) -> list:  # type: ignore
        return []

    def read_file(path: str) -> str:  # type: ignore
        return Path(path).read_text(encoding="utf-8")[:20_000]

    def write_report(args: str) -> str:  # type: ignore
        raw_path, _, markdown = args.partition("|||")
        p = Path(raw_path.strip())
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(markdown, encoding="utf-8")
        return f"Report written to {p}"
