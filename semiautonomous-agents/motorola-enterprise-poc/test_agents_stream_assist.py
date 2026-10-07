import time
import json
import requests
from google.auth import default
from google.auth.transport.requests import Request

creds, _ = default()
creds.refresh(Request())
headers = {
    "Authorization": f"Bearer {creds.token}",
    "Content-Type": "application/json",
    "X-Goog-User-Project": "vtxdemos",
}

base = "https://discoveryengine.googleapis.com/v1alpha/projects/254356041555/locations/global/collections/default_collection/engines/gemini-enterprise-17877637_1787763712023/assistants/default_assistant"

print("=================================================================")
print("⚡ TESTING BASIC AGENT (Row 5) VIA STREAMASSIST API")
print("=================================================================\n")

payload_basic = {
    "query": {
        "text": "What is the current renewal status and contract size for the Miami-Dade Dispatch deal in Salesforce?"
    },
    "agentsSpec": {"agentSpecs": [{"agentId": "8517176328388284078"}]},
}

t0 = time.time()
r = requests.post(f"{base}:streamAssist", headers=headers, json=payload_basic)
t_basic = time.time() - t0
print(f"Basic Agent StreamAssist HTTP {r.status_code} | Total Latency: {t_basic:.3f}s")
if r.status_code == 200:
    chunks = json.loads(r.text)
    for idx, c in enumerate(chunks):
        ans = c.get("answer", {})
        steps = ans.get("steps", [])
        for s in steps:
            st = s.get("state")
            desc = s.get("description")
            print(f"  [Chunk {idx+1} Step] ({st}) {desc}")
        replies = ans.get("replies", [])
        for rep in replies:
            txt = rep.get("groundedContent", {}).get("content", {}).get("text", "")
            if txt:
                print(f"  [Reply Chunk {idx+1}]: {txt[:250]}")
else:
    print("Error:", r.text[:400])

print("\n=================================================================")
print("⚡ TESTING WORKFLOW AGENT (Row 19) VIA STREAMASSIST API")
print("=================================================================\n")

payload_wf = {
    "query": {
        "text": "Start the workflow for Miami-Dade County Public Safety"
    },
    "agentsSpec": {"agentSpecs": [{"agentId": "9292006299939784738"}]},
}

t1 = time.time()
r_wf = requests.post(f"{base}:streamAssist", headers=headers, json=payload_wf)
t_wf = time.time() - t1
print(f"Workflow Agent StreamAssist HTTP {r_wf.status_code} | Total Latency: {t_wf:.3f}s")
if r_wf.status_code == 200:
    chunks = json.loads(r_wf.text)
    for idx, c in enumerate(chunks):
        ans = c.get("answer", {})
        steps = ans.get("steps", [])
        for s in steps:
            st = s.get("state")
            desc = s.get("description")
            print(f"  [Chunk {idx+1} Step] ({st}) {desc}")
        replies = ans.get("replies", [])
        for rep in replies:
            txt = rep.get("groundedContent", {}).get("content", {}).get("text", "")
            if txt:
                print(f"  [Reply Chunk {idx+1}]: {txt[:300]}")
else:
    print("Error:", r_wf.text[:400])
