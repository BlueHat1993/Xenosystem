"""Shared state for delegated research and evidence collection."""

from __future__ import annotations

try:
    from deepagents import DeepAgentState  # type: ignore

    class ResearchState(DeepAgentState):  # type: ignore
        """Deep Agents state plus structured research metadata."""

        question: str
        plan: str
        findings: list[dict]
        selected_capabilities: list[str]
        provenance: list[dict]

except Exception:  # deepagents not installed yet — fall back to plain TypedDict
    from typing import Annotated, TypedDict

    from langgraph.graph.message import add_messages

    class ResearchState(TypedDict):
        messages: Annotated[list, add_messages]
        question: str
        plan: str
        findings: list[dict]
        selected_capabilities: list[str]
        provenance: list[dict]
