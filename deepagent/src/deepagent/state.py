"""Shared state for delegated research and evidence collection."""

from __future__ import annotations

from deepagents import DeepAgentState


class ResearchState(DeepAgentState):
    """Deep Agents state plus structured research metadata."""

    question: str
    plan: str
    findings: list[dict]
    selected_capabilities: list[str]
    provenance: list[dict]
