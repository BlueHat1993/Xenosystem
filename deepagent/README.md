# DeepAgent — Generalized Research Agent (DeepSeek-powered)

A generalized **research agent** inspired by [Deep Agents](https://docs.langchain.com/oss/python/deepagents/quickstart). It delegates planning, evidence collection, verification, and synthesis across public web sources and an explicitly configured local workspace.
Model provider: **DeepSeek** (`deepseek-chat` / `deepseek-reasoner`) via OpenAI-compatible API.

## Quickstart

```powershell
# 1. Create venv + install
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 2. Configure keys
copy .env.example .env
# edit .env -> set DEEPSEEK_API_KEY (https://platform.deepseek.com)
# optionally set TAVILY_API_KEY for web search (https://tavily.com)

# 3. Run a research task from the deepagent directory
cd deepagent
$env:PYTHONPATH="src"
python -m deepagent.cli "What are the latest advances in Mixture-of-Experts models?"
# or
python examples/run_research.py "Compare DeepSeek-V3 vs GPT-4o on reasoning benchmarks"
```

## Layout

```
deepagent/
  src/deepagent/      # core agent: config, agent factory, CLI, state
  tools/              # agent tools (web search, file tools)
  skills/             # reusable skill cards (SKILL.md)
  instructions/       # system / planner / researcher / synthesizer prompts
  plugins/            # optional extensions (registry + example)
  mcp/                # Model Context Protocol servers config
  examples/           # runnable examples
  tests/              # smoke tests
```

## How it works

1. `src/deepagent/config.py` loads DeepSeek, search, workspace, and capability policy settings.
2. `tools/web_search.py` provides internet search (Tavily preferred, DuckDuckGo fallback).
3. `tools/file_tools.py` provides workspace-scoped local reads and optional report writes.
4. `instructions/system_prompt.md` is the coordinator prompt.
5. `src/deepagent/agent.py` calls `deepagents.create_deep_agent` with trusted tools, specialized subagents, skills, and structured research state.
   - Model is an initialized `ChatDeepSeek` (from `langchain-deepseek`), so any
     DeepSeek model string works without provider hacks.
5. `src/deepagent/cli.py` runs the agent and prints the final report.

## DeepSeek notes

- Base URL: `https://api.deepseek.com` (OpenAI-compatible)
- Chat model: `deepseek-chat` (default, fast + cheap)
- Reasoning model: `deepseek-reasoner` (slower, better for deep research; set `DEEPSEEK_MODEL=deepseek-reasoner`)
- Env: `DEEPSEEK_API_KEY`, `DEEPSEEK_BASE_URL`, `DEEPSEEK_MODEL`, `DEEPSEEK_TEMPERATURE`, `DEEPSEEK_MAX_TOKENS`

## MCP

See `mcp/mcp_config.json` and `mcp/README.md`. Add your own servers there;
`examples/run_with_mcp.py` shows how to load them with `langchain-mcp-adapters`.

## Capability policy

`DEEPAGENT_WORKSPACE_ROOT` is the boundary for local reads and report writes. Paths
outside it are rejected. Report writes can be disabled with
`DEEPAGENT_ALLOW_REPORT_WRITES=false`.

Runtime composition uses only registered tools. Generated executable tools are
disabled by default; enabling them requires approval and a separately implemented
sandbox. This repository does not expose arbitrary shell or host-process access.

## Status

**Draft v0.1** — runnable skeleton. Not production-hardened. No keys committed.
