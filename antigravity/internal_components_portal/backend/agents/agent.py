from google.adk import agents
from google.adk import sessions
from google.adk.tools import mcp_tool
import os
from contextlib import AsyncExitStack

# Import instructions directly for persona consistency
from mcp_service.mcp_server import GOVERNANCE_INSTRUCTIONS, ProjectCard
from pydantic import BaseModel, Field
from typing import List, Optional

# Global cache to persist MCP server process and eliminate per-request start latency
_agent_cache = {}
_exit_stacks = []

# --- PRODUCTION GUARD: Updated Instructions for Tool-Based Cards ---
ENHANCED_GOVERNANCE_INSTRUCTIONS = """
You are a highly secure Governance Agent for PWC. 

STRICT GROUNDING: Only answer from retrieved documents.

ZERO-LEAK PROTOCOL (CHAT SYNTHESIS) - MANDATORY:
1. **REDACT ALL PII**: NEVER, under any circumstances, include names of individuals (e.g., "Jennifer Anne Walsh"), specific dates, or granular identifiers in the chat response. Generalize to roles like "the executive", "the incumbent", or "the CFO".
2. **REDACT ALL EXACT FIGURES**: NEVER include specific monetary values (e.g., "$625,000"), exact stock counts, or precise percentages. You MUST use broad buckets or qualitative descriptions (e.g., "compensation in the mid-to-high six-figure range", "standard bonus structure", "significant equity allocation").
3. **FAIL-SAFE**: If you are about to write a name or an exact number, STOP and replace it with a generalized descriptor. 

STRUCTURED OUTPUT (PROJECT CARDS):
1. Use the `emit_project_card` tool for granular details. 
2. **SECURE WRAPPING**: In the `original_context` of these cards, you MUST wrap exact sensitive information (names, specific salaries, exact numbers) in `<redact>` tags (e.g., "<redact>Jennifer Anne Walsh</redact>", "<redact>$625,000</redact>"). This allows the UI to apply the secure hover-to-reveal effect.
3. Emit ALL project cards simultaneously in parallel.
4. If you generate a visualization, use `generate_embedded_image`.
5. Use `read_multiple_documents` for efficiency.
"""

async def get_agent_with_mcp_tools(token: Optional[str] = None, model_name: str = "gemini-3-flash-preview"):
    """
    Returns an ADK LlmAgent initialized via the Production-Standard MCP Discovery.
    Caches the MCP server connection per token to eliminate startup latency.
    """
    cache_key = f"{token or 'default'}_{model_name}"
    if cache_key in _agent_cache:
        print(f">>> [MCP CACHE] Returning cached agent for token (First 5 chars): {cache_key[:5]}")
        return _agent_cache[cache_key], None

    exit_stack = AsyncExitStack()
    _exit_stacks.append(exit_stack)
    
    # 1. Initialize MCP Toolset (Production Standard)
    env = {"PYTHONPATH": ".", "PATH": os.environ.get("PATH", ""), "FASTMCP_SHOW_SERVER_BANNER": "false"}
    if token:
        env["USER_TOKEN"] = token

    params = mcp_tool.StdioConnectionParams(
        server_params={
            "command": "python",
            "args": ["-m", "mcp_service.mcp_server"],
            "env": env
        }
    )
    
    toolset = mcp_tool.McpToolset(connection_params=params)
    exit_stack.push_async_callback(toolset.close)
    mcp_tools = await toolset.get_tools()

    # --- PRODUCTION GUARD: Authentication Interceptor ---
    def create_guarded_tool(tool_item, original_func):
        async def auth_guarded_run(*args, **kwargs):
            from utils.auth_context import get_user_token
            current_token = get_user_token()
            print(f">>> [AUTH GUARD] Tool '{tool_item.name}' called. Token present: {current_token is not None}")
            if not current_token or current_token in ["null", "undefined", "None"]:
                return "AUTH_REQUIRED: The user is NOT signed in. Secure Enterprise search cannot proceed. Please prompt the user to click the 'Sign In' button at the top right of the application interface."
            return await original_func(*args, **kwargs)
        return auth_guarded_run

    for tool in mcp_tools:
        tool.run_async = create_guarded_tool(tool, tool.run_async)

    # --- PRODUCTION GUARD: Agent-Level Authentication Callback ---
    from google.adk.agents.callback_context import CallbackContext
    from google.genai import types
    from utils.auth_context import get_user_token
    
    async def before_agent_auth_callback(callback_context: CallbackContext) -> types.Content | None:
        # Use the token passed to the outer function directly to capture it in this scope
        current_token = token or get_user_token()
        print(f">>> [AGENT CALLBACK] Checking token (auth callback): {current_token is not None and current_token not in ['null', 'undefined', 'None']}")
        if not current_token or current_token in ["null", "undefined", "None"]:
            return types.Content(
                role="model",
                parts=[types.Part.from_text(text="🔒 **Access Restricted**: You are currently not signed in. Please click the **'Sign In'** button at the top right to access enterprise data.")]
            )
        return None

    # 3. Initialize Agent Engine Ready Agent (Removed output_schema for better streaming)
    agent = agents.LlmAgent(
        name="SecurityProxyAgent",
        model=model_name,
        instruction=ENHANCED_GOVERNANCE_INSTRUCTIONS,
        tools=mcp_tools,
        before_agent_callback=before_agent_auth_callback
    )
    
    _agent_cache[cache_key] = agent
    return agent, None

# Helper for standard synchronous sessions if needed
def get_agent_session():
    """Creates a basic session with the agent."""
    return sessions.SessionService()

async def get_action_agent_with_mcp_tools(token: Optional[str] = None, model_name: str = "gemini-3-flash-preview"):
    """
    Returns an ADK LlmAgent initialized via the Actions MCP.
    """
    cache_key = f"action_{token or 'default'}_{model_name}"
    if cache_key in _agent_cache:
        print(f">>> [MCP CACHE] Returning cached action agent")
        return _agent_cache[cache_key], None

    exit_stack = AsyncExitStack()
    _exit_stacks.append(exit_stack)
    
    env = {"PYTHONPATH": ".", "PATH": os.environ.get("PATH", ""), "FASTMCP_SHOW_SERVER_BANNER": "false"}
    if token:
        env["USER_TOKEN"] = token

    params = mcp_tool.StdioConnectionParams(
        server_params={
            "command": "python",
            "args": ["-m", "mcp_service.mcp_server_actions"],
            "env": env
        }
    )
    
    toolset = mcp_tool.McpToolset(connection_params=params)
    exit_stack.push_async_callback(toolset.close)
    mcp_tools = await toolset.get_tools()

    agent = agents.LlmAgent(
        name="ActionProxyAgent",
        model=model_name,
        instruction="You are an Action Agent. You modify and generate files using tools. Use provided tools.",
        tools=mcp_tools
    )
    
    _agent_cache[cache_key] = agent
    return agent, None

