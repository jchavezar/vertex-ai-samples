import requests
import json
import os
import subprocess

# Get token
def get_token():
    return subprocess.check_output("gcloud auth print-access-token", shell=True).decode().strip()

TOKEN = get_token()
PROJECT_NUMBER = "440133963879"
LOCATION = "global"
ENGINE_ID = "deloitte-demo"
ASSISTANT_ID = "default_assistant"

# The streamAssist endpoint for Agentic Assistant
URL = f"https://discoveryengine.googleapis.com/v1alpha/projects/{PROJECT_NUMBER}/locations/{LOCATION}/collections/default_collection/engines/{ENGINE_ID}/assistants/{ASSISTANT_ID}:streamAssist"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
    "X-Goog-User-Project": PROJECT_NUMBER,
    "Accept": "text/event-stream"
}

def test_payload(p, name):
    print(f"\n--- Testing {name} ---")
    print(f"Payload: {json.dumps(p, indent=2)}")
    response = requests.post(URL, headers=headers, json=p, stream=True)
    print(f"Status: {response.status_code}")
    
    if response.status_code != 200:
        print(f"Error: {response.text}")
    else:
        print("Success! (First 5 chunks)")
        count = 0
        for line in response.iter_lines():
            if line and count < 5:
                # streamAssist returns JSON objects in lines
                try:
                    data = json.loads(line.decode())
                    print(json.dumps(data, indent=2))
                except:
                    print(line.decode())
                count += 1
            elif count >= 5:
                break

# 1. FIXED Structure for streamAssist (Agentic Assistant)
# Note: vertexAiSearchSpec takes dataStoreSpecs, NOT answerGenerationSpec
test_payload({
    "query": { "text": "What is the policy for medical leave?" },
    "toolsSpec": {
        "vertexAiSearchSpec": {
            "dataStoreSpecs": [
                {
                    "dataStore": f"projects/{PROJECT_NUMBER}/locations/{LOCATION}/collections/default_collection/dataStores/deloitte-sharepoint_file"
                }
            ]
        },
        "webGroundingSpec": {} # Optional toggle
    }
}, "Correct streamAssist Tools Structure")

# 2. FIXED generationSpec (modelId)
# Note: generationSpec at this level only supports modelId.
# Traditional answerGenerationSpec (topP, temperature) belongs to streamAnswer, not streamAssist.
test_payload({
    "query": { "text": "Hello, who are you?" },
    "generationSpec": {
        # If modelId is not set, it uses the Assistant default.
        # "modelId": "gemini-1.5-flash" # Note: specific versioning might be required
    }
}, "Minimal streamAssist with generationSpec")
