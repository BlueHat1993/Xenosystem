"""Offline tests for generalized capability and subagent contracts."""

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))


def test_workspace_tools_reject_paths_outside_root(tmp_path):
    from deepagent.config import Settings
    from tools.file_tools import make_file_tools

    settings = Settings(deepseek_api_key="test-key", workspace_root=str(tmp_path))
    read_file = make_file_tools(settings)[0]
    outside = tmp_path.parent / "outside.txt"
    outside.write_text("secret", encoding="utf-8")

    result = read_file.invoke(str(outside))

    assert result.startswith("Permission denied:")


def test_workspace_tools_can_disable_report_writes(tmp_path):
    from deepagent.config import Settings
    from tools.file_tools import make_file_tools

    settings = Settings(
        deepseek_api_key="test-key",
        workspace_root=str(tmp_path),
        allow_report_writes=False,
    )

    assert [tool.name for tool in make_file_tools(settings)] == ["read_file"]


def test_dynamic_tools_require_approval(tmp_path):
    from deepagent.config import Settings

    settings = Settings(
        deepseek_api_key="test-key",
        workspace_root=str(tmp_path),
        enable_dynamic_tools=True,
        require_tool_approval=False,
    )

    with pytest.raises(ValueError, match="approval"):
        settings.validate()


def test_build_subagents_has_explicit_roles(tmp_path):
    from deepagent.agent import build_subagents
    from deepagent.config import Settings

    settings = Settings(deepseek_api_key="test-key", workspace_root=str(tmp_path))
    tools = [{"name": "web_search"}, {"name": "read_file"}]

    subagents = build_subagents(settings, tools)

    assert [subagent["name"] for subagent in subagents] == [
        "planner",
        "researcher",
        "verifier",
        "synthesizer",
    ]
    assert [tool["name"] for tool in subagents[1]["tools"]] == [
        "web_search",
        "read_file",
    ]


def test_build_agent_passes_research_contract(monkeypatch, tmp_path):
    import deepagents
    import deepagent.agent as agent_module
    from deepagent.config import Settings

    captured = {}

    def fake_create_deep_agent(**kwargs):
        captured.update(kwargs)
        return "compiled-agent"

    monkeypatch.setattr(deepagents, "create_deep_agent", fake_create_deep_agent)
    monkeypatch.setattr(agent_module, "build_model", lambda settings: "model")
    monkeypatch.setattr(agent_module, "build_tools", lambda settings: [])

    result = agent_module.build_agent(
        Settings(deepseek_api_key="test-key", workspace_root=str(tmp_path))
    )

    assert result == "compiled-agent"
    assert {subagent["name"] for subagent in captured["subagents"]} == {
        "planner",
        "researcher",
        "verifier",
        "synthesizer",
    }
    assert captured["skills"]
    assert captured["state_schema"].__name__ == "ResearchState"


def test_agent_resolves_project_root_tool_imports(tmp_path):
    from deepagent.agent import build_tools
    from deepagent.config import Settings

    settings = Settings(deepseek_api_key="test-key", workspace_root=str(tmp_path))

    tools = build_tools(settings)

    assert {tool.name for tool in tools} >= {
        "web_search",
        "fetch_url",
        "read_file",
        "write_report",
    }


def test_agent_includes_registered_plugin_tools(monkeypatch, tmp_path):
    from types import SimpleNamespace

    import deepagent.agent as agent_module
    from deepagent.config import Settings

    plugin_tool = SimpleNamespace(name="test_plugin_tool")
    monkeypatch.setattr(agent_module, "load_plugin_tools", lambda: [plugin_tool])
    settings = Settings(deepseek_api_key="test-key", workspace_root=str(tmp_path))

    assert plugin_tool in agent_module.build_tools(settings)