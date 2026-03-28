"""
ServiceNow Agent with MCP SSE transport.
Uses thinking_budget=1024 for complex reasoning with tools.
"""
import os
import sys
from typing import Optional
from google.adk.agents import LlmAgent
from google.adk.planners import BuiltInPlanner
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset, SseConnectionParams
from google.adk.agents.readonly_context import ReadonlyContext
from google.genai.types import ThinkingConfig


# MCP Server URL - SSE endpoint
MCP_URL = os.environ.get("SERVICENOW_MCP_URL")


SERVICENOW_INSTRUCTION = """You are a ServiceNow Expert Agent.

Your capabilities:
- Query and search incidents, problems, changes, and service requests
- Create new tickets (always confirm with user first)
- Update ticket status and add comments
- List attachments and catalog items

Guidelines:
1. Format results as clean Markdown tables when listing data
2. ALWAYS confirm before creating or updating tickets
3. If a query returns many results, summarize and offer pagination
4. Handle errors gracefully and explain issues clearly
5. Use the user's ServiceNow permissions (their JWT identity)

Available tools are provided by the ServiceNow MCP server.
When you need to perform an action, use the appropriate tool.
"""


def _get_mcp_header_provider(user_token: Optional[str] = None):
    """
    Create a header provider for MCP requests.
    Provides Cloud Run ID token + User JWT.
    """
    def header_provider(readonly_context: ReadonlyContext) -> dict[str, str]:
        headers = {"Accept": "application/json"}

        # Get MCP base URL for audience
        mcp_url = os.environ.get("SERVICENOW_MCP_URL", "")
        mcp_base_url = mcp_url.rsplit("/", 1)[0] if mcp_url.endswith("/sse") else mcp_url

        # Get Cloud Run ID token at runtime
        try:
            import google.auth.transport.requests
            from google.oauth2 import id_token as gcp_id_token

            request = google.auth.transport.requests.Request()
            cloud_run_token = gcp_id_token.fetch_id_token(request, mcp_base_url)
            headers["Authorization"] = f"Bearer {cloud_run_token}"
        except Exception as e:
            print(f"[ServiceNow Agent] Cloud Run token error: {e}", file=sys.stderr)

        # Get user token from session state or closure
        token = user_token
        if not token and hasattr(readonly_context, "session") and hasattr(readonly_context.session, "state"):
            session_state = dict(readonly_context.session.state)
            token = session_state.get("USER_TOKEN")

        if token and isinstance(token, str) and token.startswith("eyJ"):
            headers["X-User-Token"] = token

        return headers

    return header_provider


def create_servicenow_agent(
    user_token: Optional[str] = None,
    model: str = "gemini-2.5-flash",
) -> LlmAgent:
    """
    Create a ServiceNow agent with MCP tools.

    Args:
        user_token: Optional user JWT for ServiceNow auth
        model: Model to use (default: gemini-2.5-flash)

    Returns:
        Configured LlmAgent
    """
    mcp_url = os.environ.get("SERVICENOW_MCP_URL")
    if not mcp_url:
        raise ValueError("SERVICENOW_MCP_URL environment variable is required")

    # Create MCP toolset with SSE transport
    mcp_toolset = McpToolset(
        connection_params=SseConnectionParams(
            url=mcp_url,
            timeout=120,
        ),
        header_provider=_get_mcp_header_provider(user_token),
        errlog=lambda msg: print(f"[MCP Error] {msg}", file=sys.stderr),
    )

    # Create agent with optimized planner
    agent = LlmAgent(
        name="ServiceNowAgent",
        model=model,
        instruction=SERVICENOW_INSTRUCTION,
        description="Handles ServiceNow tickets, incidents, problems, and IT service requests",
        tools=[mcp_toolset],
        planner=BuiltInPlanner(
            thinking_config=ThinkingConfig(
                include_thoughts=True,
                thinking_budget=1024  # Optimized for tool reasoning
            )
        )
    )

    return agent


# Singleton instance for reuse
_servicenow_agent: Optional[LlmAgent] = None


def get_servicenow_agent(user_token: Optional[str] = None) -> LlmAgent:
    """Get or create the ServiceNow agent singleton."""
    global _servicenow_agent
    if _servicenow_agent is None:
        _servicenow_agent = create_servicenow_agent(user_token)
    return _servicenow_agent
