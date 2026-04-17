# SharePoint WIF Portal - Architecture Diagrams

Comprehensive architecture diagrams for the SharePoint WIF Portal solution, showing Google Cloud components, authentication flows, and data paths.

---

## 1. High-Level Architecture Overview

```mermaid
flowchart TB
    subgraph Users["👤 Users"]
        U1[Enterprise User]
    end

    subgraph Microsoft["Microsoft Entra ID"]
        MSAL[MSAL Authentication]
        ENTRA[Entra ID<br/>OAuth 2.0]
        JWT_ID[ID Token<br/>aud: client-id]
        JWT_ACCESS[Access Token<br/>aud: api://client-id]
    end

    subgraph UI["User Interfaces"]
        PORTAL[Custom React Portal<br/>Port 5173/8080]
        GE_UI[Gemini Enterprise UI<br/>Agentspace]
    end

    subgraph GCP["Google Cloud Platform"]
        subgraph WIF["Workforce Identity Federation"]
            WIF_POOL[WIF Pool<br/>sp-wif-pool-v2]
            GE_PROVIDER[ge-login-provider<br/>aud: client-id]
            ENTRA_PROVIDER[entra-provider<br/>aud: api://client-id]
            STS[Security Token Service<br/>sts.googleapis.com]
        end

        subgraph CloudRun["Cloud Run"]
            NGINX[nginx<br/>Reverse Proxy<br/>Port 8080]
            FASTAPI[FastAPI Backend<br/>Port 8000]
        end

        subgraph DiscoveryEngine["Discovery Engine / Grounding Engine"]
            GE_ENGINE[Gemini Enterprise Engine<br/>streamAssist API]
            SP_CONNECTOR[SharePoint Connector<br/>Federated - Third Party]
            DATASTORE[Data Store<br/>SharePoint Documents]
        end

        subgraph AgentEngine["Agent Engine / Vertex AI"]
            ADK[Google ADK<br/>InsightComparator Agent]
            GEMINI[Gemini 2.5 Flash Lite<br/>Model]
            TOOLS[compare_insights Tool]
        end

        subgraph OtherGCP["Supporting Services"]
            SECRET[Secret Manager]
            IAM[IAM & Permissions]
            ARTIFACT[Artifact Registry]
        end
    end

    subgraph Microsoft365["Microsoft 365"]
        SHAREPOINT[SharePoint Online<br/>Document Libraries]
    end

    subgraph Web["Public Web"]
        GOOGLE_SEARCH[Google Search<br/>Grounding]
    end

    %% User Flow
    U1 --> MSAL
    MSAL --> ENTRA
    ENTRA --> JWT_ID
    ENTRA --> JWT_ACCESS

    %% Portal Path
    JWT_ACCESS --> PORTAL
    PORTAL --> NGINX
    NGINX --> FASTAPI
    FASTAPI --> STS
    STS --> ENTRA_PROVIDER
    FASTAPI --> GE_ENGINE

    %% GE UI Path
    JWT_ID --> GE_UI
    GE_UI --> GE_PROVIDER
    GE_PROVIDER --> STS
    GE_UI --> ADK

    %% Discovery Engine
    GE_ENGINE --> SP_CONNECTOR
    SP_CONNECTOR --> DATASTORE
    DATASTORE -.->|Federated Auth| SHAREPOINT

    %% Agent
    ADK --> TOOLS
    TOOLS --> GE_ENGINE
    TOOLS --> GEMINI
    GEMINI --> GOOGLE_SEARCH

    %% Config
    SECRET -.-> CloudRun
    IAM -.-> WIF

    classDef microsoft fill:#0078d4,color:#fff
    classDef google fill:#4285f4,color:#fff
    classDef auth fill:#fbbc04,color:#000
    classDef agent fill:#34a853,color:#fff

    class MSAL,ENTRA,JWT_ID,JWT_ACCESS,SHAREPOINT microsoft
    class GE_ENGINE,ADK,GEMINI,DATASTORE google
    class WIF_POOL,GE_PROVIDER,ENTRA_PROVIDER,STS auth
    class TOOLS agent
```

---

## 2. Authentication Flow - JWT to GCP Token

```mermaid
sequenceDiagram
    autonumber
    participant User as 👤 User
    participant Frontend as React Portal
    participant MSAL as MSAL Library
    participant Entra as Microsoft Entra ID
    participant Backend as FastAPI Backend
    participant STS as Google STS
    participant WIF as WIF Provider<br/>(entra-provider)
    participant GE as Discovery Engine

    Note over User,GE: Step 1: User Authentication with Microsoft

    User->>Frontend: Open Portal
    Frontend->>MSAL: Check authentication
    MSAL->>Entra: Redirect to login
    User->>Entra: Enter credentials
    Entra->>Entra: Validate credentials

    Note over Entra: Issues TWO tokens:<br/>1. ID Token (aud: client-id)<br/>2. Access Token (aud: api://client-id)

    Entra-->>MSAL: Return tokens
    MSAL-->>Frontend: Store in session

    Note over User,GE: Step 2: Portal Query with WIF Exchange

    User->>Frontend: Submit search query
    Frontend->>Frontend: acquireTokenSilent()
    Frontend->>Backend: POST /api/chat<br/>Header: X-Entra-Id-Token

    Note over Backend: Extract Microsoft JWT<br/>from header

    Backend->>STS: POST /v1/token<br/>{subjectToken: JWT,<br/>audience: WIF pool/provider}

    STS->>WIF: Validate token
    WIF->>WIF: Check audience matches<br/>"api://client-id"
    WIF->>WIF: Map attributes<br/>(email, groups)

    alt Token Valid
        STS-->>Backend: GCP Access Token<br/>(user identity)
    else Token Invalid
        STS-->>Backend: Error: invalid_grant
        Backend-->>Frontend: "Please login"
    end

    Note over User,GE: Step 3: Query with User Identity

    Backend->>GE: POST streamAssist<br/>Authorization: Bearer GCP_TOKEN<br/>+ dataStoreSpecs

    Note over GE: User identity from token<br/>enforces SharePoint ACLs

    GE->>GE: Search SharePoint<br/>(ACL filtered)
    GE-->>Backend: Grounded answer + sources
    Backend-->>Frontend: Display results
    Frontend-->>User: Show answer with citations
```

---

## 3. Detailed WIF Token Exchange

```mermaid
flowchart LR
    subgraph Input["Input Token"]
        MS_JWT["Microsoft JWT<br/>───────────────<br/>iss: sts.windows.net/{tenant}<br/>aud: api://{client-id}<br/>sub: user@domain.com<br/>groups: [sg-1, sg-2]"]
    end

    subgraph STS_Exchange["STS Token Exchange"]
        STS_REQ["POST sts.googleapis.com/v1/token<br/>───────────────────────────<br/>audience: //iam.googleapis.com/<br/>  locations/global/<br/>  workforcePools/sp-wif-pool-v2/<br/>  providers/entra-provider<br/><br/>grantType: token-exchange<br/>subjectToken: {MS_JWT}<br/>subjectTokenType: jwt<br/>scope: cloud-platform"]
    end

    subgraph WIF_Validation["WIF Provider Validation"]
        CHECK_ISS["✓ Issuer matches<br/>sts.windows.net/{tenant}"]
        CHECK_AUD["✓ Audience matches<br/>api://{client-id}"]
        MAP_ATTR["Map Attributes<br/>───────────────<br/>google.subject = email<br/>google.groups = groups<br/>google.display_name = name"]
    end

    subgraph Output["Output Token"]
        GCP_TOKEN["GCP Access Token<br/>───────────────<br/>principal: user@domain.com<br/>principalSet: workforcePools/...<br/>expires_in: 3600<br/>scope: cloud-platform"]
    end

    MS_JWT --> STS_REQ
    STS_REQ --> CHECK_ISS
    CHECK_ISS --> CHECK_AUD
    CHECK_AUD --> MAP_ATTR
    MAP_ATTR --> GCP_TOKEN

    style MS_JWT fill:#0078d4,color:#fff
    style GCP_TOKEN fill:#4285f4,color:#fff
    style CHECK_ISS fill:#34a853,color:#fff
    style CHECK_AUD fill:#34a853,color:#fff
```

---

## 4. Two WIF Providers - Why Both Are Required

```mermaid
flowchart TB
    subgraph EntraTokens["Microsoft Entra ID Tokens"]
        ID_TOKEN["ID Token<br/>═══════════<br/>aud: {client-id}<br/>Used for: Direct login"]
        ACCESS_TOKEN["Access Token<br/>═══════════<br/>aud: api://{client-id}<br/>Used for: API calls"]
    end

    subgraph WIFPool["WIF Pool: sp-wif-pool-v2"]
        subgraph Provider1["ge-login-provider"]
            P1_AUD["Configured Audience:<br/>{client-id}"]
            P1_USE["Use Case:<br/>Gemini Enterprise Login"]
        end

        subgraph Provider2["entra-provider"]
            P2_AUD["Configured Audience:<br/>api://{client-id}"]
            P2_USE["Use Case:<br/>Portal + Agent WIF"]
        end
    end

    subgraph Flows["Authentication Flows"]
        GE_FLOW["Gemini Enterprise UI<br/>→ User clicks login<br/>→ WIF redirect<br/>→ ge-login-provider"]

        PORTAL_FLOW["Custom Portal<br/>→ MSAL acquireToken<br/>→ Backend exchange<br/>→ entra-provider"]

        AGENT_FLOW["Agent Engine<br/>→ OAuth grant<br/>→ Tool receives token<br/>→ entra-provider"]
    end

    ID_TOKEN --> P1_AUD
    ACCESS_TOKEN --> P2_AUD

    P1_AUD --> GE_FLOW
    P2_AUD --> PORTAL_FLOW
    P2_AUD --> AGENT_FLOW

    style ID_TOKEN fill:#0078d4,color:#fff
    style ACCESS_TOKEN fill:#0078d4,color:#fff
    style P1_AUD fill:#fbbc04,color:#000
    style P2_AUD fill:#fbbc04,color:#000
```

---

## 5. Data Flow - Query to Answer

```mermaid
sequenceDiagram
    autonumber
    participant User as 👤 User
    participant Portal as React Portal
    participant Backend as FastAPI
    participant STS as Google STS
    participant GE as Discovery Engine
    participant SP as SharePoint Connector
    participant SPO as SharePoint Online

    User->>Portal: "What is our Q3 strategy?"

    Note over Portal: Show thinking indicator<br/>Start elapsed timer

    Portal->>Portal: Get tokens from MSAL
    Portal->>Backend: POST /api/chat<br/>X-Entra-Id-Token: {jwt}

    Backend->>STS: Exchange JWT for GCP token
    STS-->>Backend: GCP access token

    Note over Backend: Build request with<br/>dataStoreSpecs (REQUIRED)

    Backend->>GE: POST streamAssist<br/>Authorization: Bearer {gcp_token}<br/>toolsSpec.dataStoreSpecs: [...]

    Note over GE: Extract user identity<br/>from GCP token

    GE->>SP: Search with user identity
    SP->>SPO: Query documents

    Note over SPO: ACL Check:<br/>User can access these docs?

    SPO-->>SP: Matching documents (ACL filtered)
    SP-->>GE: Document chunks + metadata

    GE->>GE: Generate grounded answer<br/>Add citations

    GE-->>Backend: Streamed response chunks

    Backend->>Backend: Extract answer + sources<br/>Parse groundingMetadata

    Backend-->>Portal: {answer, sources[], session_id}

    Portal->>Portal: Stop timer<br/>Render markdown

    Portal-->>User: Display answer with<br/>clickable citations
```

---

## 6. Agent Engine - Compare Insights Flow

```mermaid
sequenceDiagram
    autonumber
    participant User as 👤 User
    participant GE_UI as Gemini Enterprise
    participant Agent as InsightComparator<br/>Agent
    participant Tool as compare_insights<br/>Tool
    participant DE_Client as DiscoveryEngine<br/>Client
    participant STS as Google STS
    participant GE as Discovery Engine
    participant Gemini as Gemini 2.5<br/>Flash Lite
    participant Google as Google Search

    User->>GE_UI: "Compare our policy with industry standards"

    Note over GE_UI: User authorized agent<br/>Token in state: temp:sharepointauth2

    GE_UI->>Agent: Invoke with message

    Agent->>Agent: Detect auth key<br/>Pattern match temp:*

    Agent->>Tool: compare_insights(query, context)

    Note over Tool: Extract MS JWT from<br/>tool_context.state

    par Parallel Searches
        Tool->>DE_Client: search(query, user_token)
        DE_Client->>STS: Exchange JWT
        STS-->>DE_Client: GCP token
        DE_Client->>GE: streamAssist + dataStoreSpecs
        GE-->>DE_Client: Internal findings
        DE_Client-->>Tool: SharePoint results

    and
        Tool->>Gemini: Generate with googleSearch
        Gemini->>Google: Web search
        Google-->>Gemini: Web results
        Gemini-->>Tool: External findings
    end

    Tool-->>Agent: {internal_findings, external_findings}

    Agent->>Agent: Synthesize comparison

    Agent-->>GE_UI: Formatted response

    GE_UI-->>User: Internal vs External comparison
```

---

## 7. Cloud Run Deployment Architecture

```mermaid
flowchart TB
    subgraph Internet["Internet"]
        CLIENT[Browser Client]
    end

    subgraph CloudRun["Cloud Run Container"]
        subgraph Supervisord["supervisord (Process Manager)"]
            subgraph NGINX_PROC["nginx Process"]
                NGINX["nginx<br/>Port 8080<br/>══════════<br/>• Serve React SPA<br/>• Proxy /api/* → :8000<br/>• Health check proxy"]
            end

            subgraph BACKEND_PROC["backend Process"]
                UVICORN["uvicorn<br/>Port 8000<br/>══════════<br/>• FastAPI app<br/>• WIF exchange<br/>• Session mgmt"]
            end
        end

        STATIC["Static Files<br/>/usr/share/nginx/html<br/>══════════<br/>• React build<br/>• index.html<br/>• assets/"]

        CONFIG["Configuration<br/>══════════<br/>• /etc/nginx/sites-enabled/default<br/>• /etc/supervisor/supervisord.conf"]
    end

    subgraph GCP_Services["GCP Services"]
        SECRET_MGR["Secret Manager<br/>══════════<br/>• PROJECT_NUMBER<br/>• ENGINE_ID<br/>• DATA_STORE_ID<br/>• WIF_POOL_ID<br/>• etc."]

        IAM_SVC["IAM<br/>══════════<br/>• Service Account<br/>• WIF Pool binding<br/>• Discovery Engine roles"]
    end

    CLIENT -->|"HTTPS :443"| NGINX
    NGINX -->|"/"| STATIC
    NGINX -->|"/api/*"| UVICORN
    NGINX -->|"/health"| UVICORN

    SECRET_MGR -.->|"Env Vars"| UVICORN
    IAM_SVC -.->|"Permissions"| UVICORN

    style NGINX fill:#34a853,color:#fff
    style UVICORN fill:#4285f4,color:#fff
    style STATIC fill:#ea4335,color:#fff
```

---

## 8. Complete System - All Components

```mermaid
flowchart TB
    subgraph User["👤 Enterprise User"]
        BROWSER[Web Browser]
    end

    subgraph Microsoft["☁️ Microsoft Cloud"]
        ENTRA_ID["Entra ID<br/>OAuth 2.0 Provider"]
        SPO["SharePoint Online<br/>Document Libraries"]
    end

    subgraph GCP["☁️ Google Cloud Platform"]

        subgraph Presentation["Presentation Layer"]
            CR_PORTAL["Cloud Run<br/>SharePoint WIF Portal<br/>━━━━━━━━━━━━━━<br/>nginx + FastAPI<br/>React SPA"]
            GE_UI_2["Gemini Enterprise<br/>Agentspace UI"]
        end

        subgraph Identity["Identity Layer"]
            WIF_POOL_2["WIF Pool<br/>sp-wif-pool-v2<br/>━━━━━━━━━━━━━━<br/>ge-login-provider<br/>entra-provider"]
            STS_2["Security Token Service<br/>sts.googleapis.com"]
        end

        subgraph Intelligence["Intelligence Layer"]
            subgraph DiscoveryEng["Discovery Engine"]
                GE_ENGINE_2["Gemini Enterprise<br/>Engine<br/>━━━━━━━━━━━━━━<br/>streamAssist API<br/>Multi-turn sessions"]
                SP_CONN["SharePoint Connector<br/>━━━━━━━━━━━━━━<br/>Type: Federated<br/>Third-party connector"]
                DS["Data Store<br/>SharePoint docs"]
            end

            subgraph AgentEng["Agent Engine"]
                ADK_AGENT["ADK Agent<br/>InsightComparator<br/>━━━━━━━━━━━━━━<br/>compare_insights tool<br/>WIF token handling"]
                GEMINI_2["Gemini 2.5<br/>Flash Lite"]
            end
        end

        subgraph Grounding["Grounding Sources"]
            GOOGLE_2["Google Search<br/>Public Web"]
        end

        subgraph Platform["Platform Services"]
            SECRET_2["Secret Manager"]
            IAM_2["IAM"]
            ARTIFACT_2["Artifact Registry"]
            VERTEX["Vertex AI"]
        end
    end

    %% User flows
    BROWSER -->|"MSAL Login"| ENTRA_ID
    ENTRA_ID -->|"JWT Tokens"| BROWSER

    BROWSER -->|"Portal Access"| CR_PORTAL
    BROWSER -->|"GE UI Access"| GE_UI_2

    %% Auth flows
    CR_PORTAL -->|"Exchange JWT"| STS_2
    GE_UI_2 -->|"WIF Login"| WIF_POOL_2
    STS_2 <-->|"Validate"| WIF_POOL_2

    %% Query flows
    CR_PORTAL -->|"streamAssist"| GE_ENGINE_2
    GE_UI_2 -->|"Agent Query"| ADK_AGENT

    ADK_AGENT -->|"Internal Search"| GE_ENGINE_2
    ADK_AGENT -->|"LLM"| GEMINI_2
    GEMINI_2 -->|"Grounding"| GOOGLE_2

    %% Data flows
    GE_ENGINE_2 --> SP_CONN
    SP_CONN --> DS
    SP_CONN <-->|"Federated Auth"| SPO

    %% Platform
    SECRET_2 -.-> CR_PORTAL
    IAM_2 -.-> WIF_POOL_2
    VERTEX -.-> ADK_AGENT

    classDef microsoft fill:#0078d4,color:#fff
    classDef google fill:#4285f4,color:#fff
    classDef identity fill:#fbbc04,color:#000
    classDef agent fill:#34a853,color:#fff

    class ENTRA_ID,SPO microsoft
    class GE_ENGINE_2,GEMINI_2,DS,GE_UI_2 google
    class WIF_POOL_2,STS_2 identity
    class ADK_AGENT,SP_CONN agent
```

---

## 9. dataStoreSpecs - Critical Configuration

```mermaid
flowchart LR
    subgraph Request["streamAssist Request"]
        QUERY["query: {text: '...'}"]
        SESSION["session: projects/.../sessions/..."]
        TOOLS["toolsSpec:<br/>  vertexAiSearchSpec:<br/>    dataStoreSpecs: [...]"]
    end

    subgraph DataStoreSpec["dataStoreSpecs Array (REQUIRED)"]
        DS_PATH["dataStore:<br/>projects/{PROJECT_NUMBER}/<br/>locations/global/<br/>collections/default_collection/<br/>dataStores/{DATA_STORE_ID}"]
    end

    subgraph Result["Query Result"]
        direction TB
        WITH["✅ WITH dataStoreSpecs<br/>━━━━━━━━━━━━━━<br/>• SharePoint searched<br/>• Documents returned<br/>• ACLs enforced<br/>• Grounded answer"]
        WITHOUT["❌ WITHOUT dataStoreSpecs<br/>━━━━━━━━━━━━━━<br/>• NO SharePoint search<br/>• Empty sources<br/>• Generic answer<br/>• Common failure!"]
    end

    QUERY --> TOOLS
    SESSION --> TOOLS
    TOOLS --> DS_PATH
    DS_PATH --> WITH
    TOOLS -.->|"Missing"| WITHOUT

    style WITH fill:#34a853,color:#fff
    style WITHOUT fill:#ea4335,color:#fff
    style DS_PATH fill:#fbbc04,color:#000
```

---

## 10. Environment Variables Map

```mermaid
flowchart TB
    subgraph ENV[".env Configuration"]
        subgraph GCP_Config["GCP Configuration"]
            PROJECT_ID["PROJECT_ID<br/>sharepoint-wif-agent"]
            PROJECT_NUM["PROJECT_NUMBER<br/>123456789"]
            LOCATION["LOCATION<br/>us-central1"]
            BUCKET["STAGING_BUCKET<br/>gs://..."]
        end

        subgraph DE_Config["Discovery Engine"]
            ENGINE["ENGINE_ID<br/>gemini-enterprise-engine"]
            DATASTORE["DATA_STORE_ID<br/>sharepoint-datastore"]
        end

        subgraph WIF_Config["WIF Configuration"]
            POOL["WIF_POOL_ID<br/>sp-wif-pool-v2"]
            PROVIDER["WIF_PROVIDER_ID<br/>entra-provider ⚠️"]
        end

        subgraph Entra_Config["Microsoft Entra"]
            TENANT["TENANT_ID<br/>your-tenant-id"]
            CLIENT["OAUTH_CLIENT_ID<br/>your-client-id"]
            SECRET["OAUTH_CLIENT_SECRET<br/>your-secret"]
        end
    end

    subgraph Services["Services Using Config"]
        BACKEND_SVC["FastAPI Backend"]
        AGENT_SVC["ADK Agent"]
        FRONTEND_SVC["React Frontend<br/>(VITE_* vars)"]
    end

    GCP_Config --> BACKEND_SVC
    GCP_Config --> AGENT_SVC

    DE_Config --> BACKEND_SVC
    DE_Config --> AGENT_SVC

    WIF_Config --> BACKEND_SVC
    WIF_Config --> AGENT_SVC

    Entra_Config --> BACKEND_SVC
    Entra_Config --> FRONTEND_SVC

    style PROVIDER fill:#ea4335,color:#fff
    style DATASTORE fill:#fbbc04,color:#000
```

---

## Quick Reference

| Component | Technology | Port | Purpose |
|-----------|------------|------|---------|
| **Frontend** | React + Vite | 5173 (local) / 8080 (cloud) | User interface |
| **Backend** | FastAPI + uvicorn | 8000 | API, WIF exchange |
| **Proxy** | nginx | 8080 | Reverse proxy, static files |
| **Auth** | MSAL + WIF | - | Microsoft → GCP identity |
| **Search** | Discovery Engine | - | SharePoint grounded search |
| **Agent** | ADK + Agent Engine | - | Internal/external comparison |
| **Model** | Gemini 2.5 Flash Lite | - | LLM inference |

### Critical Success Factors

1. **Two WIF Providers** - ge-login-provider for GE UI, entra-provider for Portal/Agent
2. **dataStoreSpecs REQUIRED** - Without it, no SharePoint results
3. **Correct Audience** - api://client-id for access tokens
4. **oauth2AllowIdTokenImplicitFlow** - Must be true in Entra manifest
5. **IAM Roles** - discoveryengine.viewer + user on WIF principal
