# SharePoint Federated Connector DataStore Search & AuthN / AuthZ Test Suite

This directory contains standalone testing scripts, architecture diagrams, and empirical proofs verifying that **Discovery Engine / Vertex AI Search Data Stores for Federated Connectors (SharePoint)** can be queried directly without requiring a Gemini Enterprise (GE) App or Engine.

## Key Highlights

1. **Direct DataStore Search is GA & Fully Supported**: Calling `dataStores/{DATASTORE_ID}/servingConfigs/default_search:search` retrieves indexed SharePoint content without an Engine layer.
2. **AuthN & AuthZ are GE-App Independent**: All authentication steps (Microsoft Entra ID login, Google STS/WIF token exchange, and SharePoint OAuth token storage via `dataConnector:acquireAndStoreRefreshToken`) operate entirely at the GCP IAM and Discovery Engine Collection levels.
3. **Comprehensive Visual Diagrams & Walkthrough**: Includes visual Mermaid sequence diagrams, trust boundary charts, and runnable Python/TypeScript snippets.

---

## File Directory

| File | Purpose |
| :--- | :--- |
| **[`ARCHITECTURE_AND_AUTH.md`](file:///Users/jesusarguelles/IdeaProjects/vertex-ai-samples/internal-testings/sharepoint-datastore-authn-authz/ARCHITECTURE_AND_AUTH.md)** | Visual Mermaid sequence diagrams, trust boundary flowcharts, end-to-end security walkthrough, and raw JSON proofs. |
| **[`test_datastore_search.py`](file:///Users/jesusarguelles/IdeaProjects/vertex-ai-samples/internal-testings/sharepoint-datastore-authn-authz/test_datastore_search.py)** | Standalone Python script to query SharePoint Data Stores directly via REST API. |
| **[`test_auth_flow.py`](file:///Users/jesusarguelles/IdeaProjects/vertex-ai-samples/internal-testings/sharepoint-datastore-authn-authz/test_auth_flow.py)** | WIF STS exchange and connector token validation test script. |
| **[`requirements.txt`](file:///Users/jesusarguelles/IdeaProjects/vertex-ai-samples/internal-testings/sharepoint-datastore-authn-authz/requirements.txt)** | Python dependencies (`requests`, `google-auth`). |

---

## Quick Start

```bash
cd ~/IdeaProjects/vertex-ai-samples/internal-testings/sharepoint-datastore-authn-authz

# Run direct DataStore search for "jennifer"
python3 test_datastore_search.py --entity=file --query="jennifer"

# Run search on SharePoint Pages
python3 test_datastore_search.py --entity=page --query="document"
```

For full architecture details, sequence diagrams, and security code snippets, refer to [`ARCHITECTURE_AND_AUTH.md`](file:///Users/jesusarguelles/IdeaProjects/vertex-ai-samples/internal-testings/sharepoint-datastore-authn-authz/ARCHITECTURE_AND_AUTH.md).
