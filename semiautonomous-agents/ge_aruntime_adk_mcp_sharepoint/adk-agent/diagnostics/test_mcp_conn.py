import requests
import google.auth
import google.auth.transport.requests

def get_token(audience):
    try:
        import google.oauth2.id_token
        request = google.auth.transport.requests.Request()
        return google.oauth2.id_token.fetch_id_token(request, audience)
    except Exception as e:
        print(f"Failed to get token for {audience}: {e}")
        return None

urls = [
    "https://ge-custom-sharepoint-mcp-rxhrarbbrq-uc.a.run.app",
    "https://ge-custom-sharepoint-mcp-254356041555.us-central1.run.app"
]

for base_url in urls:
    print(f"\nTesting Base URL: {base_url}")
    token = get_token(base_url)
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
        print("Token obtained.")
    else:
        print("Proceeding without token.")
        
    for path in ["/sse", "/mcp", "/"]:
        url = base_url + path
        print(f"Trying {url} ...")
        try:
            # Use GET for /sse and / usually, POST for /mcp
            if path == "/mcp":
                resp = requests.post(url, headers=headers, json={"method": "initialize", "params": {}}, timeout=5)
            else:
                resp = requests.get(url, headers=headers, timeout=5)
            print(f"Status: {resp.status_code}")
            print(f"Content snippet: {resp.text[:100]}")
        except Exception as e:
            print(f"Failed: {e}")
