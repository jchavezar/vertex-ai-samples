import time
import json
import requests
from google.auth import default
from google.auth.transport.requests import Request

creds, project = default()
creds.refresh(Request())
token = creds.token

PROJECT_ID = "254356041555"
LOCATION = "global"
COLLECTION = "default_collection"
ENGINE_ID = "gemini-enterprise-17877637_1787763712023"

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json",
    "X-Goog-User-Project": "vtxdemos",
}

print("=================================================================")
print(f"📡 TESTING GEMINI ENTERPRISE STREAMASSIST API ON ENGINE: {ENGINE_ID}")
print("=================================================================\n")

stream_url = f"https://discoveryengine.googleapis.com/v1alpha/projects/{PROJECT_ID}/locations/{LOCATION}/collections/{COLLECTION}/engines/{ENGINE_ID}/assistants/default_assistant:streamAssist"

payload = {
    "query": {
        "text": "Run the MSI Cross-Silo Account 360 & Renewal Risk workflow for Miami-Dade"
    }
}

start_time = time.time()
print(f"[0.000s] Sending request to StreamAssist endpoint...")
resp = requests.post(stream_url, headers=headers, json=payload)
total_time = time.time() - start_time
print(f"[{total_time:.3f}s] HTTP Status: {resp.status_code}\n")

if resp.status_code != 200:
    print("Error response:", resp.text[:1000])
else:
    raw_text = resp.text
    try:
        chunks = json.loads(raw_text)
        print(f"Total JSON chunks received: {len(chunks)}")
        for idx, chunk in enumerate(chunks):
            answer = chunk.get("answer", {})
            state = answer.get("state", "")
            steps = answer.get("steps", [])
            reply_text = answer.get("reply", {}).get("replyText", "")
            
            if steps or reply_text or state:
                print(f"Chunk #{idx+1} (State: {state}):")
                for s_idx, step in enumerate(steps):
                    desc = step.get("description", "")
                    st = step.get("state", "")
                    print(f"   [Step {s_idx+1}] ({st}) {desc}")
                if reply_text:
                    print(f"   [Reply]: {reply_text[:400]}...")
    except Exception as e:
        print("Raw text snippet:", raw_text[:1500])
