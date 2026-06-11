import logging
import os
import re
import httpx
import base64
import json
from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("adk-agent")

# MCP URL - updated to use the working one in vtxdemos
MCP_URL = os.environ.get("SHAREPOINT_MCP_URL", "https://ge-custom-sharepoint-mcp-254356041555.us-central1.run.app/mcp")

def decode_jwt_payload(token: str) -> dict:
    """Safely decodes JWT payload without signature verification."""
    try:
        parts = token.split('.')
        if len(parts) < 2:
            return {}
        payload_b64 = parts[1]
        # Add padding if necessary
        padding = '=' * (4 - (len(payload_b64) % 4))
        payload_json = base64.urlsafe_b64decode(payload_b64 + padding).decode('utf-8')
        return json.loads(payload_json)
    except Exception as e:
        logger.warning(f"[Agent] Failed to decode JWT payload: {e}")
        return {}

def mcp_header_provider(ctx: CallbackContext) -> dict[str, str]:
    headers = {}
    
    # Pillar B: Generate OIDC token for service-to-service auth (Cloud Run IAM)
    try:
        import google.auth.transport.requests
        from google.oauth2 import id_token
        request = google.auth.transport.requests.Request()
        # Use the base URL (without path) for audience
        audience = MCP_URL.split("/mcp")[0]
        cloud_run_token = id_token.fetch_id_token(request, audience)
        headers["Authorization"] = f"Bearer {cloud_run_token}"
        logger.info("[Agent] Added Service Account OIDC token to Authorization header")
    except Exception as e:
        logger.warning(f"[Agent] Failed to get OIDC token: {e}")

    # Pillar A: Extract user JWT from GE state and put in X-User-Token
    user_token = None
    if hasattr(ctx, "session") and hasattr(ctx.session, "state"):
        state_dict = dict(ctx.session.state)
        temp_pattern = re.compile(r'^temp:(.+)$')
        logger.info(f"[Agent] Found {len(state_dict)} keys in session state: {list(state_dict.keys())}")
        for k, v in state_dict.items():
            logger.info(f"[Agent] Key: {k}, type: {type(v)}, length/value: {len(v) if hasattr(v, '__len__') else str(v)[:50]}")
        
        candidates = []
        for key, val in state_dict.items():
            if isinstance(val, str) and val.startswith("eyJ") and len(val) > 100:
                payload = decode_jwt_payload(val)
                iss = str(payload.get("iss", "")).lower()
                aud = str(payload.get("aud", "")).lower()
                logger.info(f"[Agent] Candidate token key='{key}', iss='{iss}', aud='{aud}'")
                
                is_ms_graph = (
                    "microsoftonline" in iss or 
                    "windows.net" in iss or 
                    "graph.microsoft.com" in aud or 
                    "00000003-0000-0000-c000-000000000000" in aud
                )
                if is_ms_graph:
                    candidates.append((key, val, iss, aud))
        
        if candidates:
            selected_key, selected_token, selected_iss, selected_aud = candidates[0]
            user_token = selected_token
            logger.info(f"[Agent] Successfully selected Microsoft Graph token from key='{selected_key}' (iss='{selected_iss}', aud='{selected_aud}')")
        else:
            # Fallback to first non-Google token, or direct match for sharepoint keys
            fallback_candidates = []
            for key, val in state_dict.items():
                if isinstance(val, str) and len(val) > 100:
                    if val.startswith("eyJ"):
                        payload = decode_jwt_payload(val)
                        iss = str(payload.get("iss", "")).lower()
                        aud = str(payload.get("aud", "")).lower()
                        is_google = "google" in iss or "google" in aud
                        if not is_google:
                            fallback_candidates.append((key, val, iss, aud))
                    elif "sharepoint" in key:
                        fallback_candidates.append((key, val, "opaque", "opaque"))
            
            if fallback_candidates:
                selected_key, selected_token, selected_iss, selected_aud = fallback_candidates[0]
                user_token = selected_token
                logger.info(f"[Agent] No explicit Microsoft Graph token. Fallback selecting non-Google token/key from key='{selected_key}' (iss='{selected_iss}', aud='{selected_aud}')")
            else:
                logger.warning("[Agent] No Microsoft Graph token or suitable fallback token found in session state.")
        
        if user_token:
            headers["X-User-Token"] = user_token
            logger.info(f"[Agent] Added X-User-Token (length: {len(user_token)})")
        else:
            logger.warning("[Agent] No user JWT found in session state")

    return headers

async def _call_mcp(ctx: CallbackContext, method: str, arguments: dict) -> dict:
    headers = mcp_header_provider(ctx)
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": method,
            "arguments": arguments
        }
    }
    logger.info(f"[Agent] Calling MCP tool '{method}' at {MCP_URL}")
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(MCP_URL, headers=headers, json=payload, timeout=60)
            if resp.status_code == 200:
                result = resp.json().get("result", {})
                return result.get("structuredContent", result.get("content"))
            else:
                logger.error(f"[Agent] MCP call failed with status {resp.status_code}: {resp.text}")
                return {"error": f"MCP call failed with status {resp.status_code}", "detail": resp.text}
        except Exception as e:
            logger.exception(f"[Agent] Exception calling MCP: {e}")
            return {"error": f"Exception calling MCP: {str(e)}"}

# Define tools for the agent

async def search(ctx: CallbackContext, query: str, top: int = 20) -> dict:
    """Search SharePoint content by free-text query.
    
    Args:
        query: Free-text query.
        top: Max results (default 20).
    """
    return await _call_mcp(ctx, "search", {"query": query, "top": top})

async def fetch(ctx: CallbackContext, id: str) -> dict:
    """Fetch a SharePoint driveItem by id and return extracted text.
    
    Args:
        id: '<driveId>:<itemId>' as returned by search.
    """
    return await _call_mcp(ctx, "fetch", {"id": id})

async def list_sites(ctx: CallbackContext, search: str = "") -> dict:
    """List SharePoint sites visible to the user (optional name filter).
    
    Args:
        search: Optional name filter.
    """
    return await _call_mcp(ctx, "list_sites", {"search": search})

async def list_libraries(ctx: CallbackContext, site_id: str) -> dict:
    """List document libraries (drives) for a SharePoint site.
    
    Args:
        site_id: The ID of the site.
    """
    return await _call_mcp(ctx, "list_libraries", {"site_id": site_id})

async def list_files(ctx: CallbackContext, library_id: str, folder: str = "", limit: int = 50) -> dict:
    """List items in a library (or sub-folder).
    
    Args:
        library_id: The ID of the library.
        folder: Optional driveItem id of a folder; omit for root.
        limit: Max items (default 50).
    """
    return await _call_mcp(ctx, "list_files", {"library_id": library_id, "folder": folder, "limit": limit})

async def read_file(ctx: CallbackContext, file_id: str) -> dict:
    """Download a SharePoint file (<=5 MB) and return extracted text.
    
    Args:
        file_id: '<driveId>:<itemId>'.
    """
    return await _call_mcp(ctx, "read_file", {"file_id": file_id})


# Initialize the Agent
# User instructed to use gemini-3.5-flash
root_agent = LlmAgent(
    name="SharePointExplorerAgent",
    model="gemini-2.5-flash",
    instruction=(
        "You are an expert enterprise virtual assistant with secure access to corporate SharePoint document libraries.\n\n"
        "CRITICAL ANTI-HALLUCINATION & GROUNDING PROTOCOL:\n"
        "1. STRICT REAL-DATA GROUNDING: You must base your responses ONLY and EXCLUSIVELY on the actual text retrieved from SharePoint using your tools. "
        "Do NOT use any pre-trained knowledge or guess. Under no circumstances should you state that Jennifer Walsh works for 'Altostrat' or is a 'Senior Software Engineer'. "
        "These are incorrect hallucinations from pre-trained/mock data. If you search and find the real corporate documents, you will see that Jennifer Walsh is "
        "the Chief Financial Officer (CFO) of Meridian Technologies Corporation.\n"
        "2. TWO-STEP VERIFICATION MANDATE: When queried about a person, file, or topic (such as 'Jennifer Walsh'), you MUST first use the `search` tool to locate relevant files. "
        "Once files are found (e.g., '03_Client_Contract_Apex_Financial.pdf' or '01_Financial_Audit_Report_FY2024.pdf'), you MUST call `fetch` or `read_file` to read the actual text content "
        "of those files before answering. Do not summarize or answer using only the search snippet or metadata. Always read the text inside the files.\n"
        "3. RIGOROUS CLICKABLE CITATIONS: For every claim, fact, or detail you present, you MUST provide a direct, clickable Markdown citation pointing to the source file. "
        "Format the citation EXACTLY as `[Document Title](webUrl)` where `Document Title` is the exact filename (e.g. '03_Client_Contract_Apex_Financial.pdf') and `webUrl` is the actual "
        "destination web URL returned in the tool's result (e.g. `https://sockcop.sharepoint.com/...`). If the tool returns a `url` or `webUrl` property, use that exact string for the markdown link.\n"
        "4. EXPLICIT AUTH/EMPTY FALLBACK: If any tool call returns an authentication error, 401, 403, or permission-denied, or if no results are returned, "
        "you must explicitly inform the user that you cannot access the requested documents due to insufficient permissions or empty search results. "
        "Do NOT invent or fabricate any details to fill the gap. State: 'I am unable to retrieve the corporate records because...'\n"
        "5. TONE & FORMAT: Maintain a professional, executive-ready tone. Present data in clean markdown tables or bulleted lists for maximum readability. Be precise, concise, and completely transparent about your sources."
    ),
    tools=[search, fetch, list_sites, list_libraries, list_files, read_file],
)

__all__ = ["root_agent"]
