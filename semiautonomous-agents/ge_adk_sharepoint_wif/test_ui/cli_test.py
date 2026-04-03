#!/usr/bin/env python3
"""
CLI Test for Microsoft JWT -> ADK Agent -> WIF -> Discovery Engine flow.
Simulates how Agentspace passes JWT to ADK agent via session state.
"""
import os
import sys
import asyncio
import webbrowser
from urllib.parse import urlencode, urlparse, parse_qs
from http.server import HTTPServer, BaseHTTPRequestHandler

import requests
from dotenv import load_dotenv

# Add parent to path to import agent
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

# Configuration
ENTRA_CLIENT_ID = os.environ.get("ENTRA_CLIENT_ID", "")
ENTRA_TENANT_ID = os.environ.get("ENTRA_TENANT_ID", "")
REDIRECT_URI = os.environ.get("REDIRECT_URI", "http://localhost:8550/callback")
REDIRECT_PORT = int(REDIRECT_URI.split(":")[-1].split("/")[0])
AUTH_ID = os.environ.get("AUTH_ID", "sharepointauth")

# Global
captured_id_token = None


class OAuthCallbackHandler(BaseHTTPRequestHandler):
    def log_message(self, *args): pass

    def do_GET(self):
        global captured_id_token
        params = parse_qs(urlparse(self.path).query)

        if "code" in params:
            code = params["code"][0]
            token_url = f"https://login.microsoftonline.com/{ENTRA_TENANT_ID}/oauth2/v2.0/token"
            data = {
                "client_id": ENTRA_CLIENT_ID,
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": REDIRECT_URI,
                "scope": "openid profile email",
            }
            resp = requests.post(token_url, data=data, timeout=10)
            if resp.status_code == 200:
                captured_id_token = resp.json().get("id_token")
                self._respond("Success! Return to terminal.")
            else:
                self._respond(f"Error: {resp.text}")
        else:
            self._respond(f"Error: {params.get('error_description', 'Unknown')}")

    def _respond(self, msg):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(f"<html><body><h2>{msg}</h2></body></html>".encode())


def login_microsoft():
    """Open browser for Microsoft login and capture JWT."""
    global captured_id_token
    captured_id_token = None

    print("\n[1] Starting OAuth server on port", REDIRECT_PORT)
    server = HTTPServer(("localhost", REDIRECT_PORT), OAuthCallbackHandler)

    auth_url = (
        f"https://login.microsoftonline.com/{ENTRA_TENANT_ID}/oauth2/v2.0/authorize?"
        + urlencode({
            "client_id": ENTRA_CLIENT_ID,
            "response_type": "code",
            "redirect_uri": REDIRECT_URI,
            "scope": "openid profile email",
            "response_mode": "query",
            "prompt": "select_account",
        })
    )

    print("[2] Opening browser for login...")
    webbrowser.open(auth_url)

    print("[3] Waiting for callback...")
    server.handle_request()

    if captured_id_token:
        print(f"[4] Got ID token (length: {len(captured_id_token)})")
        return captured_id_token
    else:
        print("[4] Failed to get token")
        return None


async def run_agent_with_jwt(query: str, jwt_token: str):
    """
    Run the ADK agent with JWT in session state.
    This simulates how Agentspace passes the token to the agent.
    """
    from google.adk.sessions import InMemorySessionService
    from google.adk.runners import Runner
    from google.genai.types import Content, Part

    # Import our agent
    from agent import root_agent

    print(f"\n[ADK] Running agent with query: {query}")
    print(f"[ADK] JWT will be in session.state['temp:{AUTH_ID}']")

    # Create session service with initial state containing the JWT
    # This simulates what Agentspace does when it passes the OAuth token
    session_service = InMemorySessionService()

    # Create session with the JWT in state (simulating Agentspace behavior)
    initial_state = {
        f"temp:{AUTH_ID}": jwt_token,  # This is how Agentspace stores OAuth tokens
    }

    session = await session_service.create_session(
        app_name="test",
        user_id="test",
        session_id="test",
        state=initial_state,
    )

    print(f"[ADK] Session created with state keys: {list(session.state.keys())}")

    # Create runner
    runner = Runner(
        agent=root_agent,
        app_name="test",
        session_service=session_service,
    )

    # Run the agent
    content = Content(role="user", parts=[Part(text=query)])

    final_response = None
    async for event in runner.run_async(
        user_id="test",
        session_id="test",
        new_message=content,
    ):
        if event.is_final_response() and event.content and event.content.parts:
            final_response = event.content.parts[0].text

    return final_response


def main():
    print("=" * 60)
    print("ADK Agent Test: JWT -> session.state -> WIF -> Discovery Engine")
    print("=" * 60)
    print(f"Tenant: {ENTRA_TENANT_ID}")
    print(f"AUTH_ID: {AUTH_ID}")
    print(f"Token key: temp:{AUTH_ID}")
    print("=" * 60)

    # Check if JWT is provided as argument
    if len(sys.argv) > 1 and sys.argv[1].startswith("eyJ"):
        id_token = sys.argv[1]
        print(f"\nUsing provided JWT (length: {len(id_token)})")
    else:
        # Login to get JWT
        id_token = login_microsoft()
        if not id_token:
            print("Login failed!")
            sys.exit(1)

    # Interactive search loop using ADK agent
    print("\n" + "=" * 60)
    print("Ready! The ADK agent will:")
    print(f"  1. Extract JWT from tool_context.state['temp:{AUTH_ID}']")
    print("  2. Exchange via WIF/STS for GCP token")
    print("  3. Call Discovery Engine with dataStoreSpecs")
    print("Type 'quit' to exit.")
    print("=" * 60)

    while True:
        try:
            query = input("\nQuery: ").strip()
            if query.lower() in ("quit", "exit", "q"):
                break
            if not query:
                continue

            # Run agent with JWT in session state
            result = asyncio.run(run_agent_with_jwt(query, id_token))

            print("\n" + "-" * 40)
            print("AGENT RESPONSE:")
            print("-" * 40)
            print(result)
            print("-" * 40)

        except KeyboardInterrupt:
            break
        except EOFError:
            break
        except Exception as e:
            print(f"\nError: {e}")
            import traceback
            traceback.print_exc()

    print("\nDone!")


if __name__ == "__main__":
    main()
