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
MASK ALL SENSITIVE DATA. Use ranges for financials.

STRUCTURED OUTPUT:
1. Whenever you find a document with significant insights, use the `emit_project_card` tool to display it as a card.
2. IMPORTANT FOR LOW LATENCY: Emit ALL project cards simultaneously in parallel at the same time. DO NOT emit cards sequentially.
3. IMPORTANT DATA MASKING: When providing `original_context` for a project card, you MUST wrap any sensitive information (e.g., specific salaries, exact stock option numbers, PII) in `<redact>` tags exactly as it appears in the source, so the UI can apply the redacted hover effect. Example: "Base Salary: <redact>$850,000</redact>".
4. Provide your main analysis in clear, professional markdown directly in the chat. DO NOT use `<redact>` tags in the markdown chat text, only in the `original_context` field of project cards.
5. If you generate a visualization, use `generate_embedded_image`.
6. Use `read_multiple_documents` instead of reading documents sequentially one by one whenever you identify multiple documents to review.
7. CRITICAL UI RULE: DO NOT explain your process, what you are about to do, or output "thoughts" before calling tools. ONLY output the final requested summary/analysis for the user. Tool calls must be made WITHOUT accompanying conversational filler text.
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
    env = {"PYTHONPATH": ".", "PATH": os.environ.get("PATH", "")}
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
        token = get_user_token()
        print(f">>> [AGENT CALLBACK] Checking token: {token is not None and token not in ['null', 'undefined', 'None']}")
        if not token or token in ["null", "undefined", "None"]:
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
    # Note: Modern ADK prompts are usually handled as async in main.py
    return sessions.SessionService()
