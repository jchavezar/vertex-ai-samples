"""Extracts a JSON graph (nodes + edges) from any ADK agent tree.

Walks `sub_agents` recursively and produces a topology suitable for
Cytoscape.js. Container agents (Sequential/Loop/Parallel) are emitted as
their own node so the UI can show grouping; we also tag the orchestration
kind so the UI can pulse animated edges differently for parallel vs.
sequential branches.
"""
from __future__ import annotations

from typing import Any

from google.adk.agents import (
    BaseAgent,
    LoopAgent,
    ParallelAgent,
    SequentialAgent,
)


def _kind(agent: BaseAgent) -> str:
    if isinstance(agent, SequentialAgent):
        return "sequential"
    if isinstance(agent, LoopAgent):
        return "loop"
    if isinstance(agent, ParallelAgent):
        return "parallel"
    cls = type(agent).__name__
    if cls.endswith("Agent"):
        return cls.replace("Agent", "").lower() or "agent"
    return cls.lower()


def agent_to_graph(root: BaseAgent) -> dict[str, list[dict[str, Any]]]:
    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []
    seen: set[str] = set()

    def visit(agent: BaseAgent, parent_id: str | None) -> None:
        if agent.name in seen:
            return
        seen.add(agent.name)
        kind = _kind(agent)
        nodes.append(
            {
                "id": agent.name,
                "label": agent.name,
                "kind": kind,
                "description": (agent.description or "")[:240],
                "is_container": bool(getattr(agent, "sub_agents", None)),
            }
        )
        if parent_id is not None:
            edges.append({"source": parent_id, "target": agent.name, "kind": "contains"})

        children = getattr(agent, "sub_agents", None) or []
        for i, child in enumerate(children):
            visit(child, agent.name)
            # In sequential pipelines, draw a "next" edge between siblings
            # so the UI can animate the data flow.
            if isinstance(agent, (SequentialAgent, LoopAgent)) and i > 0:
                edges.append(
                    {
                        "source": children[i - 1].name,
                        "target": child.name,
                        "kind": "flow",
                    }
                )

    visit(root, None)
    return {"nodes": nodes, "edges": edges}
