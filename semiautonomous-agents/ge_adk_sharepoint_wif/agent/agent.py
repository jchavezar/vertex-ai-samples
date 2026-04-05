"""
GE ADK SharePoint WIF - InsightComparator Agent
Compares internal SharePoint documents with external web sources.
- SharePoint: via Discovery Engine with WIF token exchange
- Web: via Gemini with Google Search grounding
"""
import os
import sys
import logging
import requests

from google.adk.agents import Agent
from google.adk.tools import ToolContext
import google.auth
from google.auth.transport.requests import Request as AuthRequest

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
    # In Agentspace: tokens are at temp:{AUTH_ID} (runtime-injected) in tool_context.state
    # In SDK calls: tokens are at {AUTH_ID} in invocation_context.session.state
    # In local testing: tokens are at {AUTH_ID} in tool_context.state
    microsoft_jwt = None
    temp_key = f"temp:{AUTH_ID}"
    local_key = AUTH_ID

    try:
        # Try temp: key first (Agentspace/Gemini Enterprise runtime)
        microsoft_jwt = tool_context.state.get(temp_key)
        if microsoft_jwt:
            print(f"[TOKEN] Found via tool_context.state['{temp_key}'] (length: {len(microsoft_jwt)})", flush=True)

        # Try local key in tool_context.state (local testing)
        if not microsoft_jwt:
            microsoft_jwt = tool_context.state.get(local_key)
            if microsoft_jwt:
                print(f"[TOKEN] Found via tool_context.state['{local_key}'] (length: {len(microsoft_jwt)})", flush=True)

        # Try session.state from invocation_context (SDK/custom UI calls)
        if not microsoft_jwt and hasattr(tool_context, '_invocation_context'):
            inv_ctx = tool_context._invocation_context
            if hasattr(inv_ctx, 'session') and inv_ctx.session and hasattr(inv_ctx.session, 'state'):
                session_state = inv_ctx.session.state
                if isinstance(session_state, dict):
                    microsoft_jwt = session_state.get(local_key)
                    if microsoft_jwt:
                        print(f"[TOKEN] Found via session.state['{local_key}'] (length: {len(microsoft_jwt)})", flush=True)

        if not microsoft_jwt:
            print(f"[TOKEN] No token found (tried temp_key, local_key, session.state)", flush=True)
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


async def search_web(query: str, tool_context: ToolContext) -> dict:
    """
    Search the public web using Google Search.
    Uses Gemini with Google Search grounding for external information.

    Args:
        query: The search query to find relevant web information

    Returns:
        Search results with answer and source URLs from the web
    """
    logger.info(f"[search_web] Query: {query}")

    try:
        # Get GCP credentials
        creds, _ = google.auth.default()
        creds.refresh(AuthRequest())
        access_token = creds.token

        # Use Gemini with Google Search grounding (global location for Google Search)
        url = f"https://aiplatform.googleapis.com/v1/projects/{PROJECT_NUMBER}/locations/global/publishers/google/models/gemini-2.5-flash:generateContent"

        response = requests.post(url,
            headers={"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"},
            json={
                "contents": [{"role": "user", "parts": [{"text": f"{query}\n\nProvide a concise, factual answer based on current web information."}]}],
                "tools": [{"googleSearch": {}}],
                "generationConfig": {
                    "maxOutputTokens": 800,
                    "temperature": 0.7
                }
            },
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            candidate = data.get("candidates", [{}])[0]

            # Extract text
            parts = candidate.get("content", {}).get("parts", [])
            answer = ""
            for part in parts:
                if part.get("text"):
                    answer += part.get("text", "")

            # Extract Google Search sources
            sources = []
            grounding = candidate.get("groundingMetadata", {})
            for chunk in grounding.get("groundingChunks", []):
                web = chunk.get("web", {})
                if web.get("uri") and web.get("title"):
                    sources.append({
                        "title": web.get("title", ""),
                        "url": web.get("uri", "")
                    })

            return {
                "answer": answer.strip() if answer else "No web results found.",
                "source_count": len(sources),
                "sources": sources[:5]
            }
        else:
            logger.error(f"[search_web] API error: {response.status_code}")
            return {"error": f"Web search failed: {response.status_code}", "answer": "Web search unavailable."}

    except Exception as e:
        logger.error(f"[search_web] Error: {e}")
        return {"error": str(e), "answer": f"Web search error: {e}"}


# Agent definition
root_agent = Agent(
    name="InsightComparator",
    model="gemini-2.5-flash",
    description="AI Agent that compares internal SharePoint documents with external web sources",
    instruction="""You are InsightComparator - an AI agent that provides comprehensive insights by comparing INTERNAL company documents with EXTERNAL web information.

**YOUR WORKFLOW:**
1. ALWAYS call `search_sharepoint` FIRST to find internal company information
2. THEN call `search_web` to find external/public information on the same topic
3. COMPARE and SYNTHESIZE both sources in your response

**RESPONSE FORMAT:**
After gathering both internal and external data, structure your response as:

**Internal Insights (SharePoint):**
[Summary of what you found in company documents]

**External Context (Web):**
[Summary of relevant public information]

**Comparison & Analysis:**
[How internal data compares to external benchmarks/information]

**IMPORTANT RULES:**
- NEVER skip the SharePoint search - internal data comes first
- ALWAYS provide the web search for external context
- Clearly distinguish between internal (confidential) and external (public) sources
- If internal data is sensitive, note that external sources are for context only
- Include source links from both searches

Example:
User: "What is Jennifer's salary?"
1. Call search_sharepoint("Jennifer salary")
2. Call search_web("CFO salary benchmarks 2024")
3. Compare: "Jennifer earns $625K as CFO. Industry benchmark for CFOs is $500-800K..."
""",
    tools=[search_sharepoint, search_web]
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
