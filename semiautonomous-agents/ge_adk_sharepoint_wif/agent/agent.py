"""
GE ADK SharePoint WIF - Main Agent
Accesses SharePoint via Discovery Engine with WIF token exchange.
Token is received from Gemini Enterprise via tool_context.state["temp:{AUTH_ID}"]
"""
import os
import sys
import logging

from google.adk.agents import Agent
from google.adk.tools import ToolContext

from .discovery_engine import DiscoveryEngineClient

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Configuration
AUTH_ID = os.environ.get("AUTH_ID", "sharepointauth2")
PROJECT_NUMBER = os.environ.get("PROJECT_NUMBER", "")
ENGINE_ID = os.environ.get("ENGINE_ID", "")
WIF_POOL_ID = os.environ.get("WIF_POOL_ID", "")
WIF_PROVIDER_ID = os.environ.get("WIF_PROVIDER_ID", "")


async def search_sharepoint(query: str, tool_context: ToolContext) -> dict:
    """
    Search SharePoint documents using Discovery Engine.
    Uses Microsoft JWT from Agentspace, exchanges via WIF for GCP token.

    Args:
        query: The search query to find relevant documents

    Returns:
        Search results with answer and source documents from SharePoint
    """
    logger.info(f"[search_sharepoint] Query: {query}")

    # Debug: Print all context for troubleshooting (print is captured by Cloud Logging)
    print("=" * 50, flush=True)
    print("[CONTEXT DEBUG] Tool Context Details:", flush=True)
    print(f"  tool_context type: {type(tool_context)}", flush=True)

    # Log state contents
    try:
        state_dict = tool_context.state.to_dict() if hasattr(tool_context.state, 'to_dict') else {}
        print(f"  state keys: {list(state_dict.keys())}", flush=True)
        for key, val in state_dict.items():
            val_preview = str(val)[:100] + "..." if len(str(val)) > 100 else str(val)
            print(f"    {key}: {val_preview}", flush=True)
    except Exception as e:
        print(f"  state access error: {e}", flush=True)

    # Log other context attributes
    for attr in ['user_id', 'session_id', 'app_name', 'function_call_id']:
        if hasattr(tool_context, attr):
            print(f"  {attr}: {getattr(tool_context, attr, 'N/A')}", flush=True)

    # Log invocation context if available
    if hasattr(tool_context, '_invocation_context'):
        inv_ctx = tool_context._invocation_context
        print(f"  invocation_context.app_name: {getattr(inv_ctx, 'app_name', 'N/A')}", flush=True)
        print(f"  invocation_context.user_id: {getattr(inv_ctx, 'user_id', 'N/A')}", flush=True)
        if hasattr(inv_ctx, 'session') and inv_ctx.session:
            print(f"  session.state: {inv_ctx.session.state}", flush=True)

    print("=" * 50, flush=True)

    # Extract Microsoft JWT from session state
    # In Agentspace: tokens are at temp:{AUTH_ID} (runtime-injected)
    # In local testing: tokens are at {AUTH_ID} (stored in session state)
    microsoft_jwt = None
    temp_key = f"temp:{AUTH_ID}"
    local_key = AUTH_ID

    try:
        # Try temp: key first (Agentspace runtime)
        microsoft_jwt = tool_context.state.get(temp_key)
        if microsoft_jwt:
            print(f"[TOKEN] Found via '{temp_key}' (length: {len(microsoft_jwt)})", flush=True)
        else:
            # Try local key (local testing)
            microsoft_jwt = tool_context.state.get(local_key)
            if microsoft_jwt:
                print(f"[TOKEN] Found via '{local_key}' (length: {len(microsoft_jwt)})", flush=True)

        if not microsoft_jwt:
            print(f"[TOKEN] No token found (tried '{temp_key}' and '{local_key}')", flush=True)
            print("[TOKEN] Using service account fallback", flush=True)

    except Exception as e:
        logger.error(f"Error extracting token: {e}")

    # Create Discovery Engine client
    client = DiscoveryEngineClient(
        project_number=PROJECT_NUMBER,
        engine_id=ENGINE_ID,
        wif_pool_id=WIF_POOL_ID,
        wif_provider_id=WIF_PROVIDER_ID,
    )

    try:
        result = await client.search(query, user_token=microsoft_jwt)

        response = {
            "answer": result.answer,
            "source_count": len(result.sources),
        }

        if result.sources:
            response["sources"] = [
                {"title": s.title, "url": s.url}
                for s in result.sources[:5]
            ]

        return response

    except Exception as e:
        logger.error(f"[search_sharepoint] Error: {e}")
        return {"error": str(e), "answer": f"Search error: {e}"}


# Agent definition
root_agent = Agent(
    name="SharePointAssistant",
    model="gemini-2.5-flash-lite",
    description="AI Assistant with access to SharePoint documents via Discovery Engine",
    instruction="""You are a SharePoint Document Assistant.

**CRITICAL RULE: For EVERY user question, you MUST call the search_sharepoint tool FIRST.**

Do NOT respond directly. Do NOT try to answer from general knowledge.
ALWAYS call `search_sharepoint` with the user's question as the query.

After receiving the search results:
1. Present the answer from the search results
2. Include source document titles and links
3. If no results found, say so - do NOT make up information

Example:
User: "What is the CEO salary?"
You: [Call search_sharepoint with query="What is the CEO salary?"]
Then: Present the results from the tool.
""",
    tools=[search_sharepoint]
)


__all__ = ["root_agent"]


if __name__ == "__main__":
    print(f"""
=====================================
GE ADK SharePoint WIF Agent
=====================================
AUTH_ID:        {AUTH_ID}
PROJECT_NUMBER: {PROJECT_NUMBER or 'Not set'}
ENGINE_ID:      {ENGINE_ID or 'Not set'}
WIF_POOL_ID:    {WIF_POOL_ID or 'Not set'}
WIF_PROVIDER_ID: {WIF_PROVIDER_ID or 'Not set'}
=====================================
""")
