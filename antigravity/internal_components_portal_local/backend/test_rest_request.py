import google.auth
import google.auth.transport.requests
import requests
import os
import json

# Get Credentials
credentials, project = google.auth.default()
auth_request = google.auth.transport.requests.Request()
credentials.refresh(auth_request)
token = credentials.token

ENGINE_ID = "projects/REDACTED_PROJECT_NUMBER/locations/us-central1/reasoningEngines/3149353695427166208"
url = f"https://us-central1-aiplatform.googleapis.com/v1beta1/{ENGINE_ID}:streamQuery"

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

payload = {
    "input": {
         "message": "What is the temperature in Seattle? Respond STRICTLY with SEARCH.",
         "user_id": "test_user_123"
    }
}

print(f"Sending REST Stream query to {url}...")
try:
    with requests.post(url, headers=headers, json=payload) as response:
        print(f"HTTP Status: {response.status_code}")
        print("Response Text:", response.text)
except Exception as e:
    print("REST Exception:", str(e))
