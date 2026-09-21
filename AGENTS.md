# AGENTS.md

Not a git repo. No CI, pre-commit, lint, format, or typecheck tooling exists — **pytest is the only verification step**. All commands verified on Windows/PowerShell.

## Layout

- Workspace root holds only: `.venv/` (shared venv), `.agents/skills/` (opencode skills: deepagentskill, langchainskill, deepagentmcp), and `deepagent/` — the actual project (draft DeepSeek research agent, Python + LangChain `deepagents`).
- Two different `skills` dirs: `.agents/skills/` = opencode skills for *this* agent; `deepagent/skills/*/SKILL.md` = skill cards read by the *deepagent runtime* (tests assert ≥1 exists — don't delete/rename).
- `deepagent/` uses src layout: `src/deepagent/` is the package (config, agent factory, CLI, state). But `tools/`, `plugins/`, `instructions/`, `mcp/`, `skills/` live **outside** the package at `deepagent/` root and are imported as top-level modules (`from tools.web_search import ...`). Nothing is pip-installed in the venv.

## Commands

The venv is at workspace root `.venv/` — **not** `deepagent/.venv` as the README claims. The README's quickstart is also stale about CLI invocation; use these instead:

```powershell
# Tests — work from anywhere; tests insert both roots into sys.path themselves. Offline, no API key.
.\.venv\Scripts\python.exe -m pytest deepagent/tests -q
.\.venv\Scripts\python.exe -m pytest deepagent/tests\test_smoke.py::test_config_defaults -q   # single test

# CLI — package is NOT pip-installed. Requires CWD=deepagent\ AND src on PYTHONPATH
# (running `python -m deepagent.cli` without PYTHONPATH fails: No module named 'deepagent')
cd deepagent
$env:PYTHONPATH="src"
..\.venv\Scripts\python.exe -m deepagent.cli "your question" --model deepseek-reasoner

# Examples resolve sys.path themselves, but .env only loads when CWD=deepagent\
..\.venv\Scripts\python.exe examples\run_research.py "question"
```

## Runtime quirks (verified)

- **CWD must be `deepagent/`** for real runs: `tools`/`plugins` imports resolve relative to it, and `load_dotenv()` only picks up `deepagent/.env` from there (running from workspace root silently loads no keys → `DEEPSEEK_API_KEY is not set`).
- Setup: copy `deepagent/.env.example` → `deepagent/.env` (gitignored; never commit keys). `DEEPSEEK_API_KEY` required; `TAVILY_API_KEY` optional — without it `web_search` falls back to DuckDuckGo via `ddgs`.
- Model via `DEEPSEEK_MODEL` or `--model`: `deepseek-chat` (default) / `deepseek-reasoner`.
- No lint/typecheck to run — after changes, just run pytest.

## Architecture

- Build chain: `src/deepagent/config.py` (env → `Settings`) → `agent.py::build_agent()` → `deepagents.create_deep_agent(model=ChatDeepSeek instance, tools, system_prompt)`. The model is an *initialized* `ChatDeepSeek`, not a provider-string.
- Prompts in `instructions/*.md` are read at runtime via a path relative to `agent.py` (`parents[2]`), not packaged. `tests/test_smoke.py::test_prompts_exist` pins all four filenames (`system_prompt`, `planner`, `researcher`, `synthesizer`) — renaming breaks tests.
- Other test-pinned structure: `mcp/mcp_config.json` must keep a top-level `mcpServers` key; `plugins.registry` must stay importable; ≥1 `skills/*/SKILL.md`.
- Plugins are opt-in: add the dotted module path to `ENABLED` in `plugins/registry.py` (currently `[]`); `register()` returns a tool list.
- `build_tools()` swallows file-tool and plugin import errors with bare `except: pass` — missing tools fail silently; check manually when debugging.
- MCP: `examples/run_with_mcp.py` shows loading `mcp/mcp_config.json` via `langchain-mcp-adapters` (2 remote LangChain docs servers + a `npx` Tavily server needing `TAVILY_API_KEY`). `mcp/servers/docs_server.py` is an unwired stub.
- `deepagent/opencode.json` defines an opencode `research` agent + DeepSeek provider reading `DEEPSEEK_API_KEY` from the environment.
