"""
Light MCP Cloud Portal - Main Agent Entry Point.
Uses LlmAgent with Discovery Engine and ServiceNow MCP tools.
"""
import os
import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Ensure imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from google.adk.agents import LlmAgent
from google.adk.agents.readonly_context import ReadonlyContext
from google.adk.tools.tool_context import ToolContext
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset, SseConnectionParams
from google.adk.tools.base_toolset import BaseToolset

from tools.discovery_engine import DiscoveryEngineClient


# Environment configuration
MCP_URL = os.environ.get("SERVICENOW_MCP_URL")
MCP_BASE_URL = MCP_URL.rsplit("/", 1)[0] if MCP_URL else None  # Remove /sse for audience
DATA_STORE_ID = os.environ.get("DATA_STORE_ID")

if MCP_URL:
    logger.info(f"[Agent] ServiceNow MCP URL: {MCP_URL}")
if DATA_STORE_ID:
    logger.info(f"[Agent] Discovery Engine Data Store: {DATA_STORE_ID}")


# ============= Discovery Engine Tool =============
async def search_sharepoint(query: str, tool_context: ToolContext) -> dict:
    """
    Search SharePoint documents using Discovery Engine.

    ALWAYS use this tool first for any question about company information,
    documents, reports, policies, salaries, financial data, or any factual question.

    Args:
        query: The search query to find relevant documents

    Returns:
        Search results with answer and source documents from SharePoint
    """
    logger.info(f"[search_sharepoint] Searching: {query}")

    try:
        # Get user token from session state for WIF authentication
        user_token = None
        if tool_context:
            # Debug: log available state keys
            state_keys = list(tool_context.state.keys()) if hasattr(tool_context.state, 'keys') else []
            print(f"[search_sharepoint] State keys: {state_keys}", flush=True)

            # Access state directly - ADK ToolContext.state is dict-like
            user_token = tool_context.state.get("USER_TOKEN")

            if user_token:
                print(f"[search_sharepoint] Got USER_TOKEN (length: {len(user_token)})", flush=True)
            else:
                # Fallback: check session.state
                if hasattr(tool_context, 'session') and tool_context.session:
                    session_state = tool_context.session.state
                    if hasattr(session_state, 'get'):
                        user_token = session_state.get("USER_TOKEN")
                        if user_token:
                            print(f"[search_sharepoint] Got USER_TOKEN from session.state (length: {len(user_token)})", flush=True)

            if not user_token:
                print("[search_sharepoint] No USER_TOKEN found - using service account", flush=True)
        else:
            print("[search_sharepoint] No tool_context - using service account", flush=True)

        client = DiscoveryEngineClient()
        result = await client.search(query, user_token=user_token)

        response = {
            "answer": result.answer,
            "source_count": len(result.sources),
        }

        # Include sources if found
        if result.sources:
            response["sources"] = [
                {"title": s.title, "url": s.url}
                for s in result.sources[:5]
            ]

        return response

    except Exception as e:
        logger.error(f"[search_sharepoint] Error: {e}")
        return {"error": str(e), "answer": f"Search error: {e}"}


# ============= ServiceNow MCP Header Provider =============
def mcp_header_provider(readonly_context: ReadonlyContext) -> dict[str, str]:
    """
    Provide headers for MCP server connection.
    - Authorization: Cloud Run ID token (service-to-service auth)
    - X-User-Token: User's Entra ID JWT (for ServiceNow identity)
    """
    headers = {}

    # Get Cloud Run ID token at runtime for service auth
    if MCP_BASE_URL:
        try:
            import google.auth.transport.requests
            from google.oauth2 import id_token
            request = google.auth.transport.requests.Request()
            cloud_run_token = id_token.fetch_id_token(request, MCP_BASE_URL)
            headers["Authorization"] = f"Bearer {cloud_run_token}"
            logger.info("[MCP] Got Cloud Run ID token")
        except Exception as e:
            logger.warning(f"[MCP] Cloud Run token error: {e}")

    # Pass user JWT via X-User-Token header
    if hasattr(readonly_context, "session") and hasattr(readonly_context.session, "state"):
        session_state = dict(readonly_context.session.state)
        user_token = session_state.get("USER_TOKEN")
        if user_token and user_token.startswith("eyJ"):
            headers["X-User-Token"] = user_token
            logger.info(f"[MCP] Added X-User-Token (length: {len(user_token)})")
        else:
            logger.info("[MCP] No USER_TOKEN in session state")
    else:
        logger.info("[MCP] No session state available")

    return headers


# ============= Lazy MCP Toolset =============
class LazyMcpToolset(BaseToolset):
    """
    Lazy wrapper for McpToolset that creates the toolset at runtime.
    This avoids pickle serialization issues during Agent Engine deployment.
    """
    def __init__(self, url: str, header_provider):
        super().__init__()
        self._url = url
        self._header_provider = header_provider
        self._toolset = None

    def _get_toolset(self):
        if self._toolset is None:
            logger.info(f"[LazyMCP] Creating McpToolset for {self._url}")
            self._toolset = McpToolset(
                connection_params=SseConnectionParams(url=self._url, timeout=120),
                header_provider=self._header_provider,
                errlog=lambda msg: logger.info(f"[MCP] {msg}"),
            )
        return self._toolset

    async def get_tools(self, readonly_context=None):
        return await self._get_toolset().get_tools(readonly_context)

    def __getstate__(self):
        # Only pickle the URL and header_provider, not the toolset
        return {"_url": self._url, "_header_provider": self._header_provider, "_toolset": None}

    def __setstate__(self, state):
        self.__init__(state["_url"], state["_header_provider"])


# ============= Build Tools List =============
def get_tools():
    """Build the tools list."""
    tools = [search_sharepoint]

    # Add ServiceNow MCP toolset if configured (lazy initialization)
    if MCP_URL:
        servicenow_toolset = LazyMcpToolset(
            url=MCP_URL,
            header_provider=mcp_header_provider,
        )
        tools.append(servicenow_toolset)
        logger.info("[Agent] Added LazyMcpToolset for ServiceNow")

    return tools


# ============= Agent Instruction =============
AGENT_INSTRUCTION = """You are a Cloud Portal Assistant with access to two systems:

1. **SharePoint Document Search** (search_sharepoint tool)
   - Use this tool for ANY question about company information
   - This searches internal documents: reports, policies, contracts, financial data
   - ALWAYS try this tool first for factual questions

2. **ServiceNow IT Support** (MCP tools)
   - list_incidents: Show open IT tickets
   - create_incident: Create a new IT support ticket
   - get_incident: Get details of a specific ticket
   - search_knowledge: Search the knowledge base
   - get_user_info: Get user profile information

**CRITICAL INSTRUCTIONS:**
- For ANY question about salaries, financial data, reports, policies, or company information:
  ALWAYS use search_sharepoint FIRST before responding
- Do NOT make up information - if you don't find it in search, say so
- Include source links when presenting search results
- For IT issues: use the ServiceNow tools to create or check tickets

**Examples of when to search:**
- "What is the CFO's salary?" -> search_sharepoint("CFO salary compensation")
- "Show me the audit report" -> search_sharepoint("audit report")
- "What are the Q3 earnings?" -> search_sharepoint("Q3 earnings financial")
- "Find information about X" -> search_sharepoint("X")
"""


# Create the root agent
root_agent = LlmAgent(
    name="CloudPortalAssistant",
    model="gemini-2.5-flash",
    instruction=AGENT_INSTRUCTION,
    tools=get_tools(),
)


# Export for Agent Engine
__all__ = ["root_agent"]


if __name__ == "__main__":
    print(f"""
=====================================
Light MCP Cloud Portal - LlmAgent
=====================================
ServiceNow MCP: {MCP_URL or 'Not configured'}
Data Store ID:  {DATA_STORE_ID or 'Not configured'}
=====================================

Tools:
- search_sharepoint: Discovery Engine / SharePoint
- servicenow_*: ServiceNow MCP (if configured)

Test locally:
    uv run python test_local.py "what is the CFO salary?"
""")
