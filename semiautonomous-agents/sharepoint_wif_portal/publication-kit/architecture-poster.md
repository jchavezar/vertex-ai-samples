# SharePoint WIF Portal - Architecture Poster

## Complete Solution Architecture

```mermaid
%%{init: {'theme': 'base', 'themeVariables': { 'primaryColor': '#4285f4', 'primaryTextColor': '#fff', 'primaryBorderColor': '#1a73e8', 'lineColor': '#5f6368', 'secondaryColor': '#34a853', 'tertiaryColor': '#fbbc04'}}}%%

flowchart TB
    %% ============================================
    %% USER LAYER
    %% ============================================
    subgraph USERS["<b>👤 ENTERPRISE USERS</b>"]
        direction LR
        USER_PORTAL["Portal User"]
        USER_GE["Gemini Enterprise User"]
    end

    %% ============================================
    %% MICROSOFT IDENTITY
    %% ============================================
    subgraph MICROSOFT["<b>☁️ MICROSOFT ENTRA ID</b>"]
        direction TB
        MSAL["<b>MSAL</b><br/>Authentication Library"]
        ENTRA["<b>Entra ID</b><br/>OAuth 2.0 / OIDC"]

        subgraph TOKENS["Issued Tokens"]
            direction LR
            ID_TOK["<b>ID Token</b><br/>━━━━━━━━━<br/>aud: {client-id}<br/>For: GE Login"]
            ACCESS_TOK["<b>Access Token</b><br/>━━━━━━━━━<br/>aud: api://{client-id}<br/>For: Portal + Agent"]
        end

        MSAL --> ENTRA
        ENTRA --> TOKENS
    end

    %% ============================================
    %% USER INTERFACES
    %% ============================================
    subgraph INTERFACES["<b>🖥️ USER INTERFACES</b>"]
        direction LR
        subgraph PORTAL_UI["Custom Portal"]
            REACT["<b>React SPA</b><br/>━━━━━━━━━<br/>• MSAL Auth<br/>• Chat Interface<br/>• Source Citations"]
        end

        subgraph GE_INTERFACE["Gemini Enterprise"]
            AGENTSPACE["<b>Agentspace</b><br/>━━━━━━━━━<br/>• WIF Login<br/>• Agent Picker<br/>• OAuth Grant"]
        end
    end

    %% ============================================
    %% GOOGLE CLOUD - IDENTITY
    %% ============================================
    subgraph GCP["<b>☁️ GOOGLE CLOUD PLATFORM</b>"]

        subgraph WIF_LAYER["<b>🔐 WORKFORCE IDENTITY FEDERATION</b>"]
            direction TB
            WIF_POOL["<b>WIF Pool</b><br/>sp-wif-pool-v2"]

            subgraph PROVIDERS["Identity Providers"]
                direction LR
                GE_PROV["<b>ge-login-provider</b><br/>━━━━━━━━━━━━<br/>Audience: {client-id}<br/>Use: GE UI Login"]
                ENTRA_PROV["<b>entra-provider</b><br/>━━━━━━━━━━━━<br/>Audience: api://{client-id}<br/>Use: Portal + Agent"]
            end

            STS["<b>Security Token Service</b><br/>sts.googleapis.com<br/>━━━━━━━━━━━━━━━<br/>JWT → GCP Token Exchange"]

            WIF_POOL --> PROVIDERS
            PROVIDERS --> STS
        end

        %% ============================================
        %% GOOGLE CLOUD - COMPUTE
        %% ============================================
        subgraph COMPUTE_LAYER["<b>⚙️ CLOUD RUN</b>"]
            direction TB
            subgraph CR_CONTAINER["Container"]
                direction LR
                NGINX["<b>nginx</b><br/>:8080<br/>━━━━━<br/>Proxy"]
                FASTAPI["<b>FastAPI</b><br/>:8000<br/>━━━━━<br/>Backend"]
                NGINX --> FASTAPI
            end
        end

        %% ============================================
        %% GOOGLE CLOUD - INTELLIGENCE
        %% ============================================
        subgraph AI_LAYER["<b>🧠 INTELLIGENCE LAYER</b>"]
            direction TB

            subgraph DISCOVERY["<b>Discovery Engine / Grounding Engine</b>"]
                direction TB
                GE_ENGINE["<b>Gemini Enterprise Engine</b><br/>━━━━━━━━━━━━━━━━━<br/>• streamAssist API<br/>• Multi-turn Sessions<br/>• Grounded Answers"]

                SP_CONNECTOR["<b>SharePoint Connector</b><br/>━━━━━━━━━━━━━━━━━<br/>Type: Federated (Third-party)<br/>Auth: WIF User Identity<br/>ACL: Enforced"]

                DATA_STORE["<b>Data Store</b><br/>━━━━━━━━━<br/>SharePoint Docs"]

                GE_ENGINE --> SP_CONNECTOR
                SP_CONNECTOR --> DATA_STORE
            end

            subgraph AGENT["<b>Agent Engine / Vertex AI</b>"]
                direction TB
                ADK_APP["<b>ADK Agent</b><br/>InsightComparator<br/>━━━━━━━━━━━━<br/>• compare_insights tool<br/>• WIF token handling<br/>• Parallel search"]

                GEMINI_MODEL["<b>Gemini 2.5 Flash Lite</b><br/>━━━━━━━━━━━━━━━<br/>• Tool execution<br/>• Response synthesis"]

                ADK_APP --> GEMINI_MODEL
            end
        end

        subgraph GROUNDING["<b>🌐 GROUNDING SOURCES</b>"]
            direction LR
            GOOGLE_SEARCH["<b>Google Search</b><br/>Public Web"]
        end
    end

    %% ============================================
    %% MICROSOFT 365 DATA
    %% ============================================
    subgraph M365["<b>📁 MICROSOFT 365</b>"]
        SPO["<b>SharePoint Online</b><br/>━━━━━━━━━━━━━━<br/>Document Libraries<br/>ACL-Protected Content"]
    end

    %% ============================================
    %% CONNECTIONS
    %% ============================================

    %% User Authentication
    USERS --> MSAL
    ACCESS_TOK --> PORTAL_UI
    ID_TOK --> GE_INTERFACE

    %% Portal Flow
    PORTAL_UI --> CR_CONTAINER
    FASTAPI -->|"1. Exchange JWT"| STS
    STS -->|"2. Validate"| ENTRA_PROV
    FASTAPI -->|"3. Query with<br/>GCP Token"| GE_ENGINE

    %% GE UI Flow
    GE_INTERFACE -->|"WIF Login"| GE_PROV
    GE_PROV --> STS
    GE_INTERFACE -->|"Agent Query"| ADK_APP

    %% Agent Flow
    ADK_APP -->|"Internal Search"| GE_ENGINE
    GEMINI_MODEL -->|"External Search"| GOOGLE_SEARCH

    %% Data Flow
    DATA_STORE <-->|"Federated Auth<br/>ACL Enforced"| SPO

    %% ============================================
    %% STYLING
    %% ============================================
    classDef microsoft fill:#0078d4,color:#fff,stroke:#005a9e
    classDef google fill:#4285f4,color:#fff,stroke:#1a73e8
    classDef identity fill:#fbbc04,color:#000,stroke:#f9a825
    classDef agent fill:#34a853,color:#fff,stroke:#1e8e3e
    classDef data fill:#ea4335,color:#fff,stroke:#c5221f
    classDef user fill:#9c27b0,color:#fff,stroke:#7b1fa2

    class MSAL,ENTRA,ID_TOK,ACCESS_TOK,SPO microsoft
    class GE_ENGINE,GEMINI_MODEL,DATA_STORE,AGENTSPACE,GOOGLE_SEARCH google
    class WIF_POOL,GE_PROV,ENTRA_PROV,STS identity
    class ADK_APP,SP_CONNECTOR agent
    class REACT,FASTAPI,NGINX data
    class USER_PORTAL,USER_GE user
```

---

## Authentication Sequence - The Complete Flow

```mermaid
%%{init: {'theme': 'base', 'themeVariables': { 'actorBkg': '#4285f4', 'actorTextColor': '#fff'}}}%%

sequenceDiagram
    autonumber

    box rgb(156, 39, 176) Users
        participant User as 👤 User
    end

    box rgb(0, 120, 212) Microsoft
        participant MSAL as MSAL
        participant Entra as Entra ID
    end

    box rgb(251, 188, 4) Identity Federation
        participant STS as Google STS
        participant WIF as WIF Provider
    end

    box rgb(66, 133, 244) Google Services
        participant Backend as FastAPI
        participant GE as Discovery Engine
        participant SP as SharePoint<br/>Connector
    end

    box rgb(0, 120, 212) Microsoft 365
        participant SPO as SharePoint<br/>Online
    end

    Note over User,SPO: PHASE 1: Microsoft Authentication

    User->>MSAL: Open Portal
    MSAL->>Entra: Authorization Request<br/>scope: api://{client-id}/user_impersonation
    Entra->>User: Login Page
    User->>Entra: Credentials
    Entra-->>MSAL: ID Token + Access Token

    Note over User,SPO: PHASE 2: WIF Token Exchange

    User->>Backend: POST /api/chat<br/>X-Entra-Id-Token: {jwt}

    rect rgb(251, 188, 4, 0.1)
        Backend->>STS: Exchange Token Request<br/>subjectToken: {microsoft_jwt}<br/>audience: workforcePools/.../providers/entra-provider
        STS->>WIF: Validate JWT
        WIF->>WIF: ✓ Issuer: sts.windows.net/{tenant}<br/>✓ Audience: api://{client-id}<br/>✓ Map: email → google.subject
        WIF-->>STS: Validation OK
        STS-->>Backend: GCP Access Token<br/>(represents user identity)
    end

    Note over User,SPO: PHASE 3: Grounded Search with ACLs

    rect rgb(66, 133, 244, 0.1)
        Backend->>GE: POST streamAssist<br/>Authorization: Bearer {gcp_token}<br/>dataStoreSpecs: [{dataStore: ...}]
        GE->>SP: Search with user identity
        SP->>SPO: Query documents<br/>User: user@domain.com
        Note over SPO: ACL Check:<br/>What can this user see?
        SPO-->>SP: Filtered documents
        SP-->>GE: Document chunks + metadata
        GE->>GE: Generate grounded answer<br/>Add citations
        GE-->>Backend: Answer + Sources
    end

    Backend-->>User: Grounded response<br/>with SharePoint citations
```

---

## Component Details

### Discovery Engine Configuration

| Setting | Value | Purpose |
|---------|-------|---------|
| **Engine Type** | Gemini Enterprise | Generative search with grounding |
| **Location** | global | Multi-region availability |
| **Collection** | default_collection | Standard container |
| **API** | streamAssist | Streaming grounded answers |
| **Sessions** | Multi-turn | Conversation context |

### WIF Provider Configuration

| Provider | Audience | Use Case |
|----------|----------|----------|
| **ge-login-provider** | `{client-id}` | Gemini Enterprise UI login via WIF redirect |
| **entra-provider** | `api://{client-id}` | Portal backend + Agent Engine WIF exchange |

### Agent Engine (ADK)

| Setting | Value |
|---------|-------|
| **Agent Name** | InsightComparator |
| **Model** | gemini-2.5-flash-lite |
| **Tool** | compare_insights |
| **Deployment** | Vertex AI Reasoning Engines |
| **Auth Handling** | Auto-detect temp:* keys in state |

### Critical Environment Variables

```
# MUST SET (deployments fail silently without these)
PROJECT_NUMBER=123456789          # For Discovery Engine URLs
ENGINE_ID=your-engine-id          # Discovery Engine
DATA_STORE_ID=your-datastore-id   # SharePoint data store (CRITICAL!)
WIF_POOL_ID=sp-wif-pool-v2        # WIF pool
WIF_PROVIDER_ID=entra-provider    # MUST be "entra-provider" for api:// audience
```
