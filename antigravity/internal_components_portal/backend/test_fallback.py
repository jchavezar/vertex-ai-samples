import requests
import json
import os
import subprocess

PROJECT_NUMBER = "REDACTED_PROJECT_NUMBER" # the numeric project ID
ENGINE_ID = "deloitte-demo"
LOCATION = "global"

token = subprocess.check_output(["gcloud", "auth", "print-access-token"]).decode("utf-8").strip()

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json",
    "x-goog-user-project": PROJECT_NUMBER
}

search_url = f"https://discoveryengine.googleapis.com/v1alpha/projects/{PROJECT_NUMBER}/locations/{LOCATION}/collections/default_collection/engines/{ENGINE_ID}/servingConfigs/default_search:search"

search_payload = {
    "query": "Deloitte",
    "pageSize": 5
}
print(f"Hitting {search_url} with 'Deloitte'")
search_resp = requests.post(search_url, headers=headers, json=search_payload, timeout=30)
if search_resp.status_code != 200:
    print(f"Error {search_resp.status_code}: {search_resp.text}")
else:
    search_data = search_resp.json()
    print("Results found:", len(search_data.get("results", [])))
    if search_data.get("results"):
        print("First result title:", search_data["results"][0].get("document", {}).get("derivedStructData", {}).get("title", ""))
