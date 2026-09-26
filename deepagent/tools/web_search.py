"""Web tools: search (Tavily / DuckDuckGo) and direct URL / GitHub content fetching."""

from __future__ import annotations

import re
import html
from langchain_core.tools import tool


def _clean_html(raw_html: str) -> str:
    """Extract readable text from HTML by removing boilerplate tags."""
    # Remove script, style, head, nav, footer tags and their contents
    text = re.sub(r"<(script|style|head|nav|footer)[^>]*>.*?</\1>", " ", raw_html, flags=re.DOTALL | re.IGNORECASE)
    # Convert common block tags to newlines
    text = re.sub(r"<(p|br|h[1-6]|li|tr)[^>]*>", "\n", text, flags=re.IGNORECASE)
    # Strip remaining tags
    text = re.sub(r"<[^>]+>", " ", text)
    # Decode HTML entities
    text = html.unescape(text)
    # Normalize excessive whitespace
    lines = [re.sub(r"[ \t]+", " ", line).strip() for line in text.splitlines()]
    return "\n".join(line for line in lines if line)


def _normalize_github_url(url: str) -> str:
    """Convert standard GitHub web URLs to raw content URLs when possible."""
    clean_url = url.strip()
    # Pattern: github.com/{owner}/{repo}/blob/{branch}/{path} -> raw.githubusercontent.com/{owner}/{repo}/{branch}/{path}
    blob_match = re.match(r"^https?://github\.com/([^/]+)/([^/]+)/blob/([^/]+)/(.+)$", clean_url)
    if blob_match:
        owner, repo, branch, path = blob_match.groups()
        return f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{path}"
    return clean_url


def make_fetch_url_tool(settings=None):
    """Return a tool to fetch and extract text from web URLs and GitHub files."""

    @tool("fetch_url")
    def fetch_url(url: str) -> str:
        """Fetch the text content of a public webpage or GitHub file. Input: a full HTTP or HTTPS URL."""
        import httpx

        target_url = _normalize_github_url(url)
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) DeepAgent/0.1",
            "Accept": "text/html,application/xhtml+xml,text/plain,application/json;q=0.9,*/*;q=0.8",
        }

        try:
            with httpx.Client(timeout=15.0, follow_redirects=True, headers=headers) as client:
                resp = client.get(target_url)

                # If a GitHub repo root was requested and got 404 or web HTML, try fetching its README
                if "github.com" in url and not blob_match_check(url):
                    repo_match = re.match(r"^https?://github\.com/([^/]+)/([^/]+)/?$", url.strip())
                    if repo_match:
                        owner, repo = repo_match.groups()
                        for branch in ("main", "master"):
                            raw_readme = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/README.md"
                            readme_resp = client.get(raw_readme)
                            if readme_resp.status_code == 200:
                                return f"[GitHub README: {owner}/{repo}]\n\n" + readme_resp.text[:20_000]

                if resp.status_code != 200:
                    return f"Failed to fetch {url}: HTTP {resp.status_code}"

                content_type = resp.headers.get("content-type", "").lower()
                text = resp.text

                if "text/html" in content_type:
                    extracted = _clean_html(text)
                else:
                    extracted = text

                return extracted[:20_000] or "No text content found at URL."
        except Exception as exc:
            return f"Error fetching URL {url}: {exc}"

    def blob_match_check(u: str) -> bool:
        return "/blob/" in u or "/raw/" in u

    return fetch_url


def make_web_search_tool(settings):
    """Return a LangChain-compatible `web_search` tool bound to settings."""

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
