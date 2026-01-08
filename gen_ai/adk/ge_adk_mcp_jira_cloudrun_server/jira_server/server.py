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
sessions = {}

# --- 4. Helpers & Tools ---
def get_atlassian_resources(token: str):
    resp = requests.get(
        "https://api.atlassian.com/oauth/token/accessible-resources",
        headers={"Authorization": f"Bearer {token}"}
    )
    resp.raise_for_status()
    return resp.json()

def get_jira_client() -> tuple[Jira, str]:
    token = user_token_var.get()
    if not token:
        raise ValueError("Authentication required. Please provide a Bearer token.")

    try:
        sites = get_atlassian_resources(token)
        if not sites:
            raise ValueError("No Jira sites found for this user.")

        # Default to the first site
        cloud_id = sites[0]['id']
        site_url = sites[0]['url'].rstrip('/')
        api_url = f"https://api.atlassian.com/ex/jira/{cloud_id}"

        return Jira(url=api_url, token=token, cloud=True), site_url
    except Exception as e:
        raise ValueError(f"Jira Connection Error: {str(e)}")

@mcp_server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(name="getVisibleJiraProjects", description="Get projects list.", inputSchema={"type": "object"}),
        Tool(name="searchJiraIssuesUsingJql", description="Fetch issues. Call repeatedly with nextPageToken for full analysis.",
             inputSchema={
                 "type": "object",
                 "properties": {
                     "jql": {"type": "string"},
                     "maxResults": {"type": "integer", "default": 50},
                     "nextPageToken": {"type": "string"},
                     "startAt": {"type": "integer", "default": 0}
                 },
                 "required": ["jql"]
             }
             ),
        Tool(name="summarizeJiraIssues", description="Server-side aggregation for large datasets. Returns statistical counts (Status, Priority, Type) without returning raw issues.",
             inputSchema={
                 "type": "object",
                 "properties": {
                     "jql": {"type": "string"},
                     "maxResults": {"type": "integer", "default": 1000}
                 },
                 "required": ["jql"]
             }
             ),
        Tool(name="getJiraIssuesReport", description="Generates a detailed report of issues including ID, Duration (calculated), and Summary. Handles pagination internally to return all matching results up to maxResults. Supports 'nextPageToken' for fetching subsequent batches.",
             inputSchema={
                 "type": "object",
                 "properties": {
                     "jql": {"type": "string"},
                     "maxResults": {"type": "integer", "default": 2000},
                     "nextPageToken": {"type": "string"}
                 },
                 "required": ["jql"]
             }
             )
    ]

@mcp_server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    try:
        jira, site_url = get_jira_client()
        token = user_token_var.get()

        if name == "getVisibleJiraProjects":
            projects = jira.projects()
            return [TextContent(type="text", text="\n".join([f"{p['key']}: {p['name']}" for p in projects]))]

        elif name == "getJiraIssuesReport":
            jql = arguments.get("jql")
            max_results = min(arguments.get("maxResults", 2000), 10000)
            input_next_token = arguments.get("nextPageToken")
            
            all_issues = []
            next_page_token = input_next_token
            batch_size = 100
            
            from datetime import datetime
            
            while len(all_issues) < max_results:
                kwargs = {
                    "limit": min(batch_size, max_results - len(all_issues)),
                    "fields": "summary,status,created,resolutiondate,description"
                }
                if next_page_token:
                    kwargs["nextPageToken"] = next_page_token

                data = jira.enhanced_jql(jql, **kwargs)
                issues = data.get('issues', [])
                
                if not issues:
                    # No more issues returned
                    next_page_token = None
                    break
                    
                all_issues.extend(issues)
                next_page_token = data.get('nextPageToken')
                
                if not next_page_token:
                    break
            
            # Generate Report
            token_str = next_page_token if next_page_token else "NONE"
            lines = [f"METADATA: Found={len(all_issues)}, NextToken={token_str}", ""]
            
            lines.append(f"**Jira Detailed Report** (Batch size: {len(all_issues)})")
            lines.append(f"{ 'ID':<20} | {'Duration':<20} | {'Summary'}")
            lines.append("-" * 100)
            
            for i in all_issues:
                fields = i.get('fields', {})
                key = i['key']
                key_link = f"[{key}]({site_url}/browse/{key})"
                summary = fields.get('summary', 'No Summary')
                
                created_str = fields.get('created')
                resolved_str = fields.get('resolutiondate')
                duration_str = "N/A"
                
                if created_str and resolved_str:
                    try:
                        c_dt = datetime.strptime(created_str[:19], "%Y-%m-%dT%H:%M:%S")
                        r_dt = datetime.strptime(resolved_str[:19], "%Y-%m-%dT%H:%M:%S")
                        diff = r_dt - c_dt
                        
                        total_seconds = int(diff.total_seconds())
                        days, remainder = divmod(total_seconds, 86400)
                        hours, remainder = divmod(remainder, 3600)
                        minutes, seconds = divmod(remainder, 60)
                        
                        if days > 0:
                            duration_str = f"{days}d {hours}h"
                        elif hours > 0:
                            duration_str = f"{hours}h {minutes}m"
                        else:
                            duration_str = f"{minutes}m {seconds}s"
                    except Exception:
                        duration_str = "Error"

                lines.append(f"{key_link:<20} | {duration_str:<20} | {summary[:50]}")

            return [TextContent(type="text", text="\n".join(lines))]
            
        elif name == "summarizeJiraIssues":
            jql = arguments.get("jql")
            max_results = min(arguments.get("maxResults", 1000), 2000)
            
            all_issues = []
            next_page_token = None
            batch_size = 100
            
            while len(all_issues) < max_results:
                kwargs = {
                    "limit": min(batch_size, max_results - len(all_issues)),
                    "fields": "status,priority,issuetype"
                }
                if next_page_token:
                    kwargs["nextPageToken"] = next_page_token

                data = jira.enhanced_jql(jql, **kwargs)
                issues = data.get('issues', [])
                
                if not issues:
                    break
                    
                all_issues.extend(issues)
                next_page_token = data.get('nextPageToken')
                
                if not next_page_token:
                    break

            # Aggregate Data
            stats = {
                "total": len(all_issues),
                "status": {},
                "priority": {},
                "issuetype": {}
            }

            for i in all_issues:
                fields = i.get('fields', {})
                s_name = fields.get('status', {}).get('name', 'Unknown')
                stats["status"][s_name] = stats["status"].get(s_name, 0) + 1
                p_name = fields.get('priority', {}).get('name', 'None')
                stats["priority"][p_name] = stats["priority"].get(p_name, 0) + 1
                t_name = fields.get('issuetype', {}).get('name', 'Unknown')
                stats["issuetype"][t_name] = stats["issuetype"].get(t_name, 0) + 1

            # Format Report
            report = [f"**Jira Summary Report** (Analyzed {stats['total']} issues)"]
            
            report.append("\n**By Status:**")
            for k, v in sorted(stats["status"].items(), key=lambda x: x[1], reverse=True):
                report.append(f"- {k}: {v}")
                
            report.append("\n**By Priority:**")
            for k, v in sorted(stats["priority"].items(), key=lambda x: x[1], reverse=True):
                report.append(f"- {k}: {v}")
                
            report.append("\n**By Type:**")
            for k, v in sorted(stats["issuetype"].items(), key=lambda x: x[1], reverse=True):
                report.append(f"- {k}: {v}")

            return [TextContent(type="text", text="\n".join(report))]

        elif name == "searchJiraIssuesUsingJql":
            jql = arguments.get("jql")
            max_results = arguments.get("maxResults", 50)
            kwargs = {
                "limit": max_results,
                "fields": "summary,status,created,issuetype,priority,resolutiondate,updated,description"
            }
            next_page_token = arguments.get("nextPageToken")
            if next_page_token:
                kwargs["nextPageToken"] = next_page_token
            
            data = jira.enhanced_jql(jql, **kwargs)
            issues = data.get('issues', [])
            resp_next_token = data.get('nextPageToken')
            has_more = bool(resp_next_token)

            if not issues:
                return [TextContent(type="text", text="No results found.")]

            res = [f"METADATA: PageCount={len(issues)}, HasMore={has_more}, NextToken={resp_next_token or 'NONE'}\n"]
            
            def extract_adf(node):
                try:
                    if isinstance(node, dict):
                        if "text" in node: return str(node.get("text", ""))
                        if "content" in node and isinstance(node["content"], list):
                            return " ".join(extract_adf(n) for n in node["content"])
                    return ""
                except: return ""

            for i in issues:
                f = i.get('fields', {})
                created = f.get('created', '')[:19]
                resolution_date = f.get('resolutiondate', '')[:19] if f.get('resolutiondate') else 'N/A'
                updated = f.get('updated', '')[:19]
                
                desc_raw = f.get('description', '') or ""
                desc_text = desc_raw if isinstance(desc_raw, str) else extract_adf(desc_raw)
                desc_trunc = desc_text[:500].replace('\n', ' ') + "..." if len(desc_text) > 500 else desc_text.replace('\n', ' ')
                
                res.append(f"ISSUE: Key={i['key']} | Status={f.get('status',{}).get('name')} | Created={created} | ResolutionDate={resolution_date} | Updated={updated} | Summary={f.get('summary')} | Desc={desc_trunc} | URL={site_url}/browse/{i['key']}")

            return [TextContent(type="text", text="\n".join(res))]

        raise ValueError("Unknown tool")
    except Exception as e:
        logger.error(f"Tool Error: {e}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]

# --- 5. Correct SSE Implementation ---
from starlette.responses import Response as StarletteResponse

class ASGIResponse(StarletteResponse):
    def __init__(self, app):
        self.app = app
        self.background = None # Required by Starlette
        self.body = b""
        self.status_code = 200

    async def __call__(self, scope, receive, send):
        await self.app(scope, receive, send)

@app.get("/sse")
async def handle_sse(request: Request):
    session_id = str(uuid.uuid4())
    logger.info(f"New SSE Session (Rev 13): {session_id}")
    transport = SseServerTransport(f"/messages/{session_id}")
    sessions[session_id] = transport
    async def sse_handler(scope, receive, send):
        async with transport.connect_sse(scope, receive, send) as (read, write):
            await mcp_server.run(read, write, mcp_server.create_initialization_options())
    return ASGIResponse(sse_handler)

@app.post("/messages/{session_id}")
async def handle_messages(request: Request, session_id: str):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session expired")
    return ASGIResponse(sessions[session_id].handle_post_message)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
# Revision Trigger Thu Jan  8 13:44:22 EST 2026
