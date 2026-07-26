# Getting Started — Production Agent Platform (`cloud-agent-platform`)

This guide walks you through deploying the Model Context Protocol (MCP) server to Cloud Run, packaging and deploying the ADK Reasoning Engine Agent to Vertex AI, and starting the streaming custom UI.

---

## 1. Prerequisites & GCP Setup

Ensure you have installed the Google Cloud SDK and authenticated:

```bash
gcloud auth login
gcloud auth configure-docker
gcloud config set project vtxdemos
```

---

## 2. Step 1: Deploy FastMCP Gateway to Cloud Run

The Cloud Run service serves as the secure tool executor boundary between Vertex AI and Microsoft Graph.

1. Navigate to the `mcp-server` subdirectory:
   ```bash
   cd cloud-agent-platform/mcp-server
   ```
2. Build and deploy the container source to Cloud Run:
   ```bash
   gcloud run deploy ms365-mcp-server \
     --source . \
     --region us-central1 \
     --allow-unauthenticated \
     --service-account=254356041555-compute@developer.gserviceaccount.com
   ```
3. Record the deployed service URL (e.g. `https://ms365-mcp-server-254356041555.us-central1.run.app`).

---

## 3. Step 2: Deploy ADK Agent to Vertex AI Reasoning Engine

The deployer packages your agent logic, links the Cloud Run MCP server URL, and uploads it to Vertex AI.

1. Navigate to the `adk-agent` subdirectory:
   ```bash
   cd ../adk-agent
   ```
2. Set up your `.env` variables or confirm the settings in `deploy.py`.
3. Execute the deployment script:
   ```bash
   python3 deploy.py
   ```
4. Verify the console output displays successful update:
   ```text
   Update complete: projects/254356041555/locations/us-central1/reasoningEngines/3073250998110650368
   Resource ID:   3073250998110650368
   ```

---

## 4. Step 3: Register Agent Identity Redirect URI

Because the Reasoning Engine agent acts on behalf of the user, Entra ID requires registering its redirect URI for OAuth:

1. Copy the Reasoning Engine Resource ID (e.g., `3073250998110650368`).
2. Construct the Redirect URI:
   `https://us-central1-aiplatform.googleapis.com/v1beta1/projects/254356041555/locations/us-central1/reasoningEngines/3073250998110650368:authenticate`
3. Add this URI to the Redirect URIs list of your Microsoft App Registration in Microsoft Entra Admin Center.

---

## 5. Step 4: Run the Production Frontend UI

Start the wrapper node server to host the custom React/HTML interface locally.

1. Navigate to the frontend backend directory:
   ```bash
   cd ../custom-ui-production/backend
   ```
2. Run the FastAPI dev server:
   ```bash
   python3 -m uvicorn main:app --host 0.0.0.0 --port 8001
   ```
3. Open `http://localhost:8001/` in your browser.
4. Interact with the chat UI. You should see streaming answers, with collapsible tools trace details showing exactly which MCP tools were triggered.

---

## 6. Troubleshooting & Enterprise Setup Pitfalls

Enterprise setups integrating Microsoft Entra ID and Google Cloud WIF are susceptible to token exchange and delegation failures. Use the following specifications to verify and troubleshoot your deployment:

### A. Microsoft Entra ID App Manifest Properties
If MSAL returns authorization code exchange errors or rejects token swaps, verify that both the **ID Token** and **Access Token** implicit flows are enabled in the App Manifest:

1. Open **Microsoft Entra ID admin center** > **App registrations** > select your Portal App.
2. Select **Manifest** on the sidebar.
3. Verify or edit the following JSON properties to match:
   ```json
   {
     "oauth2AllowIdTokenImplicitFlow": true,
     "oauth2AllowImplicitFlow": true
   }
   ```
4. Click **Save**.

---

### B. Google Cloud Workforce Identity Federation (WIF) Attribute Mappings
If WIF authentication returns `400 Bad Request` during federated credential swaps, ensure the pool provider maps the OpenID Connect (OIDC) assertions to Google IAM identifiers.

Configure using `gcloud` or verify in the GCP Console under **IAM & Admin** > **Workforce Identity Federation**:
```bash
gcloud iam workforce-pools providers update-oidc entra-provider \
  --workforce-pool="sp-wif-pool-v2" \
  --location="global" \
  --issuer-uri="https://login.microsoftonline.com/de46a3fd-0d68-4b25-8343-6eb5d71afce9/v2.0" \
  --client-id="api://b2d25471-834f-4ac9-9ba9-c05c06b42003" \
  --attribute-mapping="google.subject=assertion.sub,attribute.email=assertion.email,attribute.display_name=assertion.name"
```

---

### C. GCP IAM Permissions & Service Account Token Creation
The Reasoning Engine service account requires permission to invoke the Cloud Run FastMCP Gateway tool endpoint. Additionally, the Vertex platform service account must be trusted to act on behalf of the runtime account.

1. Ensure the **Reasoning Engine Service Account** (e.g. `agent-runner-sa`) has:
   - `roles/aiplatform.user`
   - `roles/logging.logWriter`
2. Grant the Vertex AI platform service agent token creator permissions on the runner service account:
   ```bash
   gcloud iam service-accounts add-iam-policy-binding \
     agent-runner-sa@vtxdemos.iam.gserviceaccount.com \
     --role="roles/iam.serviceAccountTokenCreator" \
     --member="serviceAccount:service-254356041555@gcp-sa-aiplatform.iam.gserviceaccount.com"
   ```

---

### D. Vertex AI Reasoning Engine Trace Logs
To verify that the agent is executing tool calls correctly, query the Vertex Reasoning Engine logs in Google Cloud Console **Log Explorer**:

1. Open the GCP Logs Explorer.
2. Run the following query filter to view execution traces:
   ```text
   resource.type="aiplatform.googleapis.com/ReasoningEngine"
   severity>=INFO
   ```
3. Expand the JSON payload to trace individual Model Context Protocol (MCP) dispatches (e.g., tracking `tool_search_emails` execution times and returned email arrays).

