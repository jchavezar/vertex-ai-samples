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
3. Name it (e.g., `pwc-sharepoint-proxy`).
4. Under **Redirect URI**, select **Single-page application (SPA)** and enter `http://localhost:5173/` (or `http://localhost:3000/` depending on your frontend port). This is required for the frontend sign-in.
5. Note your **Application (client) ID** and **Directory (tenant) ID**.
6. Go to **Certificates & secrets** and create a **New client secret**. Save the `Value` immediately (for the backend daemon).

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

> **Note:** Enure your environment variables are set correctly. You can find your `SITE_ID` and `DRIVE_ID` via the Microsoft Graph Explorer if needed.

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

You can run the application in its integrated mode (FastAPI + Agent) or use the standalone MCP server.

### Integrated Mode (FastAPI + ADK Runner)
This starts the backend on port `8001`.
```bash
cd backend
uv run python main.py
```

### Start the Frontend (Vite + React)
We configure this to run on `3000` to avoid conflicts.
```bash
cd frontend
npm run dev
```

---

## 5. Standalone MCP Server & Cloud Run Deployment

This project now includes a **standalone MCP Server** using `FastMCP` (in `backend/mcp_server.py`). This allows other agents or applications to consume your SharePoint logic directly via the Model Context Protocol.

### Running the MCP Server Locally (Inspector Mode)
You can run the server in `stdio` mode to use it with the [MCP Inspector](https://github.com/modelcontextprotocol/inspector):
```bash
cd backend
uv run python mcp_server.py
```

### Deploying to Google Cloud Run
1. **Build the container**:
   ```bash
   gcloud builds submit --tag gcr.io/[PROJECT_ID]/sharepoint-mcp-server ./backend
   ```
2. **Deploy as an SSE Server**:
   ```bash
   gcloud run deploy sharepoint-mcp-server \
     --image gcr.io/[PROJECT_ID]/sharepoint-mcp-server \
     --set-env-vars="TENANT_ID=...,CLIENT_ID=...,..." \
     --allow-unauthenticated
   ```
   *The server dynamically switches to SSE transport when the `PORT` environment variable is detected.*

---

The application will be available at `http://localhost:3000`. 

---

## 7. How It Works: The Zero-Parsing Flow
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
