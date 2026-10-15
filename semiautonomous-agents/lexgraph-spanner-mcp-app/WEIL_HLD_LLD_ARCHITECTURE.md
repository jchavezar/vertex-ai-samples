# Weil, Gotshal & Manges LLP — Enterprise Legal AI MVP: High-Level Design (HLD), Low-Level Design (LLD) & 8-Use-Case Live Demos

**Author:** Jesus Chavez (`jesusarguelles@google.com`)  
**GCP Reference Environment:** `vtxdemos` (`us-central1`) · **Spanner GraphRAG:** `weil-legal-spanner` / `weil-legal-context` (`WeilLegalGraph`)  
**Gemini Enterprise Engines:** [`weil-legal-spanner-ge`](https://vertexaisearch.cloud.google.com/home/cid/ed20fa6b-3ad3-42e3-8fcf-0c8cc1af065f) & [`gemini-enterprise-17877637_1787763712023`](https://vertexaisearch.cloud.google.com/home/cid/b9298b3d-d513-4be8-b33a-971d8d3a0965)

---

## Quick Navigation
1. [Executive Summary & MVP Feasibility (Why Unstructured Indexing is the Critical Path)](#1-executive-summary--mvp-feasibility-why-unstructured-indexing-is-the-critical-path)
2. [High-Level Design (HLD) — End-to-End Enterprise Legal Platform Architecture](#2-high-level-design-hld--end-to-end-enterprise-legal-platform-architecture)
3. [Low-Level Design (LLD-1) — Unstructured Multimodal Document Indexing Pipeline](#3-low-level-design-lld-1--unstructured-multimodal-document-indexing-pipeline)
4. [Low-Level Design (LLD-2) — Direct API vs. Selective Indexing for Email, Calendar & Chat](#4-low-level-design-lld-2--direct-api-vs-selective-indexing-for-email-calendar--chat)
5. [Low-Level Design (LLD-3) — All 8 Legal Use Cases, Architecture & Live Cloud Run Demos](#5-low-level-design-lld-3--all-8-legal-use-cases-architecture--live-cloud-run-demos)
   - [UC-1: Document Redlining & Playbook Deviation Analysis](#uc-1-document-redlining--playbook-deviation-analysis)
   - [UC-2: Integrated Word Processing & Privacy Pro "Legal Legos" (.docx)](#uc-2-integrated-word-processing--privacy-pro-legal-legos-docx)
   - [UC-3: Side-by-Side Pin-Cite Citation Review (★ Priority)](#uc-3-side-by-side-pin-cite-citation-review--priority)
   - [UC-4: Email, Calendar & Chat Triage Automation (Direct API vs. Graph Evaluation)](#uc-4-email-calendar--chat-triage-automation-direct-api-vs-graph-evaluation)
   - [UC-5: Multi-Document Tabular Analysis Grids (★ Priority — Mike OSS in GE)](#uc-5-multi-document-tabular-analysis-grids--priority--mike-oss-in-ge)
   - [UC-6: Self-Service Workflow & Grid Builder + Homegrown Apps (FundGen, FundHQ, Antitrust)](#uc-6-self-service-workflow--grid-builder--homegrown-apps-fundgen-fundhq-antitrust)
   - [UC-7: Matter & Knowledge Workspaces (Cross-Matter Precedent GraphRAG)](#uc-7-matter--knowledge-workspaces-cross-matter-precedent-graphrag)
   - [UC-8: Dynamic Client-Matter Tracking (CMN Context Switcher & Intapp Ethical Walls)](#uc-8-dynamic-client-matter-tracking-cmn-context-switcher--intapp-ethical-walls)

---

## 1. Executive Summary & MVP Feasibility (Why Unstructured Indexing is the Critical Path)

Delivering the MVP in **November** (ahead of the December 10 target) is **technically feasible on the application and agent layer**—we already have all **5 Custom MCP App Studios (`SEP-1865`)** and **8 Use Cases** running end-to-end inside Gemini Enterprise and Cloud Run.

However, **overall timeline feasibility depends primarily on the Unstructured Document Indexing Pipeline**:
1. **Unstructured Legal Documents (Critical Path for Indexing)**:
   - Legal data rooms contain heterogeneous unstructured files: multi-hundred-page executed PDFs, hierarchical Word (`.docx`) agreements with 15-year multi-level numbering, financial waterfall charts, corporate org/blocker diagrams, and scanned wet-ink signature/wire exhibits.
   - To make **Tabular Analysis Grids (`UC-5`)**, **Side-by-Side Pin-Cites (`UC-3`)**, and **Cross-Matter Precedent Search (`UC-7`)** accurate, these unstructured files must go through layout-aware clause segmentation, bounding-box (`bbox`) coordinate extraction, Client-Matter Number (`CMN`) + Intapp Ethical Wall tagging, `3072-dim` vector embedding, and `TOKENLIST` full-text indexing in Cloud Spanner.
2. **Communication & Transactional Sources (Email, Calendar, Chat — Evaluating Direct API vs. Indexing)**:
   - For high-volume operational channels like **Email (~150M M365/Workspace messages), Calendar (`.ics` / Exchange / Google Calendar), and Chat**, full-corpus vector indexing is often unnecessary and cost-prohibitive.
   - We are actively evaluating **when to call their APIs directly at runtime** (via Federated MCP / Microsoft Graph / Google Workspace APIs for live inbox triage, calendar conflict resolution, and chat lookups) versus **lightweight metadata/entity graphing in Spanner** (storing only `Sender`, `Recipient`, `CMN`, and attachment pointers without embedding raw message bodies).

---

## 2. High-Level Design (HLD) — End-to-End Enterprise Legal Platform Architecture

![Weil Enterprise Legal AI High-Level Design (HLD)](./docs/diagrams/01_weil_hld_end_to_end_architecture.svg)

```mermaid
flowchart TB
    subgraph SOURCES["1. Enterprise Data Sources (Unstructured vs. Direct API Channels)"]
        UNSTRUCT["Unstructured Deal & Precedent Corpus<br/>• Executed PDFs (SPA, Credit, LPA)<br/>• Word Contracts (.docx 15-yr Numbering)<br/>• Financial Charts, Org Diagrams & Wet-Ink Scans"]
        META["Structured Deal & Governance Metadata<br/>• Client-Matter Numbers (CMN)<br/>• Intapp Ethical Walls (Allow/Deny)<br/>• Homegrown Apps (FundGen, FundHQ, Antitrust)"]
        COMMS["Communication & Schedule Channels<br/>• Email (Exchange / Workspace BCP)<br/>• Calendar (Outlook / Google Calendar)<br/>• Enterprise Chat & Collaborations"]
    end

    subgraph PIPELINE["2. Data Ingestion vs. Direct API Routing Layer"]
        UNSTRUCT --> DOCPARSE["Unstructured Multimodal Indexing Pipeline<br/>• Layout & Clause Tree Parser + BBox Pin-Cites<br/>• 2-Pass Chart/Diagram/OCR Extractor (docparse)<br/>• Vertex AI gemini-embedding-001 (3072-Dim)"]
        META --> CDC["Metadata & Intapp Wall Sync<br/>• Matter-Bounded & Cross-Matter Tags<br/>• Screen-Before-Rank ACL Tokens"]
        COMMS --> API_EVAL{"Evaluation Gate:<br/>Direct API vs. Index?"}
        API_EVAL -- "Live Triage, Schedule & Chat Lookups" --> DIRECT_API["Direct Runtime API / Federated MCP<br/>(Zero Vector Indexing Overhead)"]
        API_EVAL -- "Deal Attachments & CMN Entity Links" --> DOCPARSE
    end

    subgraph STORAGE["3. Unified Cloud Spanner Hybrid GraphRAG (weil-legal-spanner)"]
        DOCPARSE --> SPANNER[("Cloud Spanner: WeilLegalGraph<br/>• Relational: Matters, Documents, Clauses<br/>• Vector: ARRAY&lt;FLOAT32&gt;(3072) Cosine<br/>• Lexical: ClauseFtsIndex (TOKENLIST BM25)<br/>• Graph: ISO GQL (CITES_PRECEDENT, INTAPP_WALL)")]
        CDC --> SPANNER
        SPANNER --> RRF["Screen-Before-Rank + 3-Way Hybrid RRF Engine<br/>Gate 0: Intapp Wall Pre-Filter -> Vector + BM25 + Graph"]
    end

    subgraph RUNTIME["4. Google Cloud Agent Platform & Gemini Enterprise MCP Apps (SEP-1865)"]
        RRF --> GATEWAY["Agent Registry + Agent Gateway (SPIFFE mTLS / IAP)<br/>+ Google ADK (gemini-3.8-flash) Multi-Agent Orchestrator"]
        DIRECT_API --> GATEWAY
        GATEWAY --> S1["Studio 1: Mike OSS Tabular Grid & Pin-Cite (UC-3, UC-5, UC-6)"]
        GATEWAY --> S2["Studio 2: Redline & Word Legal Legos (UC-1, UC-2)"]
        GATEWAY --> S3["Studio 3: FundGen, FundHQ MFN & Antitrust HSR (UC-6)"]
        GATEWAY --> S4["Studio 4: Intapp Ethical Wall & Spanner Graph (UC-7, UC-8)"]
        GATEWAY --> S5["Studio 5: Partner Inbox & Calendar Triage (UC-4)"]
    end
```

```text
┌────────────────────────────────────────────────────────────────────────────┐
│      HIGH-LEVEL DESIGN (HLD): WEIL ENTERPRISE LEGAL AI PLATFORM (GCP)      │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  [A. DATA SOURCES]                                                         │
│   ├── Path 1 (Unstructured Docs): PDFs, .docx, Charts, Diagrams, Scans     │
│   ├── Path 2 (Governance/Apps):   Intapp Walls, CMN Metadata, FundGen/HQ   │
│   └── Path 3 (Email/Cal/Chat):    Evaluating Direct API vs. Graph Metadata │
│                                    │                                       │
│                                    ▼                                       │
│  [B. UNSTRUCTURED INDEXING PIPELINE vs. DIRECT API FEDERATION]             │
│   ├── Unstructured Pipeline (CRITICAL PATH FOR MVP):                       │
│   │   • Clause/Section Hierarchy + Page/BBox Pin-Cite Extraction           │
│   │   • Multimodal 2-Pass Chart, Table, Org-Diagram & Signature OCR        │
│   │   • 3072-Dim gemini-embedding-001 + TOKENLIST Full-Text Tokenization   │
│   └── Direct API / Federated MCP (Email, Calendar, Chat):                  │
│       • Live runtime API calls for schedule conflicts, inbox triage & chat │
│       • Avoids indexing/embedding 150M+ raw emails                         │
│                                    │                                       │
│                                    ▼                                       │
│  [C. CLOUD SPANNER HYBRID GRAPHRAG (weil-legal-spanner / WeilLegalGraph)]  │
│   ├── Gate 0: Screen-Before-Rank Intapp Ethical Wall & TeammateGrants      │
│   └── 3-Way Hybrid RRF: Vector (Cosine) + Lexical (BM25) + ISO GQL Graph   │
│                                    │                                       │
│                                    ▼                                       │
│  [D. GEMINI ENTERPRISE + 5 CUSTOM MCP APP STUDIOS (SEP-1865 / Cloud Run)]  │
│   ├── Studio 1: Mike OSS Tabular Analysis Grid & Pin-Cite Reader (UC-3/5/6)│
│   ├── Studio 2: Deterministic Redline & Word Legal Legos Studio (UC-1/2)   │
│   ├── Studio 3: FundGen / FundHQ MFN & Antitrust HSR Lab (UC-6)            │
│   ├── Studio 4: Intapp Ethical Wall, CMN Switcher & Graph Studio (UC-7/8)  │
│   └── Studio 5: Partner Deal Inbox & Calendar Triage Studio (UC-4)         │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Low-Level Design (LLD-1) — Unstructured Multimodal Document Indexing Pipeline

![Weil Low-Level Design: Unstructured Indexing Pipeline vs. Direct API Evaluation](./docs/diagrams/02_weil_lld_unstructured_indexing_vs_direct_api.svg)

Because legal diligence requires **exact verbatim clause pin-citing (`bbox` + page + hierarchical section)** across heterogeneous data rooms, the unstructured indexing pipeline is the primary technical dependency for moving from sample data to production data rooms:

```mermaid
sequenceDiagram
    autonumber
    participant GCS as GCS / Temporary Matter Bucket<br/>(PDF, .docx, PNG, Scans)
    participant PARSER as Multimodal Extractor (docparse)<br/>(Layout + 2-Pass Gemini 3.8 Flash)
    participant EMB as Vertex AI Embeddings<br/>(gemini-embedding-001 3072-D)
    participant SPANNER as Cloud Spanner (WeilLegalGraph)<br/>Relational + Vector + FTS + Graph
    participant GE as Gemini Enterprise MCP App<br/>(Tabular Grid & Pin-Cite UI)

    GCS->>PARSER: 1. Ingest Unstructured File + Matter ID (CMN)
    alt Executed PDF or Word (.docx)
        PARSER->>PARSER: Extract 15-yr Legal Numbering Tree (ARTICLE / Section 8.02(b)) + Page BBox
    else Financial Chart / Waterfall (PDF/PNG)
        PARSER->>PARSER: Pass 1: Extract ChartSchemaOnly (Axes, Units, Series)<br/>Pass 2: Extract ChartData + Sum-to-Total Verification
    else Corporate Org Diagram / Wet-Ink Scan
        PARSER->>PARSER: Extract Entity Blocker Graph (Mermaid/JSON) + Signatory/Wire OCR
    end
    PARSER->>EMB: 2. Batch Embed Clause Chunks (task_type=RETRIEVAL_DOCUMENT, 3072-dim)
    EMB-->>PARSER: Normalized FLOAT32[3072] Vectors
    PARSER->>SPANNER: 3. Upsert Documents, Clauses, TOKENLIST & ISO GQL Edges (BelongsToMatter, CitesPrecedent)
    GE->>SPANNER: 4. Query Grid Cell / Citation (with Lawyer ID & Active CMN)
    SPANNER->>SPANNER: 5. Enforce IntappWalls (Screen-Before-Rank) -> Run 3-Way Hybrid RRF
    SPANNER-->>GE: 6. Return Grounded Cell Answer + Verbatim Pin-Cite BBox & Page Highlight
```

---

## 4. Low-Level Design (LLD-2) — Direct API vs. Selective Indexing for Email, Calendar & Chat

For non-document channels (**Email, Calendar, Chat**), we are evaluating a **two-tier hybrid pattern** so we do not block the MVP or incur unnecessary indexing costs on ~150M messages:

| Data Source | Option A: Direct Runtime API / Federated MCP *(Preferred for Live Operations)* | Option B: Selective Metadata Graphing in Spanner *(Only for Deal Provenance)* | Why We Are Evaluating Both |
| :--- | :--- | :--- | :--- |
| **Email** *(Exchange / Workspace BCP)* | Query live inbox threads, unread partner requests, and recent deal correspondence on demand via **Exchange / Workspace MCP APIs** at runtime. | Extract **only** envelope metadata (`sender`, `recipient`, `CMN`, `timestamp`, and attachment GCS pointers) into Spanner Graph (`Emails` + `TeammateGrants`) **without vector-embedding 150M email bodies**. Only attachments promoted to a deal room enter the unstructured indexing pipeline. | Eliminates massive vector storage/embedding cost while preserving cross-matter relationship discovery and 30-day unfiled email grants (`EM-9901`). |
| **Calendar** *(Outlook / Google Calendar `.ics`)* | Call **Calendar APIs directly at runtime** (`freeBusy`, event list, conflict detection, delegation) when triaging partner schedules (`CAL-101`). | No bulk vector indexing needed; calendar events are ephemeral time-window lookups best served by direct API calls. | Zero reason to vector-index calendar invites when live API lookups return exact conflict windows in `<100ms`. |
| **Chat** *(Google Chat / Teams)* | Call **Chat MCP / Graph APIs directly at runtime** for live workspace thread lookups and action-item extraction. | Optional lightweight link persistence only when a chat thread is explicitly pinned to a Client-Matter Number (`CMN`). | Keeps chat ephemeral and compliant with court-ordered matter deletion/retention rules. |

---

## 5. Low-Level Design (LLD-3) — All 8 Legal Use Cases, Architecture & Live Cloud Run Demos

![Weil Low-Level Design: 8 Legal Use Cases Mapped to 5 Gemini Enterprise MCP App Studios](./docs/diagrams/03_weil_lld_8_use_cases_5_studios_matrix.svg)

All **8 Use Cases** from the Weil Executive Blueprint are implemented across **5 dedicated, single-purpose Cloud Run Custom MCP App Studios (`SEP-1865`)**, wired into Gemini Enterprise (`weil-legal-spanner-ge`) and backed by Cloud Spanner (`weil-legal-spanner`):

| Use Case # | Capability Name | MVP Pillar | Dedicated Cloud Run MCP App URL | Gemini Enterprise MCP DataStore ID |
| :-: | :--- | :---: | :--- | :--- |
| **UC-1** | **Document Redlining & Playbook Deviation** | Match & Exceed | [`weil-redline-word-agent`](https://weil-redline-word-agent-254356041555.us-central1.run.app) | `weil-redline-legos-mcp_mcp_data` |
| **UC-2** | **Integrated Word Processing & Privacy Pro "Legal Legos"** | Match & Everyday | [`weil-redline-word-agent`](https://weil-redline-word-agent-254356041555.us-central1.run.app) | `weil-redline-legos-mcp_mcp_data` |
| **UC-3** | **Side-by-Side Pin-Cite Citation Review (★ Priority)** | Match & Exceed | [`mike-gcp-platform`](https://mike-gcp-platform-254356041555.us-central1.run.app) | `mike-oss-legal-grid-mcp_mcp_data` |
| **UC-4** | **Email, Calendar & Chat Triage Automation** | Everyday | [`weil-inbox-calendar-agent`](https://weil-inbox-calendar-agent-254356041555.us-central1.run.app) | `weil-inbox-calendar-mcp_mcp_data` |
| **UC-5** | **Multi-Document Tabular Analysis Grids (★ Priority)** | Match & Exceed | [`mike-gcp-platform`](https://mike-gcp-platform-254356041555.us-central1.run.app) | `mike-oss-legal-grid-mcp_mcp_data` |
| **UC-6** | **Workflow & Grid Builder + FundGen / FundHQ / Antitrust** | Migrate & Exceed | [`weil-funds-antitrust-agent`](https://weil-funds-antitrust-agent-254356041555.us-central1.run.app) | `weil-funds-antitrust-mcp_mcp_data` |
| **UC-7** | **Matter & Knowledge Workspaces (Cross-Matter GraphRAG)** | Migrate & Exceed | [`weil-governance-wall-agent`](https://weil-governance-wall-agent-254356041555.us-central1.run.app) | `weil-intapp-wall-graph-mcp_mcp_data` |
| **UC-8** | **Dynamic Client-Matter Tracking & Intapp Ethical Walls** | Exceed & Everyday | [`weil-governance-wall-agent`](https://weil-governance-wall-agent-254356041555.us-central1.run.app) | `weil-intapp-wall-graph-mcp_mcp_data` |

---

### UC-1: Document Redlining & Playbook Deviation Analysis
* **Live Demo**: [`https://weil-redline-word-agent-254356041555.us-central1.run.app`](https://weil-redline-word-agent-254356041555.us-central1.run.app)
* **Low-Level Design**:
  * Ingests opposing counsel markups (`.docx` / PDF pairs, e.g., *Brightwater Merger Agreement Weil v3 vs. Skadden v4*), computes deterministic word-level `<del>`/`<ins>` diffs, and benchmarks deviations against historical precedent caps in Cloud Spanner (`M-215` Project Kestrel & `M-518` Project Vanguard).
  * Renders interactive `EditCardUI` cards allowing counsel to `Accept Weil v3`, `Reject Markup`, or inspect Playbook risk flags.

![UC-1 & UC-2 Redline and Legal Legos Studio](./docs/screenshots_v3/v3_studio2_redline_1440px.png)

---

### UC-2: Integrated Word Processing & Privacy Pro "Legal Legos" (`.docx`)
* **Live Demo**: [`https://weil-redline-word-agent-254356041555.us-central1.run.app`](https://weil-redline-word-agent-254356041555.us-central1.run.app)
* **Low-Level Design**:
  * Preserves 15-year multi-level legal numbering (`ARTICLE I`, `Section 8.02(b)`) across OpenXML `.docx` files.
  * Implements Weil's **Privacy Pro ("Legal Legos")** modular clause assembly engine (GDPR Art. 28, CCPA/CPRA, EU AI Act High-Risk Annex III, and FormSpec v06 NDA riders) with live `.docx` binary generation (`GET /api/legal-legos/docx`).

---

### UC-3: Side-by-Side Pin-Cite Citation Review (★ Priority)
* **Live Demo**: [`https://mike-gcp-platform-254356041555.us-central1.run.app`](https://mike-gcp-platform-254356041555.us-central1.run.app)
* **Low-Level Design**:
  * Shared subroutine (`CUJ-4`) invoked from any Analysis Grid cell or Red-Flag Memo citation.
  * Clicking a numbered `CitationPillUI` badge opens the right-hand `EB Garamond` contract reader at `<15ms`, scrolls directly to the cited page and section (`bbox_json`), highlights the verbatim grounding clause in yellow, and supports instant row-to-row (`↑`/`↓`) navigation and original file download.

![UC-3 & UC-5 Mike OSS Tabular Diligence Grid & Pin-Cite Reader](./docs/screenshots_v3/v3_studio1_tabular_1440px.png)

---

### UC-4: Email, Calendar & Chat Triage Automation (Direct API vs. Graph Evaluation)
* **Live Demo**: [`https://weil-inbox-calendar-agent-254356041555.us-central1.run.app`](https://weil-inbox-calendar-agent-254356041555.us-central1.run.app)
* **Low-Level Design**:
  * Triages partner deal emails (`EM-9901..9903`) by matching sender/recipient and attachment context to active Client-Matter Numbers (`CMN`), staging 1-tap `Approve & File to iManage` actions.
  * Detects hard calendar overlaps (`CAL-101`: *Brightwater Board SPA Approval Call* vs. *FTC HSR Second Request Meet & Confer*) via direct Calendar API / `.ics` inspection and executes 1-tap partner delegation.

![UC-4 Partner Deal Inbox & Calendar Triage Studio](./docs/screenshots_v3/v3_studio5_inbox_1440px.png)

---

### UC-5: Multi-Document Tabular Analysis Grids (★ Priority — Mike OSS in GE)
* **Live Demo**: [`https://mike-gcp-platform-254356041555.us-central1.run.app`](https://mike-gcp-platform-254356041555.us-central1.run.app)
* **Low-Level Design**:
  * Adapts the open-source **Mike OSS** tabular review experience inside Gemini Enterprise (`SEP-1865` `ui://mike-gcp/workspace.html`).
  * Populates rows from matter-bounded data rooms (`Path A`) or cross-matter Spanner metadata queries (`Path B / CUJ-0`), executes parallel `gemini-3.8-flash` cell extraction when users click `+ Add column`, supports cell validation/locking (`CUJ-2`), and synthesizes Red-Flag diligence memos (`CUJ-3`).

![Live Parallel Column Extraction Inside Gemini Enterprise Sandboxed Iframe](./docs/screenshots_v3/live_title_column_verified.png)

---

### UC-6: Self-Service Workflow & Grid Builder + Homegrown Apps (`FundGen`, `FundHQ`, Antitrust)
* **Live Demo**: [`https://weil-funds-antitrust-agent-254356041555.us-central1.run.app`](https://weil-funds-antitrust-agent-254356041555.us-central1.run.app)
* **Low-Level Design**:
  * Demonstrates the GCP modernization path for Weil's homegrown Private Funds and Antitrust applications (**`FundGen`** LPA drafter, **`FundHQ`** LP Side-Letter Most-Favored-Nation [MFN] compendium, and **Antitrust HSR HHI** market-concentration simulator) alongside multimodal extraction of financial waterfall charts (`DOC-CHART-01/02`), J.Crew blocker org diagrams (`DOC-DIAG-01`), and wet-ink wire scans (`DOC-SCAN-01`).

![UC-6 FundGen, FundHQ MFN & Antitrust HSR Lab](./docs/screenshots_v3/v3_studio3_funds_1440px.png)

---

### UC-7: Matter & Knowledge Workspaces (Cross-Matter Precedent GraphRAG)
* **Live Demo**: [`https://weil-governance-wall-agent-254356041555.us-central1.run.app`](https://weil-governance-wall-agent-254356041555.us-central1.run.app)
* **Low-Level Design**:
  * Implements **CUJ-0 (Cross-Matter Set Assembly)** and precedent graph traversal over Cloud Spanner (`CREATE PROPERTY GRAPH WeilLegalGraph`) combining `COSINE_DISTANCE` (3072-dim embeddings), `SEARCH(clause_tokens)` (BM25), and ISO GQL multi-hop edges (`(m:Matter)-[:CITES_PRECEDENT]->(d:Document)-[:CONTAINS_CLAUSE]->(c:Clause)`).

---

### UC-8: Dynamic Client-Matter Tracking (CMN Context Switcher & Intapp Ethical Walls)
* **Live Demo**: [`https://weil-governance-wall-agent-254356041555.us-central1.run.app`](https://weil-governance-wall-agent-254356041555.us-central1.run.app)
* **Low-Level Design**:
  * Binds every query and grid session to an active **Client-Matter Number (`CMN`)** and attorney identity (`L-001`..`L-005`).
  * Enforces **Intapp Ethical Walls (`Screen-Before-Rank`)** inside Cloud Spanner *before* vector or keyword scoring—mathematically blocking walled attorneys (`L-001` Sarah Jenkins) from restricted matters (`M-999` *Project Omega*) while managing 30-day `TeammateGrants` for unfiled deal emails (`EM-9901`).

![UC-7 & UC-8 Intapp Ethical Wall & Cloud Spanner Graph Studio](./docs/screenshots_v3/v3_studio4_governance_1440px.png)
