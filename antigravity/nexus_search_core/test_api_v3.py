import requests
import json
import subprocess

def get_token():
    return subprocess.check_output(["gcloud", "auth", "print-access-token"]).decode("utf-8").strip()

PROJECT_NUMBER = "440133963879"
ENGINE_ID = "deloitte-demo"
LOCATION = "global"

url = f"https://discoveryengine.googleapis.com/v1beta/projects/{PROJECT_NUMBER}/locations/{LOCATION}/collections/default_collection/engines/{ENGINE_ID}/assistants/default_assistant:streamAssist"

token = get_token()
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# Try with searchSpec at top level
payload = {
    "query": { "text": "What was Alphabet revenue in 2023? Use your search tool." },
    "searchSpec": {
        "searchParams": {
            "maxReturnResults": 5
        }
    }
}

print(f"Calling: {url}")

with requests.post(url, json=payload, headers=headers, stream=True) as response:
    print(f"Status: {response.status_code}")
    for line in response.iter_lines():
        if line:
            raw = line.decode('utf-8')
            print(f"RAW: {raw}")
            if any(key in raw for key in ["searchResults", "groundedContent", "references", "citations", "answerStep", "observationStep"]):
                print(">>> FOUND RELEVANT CONTENT IN PACKET! <<<")
