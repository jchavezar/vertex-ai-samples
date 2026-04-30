#!/usr/bin/env python3
"""Upload PNG files to Google Drive via gworkspace MCP server."""
import os
import base64
import json
import httpx

MCP_URL = "http://localhost:8081/mcp"
PARENT_ID = "1K2lkvQYuWd3SN8gg9R7obL9GQ2juFj7e"

def upload_file(filename: str):
    """Upload a PNG file to Google Drive."""
    print(f"Uploading {filename}...")

    # Read and encode file
    with open(filename, "rb") as f:
        content = base64.b64encode(f.read()).decode()

    # Build MCP request
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "drive_upload_binary",
            "arguments": {
                "name": filename,
                "content_base64": content,
                "mime_type": "image/png",
                "parent_id": PARENT_ID
            }
        }
    }

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream"
    }

    try:
        response = httpx.post(MCP_URL, json=payload, headers=headers, timeout=60)
        result = response.json()
        if "result" in result:
            text = result["result"].get("content", [{}])[0].get("text", "Success")
            print(f"  {text}")
        else:
            print(f"  Error: {result.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"  Error: {e}")

def main():
    files = [
        "01-high-level-architecture.png",
        "02-auth-flow.png",
        "03-wif-exchange.png",
        "04-agent-flow.png",
        "05-deployment.png"
    ]

    for f in files:
        if os.path.exists(f):
            upload_file(f)
        else:
            print(f"File not found: {f}")

if __name__ == "__main__":
    main()
