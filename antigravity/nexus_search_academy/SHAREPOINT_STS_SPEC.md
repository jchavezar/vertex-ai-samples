# 🛰️ SharePoint Grounding: Authentication & DataStore Specifications

> **Core Objective:** Authenticate securely using Federated Workload Identity (WIF) and ground queries transparently against high-security SharePoint Connected Indices without statically managing long-lived static service account keys.

---

## 🔑 Phase 1: The Token Exchange Cycle

To access the Discovery Engine via Vertex AI StreamAssist APIs using a corporate identity system (e.g., Microsoft Entra ID), follow this token translation track:

### ⚡ Step 1: Obtain a federated `id_token`
Your Client logs in using standard OAuth 2.0 against the Microsoft Entra ID Endpoint.
*   **Result:** returns `id_token` (JWT representation for the user's corporate context).

### ⚡ Step 2: Swap at Google STS (Secure Token Service)
The Backend forwards the user's `id_token` into Google STS to exchange it for a temporary Google Cloud Access Token bound securely to the target IAM role permissions.

```python
# python snippet exchange
import requests

def exchange_wif_token(user_id_token):
    sts_url = "https://sts.googleapis.com/v1/token"
    payload = {
        "audience": "//iam.googleapis.com/projects/[PROJECT_NUMBER]/locations/global/workloadIdentityPools/[POOL_ID]/providers/[PROVIDER_ID]",
        "grantType": "urn:ietf:params:oauth:grant-type:token-exchange",
        "requestedTokenType": "urn:ietf:params:oauth:token-type:access_token",
        "scope": "https://www.googleapis.com/auth/cloud-platform",
        "subjectToken": user_id_token,
        "subjectTokenType": "urn:ietf:params:oauth:token-type:jwt"
    }
    
    response = requests.post(sts_url, json=payload)
    # Returns google_access_token
    return response.json().get("access_token")
```

---

## 🔍 Optional: dynamic DataStore Lookup with Google Admin Credentials

If your backend needs to query the structure of the Discovery Engines/DataStores dynamically instead of using hardcoded specification indexes, load standard Service Account permissions on the background thread backends:

```python
import google.auth
from google.auth.transport.requests import Request
import requests

def get_available_datastores(project_number):
    try:
        # 🛡️ 1. Elevated Service Account contexts
        creds, _ = google.auth.default()
        auth_req = Request()
        creds.refresh(auth_req) # Loads creds.token

        ds_url = f"https://discoveryengine.googleapis.com/v1alpha/projects/{project_number}/locations/global/collections/default_collection/dataStores"
        
        headers = {
            'Authorization': f'Bearer {creds.token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(ds_url, headers=headers)
        
        # 2. Extract DataStore Names specs
        details = response.json().get("dataStores", [])
        return [ {"dataStore": d["name"]} for d in details ]
        
    except Exception as e:
        print(f"Discovery payload error: {e}")
        return []
```

---

## 🛰️ Phase 2: Vertex AI ToolsSpec DataStore Structure

To specifically target SharePoint Online Federated Corpora indices or connect datasets dynamically, forward the `access_token` inside header headers and structure the **payload tools list** using descriptive string mapping values.

### 📝 Accurate Payload Template
Forward this explicit dictionary inside your stream-assist stream loop or query trigger endpoints:

```python
## Vertex AI DataStore Specifications Payload
payload = {
    "query": "Who is our current Chief Financial Officer?",
    "toolsSpec": {
        "vertexAiSearchSpec": {
            "dataStoreSpecs": [
                {
                    # 🚀 Directly targets the SharePoint Connected index
                    "dataStore": "projects/REDACTED_PROJECT_NUMBER/locations/global/collections/default_collection/dataStores/5817ee80-82a4-49e3-a19c-2cedc73a6300",
                    "description": "SharePoint Online Federated Corpus" 
                }
            ]
        }
    }
}
```

### 📡 Execute Target Streaming Loop
```python
headers = {
    "Authorization": f"Bearer {exchange_access_token}",
    "Content-Type": "application/json"
}

assist_url = "https://discoveryengine.googleapis.com/v1beta/projects/[PROJECT_NUMBER]/locations/global/collections/default_collection/engines/[ENGINE_ID]/servingConfigs/default_serving_config:streamAssist"

response = requests.post(assist_url, headers=headers, json=payload, stream=True)
```

By supplying the implicit index mapping path above directly inside the header structure config setups, Vertex AI executes compliant queries verifying strictly tailored layout file trees based on user role authorization layers! 🚀
