"""
ServiceNow Agent for Agent Engine deployment.
Uses SSE transport with header_provider for JWT token flow.
"""
import os
import sys
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset, SseConnectionParams
from google.adk.agents.readonly_context import ReadonlyContext

# MCP Server URL - SSE endpoint
# Set via environment variable - no default to avoid hardcoded URLs
MCP_URL = os.environ.get("SERVICENOW_MCP_URL")
if not MCP_URL:
    raise ValueError("SERVICENOW_MCP_URL environment variable is required")

print(f"[Agent Init] MCP_URL = {MCP_URL}")
MCP_BASE_URL = MCP_URL.rsplit("/", 1)[0] if MCP_URL.endswith("/sse") else MCP_URL


def explicit_logger(msg: str):
    """Explicit logger for MCP errors."""
    print(f"[MCP Error] {msg}", file=sys.stderr)


def get_user_token(readonly_context: ReadonlyContext) -> str | None:
    """Extract USER_TOKEN from session state."""
    if hasattr(readonly_context, "session") and hasattr(readonly_context.session, "state"):
        session_state = dict(readonly_context.session.state)
        token = session_state.get("USER_TOKEN")
        if token and isinstance(token, str) and token.startswith("eyJ"):
            return token
    return os.getenv("USER_TOKEN") or os.getenv("USER_ID_TOKEN")


def mcp_header_provider(readonly_context: ReadonlyContext) -> dict[str, str]:
    """
    Provides ALL headers for MCP requests:
    - Authorization: Cloud Run ID token (runtime-generated)
    - X-User-Token: User's JWT for ServiceNow
    """
    headers = {"Accept": "application/json"}

    # Get Cloud Run ID token at runtime
    try:
        import google.auth.transport.requests
        from google.oauth2 import id_token

        request = google.auth.transport.requests.Request()
        cloud_run_token = id_token.fetch_id_token(request, MCP_BASE_URL)
        headers["Authorization"] = f"Bearer {cloud_run_token}"
        print(f"[header_provider] Got runtime Cloud Run token", file=sys.stderr)
    except Exception as e:
        print(f"[header_provider] Cloud Run token error: {e}", file=sys.stderr)

    # Get user token for ServiceNow
    user_token = get_user_token(readonly_context)
    if user_token:
        headers["X-User-Token"] = user_token
        print(f"[header_provider] Added user token", file=sys.stderr)

    return headers


# Agent instructions
INSTRUCTIONS = """
You are a ServiceNow Expert Agent for the Light MCP Portal.

Your capabilities:
- Query and search incidents, problems, changes, and service requests
- Create new tickets (with user confirmation)
- Update ticket status and add comments
- List attachments and catalog items

Important guidelines:
1. When listing data, format results as clean Markdown tables
2. Always confirm before creating or updating tickets
3. If a query returns many results, summarize and offer pagination
4. Handle errors gracefully and explain issues to the user
5. Use the user's ServiceNow permissions (their JWT identity)

Available tools are provided by the ServiceNow MCP server.
"""

# Export the agent for deployment
root_agent = LlmAgent(
    name="ServiceNowAgentCloud",
    model="gemini-2.5-flash",
    instruction=INSTRUCTIONS,
    tools=[
        McpToolset(
            connection_params=SseConnectionParams(
                url=MCP_URL,
                timeout=120,
            ),
            header_provider=mcp_header_provider,
            errlog=explicit_logger,
        )
    ]
)

if __name__ == "__main__":
    print(f"Agent configured with MCP URL: {MCP_URL}")
