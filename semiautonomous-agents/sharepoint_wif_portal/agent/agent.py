"""
SharePoint WIF Portal - Internal vs External Insight Comparator
ADK Agent for Gemini Enterprise

Compares SharePoint documents (internal) with Google Search (external).
Outputs structured response: internal findings, external findings, synthesis.

Version: 1.2.0
Date: 2026-04-05
Last Fix: WIF provider changed to entra-provider for api:// audience matching

Note: Uses single compare_insights tool to avoid model limitation with
mixed tool types (search tools + function tools not supported together).
"""
import os
import re
import logging
import httpx
import google.auth
from google.auth.transport.requests import Request

from google.adk.agents import Agent
from google.adk.tools import ToolContext

from .discovery_engine import DiscoveryEngineClient

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Configuration from environment (Agent Engine sets CLOUD_ML_PROJECT_ID at runtime)
PROJECT_NUMBER = os.environ.get("PROJECT_NUMBER") or os.environ.get("CLOUD_ML_PROJECT_ID", "")
ENGINE_ID = os.environ.get("ENGINE_ID", "")
WIF_POOL_ID = os.environ.get("WIF_POOL_ID", "")
WIF_PROVIDER_ID = os.environ.get("WIF_PROVIDER_ID", "")
DATA_STORE_ID = os.environ.get("DATA_STORE_ID", "")

# AUTH_ID - can be overridden via env var, or auto-detected from tool_context.state keys
AUTH_ID_OVERRIDE = os.environ.get("AUTH_ID", "")


def _detect_auth_id(tool_context: ToolContext) -> tuple[str | None, str | None]:
    """
    Dynamically detect AUTH_ID from tool_context.state keys.
    Pattern: In Agentspace, tokens are stored as "temp:{auth_id}" keys.
    """
    try:
        state_dict = tool_context.state.to_dict() if hasattr(tool_context.state, 'to_dict') else {}

        # Priority 1: Use AUTH_ID_OVERRIDE if set
        if AUTH_ID_OVERRIDE:
            temp_key = f"temp:{AUTH_ID_OVERRIDE}"
            if temp_key in state_dict:
                return AUTH_ID_OVERRIDE, state_dict[temp_key]
            if AUTH_ID_OVERRIDE in state_dict:
                return AUTH_ID_OVERRIDE, state_dict[AUTH_ID_OVERRIDE]

        # Priority 2: Auto-detect from temp:* keys (Agentspace runtime)
        temp_pattern = re.compile(r'^temp:(.+)$')
        for key in state_dict.keys():
            match = temp_pattern.match(key)
            if match:
                auth_id = match.group(1)
                token = state_dict[key]
                if token and isinstance(token, str) and '.' in token and len(token) > 100:
                    logger.info(f"[AUTH] Auto-detected AUTH_ID: {auth_id}")
                    return auth_id, token

        # Priority 3: Check for common auth key names (local testing)
        for key in ['sharepointauth', 'sharepointauth2', 'msauth', 'entra_token']:
            if key in state_dict:
                token = state_dict[key]
                if token and isinstance(token, str) and len(token) > 100:
                    logger.info(f"[AUTH] Found token via common key: {key}")
                    return key, token

        logger.warning("[AUTH] No token found in state")
        return None, None

    except Exception as e:
        logger.error(f"[AUTH] Error detecting auth: {e}")
        return None, None


async def _search_google(query: str) -> dict:
    """
    Search Google using Gemini with Google Search grounding.
    Called internally by compare_insights.
    """
    try:
        creds, _ = google.auth.default()
        creds.refresh(Request())
        access_token = creds.token
    except Exception as e:
        logger.error(f"[GoogleSearch] Auth error: {e}")
        return {"error": str(e), "answer": "", "sources": []}

    project = PROJECT_NUMBER or os.environ.get("GOOGLE_CLOUD_PROJECT", "")
    # Use gemini-2.5-flash-lite which is available in the project
    url = f"https://aiplatform.googleapis.com/v1/projects/{project}/locations/us-central1/publishers/google/models/gemini-2.5-flash-lite:generateContent"

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(url,
                headers={"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"},
                json={
                    "contents": [{"role": "user", "parts": [{"text": f"Search the web and answer: {query}"}]}],
                    "tools": [{"googleSearch": {}}],
                    "generationConfig": {"maxOutputTokens": 1000, "temperature": 0.7}
                }
            )

            if resp.status_code == 200:
                data = resp.json()
                candidate = data.get("candidates", [{}])[0]

                # Extract text
                parts = candidate.get("content", {}).get("parts", [])
                answer = "".join(p.get("text", "") for p in parts if p.get("text"))

                # Extract sources
                sources = []
                grounding = candidate.get("groundingMetadata", {})
                for chunk in grounding.get("groundingChunks", []):
                    web = chunk.get("web", {})
                    if web.get("uri") and web.get("title"):
                        sources.append({"title": web["title"], "url": web["uri"]})

                return {"answer": answer.strip(), "sources": sources[:5]}
            else:
                logger.error(f"[GoogleSearch] API error: {resp.status_code} - {resp.text[:200]}")
                return {"error": f"API error: {resp.status_code}", "answer": "", "sources": []}

    except Exception as e:
        logger.error(f"[GoogleSearch] Error: {e}")
        return {"error": str(e), "answer": "", "sources": []}


async def compare_insights(query: str, tool_context: ToolContext) -> dict:
    """
    Compare internal SharePoint documents with external Google Search results.

    This tool searches BOTH internal and external sources and returns a
    structured comparison. Use this for any research query where you need
    to understand both internal company knowledge and external context.

    Args:
        query: The research question to investigate

    Returns:
        Structured comparison with:
        - internal_findings: Results from SharePoint (company documents)
        - external_findings: Results from Google Search (public web)
        - Both include answer text and source references
    """
    logger.info(f"[Compare] Query: {query[:80]}...")

    # Get user token for SharePoint ACL
    auth_id, microsoft_jwt = _detect_auth_id(tool_context)
    logger.info(f"[Compare] Auth ID: {auth_id}, Token present: {bool(microsoft_jwt)}, Token length: {len(microsoft_jwt) if microsoft_jwt else 0}")

    # Create Discovery Engine client
    client = DiscoveryEngineClient(
        project_number=PROJECT_NUMBER,
        engine_id=ENGINE_ID,
        wif_pool_id=WIF_POOL_ID,
        wif_provider_id=WIF_PROVIDER_ID,
        data_store_id=DATA_STORE_ID,
    )

    # Search both sources concurrently
    import asyncio

    internal_task = client.search(query, user_token=microsoft_jwt)
    external_task = _search_google(query)

    internal_result, external_result = await asyncio.gather(
        internal_task, external_task, return_exceptions=True
    )

    # Process internal results
    if isinstance(internal_result, Exception):
        internal_findings = {"error": str(internal_result), "answer": "", "sources": []}
    else:
        internal_findings = {
            "answer": internal_result.answer,
            "sources": [{"title": s.title, "url": s.url} for s in internal_result.sources[:5]]
        }

    # Process external results
    if isinstance(external_result, Exception):
        external_findings = {"error": str(external_result), "answer": "", "sources": []}
    else:
        external_findings = external_result

    return {
        "query": query,
        "internal_findings": {
            "source": "SharePoint (Internal Documents)",
            **internal_findings
        },
        "external_findings": {
            "source": "Google Search (Public Web)",
            **external_findings
        }
    }


# Agent definition with single comparison tool
root_agent = Agent(
    name="InsightComparator",
    model="gemini-2.5-flash-lite",
    description="AI Assistant that compares internal SharePoint documents with external web sources",
    instruction="""You are an Insight Comparator Assistant that helps users understand topics by comparing internal company knowledge (SharePoint) with external public information (Google Search).

**YOUR WORKFLOW:**

When the user asks a question:

1. Call `compare_insights` with their query
   - This automatically searches BOTH SharePoint and Google
   - Returns structured results from both sources

2. Present a clear comparison:

## Internal Findings (SharePoint)
[Summarize internal_findings.answer]
- Key points from company documents
- Sources: [List document titles/links from internal_findings.sources]

## External Findings (Web)
[Summarize external_findings.answer]
- Key points from public sources
- Sources: [List website titles/links from external_findings.sources]

## Synthesis
- What aligns between internal and external?
- What's unique to internal documents?
- What external context adds value?
- Recommendations

**IMPORTANT:**
- ALWAYS call compare_insights for every question
- Present findings from BOTH sources clearly labeled
- Never make up information - only use what the tool returns
- If either source has an error, explain what happened
""",
    tools=[compare_insights]
)


__all__ = ["root_agent"]


if __name__ == "__main__":
    print(f"""
=====================================
SharePoint WIF Portal - ADK Agent
Internal vs External Insight Comparator
=====================================
PROJECT_NUMBER:   {PROJECT_NUMBER or 'Auto (CLOUD_ML_PROJECT_ID)'}
ENGINE_ID:        {ENGINE_ID or 'Not set'}
DATA_STORE_ID:    {DATA_STORE_ID or 'Not set'}
WIF_POOL_ID:      {WIF_POOL_ID or 'Not set'}
WIF_PROVIDER_ID:  {WIF_PROVIDER_ID or 'Not set'}
AUTH_ID_OVERRIDE: {AUTH_ID_OVERRIDE or 'Auto-detect'}
=====================================
""")
