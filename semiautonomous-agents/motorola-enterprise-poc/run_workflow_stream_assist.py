import json
import time
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
wf_url = f"{base}/agents/9292006299939784738"

r_get = requests.get(wf_url, headers=headers)
wf_data = r_get.json()

labels = wf_data.get("labels", {})
labels["agent:workflow-agent:trigger-type:manual"] = "true"

r_patch = requests.patch(
    f"{wf_url}?updateMask=labels,state",
    headers=headers,
    json={"labels": labels, "state": "ENABLED"},
)
print("Patch status:", r_patch.status_code)

payload = {
    "query": {
        "text": 'msi_crosssilo_account_360__renewal_risk({"parameters": {"account_name": "Miami-Dade"}, "request": "Start the workflow"})'
    },
    "agentsSpec": {"agentSpecs": [{"agentId": "9292006299939784738"}]},
}

t_start = time.time()
r_run = requests.post(f"{base}:streamAssist", headers=headers, json=payload)
t_total = time.time() - t_start

print(f"\nTotal StreamAssist Execution Time: {t_total:.2f}s | Status: {r_run.status_code}")
try:
    chunks = json.loads(r_run.text)
    print(f"Total chunks streamed: {len(chunks)}")
    for idx, c in enumerate(chunks):
        ans = c.get("answer", {})
        state = ans.get("state", "")
        replies = ans.get("replies", [])
        for rep in replies:
            wf_ev = rep.get("workflowAdkEvent", {})
            if wf_ev:
                node_id = wf_ev.get("nodeId")
                err = wf_ev.get("errorEvent")
                print(f"  [Chunk {idx+1}] Node: {node_id} | Error: {err} | Event keys: {list(wf_ev.keys())}")
            txt = rep.get("groundedContent", {}).get("content", {}).get("text", "")
            if txt:
                print(f"  [Chunk {idx+1} Text]: {txt[:300]}...")
except Exception as e:
    print("Raw output:", r_run.text[:1500])
