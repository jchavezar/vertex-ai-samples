import google.auth, httpx
from google.auth.transport.requests import Request

credentials, project = google.auth.default()
credentials.refresh(Request())
token = credentials.token

headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
}
url = 'https://us-central1-aiplatform.googleapis.com/v1/projects/254356041555/locations/us-central1/reasoningEngines/3073250998110650368:query'

# Try specifying method inside input
body = {
    "input": {
        "class_method": "create_session"
    }
}
with httpx.Client(timeout=30) as client:
    r = client.post(url, headers=headers, json=body)
    print("Response status with class_method:", r.status_code)
    try:
        print(r.json())
    except:
        print(r.text)

body_2 = {
    "input": {
        "method": "create_session"
    }
}
with httpx.Client(timeout=30) as client:
    r = client.post(url, headers=headers, json=body_2)
    print("Response status with method:", r.status_code)
    try:
        print(r.json())
    except:
        print(r.text)
