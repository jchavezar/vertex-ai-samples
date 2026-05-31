import google.auth
import google.auth.transport.requests
import requests
import json

# Testing root endpoint tools/call
URL = "https://docparse-firestore-mcp-254356041555.us-central1.run.app/tools/call"

def main():
    creds, project = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    auth_req = google.auth.transport.requests.Request()
    creds.refresh(auth_req)
    
    headers = {
        "Authorization": f"Bearer {creds.token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "method": "tools/call",
        "params": {
            "name": "search_docs",
            "arguments": {
                "query": "what is the metaverse?",
                "top_k": 3
            }
        }
    }
    
    print(f"Calling Cloud Run MCP service tools/call endpoint directly: {URL}")
    r = requests.post(URL, headers=headers, json=payload)
    print(f"Response Status: {r.status_code}")
    try:
        data = r.json()
        print("Response JSON:")
        print(json.dumps(data, indent=2))
    except Exception as e:
        print("Response Text:")
        print(r.text)

if __name__ == "__main__":
    main()
