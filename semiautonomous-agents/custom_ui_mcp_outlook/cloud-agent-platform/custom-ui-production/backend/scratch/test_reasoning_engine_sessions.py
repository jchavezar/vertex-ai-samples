import google.auth, httpx
from google.auth.transport.requests import Request

credentials, project = google.auth.default()
credentials.refresh(Request())
token = credentials.token

headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
}
# Invoke create_session method
url = 'https://us-central1-aiplatform.googleapis.com/v1/projects/254356041555/locations/us-central1/reasoningEngines/3073250998110650368:create_session'
body = {
    "input": {}
}
with httpx.Client(timeout=30) as client:
    r = client.post(url, headers=headers, json=body)
    print(r.status_code)
    try:
        print(r.json())
    except:
        print(r.text)
