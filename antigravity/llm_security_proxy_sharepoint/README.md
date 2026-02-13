# PWC LLM Security Proxy: SharePoint Integration

This project is a secure, generalized consulting intelligence proxy. It acts as a middleman between confidential SharePoint documents and a chat interface, allowing users to query intelligence without ever exposing sensitive client data, PII, or raw financial specifics.

This project implements the **Zero-Parsing Architecture** using FastAPI, Google ADK (Agent Development Kit), and the React 19 Vercel AI SDK.

## Architecture & Features
- **Frontend (React 19 + Vercel AI SDK):** Built with "Modern Cave" aesthetics. It uses a Zero-Parsing UI where the backend streams both markdown chat tokens (`0:` protocol) and structured UI components (`2:` Data Protocol) directly to the user interface.
- **Backend (FastAPI + Google ADK):** Hosts an `LlmAgent` using `gemini-3-pro-preview`. The agent enforces strict data masking guidelines and processes incoming streams.
- **MCP Server (Microsoft Graph API):** A specialized set of tools that allows the LLM to search and download PDF documents directly from a corporate SharePoint tenant using daemon-style Application credentials.

---

## 1. Prerequisites & Azure AD Configuration

Before running any code, you must configure Microsoft Entra ID (Azure AD) to allow the backend daemon to read SharePoint files automatically.

### Creating the App Registration
1. Go to the **Azure Portal** -> **Microsoft Entra ID**.
2. Click **App registrations** -> **New registration**.
3. Name it (e.g., `pwc-sharepoint-proxy`) and leave the Redirect URIs empty (we are using the Client Credentials flow).
4. Note your **Application (client) ID** and **Directory (tenant) ID**.
5. Go to **Certificates & secrets** and create a **New client secret**. Save the `Value` immediately.

### Setting API Permissions
This step is critical; without it, you will receive `403 Forbidden` errors.
1. In your App Registration, go to **API permissions**.
2. Click **Add a permission** -> **Microsoft Graph**.
3. Select **Application permissions** (NOT Delegated).
4. Search for and check: `Sites.Read.All` and `Files.Read.All`.
5. Click **Add permissions**.
6. **CRITICAL:** Click the **Grant admin consent for [Your Tenant]** button at the top of the list and confirm. The status dots must turn into green checkmarks.

---

## 2. Environment Setup

At the root of the project (`llm_security_proxy_sharepoint/`), create a `.env` file containing your Azure credentials and SharePoint targets:

```env
# Microsoft Graph API Credentials
TENANT_ID=your_tenant_id
CLIENT_ID=your_client_id
CLIENT_SECRET=your_client_secret

# SharePoint Targets
SITE_ID=your_site_id
DRIVE_ID=your_drive_id

# Google Cloud (For LLM and ADK)
GOOGLE_CLOUD_PROJECT=your_gcp_project
```

> **Note:** Run the scripts inside `backend/manual_to_sharepoint_api.md` (specifically `get_site_for_drive.py` or `find_financial_drives.py`) if you need help finding your exact `SITE_ID` and `DRIVE_ID` strings.

---

## 3. Project Installation

We strictly use `uv` for Python dependency management.

### Backend Setup
```bash
cd backend
# Install dependencies
uv sync
```

### Frontend Setup
Ensure you have `npm` or `yarn` installed.

```bash
cd frontend
npm install
```

---

## 4. Running the Application

You must run both the backend API server and the frontend dev server simultaneously.

### Start the Backend (FastAPI + ADK Runner)
This starts the backend on port `8001`.
```bash
cd backend
uv run python main.py
```

### Start the Frontend (Vite + React)
We configure this to run on port `3000` to avoid conflicts.
```bash
cd frontend
npm run dev
```

The application will be available at `http://localhost:3000`. 

---

## How It Works: The Zero-Parsing Flow
1. User types a query into the React `<Chat />` interface.
2. The Vercel AI SDK sends a single `/chat` HTTP POST to the FastAPI backend.
3. FastAPI instantiates the `LlmAgent` through the ADK `Runner`.
4. The Gemini 3 Pro model evaluates the query, realizes it needs SharePoint data, and executes the `search_documents` and `get_document_content` MCP tools.
5. `mcp_sharepoint.py` acquires an MSAL token and downloads the raw PDF bytes, using `markitdown` to convert it into raw text.
6. The LLM reads the raw text, applies its masking instructions (hiding names/PII), and generates a response.
7. `main.py` catches this response and streams it back to the frontend:
   - It yields conversational text as `0: "markdown text"`.
   - It yields structured Project Cards as `2: [{"type": "project_card", "data": {...}}]`.
8. The React frontend's `useTerminalChat` hook automatically parses these streams and updates the Zustand store, rendering the beautiful UI components dynamically without any manual JSON parsing logic.
