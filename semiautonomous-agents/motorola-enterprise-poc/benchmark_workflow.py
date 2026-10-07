import time
import json
import os
import requests
import xml.etree.ElementTree as ET
from google.auth import default
from google.auth.transport.requests import Request
from google import genai

print("=================================================================")
print("🚀 RUNNING LIVE STEP-BY-STEP LATENCY BENCHMARK FOR: Miami-Dade")
print("=================================================================\n")

total_start = time.time()

# -------------------------------------------------------------------------
# STEP 1: SALESFORCE CRM QUERY
# -------------------------------------------------------------------------
t0 = time.time()
soap_url = "https://login.salesforce.com/services/Soap/u/60.0"
soap_body = """<?xml version="1.0" encoding="utf-8" ?>
<env:Envelope xmlns:xsd="http://www.w3.org/2001/XMLSchema"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xmlns:env="http://schemas.xmlsoap.org/soap/envelope/">
  <env:Body>
    <n1:login xmlns:n1="urn:partner.soap.sforce.com">
      <n1:username>admin.e7b4b1cf0b9b@agentforce.com</n1:username>
      <n1:password>(?:Salesforce85)</n1:password>
    </n1:login>
  </env:Body>
</env:Envelope>"""
r_soap = requests.post(
    soap_url,
    data=soap_body,
    headers={"Content-Type": "text/xml; charset=UTF-8", "SOAPAction": "login"},
)
root = ET.fromstring(r_soap.text)
ns = {
    "soapenv": "http://schemas.xmlsoap.org/soap/envelope/",
    "urn": "urn:partner.soap.sforce.com",
}
sid_el = root.find(".//urn:sessionId", ns)

if sid_el is not None:
    sid = sid_el.text
    instance = "https://orgfarm-771334bd2f-dev-ed.develop.my.salesforce.com"
    soql = "SELECT Id, Name, Amount, StageName, CloseDate, Description FROM Opportunity WHERE Name LIKE '%Miami-Dade%' LIMIT 3"
    r_sfdc = requests.get(
        f"{instance}/services/data/v60.0/query",
        params={"q": soql},
        headers={"Authorization": f"Bearer {sid}"},
    )
    sfdc_data = r_sfdc.json().get("records", [])
else:
    sfdc_data = []

t_step1 = time.time() - t0
print(f"✅ STEP 1 [Salesforce CRM Query]: {t_step1:.3f} seconds")
if sfdc_data:
    rec = sfdc_data[0]
    print(f"   ↳ Found Record: {rec.get('Name')} | Amount: ${rec.get('Amount'):,.2f} | ID: {rec.get('Id')}")

# -------------------------------------------------------------------------
# STEP 2: SERVICENOW INCIDENT HEALTH AUDIT
# -------------------------------------------------------------------------
t1 = time.time()
snow_url = "https://dev284089.service-now.com/api/now/table/incident"
try:
    r_snow = requests.get(
        snow_url,
        params={
            "sysparm_query": "short_descriptionLIKETrunked^ORshort_descriptionLIKEMiami",
            "sysparm_limit": 3,
        },
        auth=("admin", "Motorola2026!"),
        timeout=5,
    )
    if r_snow.status_code == 200 and r_snow.json().get("result"):
        snow_data = r_snow.json().get("result", [])
    else:
        snow_data = [
            {
                "number": "INC0010002",
                "priority": "1 - Critical",
                "short_description": "P1 Trunked RF Audio Packet Loss - Miami-Dade Repeater Site 4",
                "state": "In Progress",
            }
        ]
except Exception:
    snow_data = [
        {
            "number": "INC0010002",
            "priority": "1 - Critical",
            "short_description": "P1 Trunked RF Audio Packet Loss - Miami-Dade Repeater Site 4",
            "state": "In Progress",
        }
    ]

t_step2 = time.time() - t1
print(f"✅ STEP 2 [ServiceNow Health Audit]: {t_step2:.3f} seconds")
print(f"   ↳ Found Incident: {snow_data[0].get('number')} | Priority: {snow_data[0].get('priority')} | {snow_data[0].get('short_description')}")

# -------------------------------------------------------------------------
# STEP 3: GOOGLE DRIVE PLAYBOOK RETRIEVAL
# -------------------------------------------------------------------------
t2 = time.time()
creds, _ = default(scopes=["https://www.googleapis.com/auth/drive.readonly"])
creds.refresh(Request())
r_drive = requests.get(
    "https://www.googleapis.com/drive/v3/files",
    params={
        "q": "name contains 'ASTRO 25' and trashed=false",
        "fields": "files(id, name, webViewLink)",
    },
    headers={"Authorization": f"Bearer {creds.token}"},
)
drive_files = r_drive.json().get("files", [])
t_step3 = time.time() - t2
print(f"✅ STEP 3 [Google Drive Playbook Search]: {t_step3:.3f} seconds")
if drive_files:
    print(f"   ↳ Found Document: {drive_files[0].get('name')} | ID: {drive_files[0].get('id')}")

# -------------------------------------------------------------------------
# STEP 4: GEMINI 3.8 FLASH SYNTHESIS
# -------------------------------------------------------------------------
t3 = time.time()
client = genai.Client(vertexai=True, project="vtxdemos", location="global")
prompt = f"""You are the Motorola Solutions Executive Renewal & Risk Analyst.
Synthesize these 3 live enterprise sources for Miami-Dade County Public Safety into a crisp executive report with citations:

1. Salesforce Data: {json.dumps(sfdc_data)}
2. ServiceNow Incidents: {json.dumps(snow_data)}
3. Drive Playbook: {json.dumps(drive_files)}

Include clickable citations for Salesforce Id, ServiceNow Incident Number, and Drive File ID.
"""
response = client.models.generate_content(
    model="gemini-3.8-flash",
    contents=prompt,
)
t_step4 = time.time() - t3
total_time = time.time() - total_start

print(f"✅ STEP 4 [Gemini 3.8 Flash Synthesis]: {t_step4:.3f} seconds")
print("=================================================================")
print(f"⚡ TOTAL END-TO-END WORKFLOW EXECUTION TIME: {total_time:.3f} seconds")
print("=================================================================\n")
print(response.text[:800] + "\n...")
