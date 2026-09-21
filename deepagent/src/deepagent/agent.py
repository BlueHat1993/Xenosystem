"""Agent factory — wires a DeepSeek chat model + tools into create_deep_agent."""

from __future__ import annotations

from pathlib import Path

from deepagent.config import Settings, get_settings

INSTRUCTIONS_DIR = Path(__file__).resolve().parents[2] / "instructions"


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
    """Collect default tools: web search + file helpers."""
    from tools.web_search import make_web_search_tool

    tools = [make_web_search_tool(settings)]

    try:
        from tools.file_tools import read_file, write_report

        tools.extend([read_file, write_report])
    except Exception:
        pass  # file tools are optional in the draft

    # Append plugin tools if any are registered.
    try:
        from plugins.registry import load_plugin_tools

        tools.extend(load_plugin_tools())
    except Exception:
        pass

    return tools


def build_agent(settings: Settings | None = None):
    """Create the DeepAgent research agent."""
    from deepagents import create_deep_agent

    settings = settings or get_settings()
    settings.validate()

    model = build_model(settings)
    tools = build_tools(settings)
    system_prompt = load_prompt("system_prompt.md") or (
        "You are a careful research agent. Plan, search, cite sources, then synthesize."
    )

    agent = create_deep_agent(
        model=model,
        tools=tools,
        system_prompt=system_prompt,
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
