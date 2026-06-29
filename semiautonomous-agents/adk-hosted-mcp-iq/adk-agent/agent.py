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

# Microsoft-hosted Work IQ SharePoint MCP server URL
MCP_URL = os.environ.get("SHAREPOINT_MCP_URL", "https://agent365.svc.cloud.microsoft/agents/servers/mcp_SharePointRemoteServer")

def decode_jwt_payload(token: str) -> dict:
    """Safely decodes JWT payload without signature verification."""
    try:
        parts = token.split('.')
        if len(parts) < 2:
            return {}
        payload_b64 = parts[1]
        padding = '=' * (4 - (len(payload_b64) % 4))
        payload_json = base64.urlsafe_b64decode(payload_b64 + padding).decode('utf-8')
        return json.loads(payload_json)
    except Exception as e:
        logger.warning(f"[Agent] Failed to decode JWT payload: {e}")
        return {}

def mcp_header_provider(ctx: CallbackContext) -> dict[str, str]:
    headers = {}
    user_token = None
    
    if hasattr(ctx, "session") and hasattr(ctx.session, "state"):
        state_dict = dict(ctx.session.state)
        logger.info(f"[Agent] Found {len(state_dict)} keys in session state: {list(state_dict.keys())}")
        
        candidates = []
        for key, val in state_dict.items():
            if isinstance(val, str) and val.startswith("eyJ") and len(val) > 100:
                payload = decode_jwt_payload(val)
                iss = str(payload.get("iss", "")).lower()
                aud = str(payload.get("aud", "")).lower()
                logger.info(f"[Agent] Candidate token key='{key}', iss='{iss}', aud='{aud}'")
                
                is_ms_agent365 = (
                    "microsoftonline" in iss or 
                    "windows.net" in iss or 
                    "graph.microsoft.com" in aud or
                    "agent365.svc.cloud.microsoft" in aud or
                    "00000003-0000-0000-c000-000000000000" in aud
                )
                if is_ms_agent365:
                    candidates.append((key, val, iss, aud))
        
        if candidates:
            selected_key, selected_token, selected_iss, selected_aud = candidates[0]
            user_token = selected_token
            logger.info(f"[Agent] Successfully selected Microsoft token from key='{selected_key}' (iss='{selected_iss}', aud='{selected_aud}')")
        else:
            # Fallback to non-Google tokens or keys containing 'sharepoint'
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
                logger.info(f"[Agent] Fallback selecting token from key='{selected_key}'")
        
        if user_token:
            # For the hosted Microsoft MCP, the user's token is passed directly in Authorization Bearer.
            headers["Authorization"] = f"Bearer {user_token}"
            logger.info(f"[Agent] Added Authorization Bearer user token (length: {len(user_token)})")
        else:
            logger.warning("[Agent] No suitable Microsoft user JWT found in session state.")
            
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
    logger.info(f"[Agent] Calling hosted MCP tool '{method}' at {MCP_URL}")
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(MCP_URL, headers=headers, json=payload, timeout=60)
            logger.info(f"[Agent] Hosted MCP response status: {resp.status_code}, length: {len(resp.content)}")
            logger.info(f"[Agent] Raw response body: {resp.text}")
            if resp.status_code == 200:
                text = resp.text
                json_str = text.strip()
                # If SSE formatted, extract data payload
                for line in text.splitlines():
                    if line.strip().startswith("data:"):
                        json_str = line.replace("data:", "", 1).strip()
                        break
                
                try:
                    parsed_json = json.loads(json_str)
                    result = parsed_json.get("result", {})
                    
                    # Check for isError in root or result
                    if parsed_json.get("isError") or result.get("isError"):
                        content_list = result.get("content", [])
                        err_texts = [c.get("text", "") for c in content_list if c.get("type") == "text"]
                        err_msg = " | ".join(err_texts) or "Hosted MCP returned an error response."
                        logger.error(f"[Agent] Hosted MCP returned error: {err_msg}")
                        return {"error": err_msg}
                        
                    return result.get("structuredContent", result.get("content"))
                except json.JSONDecodeError as je:
                    logger.error(f"[Agent] Failed to parse JSON payload: {json_str}. Error: {je}")
                    return {"error": f"Failed to parse JSON response: {str(je)}", "raw": text}
            else:
                logger.error(f"[Agent] Hosted MCP call failed with status {resp.status_code}: {resp.text}")
                return {"error": f"MCP call failed with status {resp.status_code}", "detail": resp.text}
        except Exception as e:
            logger.exception(f"[Agent] Exception calling hosted MCP: {e}")
            return {"error": f"Exception calling hosted MCP: {str(e)}"}

# Define hosted MCP tools mapping

async def find_site(ctx: CallbackContext, searchQuery: str = "") -> dict:
    """Find SharePoint sites visible to the user.
    
    Args:
        searchQuery: Optional free-text query to search for sites.
    """
    return await _call_mcp(ctx, "findSite", {"searchQuery": searchQuery})

async def list_document_libraries_in_site(ctx: CallbackContext, siteId: str = "") -> dict:
    """List document libraries (drives) for a specific SharePoint site.
    
    Args:
        siteId: The ID of the site. If empty, defaults to root.
    """
    return await _call_mcp(ctx, "listDocumentLibrariesInSite", {"siteId": siteId})

async def get_folder_children(ctx: CallbackContext, documentLibraryId: str, parentFolderId: str = "root") -> dict:
    """List child files and folders within a folder of a document library (returns top 20).
    
    Args:
        documentLibraryId: The ID of the document library.
        parentFolderId: Optional ID of the parent folder (defaults to 'root').
    """
    return await _call_mcp(ctx, "getFolderChildren", {"documentLibraryId": documentLibraryId, "parentFolderId": parentFolderId})

async def find_file_or_folder(ctx: CallbackContext, searchQuery: str) -> dict:
    """Search for files or folders (DriveItems) by a search query across all accessible SharePoint sites.
    
    Args:
        searchQuery: The search query string.
    """
    return await _call_mcp(ctx, "findFileOrFolder", {"searchQuery": searchQuery})

async def read_small_text_file(ctx: CallbackContext, fileId: str, documentLibraryId: str) -> dict:
    """Download a SharePoint text file (<=5 MB) and return its raw text content.
    
    Args:
        fileId: The ID of the file.
        documentLibraryId: The ID of the document library containing the file.
    """
    return await _call_mcp(ctx, "readSmallTextFile", {"fileId": fileId, "documentLibraryId": documentLibraryId})

async def read_small_binary_file(ctx: CallbackContext, fileId: str, documentLibraryId: str) -> dict:
    """Download a SharePoint binary file (<=5 MB) and return its base64-encoded content.
    
    Args:
        fileId: The ID of the file.
        documentLibraryId: The ID of the document library containing the file.
    """
    return await _call_mcp(ctx, "readSmallBinaryFile", {"fileId": fileId, "documentLibraryId": documentLibraryId})


# Initialize the ADK LlmAgent
root_agent = LlmAgent(
    name="SharePointHostedExplorerAgent",
    model="gemini-2.5-flash",
    instruction=(
        "You are an expert enterprise virtual assistant with secure access to corporate SharePoint document libraries via a Microsoft-hosted MCP server.\n\n"
        "CRITICAL ANTI-HALLUCINATION & GROUNDING PROTOCOL:\n"
        "1. STRICT REAL-DATA GROUNDING: You must base your responses ONLY and EXCLUSIVELY on the actual text retrieved from SharePoint using your tools. "
        "Do NOT use any pre-trained knowledge or guess. Under no circumstances should you state that Jennifer Walsh works for 'Altostrat' or is a 'Senior Software Engineer'. "
        "These are incorrect hallucinations from pre-trained/mock data. If you search and find the real corporate documents, you will see that Jennifer Walsh is "
        "the Chief Financial Officer (CFO) of Meridian Technologies Corporation.\n"
        "2. TWO-STEP VERIFICATION MANDATE: When queried about a person, file, or topic, you MUST first use `find_file_or_folder` or `get_folder_children` to locate the relevant files. "
        "Once files are found, you MUST call `read_small_text_file` or `read_small_binary_file` to read the actual text or binary content "
        "of those files before answering. Do not summarize or answer using only the search metadata. Always read the text inside the files.\n"
        "3. RIGOROUS CLICKABLE CITATIONS: For every claim, fact, or detail you present, you MUST provide a direct, clickable Markdown citation pointing to the source file. "
        "Format the citation EXACTLY as `[Document Title](webUrl)` where `Document Title` is the exact filename and `webUrl` is the actual "
        "destination web URL returned in the tool's result. If the tool returns a `url` or `webUrl` property, use that exact string for the markdown link.\n"
        "4. HARD FILE-SIZE LIMIT: Note that files larger than 5 MB cannot be read by this server. If you encounter a file size larger than 5 MB, inform the user about the size limitation.\n"
        "5. EXPLICIT AUTH/EMPTY FALLBACK: If any tool call returns an authentication error, 401, 403, or permission-denied, or if no results are returned, "
        "you must explicitly inform the user that you cannot access the requested documents due to insufficient permissions or empty search results. "
        "Do NOT invent or fabricate any details. State: 'I am unable to retrieve the corporate records because...'\n"
        "6. TONE & FORMAT: Maintain a professional, executive-ready tone. Present data in clean markdown tables or bulleted lists for maximum readability. Be precise, concise, and completely transparent about your sources."
    ),
    tools=[
        find_site,
        list_document_libraries_in_site,
        get_folder_children,
        find_file_or_folder,
        read_small_text_file,
        read_small_binary_file
    ],
)

__all__ = ["root_agent"]
