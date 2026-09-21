"""Smoke tests — no API key or network required."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))


def test_config_defaults():
    from deepagent.config import Settings

    s = Settings(deepseek_api_key="test-key")
    assert s.deepseek_model in ("deepseek-chat", "deepseek-reasoner") or s.deepseek_model
    s.validate()  # should not raise with a key present


def test_config_requires_key():
    import pytest

    from deepagent.config import Settings

    with pytest.raises(RuntimeError, match="DEEPSEEK_API_KEY"):
        Settings(deepseek_api_key="").validate()


def test_prompts_exist():
    from deepagent.agent import INSTRUCTIONS_DIR

    for name in ("system_prompt.md", "planner.md", "researcher.md", "synthesizer.md"):
        assert (INSTRUCTIONS_DIR / name).exists(), name


def test_mcp_config_valid_json():
    import json

    cfg = ROOT / "mcp" / "mcp_config.json"
    data = json.loads(cfg.read_text(encoding="utf-8"))
    assert "mcpServers" in data


def test_skills_have_skill_md():
    skills = ROOT / "skills"
    found = list(skills.glob("*/SKILL.md"))
    assert found, "at least one skill card expected"


def test_registry_no_crash():
    from plugins.registry import load_plugin_tools

    tools = load_plugin_tools()
    assert isinstance(tools, list)
