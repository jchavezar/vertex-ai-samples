import requests
import json
from google.auth import default
from google.auth.transport.requests import Request

creds, _ = default()
creds.refresh(Request())
headers = {"Authorization": f"Bearer {creds.token}", "X-Goog-User-Project": "vtxdemos"}

url = "https://discoveryengine.googleapis.com/v1alpha/projects/254356041555/locations/global/collections/default_collection/dataStores"
r = requests.get(url, headers=headers)
for ds in r.json().get("dataStores", []):
    if "sfdc" in ds.get("name", "") or "mcp" in ds.get("name", ""):
        print("DataStore:", ds["name"])
        print(json.dumps(ds, indent=2))
