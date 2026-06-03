# Developer Guide: WIF & Discovery Engine streamAssist Integration

> **Next-Generation API Integration Guide**  
> Learn how to build single-click, zero-credential search interfaces using Microsoft Entra ID (Azure AD), Google Workforce Identity Federation (WIF), and Gemini Enterprise.

---

## 1. The Token Exchange Protocol

Instead of managing server-side API keys or database service account files, this architecture uses a **Federated Token Exchange**. The client browser obtains a temporary identity from Entra ID and exchanges it directly for Google Cloud access.

```mermaid
sequenceDiagram
    autonumber
    actor User as Corporate User
    participant Client as SPA Frontend (Browser)
    participant Entra as Microsoft Entra ID
    participant STS as Google Security Token Service (STS)
    participant Search as Vertex AI Search API

    User->>Client: Click "Sign In & Search"
    Client->>Entra: loginPopup(scope: api://{client_id}/user_impersonation)
    Entra->>User: Display Login & MFA prompts
    User->>Entra: Approve credentials
    Entra->>Client: Return Microsoft Access Token (Audience: api://{client_id})
    
    Note over Client,STS: Token exchange happens transparently in the background
    Client->>STS: POST /v1/token (Subject Token: MS Access Token)
    STS->>Client: Return Google WIF Token (Access to GCP)

    Client->>Search: POST streamAssist (Bearer Google WIF Token)
    Search->>Client: Stream grounded answer + source document citations
```

---

## 2. API Integration Protocol

### Step 1: Microsoft Entra ID Authentication
Initialize the MSAL instance on the frontend and trigger the login. You must request the custom scope `api://{YOUR_CLIENT_ID}/user_impersonation` to ensure Microsoft issues a token compatible with Google WIF's audience mapping.

```javascript
import * as msal from "@azure/msal-browser";

const msalConfig = {
  auth: {
    clientId: "7868d053-cf9c-4848-be5a-f9bbf8279234",
    authority: "https://login.microsoftonline.com/de46a3fd-0d68-4b25-8343-6eb5d71afce9",
    redirectUri: window.location.origin
  }
};

const msalApp = new msal.PublicClientApplication(msalConfig);

async function getEntraToken() {
  const loginResponse = await msalApp.loginPopup({
    scopes: ["openid", "profile", "email", "api://7868d053-cf9c-4848-be5a-f9bbf8279234/user_impersonation"]
  });
  return loginResponse.accessToken; // Used as the subject_token in the next step
}
```

---

### Step 2: Google STS Token Exchange
Exchange the Microsoft Access Token for a Google Cloud Access Token using the Google Security Token Service (STS).

> [!TIP]
> Ensure the `subject_token_type` is set to `urn:ietf:params:oauth:token-type:jwt` since we are validating a Microsoft Access Token.

```http
POST https://sts.googleapis.com/v1/token
Content-Type: application/x-www-form-urlencoded

grant_type=urn:ietf:params:oauth:grant-type:token-exchange
&audience=//iam.googleapis.com/locations/global/workforcePools/sp-wif-pool-v2/providers/entra-provider
&scope=https://www.googleapis.com/auth/cloud-platform
&requested_token_type=urn:ietf:params:oauth:token-type:access_token
&subject_token_type=urn:ietf:params:oauth:token-type:jwt
&subject_token=YOUR_MICROSOFT_ACCESS_TOKEN
```

---

### Step 3: Call streamAssist with Grounding Spec
Once you obtain the Google Access Token, call the Discovery Engine regional endpoints. You **MUST** define `dataStoreSpecs` to point the search model to your private GCS or SharePoint datastores.

#### Request Specification
```http
POST https://discoveryengine.googleapis.com/v1alpha/projects/254356041555/locations/global/collections/default_collection/engines/YOUR_ENGINE_ID/assistants/default_assistant:streamAssist
Authorization: Bearer YOUR_GOOGLE_ACCESS_TOKEN
X-Goog-User-Project: vtxdemos
Content-Type: application/json

{
  "query": {
    "text": "Summarize the key financial highlights from the document."
  },
  "toolsSpec": {
    "vertexAiSearchSpec": {
      "dataStoreSpecs": [
        {
          "dataStore": "projects/254356041555/locations/global/collections/default_collection/dataStores/YOUR_DATASTORE_ID"
        }
      ]
    }
  }
}
```

---

## 3. Code Implementation Snippets

Below are complete snippets to orchestrate the entire flow (Token Exchange + Query) in Javascript and Python.

```carousel
```javascript
// JavaScript / Node.js
async function runQuery(microsoftToken, queryText) {
  // A. STS Exchange
  const stsParams = new URLSearchParams({
    grant_type: "urn:ietf:params:oauth:grant-type:token-exchange",
    audience: "//iam.googleapis.com/locations/global/workforcePools/sp-wif-pool-v2/providers/entra-provider",
    scope: "https://www.googleapis.com/auth/cloud-platform",
    requested_token_type: "urn:ietf:params:oauth:token-type:access_token",
    subject_token_type: "urn:ietf:params:oauth:token-type:jwt",
    subject_token: microsoftToken
  });

  const stsResp = await fetch("https://sts.googleapis.com/v1/token", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: stsParams.toString()
  });
  const { access_token: googleToken } = await stsResp.json();

  // B. streamAssist Search
  const searchUrl = "https://discoveryengine.googleapis.com/v1alpha/projects/254356041555/locations/global/collections/default_collection/engines/YOUR_ENGINE_ID/assistants/default_assistant:streamAssist";
  const searchResp = await fetch(searchUrl, {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${googleToken}`,
      "Content-Type": "application/json",
      "X-Goog-User-Project": "vtxdemos"
    },
    body: JSON.stringify({
      query: { text: queryText },
      toolsSpec: {
        vertexAiSearchSpec: {
          dataStoreSpecs: [{
            dataStore: "projects/254356041555/locations/global/collections/default_collection/dataStores/YOUR_DATASTORE_ID"
          }]
        }
      }
    })
  });
  return await searchResp.json();
}
```
<!-- slide -->
```python
# Python 3
import requests

def run_query(microsoft_token: str, query_text: str):
    # A. STS Exchange
    sts_data = {
        "grant_type": "urn:ietf:params:oauth:grant-type:token-exchange",
        "audience": "//iam.googleapis.com/locations/global/workforcePools/sp-wif-pool-v2/providers/entra-provider",
        "scope": "https://www.googleapis.com/auth/cloud-platform",
        "requested_token_type": "urn:ietf:params:oauth:token-type:access_token",
        "subject_token_type": "urn:ietf:params:oauth:token-type:jwt",
        "subject_token": microsoft_token
    }
    
    sts_resp = requests.post(
        "https://sts.googleapis.com/v1/token",
        data=sts_data
    ).json()
    google_token = sts_resp["access_token"]

    # B. streamAssist Search
    search_url = "https://discoveryengine.googleapis.com/v1alpha/projects/254356041555/locations/global/collections/default_collection/engines/YOUR_ENGINE_ID/assistants/default_assistant:streamAssist"
    headers = {
        "Authorization": f"Bearer {google_token}",
        "Content-Type": "application/json",
        "X-Goog-User-Project": "vtxdemos"
    }
    payload = {
        "query": {"text": query_text},
        "toolsSpec": {
            "vertexAiSearchSpec": {
                "dataStoreSpecs": [{
                    "dataStore": "projects/254356041555/locations/global/collections/default_collection/dataStores/YOUR_DATASTORE_ID"
                }]
            }
        }
    }
    
    resp = requests.post(search_url, headers=headers, json=payload)
    return resp.json()
```
````

---

## 4. Troubleshooting Matrix

| Error Code / Symptom | Root Cause | Solution |
|----------------------|------------|----------|
| `invalid_grant` / Audience mismatch | The Microsoft Token was issued with the wrong audience claim. | Verify you requested the custom scope `api://{client_id}/user_impersonation` during MSAL login, not Graph API scopes like `user.read`. |
| `PERMISSION_DENIED` on search API | The Google workforce identity principal lacks required permissions. | Add the `roles/discoveryengine.admin` (or `viewer` and `user`) role to your pool's principal set in GCP IAM. |
| Grounding returns plausible answer but has zero citations / sources | The dataStore spec was omitted or set incorrectly. | Ensure your payload includes `toolsSpec.vertexAiSearchSpec.dataStoreSpecs` mapping the exact datastore ID path. |
| `FAILED_PRECONDITION` | Implicit flow is disabled in Entra ID. | Edit your Azure App Registration and verify that **ID tokens** are checked under Implicit Grant / Hybrid Flows. |
