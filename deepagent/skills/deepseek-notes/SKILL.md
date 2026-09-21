---
name: deepseek-notes
description: Quick reference for DeepSeek API quirks used by this agent.
---

# DeepSeek notes

- Base URL: `https://api.deepseek.com` (OpenAI-compatible).
- Env: `DEEPSEEK_API_KEY`, `DEEPSEEK_BASE_URL`, `DEEPSEEK_MODEL`.
- `deepseek-chat`: default chat model, best cost/speed for routine research.
- `deepseek-reasoner`: chain-of-thought reasoning model, better for multi-hop
  synthesis; slower and longer outputs — raise `DEEPSEEK_MAX_TOKENS` to 8000+.
- Temperature: keep low (0.0–0.3) for factual research.
- No built-in web search — this repo adds it via `tools/web_search.py`
  (Tavily or DuckDuckGo) and passes results in as tool observations.
