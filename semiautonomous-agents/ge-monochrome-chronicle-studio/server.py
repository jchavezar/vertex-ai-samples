#!/usr/bin/env python3
"""
Gemini Enterprise Session & Artifact Studio - Local API Proxy & Static Server
Proxies requests to Google Cloud Discovery Engine v1alpha API using gcloud auth.
"""

import json
import os
import subprocess
import time
import urllib.error
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = 8765
DEFAULT_ENGINE = "projects/vtxdemos/locations/global/collections/default_collection/engines/gemini-enterprise-17877637_1787763712023"


def get_access_token():
    try:
        token = subprocess.check_output(
            ["gcloud", "auth", "print-access-token"],
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
        return token
    except Exception as e:
        raise RuntimeError(f"Failed to obtain gcloud access token: {e}")


class StudioRequestHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Quiet standard logging to keep console clean
        pass

    def _send_json(self, status_code, payload):
        body = json.dumps(payload, indent=2).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PATCH, DELETE, OPTIONS, HEAD")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        if path == "/" or path == "/index.html":
            index_path = os.path.join(os.path.dirname(__file__), "index.html")
            with open(index_path, "rb") as f:
                content = f.read()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
            return

        if path.startswith("/api/proxy"):
            self._handle_proxy("GET", query)
            return

        self._send_json(404, {"error": "Not found"})

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        query = urllib.parse.parse_qs(parsed.query)
        if parsed.path.startswith("/api/proxy"):
            self._handle_proxy("POST", query)
            return
        self._send_json(404, {"error": "Not found"})

    def do_PATCH(self):
        parsed = urllib.parse.urlparse(self.path)
        query = urllib.parse.parse_qs(parsed.query)
        if parsed.path.startswith("/api/proxy"):
            self._handle_proxy("PATCH", query)
            return
        self._send_json(404, {"error": "Not found"})

    def do_DELETE(self):
        parsed = urllib.parse.urlparse(self.path)
        query = urllib.parse.parse_qs(parsed.query)
        if parsed.path.startswith("/api/proxy"):
            self._handle_proxy("DELETE", query)
            return
        self._send_json(404, {"error": "Not found"})

    def _handle_proxy(self, method, query):
        target_url = query.get("url", [""])[0]
        if not target_url.startswith("https://discoveryengine.googleapis.com/"):
            self._send_json(400, {"error": "Target URL must start with https://discoveryengine.googleapis.com/"})
            return

        content_len = int(self.headers.get("Content-Length", 0))
        req_body = self.rfile.read(content_len) if content_len > 0 else None

        try:
            token = get_access_token()
        except Exception as e:
            self._send_json(500, {"error": str(e)})
            return

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        # Build equivalent cURL command for UI display
        curl_parts = [f'curl -s -X {method} \\']
        curl_parts.append('  -H "Authorization: Bearer $(gcloud auth print-access-token)" \\')
        curl_parts.append('  -H "Content-Type: application/json" \\')
        if req_body:
            body_str = req_body.decode("utf-8", errors="replace")
            curl_parts.append(f"  -d '{body_str}' \\")
        curl_parts.append(f'  "{target_url}"')
        curl_command = "\n".join(curl_parts)

        start_time = time.time()
        req = urllib.request.Request(target_url, data=req_body, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                latency_ms = int((time.time() - start_time) * 1000)
                raw_resp = resp.read().decode("utf-8", errors="replace")
                try:
                    parsed_resp = json.loads(raw_resp) if raw_resp else {}
                except json.JSONDecodeError:
                    parsed_resp = {"raw": raw_resp}

                self._send_json(
                    200,
                    {
                        "status": resp.status,
                        "latencyMs": latency_ms,
                        "method": method,
                        "url": target_url,
                        "curl": curl_command,
                        "data": parsed_resp,
                    },
                )
        except urllib.error.HTTPError as e:
            latency_ms = int((time.time() - start_time) * 1000)
            err_body = e.read().decode("utf-8", errors="replace")
            try:
                err_json = json.loads(err_body)
            except Exception:
                err_json = {"error": err_body}
            self._send_json(
                200,
                {
                    "status": e.code,
                    "latencyMs": latency_ms,
                    "method": method,
                    "url": target_url,
                    "curl": curl_command,
                    "data": err_json,
                },
            )
        except Exception as e:
            self._send_json(500, {"error": str(e), "curl": curl_command})


if __name__ == "__main__":
    server = HTTPServer(("127.0.0.1", PORT), StudioRequestHandler)
    print(f"Gemini Enterprise Session Studio running on http://127.0.0.1:{PORT}")
    server.serve_forever()
