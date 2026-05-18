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
# auth_kind: "bearer" (OAuth, per-user from GE popup) | "basic" (email+API token, headless)
user_auth_var = contextvars.ContextVar("user_auth", default=None)  # type: ignore

# --- 2. Middleware to Capture Token ---
class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        auth_header = request.headers.get("Authorization") or ""
        if auth_header.startswith("Bearer "):
            token = auth_header.split(" ", 1)[1].strip()
            user_auth_var.set({"kind": "bearer", "token": token})
            logger.debug(f"Captured Bearer: {token[:10]}...")
        elif auth_header.startswith("Basic "):
            # Site URL must come via X-Atlassian-Site header — we can't derive it
            # from a Basic token (no accessible-resources endpoint for that auth).
            site = request.headers.get("X-Atlassian-Site", "").rstrip("/")
            user_auth_var.set({"kind": "basic", "token": auth_header.split(" ", 1)[1].strip(), "site": site})
            logger.debug(f"Captured Basic for site: {site}")
        else:
            user_auth_var.set(None)
            logger.debug("No auth in headers")
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
    auth = user_auth_var.get()
    if not auth:
        raise ValueError("Authentication required. Provide Bearer (OAuth) or Basic (API token) header.")

    try:
        if auth["kind"] == "basic":
            # Decode email:token and call site URL directly. atlassian-python-api
            # accepts username/password for Basic auth.
            import base64
            raw = base64.b64decode(auth["token"]).decode()
            email, _, api_token = raw.partition(":")
            site_url = (auth.get("site") or "").rstrip("/")
            if not site_url:
                raise ValueError("Basic auth requires X-Atlassian-Site header (e.g. https://yoursite.atlassian.net).")
            return Jira(url=site_url, username=email, password=api_token, cloud=True), site_url
        # Bearer (OAuth) — use the proxied API endpoint with cloudId resolution.
        token = auth["token"]
        sites = get_atlassian_resources(token)
        if not sites:
            raise ValueError("No Jira sites found for this user.")
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
             ),
        Tool(name="getIssueComments", description="Retrieves all comments on a single Jira issue. Returns each comment with author, created timestamp, and body text.",
             inputSchema={
                 "type": "object",
                 "properties": {
                     "issueKey": {"type": "string", "description": "Issue key like SMP-912 or BUGS-100"},
                     "maxResults": {"type": "integer", "default": 50}
                 },
                 "required": ["issueKey"]
             }
             ),
        Tool(name="getIssueWorklogs", description="Retrieves all worklogs (time-tracking entries) on a single Jira issue. Returns each worklog with author, time spent, and comment.",
             inputSchema={
                 "type": "object",
                 "properties": {
                     "issueKey": {"type": "string", "description": "Issue key like SMP-912 or BUGS-100"},
                     "maxResults": {"type": "integer", "default": 50}
                 },
                 "required": ["issueKey"]
             }
             ),
        Tool(name="getIssueLinks", description="Retrieves all issue links (Blocks, Duplicate, Relates, Cloners) on a single Jira issue, in both directions (inward and outward).",
             inputSchema={
                 "type": "object",
                 "properties": {
                     "issueKey": {"type": "string", "description": "Issue key like SMP-912 or BUGS-100"}
                 },
                 "required": ["issueKey"]
             }
             )
    ]

@mcp_server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    try:
        jira, site_url = get_jira_client()

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

        elif name == "getIssueComments":
            issue_key = arguments.get("issueKey")
            max_results = arguments.get("maxResults", 50)
            if not issue_key:
                raise ValueError("issueKey required")
            data = jira.issue(issue_key, fields="comment")
            comments = (data.get("fields", {}).get("comment", {}) or {}).get("comments", []) or []
            comments = comments[:max_results]
            if not comments:
                return [TextContent(type="text", text=f"No comments on {issue_key}.")]
            lines = [f"COMMENTS on [{issue_key}]({site_url}/browse/{issue_key}) — {len(comments)} total:"]
            for c in comments:
                author = (c.get("author") or {}).get("displayName") or "Unknown"
                created = c.get("created", "")
                # body may be ADF dict or string
                body_raw = c.get("body")
                body_text = ""
                if isinstance(body_raw, dict):
                    def _walk(node):
                        if isinstance(node, dict):
                            if node.get("type") == "text" and "text" in node:
                                return node["text"]
                            return "".join(_walk(x) for x in (node.get("content") or []))
                        return ""
                    body_text = _walk(body_raw)
                elif isinstance(body_raw, str):
                    body_text = body_raw
                lines.append(f"---\n[{created}] {author}: {body_text[:800]}")
            return [TextContent(type="text", text="\n".join(lines))]

        elif name == "getIssueWorklogs":
            issue_key = arguments.get("issueKey")
            max_results = arguments.get("maxResults", 50)
            if not issue_key:
                raise ValueError("issueKey required")
            wl_data = jira.issue_worklog(issue_key)
            worklogs = (wl_data.get("worklogs") or [])[:max_results]
            if not worklogs:
                return [TextContent(type="text", text=f"No worklogs on {issue_key}.")]
            total_seconds = 0
            lines = [f"WORKLOGS on [{issue_key}]({site_url}/browse/{issue_key}) — {len(worklogs)} entries:"]
            for w in worklogs:
                author = (w.get("author") or {}).get("displayName") or "Unknown"
                started = w.get("started", "")
                ts = w.get("timeSpent", "")
                ts_secs = w.get("timeSpentSeconds", 0)
                total_seconds += ts_secs
                cmt_raw = w.get("comment")
                cmt = ""
                if isinstance(cmt_raw, dict):
                    def _walk(node):
                        if isinstance(node, dict):
                            if node.get("type") == "text" and "text" in node:
                                return node["text"]
                            return "".join(_walk(x) for x in (node.get("content") or []))
                        return ""
                    cmt = _walk(cmt_raw)
                elif isinstance(cmt_raw, str):
                    cmt = cmt_raw
                lines.append(f"---\n[{started}] {author}: {ts} :: {cmt[:300]}")
            hours = total_seconds / 3600
            lines.append(f"\nTOTAL TIME LOGGED: {hours:.1f}h ({total_seconds}s) across {len(worklogs)} entries")
            return [TextContent(type="text", text="\n".join(lines))]

        elif name == "getIssueLinks":
            issue_key = arguments.get("issueKey")
            if not issue_key:
                raise ValueError("issueKey required")
            data = jira.issue(issue_key, fields="issuelinks")
            links = (data.get("fields", {}) or {}).get("issuelinks", []) or []
            if not links:
                return [TextContent(type="text", text=f"No links on {issue_key}.")]
            lines = [f"ISSUE LINKS on [{issue_key}]({site_url}/browse/{issue_key}) — {len(links)} links:"]
            for l in links:
                t = (l.get("type") or {})
                tname = t.get("name", "?")
                if "outwardIssue" in l:
                    o = l["outwardIssue"]
                    relation = t.get("outward", "")
                    other = o.get("key")
                    summary = (o.get("fields", {}) or {}).get("summary", "")
                    lines.append(f"- {tname} ({relation}) → [{other}]({site_url}/browse/{other}): {summary}")
                if "inwardIssue" in l:
                    i = l["inwardIssue"]
                    relation = t.get("inward", "")
                    other = i.get("key")
                    summary = (i.get("fields", {}) or {}).get("summary", "")
                    lines.append(f"- {tname} ({relation}) ← [{other}]({site_url}/browse/{other}): {summary}")
            return [TextContent(type="text", text="\n".join(lines))]

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

# --- 6. StreamableHTTP endpoint for GE custom MCP datastores ---
@app.post("/mcp")
async def handle_mcp_jsonrpc(request: Request):
    """Handle JSON-RPC requests from GE custom MCP datastores (StreamableHTTP transport).

    This endpoint allows the same MCP server to be used both:
    - Via SSE (/sse) for Agent Engine (Option A)
    - Via StreamableHTTP (/mcp) for GE custom MCP datastores (Option C)
    """
    try:
        body = await request.json()
        method = body.get("method")
        params = body.get("params", {})
        request_id = body.get("id")

        logger.info(f"JSON-RPC request: method={method} id={request_id}")

        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "serverInfo": {
                        "name": "jira-multi-tenant",
                        "version": "1.0.0"
                    },
                    "capabilities": {
                        "tools": {}
                    }
                }
            }

        elif method == "tools/list":
            tools_list = await list_tools()
            tools_dict = [
                {
                    "name": t.name,
                    "description": t.description,
                    "inputSchema": t.inputSchema
                }
                for t in tools_list
            ]
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {"tools": tools_dict}
            }

        elif method == "tools/call":
            tool_name = params.get("name")
            tool_args = params.get("arguments", {})

            logger.info(f"Calling tool: {tool_name} with args: {tool_args}")

            result = await call_tool(tool_name, tool_args)

            # Convert TextContent to JSON-RPC format
            content_list = []
            for item in result:
                if hasattr(item, 'text'):
                    content_list.append({
                        "type": "text",
                        "text": item.text
                    })

            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {"content": content_list}
            }

        else:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}"
                }
            }

    except Exception as e:
        logger.error(f"MCP JSON-RPC error: {e}")
        return {
            "jsonrpc": "2.0",
            "id": body.get("id") if 'body' in locals() else None,
            "error": {
                "code": -32603,
                "message": str(e)
            }
        }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
# Revision Trigger Thu Jan  8 13:44:22 EST 2026
# Revision Mon May 18 18:12:34 EDT 2026
