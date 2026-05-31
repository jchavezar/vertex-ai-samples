import requests
import json

URL = "https://docparse-firestore-mcp-254356041555.us-central1.run.app/mcp"

def main():
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    payload = {
        "jsonrpc": "2.0",
        "id": "1",
        "method": "tools/list",
        "params": {}
    }
    
    print(f"Calling Cloud Run MCP /mcp tools/list directly: {URL}")
    r = requests.post(URL, headers=headers, json=payload)
    print(f"Status: {r.status_code}")
    try:
        print(json.dumps(r.json(), indent=2))
    except Exception as e:
        print("Failed to parse JSON:", e)
        print(r.text)

if __name__ == "__main__":
    main()
