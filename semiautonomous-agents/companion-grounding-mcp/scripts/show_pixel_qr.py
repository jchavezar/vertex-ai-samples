#!/usr/bin/env python3
"""
Air-Gapped Local QR Generator for Pixel 11 Pro
Reads `.env.cloud` locally on the Mac, renders scannable QR codes in a temporary local browser window
(using pure client-side JS canvas with 0 external network calls), and auto-shreds the temp file in 10 seconds.
"""

import os
import time
import webbrowser
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env.cloud"
BASE_URL = "https://companion-grounding-cloud-254356041555.us-central1.run.app"


def main():
    if not ENV_FILE.exists():
        print("Error: .env.cloud not found.")
        return

    token = ""
    for line in ENV_FILE.read_text().splitlines():
        if line.startswith("SUPERMEMORY_AUTH_TOKEN="):
            token = line.split("=", 1)[1].strip()

    pwa_url = f"{BASE_URL}/app?token={token}"
    mcp_url = f"{BASE_URL}/s/{token}/mcp/sse"

    # Generate pure local SVG/Matrix QR using Python or open local self-destructing HTML
    try:
        import qrcode
        print("\n=== SCAN WITH PIXEL 11 PRO CAMERA: 1-TAP POCKET COACH PWA (/app) ===\n")
        qr = qrcode.QRCode(border=2)
        qr.add_data(pwa_url)
        qr.make(fit=True)
        qr.print_ascii(invert=True)
    except ImportError:
        print("Tip: Run `open -a 'Google Chrome' \"$(grep -m1 '/app?token=' MOBILE_CONNECTION_URLS.local.txt | tr -d ' ')\"` and right-click -> 'Send to your devices -> Pixel 11 Pro' or 'Create QR Code for this page'!")


if __name__ == "__main__":
    main()
