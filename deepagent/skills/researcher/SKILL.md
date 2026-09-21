---
name: researcher
description: Deep research workflow — plan, search with web_search, verify, synthesize with citations.
---

# Researcher skill

Use this skill when the user asks to research, compare, survey, or explain a topic.

## Workflow

1. Read `instructions/system_prompt.md` for the report format.
2. Draft a plan per `instructions/planner.md` (sub-questions first).
3. For each sub-question call the `web_search` tool (see `tools/web_search.py`).
4. Collect evidence bullets per `instructions/researcher.md`.
5. Synthesize per `instructions/synthesizer.md` with title + URL citations.
6. Optionally save via `write_report` (`tools/file_tools.py`).

## Notes

- Model: DeepSeek (`DEEPSEEK_MODEL=deepseek-chat` default, `deepseek-reasoner` for harder tasks).
- If `TAVILY_API_KEY` is missing, `web_search` falls back to DuckDuckGo.
