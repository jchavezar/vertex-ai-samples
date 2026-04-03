"""Debug WIF exchange and Discovery Engine call"""
import requests
import os
from dotenv import load_dotenv
load_dotenv()

# Get JWT from environment or test UI
JWT = os.environ.get("TEST_JWT", "")

WIF_POOL_ID = os.environ.get("WIF_POOL_ID", "entra-id-oidc-pool-d")
WIF_PROVIDER_ID = os.environ.get("WIF_PROVIDER_ID", "entra-id-oidc-pool-provider-de")
PROJECT_NUMBER = os.environ.get("PROJECT_NUMBER", "REDACTED_PROJECT_NUMBER")
ENGINE_ID = os.environ.get("ENGINE_ID", "deloitte-demo")

print("=" * 60)
print("[1] Testing WIF Exchange")
print("=" * 60)
print(f"Pool: {WIF_POOL_ID}")
print(f"Provider: {WIF_PROVIDER_ID}")

sts_url = "https://sts.googleapis.com/v1/token"
audience = f"//iam.googleapis.com/locations/global/workforcePools/{WIF_POOL_ID}/providers/{WIF_PROVIDER_ID}"

payload = {
    "audience": audience,
    "grantType": "urn:ietf:params:oauth:grant-type:token-exchange",
    "requestedTokenType": "urn:ietf:params:oauth:token-type:access_token",
    "scope": "https://www.googleapis.com/auth/cloud-platform",
    "subjectToken": JWT,
    "subjectTokenType": "urn:ietf:params:oauth:token-type:jwt"
}

resp = requests.post(sts_url, json=payload, timeout=30)
print(f"Status: {resp.status_code}")
print(f"Response: {resp.text[:800]}")

if resp.status_code != 200:
    print("\n[ERROR] WIF exchange failed - stopping")
    exit(1)

gcp_token = resp.json().get("access_token")
print(f"\n[2] Got GCP Token (length: {len(gcp_token)})")

print("\n" + "=" * 60)
print("[3] Fetching Datastores")
print("=" * 60)
print(f"Project: {PROJECT_NUMBER}")
print(f"Engine: {ENGINE_ID}")

widget_url = f"https://discoveryengine.googleapis.com/v1alpha/projects/{PROJECT_NUMBER}/locations/global/collections/default_collection/engines/{ENGINE_ID}/widgetConfigs/default_search_widget_config"
headers = {
    "Authorization": f"Bearer {gcp_token}",
    "Content-Type": "application/json",
    "X-Goog-User-Project": PROJECT_NUMBER
}

ds_resp = requests.get(widget_url, headers=headers, timeout=30)
print(f"Widget config status: {ds_resp.status_code}")

datastores = []
if ds_resp.status_code == 200:
    for comp in ds_resp.json().get('collectionComponents', [{}]):
        for ds in comp.get('dataStoreComponents', []):
            datastores.append({'dataStore': ds['name']})
            print(f"Found datastore: {ds['name']}")
else:
    print(f"Widget error: {ds_resp.text[:500]}")
    # Fallback
    DATA_STORE_ID = os.environ.get("DATA_STORE_ID", "5817ee80-82a4-49e3-a19c-2cedc73a6300")
    datastores = [{"dataStore": f"projects/{PROJECT_NUMBER}/locations/global/collections/default_collection/dataStores/{DATA_STORE_ID}"}]
    print(f"Using fallback datastore: {DATA_STORE_ID}")

print("\n" + "=" * 60)
print("[4] Testing streamAssist API")
print("=" * 60)

query = "what is the salary of a cfo?"
url = f"https://discoveryengine.googleapis.com/v1alpha/projects/{PROJECT_NUMBER}/locations/global/collections/default_collection/engines/{ENGINE_ID}/assistants/default_assistant:streamAssist"

payload = {"query": {"text": query}}
if datastores:
    payload["toolsSpec"] = {"vertexAiSearchSpec": {"dataStoreSpecs": datastores}}
    print(f"Using {len(datastores)} datastoreSpecs")

print(f"Query: {query}")
print(f"URL: {url}")

search_resp = requests.post(url, headers=headers, json=payload, timeout=60)
print(f"Status: {search_resp.status_code}")
print(f"Response (first 1500): {search_resp.text[:1500]}")
