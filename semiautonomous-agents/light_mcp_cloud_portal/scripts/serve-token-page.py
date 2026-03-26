#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# ///
"""
Simple HTTP server to serve the JWT token helper page.
Usage: uv run scripts/serve-token-page.py
"""
import http.server
import socketserver
import os
import webbrowser

PORT = 9000
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

if __name__ == "__main__":
    os.chdir(DIRECTORY)

    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        url = f"http://localhost:{PORT}/get-jwt-token.html"
        print(f"Serving JWT Token Helper at: {url}")
        print("Press Ctrl+C to stop\n")

        # Try to open browser automatically
        try:
            webbrowser.open(url)
        except:
            pass

        httpd.serve_forever()
