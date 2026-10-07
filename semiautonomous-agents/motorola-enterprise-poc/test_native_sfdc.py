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

search_url = "https://discoveryengine.googleapis.com/v1alpha/projects/254356041555/locations/global/collections/default_collection/dataStores/sfdc_opportunity/servingConfigs/default_search:search"

t0 = time.time()
r = requests.post(search_url, headers=headers, json={"query": "Miami-Dade", "pageSize": 3})
t_native = time.time() - t0

print(f"⚡ NATIVE SALESFORCE CONNECTOR (sfdc_opportunity) LATENCY: {t_native:.3f} seconds! (HTTP {r.status_code})")
print("Results snippet:", r.text[:600])
