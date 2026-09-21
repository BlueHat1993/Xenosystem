"""DeepAgent package — DeepSeek-powered research agent (draft)."""

from deepagent.config import Settings, get_settings
from deepagent.agent import build_agent, run_research

__all__ = ["Settings", "get_settings", "build_agent", "run_research"]
__version__ = "0.1.0-draft"
