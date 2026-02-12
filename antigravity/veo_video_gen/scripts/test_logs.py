import os
from google.cloud import logging

project_id = os.environ.get("GOOGLE_CLOUD_PROJECT", "vtxdemos")
client = logging.Client(project=project_id)

FILTER = '''
resource.type="aiplatform.googleapis.com/ReasoningEngine"
severity>="ERROR"
'''

print("--- REASONING ENGINE ERRORS ---")
for entry in client.list_entries(filter_=FILTER, order_by=logging.DESCENDING, max_results=20):
    payload = entry.payload
    if isinstance(payload, dict) and "message" in payload:
        payload = payload["message"]
    print(f"[{entry.timestamp}] {entry.severity}: {payload}")

