import os
import logging
from typing import Optional
from contextlib import AsyncExitStack
from google.adk.agents import LlmAgent
from google.adk.tools import mcp_tool

logger = logging.getLogger("servicenow_agent")

# We keep a global list of exit stacks to close them on shutdown if needed, 
# but for Agent Engine deployment, we usually don't need this as much as in a long-running server.
_exit_stacks = []

async def get_servicenow_agent_with_mcp_tools(model_name: str = "gemini-3-flash-preview") -> tuple[LlmAgent, AsyncExitStack]:
    """
    Returns an ADK LlmAgent initialized via the ServiceNow MCP.
    Connects to the ServiceNow MCP server (either via Sse if URL is provided, or fallback to local stdio).
    """
    exit_stack = AsyncExitStack()
    _exit_stacks.append(exit_stack)
    
    # Check for Remote MCP URL (Cloud Run)
    mcp_url = os.environ.get("SERVICENOW_MCP_URL")
    
    if mcp_url:
        logger.info(f"Connecting to Remote ServiceNow MCP: {mcp_url}")
        params = mcp_tool.SseConnectionParams(url=mcp_url)
    else:
        logger.warning("SERVICENOW_MCP_URL is NOT set. Attempting local stdio fallback.")
        script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "servicenow_mcp", "mcp_server_servicenow.py"))
        uv_path = os.environ.get("UV_PATH", "uv")
        params = mcp_tool.StdioConnectionParams(
            server_params={
                "command": uv_path,
                "args": ["run", "python", script_path],
                "env": os.environ.copy()
            }
        )
    
    try:
        toolset = mcp_tool.McpToolset(connection_params=params)
        exit_stack.push_async_callback(toolset.close)
        mcp_tools = await toolset.get_tools()
    except Exception as e:
        logger.error(f"Failed to load MCP tools: {e}")
        mcp_tools = [] # Fallback to no tools if it fails, or we can raise depending on strictness.

    INSTRUCTIONS = """
    You are a Secure ServiceNow Agent for the Lightweight Portal. 
    Your role is to help the user manage tickets and incidents in ServiceNow.
    You MUST provide clear confirmation before executing any CREATE or UPDATE actions.
    If you are missing information to create a ticket (like description or short_description), clarify with the user.
    """

    agent = LlmAgent(
        name="ServiceNowAgent",
        model=model_name,
        instruction=INSTRUCTIONS,
        tools=mcp_tools
    )
    
    return agent, exit_stack
