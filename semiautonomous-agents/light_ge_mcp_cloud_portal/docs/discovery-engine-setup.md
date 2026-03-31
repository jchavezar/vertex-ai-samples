# Discovery Engine Setup Guide

[<- Back to Main README](../README.md) | [Architecture](architecture.md) | [Security Flow](security-flow.md) | [Troubleshooting](troubleshooting.md)

## Overview

Discovery Engine (Gemini Enterprise) enables grounded search across SharePoint documents with per-user identity via Workforce Identity Federation.

```
USER: "What is the CFO salary?"
         |
         v
+------------------+     +---------------------+     +------------------+
|  1. WIF Exchange |---->|  2. streamAssist    |---->|  3. SharePoint   |
|  Entra JWT → GCP |     |  + dataStoreSpecs   |     |  ACL-filtered    |
+------------------+     +---------------------+     +------------------+
         |
         v
RESPONSE: "Jennifer Walsh, $3,855,000" + source citations
```

## Two Requirements for Grounded Responses

| # | Requirement | Description |
|---|-------------|-------------|
| **1** | **User Access Token** | Entra ID JWT → STS → GCP Token (for ACL enforcement) |
| **2** | **dataStoreSpecs** | Tells streamAssist which datastores to search |

### Real API Output Comparison

**Query:** "What is the salary of a CFO?"

| Scenario | API Response |
|----------|--------------|
| **WITHOUT dataStoreSpecs** | *"The salary of a CFO can vary widely... In the United States, the average salary for a CFO is around **$400,000 per year**. However, for smaller companies, it might be closer to **$150,000**, while for large corporations, it can easily exceed **$1 million**..."* |
| **WITH dataStoreSpecs + Service Account** | *"I am sorry, I was unable to find any information about the salary of a CFO in your internal documents."* |
| **WITH dataStoreSpecs + User Token (WIF)** | *"According to the Financial Audit Report for Fiscal Year 2024, the total compensation for the CFO, **Jennifer Walsh**, is **$3,855,000**."* + `textGroundingMetadata` with source: `01_Financial_Audit_Report_FY2024.pdf` |

**Key insight:** The middle row proves dataStoreSpecs works - it tried searching SharePoint but the service account lacks ACL access. Only the user token (via WIF) can access ACL-protected documents.

---

## Connector Type: Federated Identity

| Type | Data Location | ACL Enforcement | Sync |
|------|---------------|-----------------|------|
| **Federated (this project)** | Stays in SharePoint | At query time via WIF | No |
| 3P Connector | Copied to GCP | At index time | Yes |

Data remains in SharePoint. User permissions are enforced at query time through WIF token exchange.

---

## streamAssist API

**Endpoint:**
```
POST https://discoveryengine.googleapis.com/v1alpha/projects/{project}/locations/global/collections/default_collection/engines/{engine}/assistants/default_assistant:streamAssist
```

**[Official API Reference](https://cloud.google.com/generative-ai-app-builder/docs/reference/rest/v1alpha/projects.locations.collections.engines.assistants/streamAssist)**

### Request Format

```http
Authorization: Bearer {user_gcp_token}
Content-Type: application/json
```

```json
{
  "query": {"text": "What is the CFO salary?"},
  "toolsSpec": {
    "vertexAiSearchSpec": {
      "dataStoreSpecs": [
        {"dataStore": "projects/.../dataStores/sharepoint_file"},
        {"dataStore": "projects/.../dataStores/sharepoint_page"}
      ]
    }
  }
}
```

### Common Mistake

```json
// WRONG - dataStoreSpecs at root (ignored!)
{"query": {...}, "dataStoreSpecs": [...]}

// CORRECT - nested in toolsSpec.vertexAiSearchSpec
{"query": {...}, "toolsSpec": {"vertexAiSearchSpec": {"dataStoreSpecs": [...]}}}
```

### Response Format

```json
{
  "answer": {
    "answerText": "According to the Financial Audit Report FY2024, the CFO Jennifer Walsh's total compensation is $3,855,000."
  },
  "textGroundingMetadata": {
    "references": [
      {
        "documentMetadata": {
          "title": "01_Financial_Audit_Report_FY2024.pdf",
          "uri": "https://CONTOSO.sharepoint.com/..."
        }
      }
    ]
  }
}
```

**Verify grounding:** If `textGroundingMetadata.references` is present → grounded. If missing → check dataStoreSpecs.

---

## How dataStoreSpecs Are Fetched

Datastores are discovered dynamically from the widget config (not hardcoded):

```python
# agent/tools/discovery_engine.py

def _get_dynamic_datastores(self):
    """Fetch datastores from widget config. Uses SERVICE ACCOUNT (admin op)."""
    
    url = f".../engines/{engine_id}/widgetConfigs/default_search_widget_config"
    resp = requests.get(url, headers={"Authorization": f"Bearer {admin_token}"})
    
    # Extract: collectionComponents → dataStoreComponents → name
    return [{"dataStore": ds["name"]} for ds in 
            resp.json()["collectionComponents"][0]["dataStoreComponents"]]
```

**Note:** Widget config fetch uses service account. The actual search uses user token for ACL enforcement.

---

## WIF Token Exchange

Converts Entra ID JWT to GCP access token:

```python
def exchange_wif_token(self, user_jwt: str) -> str:
    """Entra JWT → GCP Token via STS."""
    
    payload = {
        "audience": f"//iam.googleapis.com/.../workforcePools/{pool}/providers/{provider}",
        "grantType": "urn:ietf:params:oauth:grant-type:token-exchange",
        "subjectToken": user_jwt,
        "subjectTokenType": "urn:ietf:params:oauth:token-type:jwt",
        "scope": "https://www.googleapis.com/auth/cloud-platform"
    }
    
    resp = requests.post("https://sts.googleapis.com/v1/token", json=payload)
    return resp.json()["access_token"]
```

---

## Environment Variables

```bash
PROJECT_NUMBER=REDACTED_PROJECT_NUMBER
DISCOVERY_ENGINE_ID=deloitte-demo
WIF_POOL_ID=entra-id-oidc-pool-d
WIF_PROVIDER_ID=entra-id-oidc-pool-provider-de
```

---

## Common Issues

| Issue | Cause | Fix |
|-------|-------|-----|
| Generic LLM response (no citations) | Missing dataStoreSpecs | Add `toolsSpec.vertexAiSearchSpec.dataStoreSpecs` |
| `Unknown name "description"` | Invalid field in dataStoreSpecs | Remove description, use only `{"dataStore": "..."}` |
| Dynamic datastores = 0 | Using user token for widget config | Use service account for `_get_dynamic_datastores()` |
| No textGroundingMetadata | Parsing error | Handle SSE streaming chunks properly |

---

## Related Documentation

- [Architecture Overview](architecture.md) - System components and data flow
- [Security Flow](security-flow.md) - Token flow diagrams (WIF, STS)
- [LazyMcpToolset Pattern](lazy-mcp-pattern.md) - Pickle serialization fix
- [GCP Setup](gcp-setup.md) - WIF pool/provider configuration
- [Troubleshooting](troubleshooting.md) - Common issues and solutions
