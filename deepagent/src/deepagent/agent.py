"""Agent factory for the delegated DeepSeek research workflow."""

from __future__ import annotations

from pathlib import Path

from deepagent.config import Settings, get_settings

INSTRUCTIONS_DIR = Path(__file__).resolve().parents[2] / "instructions"
SKILLS_DIR = Path(__file__).resolve().parents[2] / "skills"


def load_prompt(name: str) -> str:
    path = INSTRUCTIONS_DIR / name
    if path.exists():
        return path.read_text(encoding="utf-8")
    return ""


def build_model(settings: Settings):
    """Return an initialized DeepSeek chat model (LangChain compatible)."""
    try:
        from langchain_deepseek import ChatDeepSeek
    except ImportError as exc:
        raise RuntimeError(
            "langchain-deepseek is not installed. Run: pip install -r requirements.txt"
        ) from exc

    return ChatDeepSeek(
        api_key=settings.deepseek_api_key,
        base_url=settings.deepseek_base_url,
        model=settings.deepseek_model,
        temperature=settings.deepseek_temperature,
        max_tokens=settings.deepseek_max_tokens,
    )


def build_tools(settings: Settings) -> list:
    """Collect trusted tools: web search, workspace helpers, and plugins."""
    from tools.web_search import make_web_search_tool
    from tools.file_tools import make_file_tools

    tools = [make_web_search_tool(settings)]

    try:
        tools.extend(make_file_tools(settings))
    except Exception:
        pass

    # Append plugin tools if any are registered.
    try:
        from plugins.registry import load_plugin_tools

        tools.extend(load_plugin_tools())
    except Exception:
        pass

    return tools


def build_subagents(settings: Settings, tools: list | None = None) -> list[dict]:
    """Build focused subagents with explicit capabilities and role prompts."""
    tools = tools if tools is not None else build_tools(settings)
    web_tools = [tool for tool in tools if _tool_name(tool) == "web_search"]
    read_tools = [tool for tool in tools if _tool_name(tool) == "read_file"]
    research_tools = web_tools + read_tools
    skill = str(SKILLS_DIR / "researcher")
    return [
        {
            "name": "planner",
            "description": "Break the request into bounded, searchable environment questions.",
            "system_prompt": load_prompt("planner.md"),
            "tools": [],
            "skills": [skill],
            "mode": "isolated",
        },
        {
            "name": "researcher",
            "description": "Gather evidence from approved web and local-workspace capabilities.",
            "system_prompt": load_prompt("researcher.md"),
            "tools": research_tools,
            "skills": [skill],
            "mode": "isolated",
        },
        {
            "name": "verifier",
            "description": "Cross-check evidence, flag conflicts, and identify unsupported claims.",
            "system_prompt": load_prompt("researcher.md"),
            "tools": research_tools,
            "skills": [skill],
            "mode": "isolated",
        },
        {
            "name": "synthesizer",
            "description": "Turn verified findings into a cited report with open questions.",
            "system_prompt": load_prompt("synthesizer.md"),
            "tools": [],
            "skills": [skill],
            "mode": "isolated",
        },
    ]


def _tool_name(tool) -> str:
    if isinstance(tool, dict):
        return str(tool.get("name", ""))
    return str(getattr(tool, "name", ""))


def build_agent(settings: Settings | None = None):
    """Create the DeepAgent research agent."""
    from deepagents import create_deep_agent

    settings = settings or get_settings()
    settings.validate()

    model = build_model(settings)
    tools = build_tools(settings)
    subagents = build_subagents(settings, tools)
    system_prompt = load_prompt("system_prompt.md") or (
        "You are a careful research agent. Plan, search, cite sources, then synthesize."
    )

    from deepagent.state import ResearchState

    agent = create_deep_agent(
        model=model,
        tools=tools,
        system_prompt=system_prompt,
        subagents=subagents,
        skills=[str(SKILLS_DIR / "researcher")],
        state_schema=ResearchState,
    )
    return agent


def run_research(question: str, settings: Settings | None = None) -> dict:
    """Run one research query and return the raw agent result."""
    settings = settings or get_settings()
    settings.validate()
    agent = build_agent(settings)
    result = agent.invoke({"messages": [{"role": "user", "content": question}]})
    return result


def extract_final_answer(result: dict) -> str:
    """Pull the last assistant message out of a deepagents result."""
    messages = result.get("messages", [])
    for msg in reversed(messages):
        content = getattr(msg, "content", msg.get("content") if isinstance(msg, dict) else "")
        if content:
            if isinstance(content, list):
                parts = [
                    c.get("text", "") if isinstance(c, dict) else str(c) for c in content
                ]
                return "\n".join(p for p in parts if p)
            return str(content)
    return ""
