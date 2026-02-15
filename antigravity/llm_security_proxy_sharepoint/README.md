# PWC LLM Security Proxy: SharePoint Integration

This project is a secure, generalized consulting intelligence proxy. It acts as a middleman between confidential SharePoint documents and a chat interface, allowing users to query intelligence without ever exposing sensitive client data, PII, or raw financial specifics.

This project implements the **Zero-Parsing Architecture** using FastAPI, Google ADK (Agent Development Kit), and the React 19 Vercel AI SDK. It also provides a beautiful, modern **Topology UI** to inspect the end-to-end trace.

## 🔐 Zero-Leak Protocol

This repository adheres to strict Zero-Leak protocols.
- **NEVER** commit `.env` files.
- **NEVER** hardcode credentials (e.g., `client_id`, `client_secret`, `tenant_id`).
- Secrets are managed entirely in your local environment.
- The `.gitignore` includes mandatory exclusion rules for all standard credential files.

---

## 🏗️ Architecture Topology

The application enforces a secure offloading architecture using the Model Context Protocol (MCP).

```mermaid
flowchart LR
    %% Styling Definitions
    classDef default fill:#fff,stroke:#333,stroke-width:1px,color:#333;
    classDef frontend fill:#eef2ff,stroke:#6366f1,stroke-width:2px,color:#4338ca,rx:10,ry:10;
    classDef backend fill:#faf5ff,stroke:#a855f7,stroke-width:2px,color:#6b21a8,rx:10,ry:10;
    classDef gemini fill:#fdf4ff,stroke:#d946ef,stroke-width:3px,color:#86198f,rx:15,ry:15;
    classDef mcp fill:#e0e7ff,stroke:#4f46e5,stroke-width:2px,color:#312e81,rx:10,ry:10;
    classDef data fill:#ecfdf5,stroke:#10b981,stroke-width:2px,color:#065f46,rx:10,ry:10;

    subgraph Frontend ["End User / React SPA"]
        A[useTerminalChat Hook]:::frontend
    end

    subgraph Backend ["Security Proxy (FastAPI)"]
        B[Google ADK Runner]:::backend
        C[gemini-3-pro-preview]:::gemini
        B <--> C
    end

    subgraph MCP ["MCP Server"]
        D[Python MCP SDK]:::mcp
        D_Tool["search_documents()"]:::mcp
        D --- D_Tool
    end

    subgraph Data ["Microsoft Cloud"]
        E[Graph API / Entra ID]:::data
        F[(SharePoint Indices)]:::data
        E --> F
    end

    A -- SSE / HTTP --> B
    B -- MCP TOOL CALL --> D
    D -- REST --> E

    %% Link Styling
    linkStyle default stroke:#64748b,stroke-width:1px,fill:none;

    %% Subgraph Styling
    style Frontend fill:#f8fafc,stroke:#94a3b8,stroke-width:1px,stroke-dasharray: 5 5
    style Backend fill:#fcfaff,stroke:#c084fc,stroke-width:1px,stroke-dasharray: 5 5
    style MCP fill:#eff6ff,stroke:#60a5fa,stroke-width:1px,stroke-dasharray: 5 5
    style Data fill:#f0fdf4,stroke:#86efac,stroke-width:1px,stroke-dasharray: 5 5
```

### Flow Breakdown:
1. **End User (React SPA):** The user types a query in the beautifully designed "Modern Cave" chat interface.
2. **Security Proxy:** The Vercel AI SDK streams the request to a FastAPI backend running a Google ADK `LlmAgent`.
3. **LLM Evaluation:** `gemini-3-pro-preview` evaluates the query and delegates extraction to the MCP Server if external knowledge is required.
4. **MCP Server:** Executes the `search_documents()` tool via the standard Model Context Protocol.
5. **Microsoft Graph:** Authenticates using OAuth 2.0 Client Credentials and accesses protected SharePoint directories.
6. **Zero-Parsing Delivery:** The Proxy returns sanitized markdown (`0:`) and structured data cards (`2:`) back to the frontend dynamically.

---

## 🚀 Environment Setup

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

Ensure your Entra ID application has `Sites.Read.All` and `Files.Read.All` with **Admin Consent Granted**.

---

## 📦 Installation & Execution

We strictly use `uv` for Python dependency management.

### Backend Start
```bash
cd backend
uv sync
uv run python main.py
```
*(Runs on port 8001)*

### Frontend Start
```bash
cd frontend
npm install
npm run dev
```
*(Runs on port 5173)*

### Standalone MCP Server
You can run the SharePoint connector natively as a standalone server for the MCP Inspector:
```bash
cd backend
uv run python mcp_server.py
```

### Serverless Cloud Run Deployment
You can deploy the FastMCP server securely on Google Cloud Run to provide streaming endpoints across any interface:
```bash
cd backend
gcloud run deploy mcp-sharepoint-server \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --env-vars-file=../.env
```
Once deployed, simply copy the URL and update your `McpInspector.tsx` state variable to consume your new edge-running MCP connection.

---

## 🎨 UI/UX Highlights
- **Topology View:** A built-in architecture viewer inside the application (`Topology` toggle in the header).
- **Responsive PWC Chat Sidebar:** Dark glassmorphism, contextual cards, and a sophisticated prompt input overlay.
- **Enterprise Grade Look:** Authentic layout based on corporate guidelines, ensuring robust navigation and aesthetic spacing.
