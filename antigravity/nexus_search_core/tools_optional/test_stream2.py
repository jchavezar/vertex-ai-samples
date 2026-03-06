import subprocess
import requests
import json
import sys

token_cmd = subprocess.run(["gcloud", "auth", "print-access-token"], capture_output=True, text=True)
token = token_cmd.stdout.strip()
PROJECT_NUMBER = "REDACTED_PROJECT_NUMBER"
ENGINE_ID = "deloitte-demo" 

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json",
    "X-Goog-User-Project": PROJECT_NUMBER
}

url = f"https://discoveryengine.googleapis.com/v1alpha/projects/{PROJECT_NUMBER}/locations/global/collections/default_collection/engines/{ENGINE_ID}/widgetConfigs/default_search_widget_config"

response = requests.get(url, headers=headers)
try:
    print(json.dumps(response.json(), indent=2))
except:
    print(response.text)

