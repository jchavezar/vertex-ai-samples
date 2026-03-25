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

The following list of tools is fully callable by the Agent Engine over HTTP requests. **Click a tool to view its source code implementation:**

```mermaid
graph TD
    classDef tool fill:#e8f5e9,stroke:#43a047,stroke-width:2px,color:#1b5e20;
    
    T1[🔍 query_table \n Generic Table API Search]:::tool
    T2[📋 list_incidents \n List Incident Tickets]:::tool
    T3[➕ create_ticket \n Insert Record into Table]:::tool
    
    click T1 "https://github.com/jchavezar/vertex-ai-samples/blob/main/antigravity/internal_components_portal_remote/backend/servicenow_mcp/mcp_server_servicenow.py#L70" "View Code"
    click T2 "https://github.com/jchavezar/vertex-ai-samples/blob/main/antigravity/internal_components_portal_remote/backend/servicenow_mcp/mcp_server_servicenow.py#L123" "View Code"
    click T3 "https://github.com/jchavezar/vertex-ai-samples/blob/main/antigravity/internal_components_portal_remote/backend/servicenow_mcp/mcp_server_servicenow.py#L166" "View Code"
```

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
