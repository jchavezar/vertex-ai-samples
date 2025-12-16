import asyncio
import contextvars
import os
import uuid
import uvicorn
import requests
from fastapi import FastAPI, Request, Response, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from mcp.server import Server
from mcp.server.sse import SseServerTransport
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource
from atlassian import Jira

import logging

# --- 0. Logging Setup ---
# Use stdout for Cloud Run/Container environments
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# --- 1. Global Context for Multi-Tenancy ---
user_token_var = contextvars.ContextVar("user_token", default=None)

# --- 2. Middleware to Capture Token ---
class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1].strip()
            user_token_var.set(token)
            logger.debug(f"Captured Token: {token[:10]}...")
        else:
            user_token_var.set(None)
            logger.debug("No Token found in headers")

        response = await call_next(request)
        return response

# --- 3. Setup App & Server ---
app = FastAPI(title="Jira Multi-Tenant MCP")
app.add_middleware(AuthMiddleware)

mcp_server = Server("jira-multi-tenant")

# Store active transports: session_id -> SseServerTransport
sessions = {}

# --- 4. Helpers & Tools ---
def get_atlassian_resources(token: str):
    resp = requests.get(
        "https://api.atlassian.com/oauth/token/accessible-resources",
        headers={"Authorization": f"Bearer {token}"}
    )
    resp.raise_for_status()
    return resp.json()

def get_jira_client() -> Jira:
    token = user_token_var.get()
    if not token:
        raise ValueError("Authentication required. Please provide a Bearer token.")

    try:
        sites = get_atlassian_resources(token)
        if not sites:
            raise ValueError("No Jira sites found for this user.")

        # Default to the first site
        cloud_id = sites[0]['id']
        api_url = f"https://api.atlassian.com/ex/jira/{cloud_id}"

        return Jira(url=api_url, token=token, cloud=True)
    except Exception as e:
        raise ValueError(f"Jira Connection Error: {str(e)}")

@mcp_server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="atlassianUserInfo",
            description="Get current user info from Atlassian",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="getAccessibleAtlassianResources",
            description="Get cloudid to construct API calls to Atlassian REST APIs",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="getJiraIssue",
            description="Get the details of a Jira issue by issue id or key.",
            inputSchema={
                "type": "object",
                "properties": {
                    "issueIdOrKey": {"type": "string", "description": "Issue id or key"}
                },
                "required": ["issueIdOrKey"]
            }
        ),
        Tool(
            name="getJiraIssueRemoteIssueLinks",
            description="Get remote issue links (eg: Confluence links etc...) of an existing Jira issue id or key",
            inputSchema={
                "type": "object",
                "properties": {
                    "issueIdOrKey": {"type": "string", "description": "Issue id or key"}
                },
                "required": ["issueIdOrKey"]
            }
        ),
        Tool(
            name="getVisibleJiraProjects",
            description="Get visible Jira projects.",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="lookupJiraAccountId",
            description="Lookup account ids of existing users in Jira based on the user's display name or email address.",
            inputSchema={
                "type": "object",
                "properties": {
                    "searchString": {"type": "string", "description": "Display name or email"}
                },
                "required": ["searchString"]
            }
        ),
        Tool(
            name="getTransitionsForJiraIssue",
            description="Get available transitions for an existing Jira issue id or key.",
            inputSchema={
                "type": "object",
                "properties": {
                    "issueIdOrKey": {"type": "string", "description": "Issue id or key"}
                },
                "required": ["issueIdOrKey"]
            }
        ),
        Tool(
            name="getJiraProjectIssueTypesMetadata",
            description="Get a page of issue type metadata for a specified project.",
            inputSchema={
                "type": "object",
                "properties": {
                    "projectIdOrKey": {"type": "string", "description": "Project ID or Key"}
                },
                "required": ["projectIdOrKey"]
            }
        ),
        Tool(
            name="getJiraIssueTypeMetaWithFields",
            description="Get issue type metadata for a project and issue type, including fields.",
            inputSchema={
                "type": "object",
                "properties": {
                    "projectIdOrKey": {"type": "string", "description": "Project ID or Key"},
                    "issueTypeId": {"type": "string", "description": "Issue Type ID"}
                },
                "required": ["projectIdOrKey", "issueTypeId"]
            }
        ),
        Tool(
            name="searchJiraIssuesUsingJql",
            description="Search Jira issues using Jira Query Language (JQL). Supports pagination via nextPageToken.",
            inputSchema={
                "type": "object",
                "properties": {
                    "jql": {"type": "string", "description": "A Jira Query Language (JQL) expression"},
                    "maxResults": {"type": "integer", "default": 15, "description": "Maximum number of issues to return per page. Default is 15."},
                    "startAt": {"type": "integer", "default": 0, "description": "Legacy pagination index."},
                    "nextPageToken": {"type": "string", "description": "The token to retrieve the next page of results."}
                },
                "required": ["jql"]
            }
        )
    ]

@mcp_server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent | ImageContent | EmbeddedResource]:
    token = user_token_var.get()

    try:
        # Tools that don't strictly need the Jira client wrapper (or use it differently)
        if name == "getAccessibleAtlassianResources":
            if not token:
                return [TextContent(type="text", text="Authentication required.")]
            resources = get_atlassian_resources(token)
            return [TextContent(type="text", text=str(resources))]

        # For other tools, get the initialized Jira client
        jira = get_jira_client()

        if name == "atlassianUserInfo":
            # Try global Atlassian profile first (often available with basic scopes)
            resp = requests.get(
                "https://api.atlassian.com/me",
                headers={"Authorization": f"Bearer {token}"}
            )
            if resp.status_code == 200:
                return [TextContent(type="text", text=str(resp.json()))]

            # Fallback to Jira-specific profile
            user_info = jira.myself()
            return [TextContent(type="text", text=str(user_info))]

        elif name == "getVisibleJiraProjects":
            projects = jira.projects()
            # Return a summarized list
            summary = [f"{p['key']}: {p['name']} (ID: {p['id']})" for p in projects]
            return [TextContent(type="text", text="\n".join(summary))]

        elif name == "lookupJiraAccountId":
            query = arguments.get("searchString")
            # Use direct API call to avoid library wrapper issues with deprecated params
            users = jira.get("user/search", params={"query": query})

            if isinstance(users, dict):
                return [TextContent(type="text", text=f"Unexpected response: {users}")]

            if not users:
                return [TextContent(type="text", text="No users found.")]

            # If users is a string, it's an error message from the API
            if isinstance(users, str):
                return [TextContent(type="text", text=f"API Error: {users}")]

            summary = []
            for u in users:
                if isinstance(u, dict):
                    summary.append(f"{u.get('displayName', 'Unknown')} (ID: {u.get('accountId', 'Unknown')})")

            return [TextContent(type="text", text="\n".join(summary))]

        elif name == "getTransitionsForJiraIssue":
            key = arguments.get("issueIdOrKey")
            # Direct API call
            data = jira.get(f"issue/{key}/transitions")

            if isinstance(data, str):
                 return [TextContent(type="text", text=f"API Error: {data}")]

            # Expecting {"transitions": [...]}
            transitions = data.get('transitions', []) if isinstance(data, dict) else []

            if not transitions:
                return [TextContent(type="text", text="No transitions available.")]

            summary = [f"{t.get('name', 'Unknown')} (ID: {t.get('id', '?')}) -> {t.get('to', {}).get('name', 'Unknown')}" for t in transitions]
            return [TextContent(type="text", text="\n".join(summary))]

        elif name == "searchJiraIssuesUsingJql":
            jql = arguments.get("jql")
            max_results = arguments.get("maxResults", 15)
            start_at = arguments.get("startAt", 0)
            next_page_token = arguments.get("nextPageToken")
            
            # Use GET /rest/api/3/search/jql (Modern endpoint)
            full_url = f"{jira.url.rstrip('/')}/rest/api/3/search/jql"
            
            params = {
                "jql": jql,
                "maxResults": max_results,
                "fields": "summary,status,created,issuetype,priority,assignee,reporter,updated"
            }
            
            # Use token if available, otherwise fallback to startAt (legacy)
            if next_page_token:
                params["nextPageToken"] = next_page_token
            elif start_at > 0:
                params["startAt"] = start_at
            
            headers = {
                "Authorization": f"Bearer {token}",
                "Accept": "application/json"
            }

            try:
                resp = requests.get(full_url, params=params, headers=headers)
                
                if resp.status_code != 200:
                    logger.error(f"JQL Error {resp.status_code}: {resp.text}")
                    return [TextContent(type="text", text=f"API Error {resp.status_code}: {resp.text}")]
                
                data = resp.json()
                
            except Exception as e:
                logger.error(f"JQL Exception: {e}")
                return [TextContent(type="text", text=f"API Exception: {str(e)}")]

            issues = data.get('issues', [])
            returned_next_token = data.get('nextPageToken')
            
            logger.info(f"DEBUG: JQL Search - Count: {len(issues)}, NextToken: {returned_next_token is not None}")

            if not issues:
                return [TextContent(type="text", text=f"No issues found for JQL: `{jql}`")]

            lines = [f"Showing {len(issues)} issues."]
            
            for i in issues:
                fields = i.get('fields', {})
                status = fields.get('status', {}).get('name', 'Unknown')
                summary = fields.get('summary', 'No Summary')
                created_date_raw = fields.get('created', '')
                created_date = created_date_raw.split('T')[0] if created_date_raw else ""
                lines.append(f"[{i['key']}] {summary} (Status: {status}, Created: {created_date})")

            if returned_next_token:
                lines.append(f"\n[SYSTEM NOTICE: There are more issues available. You MUST ask the user if they want to see the next batch. If they say YES, you MUST call this tool again with `nextPageToken='{returned_next_token}'`.]")
            elif len(issues) == max_results:
                 lines.append(f"\n[SYSTEM NOTICE: There might be more issues. Ask user. If yes, try calling with startAt={start_at + len(issues)} (legacy).]")

            return [TextContent(type="text", text="\n".join(lines))]

        elif name == "getJiraIssue":
            key = arguments.get("issueIdOrKey")
            issue = jira.issue(key)
            return [TextContent(type="text", text=str(issue))]

        elif name == "getJiraIssueRemoteIssueLinks":
            key = arguments.get("issueIdOrKey")
            try:
                links = jira.get_issue_remote_links(key)
            except AttributeError:
                links = jira.get(f"issue/{key}/remotelink")
            return [TextContent(type="text", text=str(links))]

        elif name == "getJiraProjectIssueTypesMetadata":
            key = arguments.get("projectIdOrKey")
            # Use direct API call for createmeta
            meta = jira.get(f"/rest/api/3/issue/createmeta?projectKeys={key}&expand=projects.issuetypes.fields")

            projects = meta.get('projects', [])
            if not projects:
                return [TextContent(type="text", text=f"No metadata found for project {key}")]

            p_data = projects[0]
            issuetypes = p_data.get('issuetypes', [])

            summary = [f"Project: {p_data.get('name')}"]
            for it in issuetypes:
                summary.append(f"- {it.get('name')} (ID: {it.get('id')}) - {it.get('description', 'No desc')}")

            return [TextContent(type="text", text="\n".join(summary))]

        elif name == "getJiraIssueTypeMetaWithFields":
            key = arguments.get("projectIdOrKey")
            type_id = arguments.get("issueTypeId")

            # Use direct API call for createmeta
            meta = jira.get(f"/rest/api/3/issue/createmeta?projectKeys={key}&issueTypeIds={type_id}&expand=projects.issuetypes.fields")

            projects = meta.get('projects', [])
            if not projects:
                return [TextContent(type="text", text=f"No metadata found for project {key}")]

            issuetypes = projects[0].get('issuetypes', [])
            if not issuetypes:
                 return [TextContent(type="text", text=f"Issue type {type_id} not found in project {key}")]

            target_type = issuetypes[0]
            fields = target_type.get('fields', {})

            field_list = [f"{k}: {v.get('name')} (Required: {v.get('required')})" for k, v in fields.items()]

            result = f"Fields for {target_type.get('name')}:\n" + "\n".join(field_list)
            return [TextContent(type="text", text=result)]

        raise ValueError(f"Tool {name} not found")

    except Exception as e:
        error_msg = str(e)
        # Try to extract detailed server response if available
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_msg += f"\nServer Response: {e.response.text}"
            except:
                pass
        return [TextContent(type="text", text=f"Error: {error_msg}")]


# --- 5. Correct SSE Implementation ---

from starlette.responses import Response as StarletteResponse

class ASGIResponse(StarletteResponse):
    def __init__(self, app):
        self.app = app
        self.background = None
        self.body = b""
        self.status_code = 200

    async def __call__(self, scope, receive, send):
        await self.app(scope, receive, send)

@app.get("/sse")
async def handle_sse(request: Request):
    """
    Establish an SSE connection.
    Creates a session-specific transport and runs the server loop.
    """
    session_id = str(uuid.uuid4())
    logger.info(f"New SSE connection starting. Session ID: {session_id}")

    # The endpoint URL must include the session_id so POST requests can find the right transport
    endpoint_url = f"/messages/{session_id}"

    try:
        transport = SseServerTransport(endpoint_url)
        sessions[session_id] = transport
    except Exception as e:
        logger.error(f"Error creating SseServerTransport: {e}", exc_info=True)
        raise e

    async def sse_asgi_handler(scope, receive, send):
        try:
            logger.debug(f"Session {session_id}: Starting transport.connect_sse")
            async with transport.connect_sse(scope, receive, send) as (read_stream, write_stream):
                logger.info(f"Session {session_id}: Transport connected. Running MCP server loop.")
                await mcp_server.run(
                    read_stream,
                    write_stream,
                    mcp_server.create_initialization_options()
                )
                logger.info(f"Session {session_id}: MCP server loop finished.")
        except Exception as e:
            logger.error(f"Session {session_id} closed with error: {e}", exc_info=True)
        finally:
            if session_id in sessions:
                del sessions[session_id]
            logger.info(f"Session {session_id} cleaned up.")

    return ASGIResponse(sse_asgi_handler)

@app.post("/messages/{session_id}")
async def handle_messages(request: Request, session_id: str):
    """
    Handle incoming JSON-RPC messages (POST).
    Route them to the correct transport based on session_id.
    """
    logger.debug(f"Handling POST /messages/{session_id}")

    if not session_id or session_id not in sessions:
        logger.error(f"Session {session_id} not found in active sessions: {list(sessions.keys())}")
        raise HTTPException(status_code=404, detail="Session not found or expired")

    transport = sessions[session_id]

    # Return an ASGIResponse that delegates to the transport's handler
    # This avoids FastAPI/Starlette trying to send its own response
    try:
        logger.debug(f"Delegating to transport.handle_post_message for session {session_id}")
        return ASGIResponse(transport.handle_post_message)
    except Exception as e:
        logger.error(f"Error preparing ASGIResponse: {e}", exc_info=True)
        raise e

if __name__ == "__main__":
    # For local testing and Cloud Run
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
