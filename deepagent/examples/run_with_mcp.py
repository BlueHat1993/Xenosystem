"""Run the agent with MCP tools loaded from mcp/mcp_config.json.

Usage:
    python examples/run_with_mcp.py "your research question"

Requires: pip install langchain-mcp-adapters
"""

import asyncio
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from deepagent.agent import extract_final_answer, build_model, load_prompt
from deepagent.config import get_settings
from deepagent.agent import build_tools


async def main() -> None:
    question = " ".join(sys.argv[1:]) or "Summarize the Deep Agents library."
    settings = get_settings()
    settings.validate()

    from langchain_mcp_adapters.client import MultiServerMCPClient

    config = json.loads((ROOT / "mcp" / "mcp_config.json").read_text(encoding="utf-8"))
    client = MultiServerMCPClient(config.get("mcpServers", {}))
    mcp_tools = await client.get_tools()

    tools = build_tools(settings) + mcp_tools
    print(f"[tools] {len(tools)} loaded ({len(mcp_tools)} from MCP)")

    from deepagents import create_deep_agent

    agent = create_deep_agent(
        model=build_model(settings),
        tools=tools,
        system_prompt=load_prompt("system_prompt.md"),
    )
    result = await agent.ainvoke({"messages": [{"role": "user", "content": question}]})
    print("\n=== FINAL REPORT ===\n")
    print(extract_final_answer(result) or result)


if __name__ == "__main__":
    asyncio.run(main())
