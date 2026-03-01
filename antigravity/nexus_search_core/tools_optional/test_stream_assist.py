import requests
import json

# Constants
TOKEN = "YOUR_TOKEN_HERE"
URL = "https://discoveryengine.googleapis.com/v1alpha/projects/440133963879/locations/global/collections/default_collection/engines/deloitte-demo/assistants/default_assistant:streamAssist"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
    "Accept": "text/event-stream"
}

def test_payload(p, name):
    print(f"\nTesting {name}...")
    response = requests.post(URL, headers=headers, json=p, stream=True)
    print(f"Status: {response.status_code}")
    if response.status_code != 200:
        print(f"Error: {response.text}")

# Test 4: answer_generation_spec (as in search streamAnswer)
test_payload({
    "query": { "text": "salary of COO" },
    "answer_generation_spec": {
        "model_spec": { "model_version": "stable" },
        "include_citations": True
    }
}, "answer_generation_spec")

# Test 5: generation_spec WITH prompt_spec directly (no model_spec)
test_payload({
    "query": { "text": "salary of COO" },
    "generation_spec": {
        "prompt_spec": { "preamble": "test" }
    }
}, "generation_spec -> prompt_spec")

# Test 6: generation_spec WITH model_spec directly
test_payload({
    "query": { "text": "salary of COO" },
    "generation_spec": {
        "model_spec": { "model_version": "stable" }
    }
}, "generation_spec -> model_spec")
