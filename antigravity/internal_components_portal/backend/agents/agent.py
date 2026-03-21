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

OPERATIONAL DIRECTIVES:
1. **TOOL USAGE IS MANDATORY**: You MUST invoke the `search_documents` tool for EVERY query without exception. Even if you believe the query is "general knowledge," you must confirm that PWC does not have a specific internal stance or policy. 
2. **NO PRE-EMPTIVE REFUSAL**: Do NOT refuse to answer or state that you cannot find information until AFTER you have executed `search_documents`.
3. **GROUNDING & FALLBACK**:
   - If `search_documents` returns results: Use them as your primary source to answer. Do NOT state you found no documents if results are returned.
   - If `search_documents` returns NO results: 
     a) Do NOT call `emit_project_card` with `document_id="N/A"` or generic placeholders. Only emit cards for actual documents found.
     b) Provide the answer using your internal knowledge (public consensus), but explicitly state: "I found no specific internal documents for this query. Based on general industry consensus..."
4. **STRICT DATA PRIVACY & MASKING**:
   - **Entity Masking**: You MUST MASK/GENERALIZE all specific company names, client names, individual names, and proprietary identifiers found in search results (e.g., use "Company A", "A Technology Firm", "The Client") in the final response and summaries. Do NOT leak original names.
   - **Numerical Fuzzing**: Fuzz all exact numbers into ranges (e.g., "$100k - $150k" instead of "$125,000").
   - **Redaction Tags**: Use `<redact>` tags ONLY in the `original_context` field of project cards if preserving original text with redactions.
5. **PARALLEL EMISSION**: Emit all valid project cards in a single turn for maximum performance.
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
    elif token:
        env["USER_ID_TOKEN"] = token

    uv_path = "/usr/local/google/home/jesusarguelles/.local/bin/uv"
    if not os.path.exists(uv_path):
        import shutil
        uv_path = shutil.which("uv") or "uv"

    params = mcp_tool.StdioConnectionParams(
        server_params={
            "command": uv_path,
            "args": ["run", "python", "-m", "mcp_service.mcp_server"],
            "env": env
        }
    )
    
    toolset = mcp_tool.McpToolset(connection_params=params)
    exit_stack.push_async_callback(toolset.close)
    try:
        mcp_tools = await toolset.get_tools()
        print(f">>> [MCP DISCOVERY] Successfully retrieved {len(mcp_tools)} tools.")
    except Exception as e:
        print(f">>> [MCP DISCOVERY] CRITICAL FAILURE: {str(e)}")
        import traceback
        traceback.print_exc()
        raise e

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

    # 3. Initialize Planner (Optimized for gemini-2.5-flash)
    from google.adk.planners import BuiltInPlanner
    from google.genai.types import ThinkingConfig
    
    # HARDCODED OPTIMIZATION: 1024 budget showed ~40% latency improvement in testing.
    planner = BuiltInPlanner(
        thinking_config=ThinkingConfig(
            include_thoughts=True,
            thinking_budget=1024
        )
    )
    print(">>> [PRODUCTION] Enabled BuiltInPlanner with optimized thinking_budget=1024")

    # 4. Initialize Agent Engine Ready Agent
    agent = agents.LlmAgent(
        name="SecurityProxyAgent",
        model=model_name,
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

    uv_path = "/usr/local/google/home/jesusarguelles/.local/bin/uv"
    if not os.path.exists(uv_path):
        import shutil
        uv_path = shutil.which("uv") or "uv"

    params = mcp_tool.StdioConnectionParams(
        server_params={
            "command": uv_path,
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

async def get_servicenow_agent_with_mcp_tools(token: Optional[str] = None, id_token: Optional[str] = None, model_name: str = "gemini-3-flash-preview", enable_google_search: bool = False):
    """
    Returns an ADK LlmAgent initialized via the ServiceNow MCP.
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
    elif token:
        env["USER_ID_TOKEN"] = token
    
    uv_path = "/usr/local/google/home/jesusarguelles/.local/bin/uv"
    if not os.path.exists(uv_path):
        import shutil
        uv_path = shutil.which("uv") or "uv"

    params = mcp_tool.StdioConnectionParams(
        server_params={
            "command": uv_path,
            "args": ["run", "python", "-m", "servicenow_mcp.mcp_server_servicenow"],
            "env": env
        }
    )
    
    toolset = mcp_tool.McpToolset(connection_params=params)
    exit_stack.push_async_callback(toolset.close)
    mcp_tools = await toolset.get_tools()

    from google.adk.tools import google_search

    if enable_google_search:
        SERVICENOW_INSTRUCTIONS = """
    You are a highly secure ServiceNow Agent for PWC. 
    Your role is to help the user manage tickets and incidents in ServiceNow.
    You MUST provide clear confirmation before executing any CREATE or UPDATE actions.
    You also have the `google_search` tool. Use it freely to gather precise technical information from the internet to enrich, validate, or generate content for tickets when specific details are requested but missing in your context.
    If there is missing information required to create or update an incident, you MUST explicitly ask the user to fulfill it with their own knowledge, or offer to "make it up" (i.e., generate a plausible technical placeholder) if they prefer.
    If the user asks you to create a ticket based on internet knowledge, use `google_search` first.
    You can also search through and query existing incidents if requested by the user.
    """
        agent_tools = mcp_tools + [google_search]
    else:
        SERVICENOW_INSTRUCTIONS = """
    You are a highly secure ServiceNow Agent for PWC. 
    Your role is to help the user manage tickets and incidents in ServiceNow.
    You MUST provide clear confirmation before executing any CREATE or UPDATE actions.
    """
        agent_tools = mcp_tools

    agent = agents.LlmAgent(
        name="ServiceNowProxyAgent",
        model=model_name,
        instruction=SERVICENOW_INSTRUCTIONS,
        tools=agent_tools
    )
    return agent, exit_stack




from typing import AsyncGenerator
from typing_extensions import override
from google.adk.agents import BaseAgent, LlmAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event
from pydantic import BaseModel, Field

class IntentClassification(BaseModel):
    intent: str = Field(description="The intent of the user. Must be one of: 'SERVICENOW', 'SEARCH', 'ACTION', 'CANCEL'")

class DeloitteRouterAgent(BaseAgent):
    """
    Stateful Router Agent orchestrating ServiceNow and Search using ADK 2.0
    """
    servicenow_agent: LlmAgent
    classifier_agent: LlmAgent
    model_config = {"arbitrary_types_allowed": True}

    def __init__(self, name: str, servicenow_agent: LlmAgent, model_name: str = "gemini-3-flash-preview"):
        classifier_agent = LlmAgent(
            name="IntentClassifier",
            model=model_name,
            instruction="""You are a routing classifier. Evaluate the user's latest message and reply ONLY with the intent.
Available Intents:
- 'SERVICENOW': The user mentions ServiceNow, tickets, incidents, or asks to create/update them.
- 'SEARCH': The user asks for documents, public web search, or general questions.
- 'ACTION': The user asks to perform a general action.
- 'CANCEL': The user asks to cancel, stop, or exit the current flow.""",
            output_schema=IntentClassification,
            output_key="detected_intent"
        )
        super().__init__(
            name=name,
            servicenow_agent=servicenow_agent,
            classifier_agent=classifier_agent,
            sub_agents=[servicenow_agent, classifier_agent]
        )

    @override
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        # 1. Check current route
        current_route = ctx.session.state.get("current_route")

        # 2. Before simply routing, let's run the classifier to see if it's a CANCEL or hard switch
        # Actually, for speed, in ADK 2.0 we can just check if we are in a route. 
        # If in a route, we assume they want to continue UNLESS they say "cancel"
        
        # We will use the intent classifier first
        async for event in self.classifier_agent.run_async(ctx):
            pass # We don't yield the classifier's internal thoughts to the UI

        intent_result = ctx.session.state.get("detected_intent")
        intent = intent_result.intent if intent_result else "SEARCH"

        if intent == "CANCEL":
            ctx.session.state["current_route"] = None
            from google.genai import types
            yield Event(author="router", content=types.Content(role="model", parts=[types.Part.from_text(text="Workflow cancelled. Returning to main menu.")]))
            return

        # Explicit route shifts
        if intent == "SERVICENOW":
            ctx.session.state["current_route"] = "SERVICENOW"
        elif intent == "SEARCH" and not current_route:
            # If they just ask general questions, keep route empty
            pass 

        active_route = ctx.session.state.get("current_route")

        if active_route == "SERVICENOW":
            async for event in self.servicenow_agent.run_async(ctx):
                yield event
        else:
            # For simplicity, if not servicenow, we yield a special event so main.py knows to fallback to normal search
            from google.genai import types
            yield Event(author="router", content=types.Content(role="model", parts=[types.Part.from_text(text="[SYSTEM_FALLBACK_SEARCH]")]))
