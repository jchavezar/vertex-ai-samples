#!/usr/bin/env python3
"""Tiny HTTP server for the StreamAssist · ServiceNow tester. Port 5176."""
import http.server, socketserver, os

PORT = 5176
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kw):
        super().__init__(*args, directory=DIRECTORY, **kw)
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        super().end_headers()

if __name__ == "__main__":
    print(f"\nStreamAssist · ServiceNow tester at http://localhost:{PORT}\nCtrl+C to stop.\n")
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nStopped.")
