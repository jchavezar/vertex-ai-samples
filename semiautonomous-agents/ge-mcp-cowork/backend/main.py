import os
import json
import base64
import logging
import asyncio
import httpx
import urllib.parse
import requests
import threading
import socketserver
import http.server
import secrets
import time
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from dotenv import load_dotenv

from google import genai
from google.genai import types

load_dotenv(dotenv_path="../.env", override=True)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ge-mcp-cowork-backend")

# In-memory Tool Schema Cache to avoid fetching tools from MCP on every request
SCHEMA_CACHE = {}

def get_schema_cache_key(conn_name: str, config: dict) -> str:
    # Build unique key based on connector name and credential hash (last 8 chars of token/API key)
    token = config.get("token", "") or config.get("api_token", "") or ""
    email = config.get("email", "")
    cred_part = f"{email}:{token[-8:]}" if token else "no_creds"
    return f"{conn_name}:{cred_part}"


app = FastAPI(title="Gemini Enterprise MCP Co-work Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Endpoint mappings for MCP Servers
JIRA_MCP_URL = os.getenv("JIRA_MCP_URL", "https://jira-mcp-server-recipe-oyntfgdwsq-uc.a.run.app/mcp")
SHAREPOINT_MCP_URL = os.getenv("SHAREPOINT_MCP_URL", "https://ge-custom-sharepoint-mcp-oyntfgdwsq-uc.a.run.app/mcp")

# Helper: Get auth headers for a connector based on its config
def get_auth_headers(connector_name: str, config: Dict[str, Any]) -> Dict[str, str]:
    headers = {"Content-Type": "application/json"}
    
    if connector_name == "jira":
        # Supports Basic auth or OAuth Bearer
        auth_type = config.get("auth_type", "basic")
        if auth_type == "basic":
            email = config.get("email", "")
            token = config.get("token", "")
            site_url = config.get("site_url", "")
            
            # Fallback to env variables if mock values or empty
            if not email or email == "demo@sockcop.net":
                email = os.getenv("ATLASSIAN_EMAIL", email)
            if not token or token == "demo-token":
                token = os.getenv("ATLASSIAN_API_TOKEN", token)
            if not site_url or site_url == "https://sockcop.atlassian.net":
                site_url = os.getenv("ATLASSIAN_SITE_URL", site_url)
                
            if email and token:
                auth_str = f"{email}:{token}"
                b64_auth = base64.b64encode(auth_str.encode()).decode()
                headers["Authorization"] = f"Basic {b64_auth}"
            if site_url:
                headers["X-Atlassian-Site"] = site_url.rstrip("/")
        elif auth_type == "oauth" and config.get("token"):
            headers["Authorization"] = f"Bearer {config['token']}"
            
    elif connector_name == "sharepoint":
        # Requires Bearer token
        token = config.get("token", "")
        if token:
            headers["Authorization"] = f"Bearer {token}"
            
    return headers

# Helper: Fetch tools from an MCP server
async def fetch_mcp_tools(connector_name: str, config: Dict[str, Any]) -> List[Dict[str, Any]]:
    url = JIRA_MCP_URL if connector_name == "jira" else SHAREPOINT_MCP_URL
    headers = get_auth_headers(connector_name, config)
    
    payload = {
        "jsonrpc": "2.0",
        "method": "tools/list",
        "params": {},
        "id": 1
    }
    
    logger.info(f"Fetching tools for {connector_name} from {url}")
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(url, headers=headers, json=payload)
            if resp.status_code != 200:
                logger.error(f"Failed to fetch tools for {connector_name}: {resp.status_code} - {resp.text}")
                return []
            
            data = resp.json()
            if "error" in data:
                logger.error(f"MCP server returned error for {connector_name}: {data['error']}")
                return []
                
            return data.get("result", {}).get("tools", [])
    except Exception as e:
        logger.error(f"Error fetching tools for {connector_name}: {e}")
        return []

# Helper: Call a tool on an MCP server
async def call_mcp_tool(connector_name: str, tool_name: str, arguments: Dict[str, Any], config: Dict[str, Any]) -> Any:
    url = JIRA_MCP_URL if connector_name == "jira" else SHAREPOINT_MCP_URL
    headers = get_auth_headers(connector_name, config)
    
    payload = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": arguments
        },
        "id": 2
    }
    
    logger.info(f"Calling tool {tool_name} for {connector_name} on {url}")
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(url, headers=headers, json=payload)
            if resp.status_code != 200:
                return {"error": f"MCP HTTP Error {resp.status_code}"}
            
            data = resp.json()
            if "error" in data:
                return {"error": data["error"]}
                
            # Returns the tool's result block
            return data.get("result", {})
    except Exception as e:
        logger.error(f"Error calling tool {tool_name}: {e}")
        return {"error": str(e)}

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatPayload(BaseModel):
    messages: List[ChatMessage]
    connectors: Dict[str, Any]
    use_reasoning_engine: Optional[bool] = False

@app.post("/api/chat")
async def chat_endpoint(payload: ChatPayload):
    """
    Standard function calling loop using google-genai client and streaming final results.
    """
    
    # 1. Fetch enabled tools
    logger.info(f"Received connectors payload: {json.dumps(payload.connectors)}")
    exposed_tools = []
    tool_connector_map = {} # prefixed_name -> {connector, original_name}
    
    enabled_connectors = []
    
    for conn_name, conn_config in payload.connectors.items():
        if conn_name in ("jira", "sharepoint") and conn_config.get("enabled", False):
            enabled_connectors.append(conn_name)
            
            # Check schema cache
            cache_key = get_schema_cache_key(conn_name, conn_config)
            if cache_key in SCHEMA_CACHE:
                logger.info(f"Using cached tools list for {conn_name}")
                tools_list = SCHEMA_CACHE[cache_key]
            else:
                tools_list = await fetch_mcp_tools(conn_name, conn_config)
                if tools_list:
                    SCHEMA_CACHE[cache_key] = tools_list
                    
            for t in tools_list:
                t_name = t["name"]
                prefixed_name = f"{conn_name}_{t_name}"
                tool_connector_map[prefixed_name] = {
                    "connector": conn_name,
                    "original_name": t_name
                }
                # Map to Gemini FunctionDeclaration
                exposed_tools.append(
                    types.FunctionDeclaration(
                        name=prefixed_name,
                        description=t["description"],
                        parameters=t["inputSchema"]
                    )
                )
    
    # Check if Google Search grounding is enabled
    google_search_enabled = payload.connectors.get("google_search", {}).get("enabled", False)
    
    # Build Gemini SDK tools configuration
    gemini_tools = []
    if google_search_enabled:
        # Grounding with Google Search cannot be combined with function calling or code execution
        gemini_tools.append(types.Tool(google_search=types.GoogleSearch()))
    else:
        # Combine function declarations and code execution into a single Tool object
        tool_kwargs = {}
        if exposed_tools:
            tool_kwargs["function_declarations"] = exposed_tools
        # Enable built-in Python Code Execution for advanced scripting and math calculations
        tool_kwargs["code_execution"] = types.ToolCodeExecution()
        gemini_tools.append(types.Tool(**tool_kwargs))
        
    logger.info(f"Enabled connectors: {enabled_connectors}. Google Search: {google_search_enabled}")
    logger.info(f"Exposed tool count: {len(exposed_tools)}")
    
    # Assemble conversation history
    gemini_messages = []
    for msg in payload.messages:
        role = "user" if msg.role == "user" else "model"
        gemini_messages.append(
            types.Content(role=role, parts=[types.Part.from_text(text=msg.content)])
        )
        
    async def sse_stream():
        if payload.use_reasoning_engine:
            try:
                import google.auth
                import google.auth.transport.requests
                import httpx
                
                logger.info("Routing chat to cloud Reasoning Engine (Agent Engine)...")
                
                credentials, project = google.auth.default()
                auth_req = google.auth.transport.requests.Request()
                credentials.refresh(auth_req)
                
                headers = {
                    "Authorization": f"Bearer {credentials.token}",
                    "Content-Type": "application/json"
                }
                
                ENGINE_ID = "5655965328849502208"
                LOCATION = "us-central1"
                create_session_url = f"https://{LOCATION}-aiplatform.googleapis.com/v1/projects/254356041555/locations/{LOCATION}/reasoningEngines/{ENGINE_ID}:query"
                stream_query_url = f"https://{LOCATION}-aiplatform.googleapis.com/v1/projects/254356041555/locations/{LOCATION}/reasoningEngines/{ENGINE_ID}:streamQuery?alt=sse"
                
                # 1. Create Session in Firestore
                user_id = "user-portal"
                session_payload = {
                    "class_method": "async_create_session",
                    "input": {"user_id": user_id}
                }
                
                logger.info("Creating session in cloud Firestore...")
                async with httpx.AsyncClient(timeout=30.0) as http_client:
                    resp = await http_client.post(create_session_url, headers=headers, json=session_payload)
                    if resp.status_code == 200:
                        session_id = resp.json().get("output", {}).get("id")
                        logger.info(f"Cloud session created: {session_id}")
                    else:
                        raise Exception(f"Failed to create cloud session: {resp.status_code} {resp.text}")
                        
                # 2. Stream Query
                prompt = payload.messages[-1].content
                query_payload = {
                    "class_method": "async_stream_query",
                    "input": {
                        "user_id": user_id,
                        "session_id": session_id,
                        "message": prompt
                    }
                }
                
                logger.info(f"Streaming query from cloud Reasoning Engine: '{prompt}'")
                llm_start = time.time()
                async with httpx.AsyncClient(timeout=60.0) as http_client:
                    async with http_client.stream("POST", stream_query_url, headers=headers, json=query_payload) as response:
                        if response.status_code != 200:
                            body = await response.aread()
                            raise Exception(f"Cloud query failed: {response.status_code} {body.decode()}")
                            
                        async for line in response.aiter_lines():
                            if line:
                                if line.startswith("data:"):
                                    line = line[len("data:"):].strip()
                                try:
                                    data = json.loads(line)
                                    content_dict = data.get("content", {})
                                    if content_dict:
                                        parts = content_dict.get("parts", [])
                                        for part in parts:
                                            text_chunk = part.get("text", "")
                                            if text_chunk:
                                                yield f"event: text\ndata: {json.dumps({'text': text_chunk})}\n\n"
                                except:
                                    pass
                
                total_time = time.time() - llm_start
                yield f"event: latency_split\ndata: {json.dumps({'llm_latency': round(total_time, 1), 'tool_latency': 0.0})}\n\n"
                yield "event: done\ndata: {}\n\n"
                return
            except Exception as e:
                logger.exception("Error routing to cloud reasoning engine")
                yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"
                return

        try:
            # Initialize Client
            use_vertex = os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "true").lower() == "true"
            if use_vertex:
                client = genai.Client(
                    vertexai=True,
                    project=os.getenv("GOOGLE_CLOUD_PROJECT", "vtxdemos"),
                    location=os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
                )
            else:
                client = genai.Client()
                
            model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
            
            # System instruction
            system_instruction = (
                "You are Gemini Enterprise, an expert corporate assistant. "
                "Answer the user's question using the tools available. "
                "Present answers clearly and professionally. "
                "If you fetch documents or tickets, summarize them concisely. "
                "Include URLs/cites as returned by the tools. "
                "Always format document and ticket references as clickable Markdown links "
                "using the exact URL returned by the tools (e.g., `[Document Title](URL)`). "
                "If a URL contains spaces, you must URL-encode them by replacing spaces with %20 "
                "in the link target (e.g., convert 'Shared Documents' to 'Shared%20Documents').\n\n"
                "**CRITICAL DASHBOARD VISUALIZATION RULES**:\n"
                "If the user asks for counts, statistics, status distribution, timelines, or breakdowns of tickets or documents "
                "(e.g., 'distribution of Ducati issues', 'priority breakdown', 'KPI summary dashboard', 'created timeline'), "
                "you MUST append an interactive dashboard chart using the XML <chart> tag syntax at the very end of your response. "
                "DO NOT ONLY LIST THEM IN TEXT. YOU MUST USE THE CHART TAG.\n\n"
                "EXAMPLES OF SUPPORTED CHART TYPES:\n"
                "1. **pie** (Donut distribution chart, best for category/status breakdowns):\n"
                "<chart type=\"pie\" title=\"Jira Status Distribution\">\n"
                "[\n"
                "  {\"name\": \"Done\", \"value\": 26},\n"
                "  {\"name\": \"To Do\", \"value\": 60},\n"
                "  {\"name\": \"In Progress\", \"value\": 1}\n"
                "]\n"
                "</chart>\n\n"
                "2. **bar** (Horizontal comparison bar list):\n"
                "<chart type=\"bar\" title=\"Jira Issue Counts by Type\">\n"
                "[\n"
                "  {\"name\": \"Task\", \"value\": 85},\n"
                "  {\"name\": \"Epic\", \"value\": 2}\n"
                "]\n"
                "</chart>\n\n"
                "3. **line** (Area timeline graph for trend dates/times):\n"
                "<chart type=\"line\" title=\"Issue Activity Weekly Trend\">\n"
                "[\n"
                "  {\"name\": \"Mon\", \"value\": 3},\n"
                "  {\"name\": \"Tue\", \"value\": 8},\n"
                "  {\"name\": \"Wed\", \"value\": 5},\n"
                "  {\"name\": \"Thu\", \"value\": 12},\n"
                "  {\"name\": \"Fri\", \"value\": 7}\n"
                "]\n"
                "</chart>\n\n"
                "4. **stats** (Grid of high-level KPI cards for multi-metric dashboard summaries):\n"
                "<chart type=\"stats\" title=\"Jira Workspace KPI Summary\">\n"
                "[\n"
                "  {\"name\": \"Total Tickets\", \"value\": \"87\"},\n"
                "  {\"name\": \"Completed Tasks\", \"value\": \"26\"},\n"
                "  {\"name\": \"Active Sprint To Do\", \"value\": \"60\"},\n"
                "  {\"name\": \"Blocked Items\", \"value\": \"3\"}\n"
                "]\n"
                "</chart>\n\n"
                 "Keep names concise. The data inside <chart> must be a valid JSON array of objects with 'name' and 'value' fields. Do not output raw HTML tags other than <chart>.\n\n"
                "**CRITICAL FOLLOW-UP SUGGESTIONS RULES**:\n"
                "At the very end of your response, after any charts, you MUST suggest 2 to 3 follow-up questions that are directly related to the user's question AND based ONLY on the actual data/context retrieved.\n"
                "Ensure the suggested questions are answerable using the available tools and data in the workspace (for example, if you just retrieved a list of open bugs, suggest asking about the cycle time of those bugs, or who is assigned to them). Do not suggest questions that cannot be answered or are unrelated to the current context.\n"
                "Format these suggestions inside a <suggestions> XML tag block, with each suggestion in a <suggestion> child tag, like this:\n"
                "<suggestions>\n"
                "  <suggestion>What is the average cycle time for the open bugs in PLAT?</suggestion>\n"
                "  <suggestion>Show me who is assigned to the High priority issues.</suggestion>\n"
                "</suggestions>"
            )
            
            # Track sources discovered during tool execution
            sources = []
            
            # Track latency splits
            total_llm_time = 0.0
            total_tool_time = 0.0

            # Loop for function calling
            loop_count = 0
            while loop_count < 10: # Safety cap
                loop_count += 1
                
                logger.info(f"Generating content, turn {loop_count}...")
                yield f"event: status\ndata: {json.dumps({'status': 'Thinking...'})}\n\n"
                
                # We do a synchronous/blocking generate_content call for function-calling turns
                # because we need to get the function calls, resolve them, and loop.
                llm_start = time.time()
                response = client.models.generate_content(
                    model=model,
                    contents=gemini_messages,
                    config=types.GenerateContentConfig(
                        tools=gemini_tools,
                        system_instruction=system_instruction
                    )
                )
                total_llm_time += (time.time() - llm_start)
                
                logger.info(f"Model Response turn {loop_count}: {response.text or ''} - Function calls: {response.function_calls}")
                
                function_calls = response.function_calls
                if not function_calls:
                    # Model did not generate any tool calls! We can break and do the final streaming response.
                    # Or wait, since we already did a generate_content call and it gave us the final text,
                    # we can just yield that text directly!
                    final_text = response.text or ""
                    if final_text:
                        if "<suggestions>" not in final_text.lower():
                            has_jira = any(t in final_text.lower() for t in ("jira", "project", "ticket", "bug", "smp", "bugs", "plat"))
                            has_sharepoint = any(t in final_text.lower() for t in ("sharepoint", "document", "file", "folder", "entra", "site"))
                            if has_jira:
                                sugs = [
                                    "Calculate cycle time for resolved tickets in SMP (excluding weekends)",
                                    "Run a Monte Carlo simulation on remaining To Do tickets in SMP",
                                    "What other high-priority issues are in the SMP project?"
                                ]
                            elif has_sharepoint:
                                sugs = [
                                    "Show me files modified in the last 7 days",
                                    "List all document libraries in the root site",
                                    "Summarize the recent uploaded PDF documents"
                                ]
                            else:
                                sugs = [
                                    "List all visible Jira projects",
                                    "List document libraries in SharePoint"
                                ]
                            suggestions_xml = "\n\n<suggestions>\n" + "\n".join(f"  <suggestion>{s}</suggestion>" for s in sugs) + "\n</suggestions>"
                            final_text += suggestions_xml
                        yield f"event: text\ndata: {json.dumps({'text': final_text})}\n\n"
                    break
                
                # Handle function calls
                # Append model's response to history
                gemini_messages.append(response.candidates[0].content)
                
                response_parts = []
                call_tasks = []
                calls_metadata = []
                
                for call in function_calls:
                    mapping = tool_connector_map.get(call.name)
                    if not mapping:
                        logger.warning(f"No mapping found for tool call: {call.name}")
                        conn_name = "unknown"
                        orig_tool_name = call.name
                    else:
                        conn_name = mapping["connector"]
                        orig_tool_name = mapping["original_name"]
                        
                    logger.info(f"Model calls: {call.name} (resolved to {orig_tool_name} on {conn_name})")
                    
                    # Yield tool call event to UI
                    yield f"event: tool_call\ndata: {json.dumps({'connector': conn_name, 'tool': call.name, 'arguments': call.args})}\n\n"
                    
                    conn_config = payload.connectors.get(conn_name, {})
                    call_tasks.append(
                        call_mcp_tool(conn_name, orig_tool_name, call.args, conn_config)
                    )
                    calls_metadata.append({
                        "call": call,
                        "conn_name": conn_name,
                        "orig_tool_name": orig_tool_name
                    })
                
                # Execute all calls concurrently
                tool_start = time.time()
                tool_results = await asyncio.gather(*call_tasks, return_exceptions=True)
                total_tool_time += (time.time() - tool_start)
                
                # Process results in order
                for meta, tool_result in zip(calls_metadata, tool_results):
                    call = meta["call"]
                    conn_name = meta["conn_name"]
                    orig_tool_name = meta["orig_tool_name"]
                    
                    if isinstance(tool_result, Exception):
                        logger.error(f"Error in parallel tool call {call.name}: {tool_result}")
                        tool_result = {"error": str(tool_result)}
                        
                    # Yield tool result event to UI
                    yield f"event: tool_result\ndata: {json.dumps({'connector': conn_name, 'tool': call.name, 'status': 'success', 'result': tool_result})}\n\n"
                    
                    # Parse result for display
                    content_list = tool_result.get("content", []) if isinstance(tool_result, dict) else []
                    result_text = ""
                    for item in content_list:
                        if item.get("type") == "text":
                            result_text += item.get("text", "")
                            
                    # Extract Sources (heuristics)
                    if isinstance(tool_result, dict):
                        if conn_name == "sharepoint":
                            structured = tool_result.get("structuredContent")
                            if structured:
                                if isinstance(structured, dict):
                                    if "url" in structured and "title" in structured:
                                        sources.append({
                                            "title": structured["title"],
                                            "url": structured["url"],
                                            "connector": "sharepoint"
                                        })
                                    elif "results" in structured:
                                        for res in structured["results"]:
                                            sources.append({
                                                "title": res.get("title", "SharePoint Doc"),
                                                "url": res.get("url", ""),
                                                "connector": "sharepoint"
                                            })
                            elif result_text:
                                try:
                                    parsed = json.loads(result_text)
                                    if "url" in parsed and "title" in parsed:
                                        sources.append({
                                            "title": parsed["title"],
                                            "url": parsed["url"],
                                            "connector": "sharepoint"
                                        })
                                    elif "results" in parsed:
                                        for res in parsed["results"]:
                                            sources.append({
                                                "title": res.get("title", "SharePoint Doc"),
                                                "url": res.get("url", ""),
                                                "connector": "sharepoint"
                                            })
                                except: pass
                                
                        elif conn_name == "jira":
                            import re
                            matches = re.findall(r"\[([A-Z0-9\-]+)\]\((https://[a-zA-Z0-9\.\-_/]+)\)", result_text)
                            for issue_key, issue_url in matches:
                                if not any(s["title"] == issue_key for s in sources):
                                    sources.append({
                                        "title": issue_key,
                                        "url": issue_url,
                                        "connector": "jira"
                                    })
                                    
                    # Append result part
                    response_parts.append(
                        types.Part(
                            function_response=types.FunctionResponse(
                                name=call.name,
                                response={"result": tool_result}
                            )
                        )
                    )
                    
                # Append user turn with function responses
                gemini_messages.append(
                    types.Content(role="user", parts=response_parts)
                )
                
            # If we reached here after the loop, yield final sources if any
            if sources:
                yield f"event: sources\ndata: {json.dumps({'sources': sources})}\n\n"
                
            # Yield latency split statistics
            yield f"event: latency_split\ndata: {json.dumps({'llm_latency': round(total_llm_time, 1), 'tool_latency': round(total_tool_time, 1)})}\n\n"
            
            # Yield final done event
            yield "event: done\ndata: {}\n\n"
            
        except Exception as e:
            logger.exception("Error in chat streaming")
            yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"
            
    return StreamingResponse(sse_stream(), media_type="text/event-stream")

# Global variables for Jira OAuth state
jira_oauth_state = {
    "state_token": None,
    "access_token": None,
    "error": None,
    "server_thread": None,
    "httpd": None
}

ATLASSIAN_CLIENT_ID = os.getenv("ATLASSIAN_CLIENT_ID", "")
ATLASSIAN_CLIENT_SECRET = os.getenv("ATLASSIAN_CLIENT_SECRET", "")
ATLASSIAN_REDIRECT_URI = "http://localhost:8765/callback"
ATLASSIAN_SCOPES = "read:jira-work read:jira-user write:jira-work offline_access"

class ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True

class JiraOAuthHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, *_a, **_kw): pass
    def do_GET(self):
        url_parsed = urllib.parse.urlparse(self.path)
        if url_parsed.path != "/callback":
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found")
            return
            
        qs = url_parsed.query
        params = dict(urllib.parse.parse_qsl(qs))
        
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        
        state_token = jira_oauth_state["state_token"]
        if params.get("state") == state_token and "code" in params:
            try:
                resp = requests.post(
                    "https://auth.atlassian.com/oauth/token",
                    json={
                        "grant_type": "authorization_code",
                        "client_id": ATLASSIAN_CLIENT_ID,
                        "client_secret": ATLASSIAN_CLIENT_SECRET,
                        "code": params["code"],
                        "redirect_uri": ATLASSIAN_REDIRECT_URI,
                    },
                    headers={"Content-Type": "application/json"},
                    timeout=30,
                )
                if resp.status_code != 200:
                    logger.error(f"Atlassian token exchange failed status={resp.status_code} body={resp.text}")
                resp.raise_for_status()
                data = resp.json()
                jira_oauth_state["access_token"] = data["access_token"]
                self.wfile.write(b"<h2>Authentication successful! You can close this window.</h2>")
            except Exception as e:
                logger.error(f"Error exchanging Atlassian code: {e}")
                jira_oauth_state["error"] = str(e)
                self.wfile.write(f"<h2>Authentication failed: {str(e)}</h2>".encode())
        else:
            logger.error(f"Jira OAuth state mismatch or no code. Received state: {params.get('state')}, expected state: {state_token}")
            jira_oauth_state["error"] = f"State mismatch or no code received. Got: {params}"
            self.wfile.write(b"<h2>Authentication failed: Invalid state token or missing code.</h2>")

@app.get("/api/auth/jira/url")
def get_jira_auth_url():
    jira_oauth_state["access_token"] = None
    jira_oauth_state["error"] = None
    state_token = secrets.token_urlsafe(16)
    jira_oauth_state["state_token"] = state_token
    
    if jira_oauth_state["httpd"] is None:
        try:
            httpd = ReusableTCPServer(("0.0.0.0", 8765), JiraOAuthHandler)
            jira_oauth_state["httpd"] = httpd
            
            def serve():
                try:
                    httpd.serve_forever()
                except Exception:
                    pass
                finally:
                    jira_oauth_state["httpd"] = None
                    
            thread = threading.Thread(target=serve, daemon=True)
            thread.start()
            jira_oauth_state["server_thread"] = thread
            logger.info("Started local Jira OAuth callback server on port 8765")
        except Exception as e:
            logger.error(f"Failed to start Jira OAuth server: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to start redirect server: {e}")
            
    auth_url = (
        f"https://auth.atlassian.com/authorize?audience=api.atlassian.com"
        f"&client_id={ATLASSIAN_CLIENT_ID}"
        f"&scope={urllib.parse.quote(ATLASSIAN_SCOPES)}"
        f"&redirect_uri={urllib.parse.quote(ATLASSIAN_REDIRECT_URI)}"
        f"&state={state_token}"
        f"&response_type=code"
        f"&prompt=consent"
    )
    return {"auth_url": auth_url}

@app.get("/api/auth/jira/token")
def get_jira_auth_token():
    token = jira_oauth_state["access_token"]
    error = jira_oauth_state["error"]
    
    if token or error:
        httpd = jira_oauth_state["httpd"]
        if httpd:
            try:
                httpd.shutdown()
                httpd.server_close()
            except Exception:
                pass
            jira_oauth_state["httpd"] = None
            logger.info("Shut down local Jira OAuth callback server")
            
    if error:
        raise HTTPException(status_code=400, detail=error)
        
    return {"token": token}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)

