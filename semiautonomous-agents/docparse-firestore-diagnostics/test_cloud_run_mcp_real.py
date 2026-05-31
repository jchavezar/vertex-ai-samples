import requests
import json

URL = "https://docparse-firestore-mcp-254356041555.us-central1.run.app/mcp"

def main():
    # Omit Google Authorization header to let the public invoker IAM policy handle it
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream"
    }
    
    # FastMCP streamable_http expects JSON-RPC standard
    payload = {
        "jsonrpc": "2.0",
        "id": "1",
        "method": "tools/call",
        "params": {
            "name": "search_docs",
            "arguments": {
                "query": "metaverse",
                "top_k": 3
            }
        }
    }
    
    print(f"Calling Cloud Run MCP service /mcp directly: {URL}")
    r = requests.post(URL, headers=headers, json=payload, stream=True)
    print(f"Response Status: {r.status_code}")
    print(f"Response Headers: {dict(r.headers)}")
    
    print("Response Stream:")
    for chunk in r.iter_lines():
        if chunk:
            print(chunk.decode('utf-8'))

if __name__ == "__main__":
    main()
