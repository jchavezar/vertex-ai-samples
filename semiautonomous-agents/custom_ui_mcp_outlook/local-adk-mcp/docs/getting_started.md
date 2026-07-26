# Getting Started — Local ADK Assistant (`local-adk-mcp`)

This guide walks you through registering the Entra application, configuring your local environment, and starting the local FastAPI server and evaluation console.

---

## 1. Prerequisites & Dependencies

First, ensure you have Python 3.10+ installed. Install the package dependencies using virtual environments:

```bash
cd local-adk-mcp
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## 2. Microsoft Entra ID Application Registration

To query your Outlook mailbox via Graph API, register an application in the [Microsoft Entra admin center](https://entra.microsoft.com/):

1. Navigate to **App registrations** > **New registration**.
2. **Name**: `Outlook Executive Assistant (Local Dev)`.
3. **Supported account types**: Accounts in any organizational directory (Any Microsoft Entra ID tenant - Multitenant).
4. **Redirect URI (Web)**: Configure redirect to `http://localhost:8001/api/oauth/callback`.
5. **Certificates & Secrets**: Generate a new Client Secret and record the value.
6. **API Permissions**: Add the following **Delegated** permissions and grant admin consent:
   - `User.Read`
   - `Mail.Read`
   - `Mail.Send`
   - `Calendars.Read`
   - `Calendars.ReadWrite`

---

## 3. Configuration Setup (`.env`)

Create a `.env` file in the root folder of the project (`/custom_ui_mcp_outlook/.env`) with your credentials:

```env
# Entra App Registration Credentials
CLIENT_ID=<your_azure_entra_client_id>
CLIENT_SECRET=<your_azure_entra_client_secret>
TENANT_ID=<your_azure_entra_tenant_id>

# GCP project for Gemini API
GOOGLE_CLOUD_PROJECT=<your_gcp_project_id>

# Microsoft Graph OAuth refresh token (exchanged upon initial login)
MS_GRAPH_REFRESH_TOKEN=<your_ms_graph_oauth_refresh_token>
```

---

## 4. Starting the Server

To launch the FastAPI server, start uvicorn inside the `local-adk-mcp` folder with the `PYTHONPATH` set to the folder root:

```bash
cd local-adk-mcp
PYTHONPATH=. .venv/bin/python3 backend/main.py
```

Expected Startup Logs:
```text
INFO:     Started server process [90443]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8005 (Press CTRL+C to quit)
```

---

## 5. Verifying & Troubleshooting

* **Chat Interface**: Open `http://localhost:8005/` in your browser. Type a search query, like `"what is my latest unread message?"`.
* **Visual Evaluation**: Open `http://localhost:8005/eval` to inspect the 100-case comparative visual report.
* **Inspect Redundant Auth Requests**: If latency is high, check `backend.log`. You should see `OutlookClient cache cleared` but token refresh statements should **not** log consecutively during search queries, confirming in-memory token reuse is functioning.
