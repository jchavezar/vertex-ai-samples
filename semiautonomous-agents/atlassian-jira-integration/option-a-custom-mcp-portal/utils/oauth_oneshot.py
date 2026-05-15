"""One-shot Atlassian OAuth 3LO flow.

Spins up a localhost HTTP server, prints the authorize URL, captures the
callback code, exchanges it for an access token, and writes the token to
adk_agent/.atlassian_token (chmod 600).
"""
import http.server
import os
import secrets
import socketserver
import threading
import urllib.parse
import webbrowser
from pathlib import Path

import requests

# Lightweight .env loader (no python-dotenv dependency).
_env_path = Path(__file__).resolve().parent / ".env"
if _env_path.exists():
    for line in _env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())

CLIENT_ID = os.environ["ATLASSIAN_CLIENT_ID"]
CLIENT_SECRET = os.environ["ATLASSIAN_CLIENT_SECRET"]
REDIRECT_URI = os.environ["ATLASSIAN_REDIRECT_URI"]
SCOPES = "read:jira-work read:jira-user write:jira-work offline_access"
AUTHORIZE_URL = "https://auth.atlassian.com/authorize"
TOKEN_URL = "https://auth.atlassian.com/oauth/token"
PORT = int(urllib.parse.urlparse(REDIRECT_URI).port or 8765)
TOKEN_OUT = Path(__file__).resolve().parent.parent / "adk_agent" / ".atlassian_token"

state = secrets.token_urlsafe(16)
auth_code: dict[str, str] = {}


class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, *_a, **_kw): pass
    def do_GET(self):
        qs = urllib.parse.urlparse(self.path).query
        params = dict(urllib.parse.parse_qsl(qs))
        if params.get("state") == state and "code" in params:
            auth_code["code"] = params["code"]
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"<h2>OK. You can close this tab.</h2>")
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(f"State mismatch or no code. Got: {params}".encode())


def main():
    auth_url = (
        f"{AUTHORIZE_URL}?audience=api.atlassian.com"
        f"&client_id={CLIENT_ID}"
        f"&scope={urllib.parse.quote(SCOPES)}"
        f"&redirect_uri={urllib.parse.quote(REDIRECT_URI)}"
        f"&state={state}"
        f"&response_type=code"
        f"&prompt=consent"
    )
    print(f"\n  Open this URL in a browser on THIS VM (Chrome Remote Desktop):\n\n  {auth_url}\n")

    httpd = socketserver.TCPServer(("0.0.0.0", PORT), Handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()

    try:
        webbrowser.open(auth_url)
    except Exception:
        pass

    print(f"  Waiting for callback on {REDIRECT_URI} ...")
    while "code" not in auth_code:
        threading.Event().wait(0.5)
    httpd.shutdown()
    print("  Got code. Exchanging for token...")

    resp = requests.post(
        TOKEN_URL,
        json={
            "grant_type": "authorization_code",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "code": auth_code["code"],
            "redirect_uri": REDIRECT_URI,
        },
        headers={"Content-Type": "application/json"},
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()
    token = data["access_token"]
    refresh = data.get("refresh_token", "")
    TOKEN_OUT.parent.mkdir(parents=True, exist_ok=True)
    TOKEN_OUT.write_text(token)
    TOKEN_OUT.chmod(0o600)
    print(f"\n  Access token saved to: {TOKEN_OUT}")
    print(f"  Token preview: {token[:24]}... (len={len(token)})")
    print(f"  Refresh token present: {bool(refresh)}")
    print(f"  Expires in: {data.get('expires_in')}s")

    # Also persist refresh token to eval/.env so jira_oracle.py auto-refreshes.
    eval_env = TOKEN_OUT.parent.parent.parent / "eval" / ".env"
    if refresh and eval_env.exists():
        lines = eval_env.read_text().splitlines()
        out_lines = []
        replaced = False
        for line in lines:
            if line.startswith("ATLASSIAN_REFRESH_TOKEN="):
                out_lines.append(f"ATLASSIAN_REFRESH_TOKEN={refresh}")
                replaced = True
            else:
                out_lines.append(line)
        if not replaced:
            out_lines.append(f"ATLASSIAN_REFRESH_TOKEN={refresh}")
        eval_env.write_text("\n".join(out_lines) + "\n")
        eval_env.chmod(0o600)
        print(f"  Refresh token written to: {eval_env}")


if __name__ == "__main__":
    main()
