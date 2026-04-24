#!/usr/bin/env python3
"""StreamAssist · ServiceNow tester — port 5176.

On every GET / request, reads `.env` and substitutes <PLACEHOLDER> values
into index.html before serving. This keeps secrets/IDs out of the file
that's committed to git.

Setup:
  1. cp .env.example .env
  2. Fill in your environment values
  3. python3 serve.py
  4. Open http://localhost:5176
"""
import http.server, socketserver, os, re, pathlib

PORT = 5176
DIRECTORY = pathlib.Path(__file__).parent.absolute()
ENV_FILE = DIRECTORY / ".env"
INDEX_FILE = DIRECTORY / "index.html"

# Mapping: .env key  →  placeholder string in index.html
PLACEHOLDER_MAP = {
    "PORTAL_APP_CLIENT_ID":   "<PORTAL_APP_CLIENT_ID>",
    "TENANT_ID":              "<TENANT_ID>",
    "PROJECT_NUMBER":         "<PROJECT_NUMBER>",
    "WIF_POOL_ID":            "<WIF_POOL_ID>",
    "WIF_PROVIDER_ID":        "<WIF_PROVIDER_ID>",
    "ENGINE_ID":              "<ENGINE_ID>",
    "SERVICENOW_CONNECTOR_ID":"<SERVICENOW_CONNECTOR_ID>",
    "SERVICENOW_INSTANCE_URI":"<https://YOUR_INSTANCE.service-now.com>",
    "SN_OAUTH_CLIENT_ID":     "<SN_OAUTH_CLIENT_ID>",
    "LOCATION":               '"global"',  # this one is special: replaces literal "global"
}

def load_env():
    env = {}
    if not ENV_FILE.exists():
        return env
    for line in ENV_FILE.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        env[k.strip()] = v.strip().strip('"').strip("'")
    return env

def render_index(env):
    html = INDEX_FILE.read_text()
    for k, placeholder in PLACEHOLDER_MAP.items():
        if k == "LOCATION":
            # special-case: we want to swap the default "global" string in the JS
            if env.get(k):
                html = html.replace('location: "global"', f'location: "{env[k]}"')
            continue
        val = env.get(k, "")
        if val:
            # Wrap in quotes — placeholders in HTML appear inside string literals
            html = html.replace(f'"{placeholder}"', f'"{val}"')
    return html.encode()

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kw):
        super().__init__(*args, directory=str(DIRECTORY), **kw)
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()
    def do_GET(self):
        if self.path in ("/", "/index.html"):
            env = load_env()
            missing = [k for k in PLACEHOLDER_MAP if k != "LOCATION" and not env.get(k)]
            if missing:
                msg = (
                    "<h1>tester/.env is missing or incomplete</h1>"
                    f"<p>Missing keys: <code>{', '.join(missing)}</code></p>"
                    f"<p>Copy <code>.env.example</code> to <code>.env</code> and fill in your environment values, then refresh.</p>"
                ).encode()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(msg)))
                self.end_headers()
                self.wfile.write(msg)
                return
            body = render_index(env)
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        super().do_GET()

if __name__ == "__main__":
    print(f"\nStreamAssist · ServiceNow tester at http://localhost:{PORT}")
    if not ENV_FILE.exists():
        print(f"⚠ tester/.env not found — copy .env.example → .env and fill in values")
    else:
        env = load_env()
        missing = [k for k in PLACEHOLDER_MAP if k != "LOCATION" and not env.get(k)]
        if missing:
            print(f"⚠ tester/.env is missing keys: {', '.join(missing)}")
        else:
            print(f"✓ tester/.env loaded ({len(env)} keys)")
    print("Ctrl+C to stop.\n")
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nStopped.")
