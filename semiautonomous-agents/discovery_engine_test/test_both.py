import requests
import json

# Get service account token (for the WITHOUT case - no WIF needed for demo)
import google.auth
from google.auth.transport.requests import Request

creds, _ = google.auth.default()
creds.refresh(Request())
token = creds.token

PROJECT_NUMBER = "440133963879"
ENGINE_ID = "deloitte-demo"

url = f"https://discoveryengine.googleapis.com/v1alpha/projects/{PROJECT_NUMBER}/locations/global/collections/default_collection/engines/{ENGINE_ID}/assistants/default_assistant:streamAssist"

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json",
    "X-Goog-User-Project": PROJECT_NUMBER
}

# 1. WITHOUT dataStoreSpecs
print("=" * 60)
print("WITHOUT dataStoreSpecs:")
print("=" * 60)

payload_without = {
    "query": {"text": "What is the salary of a CFO?"}
}

resp = requests.post(url, headers=headers, json=payload_without, timeout=60)
data = resp.json()

# Extract answer
for chunk in data:
    stream_resp = chunk.get("streamAssistResponse", chunk)
    answer = stream_resp.get("answer", {})
    for reply in answer.get("replies", []):
        grounded = reply.get("groundedContent", {})
        text = grounded.get("content", {}).get("text", "")
        thought = grounded.get("content", {}).get("thought", False)
        if text and not thought:
            print(f"Answer: {text[:500]}")
        
        # Check grounding
        grounding = grounded.get("textGroundingMetadata", {})
        refs = grounding.get("references", [])
        if refs:
            print(f"Sources: {len(refs)} found")
        else:
            print("Sources: NONE (no grounding)")

print("\n")

# 2. WITH dataStoreSpecs - first get datastores
print("=" * 60)
print("WITH dataStoreSpecs:")
print("=" * 60)

# Get datastores from widget config
widget_url = f"https://discoveryengine.googleapis.com/v1alpha/projects/{PROJECT_NUMBER}/locations/global/collections/default_collection/engines/{ENGINE_ID}/widgetConfigs/default_search_widget_config"
widget_resp = requests.get(widget_url, headers=headers, timeout=10)
widget_data = widget_resp.json()

datastore_specs = []
for comp in widget_data.get('collectionComponents', [{}]):
    for ds in comp.get('dataStoreComponents', []):
        datastore_specs.append({'dataStore': ds['name']})
        
print(f"Datastores found: {len(datastore_specs)}")

payload_with = {
    "query": {"text": "What is the salary of a CFO?"},
    "toolsSpec": {
        "vertexAiSearchSpec": {
            "dataStoreSpecs": datastore_specs
        }
    }
}

resp2 = requests.post(url, headers=headers, json=payload_with, timeout=60)
data2 = resp2.json()

# Extract answer and sources
for chunk in data2:
    stream_resp = chunk.get("streamAssistResponse", chunk)
    answer = stream_resp.get("answer", {})
    for reply in answer.get("replies", []):
        grounded = reply.get("groundedContent", {})
        text = grounded.get("content", {}).get("text", "")
        thought = grounded.get("content", {}).get("thought", False)
        if text and not thought:
            print(f"Answer: {text[:500]}")
        
        # Check grounding
        grounding = grounded.get("textGroundingMetadata", {})
        refs = grounding.get("references", [])
        if refs:
            print(f"\nSources ({len(refs)}):")
            for ref in refs[:3]:
                doc = ref.get("documentMetadata", {})
                print(f"  - {doc.get('title', 'Unknown')}")
                print(f"    {doc.get('uri', '')[:80]}")
