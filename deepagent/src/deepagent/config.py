"""Central configuration for the DeepSeek research agent."""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from dotenv import load_dotenv

# Ensure deepagent and deepagent/src are discoverable on sys.path
_AGENT_ROOT = Path(__file__).resolve().parents[2]
if str(_AGENT_ROOT) not in sys.path:
    sys.path.insert(0, str(_AGENT_ROOT))
if str(_AGENT_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_AGENT_ROOT / "src"))

# Search for .env in current directory, deepagent root, and parent directory
for _env_path in (
    Path.cwd() / ".env",
    _AGENT_ROOT / ".env",
    _AGENT_ROOT.parent / ".env",
):
    if _env_path.is_file():
        load_dotenv(_env_path)
        break


@dataclass
class Settings:
    deepseek_api_key: str = field(default_factory=lambda: os.getenv("DEEPSEEK_API_KEY", ""))
    deepseek_base_url: str = field(default_factory=lambda: os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"))
    deepseek_model: str = field(default_factory=lambda: os.getenv("DEEPSEEK_MODEL", "deepseek-chat"))
    deepseek_temperature: float = field(
        default_factory=lambda: float(os.getenv("DEEPSEEK_TEMPERATURE", "0.2"))
    )
    deepseek_max_tokens: int = field(
        default_factory=lambda: int(os.getenv("DEEPSEEK_MAX_TOKENS", "4096"))
    )
    tavily_api_key: str = field(default_factory=lambda: os.getenv("TAVILY_API_KEY", ""))
    tavily_max_results: int = field(
        default_factory=lambda: int(os.getenv("TAVILY_MAX_RESULTS", "5"))
    )
    workspace_root: str = field(
        default_factory=lambda: os.getenv("DEEPAGENT_WORKSPACE_ROOT", os.getcwd())
    )
    allow_report_writes: bool = field(
        default_factory=lambda: _env_bool("DEEPAGENT_ALLOW_REPORT_WRITES", True)
    )
    enable_dynamic_tools: bool = field(
        default_factory=lambda: _env_bool("DEEPAGENT_ENABLE_DYNAMIC_TOOLS", False)
    )
    require_tool_approval: bool = field(
        default_factory=lambda: _env_bool("DEEPAGENT_REQUIRE_TOOL_APPROVAL", True)
    )
    max_tool_execution_seconds: int = field(
        default_factory=lambda: int(os.getenv("DEEPAGENT_MAX_TOOL_SECONDS", "30"))
    )

    @property
    def workspace_path(self) -> Path:
        return Path(self.workspace_root).expanduser().resolve()

    def validate(self, require_keys: bool = True) -> None:
        if require_keys and not self.deepseek_api_key:
            raise RuntimeError(
                "DEEPSEEK_API_KEY is not set. "
                "Create one at https://platform.deepseek.com and export it "
                "or put it in a .env file (see .env.example)."
            )
        if self.max_tool_execution_seconds < 1:
            raise ValueError("DEEPAGENT_MAX_TOOL_SECONDS must be at least 1")
        if not self.workspace_path.exists() or not self.workspace_path.is_dir():
            raise ValueError(f"DEEPAGENT_WORKSPACE_ROOT is not a directory: {self.workspace_root}")
        if self.enable_dynamic_tools and not self.require_tool_approval:
            raise ValueError(
                "Generated dynamic tools require approval: set DEEPAGENT_REQUIRE_TOOL_APPROVAL=true"
            )


def get_settings() -> Settings:
    return Settings()


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}
