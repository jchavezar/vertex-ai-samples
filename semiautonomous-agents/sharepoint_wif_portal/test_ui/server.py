"""
Test UI Server - Login and test InsightComparator agent with real JWT.

Provides:
1. Static HTML with MSAL login
2. /api/query endpoint that passes JWT to agent

Usage:
    cd test_ui
    uv run python server.py

Then open http://localhost:8080

Version: 1.0.0
Date: 2026-04-04
"""
import os
import sys
from pathlib import Path

# Add parent to path for agent imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from dotenv import load_dotenv

# Load env from parent directory
load_dotenv(Path(__file__).parent.parent / ".env")

# Required for ADK
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")

app = FastAPI(title="InsightComparator Test UI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Config from env
PROJECT_ID = os.environ.get("PROJECT_ID", "")
PROJECT_NUMBER = os.environ.get("PROJECT_NUMBER", "")
LOCATION = os.environ.get("LOCATION", "us-central1")
REASONING_ENGINE_RES = os.environ.get("REASONING_ENGINE_RES", "")
OAUTH_CLIENT_ID = os.environ.get("OAUTH_CLIENT_ID", "")
TENANT_ID = os.environ.get("TENANT_ID", "")


class QueryRequest(BaseModel):
    query: str
    token: str = None


@app.get("/", response_class=HTMLResponse)
async def index():
    """Serve the test UI."""
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>InsightComparator Test</title>
    <script src="https://alcdn.msauth.net/browser/2.38.0/js/msal-browser.min.js"></script>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: #f5f5f5;
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{ max-width: 900px; margin: 0 auto; }}
        h1 {{ color: #333; margin-bottom: 20px; }}
        .card {{
            background: white;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        .status {{
            padding: 10px 15px;
            border-radius: 4px;
            margin-bottom: 15px;
        }}
        .status.logged-out {{ background: #fff3cd; color: #856404; }}
        .status.logged-in {{ background: #d4edda; color: #155724; }}
        .status.error {{ background: #f8d7da; color: #721c24; }}
        button {{
            background: #4285f4;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
            margin-right: 10px;
            margin-bottom: 5px;
        }}
        button:hover {{ background: #3367d6; }}
        button:disabled {{ background: #ccc; cursor: not-allowed; }}
        button.secondary {{ background: #6c757d; }}
        button.secondary:hover {{ background: #5a6268; }}
        button.copy {{ background: #28a745; padding: 5px 10px; font-size: 12px; }}
        button.copy:hover {{ background: #218838; }}
        .query-section {{ margin-top: 20px; }}
        textarea {{
            width: 100%;
            padding: 12px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 14px;
            resize: vertical;
            min-height: 80px;
        }}
        .response {{
            background: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 4px;
            padding: 15px;
            margin-top: 15px;
            white-space: pre-wrap;
            font-family: monospace;
            font-size: 13px;
            max-height: 500px;
            overflow-y: auto;
        }}
        .debug-box {{
            background: #1e1e1e;
            color: #d4d4d4;
            border-radius: 4px;
            padding: 15px;
            margin-top: 10px;
            white-space: pre-wrap;
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 11px;
            max-height: 200px;
            overflow-y: auto;
            position: relative;
        }}
        .debug-box .copy-btn {{
            position: absolute;
            top: 5px;
            right: 5px;
        }}
        .info {{ font-size: 12px; color: #666; margin-top: 10px; }}
        .token-info {{
            font-size: 11px;
            color: #888;
            margin-top: 5px;
            word-break: break-all;
        }}
        .collapsible {{
            cursor: pointer;
            user-select: none;
        }}
        .collapsible:after {{
            content: ' [+]';
            font-size: 10px;
        }}
        .collapsible.active:after {{
            content: ' [-]';
        }}
        .hidden {{ display: none; }}
        .copied {{ background: #28a745 !important; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>InsightComparator Test UI</h1>

        <div class="card">
            <div id="status" class="status logged-out">Not logged in</div>
            <button id="loginBtn" onclick="login()">Login with Microsoft</button>
            <button id="logoutBtn" onclick="logout()" class="secondary" style="display:none">Logout</button>
            <button onclick="copyDebugInfo()" class="copy">Copy Debug Info</button>
            <div id="tokenInfo" class="token-info"></div>

            <h4 class="collapsible" onclick="toggleSection('debugSection')" style="margin-top:15px">Debug Info</h4>
            <div id="debugSection" class="hidden">
                <div class="debug-box" id="debugBox">
                    <button onclick="copyElement('debugBox')" class="copy copy-btn">Copy</button>
Loading...
                </div>
            </div>
        </div>

        <div class="card query-section">
            <h3 style="margin-bottom:15px">Test Agent</h3>
            <textarea id="query" placeholder="Enter your query...">Compare internal security policies with external best practices</textarea>
            <div style="margin-top:10px">
                <button id="queryBtn" onclick="sendQuery()" disabled>Send Query</button>
                <button onclick="copyElement('response')" class="copy">Copy Response</button>
                <span class="info">Requires login for SharePoint access</span>
            </div>
            <div id="response" class="response" style="display:none"></div>
        </div>

        <div class="card">
            <h4 class="collapsible" onclick="toggleSection('logSection')">Event Log</h4>
            <div id="logSection" class="hidden">
                <button onclick="copyElement('eventLog')" class="copy" style="margin-top:10px">Copy Log</button>
                <button onclick="clearLog()" class="secondary" style="padding:5px 10px;font-size:12px">Clear</button>
                <div class="debug-box" id="eventLog" style="margin-top:10px;max-height:300px"></div>
            </div>
        </div>

        <div class="card">
            <h3 style="margin-bottom:10px">Configuration</h3>
            <div class="info">
                <strong>Client ID:</strong> {OAUTH_CLIENT_ID}<br>
                <strong>Tenant:</strong> {TENANT_ID}<br>
                <strong>Agent:</strong> {REASONING_ENGINE_RES.split('/')[-1] if REASONING_ENGINE_RES else 'Not configured'}<br>
                <strong>Redirect URI:</strong> <span id="redirectUri"></span>
            </div>
        </div>
    </div>

    <script>
        // Show redirect URI
        document.getElementById("redirectUri").textContent = window.location.origin;

        const msalConfig = {{
            auth: {{
                clientId: "{OAUTH_CLIENT_ID}",
                authority: "https://login.microsoftonline.com/{TENANT_ID}",
                redirectUri: window.location.origin
            }},
            cache: {{ cacheLocation: "sessionStorage" }},
            system: {{
                loggerOptions: {{
                    loggerCallback: (level, message, containsPii) => {{
                        log("[MSAL] " + message);
                    }},
                    logLevel: msal.LogLevel.Verbose
                }}
            }}
        }};

        const msalInstance = new msal.PublicClientApplication(msalConfig);
        let currentToken = null;
        let currentAccount = null;
        let tokenClaims = null;

        function log(msg) {{
            const el = document.getElementById("eventLog");
            const time = new Date().toISOString().substr(11, 8);
            el.textContent = `[${{time}}] ${{msg}}\n` + el.textContent;
            console.log(msg);
        }}

        function toggleSection(id) {{
            const el = document.getElementById(id);
            el.classList.toggle("hidden");
            el.previousElementSibling.classList.toggle("active");
        }}

        function clearLog() {{
            document.getElementById("eventLog").textContent = "";
        }}

        function copyElement(id) {{
            const el = document.getElementById(id);
            const text = el.textContent || el.innerText;
            navigator.clipboard.writeText(text).then(() => {{
                log("Copied to clipboard: " + id);
            }});
        }}

        function parseJwt(token) {{
            try {{
                const base64Url = token.split('.')[1];
                const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
                const jsonPayload = decodeURIComponent(atob(base64).split('').map(c => {{
                    return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
                }}).join(''));
                return JSON.parse(jsonPayload);
            }} catch (e) {{
                return {{ error: e.message }};
            }}
        }}

        function updateDebugInfo() {{
            const debug = {{
                timestamp: new Date().toISOString(),
                url: window.location.href,
                origin: window.location.origin,
                clientId: "{OAUTH_CLIENT_ID}",
                tenant: "{TENANT_ID}",
                account: currentAccount ? {{
                    username: currentAccount.username,
                    tenantId: currentAccount.tenantId,
                    homeAccountId: currentAccount.homeAccountId
                }} : null,
                token: currentToken ? {{
                    length: currentToken.length,
                    preview: currentToken.substring(0, 50) + "...",
                    claims: tokenClaims
                }} : null,
                msalAccounts: msalInstance.getAllAccounts().map(a => a.username)
            }};
            document.getElementById("debugBox").innerHTML =
                '<button onclick="copyElement(\\'debugBox\\')" class="copy copy-btn">Copy</button>' +
                JSON.stringify(debug, null, 2);
        }}

        function copyDebugInfo() {{
            const debug = {{
                timestamp: new Date().toISOString(),
                url: window.location.href,
                clientId: "{OAUTH_CLIENT_ID}",
                tenant: "{TENANT_ID}",
                account: currentAccount ? currentAccount.username : null,
                tokenLength: currentToken ? currentToken.length : 0,
                tokenClaims: tokenClaims,
                fullToken: currentToken,
                eventLog: document.getElementById("eventLog").textContent
            }};
            navigator.clipboard.writeText(JSON.stringify(debug, null, 2)).then(() => {{
                alert("Debug info copied to clipboard!");
            }});
        }}

        // Initialize
        log("Initializing MSAL...");
        log("Redirect URI: " + window.location.origin);

        msalInstance.initialize().then(() => {{
            log("MSAL initialized");
            updateDebugInfo();
            const accounts = msalInstance.getAllAccounts();
            log("Found " + accounts.length + " cached account(s)");
            if (accounts.length > 0) {{
                log("Attempting silent token acquisition...");
                acquireToken(accounts[0]);
            }}
        }}).catch(err => {{
            log("MSAL init error: " + err.message);
        }});

        async function login() {{
            log("Starting login popup...");
            try {{
                const response = await msalInstance.loginPopup({{
                    scopes: ["openid", "profile", "email", "api://{OAUTH_CLIENT_ID}/user_impersonation"]
                }});
                log("Login successful: " + response.account.username);
                await acquireToken(response.account);
            }} catch (error) {{
                log("LOGIN ERROR: " + error.message);
                console.error("Full error:", error);
                const status = document.getElementById("status");
                status.className = "status error";
                status.textContent = "Login failed: " + error.message;
                updateDebugInfo();
            }}
        }}

        async function acquireToken(account) {{
            log("Acquiring token for: " + account.username);
            try {{
                const response = await msalInstance.acquireTokenSilent({{
                    scopes: ["api://{OAUTH_CLIENT_ID}/user_impersonation"],
                    account: account
                }});
                log("Token acquired silently");
                currentToken = response.accessToken;
                currentAccount = account;
                tokenClaims = parseJwt(response.accessToken);
                log("Token audience: " + (tokenClaims.aud || "unknown"));
                updateUI(account, response.accessToken);
            }} catch (error) {{
                log("Silent token failed: " + error.message);
                log("Trying interactive...");
                try {{
                    const response = await msalInstance.acquireTokenPopup({{
                        scopes: ["api://{OAUTH_CLIENT_ID}/user_impersonation"]
                    }});
                    log("Token acquired via popup");
                    currentToken = response.accessToken;
                    currentAccount = response.account;
                    tokenClaims = parseJwt(response.accessToken);
                    updateUI(response.account, response.accessToken);
                }} catch (popupError) {{
                    log("POPUP ERROR: " + popupError.message);
                    const status = document.getElementById("status");
                    status.className = "status error";
                    status.textContent = "Token error: " + popupError.message;
                }}
            }}
            updateDebugInfo();
        }}

        function updateUI(account, token) {{
            log("Updating UI for: " + account.username);
            const status = document.getElementById("status");
            status.className = "status logged-in";
            status.textContent = "Logged in as: " + account.username;

            document.getElementById("loginBtn").style.display = "none";
            document.getElementById("logoutBtn").style.display = "inline-block";
            document.getElementById("queryBtn").disabled = false;

            const tokenInfo = document.getElementById("tokenInfo");
            tokenInfo.innerHTML = `
                <strong>Token:</strong> ${{token.substring(0, 40)}}... (${{token.length}} chars)<br>
                <strong>Audience:</strong> ${{tokenClaims?.aud || 'unknown'}}<br>
                <strong>Expires:</strong> ${{tokenClaims?.exp ? new Date(tokenClaims.exp * 1000).toLocaleString() : 'unknown'}}
            `;

            // Save token for CLI testing
            fetch("/api/save-token", {{
                method: "POST",
                headers: {{ "Content-Type": "application/json" }},
                body: JSON.stringify({{ token: token }})
            }}).then(() => log("Token saved to /tmp/entra_token.txt"));

            updateDebugInfo();
        }}

        function logout() {{
            log("Logging out...");
            msalInstance.logoutPopup().then(() => {{
                currentToken = null;
                currentAccount = null;
                tokenClaims = null;
                document.getElementById("status").className = "status logged-out";
                document.getElementById("status").textContent = "Not logged in";
                document.getElementById("loginBtn").style.display = "inline-block";
                document.getElementById("logoutBtn").style.display = "none";
                document.getElementById("queryBtn").disabled = true;
                document.getElementById("tokenInfo").textContent = "";
                log("Logged out");
                updateDebugInfo();
            }});
        }}

        async function sendQuery() {{
            const query = document.getElementById("query").value;
            const responseDiv = document.getElementById("response");
            const queryBtn = document.getElementById("queryBtn");

            if (!query.trim()) return;

            log("Sending query: " + query.substring(0, 50) + "...");
            responseDiv.style.display = "block";
            responseDiv.textContent = "Querying agent...";
            queryBtn.disabled = true;

            try {{
                const response = await fetch("/api/query", {{
                    method: "POST",
                    headers: {{ "Content-Type": "application/json" }},
                    body: JSON.stringify({{ query: query, token: currentToken }})
                }});

                log("Response status: " + response.status);

                const reader = response.body.getReader();
                const decoder = new TextDecoder();
                responseDiv.textContent = "";

                while (true) {{
                    const {{ done, value }} = await reader.read();
                    if (done) break;
                    const text = decoder.decode(value);
                    responseDiv.textContent += text;
                    responseDiv.scrollTop = responseDiv.scrollHeight;
                }}
                log("Query complete");
            }} catch (error) {{
                log("QUERY ERROR: " + error.message);
                responseDiv.textContent = "Error: " + error.message;
            }} finally {{
                queryBtn.disabled = false;
            }}
        }}
    </script>
</body>
</html>"""
    return HTMLResponse(content=html)


@app.post("/api/save-token")
async def save_token(request: Request):
    """Save token for CLI testing."""
    data = await request.json()
    token = data.get("token", "")
    if token:
        with open("/tmp/entra_token.txt", "w") as f:
            f.write(token)
        return {"status": "saved", "path": "/tmp/entra_token.txt"}
    return {"status": "no token"}


@app.post("/api/query")
async def query_agent(req: QueryRequest):
    """
    Query the ADK agent with JWT in session state.
    This simulates exactly what Gemini Enterprise does when invoking the agent.
    """
    if not req.token:
        raise HTTPException(400, "Token required - please login first")

    AUTH_ID = os.environ.get("AUTH_ID", "sharepointauth2")

    async def generate():
        try:
            yield f"[Mode: ADK Agent with JWT in session.state]\n"
            yield f"[Token: {len(req.token)} chars]\n"
            yield f"[State Key: temp:{AUTH_ID}]\n\n"

            # Import ADK components
            from google.adk.sessions import InMemorySessionService
            from google.adk.runners import Runner
            from google.genai.types import Content, Part

            # Import our agent
            from agent import root_agent

            yield f"[Agent: {root_agent.name}]\n"
            yield f"[Model: {root_agent.model}]\n"
            yield f"[Tools: {[t.__name__ for t in root_agent.tools]}]\n\n"

            # Create session service
            session_service = InMemorySessionService()

            # Create session with JWT in state - this is what GE does
            initial_state = {
                f"temp:{AUTH_ID}": req.token,  # GE stores OAuth tokens as temp:{auth_id}
            }

            session = await session_service.create_session(
                app_name="test_ui",
                user_id="test_user",
                session_id="test_session",
                state=initial_state,
            )

            yield f"[Session created with state keys: {list(session.state.keys())}]\n"
            yield "-" * 50 + "\n\n"

            # Create runner
            runner = Runner(
                agent=root_agent,
                app_name="test_ui",
                session_service=session_service,
            )

            # Create message
            content = Content(role="user", parts=[Part(text=req.query)])

            # Run the agent and stream response
            async for event in runner.run_async(
                user_id="test_user",
                session_id="test_session",
                new_message=content,
            ):
                if hasattr(event, 'content') and event.content:
                    if hasattr(event.content, 'parts'):
                        for part in event.content.parts:
                            if hasattr(part, 'text') and part.text:
                                yield part.text

            yield "\n\n" + "-" * 50
            yield "\n[ADK Agent test complete - this simulates GE behavior]"

        except Exception as e:
            import traceback
            yield f"\n[ERROR] {str(e)}\n{traceback.format_exc()}"

    return StreamingResponse(generate(), media_type="text/plain")


def main():
    """Run the test server."""
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║           InsightComparator Test UI                          ║
╠══════════════════════════════════════════════════════════════╣
║  URL:      http://localhost:8080                             ║
║  Client:   {OAUTH_CLIENT_ID[:20]}...                      ║
║  Agent:    {REASONING_ENGINE_RES.split('/')[-1] if REASONING_ENGINE_RES else 'Not set'}                              ║
╠══════════════════════════════════════════════════════════════╣
║  1. Click "Login with Microsoft"                             ║
║  2. Enter a query and click "Send Query"                     ║
║  3. Token saved to /tmp/entra_token.txt for CLI testing      ║
╚══════════════════════════════════════════════════════════════╝
""")
    uvicorn.run(app, host="0.0.0.0", port=8080)


if __name__ == "__main__":
    main()
