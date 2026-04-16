"""
Cortex Retriever — ADK Agent

Searches internal SharePoint documents via Discovery Engine and the public
web via ADK's built-in Google Search. Deployed to Agent Engine, registered
to Gemini Enterprise (Agentspace).
"""
import os
import logging

from google.adk.agents import Agent
from google.adk.tools import ToolContext
from google.adk.tools.google_search_tool import GoogleSearchTool

from .discovery_engine import DiscoveryEngineClient

logger = logging.getLogger(__name__)

PROJECT_NUMBER = os.environ.get("PROJECT_NUMBER") or os.environ.get("CLOUD_ML_PROJECT_ID", "")
ENGINE_ID = os.environ.get("ENGINE_ID", "")
WIF_POOL_ID = os.environ.get("WIF_POOL_ID", "")
WIF_PROVIDER_ID = os.environ.get("WIF_PROVIDER_ID", "")
DATA_STORE_ID = os.environ.get("DATA_STORE_ID", "")


def _detect_auth_id(tool_context: ToolContext) -> tuple[str | None, str | None]:
    """
    Auto-detect Microsoft JWT from tool_context.state.

    Agentspace injects OAuth tokens into session state using the authorization
    ID as the key. The key format varies: bare name, "temp:" prefixed, etc.
    Instead of hardcoding names, we scan all values for JWT signatures.
    """
    try:
        state_dict = tool_context.state.to_dict() if hasattr(tool_context.state, "to_dict") else {}
        logger.info(f"State keys: {list(state_dict.keys())}")

        for key, val in state_dict.items():
            if not isinstance(val, str) or len(val) < 100:
                continue
            if val.startswith("eyJ") and "." in val:
                auth_id = key.removeprefix("temp:")
                logger.info(f"JWT detected in state key: {key}")
                return auth_id, val

        return None, None

    except Exception as e:
        logger.error(f"Auth detection error: {e}")
        return None, None


async def search_sharepoint(query: str, tool_context: ToolContext) -> dict:
    """
    Search internal SharePoint documents via Discovery Engine.

    Uses Microsoft JWT from Agentspace session state, exchanges it via WIF
    for a GCP access token, then calls the streamAssist API. Results are
    ACL-aware — each user only sees documents they have access to.

    Args:
        query: The search query for SharePoint documents

    Returns:
        Search results with answer text and source document references
    """
    auth_id, microsoft_jwt = _detect_auth_id(tool_context)
    logger.info(f"SharePoint search: auth_id={auth_id}, token_present={bool(microsoft_jwt)}")

    client = DiscoveryEngineClient(
        project_number=PROJECT_NUMBER,
        engine_id=ENGINE_ID,
        wif_pool_id=WIF_POOL_ID,
        wif_provider_id=WIF_PROVIDER_ID,
        data_store_id=DATA_STORE_ID,
    )

    result = await client.search(query, user_token=microsoft_jwt)

    return {
        "query": query,
        "answer": result.answer,
        "sources": [{"title": s.title, "url": s.url, "snippet": s.snippet} for s in result.sources[:5]],
    }


google_search_tool = GoogleSearchTool(bypass_multi_tools_limit=True)

root_agent = Agent(
    name="CortexRetriever",
    model="gemini-2.5-flash",
    description="Searches internal SharePoint documents and the public web",
    instruction="""You are Cortex Retriever, an AI assistant with access to internal SharePoint documents and the public web.

**Default behavior: ALWAYS search SharePoint first.** Every user query — no matter how short or vague — should be searched in SharePoint. Users are asking about their internal documents even when the query seems generic (e.g. "who is jennifer" means a person mentioned in internal contracts, not a public figure).

**Tools:**
1. `search_sharepoint` — Search internal SharePoint documents. **Call this for EVERY query.**
2. `google_search` — Search the public web. Only use when the user explicitly asks about external/public information, or when you want to supplement SharePoint results with public context.

**Rules:**
- Never skip `search_sharepoint` — even for short, ambiguous, or seemingly incomplete queries
- If SharePoint returns no results, say so clearly — do not fabricate an answer
- When citing sources, include document titles and links
- If the user asks for a comparison (internal vs external), call both tools
""",
    tools=[search_sharepoint, google_search_tool],
)

__all__ = ["root_agent"]
