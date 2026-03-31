#!/usr/bin/env python3
"""
Simple HTTP server for Discovery Engine SharePoint test.
Serves the HTML page on port 5000 for Entra ID redirect.
"""
import http.server
import socketserver
import os

PORT = 5000
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def end_headers(self):
        # Add CORS headers for STS calls
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        super().end_headers()

if __name__ == "__main__":
    print(f"""
================================================================================
  Discovery Engine SharePoint Test Server
================================================================================

  Open in browser: http://localhost:{PORT}

  Flow:
  1. Login with Microsoft Entra ID
  2. Exchange JWT for GCP token via WIF/STS
  3. Query Discovery Engine with SharePoint datastores
  4. See grounded results from Jennifer Walsh's data

  Press Ctrl+C to stop.
================================================================================
""")

    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")
