# Light MCP Portal - ServiceNow & Entra ID

Modern, zero-trust AI portal connecting Microsoft Entra ID identities to ServiceNow via the Google Agent Development Kit (ADK) and FastMCP.

## 🚀 Key Features
- **Zero-Trust Auth**: No hardcoded credentials. User JWT tokens are passed from the browser to the MCP server.
- **Dynamic Intent Routing**: Intelligent routing of ServiceNow queries to a dedicated ADK agent.
- **OIDC Native Mapping**: Direct identity synchronization between Entra ID and ServiceNow.
- **Resilient Fallback**: Automatic failover to Basic Auth in development environments.

## 📁 Project Structure
- `backend/`: FastAPI application and ADK agent orchestration.
  - `servicenow_mcp/`: The core FastMCP server implementation.
- `frontend/`: React + MSAL frontend for Entra ID authentication.
- `docs/`: Critical security and configuration architecture.

## 🛡️ Setup & Security
For detailed instructions on mapping Entra ID to ServiceNow and troubleshooting `401 Unauthorized` errors, refer to the master security guide:

👉 **[AUTHENTICATION_SECURITY.md](./docs/AUTHENTICATION_SECURITY.md)**

## 🛠️ Development
```bash
# Install dependencies
uv sync

# Run the project
uv run main.py
```
