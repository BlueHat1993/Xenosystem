"""Shared agent state (extends Deep Agents default state when available)."""

from __future__ import annotations

try:
    from deepagents.state import DeepAgentState  # type: ignore

    class ResearchState(DeepAgentState):  # type: ignore
        """Inherits todos, files, messages from DeepAgentState."""

        pass

except Exception:  # deepagents not installed yet — fall back to plain TypedDict
    from typing import Annotated, TypedDict

    from langgraph.graph.message import add_messages

    class ResearchState(TypedDict):
        messages: Annotated[list, add_messages]
        question: str
        plan: str
        findings: list[str]
