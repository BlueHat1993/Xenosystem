"""Tests for single-command CLI, fetch_url tool, and streaming capabilities."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from deepagent.config import Settings
from tools.web_search import _clean_html, _normalize_github_url, make_fetch_url_tool


def test_normalize_github_blob_url():
    url = "https://github.com/langchain-ai/deepagents/blob/main/README.md"
    expected = "https://raw.githubusercontent.com/langchain-ai/deepagents/main/README.md"
    assert _normalize_github_url(url) == expected


def test_clean_html():
    raw = """
    <html>
        <head><title>Test</title><style>body { color: red; }</style></head>
        <body>
            <script>alert("hi");</script>
            <h1>Heading</h1>
            <p>First paragraph &amp; text.</p>
        </body>
    </html>
    """
    cleaned = _clean_html(raw)
    assert "alert" not in cleaned
    assert "color: red" not in cleaned
    assert "Heading" in cleaned
    assert "First paragraph & text." in cleaned


def test_fetch_url_tool_success():
    fetch_tool = make_fetch_url_tool()
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.headers = {"content-type": "text/html"}
    mock_resp.text = "<html><body><h1>Documentation</h1><p>Welcome to the docs.</p></body></html>"

    with patch("httpx.Client.get", return_value=mock_resp):
        result = fetch_tool.invoke("https://example.com/docs")
        assert "Documentation" in result
        assert "Welcome to the docs." in result


def test_fetch_url_tool_http_error():
    fetch_tool = make_fetch_url_tool()
    mock_resp = MagicMock()
    mock_resp.status_code = 404

    with patch("httpx.Client.get", return_value=mock_resp):
        result = fetch_tool.invoke("https://example.com/nonexistent")
        assert "HTTP 404" in result


def test_cli_argument_parsing():
    from deepagent.cli import main

    # Test missing question exits with code 2
    with pytest.raises(SystemExit) as exc:
        main([])
    assert exc.value.code == 2


def test_stream_research_generator():
    from deepagent.agent import stream_research
    from langchain_core.messages import AIMessageChunk

    settings = Settings(deepseek_api_key="test-key")

    mock_agent = MagicMock()
    mock_chunk = AIMessageChunk(content="Hello streaming world")
    mock_agent.stream.return_value = [
        ("messages", (mock_chunk, {"langgraph_node": "model"}))
    ]

    with patch("deepagent.agent.build_agent", return_value=mock_agent):
        events = list(stream_research("test question", settings))
        tokens = [p for e, p in events if e == "token"]
        assert "Hello streaming world" in tokens
