# Discovery Engine Setup Guide

[<- Back to Main README](../README.md) | [Architecture](architecture.md)

## Overview

Discovery Engine (Gemini Enterprise) enables grounded search across SharePoint documents with per-user identity via Workforce Identity Federation.

```
+-------------------------------------------------------------------+
|                    DISCOVERY ENGINE ARCHITECTURE                   |
+-------------------------------------------------------------------+
|                                                                   |
|  USER QUERY: "What is the CFO salary?"                           |
|                 |                                                 |
|                 v                                                 |
|  +-----------------------------------------------------------+   |
|  |           AGENT (search_sharepoint tool)                   |   |
|  |                                                            |   |
|  |  1. Extract USER_TOKEN from tool_context.state             |   |
|  |  2. Exchange JWT via WIF/STS for GCP token                 |   |
|  |  3. Call streamAssist API with user identity               |   |
|  +-----------------------------------------------------------+   |
|                 |                                                 |
|                 v                                                 |
|  +-----------------------------------------------------------+   |
|  |           DISCOVERY ENGINE (streamAssist)                  |   |
|  |                                                            |   |
|  |  - Searches configured datastores                          |   |
|  |  - Returns textGroundingMetadata with sources              |   |
|  |  - Respects SharePoint ACLs via user identity              |   |
|  +-----------------------------------------------------------+   |
|                 |                                                 |
|                 v                                                 |
|  +-----------------------------------------------------------+   |
|  |           SHAREPOINT (via Graph API connector)             |   |
|  |                                                            |   |
|  |  - Financial Reports, HR Documents, Contracts              |   |
|  |  - Per-document ACLs respected                             |   |
|  +-----------------------------------------------------------+   |
|                                                                   |
+-------------------------------------------------------------------+
```

## Prerequisites

| Requirement | Description |
|-------------|-------------|
| Discovery Engine App | Created in Vertex AI Search |
| SharePoint Connector | Data store connected to SharePoint |
| WIF Pool + Provider | For user identity federation |
| Service Account | With Discovery Engine permissions |

## Setup Steps

### 1. Create Discovery Engine App

```bash
# Navigate to Vertex AI Search in Cloud Console
# Create new Search app with type: "Enterprise"

# App ID format: projects/{project_num}/locations/global/collections/default_collection/engines/{engine_id}
```

### 2. Connect SharePoint Data Source

```
+-----------------------------------------------------------------+
|              SHAREPOINT DATA SOURCE CONFIGURATION                |
+-----------------------------------------------------------------+
|                                                                 |
|  STEP 1: Add Data Store                                         |
|  +---------------------------------------------------------+   |
|  |  Type: Cloud Storage / SharePoint                        |   |
|  |  Source: sockcop.sharepoint.com/sites/FinancialDocument  |   |
|  +---------------------------------------------------------+   |
|                                                                 |
|  STEP 2: Configure Sync                                         |
|  +---------------------------------------------------------+   |
|  |  Frequency: Periodic (recommended: daily)                 |   |
|  |  Full sync: Weekly                                        |   |
|  +---------------------------------------------------------+   |
|                                                                 |
|  STEP 3: Verify Indexing                                        |
|  +---------------------------------------------------------+   |
|  |  Documents indexed: 150+                                  |   |
|  |  Status: ACTIVE                                           |   |
|  +---------------------------------------------------------+   |
|                                                                 |
+-----------------------------------------------------------------+
```

### 3. Configure Widget for Datastore Discovery

The agent dynamically discovers datastores using the widget config API:

```python
# agent/tools/discovery_engine.py

def _get_dynamic_datastores(self) -> List[Dict[str, str]]:
    """Fetch SharePoint datastores from widget config.
    Uses service account (admin operation)."""

    url = f"https://discoveryengine.googleapis.com/v1alpha/projects/{self._project_number}/locations/global/collections/default_collection/engines/{self._engine_id}/widgetConfigs/default_search_widget_config"

    # Use service account for admin operations
    admin_token = self._get_service_credentials()

    resp = requests.get(url, headers={
        "Authorization": f"Bearer {admin_token}",
        "Content-Type": "application/json"
    })

    # Extract datastores from response
    widget_config = resp.json()
    data_store_uids = widget_config.get("dataStoreUids", [])

    return [{"dataStore": uid} for uid in data_store_uids]
```

## API: streamAssist

The `streamAssist` API provides grounded responses with source citations.

### Request Format

```python
POST https://discoveryengine.googleapis.com/v1alpha/projects/{project_num}/locations/global/collections/default_collection/engines/{engine_id}/servingConfigs/default_search:streamAssist

{
    "query": {
        "text": "What is the CFO salary?",
        "queryId": "unique-query-id"
    },
    "session": "projects/{project_num}/locations/global/collections/default_collection/engines/{engine_id}/sessions/-",
    "safetySpec": {
        "enable": true
    },
    "dataStoreSpecs": [
        {"dataStore": "projects/{project_num}/locations/global/collections/default_collection/dataStores/deloitte-sharepoint_file"},
        {"dataStore": "projects/{project_num}/locations/global/collections/default_collection/dataStores/deloitte-sharepoint_page"}
    ]
}
```

### Response Format

```json
{
    "answer": {
        "state": "SUCCEEDED",
        "answerText": "According to the Financial Audit Report for Fiscal Year 2024, the total compensation for the CFO, Jennifer Walsh, is $3,855,000.",
        "steps": [...],
        "answerSkippedReasons": []
    },
    "textGroundingMetadata": {
        "groundingChunks": [
            {
                "chunk_text": "Executive Compensation: CFO Jennifer Walsh - Base: $450,000, Bonus: $3,405,000, Total: $3,855,000",
                "source": "01_Financial_Audit_Report_FY2024.pdf",
                "uri": "https://sockcop.sharepoint.com/sites/FinancialDocument/01_Financial_Audit_Report_FY2024.pdf"
            }
        ],
        "supportChunks": [...]
    }
}
```

## WIF Token Exchange for User Identity

```
+-----------------------------------------------------------------+
|              WIF TOKEN EXCHANGE FOR DISCOVERY ENGINE             |
+-----------------------------------------------------------------+
|                                                                 |
|  INPUT: Entra ID JWT (user's Microsoft token)                   |
|          |                                                       |
|          v                                                       |
|  +-----------------------------------------------------------+  |
|  |  STS Token Exchange                                        |  |
|  |  POST https://sts.googleapis.com/v1/token                  |  |
|  |                                                            |  |
|  |  audience: //iam.googleapis.com/locations/global/          |  |
|  |            workforcePools/{pool}/providers/{provider}      |  |
|  |  subject_token: {Entra JWT}                                |  |
|  |  subject_token_type: urn:ietf:params:oauth:token-type:jwt  |  |
|  +-----------------------------------------------------------+  |
|          |                                                       |
|          v                                                       |
|  OUTPUT: GCP Access Token (with user principal)                  |
|                                                                 |
+-----------------------------------------------------------------+
```

### Code Implementation

```python
# agent/tools/discovery_engine.py

def exchange_wif_token(self, user_id_token: str) -> str:
    """Exchange Entra ID JWT for GCP access token via STS."""

    sts_url = "https://sts.googleapis.com/v1/token"
    audience = f"//iam.googleapis.com/locations/global/workforcePools/{self._wif_pool_id}/providers/{self._wif_provider_id}"

    payload = {
        "audience": audience,
        "grantType": "urn:ietf:params:oauth:grant-type:token-exchange",
        "subjectToken": user_id_token,
        "subjectTokenType": "urn:ietf:params:oauth:token-type:jwt",
        "requestedTokenType": "urn:ietf:params:oauth:token-type:access_token",
        "scope": "https://www.googleapis.com/auth/cloud-platform"
    }

    response = requests.post(sts_url, json=payload)
    return response.json()["access_token"]
```

## Environment Variables

```bash
# agent/.env

# Discovery Engine
PROJECT_NUMBER=440133963879
DISCOVERY_ENGINE_ID=deloitte-demo

# WIF Configuration
WIF_POOL_ID=entra-id-oidc-pool-d
WIF_PROVIDER_ID=entra-id-oidc-pool-provider-de
```

## Common Issues

### Issue: "Unknown name description"

**Error:**
```
400 Bad Request: Invalid JSON payload received. Unknown name "description"
```

**Cause:** Including `description` field in `dataStoreSpecs`

**Fix:**
```python
# WRONG
dataStoreSpecs = [{"dataStore": "...", "description": "SharePoint files"}]

# CORRECT
dataStoreSpecs = [{"dataStore": "..."}]  # No description field
```

### Issue: Dynamic Datastores Returns Empty

**Error:**
```
[DE] Dynamic datastores found: 0
[DE] Using default datastore configuration
```

**Cause:** Using user WIF token for admin operation

**Fix:** Use service account credentials for `_get_dynamic_datastores()`:
```python
def _get_dynamic_datastores(self):
    # Use service account, NOT user token
    admin_token = self._get_service_credentials()
```

### Issue: No textGroundingMetadata

**Cause:** Response not being parsed correctly

**Fix:** Handle SSE streaming response:
```python
for chunk in response.iter_lines():
    if chunk:
        data = json.loads(chunk)
        if "textGroundingMetadata" in data:
            # Extract grounding info
```

## Testing

### Local Test

```python
# test_discovery_engine.py

from tools.discovery_engine import DiscoveryEngineClient

client = DiscoveryEngineClient()
response = client.search("What is the CFO salary?", user_token="eyJ...")

print(f"Answer: {response['answer']}")
print(f"Sources: {response['sources']}")
```

### Verify SharePoint ACLs

```bash
# User A (has access)
Query: "What is the CFO salary?"
Result: "Jennifer Walsh, $3,855,000" with sources

# User B (no access)
Query: "What is the CFO salary?"
Result: "I don't have access to documents containing that information"
```

## Related Documentation

- [Architecture Overview](architecture.md)
- [Security Flow](security-flow.md)
- [WIF Setup](gcp-setup.md#workforce-identity-federation)
- [Troubleshooting](troubleshooting.md)
