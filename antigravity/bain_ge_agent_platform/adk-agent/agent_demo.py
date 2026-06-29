"""ADK agent for the Agent Gateway + Agent Identity + 3LO demo.

Two configurations live in this file (toggle via env `USE_AGENT_IDENTITY`):

  USE_AGENT_IDENTITY=0  (default — pre-gateway / local / Cloud-Run direct)
      McpToolset uses a `header_provider` that reads the user's Entra
      access token from `tool_context.state["temp:sharepoint_3lo"]` (the
      key the backend pre-injects when creating the AE session). This is
      identical to the proven pattern in:
        atlassian-on-gemini-enterprise/option-c-adk-rovo-mcp/adk_agent/agent.py:88-95
      Use this for everything BEFORE the gateway exists.

  USE_AGENT_IDENTITY=1  (post-gateway, with a connector + Auth Manager)
      McpToolset uses `GcpAuthProviderScheme` referencing the
      Agent-Identity connector. Auth Manager decrypts the user credential
      at the gateway boundary; the agent never sees the raw token.

Both modes hit the same MCP server URL (`MCP_SERVER_URL`). Switching from
mode 0 to 1 is just an env var change + a redeploy with `agent_gateway_config`.
"""
from __future__ import annotations

import logging
import os

from google.adk.agents.llm_agent import LlmAgent
from google.adk.agents.readonly_context import ReadonlyContext
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset

log = logging.getLogger("agent-gateway-demo.agent")

AGENT_MODEL = os.environ.get("AGENT_MODEL", "gemini-2.5-flash")
MCP_SERVER_URL = os.environ.get("MCP_SERVER_URL", "http://localhost:8080/mcp")
SESSION_TOKEN_KEY = os.environ.get("SESSION_TOKEN_KEY", "temp:sharepoint_3lo")
USE_AGENT_IDENTITY = os.environ.get("USE_AGENT_IDENTITY", "0") == "1"

# Agent-Identity connector resource — only consulted when USE_AGENT_IDENTITY=1.
CONNECTOR_RESOURCE = os.environ.get("CONNECTOR_RESOURCE", "")
# Backend redirect URI Auth Manager bounces back through after consent.
CONTINUE_URI = os.environ.get("CONTINUE_URI", "")


# ──────────────────────────────────────────────────────────────────────────
# Mode 0: header_provider reads pre-injected token from session state
# ──────────────────────────────────────────────────────────────────────────

def _header_provider(ctx: ReadonlyContext) -> dict[str, str]:
    """Pull the user's Entra access token from the backend-injected state
    key and forward it as `Authorization: Bearer ...` to the MCP server."""
    base = {"Accept": "application/json", "Content-Type": "application/json"}
    state = getattr(ctx, "state", None)
    token = None
    if state is not None:
        try:
            token = state.get(SESSION_TOKEN_KEY)
        except Exception:  # noqa: BLE001
            token = None
    if isinstance(token, str) and len(token) > 20:
        log.info("header_provider: forwarding user token (%s…)", token[:8])
        return {**base, "Authorization": f"Bearer {token.strip()}"}
    log.warning("header_provider: no token in state[%r] — MCP call will be unauth.", SESSION_TOKEN_KEY)
    return base


# ──────────────────────────────────────────────────────────────────────────
# McpToolset — one or the other auth wiring
# ──────────────────────────────────────────────────────────────────────────

if USE_AGENT_IDENTITY:
    # Late-import so that mode 0 doesn't require the agent-identity extra.
    from google.adk.auth.credential_manager import CredentialManager
    from google.adk.integrations.agent_identity import (
        GcpAuthProvider,
        GcpAuthProviderScheme,
    )

    if not CONNECTOR_RESOURCE:
        raise RuntimeError(
            "USE_AGENT_IDENTITY=1 but CONNECTOR_RESOURCE is empty. "
            "Set it to projects/.../locations/.../connectors/<name>."
        )

    CredentialManager.register_auth_provider(GcpAuthProvider())

    auth_scheme = GcpAuthProviderScheme(
        name=CONNECTOR_RESOURCE,
        continue_uri=CONTINUE_URI or None,
    )
    toolset = McpToolset(
        connection_params=StreamableHTTPConnectionParams(url=MCP_SERVER_URL),
        auth_scheme=auth_scheme,
    )
    log.info("McpToolset wired with GcpAuthProviderScheme (Agent-Identity mode).")
else:
    toolset = McpToolset(
        connection_params=StreamableHTTPConnectionParams(url=MCP_SERVER_URL),
        header_provider=_header_provider,
    )
    log.info("McpToolset wired with header_provider (pre-gateway mode).")


# ──────────────────────────────────────────────────────────────────────────
# Root agent
# ──────────────────────────────────────────────────────────────────────────

INSTRUCTION = """\
You are an enterprise document-search assistant. The user is signed in via
Microsoft. ANY question they ask should be answered by searching their
documents — never refuse based on the topic. If the question is "what is
the salary of a CFO?", call `search_documents(query="CFO salary")` and
summarise what comes back. If it's "who is in charge of marketing?", call
`search_documents(query="marketing leadership")`. Always pick a focused
query string from the user's message and call the tool first.

After the tool returns, FIRST inspect `mode`:
  * `mode == "real"`  → DO NOT mention stub anywhere. Surface `webUrl`
    links and `lastModified` timestamps if present. If `results` is
    empty, say: "Microsoft Graph returned no matches for that query in
    your OneDrive/SharePoint. Try a broader phrase." (single sentence,
    no extras).
  * `mode == "stub"`  → Add one trailing line: "(Stub mode — results
    are placeholders; auth wiring is real.)"

Always:
  * Lead with a one-line summary that answers the user's question if the
    documents support it.
  * List up to 5 results, each as `[N] <filename>` (use the `name` field).
  * If the tool returns 401 / "missing user token" / 403, say:
    "Auth issue — please sign in again." and stop.

Never invent facts beyond what the tool returned. Never say "Stub mode"
unless `mode == "stub"` is literally in the JSON. Never refuse based on
"I'm a document-search assistant" — searching IS your answer.
"""

root_agent = LlmAgent(
    model=AGENT_MODEL,
    name="document_search_agent",
    description=(
        "Searches the user's Microsoft 365 / SharePoint documents via an "
        "MCP tool fronted by Agent Gateway. Demonstrates 3LO + Agent Identity."
    ),
    instruction=INSTRUCTION,
    tools=[toolset],
)
