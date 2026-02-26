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

# Try with toolsSpec.vertexAiSearchSpec
serving_config = f"projects/{PROJECT_NUMBER}/locations/{LOCATION}/collections/default_collection/engines/{ENGINE_ID}/servingConfigs/default_config"

payload = {
    "query": { "text": "What was Alphabet revenue in 2023?" },
    "toolsSpec": {
        "vertexAiSearchSpec": {
            "servingConfig": serving_config
        }
    }
}

print(f"Calling: {url}")
print(f"Payload: {json.dumps(payload, indent=2)}")

with requests.post(url, json=payload, headers=headers, stream=True) as response:
    print(f"Status: {response.status_code}")
    for line in response.iter_lines():
        if line:
            raw = line.decode('utf-8')
            # Extract content if it's SSE format
            if raw.startswith("data: "):
                try:
                    data = json.loads(raw[6:])
                    print(f"PACKET: {json.dumps(data, indent=2)}")
                except:
                    print(f"RAW: {raw}")
            else:
                print(f"RAW: {raw}")

            if "searchResults" in raw or "groundedContent" in raw or "references" in raw:
                print(">>> FOUND SOURCES IN PACKET! <<<")
