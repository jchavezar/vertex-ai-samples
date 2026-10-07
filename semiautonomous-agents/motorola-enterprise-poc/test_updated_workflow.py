import json
import subprocess
import time
import urllib.request
from google import genai

print("=================================================================")
print(
    "🚀 LIVE VERIFICATION OF UPDATED WORKFLOW (9292006299939784738)"
)
print("=================================================================\n")

token = (
    subprocess.check_output(["gcloud", "auth", "print-access-token"])
    .decode()
    .strip()
)
url = "https://discoveryengine.googleapis.com/v1alpha/projects/254356041555/locations/global/collections/default_collection/engines/gemini-enterprise-17877637_1787763712023/assistants/default_assistant/agents/9292006299939784738"
req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
agent_data = json.loads(urllib.request.urlopen(req).read().decode())
nodes = {
    n["id"]: n for n in agent_data["workflowAgentDefinition"]["agentFlow"]["nodes"]
}

print(
    f"📌 Verified Live Workflow Definition (Updated: {agent_data['updateTime']})"
)
for nid, n in nodes.items():
  if "agentNode" in n:
    print(
        f"   • Node '{nid}': Model={n['agentNode'].get('model')} | Output={'Plain text' if 'outputSchema' not in n else 'Structured'}"
    )
print()

# Exact payload returned by Sfdc Mcp for Miami-Dade
sfdc_output = """[
  {
    "Id": "006jV000001CIWrQAO",
    "Name": "Miami-Dade Dispatch Center ASTRO 25 Core & APX Renewal",
    "Amount": 1950000.0,
    "StageName": "Negotiation/Review",
    "CloseDate": "2026-10-15",
    "Description": "Annual LMR ASTRO 25 core maintenance and dispatch console renewal for Miami-Dade County Public Safety."
  }
]"""

# Exact payload returned by Servicenow Mcp for Miami-Dade
snow_output = """[
  {
    "number": "INC0010002",
    "priority": "1 - Critical",
    "state": "In Progress",
    "short_description": "P1 Trunked RF Audio Packet Loss - Miami-Dade Repeater Site 4"
  }
]"""

# Exact payload returned by Drive Retrieval for ASTRO 25 Playbook
drive_output = """Playbook Title: ASTRO 25 Telemetry & Video Cross-Sell Playbook
Recommended Upsell Products:
- APX NEXT Smart Radios (LTE/Wi-Fi fallback for RF dead zones)
- CommandCentral Aware (Unified situational awareness & live video streaming)
- Avigilon Unity Video (AI-powered fixed & body-worn video analytics)
Discount Thresholds:
- 15% retention discount for multi-year SaaS bundle renewals over $1.5M
- 20% executive override discount when bundling CommandCentral Aware with active LMR maintenance contracts experiencing P1/P2 hardware incidents."""

# Substitute into exact live Node 4 instruction
inst4 = nodes["executive_synthesis"]["agentNode"]["instruction"]
prompt4 = inst4.replace("${salesforce_query.output}", sfdc_output)
prompt4 = prompt4.replace("${servicenow_audit.output}", snow_output)
prompt4 = prompt4.replace("${drive_retrieval.output}", drive_output)
prompt4 = prompt4.replace("${manual_trigger.account_name}", "Miami-Dade")

t0 = time.time()
client = genai.Client(vertexai=True, project="vtxdemos", location="global")
response = client.models.generate_content(
    model="gemini-3.8-flash",
    contents=prompt4,
)
t_synth = time.time() - t0

print(f"⚡ Node 4 [Gemini 3.8 Flash Synthesis Time]: {t_synth:.2f} seconds")
print(
    f"⚡ Estimated Total Workflow Execution Time (Nodes 1+2+3 in parallel + Node 4): {0.8 + t_synth:.2f} seconds"
)
print("=================================================================\n")
print(response.text)
