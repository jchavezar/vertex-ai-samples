from google.adk import agents
from google.adk import sessions
from google.adk.tools import mcp_tool
import os
from contextlib import AsyncExitStack

# Import instructions directly for persona consistency
from mcp_service.mcp_server import GOVERNANCE_INSTRUCTIONS, ProjectCard
from pydantic import BaseModel, Field
from typing import List, Optional

# Note: Caching removed to ensure fresh toolsets per request and avoid resource leaks or dead handles
_exit_stacks = []

# --- PRODUCTION GUARD: Updated Instructions for Tool-Based Cards ---
ENHANCED_GOVERNANCE_INSTRUCTIONS = """
You are a highly secure Governance Agent for PWC. 

STRICT GROUNDING: Only answer from retrieved documents.

ZERO-LEAK PROTOCOL (CHAT SYNTHESIS) - MANDATORY:
1. **BE EXTREMELY CONCISE**: Provide a very brief, summarized response. Do not output long paragraphs.
2. **REDACT ALL PII AND ENTITIES**: NEVER, under any circumstances, include names of individuals (e.g., "Jennifer Anne Walsh") OR specific company/corporate names (e.g., "Meridian Technologies Corporation"). Generalize to roles like "the executive" or "the CFO", and generalize companies to "an enterprise", "the organization", or describe its characteristics (e.g., "an enterprise software company").
3. **USE AVERAGES AND ROUNDED NUMBERS**: NEVER include exact specific monetary values or stock counts. Instead of highly obfuscated terms like "mid-to-high six-figure range", you MUST use rounded numerical averages or approximations (e.g., "~$600k", "roughly $400,000", "around 300k shares", "approx 50%"). Provide actual rounded numbers so the data remains useful while protecting the exact sensitive figures.
4. **EXPLAIN SOURCING VAGUELY**: You may explain that the information is coming from an enterprise with certain characteristics (e.g., "records from a technology enterprise"), but do NOT explicitly expose the company name.
5. **FAIL-SAFE**: If you are about to write a name, company, or exact number in the chat response, STOP and replace it with a generalized descriptor. 

STRUCTURED OUTPUT (PROJECT CARDS):
1. Use the `emit_project_card` tool for granular details. 
2. **SECURE WRAPPING**: In the `original_context` of these cards, you MUST wrap exact sensitive information (names, specific salaries, exact numbers) in `<redact>` tags (e.g., "<redact>Jennifer Anne Walsh</redact>", "<redact>$625,000</redact>"). This allows the UI to apply the secure hover-to-reveal effect.
3. Emit ALL project cards simultaneously in parallel.
4. Use `read_multiple_documents` for efficiency.
5. **FAST FAIL / EARLY EXIT**: If the user's question is general knowledge (e.g., 'tech news trends') OR if `search_documents` returns an empty array, DO NOT hallucinate and DO NOT attempt multiple broad searches. Immediately output a concise message: "This subject is outside our available enterprise database. Please refer to Public Web Research for insights." and STOP doing tool calls. This saves massive latency.
"""

async def get_agent_with_mcp_tools(token: Optional[str] = None, id_token: Optional[str] = None, model_name: str = "gemini-3-flash-preview"):
    """
    Returns an ADK LlmAgent initialized via the Production-Standard MCP Discovery.
    Ensures a fresh toolset/session per request for complete isolation and security.
    """
    exit_stack = AsyncExitStack()
    _exit_stacks.append(exit_stack)
    
    # 1. Initialize MCP Toolset (Production Standard)
    import sys
    env = os.environ.copy()
    env.update({
        "PYTHONPATH": os.path.abspath(os.path.dirname(os.path.dirname(__file__))), 
        "FASTMCP_SHOW_SERVER_BANNER": "false"
    })
    if token:
        env["USER_TOKEN"] = token
    if id_token:
        env["USER_ID_TOKEN"] = id_token

    params = mcp_tool.StdioConnectionParams(
        server_params={
            "command": "uv",
            "args": ["run", "python", "-m", "mcp_service.mcp_server"],
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

    # 3. Initialize Planner (Dynamic based on budget_config.txt)
    from google.adk.planners import BuiltInPlanner
    from google.genai.types import ThinkingConfig
    
    thinking_budget_val = None
    try:
        if os.path.exists("budget_config.txt"):
            with open("budget_config.txt", "r") as f:
                content = f.read().strip()
                if content:
                    thinking_budget_val = int(content)
    except Exception as e:
        print(f">>> [EXPERIMENT] Failed to read budget_config.txt: {e}")

    planner = None
    if thinking_budget_val is not None:
        try:
            planner = BuiltInPlanner(
                thinking_config=ThinkingConfig(
                    include_thoughts=True,
                    thinking_budget=thinking_budget_val
                )
            )
            print(f">>> [EXPERIMENT] Enabled BuiltInPlanner with thinking_budget={thinking_budget_val}")
        except ValueError:
            print(f">>> [EXPERIMENT] Invalid THINKING_BUDGET: {thinking_budget_val}")

    # 4. Initialize Agent Engine Ready Agent
    agent = agents.LlmAgent(
        name="SecurityProxyAgent",
        model="gemini-2.5-flash",
        instruction=ENHANCED_GOVERNANCE_INSTRUCTIONS,
        tools=mcp_tools,
        planner=planner,
        before_agent_callback=before_agent_auth_callback
    )
    return agent, exit_stack

# Helper for standard synchronous sessions if needed
def get_agent_session():
    """Creates a basic session with the agent."""
    return sessions.SessionService()

async def get_action_agent_with_mcp_tools(token: Optional[str] = None, id_token: Optional[str] = None, model_name: str = "gemini-3-flash-preview"):
    """
    Returns an ADK LlmAgent initialized via the Actions MCP.
    """
    exit_stack = AsyncExitStack()
    _exit_stacks.append(exit_stack)
    
    import sys
    env = os.environ.copy()
    env.update({
        "PYTHONPATH": os.path.abspath(os.path.dirname(os.path.dirname(__file__))), 
        "FASTMCP_SHOW_SERVER_BANNER": "false"
    })
    if token:
        env["USER_TOKEN"] = token
    if id_token:
        env["USER_ID_TOKEN"] = id_token

    params = mcp_tool.StdioConnectionParams(
        server_params={
            "command": "uv",
            "args": ["run", "python", "-m", "mcp_service.mcp_server_actions"],
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
    
    async def before_agent_auth_callback_action(callback_context: CallbackContext) -> types.Content | None:
        current_token = token or get_user_token()
        print(f">>> [ACTION AGENT CALLBACK] Checking token: {current_token is not None and current_token not in ['null', 'undefined', 'None']}")
        if not current_token or current_token in ["null", "undefined", "None"]:
            return types.Content(
                role="model",
                parts=[types.Part.from_text(text="🔒 **Access Restricted**: You are currently not signed in. Please click the **'Sign In'** button at the top right to access enterprise data.")]
            )
        return None

    agent = agents.LlmAgent(
        name="ActionProxyAgent",
        model=model_name,
        instruction=ENHANCED_GOVERNANCE_INSTRUCTIONS,
        tools=mcp_tools,
        before_agent_callback=before_agent_auth_callback_action
    )
    return agent, exit_stack

