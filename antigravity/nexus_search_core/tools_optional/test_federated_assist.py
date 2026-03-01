# /// script
# dependencies = ["requests"]
# ///
import requests
import json
import subprocess

def get_token():
    return subprocess.check_output("gcloud auth print-access-token", shell=True).decode().strip()

TOKEN = get_token()
PROJECT_NUMBER = "440133963879"
LOCATION = "global"
ENGINE_ID = "deloitte-demo"
ASSISTANT_ID = "default_assistant"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "X-Goog-User-Project": PROJECT_NUMBER,
    "Content-Type": "application/json",
    "Accept": "text/event-stream"
}

def test_stream_assist(payload, label):
    print(f"\n=== Testing: {label} ===")
    url = f"https://discoveryengine.googleapis.com/v1alpha/projects/{PROJECT_NUMBER}/locations/{LOCATION}/collections/default_collection/engines/{ENGINE_ID}/assistants/{ASSISTANT_ID}:streamAssist"
    
    resp = requests.post(url, headers=headers, json=payload, stream=True)
    print(f"Status: {resp.status_code}")
    
    if resp.status_code != 200:
        print(f"Error: {resp.text}")
        return

    for line in resp.iter_lines():
        if not line: continue
        try:
            line_str = line.decode()
            print(f"DEBUG CHUNK: {line_str}")
            chunk = json.loads(line_str)
            # ... (the rest is fine)

            # Print Answer/Replies
            if 'answer' in chunk:
                ans = chunk['answer']
                if 'replies' in ans:
                    for r in ans['replies']:
                        txt = r.get('groundedContent', {}).get('content', {}).get('text')
                        is_thought = r.get('groundedContent', {}).get('content', {}).get('thought')
                        if txt:
                            prefix = "🧠 THOUGHT" if is_thought else "💬 ANSWER"
                            print(f"{prefix}: {txt}")
                
                # Check for Observation results in the answer steps
                if 'steps' in ans:
                    for step in ans['steps']:
                        for action in step.get('actions', []):
                            if 'observation' in action and 'searchResults' in action['observation']:
                                results = action['observation']['searchResults']
                                print(f"🔍 SEARCH RESULTS found in Grounded Answer state: {len(results)}")
            
            # Check for generic replies (sometimes in 'reply' field)
            if 'reply' in chunk:
                print(f"💬 REPLY: {chunk['reply']}")

        except Exception as e:
            # print(f"Parse error: {e}")
            pass


# Scenario A: dataStoreSpecs
test_stream_assist({
    "query": { "text": "What is the policy for medical leave?" },
    "toolsSpec": {
        "vertexAiSearchSpec": {
            "dataStoreSpecs": [
                { "dataStore": f"projects/{PROJECT_NUMBER}/locations/{LOCATION}/collections/default_collection/dataStores/deloitte-sharepoint_file" }
            ]
        }
    }
}, "individual dataStoreSpecs")

# Scenario C: Minimal (No toolsSpec)
test_stream_assist({
    "query": { "text": "What is the policy for medical leave?" }
}, "Minimal (Implicit Tools)")


