"""Web search and direct URL / GitHub content fetching tools."""

from __future__ import annotations

import html
import re

from langchain_core.tools import tool


def _clean_html(raw_html: str) -> str:
    """Extract readable text from HTML by removing boilerplate tags."""
    text = re.sub(
        r"<(script|style|head|nav|footer)[^>]*>.*?</\1>",
        " ",
        raw_html,
        flags=re.DOTALL | re.IGNORECASE,
    )
    text = re.sub(r"<(p|br|h[1-6]|li|tr)[^>]*>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    lines = [re.sub(r"[ \t]+", " ", line).strip() for line in text.splitlines()]
    return "\n".join(line for line in lines if line)


def _normalize_github_url(url: str) -> str:
    """Convert standard GitHub blob URLs to raw content URLs."""
    clean_url = url.strip()
    blob_match = re.match(
        r"^https?://github\.com/([^/]+)/([^/]+)/blob/([^/]+)/(.+)$", clean_url
    )
    if blob_match:
        owner, repo, branch, path = blob_match.groups()
        return f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{path}"
    return clean_url


def make_fetch_url_tool(settings=None):
    """Return a tool to fetch and extract text from web URLs and GitHub files."""

    @tool("fetch_url")
    def fetch_url(url: str) -> str:
        """Fetch text from a public webpage or GitHub file using its HTTP(S) URL."""
        import httpx

        target_url = _normalize_github_url(url)
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) DeepAgent/0.1",
            "Accept": "text/html,application/xhtml+xml,text/plain,application/json;q=0.9,*/*;q=0.8",
        }

        try:
            with httpx.Client(timeout=15.0, follow_redirects=True, headers=headers) as client:
                response = client.get(target_url)
                if "github.com" in url and not _is_github_blob_url(url):
                    repo_match = re.match(
                        r"^https?://github\.com/([^/]+)/([^/]+)/?$", url.strip()
                    )
                    if repo_match:
                        owner, repo = repo_match.groups()
                        for branch in ("main", "master"):
                            readme_url = (
                                f"https://raw.githubusercontent.com/{owner}/{repo}/"
                                f"{branch}/README.md"
                            )
                            readme_response = client.get(readme_url)
                            if readme_response.status_code == 200:
                                return (
                                    f"[GitHub README: {owner}/{repo}]\n\n"
                                    + readme_response.text[:20_000]
                                )

                if response.status_code != 200:
                    return f"Failed to fetch {url}: HTTP {response.status_code}"

                content_type = response.headers.get("content-type", "").lower()
                text = response.text
                extracted = _clean_html(text) if "text/html" in content_type else text
                return extracted[:20_000] or "No text content found at URL."
        except Exception as exc:
            return f"Error fetching URL {url}: {exc}"

    return fetch_url


def _is_github_blob_url(url: str) -> bool:
    return "/blob/" in url or "/raw/" in url


def make_web_search_tool(settings):
    """Return a LangChain-compatible web search tool bound to settings."""

    @tool("web_search")
    def web_search(query: str) -> str:
        """Search the internet for up-to-date facts using a concise query."""
        if getattr(settings, "tavily_api_key", ""):
            try:
                from tavily import TavilyClient

                client = TavilyClient(api_key=settings.tavily_api_key)
                response = client.search(
                    query,
                    max_results=getattr(settings, "tavily_max_results", 5),
                    search_depth="advanced",
                    include_answer=True,
                )
                lines = []
                if response.get("answer"):
                    lines.append(f"Answer: {response['answer']}")
                for result in response.get("results", []):
                    lines.append(
                        f"- {result.get('title', '')} ({result.get('url', '')})\n"
                        f"  {result.get('content', '')[:800]}"
                    )
                return "\n".join(lines) or "No results."
            except Exception as exc:
                print(f"[web_search] tavily failed ({exc}), falling back to DuckDuckGo")

        try:
            from ddgs import DDGS

            output = []
            with DDGS() as ddgs:
                for result in ddgs.text(query, max_results=5):
                    output.append(
                        f"- {result.get('title', '')} ({result.get('href', '')})\n"
                        f"  {result.get('body', '')[:800]}"
                    )
            return "\n".join(output) or "No results."
        except Exception as exc:
            return f"web_search failed: {exc}. Tip: set TAVILY_API_KEY in .env."

    return web_search