# Weil, Gotshal & Manges LLP — Unified Enterprise Legal AI Architecture, Use-Case Mapping & Multi-Agent Demo Blueprint

**Prepared for:** Weil Executive & Technical Leadership (`Daulton Cockerell`, `Andrew Simon`, `Ian Miller`, `Steve Kedem`, `charlie@mikeoss.com`) & Google Cloud North AI Practice CEs / FDEs  
**GCP Project:** `vtxdemos` (`254356041555`) | **Primary Region:** `us-central1` | **Vertex AI Model Tier:** `gemini-3.8-flash` (`location="global"`) & `gemini-3.7-flash`  
**Spanner Instance / DB:** `weil-legal-spanner` / `weil-legal-context` (`WeilLegalGraph` ISO GQL + `3,072-dim gemini-embedding-2` + `TOKENLIST` BM25)  
**Gemini Enterprise Engines:** `weil-legal-spanner-ge` & `gemini-enterprise-17877637_1787763712023`

---

## 1. Executive Summary & Audit of Existing Deployments

Across our Cloudtop (`~/vertex-ai-samples`), Mac history (`jetski-history-mcp` + Firestore `vtxdemos.weil_memory_bank`), and live Google Cloud project `vtxdemos` (`254356041555`), we have built and verified the foundational components of Weil's enterprise legal platform. This document consolidates all internal intelligence, maps every legacy/competitor/homegrown application to the canonical **December MVP 4-Pillar Scope** and **2x4 Bento UX Capabilities**, and defines the upgraded **46-Document Multimodal GraphRAG + Google Cloud Agent Platform (Agent Registry + Agent Gateway + Agent Identity) + Google ADK (`gemini-3.8-flash`) Multi-Agent Architecture**.

### 1.1 Live Deployed Infrastructure Inventory (`vtxdemos`)

| Layer | Resource Name / Service ID | Live Endpoint / URI | Current Status & Role |
| :--- | :--- | :--- | :--- |
| **Cloud Spanner GraphRAG** | `weil-legal-spanner` / `weil-legal-context` | `projects/vtxdemos/instances/weil-legal-spanner/databases/weil-legal-context` | **READY (100 PU)**. Hosts `WeilLegalGraph` ISO GQL Property Graph (`Matters`, `Documents`, `Clauses`, `DocumentChunks`, `Emails`, `Lawyers`, `Clients`, `IntappWalls`, `TeammateGrants`, `CitesPrecedent`, `ContainsClause`, `BelongsToMatter`), `ClauseFtsIndex` (`TOKENLIST`), and `ARRAY<FLOAT32>(3072)` vectors. |
| **Mike OSS Cloud Platform** | `mike-gcp-platform` | `https://mike-gcp-platform-254356041555.us-central1.run.app` | **LIVE**. Faithful Mike OSS UI (EB Garamond, 12-Blade Liquid Glass Aperture, View 1 Assistant Home, View 2 Project Kestrel Cockpit, View 3 Split Tabular Diligence Grid & Yellow Pin-Cite Lightbox) + Streamable HTTP MCP (`POST /mcp`, `SEP-1865`). |
| **Interactive Legal Grid MCP** | `weil-legal-grid-mcp-agent` | `https://weil-legal-grid-mcp-agent-254356041555.us-central1.run.app` | **LIVE**. Dual-protocol A2A v0.9 (`Canvas`/`IFrameSrcdoc`) + Streamable HTTP MCP (`SEP-1865`) server wired to `weil-legal-spanner`. |
| **A2UI Visual Command Agent** | `weil-legal-a2ui-agent` | `https://weil-legal-a2ui-agent-254356041555.us-central1.run.app` | **LIVE**. A2UI v0.9/v0.8 Composite Catalog visual command matrix agent registered in Gemini Enterprise. |
| **A2UI v0.9 Composite Lab** | `weil-a2ui-v09-composite-lab` | `https://weil-a2ui-v09-composite-lab-254356041555.us-central1.run.app` | **LIVE**. ADK + Spanner A2UI v0.9 Composite Catalog sandbox. |
| **Multimodal PDF Extractor** | `docparse` & `docparse-firestore-mcp` | `https://docparse-254356041555.us-central1.run.app` | **LIVE**. Storm-proof Cloud Run + Cloud Tasks multimodal PDF-to-Markdown extractor (2-pass Chart schema+values, Table, Diagram, Photo, and bbox OCR). |
| **Agent Gateway & Identity** | `my-agent-gateway` & `agent-gateway-demo-mcp` | `projects/254356041555/locations/us-central1/agentGateways/my-agent-gateway` | **LIVE**. Google-managed `AGENT_TO_ANYWHERE` MCP gateway wired to `agentregistry.googleapis.com/v1alpha` with SPIFFE mTLS (`X-Agent-Spiffe-Id`), IAP `roles/iap.egressor` (`mcp.resourceName`), and 3LO Auth Manager. |
| **Gemini Enterprise Engine** | `weil-legal-spanner-ge` | `.../engines/weil-legal-spanner-ge` | **LIVE**. Hosts 6 registered agents including Agent `15772991373490104507` (*Mike OSS Diligence Cockpit*), Agent `16587642138788275169` (*Weil Interactive Legal Grid*), Agent `12034191125081164529` (*Spanner Graph ADK*), and Custom MCP DataStore `weil-legal-grid-mcp-app_mcp_data`. |

---

## 2. Canonical Slide Deck Use Cases & Application Mapping

From our two executive presentation decks—**Deck 1: *Legal Platform with Gemini Enterprise*** (Drive ID `1ESjepfG-JEVZ_y_IiRZlEUXRcg54yBF4RhViY8B6xQ0`, Slides 2 & 3) and **Deck 2: *Weil Enterprise Legal Data & AI Architecture*** (Drive ID `1D-2Y-VPpTWPPLNbrmRuAaYNv4n_WyrDzT9ly_s8WC64`, Slides 1–8)—plus Daulton Cockerell's Oct 7–13 workstream emails, here is the complete mapping of Weil's existing 3rd-party and homegrown tools to our Google Cloud architecture:

### 2.1 Slide 3 — The 8 UX-Enabled Bento Capabilities vs. Existing Tools & New ADK Agents

| # | Bento UX Capability (Slide 3) | MVP Pillar (Slide 2) | Existing 3P / Homegrown Tools Used at Weil | What We Built & Upgraded in This Demo | Dedicated UI Surface (`SEP-1865` & Web) |
| :-: | :--- | :--- | :--- | :--- | :--- |
| **1** | **Document Redlining** *(Automated comparison, risk flagging & Playbook deviation analysis)* | **Match** & **Exceed** | • **Syntheia Compare MCP** (Horace Wu, Oct 7 intro)<br>• **Litera Compare**<br>• **Draftable Legal**<br>• **Super Comparer / LEA Compare** | **`redline_word_composer_agent`** (`gemini-3.8-flash`): Deterministic word-level `<del>`/`<ins>` diff engine + Playbook risk evaluator benchmarking opposing counsel markups (e.g., Skadden v4 0.25% cap vs. Weil v3 0.75% cap) against Kestrel (`M-215`) & Vanguard (`M-518`) precedents in Spanner. | `/ui/redline-studio`<br>`ui://mike-gcp/redline-studio.html` |
| **2** | **Integrated Word Processing** *(Direct drafting, clause replacement & formatting inside docs)* | **Match** & **Everyday** | • **Microsoft Word (`.docx`) + Google Drive for Desktop (`G:\`)**<br>• **Weil Privacy Pro ("Legal Legos")**<br>• **NDA FormSpec Induction Engine** | **`redline_word_composer_agent`**: Preserves 15-year multi-level legal numbering (`ARTICLE I`, `Section 8.02(b)`) across `.docx` exports and assembles modular **Privacy Pro "Legal Legos"** (GDPR, CCPA, EU AI Act) & **FormSpec v06 NDA** riders. | `/ui/redline-studio`<br>`ui://mike-gcp/redline-studio.html` |
| **3** | **Side-by-Side Citation Review ★ PRIORITY** *(Split-screen verification with direct links to source evidence)* | **Match** & **Exceed** | • **Mike OSS (`mikeoss.com`)**<br>• **DeepJudge**<br>• **Harvey** | **`mike_tabular_diligence_agent`**: Instant `<15ms` pin-cite drawer jumping directly to exact contract page & bounding box (`bbox_json`), highlighting the verbatim provision in yellow with NLI entailment verification and Redline overlay toggle. | `/` & `/ui/mike-cockpit`<br>`ui://mike-gcp/workspace.html` |
| **4** | **Email & Calendar Automation** *(Context-aware communication triage & conflict resolution)* | **Everyday** | • **Microsoft Outlook / Exchange (O365)**<br>• **Claude CoWork**<br>• **Partner iPad Workflows** | **`inbox_calendar_triage_agent`**: Triages unfiled partner deal emails (`EM-9901..9903`), cross-references active closing checklists, resolves calendar conflicts (`CAL-101` Board Call vs. FTC HSR Second Request Hearing), and provides a Partner iPad 1-tap sign-off queue. | `/ui/inbox-calendar`<br>`ui://mike-gcp/inbox-calendar.html` |
| **5** | **Document Analysis Grids ★ PRIORITY** *(Multi-doc tabular extraction & structured comparison)* | **Match** & **Exceed** | • **Mike OSS (`mikeoss.com`)**<br>• **Harvey Vaults**<br>• **Legora** | **`mike_tabular_diligence_agent`**: Full Mike OSS Project Kestrel Cockpit & Split Tabular Review Grid scaling across **46 multimodal files** (`M-331`, `M-801`, `M-902`, `M-610`, `M-720`, etc.) with live `+ Add Column` parallel `gemini-3.8-flash` extraction, per-column filters, and `[x]` row scoping. | `/` & `/ui/mike-cockpit`<br>`ui://mike-gcp/workspace.html` |
| **6** | **Workflow & Grid Builder** *(Self-service creation of custom review templates & agent steps)* | **Migrate** & **Exceed** | • **Claude CoWork / Claude Projects**<br>• **ChatGPT Enterprise Custom GPTs**<br>• **Harvey Custom Workflows** | **`mike_tabular_diligence_agent` + `private_funds_antitrust_agent`**: 1-click Playbook & Grid Template Builder importing legacy Harvey/Claude prompts and powering Weil's homegrown **`FundGen`** (LPA generator), **`FundHQ`** (LP MFN Side-Letter matrix), and **Antitrust HSR HHI** calculators. | `/ui/funds-antitrust`<br>`ui://mike-gcp/funds-antitrust.html` |
| **7** | **Matter & Knowledge Workspaces** *(Centralized repositories for matter files & firm know-how)* | **Migrate** & **Exceed** | • **iManage DMS + HYCU R-Serve**<br>• **SharePoint Online/On-Prem (O365 BCP)**<br>• **Weil BenchMark (LASER) & SCS Platform** | **`ethical_wall_cmn_governance_agent`**: Unified Cloud Spanner Hybrid GraphRAG (`WeilLegalGraph`) indexing iManage/SharePoint/GCS documents, visual charts, and precedents with cross-matter citation edges (`CITES_PRECEDENT`). | `/ui/governance-wall`<br>`ui://mike-gcp/governance-wall.html` |
| **8** | **Dynamic Client Matter Tracking** *(Real-time context switching & automated billing/governance alignment)* | **Exceed** & **Everyday** | • **Intapp Walls (SQL Server CDC)**<br>• **Outside Counsel Guidelines (OCG)**<br>• **iManage Matter Workspaces** | **`ethical_wall_cmn_governance_agent`**: Real-time Client Matter Number (`CMN`) context switcher enforcing **Intapp Ethical Walls (`Screen-Before-Rank`)** (blocking `L-001` from `M-999` Project Omega), OCG AI model allowlists, and 30-day **`TeammateGrants`** (`EM-9901`). | `/ui/governance-wall`<br>`ui://mike-gcp/governance-wall.html` |

---

## 3. End-to-End Scalable Architecture (Step 1 -> Step 4)

```text
┌────────────────────────────────────────────────────────────────────────────┐
│    STEP 1: MULTIMODAL EXTRACTION PIPELINE (46+ HETEROGENEOUS LEGAL FILES)  │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  [1.1 Raw Multi-Format Deal & Firm Corpus (46 Files across 14 Matters)]    │
│   ├── 30 Executed Legal PDFs (M&A, Credit, Real Estate, IP/Tech, Emp)      │
│   │   • Includes FundGen LPA (DOC-FUND-01), FundHQ MFN (DOC-FUND-02),      │
│   │     Antitrust HSR Filing (DOC-HSR-01) & Privacy Pro DPA (DOC-PRIV-01)  │
│   ├── 4 Visual Charts, Org Diagrams & Scanned Signatures (PDF + PNG)       │
│   │   • Brightwater EBITDA Bridge & Waterfall (DOC-CHART-01)               │
│   │   • Corporate Org Chart & J.Crew IP Blocker Boundary (DOC-DIAG-01)     │
│   │   • Scanned Wet-Ink Escrow Signature & Citibank Wire (DOC-SCAN-01)     │
│   │   • Private Funds LP Commitment Fee Step-Down Curve (DOC-CHART-02)     │
│   ├── 8 Hierarchical Word Contracts & Redline Pairs (.docx)                │
│   │   • Project Kestrel 01..06 .docx + Weil v3 vs Skadden v4 Redline .docx │
│   └── 4 Partner Emails (.eml) & Calendar Conflict Invites (.ics)           │
│       • EM-9901 (338h10 Tax), EM-9902 (Skadden Markup), EM-9903, CAL-101   │
│                                    │                                       │
│                                    ▼                                       │
│  [1.2 Multimodal Region & Clause Extractor (docparse + Layout Parser)]     │
│   ├── Text & Clause Hierarchy: Section regex + .docx 15-yr numbering tree  │
│   ├── Visual Charts (2-Pass): Flash (ChartSchemaOnly) -> Pro (ChartData)   │
│   ├── Tables & Waterfalls: Schema-constrained Markdown + JSON TableData    │
│   ├── Corporate Org Diagrams: Mermaid + Entity Firewall Prose (DiagramData)│
│   └── Scanned Signatures / Exhibits: Bounding-Box OCR + PhotoCaption       │
└────────────────────────────────────┬───────────────────────────────────────┘
                                     │
                                     ▼
┌────────────────────────────────────────────────────────────────────────────┐
│  STEP 2: METADATA, 3072-DIM EMBEDDINGS & CLOUD SPANNER PROPERTY GRAPH      │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  [2.1 Cloud Spanner Instance: weil-legal-spanner / weil-legal-context]     │
│   ├── Relational Nodes: Clients, Matters (14), Lawyers, Documents (46+),   │
│   │                     Clauses (60+), DocumentChunks, Emails              │
│   ├── Governance Tables: IntappWalls (Deny/Allow), TeammateGrants (30d TTL)│
│   ├── Dense Vector Index: embedding ARRAY<FLOAT32>(vector_length=>3072)    │
│   │                       via Vertex AI gemini-embedding-2 (L2 normalized) │
│   ├── Sparse Keyword Index: SEARCH INDEX ClauseFtsIndex (TOKENLIST BM25)   │
│   └── ISO GQL Property Graph: CREATE PROPERTY GRAPH WeilLegalGraph         │
│       • Edges: BELONGS_TO_MATTER, CONTAINS_CLAUSE, CITES_PRECEDENT,        │
│                INTAPP_WALL, TEAMMATE_GRANT, WORKED_ON                      │
│                                    │                                       │
│                                    ▼                                       │
│  [2.2 Screen-Before-Rank + 3-Way Hybrid RRF & Graph Traversal Engine]      │
│   ├── Gate 0 (Pre-Filter): Filter out IntappWalls DENY & ungranted emails  │
│   ├── Leg 1 (Semantic): COSINE_DISTANCE(embedding, @q_vec) -> rank_vec     │
│   ├── Leg 2 (Lexical):  SEARCH(clause_tokens, @fts_query)  -> rank_fts     │
│   ├── Leg 3 (Graph):    GQL MATCH (m:Matter)-[:CITES_PRECEDENT]->(d:Doc)   │
│   └── Fusion Score:     RRF = 1/(60 + rank_vec) + 1/(60 + rank_fts) + boost│
└────────────────────────────────────┬───────────────────────────────────────┘
                                     │
                                     ▼
┌────────────────────────────────────────────────────────────────────────────┐
│  STEP 3: GOOGLE CLOUD AGENT PLATFORM, AGENT GATEWAY & MCP SERVER           │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  [3.1 Cloud Run Service: mike-gcp-platform (Streamable HTTP POST /mcp)]    │
│   ├── Registered in Agent Registry:                                        │
│   │   agentregistry.googleapis.com/v1alpha/.../services/weil-legal-mcp     │
│   ├── Governed by Agent Gateway (my-agent-gateway, AGENT_TO_ANYWHERE):     │
│   │   • Door 1: IAP Egressor (roles/iap.egressor + CEL mcp.resourceName)   │
│   │   • Door 2: Agent Identity SPIFFE mTLS (X-Agent-Spiffe-Id) & 3LO Token │
│   ├── OpenTelemetry Cloud Trace: Zero-Content-Leak (NO_CONTENT) spans      │
│   └── 7 MCP Tools + 5 SEP-1865 UI Resources (text/html;profile=mcp-app)    │
└────────────────────────────────────┬───────────────────────────────────────┘
                                     │
                                     ▼
┌────────────────────────────────────────────────────────────────────────────┐
│  STEP 4: GOOGLE ADK (gemini-3.8-flash) MULTI-AGENT SUITE & DEDICATED UIs   │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  [Root ADK Coordinator: weil_root_orchestrator (gemini-3.8-flash, global)] │
│   ├──► Agent 1: mike_tabular_diligence_agent                               │
│   │     • UI: Mike OSS Cockpit & Split Diligence Grid (ui://.../workspace) │
│   ├──► Agent 2: redline_word_composer_agent                                │
│   │     • UI: Syntheia/Litera Redline & Legal Legos (ui://.../redline)     │
│   ├──► Agent 3: private_funds_antitrust_agent                              │
│   │     • UI: FundGen/FundHQ MFN & HSR Chart Lab (ui://.../funds-antitrust)│
│   ├──► Agent 4: ethical_wall_cmn_governance_agent                          │
│   │     • UI: Intapp Wall, CMN Switcher & Graph (ui://.../governance-wall) │
│   └──► Agent 5: inbox_calendar_triage_agent                                │
│         • UI: Partner Inbox, Calendar & iPad Queue (ui://.../inbox-cal)    │
│                                    │                                       │
│                                    ▼                                       │
│  [Plugged into Gemini Enterprise DataStores (custom_mcp + A2A + ADK)]      │
│   ├── Engine 1: weil-legal-spanner-ge (Agent ID 15772991373490104507)      │
│   └── Engine 2: gemini-enterprise-17877637_1787763712023                   │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Deep Dive: Multimodal Extraction Pipeline (`multimodal_extraction_pipeline.py`)

To satisfy the requirement of handling **every document modality across >30 files**, our extraction pipeline combines deterministic layout parsing with `docparse`'s 2-pass visual schema extraction:

1. **Multi-Page Executed Legal PDFs (30 Agreements)**:
   - Extracts page-accurate text layers via `pypdf` / `pypdfium2`, detects hierarchical boundaries (`PREAMBLE`, `RECITALS`, `ARTICLE I..XII`, `SECTION 1.01..19.01`, `SCHEDULE 1.01..6.22`), computes bounding-box coordinates (`bbox_json`), and subdivides long provisions into atomic searchable clauses (`>1,200` clauses).
2. **Visual Charts & Waterfalls (`DOC-CHART-01`, `DOC-CHART-02`)**:
   - Uses a **Two-Pass Chart Extraction Schema** (`ChartSchemaOnly` -> `ChartData`):
     - **Pass 1**: Commits to `chart_type` (`bar`, `line`, `waterfall`), `x_categories`, `series_names` from the legend, and `value_unit` (`$M`, `bps`, `%`).
     - **Pass 2**: Extracts exact numeric series values and literal printed `value_labels` (e.g., `$145.0M GAAP EBITDA`, `+$18.0M Pro Forma Synergies`, `+$12.0M Cleanroom Restructuring`, `$175.0M Consolidated Adjusted EBITDA`), plus runtime validation checks (sum-to-total waterfall verification).
3. **Corporate Org-Structure & Blocker Diagrams (`DOC-DIAG-01`)**:
   - Uses `DiagramData` schema to convert visual entity hierarchy boxes into both a structured graph (`Restricted Subsidiaries` vs. `Unrestricted Subsidiaries` under Section 7.04 J.Crew/Envision Blocker) and clean Markdown prose.
4. **Scanned Wet-Ink Signature Pages & Wire Exhibits (`DOC-SCAN-01`)**:
   - Uses `PhotoCaption` + bounding-box OCR to capture signatory names (`Sarah Jenkins`, `David Vance`), execution timestamps, and Citibank N.A. `$18,000,000` Escrow ABA/SWIFT wire instructions.
5. **Word Processing Agreements & Redline Pairs (`.docx`, 8 Files)**:
   - Parses OpenXML paragraphs while preserving 15-year multi-level legal numbering (`1.01`, `8.02(b)`) and computes deterministic word-level `<del>`/`<ins>` diffs between `07_M331_Brightwater_Merger_Agreement_Weil_v3.docx` and `08_M331_Brightwater_Merger_Agreement_Skadden_v4_Redline.docx`.
6. **Partner Emails & Calendar Invites (`.eml` / `.ics`, 4 Files)**:
   - Extracts sender/recipient lawyer IDs (`L-001`..`L-006`), `matter_id` tags (`M-331`, `M-999`), restricted visibility states (`UNFILED_PRIVATE` requiring 30-day `TeammateGrants`), and `.ics` `VEVENT` time slots (`CAL-101` detecting the overlap between the Brightwater Closing Board Call and the FTC HSR Second Request Meet-and-Confer).

---

## 5. Deep Dive: Security, Agent Registry, Agent Gateway & Agent Identity

Our MCP server (`app.py` + `register_agent_registry.py`) implements the complete Google Cloud Agent Platform governance stack:

1. **Cloud Run -> Agent Registry (`agentregistry.googleapis.com/v1alpha`)**:
   - Registered as an official MCP service (`projects/254356041555/locations/us-central1/services/weil-legal-mcp`) with `protocolBinding: "JSONRPC"` and `mcpServerSpec: {"type": "NO_SPEC"}`.
2. **Agent Gateway (`networkservices.googleapis.com/v1beta1`) — Door 1 (IAP Egressor)**:
   - Bound to `projects/254356041555/locations/us-central1/agentGateways/my-agent-gateway` (`governedAccessPath: "AGENT_TO_ANYWHERE"`, `protocols: ["MCP"]`).
   - Enforces IAM `roles/iap.egressor` conditioned on the CEL expression:
     `resource.type == 'agentregistry.googleapis.com/Service' && mcp.resourceName == 'projects/254356041555/locations/us-central1/services/weil-legal-mcp'`
3. **Agent Identity (`IdentityType.AGENT_IDENTITY`) — Door 2 (Per-Agent SPIFFE mTLS & 3LO Token Injection)**:
   - Extracts and logs `X-Agent-Spiffe-Id` (`spiffe://...`), `X-Agent-Resource` (`projects/254356041555/locations/us-central1/reasoningEngines/...`), and `Authorization: Bearer <token>` injected by Auth Manager (`GcpAuthProviderScheme`).
4. **Spanner `Screen-Before-Rank` Ethical Wall Pre-Filtering**:
   - Every hybrid search (`hybrid_search_legal_graph`) and graph traversal (`traverse_precedent_graph`) executes `IntappWalls` and `TeammateGrants` filtering **before** vector similarity or BM25 scoring. Matter `M-999` (*Project Omega Hostile Takeover Defense*) is mathematically invisible to walled attorneys (`L-001` Sarah Jenkins), and unfiled email `EM-9901` is only included when an active 30-day `TeammateGrants` edge exists.
5. **OpenTelemetry Zero-Leak Tracing (`telemetry.py`)**:
   - Exports spans to Google Cloud Trace with `OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT=NO_CONTENT` so privileged contract text never leaks into operational logs.

---

## 6. Gemini Enterprise Custom MCP App Registration (`SEP-1865`)

To plug the Cloud Run MCP server into Gemini Enterprise DataStores (`weil-legal-spanner-ge` and `gemini-enterprise-17877637_1787763712023`), `register_mike_mcp_connector.py` executes the 3-step `custom_mcp` pipeline recovered from our Mac history:
1. **`setUpDataConnector` (`v1alpha`)**: Creates/updates the `custom_mcp` connector pointing `instance_uri` to `https://mike-gcp-platform-254356041555.us-central1.run.app/mcp` with `connectorModes: ["ACTIONS", "FEDERATED"]` and all 7 MCP tools enabled.
2. **Stubby `RefreshDataConnectorTools`**: Invokes `google.cloud.discoveryengine.v1main.DataConnectorService.RefreshDataConnectorTools` on `blade:cloud-discovery-engine-assistant-data-connector-service-prod-global` to populate `dynamic_tools` in Discovery Engine's Spanner table.
3. **Engine `dataStoreIds` & A2A Agent Card Binding**: Attaches `{collectionId}_mcp_data` to `weil-legal-spanner-ge` and `gemini-enterprise-17877637_1787763712023` and updates Agent `15772991373490104507` (*Mike OSS - Enterprise Legal AI Diligence Cockpit*).
