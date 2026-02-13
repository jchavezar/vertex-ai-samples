import requests
import json
import os
from dotenv import load_dotenv
import msal

load_dotenv(dotenv_path="../.env")

tenant_id = os.getenv("TENANT_ID")
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

options = {"tenant_id": tenant_id, "client_id": client_id, "client_secret": client_secret}
authority = f"https://login.microsoftonline.com/{options['tenant_id']}"
app = msal.ConfidentialClientApplication(
    options["client_id"],
    authority=authority,
    client_credential=options["client_secret"]
)

result = app.acquire_token_silent(["https://graph.microsoft.com/.default"], account=None)
if not result:
    result = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])

token = result["access_token"]
headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json", "Region": "NAM"}

print("Searching Graph for 'MA_Due_Diligence' or 'Acquisition'...")
search_url = "https://graph.microsoft.com/v1.0/search/query"
payload = {
    "requests": [{
        "entityTypes": ["driveItem"],
        "query": { "queryString": "MA Due Diligence OR Acquisition" },
        "fields": ["name", "id", "webUrl", "parentReference"],
        "region": "NAM",
        "size": 10
    }]
}

res = requests.post(search_url, headers=headers, json=payload)
data = res.json()
print("Search Results:")
try:
    for hit in data['value'][0]['hitsContainers'][0]['hits']:
        item = hit['resource']
        print(f"File: {item.get('name')} (ID: {item.get('id')})")
        print(f" URL: {item.get('webUrl')}")
        refs = item.get('parentReference', {})
        print(f" => Drive ID: {refs.get('driveId')}")
        print(f" => Site ID:  {refs.get('siteId')}")
        print("-------")
except Exception as e:
    print(f"Error parse hits: {e}")
    print(json.dumps(data, indent=2))

print("Searching Graph for 'Financial'...")
payload2 = {
    "requests": [{
        "entityTypes": ["driveItem"],
        "query": { "queryString": "Financial" },
        "fields": ["name", "id", "webUrl", "parentReference", "listId", "siteId"],
        "region": "NAM",
        "size": 10
    }]
}
res2 = requests.post(search_url, headers=headers, json=payload2)
data2 = res2.json()
print("\nSearch Results (Financial):")
try:
    for hit in data2['value'][0]['hitsContainers'][0]['hits']:
        item = hit['resource']
        print(f"File: {item.get('name')} (ID: {item.get('id')})")
        print(f" URL: {item.get('webUrl')}")
        refs = item.get('parentReference', {})
        print(f" => Site ID:  {refs.get('siteId')}")
        print(f" => Drive ID: {refs.get('driveId')}")
        print("-------")
except Exception as e:
    print(f"Error parse hits: {e}")

