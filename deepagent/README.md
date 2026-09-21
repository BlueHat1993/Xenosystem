# DeepAgent — Draft Research Agent (DeepSeek-powered)

A minimal, extensible **research agent** draft inspired by [Deep Agents](https://docs.langchain.com/oss/python/deepagents/quickstart).
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

# 3. Run a research task
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

1. `src/deepagent/config.py` loads `DEEPSEEK_API_KEY`, model, Tavily key.
2. `tools/web_search.py` provides internet search (Tavily preferred, DuckDuckGo fallback).
3. `instructions/system_prompt.md` is the research system prompt.
4. `src/deepagent/agent.py` calls `deepagents.create_deep_agent(model, tools, system_prompt)`.
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

## Status

**Draft v0.1** — runnable skeleton. Not production-hardened. No keys committed.
