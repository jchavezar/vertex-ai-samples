import requests
import google.auth
from google.auth.transport.requests import Request
import json

project_number = "254356041555"
engine_id = "agentspace-testing_1748446185255"
query = "what is vertex ai?"

credentials, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
auth_req = Request()
credentials.refresh(auth_req)
access_token = credentials.token

url = f"https://discoveryengine.googleapis.com/v1alpha/projects/{project_number}/locations/global/collections/default_collection/engines/{engine_id}/servingConfigs/default_search:answer"

payload = {
    "query": {"text": query},
    "answerGenerationSpec": {
        "ignoreNonAnswerSeekingQuery": False,
        "ignoreLowRelevantContent": False
    }
}

headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json",
    "X-Goog-User-Project": project_number
}

response = requests.post(url, json=payload, headers=headers)
print("Status Code:", response.status_code)
print("Response:", json.dumps(response.json(), indent=2))
