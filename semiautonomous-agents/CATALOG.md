# Catalog — searchable index

> Every project + the **customer / use case / occasion** that drove it.
> Use `Ctrl-F` for the customer name when you can't remember the generic project codename.
>
> Format per row: **codename** · *one-line pitch* · `customer / context` · `tags`

---

## How to use this file

The public READMEs use neutral codenames so the repo can be shared. **This file is the lookup table** that maps codenames back to the customer or moment that led to them.

When you remember "the Envato thing" but not "multimodal-search", grep this file.

When you start a new project, **add a row here first** — even before the README. The row is what future-you will search for.

---

## Active projects (catalog)

### Stock-media / multimodal search
- [`shutter-vibe-engine/multimodal-search/`](./shutter-vibe-engine/multimodal-search/) — Multimodal vibe search across photos, video, music, SFX, graphics. One query → 5 modalities ranked in a 3072-dim embedding space.
  - **Customer / context:** Envato — EBC briefing 2026-04-29
  - **Tags:** `vertex-vector-search` `gemini-embeddings-2` `multimodal` `eventarc` `cloud-run` `firestore` `astro-starlight`
  - **Live site:** https://jchavezar.github.io/vertex-ai-samples/multimodal-search/

### Enterprise search & portals
- [`sharepoint_wif_portal/`](./sharepoint_wif_portal/) — Reference implementation: Entra ID → Google Cloud, zero credential storage. **Tags:** `wif` `sharepoint` `discovery-engine` `react`
- [`servicedesk-sharepoint-portal/`](./servicedesk-sharepoint-portal/) — SharePoint search + ServiceNow MCP in one agent. **Tags:** `wif` `sharepoint` `servicenow` `mcp`
- [`servicenow-mcp-portal/`](./servicenow-mcp-portal/) — Agent Engine + ServiceNow via MCP, MSAL React frontend. **Tags:** `agent-engine` `servicenow` `msal`
- [`gemini-enterprise-sharepoint-agent/`](./gemini-enterprise-sharepoint-agent/) — ADK agent registered in Gemini Enterprise, SharePoint via WIF. **Tags:** `gemini-enterprise` `adk` `wif`
- [`streamassist-oauth-flow-sharepoint/`](./streamassist-oauth-flow-sharepoint/) — Custom StreamAssist portal with per-user OAuth *(formerly `streamassist-oauth-flow`)*. **Tags:** `streamassist` `oauth` `sharepoint`
- [`outlook-streamassist-oauth-flow/`](./outlook-streamassist-oauth-flow/) — Same shape as above, but for Outlook mail context. **Tags:** `streamassist` `oauth` `outlook`
- [`streamanswer-oauth-flow/`](./streamanswer-oauth-flow/) — Variant of the StreamAssist OAuth pattern. **Tags:** `oauth` `streamanswer`
- [`ge-sharepoint-cloudid/`](./ge-sharepoint-cloudid/) — SharePoint search via Google Cloud Identity (no WIF, no STS). **Tags:** `cloud-id` `sharepoint` `discovery-engine`
- [`cortex-retriever/`](./cortex-retriever/) — Agent-only ADK for Gemini Enterprise — SharePoint + Google. **Tags:** `adk` `gemini-enterprise` `wif`
- [`light_mcp_cloud_portal/`](./light_mcp_cloud_portal/) — Lightweight portal scaffold around MCP cloud APIs. **Tags:** `mcp` `portal` `react`
- [`streamassist-oauth-flow-us/`](./streamassist-oauth-flow-us/) — `us` regional variant of `streamassist-oauth-flow` — Gemini Enterprise + SharePoint federated connector + WIF. **Tags:** `streamassist` `sharepoint` `wif` `discovery-engine` `us-region`
- [`streamassist-oauth-flow-servicenow/`](./streamassist-oauth-flow-servicenow/) — Sister to the SharePoint streamassist projects: same WIF identity chain, **ServiceNow** as the federated source (incidents, KB articles, catalog) with native ServiceNow ACLs. Two frontends shipped (vanilla HTML tester + React/FastAPI). **Tags:** `streamassist` `servicenow` `wif` `discovery-engine` `gemini-enterprise` `oauth`
- [`streamassist-oauth-flow-sharepoint-servicenow/`](./streamassist-oauth-flow-sharepoint-servicenow/) — **Combined portal** — SharePoint + ServiceNow + Google Search in a single Discovery Engine app. Three independent UI toggles (each connector and web grounding can be flipped per query), anti-hallucination guardrails, per-user ACLs honored on both connectors. **Tags:** `streamassist` `sharepoint` `servicenow` `google-search` `wif` `discovery-engine` `gemini-enterprise`
- [`sharepoint-wif-portal/`](./sharepoint-wif-portal/) — Docs-only WIP variant of `sharepoint_wif_portal`. **Status:** docs only, no code yet.
- [`ge_custom_mcp_sharepoint/`](./ge_custom_mcp_sharepoint/) — Double-alternative SharePoint connection to Gemini Enterprise (Custom MCP on Cloud Run vs Microsoft-hosted Work IQ SharePoint MCP). **Tags:** `mcp` `sharepoint` `gemini-enterprise`
- [`ge_aruntime_adk_mcp_sharepoint/`](./ge_aruntime_adk_mcp_sharepoint/) — SharePoint Explorer Agent built with Google ADK, deployed on Vertex AI Agent Runtime, connected to custom SharePoint MCP. **Tags:** `adk` `agent-runtime` `sharepoint` `mcp`
- [`adk-hosted-mcp-iq/`](./adk-hosted-mcp-iq/) — SharePoint Hosted Explorer Agent built with Google ADK, deployed on Vertex AI Agent Runtime, using Microsoft-hosted Work IQ SharePoint MCP server. **Tags:** `adk` `agent-runtime` `sharepoint` `mcp` `work-iq`


**Reference doc:** [`GEMINI_ENTERPRISE_SHAREPOINT_FLOW.md`](./GEMINI_ENTERPRISE_SHAREPOINT_FLOW.md) — the four mandatory configurations + replication checklist + failure-mode lookup behind every GE + SharePoint federated portal in this section.

### MCP servers
- [`gworkspace-mcp-server/`](./gworkspace-mcp-server/) — Gmail / Drive / Calendar / Docs / Sheets / Photos. **Tags:** `mcp` `google-workspace`
- [`ms365-mcp-server/`](./ms365-mcp-server/) — Outlook / SharePoint / OneDrive / Teams / Calendar. **Tags:** `mcp` `microsoft-365`
- [`plaid-mcp-server/`](./plaid-mcp-server/) — Bank txns, balances, subscriptions. **Tags:** `mcp` `plaid` `finance`
- [`amex-mcp/`](./amex-mcp/) — Amex statements, hybrid semantic + structured search. **Tags:** `mcp` `amex` `finance`
- [`knowledge-base-mcp/`](./knowledge-base-mcp/) — Semantic search over Claude Code transcripts. **Tags:** `mcp` `knowledge-base` `claude-code`

### RAG & document intelligence
- [`hierarchical-rag-pgvector/`](./hierarchical-rag-pgvector/) — Parent-child chunking with Cloud SQL pgvector. **Tags:** `rag` `pgvector`
- [`multimodal-doc-search/`](./multimodal-doc-search/) — Images + tables + text in one semantic index. **Tags:** `rag` `multimodal` `pgvector`
- [`docparse/`](./docparse/) — End-to-end PDF → Markdown → RAG agent in Gemini Enterprise. Cloud Run extractor with Gemini-3 vision (region detection, OCR, structured chart/photo extraction) + ADK agent on Vertex AI RAG Engine, registered cross-project in GE with ALL_USERS sharing. One-button `./deploy.sh`. **92.9% composite on 216-question eval** (vs 81% for DE streamAssist, vs 64% for raw-PDF RAG). [Full eval →](./docparse/eval/RESULTS.md). **Tags:** `pdf-parsing` `gemini-vision` `adk` `rag-engine` `gemini-3-flash` `agent-engine` `gemini-enterprise` `cross-project`

### Agent platforms
- [`vertex-multi-agent-workbench/`](./vertex-multi-agent-workbench/) — Multi-model (Gemini + Claude) workbench, MCP, ADK + LangGraph. **Tags:** `adk` `multi-agent`
- [`a2a-protocol-dojo/`](./a2a-protocol-dojo/) — 7-lesson Agent-to-Agent protocol tutorial. **Tags:** `a2a` `tutorial`
- [`observability-orchestra/`](./observability-orchestra/) — Multi-model Agent Engine with Cloud Trace + Logging. **Tags:** `observability` `agent-engine`
- [`cross-project-adk-agent/`](./cross-project-adk-agent/) — ADK in Project A registered from Project B. **Tags:** `adk` `cross-project`
- [`adk-secret-snow-demo/`](./adk-secret-snow-demo/) — IT-ops agent: Secret Manager + ServiceNow MCP + grounding. **Tags:** `adk` `secret-manager` `servicenow`
- [`adk-secret-manager-demo/`](./adk-secret-manager-demo/) — Secure secret handling via Google Secret Manager. **Tags:** `adk` `secret-manager`
- [`report-generator/`](./report-generator/) — ADK SequentialAgent: research → write → render. Topic in, cited PDF out (google_search → WeasyPrint). **Tags:** `adk` `multi-agent` `gemini-3-flash` `weasyprint` `pdf-rendering`
- [`agent-gateway-handson/`](./agent-gateway-handson/) — Console-first walkthrough of Google's Agent Gateway: one MCP server on Cloud Run, IAP + Model Armor authz extensions, IAP IAM bound via raw `curl` (no helper script). Owner-on-project assumed. Companion to the public `cloud-networking-solutions/agent-gateway` demo, minus all Terraform. **Tags:** `agent-gateway` `mcp` `iap` `model-armor` `adk` `cloud-run` `walkthrough`

### Consumer & domain apps
- [`vibes_nyc/`](./vibes_nyc/) — Mood-to-venue NYC underground spots. **Tags:** `consumer` `gemini` `vibe-search`
- [`global-pulse/`](./global-pulse/) — International news intelligence with veracity scoring. **Tags:** `news` `gemini` `multi-source`
- [`nexus-tax-intelligence/`](./nexus-tax-intelligence/) — AI tax advisory, Discovery Engine + PDF reports. **Tags:** `discovery-engine` `tax`
- [`gemini-websocket-chat/`](./gemini-websocket-chat/) — Terminal-aesthetic mobile PWA, Gemini over WebSocket. **Tags:** `pwa` `websocket` `gemini`
- [`quiniela-mundial-2026/`](./quiniela-mundial-2026/) — World Cup 2026 Quiniela Charales app: real-time predictions, FUT-style trading cards (Cromos), Gemini AI bot, Firestore sync, and Playwright test suite. **Tags:** `nextjs` `firestore` `gemini-3-flash` `adk` `lucha-libre` `world-cup`

### Testing & utilities
- [`adk-script-runner/`](./adk-script-runner/) — Minimal ADK smoke test. **Tags:** `adk` `test`
- [`adk-ui-explorer/`](../adk-ui-explorer/) — Interactive Web Application showcasing Google ADK + Gemini 3.1 Flash Lite UI/UX Explorer. **Tags:** `adk` `fastapi` `gemini-3.1-flash-lite` `ui`
- [`discovery-engine-latency-probe/`](./discovery-engine-latency-probe/) — StreamAssist latency benchmarks. **Tags:** `latency` `discovery-engine`
- [`gemini-2.5-flash-latency/`](./gemini-2.5-flash-latency/) — Measures latency and Time to First Chunk (TTFT) for Gemini 2.5 Flash on semi-autonomous agent tasks. **Tags:** `latency` `gemini-2.5-flash` `evaluation`
- [`streamassist-wif-auth-tester/`](./streamassist-wif-auth-tester/) — Interactive Entra→WIF→DE auth chain tester. **Tags:** `wif` `auth` `test`
- [`nextjs-test-harness/`](./nextjs-test-harness/) — Frontend experimentation scaffold. **Tags:** `nextjs` `frontend`
- [`vector-search-canvas/`](./vector-search-canvas/) — Self-study sandbox: TREE_AH vs BRUTE_FORCE side-by-side, every Vector Search 2.0 knob exposed. **Customer / context:** Vector Search 2.0 talk 2026-04-20. **Tags:** `vertex-vector-search` `tree-ah` `brute-force` `algorithm-tuning` `fastapi`
