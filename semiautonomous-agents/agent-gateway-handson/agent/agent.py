"""Minimal ADK agent that discovers MCP tools via Agent Registry.

The trick: the tool URL comes from the registry, which is what makes every
tool call traverse the Agent Gateway and its authz extensions. If you
hard-coded the Cloud Run URL here, you'd be bypassing the governance plane.
"""

from __future__ import annotations

import logging
import os

from google.adk.agents.llm_agent import Agent
from google.adk.tools.agent_registry import AgentRegistry

log = logging.getLogger(__name__)

PROJECT  = os.environ["MCP_REGISTRY_PROJECT"]
LOCATION = os.environ.get("MCP_REGISTRY_LOCATION", "us-central1")
MODEL    = os.environ.get("MODEL_NAME", "gemini-2.5-flash-lite")


def _build_agent() -> Agent:
    registry = AgentRegistry(project=PROJECT, location=LOCATION)
    toolsets = []
    for srv in registry.list_mcp_servers():
        log.info("Discovered MCP server: %s @ %s", srv.display_name, srv.uri)
        toolsets.append(registry.get_mcp_toolset(mcp_server_name=srv.name))
    return Agent(
        name="legacy_dms_assistant",
        model=MODEL,
        instruction=(
            "You help engineers explore a legacy document store via MCP tools. "
            "When the user asks about documents, call list_documents first to see what's available, "
            "then call get_document for specifics. Always cite the document id."
        ),
        tools=toolsets,
    )


root_agent = _build_agent()
