# ServiceNow FastMCP Integration

This module provides a complete, Zero-Leak compliant FastMCP-based backend integration for interacting with standard ServiceNow instances via the Table API. It is specifically designed to fit within the `internal_components_portal` ecosystem.

## 🔐 Authentication Scopes

The `mcp_server_servicenow.py` script automatically manages intelligent protocol selection depending on what `.env` keys exist in the portal root directory:

### 1. OAuth 2.0 Password Grant (Prioritized)
If `SERVICENOW_CLIENT_ID`, `SERVICENOW_CLIENT_SECRET`, `SERVICENOW_USERNAME`, and `SERVICENOW_PASSWORD` are all provided, it issues a `POST oauth_token.do` to fetch a revocable `access_token` Bearer header dynamically.

### 2. Basic Auth (Fallback)
If OAuth registry secrets aren't provided, it falls back to basic `Authentication: Basic base64(user:pass)` encoding.

## 🧰 Available MCP Tools

These tools run under the `ServiceNow-MCP` environment and can be invoked dynamically by `google.adk` logic via the FastMCP bridge. 

### `query_table(table_name: str, query: str, limit: int, offset: int)`
The generic base query wrapper designed to handle deep Table searches.
- **Example Usage**: `query_table('incident', query='priority=1^state=1', limit=5)`

### `create_ticket(table_name: str, payload_json: str)`
Generic record creation endpoint taking stringified property blocks.

### `update_ticket(table_name: str, sys_id: str, updates_json: str)`
Updates any record field given a known `sys_id`.

### Targeted Conveniences:
To reduce agent hallucinations, specific table handlers wrap the generic queries:
- `list_incidents(limit, offset, state)`
- `list_problems(limit, offset, state)`
- `list_changes(limit, offset, state)`
- `list_catalog_tasks(limit, offset, state)`

## ✨ Implementation Details (Zero-Leak architecture)
- Dependencies use strictly `requests` parsing JSON payloads directly rather than heavy ServiceNow SDKs, which keeps latency low and removes arbitrary dependency vulnerabilities.
- Response payloads select generic default fields (number, sys_id, state) minimizing token loads returning to LLM prompts, ensuring maximum reasoning speed.
