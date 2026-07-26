import google.auth, httpx
from google.auth.transport.requests import Request

credentials, project = google.auth.default()
credentials.refresh(Request())
token = credentials.token

headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
}
# Target reasoning engine ID of outlook-mcp-executive-agent
url = 'https://us-central1-aiplatform.googleapis.com/v1/projects/254356041555/locations/us-central1/reasoningEngines/1584248371311280128:query'
body = {
    "input": {
        "input": "what was my oldest email?"
    }
}
with httpx.Client(timeout=30) as client:
    r = client.post(url, headers=headers, json=body)
    print(r.status_code)
    try:
        print(r.json())
    except:
        print(r.text)
