# DeepAgent — Generalized Research Agent (DeepSeek-powered)

A generalized **research agent** inspired by [Deep Agents](https://docs.langchain.com/oss/python/deepagents/quickstart). It delegates planning, evidence collection, verification, and synthesis across public web sources, real web URLs / GitHub repositories, and an explicitly configured local workspace.
Model provider: **DeepSeek** (`deepseek-chat` / `deepseek-reasoner`) via OpenAI-compatible API.

## Quickstart

```powershell
# 1. Activate shared venv
.\.venv\Scripts\Activate.ps1

# 2. Configure keys
copy deepagent\.env.example deepagent\.env
# edit deepagent\.env -> set DEEPSEEK_API_KEY (https://platform.deepseek.com)
# optionally set TAVILY_API_KEY for web search (https://tavily.com)

# 3. Single command run (with real-time streaming output by default)
python run.py "What are the latest advances in Mixture-of-Experts models?"

# Or inspect website links / GitHub repositories directly:
python run.py "Summarize https://github.com/langchain-ai/deepagents" --model deepseek-reasoner

# Direct CLI executable (installed in .venv):
deepagent "Compare DeepSeek-V3 vs GPT-4o on reasoning benchmarks"
```

## Commands & Options

```powershell
# Real-time streaming (default)
python run.py "question"

# Batch mode (wait for complete synthesis)
python run.py "question" --no-stream

# Override model
python run.py "question" --model deepseek-reasoner

# Run tests
.\.venv\Scripts\python.exe -m pytest deepagent/tests -v
```

## Layout

```
run.py                # Single-command root runner
deepagent/
  src/deepagent/      # core agent: config, agent factory, CLI, state
  tools/              # agent tools (web search, URL fetcher, workspace file tools)
  skills/             # reusable skill cards (SKILL.md)
  instructions/       # system / planner / researcher / synthesizer prompts
  plugins/            # optional extensions (registry + example)
  mcp/                # Model Context Protocol servers config
  examples/           # runnable examples
  tests/              # test suite
```

## How it works

1. `src/deepagent/config.py` automatically discovers `.env` and configures workspace root and settings.
2. `tools/web_search.py` provides internet search (Tavily / DuckDuckGo fallback) and `fetch_url` (direct webpage scraping and GitHub raw content resolution).
3. `tools/file_tools.py` provides workspace-scoped local reads and optional report writes.
4. `instructions/system_prompt.md` is the coordinator prompt.
5. `src/deepagent/agent.py` calls `deepagents.create_deep_agent` with trusted tools, specialized subagents, skills, and structured research state.
6. `src/deepagent/cli.py` streams tokens, tool updates, and subagent findings directly to `stdout` in real time.

## DeepSeek notes

- Base URL: `https://api.deepseek.com` (OpenAI-compatible)
- Chat model: `deepseek-chat` (default, fast + cheap)
- Reasoning model: `deepseek-reasoner` (slower, better for deep research; set `DEEPSEEK_MODEL=deepseek-reasoner` or use `--model deepseek-reasoner`)
- Env: `DEEPSEEK_API_KEY`, `DEEPSEEK_BASE_URL`, `DEEPSEEK_MODEL`, `DEEPSEEK_TEMPERATURE`, `DEEPSEEK_MAX_TOKENS`

## Capability policy

`DEEPAGENT_WORKSPACE_ROOT` is the boundary for local reads and report writes. Paths outside it are rejected. Report writes can be disabled with `DEEPAGENT_ALLOW_REPORT_WRITES=false`.
Runtime composition uses only registered tools. Generated executable tools are disabled by default; enabling them requires approval.
