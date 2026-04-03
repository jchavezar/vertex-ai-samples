"""
Browser-based Test UI for Microsoft JWT -> ADK Agent -> WIF -> Discovery Engine
SPA token exchange happens in browser (JavaScript)
"""
import os
import sys
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
import uvicorn
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv()

# Configuration
ENTRA_CLIENT_ID = os.environ.get("ENTRA_CLIENT_ID", "")
ENTRA_TENANT_ID = os.environ.get("ENTRA_TENANT_ID", "")
AUTH_ID = os.environ.get("AUTH_ID", "sharepointauth")
PORT = int(os.environ.get("PORT", "5177"))
REDIRECT_URI = f"http://localhost:{PORT}"

app = FastAPI(title="SharePoint WIF Test")

# Store JWT (set by frontend after token exchange)
stored_jwt = {"token": None}


@app.get("/", response_class=HTMLResponse)
async def home():
    # All OAuth logic happens in JavaScript for SPA
    return f"""
<!DOCTYPE html>
<html>
<head>
    <title>SharePoint WIF Test</title>
    <style>
        * {{ box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', Arial, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #eee;
            margin: 0;
            padding: 20px;
            min-height: 100vh;
        }}
        .container {{ max-width: 900px; margin: 0 auto; }}
        h1 {{ color: #4cc9f0; margin-bottom: 5px; }}
        .subtitle {{ color: #888; margin-bottom: 30px; }}
        .card {{
            background: rgba(255,255,255,0.05);
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            border: 1px solid rgba(255,255,255,0.1);
        }}
        .card h3 {{ color: #4cc9f0; margin-top: 0; }}
        button {{
            background: #4361ee;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 16px;
            margin-right: 10px;
        }}
        button:hover {{ background: #3a56d4; }}
        button.success {{ background: #06d6a0; }}
        textarea, input[type="text"] {{
            width: 100%;
            padding: 12px;
            border-radius: 6px;
            border: 1px solid #444;
            background: #1a1a2e;
            color: #eee;
            font-family: monospace;
        }}
        .jwt-box {{ height: 100px; font-size: 12px; }}
        .response-box {{ height: 300px; font-size: 14px; }}
        .status {{
            padding: 10px 15px;
            border-radius: 6px;
            margin: 15px 0;
            font-weight: bold;
        }}
        .timer {{
            font-family: monospace;
            font-size: 14px;
            color: #4cc9f0;
            margin-left: 10px;
        }}
        .status.ready {{ background: rgba(6, 214, 160, 0.2); color: #06d6a0; }}
        .status.waiting {{ background: rgba(255, 190, 11, 0.2); color: #ffbe0b; }}
        .status.error {{ background: rgba(239, 71, 111, 0.2); color: #ef476f; }}
        .row {{ display: flex; gap: 10px; }}
        .row input {{ flex: 1; }}
        label {{ display: block; margin-bottom: 8px; color: #aaa; }}
        pre {{ color: #888; font-size: 11px; white-space: pre-wrap; max-height: 150px; overflow: auto; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>SharePoint WIF Test</h1>
        <p class="subtitle">Microsoft JWT -> ADK Agent -> WIF/STS -> Discovery Engine</p>

        <div class="card">
            <h3>Step 1: Get Microsoft JWT</h3>
            <button onclick="login()">Login with Microsoft</button>
            <div id="status" class="status waiting">Not logged in</div>

            <label>JWT Token:</label>
            <textarea id="jwt" class="jwt-box" placeholder="JWT appears here after login..."></textarea>
        </div>

        <div class="card">
            <h3>Step 2: Query via ADK Agent</h3>
            <div class="row">
                <input type="text" id="query" placeholder="Ask about SharePoint documents..." onkeypress="if(event.key==='Enter')search()">
                <button class="success" onclick="search()">Search</button>
                <span id="timer" class="timer"></span>
            </div>
            <label style="margin-top:15px">Response:</label>
            <textarea id="response" class="response-box" readonly></textarea>
        </div>

        <div class="card">
            <h3>Logs</h3>
            <pre id="logs">Ready...</pre>
        </div>
    </div>

    <script>
        const CLIENT_ID = "{ENTRA_CLIENT_ID}";
        const TENANT_ID = "{ENTRA_TENANT_ID}";
        const REDIRECT_URI = "{REDIRECT_URI}";

        let codeVerifier = null;

        function log(msg) {{
            document.getElementById('logs').textContent = new Date().toLocaleTimeString() + ' ' + msg + '\\n' + document.getElementById('logs').textContent;
        }}

        function generatePKCE() {{
            const array = new Uint8Array(64);
            crypto.getRandomValues(array);
            codeVerifier = btoa(String.fromCharCode(...array)).replace(/\\+/g, '-').replace(/\\//g, '_').replace(/=+$/, '').substring(0, 128);

            return crypto.subtle.digest('SHA-256', new TextEncoder().encode(codeVerifier))
                .then(hash => btoa(String.fromCharCode(...new Uint8Array(hash))).replace(/\\+/g, '-').replace(/\\//g, '_').replace(/=+$/, ''));
        }}

        async function login() {{
            log('Generating PKCE...');
            const codeChallenge = await generatePKCE();

            const params = new URLSearchParams({{
                client_id: CLIENT_ID,
                response_type: 'code',
                redirect_uri: REDIRECT_URI,
                scope: 'openid profile email',
                prompt: 'select_account',
                code_challenge: codeChallenge,
                code_challenge_method: 'S256'
            }});

            // Store verifier in sessionStorage
            sessionStorage.setItem('pkce_verifier', codeVerifier);

            log('Redirecting to Microsoft login...');
            window.location.href = `https://login.microsoftonline.com/${{TENANT_ID}}/oauth2/v2.0/authorize?${{params}}`;
        }}

        async function exchangeCode(code) {{
            const verifier = sessionStorage.getItem('pkce_verifier');
            if (!verifier) {{
                log('ERROR: No PKCE verifier found');
                return null;
            }}

            log('Exchanging code for token (SPA cross-origin)...');

            const params = new URLSearchParams({{
                client_id: CLIENT_ID,
                grant_type: 'authorization_code',
                code: code,
                redirect_uri: REDIRECT_URI,
                scope: 'openid profile email',
                code_verifier: verifier
            }});

            try {{
                const resp = await fetch(`https://login.microsoftonline.com/${{TENANT_ID}}/oauth2/v2.0/token`, {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/x-www-form-urlencoded' }},
                    body: params
                }});

                const data = await resp.json();
                sessionStorage.removeItem('pkce_verifier');

                if (data.id_token) {{
                    log('Got ID token!');
                    return data.id_token;
                }} else {{
                    log('Token error: ' + JSON.stringify(data));
                    return null;
                }}
            }} catch (e) {{
                log('Exchange error: ' + e.message);
                return null;
            }}
        }}

        let timerInterval = null;

        async function search() {{
            const query = document.getElementById('query').value.trim();
            const jwt = document.getElementById('jwt').value.trim();
            if (!query || !jwt) {{ alert('Need query and JWT'); return; }}

            log('Sending to ADK agent...');
            document.getElementById('response').value = 'Processing...';

            // Start timer
            const startTime = performance.now();
            const timerEl = document.getElementById('timer');
            if (timerInterval) clearInterval(timerInterval);

            timerInterval = setInterval(() => {{
                const elapsed = performance.now() - startTime;
                timerEl.textContent = (elapsed / 1000).toFixed(3) + 's';
            }}, 10);

            try {{
                const resp = await fetch('/search', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ query, jwt }})
                }});
                const data = await resp.json();

                // Stop timer and show final time
                clearInterval(timerInterval);
                const finalTime = performance.now() - startTime;
                timerEl.textContent = (finalTime / 1000).toFixed(3) + 's';

                document.getElementById('response').value = data.response || data.error || JSON.stringify(data);
                log('Done in ' + (finalTime / 1000).toFixed(3) + 's');
            }} catch (e) {{
                clearInterval(timerInterval);
                document.getElementById('response').value = 'Error: ' + e.message;
                log('Error: ' + e.message);
            }}
        }}

        // On page load, check for code in URL
        window.onload = async function() {{
            const params = new URLSearchParams(window.location.search);
            const code = params.get('code');

            if (code) {{
                log('Found authorization code');
                // Clean URL
                window.history.replaceState({{}}, '', '/');

                const token = await exchangeCode(code);
                if (token) {{
                    document.getElementById('jwt').value = token;
                    document.getElementById('status').className = 'status ready';
                    document.getElementById('status').textContent = 'Ready! JWT loaded (' + token.length + ' chars)';

                    // Save to server
                    await fetch('/save-token', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify({{ token }})
                    }});
                }} else {{
                    document.getElementById('status').className = 'status error';
                    document.getElementById('status').textContent = 'Token exchange failed';
                }}
            }}
        }};
    </script>
</body>
</html>
"""


@app.post("/save-token")
async def save_token(request: Request):
    data = await request.json()
    stored_jwt["token"] = data.get("token")
    return JSONResponse({"ok": True})


@app.get("/token")
async def get_token():
    return JSONResponse({"token": stored_jwt["token"]})


@app.post("/search")
async def search(request: Request):
    data = await request.json()
    query = data.get("query", "")
    jwt = data.get("jwt", "")

    if not query or not jwt:
        return JSONResponse({"error": "Missing query or jwt"})

    try:
        from google.adk.sessions import InMemorySessionService
        from google.adk.runners import Runner
        from google.genai.types import Content, Part
        from agent import root_agent

        session_service = InMemorySessionService()
        # Use key WITHOUT temp: prefix for local testing
        # (temp: keys are runtime-only in Agentspace, not stored in session state)
        await session_service.create_session(
            app_name="test",
            user_id="test",
            session_id="test",
            state={AUTH_ID: jwt},
        )

        runner = Runner(agent=root_agent, app_name="test", session_service=session_service)
        content = Content(role="user", parts=[Part(text=query)])

        result = None
        async for event in runner.run_async(user_id="test", session_id="test", new_message=content):
            if event.is_final_response() and event.content and event.content.parts:
                result = event.content.parts[0].text

        return JSONResponse({"response": result or "No response"})

    except Exception as e:
        import traceback
        return JSONResponse({"error": str(e), "trace": traceback.format_exc()})


if __name__ == "__main__":
    print(f"""
=====================================
SharePoint WIF Test (SPA Mode)
=====================================
URL: http://localhost:{PORT}
=====================================
""")
    uvicorn.run(app, host="0.0.0.0", port=PORT)
