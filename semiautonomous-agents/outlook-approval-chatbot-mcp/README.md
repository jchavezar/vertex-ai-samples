# Outlook Approval Chatbot & Executive Dashboard (Option 2: Google ADK + Local MCP Outlook Tools)

> *A custom dashboard powered by the **Google ADK Agent Runtime** and direct Microsoft Graph local tool bindings acting as an Outlook MCP server, seamlessly integrated with the same premium WIF and React frontend.*

---

## Architecture Overview (Option 2)

This comparison sibling implements the identical split-pane workspace but replaces the backend core:
1. **Left Pane (Gemini Chat Console):** powered by a **Google ADK `Agent`** running locally on `gemini-2.5-flash`, bound with local Microsoft Graph tools (`fetch_outlook_emails`, `send_outlook_reply`, `send_new_outlook_email`) acting as the Outlook MCP server.
2. **Right Pane (Executive Action Items):** scans the user's recent Outlook emails by running the Google ADK Agent with a custom structuring prompt using the local email tool fetcher.
3. **No Frontend Code Changes:** Maintains absolute compatibility with the premium React frontend, enabling instant side-by-side comparison of Vertex AI StreamAssist (Option 1) vs. custom ADK orchestrators (Option 2).

```
+------------------------------------------------------------------------------------+
| EXECUTIVE ASSISTANT                                           [OUTLOOK CONNECTED]  |
+--------------------------------------------------+---------------------------------+
|                                                  | EXECUTIVE ACTION ITEMS          |
|  USER                                            | +-----------------------------+ |
|  Scan for tonight's deployment status            | | APPROVAL                    | |
|                                                  | | Go/no-go tonight's v2.3 deploy| |
|  GEMINI ENTERPRISE                               | | Aleksandra Kiszkiel         | |
|  I searched your emails...                       | | Review and provide decision.| |
|                                                  | | [APPROVE]  [REJECT]           | |
|                                                  | +-----------------------------+ |
|                                                  |                                 |
+--------------------------------------------------+---------------------------------+
```

---

## Quick Start

### 1. Configure Sibling Credentials
Create your `.env` files for both backend and frontend.

**Backend (`backend/.env`):**
```env
PROJECT_NUMBER=YOUR_GCP_PROJECT_NUMBER
ENGINE_ID=gemini-enterprise
CONNECTOR_ID=YOUR_OUTLOOK_CONNECTOR_ID
WIF_POOL_ID=YOUR_WORKFORCE_POOL_ID
WIF_PROVIDER_ID=YOUR_WORKFORCE_PROVIDER_ID
CONNECTOR_CLIENT_ID=YOUR_MS_CONNECTOR_APP_CLIENT_ID
TENANT_ID=YOUR_MS_TENANT_ID
REDIRECT_URI=https://vertexaisearch.cloud.google.com/oauth-redirect
```

**Frontend (`frontend/.env`):**
```env
VITE_CLIENT_ID=YOUR_MS_PORTAL_APP_CLIENT_ID
VITE_TENANT_ID=YOUR_MS_TENANT_ID
```

### 2. Run the App
Always use `uv` for backend python tasks.

```bash
# Terminal 1: Backend
cd backend
uv sync
uv run python main.py # Runs on port 8005

# Terminal 2: Frontend
cd frontend
npm install
npm run dev # Runs on port 5173 (proxies /api to 8005)
```

---

## Infrastructure Setup

This setup matches the architecture described in `outlook-streamassist-oauth-flow/README.md`.

### 1. Microsoft Entra ID — Portal App (MSAL login)
- **Redirect URI:** Single-page application → `http://localhost:5173`
- **Expose an API:** Add scope `user_impersonation` (Application ID URI: `api://{client-id}`).
- **Manifest:** Set `"oauth2AllowIdTokenImplicitFlow": true`.
- **API Permissions:** `openid`, `profile`, `email`, `offline_access`, `User.Read`.

### 2. Microsoft Entra ID — Connector App (Outlook OAuth)
- **Redirect URI (Web):** `https://vertexaisearch.cloud.google.com/oauth-redirect`
- **API Permissions:** `Calendars.Read`, `Mail.Read`, `User.Read`.
- **Secret:** Create a client secret and copy its value.

### 3. Google Cloud — Workforce Identity Federation
Configure WIF provider with issuer URI pointing to Entra and client ID set to `api://PORTAL_APP_CLIENT_ID`. Ensure workforce members have `roles/discoveryengine.editor` in your GCP project.

### 4. Gemini Enterprise App
Create a Search App named `gemini-enterprise` in location `global` with Microsoft Outlook as a federated data store using your Connector App's client ID and secret.

---

## Approvals & Direct Actions Flow

1. When **Scan Inbox** is clicked, the backend calls Gemini Enterprise StreamAssist using the scanning prompt.
2. The model returns a structured JSON payload representing the items requiring attention.
3. The frontend renders these items as technical grid cards.
4. When **Approve** or **Reject** is clicked:
    - The backend requests a delegated Microsoft Graph access token using GCP's `dataConnector:acquireAccessToken` API.
    - The backend calls Microsoft Graph's `/me/messages/{id}/reply` endpoint to send a reply ("Approved." or "Rejected.") to the email thread.
    - The card transitions to a success/actioned state.

### Real-time Scanning & Execution Timing
To provide maximum operational visibility, the scanning interface features a high-precision, real-time stopwatch displaying search elapsed duration with 100ms precision:

![Real-time Inbox Scan Timer](images/scanning_timer_live.png)

---

## Interactive Chat Drafting & Send Approval Flow

In addition to processing existing inbox action items, the **Gemini Chat Console** supports composing and sending newly drafted outbound emails using the same secure validation pipeline:

1. **Request a Draft**: The user asks Gemini to compose a new message (e.g., *"Draft an email to jesusarguelles@google.com saying..."*).
2. **AI Composition**: Gemini Enterprise queries your mailbox context, generates the appropriate draft body, and renders it inside the chat console.
3. **Dynamic Interactive Card**: The frontend automatically parses the draft parameters (To, Subject, and Body) from Gemini's response and renders a beautiful, high-contrast, slate-themed **DRAFTED EMAIL ACTION REQUIRED** card directly under the message block:
   
   ![Interactive Draft Approval Card](images/custom_ui_readable_draft.png)
   
4. **One-Click Dispatch**: When the user clicks **APPROVE & SEND EMAIL**, the client issues a POST request to `/api/send-email`. The backend secures a delegated Microsoft Graph Access token and dispatches the email via `/v1.0/me/sendMail`.
5. **Visual Confirmation**: Upon successful delivery, the card updates dynamically to show a green success state (`✓ EMAIL SENT`):

   ![Successful Email Delivery State](images/custom_ui_dispatch_success_final.png)

This ensures high-privilege operations remain secure, intuitive, and under direct user control with full visual alignment.
