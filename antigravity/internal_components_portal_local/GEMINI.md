# Internal Components Portal (Local Instance)

This is an isolated, local development version of the Internal Components Portal. It is designed to run independently from the production/shared instance to avoid port conflicts and session data interference.

## Port Assignment

To prevent conflicts with other services in the Antigravity suite, the following ports are strictly reserved for this local portal:

| Component | Port | URI |
| :--- | :--- | :--- |
| **Frontend** | `5181` | `http://localhost:5181` |
| **Backend** | `8011` | `http://localhost:8011` |

## Authentication Setup

This application uses Microsoft Entra ID (Azure AD) and ServiceNow (OIDC) for authentication.

### Required Redirect URIs
The following URI must be added to the authorized redirect lists in the respective identity provider consoles:
- `http://localhost:5181`

### Configuration Specifics
- **Microsoft Entra**: App Registration ID `33ebbc81-e8e8-47b6-b6a7-35df56b9a9f0` (Name: `ge`).
- **ServiceNow**: Application Registry record `Internal Components Portal MCP`.

## Usage
Start the backend first:
```bash
./start_backend.sh
```
Then start the frontend:
```bash
cd frontend && npm run dev:ui
```
Access the portal at `http://localhost:5181`.
