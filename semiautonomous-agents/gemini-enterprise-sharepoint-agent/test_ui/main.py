"""
Test UI: Microsoft Login -> ADK Agent -> WIF -> Discovery Engine
"""
import os
import sys
import asyncio
import webbrowser
import threading
from urllib.parse import urlencode, urlparse, parse_qs
from http.server import HTTPServer, BaseHTTPRequestHandler

import flet as ft
import requests
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv()

# Configuration
ENTRA_CLIENT_ID = os.environ.get("ENTRA_CLIENT_ID", "")
ENTRA_TENANT_ID = os.environ.get("ENTRA_TENANT_ID", "")
REDIRECT_URI = os.environ.get("REDIRECT_URI", "http://localhost:5177")
uri_parts = REDIRECT_URI.replace("http://", "").replace("https://", "")
REDIRECT_PORT = int(uri_parts.split(":")[1].split("/")[0]) if ":" in uri_parts else 80
AUTH_ID = os.environ.get("AUTH_ID", "sharepointauth")

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
                self._respond("Success! Close this window.")
            else:
                self._respond(f"Error: {resp.text[:200]}")
        else:
            self._respond("Error: No code received")

    def _respond(self, msg):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(f"<html><body><h2>{msg}</h2></body></html>".encode())


async def run_agent_query(query: str, jwt_token: str) -> str:
    from google.adk.sessions import InMemorySessionService
    from google.adk.runners import Runner
    from google.genai.types import Content, Part
    from agent import root_agent

    session_service = InMemorySessionService()
    # Use key WITHOUT temp: prefix for local testing
    # (temp: keys are runtime-only in Agentspace, not stored in session state)
    await session_service.create_session(
        app_name="test", user_id="test", session_id="test",
        state={AUTH_ID: jwt_token},
    )

    runner = Runner(agent=root_agent, app_name="test", session_service=session_service)
    content = Content(role="user", parts=[Part(text=query)])

    result = None
    async for event in runner.run_async(user_id="test", session_id="test", new_message=content):
        if event.is_final_response() and event.content and event.content.parts:
            result = event.content.parts[0].text
    return result or "No response"


def main(page: ft.Page):
    page.title = "SharePoint WIF Test"
    page.theme_mode = ft.ThemeMode.DARK
    page.window.width = 900
    page.window.height = 800
    page.padding = 20

    state = {"jwt": None}

    # UI Elements
    status = ft.Text("Paste JWT or click Login", size=16, color=ft.Colors.ORANGE_400)

    # JWT input for manual paste
    jwt_input = ft.TextField(
        label="Paste JWT here (for troubleshooting)",
        multiline=True,
        min_lines=3,
        max_lines=5,
        width=700,
        hint_text="eyJhbGciOiJSUzI1NiIs..."
    )

    use_jwt_btn = ft.FilledButton("Use this JWT", disabled=False)

    response_box = ft.TextField(
        label="Response", multiline=True, min_lines=10, read_only=True, width=700
    )
    query_input = ft.TextField(label="Your question", width=500, disabled=True)
    search_btn = ft.FilledButton("Search", disabled=True)

    def use_pasted_jwt(e):
        jwt = jwt_input.value.strip()
        if jwt and jwt.startswith("eyJ"):
            state["jwt"] = jwt
            status.value = f"JWT loaded! ({len(jwt)} chars) - Ready to search"
            status.color = ft.Colors.GREEN_400
            query_input.disabled = False
            search_btn.disabled = False
            jwt_input.border_color = ft.Colors.GREEN_400
        else:
            status.value = "Invalid JWT - must start with 'eyJ'"
            status.color = ft.Colors.RED_400
        page.update()

    def login_clicked(e):
        global captured_id_token
        captured_id_token = None

        status.value = f"Opening browser... (redirect: {REDIRECT_URI})"
        status.color = ft.Colors.YELLOW_400
        page.update()

        def run_server():
            server = HTTPServer(("localhost", REDIRECT_PORT), OAuthCallbackHandler)
            server.handle_request()

        t = threading.Thread(target=run_server, daemon=True)
        t.start()

        auth_url = (
            f"https://login.microsoftonline.com/{ENTRA_TENANT_ID}/oauth2/v2.0/authorize?"
            + urlencode({
                "client_id": ENTRA_CLIENT_ID,
                "response_type": "code",
                "redirect_uri": REDIRECT_URI,
                "scope": "openid profile email",
                "prompt": "select_account",
            })
        )
        webbrowser.open(auth_url)

        status.value = "Waiting for login..."
        page.update()

        t.join(timeout=120)

        if captured_id_token:
            state["jwt"] = captured_id_token
            jwt_input.value = captured_id_token  # Show it for reference
            status.value = f"Logged in! JWT ready ({len(captured_id_token)} chars)"
            status.color = ft.Colors.GREEN_400
            query_input.disabled = False
            search_btn.disabled = False
            login_btn.disabled = True
        else:
            status.value = "Login failed or timed out"
            status.color = ft.Colors.RED_400
        page.update()

    def search_clicked(e):
        if not state["jwt"] or not query_input.value.strip():
            return

        status.value = "Searching via ADK Agent..."
        status.color = ft.Colors.CYAN_400
        response_box.value = "Agent processing...\n- Extracting JWT from tool_context.state\n- WIF/STS exchange\n- Calling Discovery Engine"
        search_btn.disabled = True
        page.update()

        try:
            loop = asyncio.new_event_loop()
            result = loop.run_until_complete(run_agent_query(query_input.value, state["jwt"]))
            loop.close()
            response_box.value = result
            status.value = "Done!"
            status.color = ft.Colors.GREEN_400
        except Exception as ex:
            response_box.value = f"Error: {ex}\n\n"
            import traceback
            response_box.value += traceback.format_exc()
            status.value = "Error occurred"
            status.color = ft.Colors.RED_400

        search_btn.disabled = False
        page.update()

    login_btn = ft.FilledButton("Login with Microsoft", on_click=login_clicked)
    use_jwt_btn.on_click = use_pasted_jwt
    search_btn.on_click = search_clicked
    query_input.on_submit = search_clicked

    page.add(
        ft.Column([
            ft.Text("SharePoint WIF Test", size=24, weight=ft.FontWeight.BOLD),
            ft.Text("Microsoft JWT -> ADK Agent -> WIF -> Discovery Engine", size=12),
            ft.Divider(),
            status,
            ft.Container(height=10),

            # Manual JWT section
            ft.Text("Option 1: Paste JWT manually", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.CYAN_400),
            jwt_input,
            use_jwt_btn,

            ft.Container(height=10),
            ft.Text("Option 2: Login via browser", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.CYAN_400),
            ft.Text(f"Redirect URI: {REDIRECT_URI}", size=10, color=ft.Colors.BLUE_GREY_500),
            login_btn,

            ft.Divider(),
            ft.Container(height=10),
            ft.Row([query_input, search_btn], alignment=ft.MainAxisAlignment.CENTER),
            ft.Container(height=10),
            response_box,
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    )


if __name__ == "__main__":
    ft.app(main)
