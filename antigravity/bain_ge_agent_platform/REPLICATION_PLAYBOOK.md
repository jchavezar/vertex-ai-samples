# Step-by-Step Replication Playbook // Bain & Company Financial Analysis Agent

This playbook provides concise, point-by-point instructions to replicate the entire Gemini Enterprise Agent Platform showcase from scratch, integrating Google ADK, Agent Runtime, Agent Gateway, Agent Identity, and the SharePoint MCP server.

---

## Prerequisites & Environment Setup

1. **Google Cloud Project**: Ensure you have an active GCP project (`vtxdemos`) with Vertex AI, Cloud Run, and Discovery Engine APIs enabled.
2. **Authenticated CLI**: Verify your Google Cloud CLI is authenticated with Owner permissions:
   ```bash
   gcloud auth login
   gcloud config set project vtxdemos
   ```
3. **Python Environment Tooling (`uv`)**: Ensure `uv` is installed for high-speed, isolated Python dependency management:
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```
4. **Microsoft 365 Tenant**: Ensure you have a SharePoint Online tenant with a site named `sockcop` and active financial due diligence documents (e.g., `01_Financial_Audit_Report_FY2024.pdf`, `03_Client_Contract_Apex_Financial.pdf`).

---

## Phase 1: Deploy the SharePoint MCP Server

1. **Navigate to the MCP Server Repository**:
   Locate the custom SharePoint MCP server in the `semiautonomous-agents` directory:
   ```bash
   cd /usr/local/google/home/jesusarguelles/vertex-ai-samples/semiautonomous-agents/ge_custom_mcp_sharepoint/1-custom-mcp
   ```
2. **Deploy to Google Cloud Run**:
   Deploy the MCP server as a private, unauthenticated-blocked service:
   ```bash
   gcloud run deploy ge-custom-sharepoint-mcp \
       --source . \
       --project=vtxdemos \
       --region=us-central1 \
       --no-allow-unauthenticated \
       --set-env-vars="TENANT_ID=de46a3fd-0d68-4b25-8343-6eb5d71afce9,CLIENT_ID=030b6aac-63d1-40e9-8d80-7ce928b839b8"
   ```
   *Note the resulting service URL (e.g., `https://ge-custom-sharepoint-mcp-rxhrarbbrq-uc.a.run.app`).*

---

## Phase 2: Configure Agent Gateway & Agent Identity

1. **Configure Agent Identity Authorization Binding**:
   Register the Entra ID OAuth 2.0 authorization binding (`sharepointauth_new`) using the Discovery Engine API:
   ```bash
   curl -X POST \
     -H "Authorization: Bearer $(gcloud auth print-access-token)" \
     -H "Content-Type: application/json" \
     -H "x-goog-user-project: vtxdemos" \
     "https://discoveryengine.googleapis.com/v1alpha/projects/254356041555/locations/global/authorizations?authorizationId=sharepointauth_new" \
     -d '{
       "name": "projects/254356041555/locations/global/authorizations/sharepointauth_new",
       "serverSideOauth2": {
         "clientId": "030b6aac-63d1-40e9-8d80-7ce928b839b8",
         "clientSecret": "YOUR_ENTRA_CLIENT_SECRET",
         "authorizationUri": "https://login.microsoftonline.com/de46a3fd-0d68-4b25-8343-6eb5d71afce9/oauth2/v2.0/authorize?client_id=030b6aac-63d1-40e9-8d80-7ce928b839b8&scope=openid%20profile%20email%20offline_access%20https%3A%2F%2Fgraph.microsoft.com%2FSites.ReadWrite.All%20https%3A%2F%2Fgraph.microsoft.com%2FFiles.ReadWrite.All&redirect_uri=https%3A%2F%2Fvertexaisearch.cloud.google.com%2Foauth-redirect&response_type=code&prompt=consent",
         "tokenUri": "https://login.microsoftonline.com/de46a3fd-0d68-4b25-8343-6eb5d71afce9/oauth2/v2.0/token"
       }
     }'
   ```
2. **Create Agent Gateway Governance Policy**:
   Create the Agent Gateway instance to wrap your upcoming Agent Engine deployment:
   ```bash
   gcloud beta ai agent-gateway create bain-governance-gateway \
       --project=vtxdemos \
       --location=us-central1 \
       --display-name="Bain & Company Governance Gateway" \
       --routing-target="projects/254356041555/locations/us-central1/reasoningEngines/SHAREPOINT_AGENT_ENGINE"
   ```
3. **Attach DLP Rules for Bain's "10 Non-Negotiables"**:
   Apply the DLP rules file to block Material Non-Public Information (MNPI):
   ```bash
   gcloud beta ai agent-gateway update bain-governance-gateway \
       --project=vtxdemos \
       --location=us-central1 \
       --dlp-rules-file=gateway_dlp_rules.json
   ```

---

## Phase 3: Build & Deploy the Google ADK Agent

1. **Navigate to the ADK Agent Directory**:
   ```bash
   cd /usr/local/google/home/jesusarguelles/vertex-ai-samples/antigravity/bain_ge_agent_platform/adk-agent
   ```
2. **Initialize Python Environment with `uv`**:
   Use `uv` to initialize and install dependencies:
   ```bash
   uv venv
   source .venv/bin/activate
   uv pip install -r requirements.txt
   ```
3. **Local Testing & Verification**:
   Before deploying to the cloud, you can test the agent locally using two methods:
   - **Terminal Streaming (`async_stream`)**: Verify initialization and stream responses directly in Python:
     ```bash
     uv run agent.py
     ```
   - **ADK Web UI (`adk web`)**: Launch the built-in local web harness to interact via browser:
     ```bash
     uv run adk web --agent agent:root_agent --port 8025
     ```
4. **Deploy the Agent to Vertex AI Agent Runtime**:
   Execute the deployment script using `uv run`. This automatically packages `agent.py`, wraps it in `AdkApp(enable_tracing=True)`, and deploys it to GKE / Agent Runtime:
   ```bash
   uv run deploy.py
   ```
   *Note the resulting `REASONING_ENGINE_ID` printed in the terminal console.*
5. **(Optional) Register in Gemini Enterprise**:
   *Note: If you are interacting exclusively through the Minimalist Custom UI, you do NOT need to execute this step.*
   ```bash
   # Only required if attaching to the Gemini Enterprise Chat UI
   export REASONING_ENGINE_ID="8655608971282874368"
   export CLIENT_SECRET="your_entra_client_secret_here"
   uv run register.py
   ```

---

## Phase 4: Deploy the Minimalist Custom UI (Direct Runtime Integration)

The Custom UI interacts directly with the deployed Reasoning Engine / Agent Gateway via the Vertex AI REST endpoint (`streamQuery?alt=sse`), bypassing Gemini Enterprise entirely.

1. **Navigate to the Custom UI Directory**:
   ```bash
   cd /usr/local/google/home/jesusarguelles/vertex-ai-samples/antigravity/bain_ge_agent_platform/custom-ui
   ```
2. **Install Node Dependencies**:
   Verify you have Node.js / npm installed, then install dependencies (using `--legacy-peer-deps` to automatically resolve React 19 peer dependency checks for `lucide-react`):
   ```bash
   npm install --legacy-peer-deps
   ```
3. **Verify and Clean Port Allocation**:
   Ensure port `5185` is fully unallocated before starting the local development server:
   ```bash
   kill -9 $(lsof -t -i:5185) 2>/dev/null || true
   ```
4. **Start the Vite Frontend Server**:
   ```bash
   npm run dev
   ```
5. **Access the Interface**:
   Open your browser to `http://localhost:5185`. Submit the query:
   > *"Retrieve the financial position and latest contracts for Meridian Technologies (from our sockcop SharePoint site) and formulate an investment position."*
   Verify that the response includes precise data tables and premium clickable citations (`[Title](webUrl)`).
