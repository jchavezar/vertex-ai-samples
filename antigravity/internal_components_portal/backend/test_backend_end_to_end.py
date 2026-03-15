import requests, json

url = "http://localhost:8008/chat"
headers = {"Content-Type": "application/json", "Authorization": "Bearer TEST_TOKEN_BYPASS"}
data = {
    "messages": [{"role": "user", "content": "What is the timeline for project alpha?"}],
    "model": "gemini-2.5-flash",
    "routerMode": "ge_mcp"
}

with requests.post(url, headers=headers, json=data, stream=True) as r:
    for line in r.iter_lines():
        pass # just consume them so the backend logs them
