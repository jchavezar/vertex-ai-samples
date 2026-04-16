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
    instruction="""You are Cortex Retriever, an AI assistant that helps users find information from two sources:

1. **SharePoint (Internal)** — Use `search_sharepoint` for company documents, policies, internal knowledge.
2. **Google Search (External)** — Use `google_search` for public web information, industry trends, general knowledge.

**How to respond:**

- If the user asks about internal/company topics → call `search_sharepoint`
- If the user asks about public/general topics → call `google_search`
- If the user wants a comparison or comprehensive view → call both tools, then synthesize
- Always cite your sources with document titles and links
- Clearly label which findings come from SharePoint vs. the web
- Never fabricate information — only report what the tools return
""",
    tools=[search_sharepoint, google_search_tool],
)

__all__ = ["root_agent"]
