import requests

urls = [
    "https://ge-custom-sharepoint-mcp-rxhrarbbrq-uc.a.run.app",
    "https://ge-custom-sharepoint-mcp-254356041555.us-central1.run.app"
]

for base_url in urls:
    print(f"\nTesting Base URL: {base_url}")
    for path in ["/sse", "/mcp", "/"]:
        url = base_url + path
        print(f"Trying {url} ...")
        try:
            resp = requests.get(url, timeout=5)
            print(f"Status: {resp.status_code}")
            print(f"Content snippet: {resp.text[:100]}")
        except Exception as e:
            print(f"Failed: {e}")
