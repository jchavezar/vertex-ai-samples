# Sockcop Search | Native Vertex AI Answer Integration & SharePoint Grounding

Sockcop Search is a highly secure, modern GenAI unified search interface built with React, Vite, and Tailwind CSS. It leverages the **Google Vertex AI Answer API** to natively query and summarize your company's documents, utilizing **Workload Identity Federation (WIF)** to exchange Entra ID (Azure AD) user tokens for Google Cloud credentials on the fly, seamlessly grounding the LLM responses.

![Vertex AI Native Answer Result](./public/screenshots/search_results_success.png)

## Core Architecture: Workload Identity Federation Flow

The following diagram illustrates the zero-trust authentication flow across Microsoft Entra ID and Google Cloud via WIF.

```mermaid
sequenceDiagram
    box rgba(15, 23, 42, 0.4) Identity & Access Management
        participant User as End User
        participant Frontend as Sockcop Search UI
        participant EntraID as Microsoft Entra ID
        participant WIF as Google WIF Boundary 🛡️
    end
    box rgba(12, 74, 110, 0.3) Google Cloud Platform
        participant VertexAI as Vertex AI Answer API
    end
    
    User->>Frontend: Clicks "Sign in with Entra ID"
    Frontend->>EntraID: Redirects for OAuth Consent
    EntraID-->>Frontend: OAuth JWT `id_token`
    
    note over Frontend,WIF: Workload Identity Federation Exchange
    Frontend->>WIF: POST /v1/token (audience, subject_token)
    WIF-->>Frontend: Short-lived Google `access_token`
    Frontend->>Frontend: Stores Google Token locally (In-Memory)
```

## Advanced Architecture: Native Answer API Integration

Sockcop Search relies entirely on the powerful `default_config:answer` endpoint provided by Vertex AI Search. This modern endpoint natively handles the complex Retrieval-Augmented Generation (RAG) pipeline on the backend, ensuring accurate, grounded summarizations without the need for manual, client-side extraction or secondary LLM fallbacks.

```mermaid
flowchart TD
    classDef ui fill:#0f172a,stroke:#38bdf8,stroke-width:2px,color:#fff;
    classDef api border-style:dashed,fill:#1e293b,stroke:#0f172a,color:#e2e8f0;
    classDef extract fill:#082f49,stroke:#0c4a6e,color:#bae6fd;
    classDef rank text-align:center,fill:#f59e0b,stroke:#b45309,color:#fff;

    User(["👤 User Query"]) --> UI("Sockcop React UI")
    UI -- "POST /servingConfigs/default_config:answer\nAuthorization: Bearer <GCP_TOKEN>" --> VAIS{{"Vertex AI Answer API"}}:::api
    
    VAIS -- "Retrieves Documents\nSynthesizes Grounded Answer" --> Extraction["Frontend Deep Extraction\n(Answer Payload & structData)"]:::extract
    
    Extraction --> Score("Extracts Confidence Score (rank)"):::rank
    Extraction --> Link("Extracts SharePoint Source (url_for_connector)"):::rank
    Extraction --> Author("Extracts Document Metadata (author, title)"):::rank
    
    Score --> Render("Displays Generative AI Summary & Detailed Citations"):::ui
    Link --> Render
    Author --> Render
```

## UI Showcase: Native Grounding in Action

### Interactive Citation Panel
Explore grounded sources with deep metadata extraction directly from your connected datastores.
![Detailed Citation View](./public/screenshots/citation_detail.png)

### Native Answer Generation
Vertex AI's `default_config:answer` synthesizing search results and providing fallback-free AI summarizations.
![Search Results Overview](./public/screenshots/search_results.png)

### Original Document Linking
Deeply link directly to the source datastore (e.g. Microsoft SharePoint) to read the full context.
![SharePoint Source View](./public/screenshots/sharepoint_source.png)

## Key Features

* **Zero-Leak Stateless Architecture:** No middle-tier secrets or API keys are stored in the frontend source code. The user authenticates natively and generates a temporary session with WIF.
* **Native Generation Pipeline:** Replaces legacy, constrained search endpoints with the comprehensive Vertex AI Answer API. Summarization, document retrieval, and grounding citations are generated server-side in one swift request.
* **Intelligent Metadata Mapping:** The UI securely dives into the payload's `structData` schema to render a beautifully formatted citation list. This includes visual indicators for the API's internal Confidence Score (`rank`), origin author, and precise deep links mapped back to the connected SharePoint site.
* **XSS Protection:** DOMPurify is embedded to securely process highlight `<b>` tags delivered from the Vertex APIs without exposing the frontend to HTML injections.

## Development Setup

1. **Verify Dependencies**
Make sure you use **npm**, **pnpm** or **yarn** to install local frontend packages.
```bash
npm install
```

2. **Environment & Configuration**
For security, do not embed secrets! All configuration identifiers are inside `src/api/config.js`. Ensure your `.gitignore` is completely strict (we have appended the zero-leak rules automatically) protecting your `.env` tokens. 

```javascript
// Example src/api/config.js
export const CONFIG = {
  PROJECT_NUMBER: 'YOUR_PROJECT_NUMBER',
  LOCATION: 'global',
  WIF_POOL: '...',
  WIF_PROVIDER: '...',
  DATA_STORE_ID: '...',
  ENGINE_ID: 'deloitte-demo',
  TENANT_ID: '...',
  MS_APP_ID: '...',
  ISSUER: 'https://login.microsoftonline.com/...'
};
```

3. **Running the App**
Use the standard dev server:
```bash
npm run dev
```


## 🚀 Configuration Guide: Google Cloud WIF & Azure AD (Entra ID)

To securely integrate your application as a federated search connector using Gemini Enterprise capabilities, you must configure both GCP's Workforce Identity Federation (WIF) and Azure AD. **Crucially, no credentials must be leaked or stored in your frontend.**

### Step 1: Configure Google Cloud WIF (Workforce Identity Federation)
We set up the WIF configuration first to establish the OpenID Connect (OIDC) trust with Entra ID and obtain the explicit Redirect URL needed for Azure AD.

*Run the following commands using the `gcloud` CLI. Ensure you replace the placeholder values (`<TENANT_ID>`, `<CLIENT_ID>`, `<CLIENT_SECRET>`) with the corresponding ones from your Azure Entra ID Application.*

**1A. Create the OIDC Provider in your Workforce Pool:**
```bash
gcloud iam workforce-pools providers create-oidc entra-id-oidc-pool-provider-de \
    --workforce-pool="entra-id-oidc-pool-d" \
    --location="global" \
    --display-name="Entra ID Provider" \
    --description="OIDC provider for Entra ID" \
    --issuer-uri="https://login.microsoftonline.com/<TENANT_ID>/v2.0" \
    --client-id="<CLIENT_ID>" \
    --client-secret-value="<CLIENT_SECRET>" \
    --web-sso-response-type="code" \
    --web-sso-assertion-claims-behavior="merge-user-info-over-id-token-claims" \
    --attribute-mapping="google.subject=assertion.sub,google.groups=assertion.groups,google.display_name=assertion.preferred_username" \
    --attribute-condition='assertion.issuer.startsWith("https://login.microsoftonline.com/<TENANT_ID>")' \
    --detailed-audit-logging
```

**1B. Bind IAM Permissions for the Identity Pool**
Grant the necessary permissions to the federated identities so they can natively query the Vertex AI Answer API:
```bash
# Replace <YOUR_PROJECT_ID> with your actual GCP project ID
gcloud projects add-iam-policy-binding <YOUR_PROJECT_ID> \
    --member="principalSet://iam.googleapis.com/locations/global/workforcePools/entra-id-oidc-pool-d/*" \
    --role="roles/discoveryengine.viewer"
```

**1C. Obtain the WIF Redirect URL**
Your specific redirect URL for the Entra ID configuration will look like this:
`https://auth.cloud.google/signin-callback/locations/global/workforcePools/entra-id-oidc-pool-d/providers/entra-id-oidc-pool-provider-de`

### Step 2: Azure AD (Entra ID) Application Setup
With your WIF provider running, complete the setup of your Entra ID application to act as the Identity Provider (IdP) and your Datastore Connector.

**2A. Create/Configure the Application (`deloitte-entraid`)**
* Ensure your application is registered in Entra ID.
* Navigate to **Authentication**. Under **Web and SPA settings**:
  * Add the following **Redirect URIs**:
    * `http://localhost:5173/` (for local development)
    * `https://auth.cloud.google/signin-callback/locations/global/workforcePools/entra-id-oidc-pool-d/providers/entra-id-oidc-pool-provider-de` (from Step 1C)
  * Enable **ID tokens (used for implicit and hybrid flows)**.

**2B. Configure API Permissions**
Under **API Permissions**, you need to grant delegated permissions necessary for both basic sign-in and Datastore connectivity.
* **For the core Entra ID auth app (`deloitte-entraid`):**
  * Grant Microsoft Graph permissions: `email`, `openid`, `profile`, `User.Read`.
* **For the SharePoint Datastore connector (`deloitte-sharepoint-datastore`):**
  * Grant Microsoft Graph permissions: `Files.ReadWrite.All`, `Sites.Manage.All`, `Sites.Read.All`, `Sites.ReadWrite.All`, `User.Read`, `offline_access`.
  * Grant SharePoint permissions: `AllSites.Read`, `Sites.Search.All` (Requires Admin Consent).

*Example Screenshots of Entra ID & WIF Setup:*

**WIF Provider Configuration:**
![WIF Provider Configuration](./public/screenshots/WIF_provider_config.png)

**Entra ID Auth App (deloitte-entraid):**
![Entra ID Authentication Config](./public/screenshots/deloitte-entraid_Authentication.png)
![Entra ID API Permissions](./public/screenshots/deloitte-entraid_API_permissions.png)

**Datastore Connector (deloitte-sharepoint-datastore):**
![SharePoint Datastore Auth](./public/screenshots/deloitte-sharepoint-datastore_Authentication.png)
![SharePoint Datastore Permissions](./public/screenshots/deloitte-sharepoint-datastore_API_permissions.png)

### Step 3: Integrate with Frontend (No Secrets!)
Finally, configure the variables in `src/api/config.js` to link your frontend natively:
```javascript
export const CONFIG = {
  PROJECT_NUMBER: '<YOUR_PROJECT_NUMBER>',
  LOCATION: 'global',
  WIF_POOL: 'entra-id-oidc-pool-d',
  WIF_PROVIDER: 'entra-id-oidc-pool-provider-de',
  DATA_STORE_ID: '<YOUR_DATASTORE_ID>',
  ENGINE_ID: 'deloitte-demo',
  TENANT_ID: '<YOUR_TENANT_ID>',
  MS_APP_ID: '<YOUR_CLIENT_ID>', 
  ISSUER: 'https://login.microsoftonline.com/<YOUR_TENANT_ID>/v2.0'
};
```
Once configured, your frontend will securely authenticate via Entra ID, exchange the token using WIF (`entra-id-oidc-pool-d`), and query the Vertex AI Answer API natively containing actions in Gemini Enterprise.
