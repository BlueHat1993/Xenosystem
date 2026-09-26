# AGENTS.md

Not a git repo. No CI, pre-commit, lint, format, or typecheck tooling exists — **pytest is the only verification step**. All commands verified on Windows/PowerShell.

## Layout

- Workspace root holds: `.venv/` (shared venv), `.agents/skills/` (opencode skills), `run.py` (unified root runner), and `deepagent/` — the actual project (DeepSeek research agent, Python + LangChain `deepagents`).
- Two different `skills` dirs: `.agents/skills/` = opencode skills for *this* agent; `deepagent/skills/*/SKILL.md` = skill cards read by the *deepagent runtime* (tests assert ≥1 exists — don't delete/rename).
- `deepagent/` uses src layout and is pip-installed in editable mode (`pip install -e deepagent`).
- `tools/`, `plugins/`, `instructions/`, `mcp/`, `skills/` live at `deepagent/` root and are auto-resolved into `sys.path`.

## Commands

```powershell
# Tests — work from anywhere; tests insert roots into sys.path themselves. Offline, no API key.
.\.venv\Scripts\python.exe -m pytest deepagent/tests -v

# Single Command Runner (from workspace root) — streams in real-time by default:
.\.venv\Scripts\python.exe run.py "your question"
.\.venv\Scripts\python.exe run.py "https://github.com/langchain-ai/deepagents" --model deepseek-reasoner
.\.venv\Scripts\python.exe run.py "question" --no-stream   # batch mode

# Direct CLI executable (installed in .venv):
.\.venv\Scripts\deepagent.exe "your question"

# Module CLI:
.\.venv\Scripts\python.exe -m deepagent "your question"
```

## Runtime features

- **CWD independent**: `config.py` and `agent.py` automatically discover `deepagent/.env` and insert project roots onto `sys.path`. You can run commands from `f:\Xenosystem` or `f:\Xenosystem\deepagent` seamlessly without manual `$env:PYTHONPATH` configuration.
- **Real-Time Streaming Output**: Enabled by default in CLI and `run.py`; tokens and tool actions stream live to stdout.
- **Direct Link & GitHub Fetching**: `fetch_url` tool automatically converts GitHub blob/repo URLs to raw content and extracts text from web links.
- Setup: copy `deepagent/.env.example` → `deepagent/.env` (gitignored; never commit keys). `DEEPSEEK_API_KEY` required; `TAVILY_API_KEY` optional — without it `web_search` falls back to DuckDuckGo via `ddgs`.
- Model via `DEEPSEEK_MODEL` or `--model`: `deepseek-chat` (default) / `deepseek-reasoner`.
- No lint/typecheck to run — after changes, just run pytest.

## Architecture

- Build chain: `src/deepagent/config.py` (env → `Settings`) → `agent.py::build_agent()` → `deepagents.create_deep_agent(model=ChatDeepSeek instance, tools, system_prompt)`. The model is an *initialized* `ChatDeepSeek`, not a provider-string.
- Prompts in `instructions/*.md` are read at runtime via a path relative to `agent.py` (`parents[2]`), not packaged. `tests/test_smoke.py::test_prompts_exist` pins all four filenames (`system_prompt`, `planner`, `researcher`, `synthesizer`) — renaming breaks tests.
- Other test-pinned structure: `mcp/mcp_config.json` must keep a top-level `mcpServers` key; `plugins.registry` must stay importable; ≥1 `skills/*/SKILL.md`.
- Plugins are opt-in: add the dotted module path to `ENABLED` in `plugins/registry.py` (currently `[]`); `register()` returns a tool list.
- MCP: `examples/run_with_mcp.py` shows loading `mcp/mcp_config.json` via `langchain-mcp-adapters` (2 remote LangChain docs servers + a `npx` Tavily server needing `TAVILY_API_KEY`).
- `deepagent/opencode.json` defines an opencode `research` agent + DeepSeek provider reading `DEEPSEEK_API_KEY` from the environment.
