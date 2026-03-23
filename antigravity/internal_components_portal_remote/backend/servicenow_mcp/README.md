# ServiceNow MCP: IT Services Documentation

The ServiceNow MCP service provides a complete, Zero-Leak compliant FastMCP-based integration for interacting with standard ServiceNow Cloud instances via the Table and Cart APIs. It is designed to carry out safely grounded ticketing queries and requests directly through the `ge_adk_portal_router` mesh.

---

## 🔐 Authentication Scopes

The `mcp_server_servicenow.py` script automatically manages intelligent protocol selection depending on what `.env` keys exist in the portal root directory:

1. **OIDC/JWT Bearer Flow (Prioritized for ADK Token Passing)**
If `USER_ID_TOKEN` exists, the Microsoft Entra ID claim passes directly to ServiceNow as a Bearer header. ServiceNow validates the JWT mapped `upn` or `email` SysID record natively.

2. **Basic Auth (Fallback Developer Access)**
If `SERVICENOW_BASIC_AUTH_USER` and `SERVICENOW_BASIC_AUTH_PASS` are provided, it falls back to basic `Authentication: Basic base64(user:pass)` encoding.

---

## 🌐 The SSE Bridge (`mcp_server_servicenow_sse.py`)
This file wraps the main tools definition layer into an **SSE server listener** for deployment on Cloud Run. It binds the container port to feed event streams directly back to Vertex AI Agent Engine operations:
```python
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    # Run using SSE transport bound to 0.0.0.0
    mcp.run(transport="sse", port=port, host="0.0.0.0")
```

---

## 🔧 Exposing Advanced API Capabilities

The following list of tools is fully callable by the Agent Engine over HTTP requests:

| Tool Name | Arguments | Description |
| :--- | :--- | :--- |
| `query_table` | `table_name: str, query: str` | Generic Table API wrapper search. |
| `create_ticket` | `table_name, payload_json` | Creates a record in any ServiceNow table (e.g., incident). |
| `update_ticket` | `table_name, sys_id, updates_json` | Updates ticket fields/state using raw stringified JSON. |
| `get_ticket` | `number: str` | Fetches single ticket exact match (e.g., INC0000601). |
| `delete_ticket` | `table_name, sys_id` | Deletes record from table (Fails if user lacks ACL permissions). |
| `add_comment` | `table_name, sys_id, text` | Appends customer visible `comment` or internal `work_note`. |
| `submit_catalog_item`| `catalog_item_sys_id, quantities, variables` | Submits a Service Catalog request via order_now Cart API. |
| `search_catalog_items`| `search_term: str` | Searches `sc_cat_item` (e.g., 'Laptop', 'Vpn') for Order SysID discovery. |

---

## 🚀 Replicating to Cloud Run

Each time you deploy the ServiceNow server to Cloud Run directly to ground your query:

1. Build/Deploy container targeting `mcp_server_servicenow_sse.py` script.
```bash
gcloud run deploy servicenow-mcp --source . --allow-unauthenticated
```
2. Setup continuous delivery endpoint target inside your `.env` bindings:
```bash
SERVICENOW_MCP_URL="https://servicenow-mcp-<hash>.us-central1.run.app/sse"
```
Once deployed, the model uses standard FastMCP structures to parse tools descriptions and append them recursively to the continuous text generation flow setup correctly!
