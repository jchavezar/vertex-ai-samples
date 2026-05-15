from google.adk import agents
from google.adk import sessions
from google.adk.tools import mcp_tool
import asyncio
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

==== HARD SEARCH BUDGET (latency control) ====
A. You may call `search_documents` AT MOST 2 times per user query. Pick your two best query phrasings up front; do not iterate after that.
B. If both searches return empty OR contain no documents whose name/summary clearly relates to the user's question, STOP searching. Respond in plain text:
   "No documents in the secure index match this query." Do NOT browse folders, do NOT read documents, do NOT emit cards.
C. Do NOT call `browse_sharepoint_folder` unless the user explicitly asks to list or navigate folders. It is a fallback, not a discovery tool.

==== RELEVANCE GATE FOR READS AND CARDS ====
D. Before reading a document, verify the document's name OR summary contains at least one substantive keyword from the user's query (ignore stopwords). If none match, SKIP that document.
E. **CARD RULE**: A `emit_project_card` call is ONLY permitted when the document's content directly answers the user's question. NEVER emit a card for a document that is merely "in the same repository" or "tangentially related." If you cannot defend the card with a one-sentence "this document answers the question because…", do not emit it.
F. If no document passes the relevance gate, emit ZERO cards and say so explicitly in the synthesis.

==== CROSS-SITE READS ====
G. `search_documents` returns hits from ANY SharePoint site you have access to (not just one configured drive). Each hit includes a `driveId` field. When calling `read_document_content`, ALWAYS pass that hit's `driveId` along with `item_id` so the read works regardless of which site the document lives in. Do NOT use `read_multiple_documents` for cross-site batches — call `read_document_content` per item with its own `driveId`.

==== STRUCTURED OUTPUT ====
1. Whenever a document genuinely answers the user, use `emit_project_card` to surface it.
2. Emit ALL relevant project cards in parallel in a single turn. Do NOT emit them sequentially.
3. **DATA MASKING**: In `original_context`, wrap sensitive PII / financials / specific numbers in `<redact>...</redact>` tags exactly as they appear. Example: "Base Salary: <redact>$850,000</redact>".
4. The chat synthesis text must be a high-level, generalized answer. Do NOT lift specific names or un-redacted figures into the chat text — use descriptive ranges or concepts.
5. If you generate a visualization, use `generate_embedded_image`.
6. When reading multiple relevant documents, use `read_multiple_documents` ONCE rather than `read_document_content` per file.
7. **NO FILLER**: Do not narrate your tool plan ("Now I will search…"). Call tools silently. Only output the final synthesis as user-facing text.
8. **SYNTHESIS RULE**: Ground the synthesis STRICTLY in documents that passed the relevance gate. If retrieval returned nothing relevant, say so honestly — do NOT pad with public-knowledge speculation.
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
    # Inherit parent env so SITE_ID, DRIVE_ID, GOOGLE_*, MS_GRAPH_REGION, etc.
    # reach the MCP subprocess (otherwise SharePointMCP sees None/None).
    env = {**os.environ, "PYTHONPATH": "."}
    if token:
        env["USER_TOKEN"] = token

    params = mcp_tool.StdioConnectionParams(
        server_params={
            "command": "python",
            "args": ["-m", "mcp_service.mcp_server"],
            "env": env
        },
        # Default is 5s — too tight for FastMCP's startup (incl. its pypi
        # version-check call) on a cold container. Bump to 30s.
        timeout=30.0,
    )
    
    toolset = mcp_tool.McpToolset(connection_params=params)
    exit_stack.push_async_callback(toolset.close)

    # Cold-start retry: ADK's MCP session creation has a hard 5s timeout, and
    # FastMCP's startup (incl. its pypi version-check call) can blow past it
    # on a brand-new container. The first attempt warms the subprocess; the
    # second almost always succeeds. Without this, users see a one-time
    # "Discovery Error" that is actually a timeout, not a real failure.
    last_err = None
    mcp_tools = None
    for attempt in range(3):
        try:
            mcp_tools = await toolset.get_tools()
            if attempt > 0:
                print(f">>> [MCP DISCOVERY] Recovered on retry attempt {attempt + 1}")
            break
        except Exception as e:
            last_err = e
            print(f">>> [MCP DISCOVERY] Attempt {attempt + 1} failed: {e}")
            await asyncio.sleep(1.5)
    if mcp_tools is None:
        raise last_err or RuntimeError("MCP discovery failed after retries")

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
