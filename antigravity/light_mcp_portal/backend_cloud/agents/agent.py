import os
import sys
import logging
from typing import Optional
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, SseConnectionParams
from google.adk.agents.readonly_context import ReadonlyContext

logger = logging.getLogger("servicenow_agent")

def explicit_logger(msg):
    logger.info(f"[MCP LOG] {msg}")

def get_access_token(readonly_context: ReadonlyContext) -> str | None:
    if hasattr(readonly_context, "session") and hasattr(readonly_context.session, "state"):
        session_state = dict(readonly_context.session.state)
        # Attempt to grab the literal token we injected via backend
        token = session_state.get("USER_TOKEN")
        if token and isinstance(token, str) and token.startswith("eyJ"):
            return token
            
    # Fallback for local testing if running agent.py independently
    return os.getenv("USER_TOKEN") or os.getenv("USER_ID_TOKEN")

def mcp_header_provider(readonly_context: ReadonlyContext) -> dict[str, str]:
    token = get_access_token(readonly_context)
    if not token:
        logger.warning("[CRITICAL] No User Token found in context state! ServiceNow Auth may fail.")
        return {}
    return {
        "Authorization": f"Bearer {token.strip()}",
        "Accept": "text/event-stream"
    }

# Check for Remote MCP URL (Cloud Run)
mcp_url = os.environ.get("SERVICENOW_MCP_URL", "https://servicenow-mcp-prod-REDACTED_PROJECT_NUMBER.us-central1.run.app/sse")

logger.info(f"Configuring Remote ServiceNow MCP Connection: {mcp_url}")

# Define the dynamic MCP Toolset
servicenow_toolset = MCPToolset(
    connection_params=SseConnectionParams(
        url=mcp_url,
        timeout=120
    ),
    header_provider=mcp_header_provider,
    errlog=explicit_logger
)

INSTRUCTIONS = """
You are a Super-Intelligence ServiceNow Expert for the Lightweight Portal. 
Your role is to help the user manage tickets and incidents in ServiceNow.

CRITICAL: 
- If the user asks for "all" incidents, use 'list_incidents' or 'query_table' with a reasonable limit (like 50).
- If the tool returns a lot of data, FORMAT IT into a clean Markdown Table. Never return raw JSON.
- If you encounter an error or empty result, explain it gracefully.
- You MUST provide clear confirmation before executing any CREATE or UPDATE actions.
"""

# The exported Agent instance for production deployment
root_agent = LlmAgent(
    name="ServiceNowAgentCloud",
    model="gemini-3-flash-preview",
    instruction=INSTRUCTIONS,
    tools=[servicenow_toolset]
)
