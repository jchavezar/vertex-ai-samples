
import os
import sys
import json
import time
import base64
import uvicorn
import httpx
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv
import urllib.parse
import threading
import signal

# Add current directory to path
sys.path.append(os.getcwd())

load_dotenv()

# Constants
TOKEN_FILE = "factset_tokens.json"
FS_CLIENT_ID = os.getenv("FS_CLIENT_ID")
FS_CLIENT_SECRET = os.getenv("FS_CLIENT_SECRET")
FS_REDIRECT_URI = os.getenv("FS_REDIRECT_URI", "http://localhost:8001/auth/factset/callback")
FS_AUTH_URL = "https://auth.factset.com/as/authorization.oauth2"
FS_TOKEN_URL = "https://auth.factset.com/as/token.oauth2"

if not FS_CLIENT_ID or not FS_CLIENT_SECRET:
    print("ERROR: FS_CLIENT_ID or FS_CLIENT_SECRET not found in .env")
    sys.exit(1)

app = FastAPI()

# Global event to stop server
stop_event = threading.Event()

def save_tokens(tokens):
    try:
        current = {}
        if os.path.exists(TOKEN_FILE):
            with open(TOKEN_FILE, 'r') as f:
                current = json.load(f)
        
        # Update default_chat session
        current["default_chat"] = {
            "token": tokens.get("access_token"),
            "refresh_token": tokens.get("refresh_token"),
            "expires_at": time.time() + tokens.get("expires_in", 900),
            "created_at": time.time()
        }
        
        with open(TOKEN_FILE, 'w') as f:
            json.dump(current, f, indent=2)
        print(f"Tokens saved to {TOKEN_FILE}")
    except Exception as e:
        print(f"Failed to save tokens: {e}")

@app.get("/auth/factset/callback")
async def auth_callback(code: str):
    print(f"\nReceived Auth Code: {code[:10]}...")
    
    # Exchange for Token
    auth_str = f"{FS_CLIENT_ID}:{FS_CLIENT_SECRET}"
    b64_auth = base64.b64encode(auth_str.encode()).decode()
    
    headers = {
        "Authorization": f"Basic {b64_auth}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    payload = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": FS_REDIRECT_URI
    }

    async with httpx.AsyncClient() as client:
        print("Exchanging code for token...")
        response = await client.post(FS_TOKEN_URL, data=payload, headers=headers)
        
        if response.status_code == 200:
            tokens = response.json()
            save_tokens(tokens)
            
            # Signal to stop
            stop_timer = threading.Timer(2.0, lambda: os.kill(os.getpid(), signal.SIGINT))
            stop_timer.start()
            
            return HTMLResponse("""
            <h1>Authentication Successful!</h1>
            <p>Tokens have been saved to <code>factset_tokens.json</code>.</p>
            <p>You can close this window and return to the terminal.</p>
            <script>window.close();</script>
            """)
        else:
            print(f"Token Exchange Failed: {response.text}")
            return HTMLResponse(f"<h1>Error</h1><p>{response.text}</p>")

def print_auth_url():
    params = {
        "response_type": "code",
        "client_id": FS_CLIENT_ID,
        "redirect_uri": FS_REDIRECT_URI,
        "scope": "mcp",
        "state": "auth_script",
        "prompt": "consent"
    }
    query_string = urllib.parse.urlencode(params)
    auth_url = f"{FS_AUTH_URL}?{query_string}"
    
    print("\n" + "="*60)
    print("PLEASE AUTHENTICATE HERE:")
    print(auth_url)
    print("="*60 + "\n")
    print("Waiting for callback on port 8001...")

if __name__ == "__main__":
    print_auth_url()
    try:
        uvicorn.run(app, host="0.0.0.0", port=8001)
    except Exception as e:
        print(f"Error starting server: {e}")
        print("NOTE: If port 8001 is busy, please stop the running backend.")
