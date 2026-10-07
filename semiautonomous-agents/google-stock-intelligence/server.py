#!/usr/bin/env python3
"""
Lightweight Secure HTTP Server for Google Stock Intelligence Platform.
Adheres strictly to Mandatory Secure Web Skills & Zero-Leak Protocol.
Binds exclusively to 127.0.0.1 (localhost) on port 8090 (or next open port).
"""

import http.server
import json
import os
import socket
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_PORT = 8090
HOST = "127.0.0.1"


class SecureFinancialPlatformHandler(http.server.SimpleHTTPRequestHandler):
    """Secure request handler enforcing strict security headers and custom API routes."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=BASE_DIR, **kwargs)

    def end_headers(self):
        # Mandatory Security Headers
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("X-XSS-Protection", "1; mode=block")
        self.send_header("Referrer-Policy", "strict-origin-when-cross-origin")
        self.send_header(
            "Content-Security-Policy",
            "default-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com https://cdn.jsdelivr.net https://fonts.googleapis.com https://fonts.gstatic.com; "
            "img-src 'self' data: https:; "
            "font-src 'self' https://fonts.gstatic.com; "
            "script-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com https://cdn.jsdelivr.net;",
        )
        super().end_headers()

    def do_GET(self):
        # Custom health-check endpoint
        if self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            response = {
                "status": "healthy",
                "service": "google-stock-intelligence-platform",
                "host": HOST,
                "port": self.server.server_port,
            }
            self.wfile.write(json.dumps(response).encode("utf-8"))
            return

        # Default to index.html for root path
        if self.path in ("/", ""):
            self.path = "/index.html"

        return super().do_GET()

    def log_message(self, format, *args):
        # Suppress noisy standard logs unless an error occurs
        if args and str(args[0]).startswith(("4", "5")):
            sys.stderr.write(f"[HTTP ERROR] {format % args}\n")


def is_port_available(port: int, host: str = HOST) -> bool:
    """Check if a given TCP port is available on the specified host."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind((host, port))
            return True
        except socket.error:
            return False


def find_available_port(start_port: int = DEFAULT_PORT, host: str = HOST) -> int:
    """Find the next open port starting from start_port."""
    for port in range(start_port, start_port + 50):
        if is_port_available(port, host):
            return port
    raise RuntimeError(f"Could not find an open port between {start_port} and {start_port + 50}")


def main():
    target_port = find_available_port(DEFAULT_PORT)
    server_address = (HOST, target_port)
    httpd = http.server.ThreadingHTTPServer(server_address, SecureFinancialPlatformHandler)

    print(f"======================================================================")
    print(f" Alphabet Inc. (GOOGL) - Institutional Financial Intelligence Platform")
    print(f" Local URL: http://{HOST}:{target_port}")
    print(f" Serving directory: {BASE_DIR}")
    print(f" Security: Bound exclusively to {HOST} (Zero-Leak / Localhost Only)")
    print(f"======================================================================")
    sys.stdout.flush()

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer gracefully shutting down...")
        httpd.server_close()


if __name__ == "__main__":
    main()
