"""Web search tool: Tavily (preferred) with DuckDuckGo fallback (no key needed)."""

from __future__ import annotations


def make_web_search_tool(settings):
    """Return a LangChain-compatible `web_search` tool bound to settings."""
    try:
        from langchain_core.tools import tool
    except ImportError as exc:
        raise RuntimeError("langchain-core is required: pip install -r requirements.txt") from exc

    @tool("web_search")
    def web_search(query: str) -> str:
        """Search the internet for up-to-date facts. Input: a concise search query."""
        # 1. Try Tavily when a key is configured.
        if getattr(settings, "tavily_api_key", ""):
            try:
                from tavily import TavilyClient

                client = TavilyClient(api_key=settings.tavily_api_key)
                resp = client.search(
                    query,
                    max_results=getattr(settings, "tavily_max_results", 5),
                    search_depth="advanced",
                    include_answer=True,
                )
                lines = []
                if resp.get("answer"):
                    lines.append(f"Answer: {resp['answer']}")
                for r in resp.get("results", []):
                    lines.append(f"- {r.get('title', '')} ({r.get('url', '')})\n  {r.get('content', '')[:800]}")
                return "\n".join(lines) or "No results."
            except Exception as exc:  # fall through to DDG
                print(f"[web_search] tavily failed ({exc}), falling back to DuckDuckGo")

        # 2. DuckDuckGo fallback — free, no key.
        try:
            from ddgs import DDGS

            out = []
            with DDGS() as ddgs:
                for i, r in enumerate(ddgs.text(query, max_results=5)):
                    out.append(f"- {r.get('title', '')} ({r.get('href', '')})\n  {r.get('body', '')[:800]}")
            return "\n".join(out) or "No results."
        except Exception as exc:
            return f"web_search failed: {exc}. Tip: set TAVILY_API_KEY in .env."

    return web_search
