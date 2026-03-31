# Discovery Engine SharePoint Test

Interactive tool to test the full authentication flow:

```
Entra ID (Microsoft) -> WIF/STS -> Discovery Engine streamAssist
```

## Quick Start

```bash
cd ~/vertex-ai-samples/semiautonomous-agents/discovery_engine_test
python3 serve.py
```

Then open http://localhost:5000 in your browser.

## Flow

1. **Login with Microsoft** - Gets Entra ID JWT (id_token)
2. **Exchange Token** - Calls STS to exchange JWT for GCP access token via WIF
3. **Query SharePoint** - Calls Discovery Engine streamAssist with:
   - User's GCP token (carries SharePoint ACL permissions)
   - `dataStoreSpecs` pointing to SharePoint datastores
4. **See Results** - Response includes grounding metadata with SharePoint sources

## Configuration

The following are configured for `deloitte-plantas`:

| Setting | Value |
|---------|-------|
| Entra Client ID | `ecbfa47e-a75c-403c-a13b-f27eff101e4e` |
| Entra Tenant ID | `de46a3fd-0d68-4b25-8343-6eb5d71afce9` |
| WIF Pool | `entra-id-oidc-pool-d` |
| WIF Provider | `entra-id-oidc-pool-provider-de` |
| GCP Project | `440133963879` (deloitte-plantas) |
| Engine ID | `deloitte-demo` |

## Key API Endpoint

**Official Docs:** [streamAssist API Reference](https://cloud.google.com/generative-ai-app-builder/docs/reference/rest/v1alpha/projects.locations.collections.engines.assistants/streamAssist)

```
POST https://discoveryengine.googleapis.com/v1alpha/projects/{PROJECT_NUMBER}/locations/global/collections/default_collection/engines/{ENGINE_ID}/assistants/default_assistant:streamAssist
```

## CRITICAL: dataStoreSpecs for Grounded Responses

**Without `dataStoreSpecs`, streamAssist returns generic LLM responses (not grounded on SharePoint).**

| Payload | Result |
|---------|--------|
| `{"query": {"text": "..."}}` | Generic LLM answer, no citations |
| `{"query": {...}, "toolsSpec": {"vertexAiSearchSpec": {"dataStoreSpecs": [...]}}}` | Grounded answer with SharePoint sources |

### Correct Payload Structure

```json
{
  "query": {"text": "what's the salary of a cfo?"},
  "toolsSpec": {
    "vertexAiSearchSpec": {
      "dataStoreSpecs": [
        {"dataStore": "projects/.../dataStores/deloitte-sharepoint_file"},
        {"dataStore": "projects/.../dataStores/deloitte-sharepoint_page"}
      ]
    }
  }
}
```

### Common Mistake

```json
// WRONG - dataStoreSpecs at root level (will be ignored!)
{
  "query": {"text": "..."},
  "dataStoreSpecs": [...]
}

// CORRECT - nested in toolsSpec.vertexAiSearchSpec
{
  "query": {"text": "..."},
  "toolsSpec": {
    "vertexAiSearchSpec": {
      "dataStoreSpecs": [...]
    }
  }
}
```

### How to Verify Grounding

Check for `textGroundingMetadata` in the response:
- **Present with references** = Grounded on SharePoint
- **Missing or empty** = Generic LLM response (check dataStoreSpecs)

## Why User Token Matters

SharePoint data in Discovery Engine is **ACL-controlled**. The user's identity (via WIF exchange) determines what documents they can access. Using a service account won't see the SharePoint documents.
