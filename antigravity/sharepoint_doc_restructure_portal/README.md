# SharePoint Restructure & AI Governance Portal

<div align="center">

![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)
![Vite](https://img.shields.io/badge/Vite-646CFF?style=for-the-badge&logo=vite&logoColor=white)
![Google Cloud](https://img.shields.io/badge/Google_Cloud-4285F4?style=for-the-badge&logo=google-cloud&logoColor=white)
![Gemini AI](https://img.shields.io/badge/Gemini_3.5_Flash-8E75C2?style=for-the-badge&logo=google-gemini&logoColor=white)
![Microsoft Graph](https://img.shields.io/badge/Microsoft_Graph-0078D4?style=for-the-badge&logo=microsoft&logoColor=white)
![Security: Zero Leak](https://img.shields.io/badge/Security-Zero_Leak_Protocol-success?style=for-the-badge)

An enterprise-grade, serverless platform for AI-native metadata extraction, document restructuring, and secure role-based semantic search. This solution bridges Microsoft SharePoint Online repositories with Google Cloud's advanced Generative AI and security ecosystem, transforming unstructured corporate knowledge into structured, protected, and searchable assets.

</div>

---

## 📋 Table of Contents
1. [Executive Summary](#1-executive-summary)
2. [Zero-Leak Compliance Pipeline (Infographic)](#2-zero-leak-compliance-pipeline-infographic)
3. [Customer Journey (Step-by-Step)](#3-customer-journey-step-by-step)
4. [Google Cloud Target Architecture](#4-google-cloud-target-architecture)
5. [Codebase Anatomy & Repository Map](#5-codebase-anatomy--repository-map)
6. [Requirements Traceability Matrix (RTM)](#6-requirements-traceability-matrix-rtm)
7. [Secure Development & Zero-Leak Protocol](#7-secure-development--zero-leak-protocol)
8. [How to Run & Verify the Portal (Demo Environment)](#8-how-to-run--verify-the-portal-demo-environment)

---

## 1. Executive Summary

Corporate document storage is notoriously disorganized, containing millions of unstructured files across disconnected directories, legacy shares, and SharePoint sites. This disorganization creates substantial compliance and security risks (unredacted PII, incorrect confidentiality tags, broken access boundaries) and makes knowledge retrieval incredibly difficult.

The **SharePoint Document Restructure & AI Governance Portal** solves this challenge by implementing an automated, secure pipeline that:
1. **Crawls & Ingests** files recursively from SharePoint libraries using secure, delegated Entra ID authentication.
2. **Checks Data Compliance (DLP)** by running high-speed pattern scans for unredacted Personally Identifiable Information (PII) before any file is cataloged.
3. **Classifies & Tags** documents automatically against a three-level corporate taxonomy using **Gemini 3.5 Flash**, registering confidence scores and extraction rationales.
4. **Enables Human-in-the-Loop (HITL) QA** for manual validation and override of low-confidence classification tags.
5. **Guarantees Zero-Leak Access-Aware RAG** by indexing document embeddings into Vertex AI Search and applying Entra ID User Security Group filters *at query time*, ensuring users only retrieve search and chat answers from documents they are explicitly allowed to view in SharePoint.

---

## 2. Zero-Leak Compliance Pipeline (Infographic)

For business and compliance sponsors, this high-level pipeline infographic shows the end-to-end flow of raw corporate knowledge as it is synchronized, sanitized, classified, and made available for secure search—guaranteeing that role-based permissions are respected at every stage.

<div align="center">
  <img src="./assets/zero_leak_compliance_infographic.png" alt="Zero-Leak AI Document Shield Infographic" width="800px" style="border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.3); margin: 20px 0;" />
</div>

---

## 3. Customer Journey (Step-by-Step)

The portal provides an intuitive, streamlined workflow for both administrators (compliance/data managers) and corporate knowledge workers.

```
       [ Compliance Admin ]                             [ End User / Knowledge Worker ]
                │                                                     │
 1. Sign-in via Microsoft OAuth (Delegated)             1. Sign-in via Secure Portal
                │                                                     │
 2. Discover Site / Choose Library                      2. Enter Search Query / Ask Chatbot
                │                                                     │
 3. Trigger Sync (Incremental Crawler)                  3. System Resolves User's Entra ID Groups
                │                                                     │
 4. Monitor Live Sync Logs                              4. Vector Search Filters Chunks by ACL
                │                                                     │
 5. Validate Low-Confidence Tags (HITL)                5. Chatbot Generates Secure Grounded Answer
```

### Step 1: Secure Microsoft Authentication (OAuth 2.0 + PKCE)
*   **Action:** The Compliance Administrator accesses the portal and clicks **"Connect SharePoint"**. They are redirected to the standard Microsoft Entra ID sign-in page.
*   **Result:** Upon successful login with their corporate credentials (`admin@domain.com`), the application receives secure access and refresh tokens. The administrator is redirected back to the portal dashboard, where their active profile is displayed.

### Step 2: SharePoint Library Discovery
*   **Action:** The administrator enters a search term (e.g., `sockcop` or `CWP`) in the site discovery panel.
*   **Result:** The portal calls Microsoft Graph API to find matching SharePoint sites and lists their available Document Libraries (e.g., `Shared Documents`). The admin selects the target directory or path to synchronize.

### Step 3: Triggering Incremental Synchronization
*   **Action:** The admin clicks **"Sync SharePoint Site"**.
*   **Result:** The pipeline starts in a background thread.
    *   *Incremental Sync:* The crawler compares SharePoint files with documents already registered in Google Cloud Firestore. **Previously indexed files are skipped automatically**, preventing redundant downloads and unnecessary GenAI token usage.
    *   *Paced Downloading:* The crawler streams files safely, managing rate-limits and retries automatically if Microsoft Graph throttles the requests.
    *   *Extensible Parsers:* Supports native, zero-dependency extraction of `.pdf`, `.docx`, `.pptx` (PowerPoint), `.xlsx` (Excel matrices), `.eml` (email headers/bodies), and raw image formats.

### Step 4: Real-time Live Log Monitoring
*   **Action:** The administrator watches the **Live Ingestion Console** inside the UI.
*   **Result:** A terminal-like status panel outputs real-time progress:
    *   `[10:20:39] Initializing SharePoint Sync...`
    *   `[10:20:39] Fetching directory folders mapping recursively...`
    *   `[10:21:07] Skipping already-indexed file: Annual Report 2025.pdf (FR04)`
    *   `[10:21:08] Checking for unredacted PII...`
    *   `[10:21:17] Ontology extracted: type=PwC Operational File, subtype=PwC Thought Leadership...`
    *   `[10:21:18] Writing metadata properties to Cloud Firestore catalog...`

### Step 5: Human-in-the-Loop (HITL) Taxonomy Validation
*   **Action:** Files containing unredacted PII, metadata mismatches, or low-confidence scores from Gemini are flagged and routed to the **Compliance Review Queue**.
*   **Result:** A supervisor reviews Gemini's extraction rationale side-by-side with the document details. They can manually adjust the confidentiality level (e.g., *Internal* to *Confidential*) or correct a document sub-type using a dropdown form, and click **"Approve Override"**. Approvals update the vector index in real time.

### Step 6: Secure Semantic Search & Chat Retrieval (RAG)
*   **Action:** An end-user signs into the Aether Chat Assistant and asks a question (e.g., *"What are the liability terms for Client B?"*).
*   **Result:** 
    1.  The backend immediately calls Microsoft Graph to retrieve the user's active **Entra ID Security Group memberships** (transitive groups).
    2.  The backend queries the Vector Database, appending the user's group IDs as metadata filters.
    3.  Only text chunks matching the user's allowed groups are retrieved. **Unauthorized content is filtered out at the database layer** and never reaches the LLM.
    4.  The assistant provides a clear, grounded answer with clickable citation links to open the original source file directly in SharePoint.

---

## 4. Google Cloud Target Architecture

For IT architects and technical managers, this architecture diagram maps the secure boundaries, compute nodes, and serverless APIs on Google Cloud Platform.

<div align="center">
  <img src="./assets/customer_architecture_infographic.png" alt="Google Cloud Target Architecture Diagram" width="800px" style="border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.3); margin: 20px 0;" />
</div>

> [!NOTE]
> The diagram above represents our production deployment model. The system can also render as a live Mermaid flowchart by expanding the panel below.

<details>
<summary><b>📐 View Interactive Mermaid Flowchart</b></summary>

```mermaid
graph TB
    %% Nodes
    User((Corporate User))
    Frontend[Cloud Run: Portal Frontend]
    Backend[Cloud Run: Ingestion & Search Backend]
    Crawler[Cloud Run: SharePoint Ingest Worker]
    Tasks[Cloud Tasks: Retry Queue]
    Redis[(Cloud Memorystore: Redis Cache)]
    WIF[Workforce Identity Federation]
    SM[Secret Manager]
    DLP[Cloud DLP API]
    Gemini[Vertex AI: Gemini 3.5 Flash]
    Embeddings[Vertex AI: text-embedding-004]
    Firestore[(Cloud Firestore: State Registry)]
    BigQuery[(BigQuery: Audit Ledger)]
    VectorSearch[Vertex AI Search: Data Stores]
    Entra[Microsoft Entra ID / OAuth]
    Graph[Microsoft Graph API]
    SPO[SharePoint Document Libraries]

    %% Subgraphs
    subgraph SPO_Tenant ["Microsoft 365 Tenant"]
        Entra
        Graph
        SPO
    end

    subgraph GCP_Identity ["GCP Ingress & Secrets"]
        WIF
        SM
    end

    subgraph GCP_Compute ["GCP Compute & Queueing"]
        Frontend
        Backend
        Crawler
        Tasks
        Redis
    end

    subgraph GCP_Services ["GCP Data & Security APIs"]
        DLP
        Gemini
        Embeddings
    end

    subgraph GCP_Storage ["GCP Storage & Search Indexes"]
        Firestore
        BigQuery
        VectorSearch
    end

    %% Connections
    User -->|HTTPS| Frontend
    Frontend -->|API Queries| Backend
    Backend -->|Initiate MSAL Auth / Token Cache| Redis
    Backend -->|Read App Keys| SM
    Backend -->|Delegated Access Tokens| WIF
    Backend -->|Enqueues Sync Jobs| Tasks
    WIF <-->|OIDC Federated Trust| Entra
    Tasks -->|Triggers Crawls| Crawler
    Crawler -->|Fetch Directories / Download Content| Graph
    Graph -->|Downloads File Content| SPO
    Crawler -->|Fetch Tokens / Check Status| Redis
    Crawler -->|Scan Text for PII| DLP
    Crawler -->|Taxonomy Tagging & Classification| Gemini
    Crawler -->|Generate Semantic Vectors| Embeddings
    Crawler -->|Save Extraction State| Firestore
    Crawler -->|Write Audit Logs| BigQuery
    Crawler -->|Index Vectors & ACL Metadata| VectorSearch
    Backend -->|Permission-Aware Query| VectorSearch
```
</details>

### Architectural Component Mapping & Justifications

| Component | Target GCP Service | Technical Purpose | Customer Value / Justification |
| :--- | :--- | :--- | :--- |
| **Portal UI** | **Cloud Run** (React Container) | Serves the admin portal and chat interface. | Serverless, autoscaling, and fully isolated from the public internet using Google Identity-Aware Proxy (IAP). |
| **API Backend** | **Cloud Run** (FastAPI Container) | Core orchestrator. Mappings, tokens, and active session workflows. | Autoscales-to-zero when inactive, eliminating ongoing compute idle costs. |
| **Crawler Daemon** | **Cloud Run** (Background Worker) | Dedicated worker that downloads and indexes files. | Scaled to higher memory and execution timeouts to support large legal contracts and PDF parsing. |
| **Throttling Buffer** | **Cloud Tasks** | Controls request flow rates. | Microsoft Graph throttles heavily. Cloud Tasks handles automated retries and pacing to prevent rate limiting (HTTP 429). |
| **Auth Cache** | **Cloud Memorystore (Redis)** | Cache for OAuth tokens. | Maintains session continuity. Resolves background thread MSAL token refreshes. |
| **Identity Federation** | **Workforce Identity Pools** | Bridges Entra ID identity to Google IAM. | Allows secure, credential-less access to Google services directly using M365 tokens. |
| **Data Compliance** | **Cloud DLP API** | Automated PII checker. | Prevents sensitive personal data (SSNs, phone numbers) from leaking into shared AI search indexes. |
| **Document Understanding** | **Vertex AI (Gemini 3.5 Flash)** | Extracts structured taxonomies from files. | High performance and cost-efficiency. Its native multimodal engine parses complex layouts without custom OCR code. |
| **State Database** | **Cloud Firestore** | NoSQL Document DB for active configurations. | Real-time status updates and document states with sub-millisecond query performance. |
| **Enterprise Ledger** | **BigQuery** | Canonical log of metadata and overrides. | Provides immutable, tamper-evident audit logs of all human tag adjustments and compliance actions. |
| **Search Engine** | **Vertex AI Search** | Secure vector database. | Performs permissions-aware similarity search, automatically filtering results by user-level active directory groups. |

---

## 5. Codebase Anatomy & Repository Map

To help developers quickly navigate our codebase and understand where key operations are implemented:

```
sharepoint_doc_restructure_portal/
├── assets/                           # High-fidelity marketing & architecture infographics
│   ├── zero_leak_compliance_infographic.png  # Business-facing executive overview
│   ├── customer_architecture_infographic.png  # GCP Infrastructure architecture diagram
│   └── sharepoint_portal_mockup.png  # Screenshot of the live portal interface
├── backend/                          # FastAPI Backend Engine (Python 3.11+)
│   ├── main.py                       # Core API orchestrator, Graph sync loop & Gemini extraction
│   └── uvicorn.log                   # Service startup and execution logs
├── frontend/                         # React Admin & Chat Dashboard (Vite + TypeScript)
│   ├── src/
│   │   ├── App.tsx                   # Main layout, router, and live log polling connections
│   │   ├── main.tsx                  # React DOM entry point
│   │   └── index.css                 # Clean CSS typography, console animations & layouts
│   ├── package.json                  # Frontend dependencies
│   └── vite.config.ts                # Vite execution config (Port 5185)
├── scripts/                          # Administration and diagnostic scripts
├── ACL_MAPPING.md                    # Technical guide on synchronizing and mapping SharePoint ACLs to GCP
├── LOW_LEVEL_DESIGN.md               # Detailed logical data flows and service configurations
├── PERFORMANCE_AUDIT.md              # Performance findings, API latency reviews and optimizations
└── UI_SPECIFICATION.md               # User Interface structure, console and chat design guidelines
```

### Essential Technical References
*   **Access Control Strategy:** Detail on Entra ID to GCP Group mapping can be found in [ACL_MAPPING.md](file:///Users/jesusarguelles/IdeaProjects/vertex-ai-samples/antigravity/sharepoint_doc_restructure_portal/ACL_MAPPING.md).
*   **Sub-system Architecture:** Deep logical data flows are specified in [LOW_LEVEL_DESIGN.md](file:///Users/jesusarguelles/IdeaProjects/vertex-ai-samples/antigravity/sharepoint_doc_restructure_portal/LOW_LEVEL_DESIGN.md).
*   **Frontend Design System:** Console layout guidelines are outlined in [UI_SPECIFICATION.md](file:///Users/jesusarguelles/IdeaProjects/vertex-ai-samples/antigravity/sharepoint_doc_restructure_portal/UI_SPECIFICATION.md).

---

## 6. Requirements Traceability Matrix (RTM)

This matrix maps how each of your functional, technical, and regulatory requirements is directly addressed by our implementation.

| Requirement ID | Description | Solution Implementation Details | Verification Status |
| :--- | :--- | :--- | :--- |
| **FR01** | Multi-level Taxonomy Classification | [main.py](file:///Users/jesusarguelles/IdeaProjects/vertex-ai-samples/antigravity/sharepoint_doc_restructure_portal/backend/main.py#L740-L789) executes Gemini 3.5 Flash with a strictly typed Pydantic extraction schema, returning Level 1 Class, Level 2 Sub-Class, and relevant industry. | **Verified** |
| **FR04** | Deduplication & Incremental Loading | [main.py](file:///Users/jesusarguelles/IdeaProjects/vertex-ai-samples/antigravity/sharepoint_doc_restructure_portal/backend/main.py#L701-L704) loads existing documents from Firestore on start and compares names, skipping previously successfully processed files. | **Verified** |
| **FR06** | Real-Time Sync Logs | Ingest console polls the `/api/sharepoint/crawler-logs` endpoint, streaming granular steps and warnings to the Live Logs interface. | **Verified** |
| **FR09** | Clickable Source Citations | Document chunks are indexed alongside their SharePoint `webUrl` in Vertex AI Search. The chat assistant returns these as active hyperlinked citations. | **Verified** |
| **FR10** | Multimodal Document Extraction | PDFs and Word docs are fed directly to Gemini as raw bytes, bypassing local parsing errors on images, flowcharts, or complex tables. | **Verified** |
| **FR37** | Rigorous Metadata Rationale | The Gemini Pydantic schema includes a `rationale` field. The model must write its analytical justification, which is visible in the audit logs. | **Verified** |
| **FR39** | Real-Time Access Control | User's transitive group memberships are fetched via Entra ID at query time and applied as pre-filters to the vector search index. | **Verified** |
| **SR02** | Sensitive Data Protection (DLP) | Documents are scanned for unredacted PII patterns. Detections raise warning flags, block public viewing, and request compliance reviews. | **Verified** |
| **SR45** | Human-in-the-Loop (HITL) Queue | Flagged or low-confidence documents are set to `PENDING_QA` in Firestore. Admins use a dedicated UI form to override metadata tags. | **Verified** |

---

## 7. Secure Development & Zero-Leak Protocol

This project handles highly confidential corporate and legal files. Our secure development protocol guarantees that **no private or proprietary information is ever exposed or leaked into public repositories like GitHub.**

> [!IMPORTANT]
> **Strict Environment Separation:**
> Credentials (tokens, secrets, and `.env` files) are never checked into git. If a credential is accidentally committed, it is considered compromised and must be revoked immediately.

### 🛡️ Ironclad Security Safeguards
1. **Dynamic Secret Sourcing:** No API keys, client secrets, or OAuth credentials are written in code. All configurations are loaded from system environment variables or GCP Secret Manager.
2. **Explicit Git Exclusions:** The repository's active `.gitignore` strictly blocks the staging or committing of any local settings, secrets, or temporary state caches.
3. **Isolated Session Cache:** Active session tokens and silent refresh states are stored in `.ms365_auth.json` within a local, un-tracked system folder. No credentials are pushed to remote Git targets, making code promotion entirely safe.
4. **Vector Math Protection:** Vertex AI Vector Search indexes high-level document summaries and mathematically generated semantic vectors (embeddings). Raw files remain safely stored in your Microsoft SharePoint Online tenant.

---

## 8. How to Run & Verify the Portal (Demo Environment)

Follow these instructions to start the development servers and verify the end-to-end synchronization pipeline.

### Prerequisites
*   A Google Cloud Platform environment (using project `vtxdemos` in the `global` region).
*   Active Microsoft SharePoint tenant credentials.

### Step 1: Run the Backend Portal
Launch the FastAPI uvicorn server in a separate terminal:
```bash
cd ~/IdeaProjects/vertex-ai-samples/antigravity/sharepoint_doc_restructure_portal
./start_portal.sh
```
*The server will warm up the vector index with existing Firestore entries and listen on port `8095`.*

### Step 2: Run the Frontend UI
Start the Vite developer server:
```bash
cd ~/IdeaProjects/vertex-ai-samples/antigravity/sharepoint_doc_restructure_portal/frontend
npm run dev -- --port 5185
```
*Open [http://localhost:5185](http://localhost:5185) in your web browser.*

### Step 3: Trigger Sync & Review Logs
1. Navigate to the portal UI.
2. Click **"Connect SharePoint"** and sign in.
3. Search for your site (e.g., `sockcop`), choose the library, and click **"Sync SharePoint Site"**.
4. Observe the live console logs at the bottom of the screen. Watch as the incremental logic skips existing files and safely catalogs new documents, fully managing background session refreshes indefinitely!

<details>
<summary><b>🔑 View Microsoft Entra ID App Registration Guidelines</b></summary>

To register the application in Microsoft Entra ID:
1. Navigate to the **Microsoft Entra admin center**.
2. Select **Applications** > **App registrations** > **New registration**.
3. Set the name to `SharePoint Restructure AI Portal`.
4. Set the **Supported account types** to *Accounts in this organizational directory only*.
5. Under **Redirect URI**, select *Single-page application (SPA)* or *Web* as appropriate, and configure redirect URLs pointing to:
   * `http://localhost:5185/`
   * `http://localhost:8095/api/sharepoint/auth-callback`
6. Under **API permissions**, click **Add a permission** and select **Microsoft Graph** with **Delegated permissions**:
   * `User.Read`
   * `Sites.Read.All`
   * `Files.Read.All`
   * `GroupMember.Read.All` (for transit group resolution)
7. Grant Admin Consent for the configured tenant.
8. Create a Client Secret under **Certificates & secrets** and record the Client ID and Tenant ID. Save these values inside your local parent directory `.env` file (which is safely excluded from Git).
</details>
