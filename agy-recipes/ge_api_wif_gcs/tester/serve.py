#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "google-auth",
#     "requests",
# ]
# ///
"""
Simple HTTP server and reverse proxy for WIF + GCS + Discovery Engine testing.
"""
import http.server
import socketserver
import os
import urllib.request
import urllib.error
import json
import google.auth
import google.auth.transport.requests

PORT = 8003
DIRECTORY = os.path.dirname(os.path.abspath(__file__))
WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(DIRECTORY)))

class TesterProxyHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, GET')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Goog-User-Project')
        super().end_headers()

    def do_GET(self):
        if self.path == '/last_setup_resources.json':
            # Load from workspace root
            resource_file = os.path.join(WORKSPACE_ROOT, 'last_setup_resources.json')
            if os.path.exists(resource_file):
                try:
                    with open(resource_file, 'r') as f:
                        data = json.load(f)
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps(data).encode())
                except Exception as e:
                    self.send_response(500)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'error': str(e)}).encode())
            else:
                self.send_response(404)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'last_setup_resources.json not found'}).encode())
        
        elif self.path == '/api/adc-token':
            # Fetch default ADC token to make local testing simple
            try:
                creds, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
                creds.refresh(google.auth.transport.requests.Request())
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'token': creds.token}).encode())
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': f"Failed to get ADC token: {str(e)}"}).encode())
        else:
            super().do_GET()

    def do_POST(self):
        if self.path.startswith('/api/proxy/'):
            # Proxy request to Discovery Engine or STS
            target_url = self.path[len('/api/proxy/'):]
            if not target_url.startswith('http'):
                target_url = 'https://' + target_url

            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length) if content_length > 0 else None

            # Copy headers
            req_headers = {}
            for h in ['Authorization', 'Content-Type', 'X-Goog-User-Project']:
                if h in self.headers:
                    req_headers[h] = self.headers[h]

            req = urllib.request.Request(
                target_url,
                data=body,
                headers=req_headers,
                method='POST'
            )

            try:
                with urllib.request.urlopen(req) as response:
                    res_body = response.read()
                    self.send_response(response.status)
                    self.send_header('Content-Type', response.headers.get('Content-Type', 'application/json'))
                    self.end_headers()
                    self.wfile.write(res_body)
            except urllib.error.HTTPError as e:
                self.send_response(e.code)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(e.read())
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': str(e)}).encode())
        else:
            super().do_POST()

if __name__ == "__main__":
    print(f"================================================================")
    print(f"  WIF + GCS + Discovery Engine streamAssist Tester")
    print(f"================================================================")
    print(f"  Local Server: http://localhost:{PORT}")
    print(f"================================================================")

    # Allow immediate socket reuse
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), TesterProxyHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")
