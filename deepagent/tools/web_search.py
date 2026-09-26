"""Compatibility imports for the source-tree tools package."""

from deepagent.tools.web_search import (
    _clean_html,
    _normalize_github_url,
    make_fetch_url_tool,
    make_web_search_tool,
)

__all__ = [
    "_clean_html",
    "_normalize_github_url",
    "make_fetch_url_tool",
    "make_web_search_tool",
]
