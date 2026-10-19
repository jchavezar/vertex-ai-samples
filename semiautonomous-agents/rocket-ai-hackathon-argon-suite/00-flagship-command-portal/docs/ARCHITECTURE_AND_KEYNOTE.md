# Flagship Command Hub (`rocket-hackathon-portal`) — Architecture & 2-Hour Keynote Runbook

- **Live Cloud Run Portal:** [https://rocket-hackathon-portal-254356041555.us-central1.run.app](https://rocket-hackathon-portal-254356041555.us-central1.run.app)
- **Real Gemini Enterprise Web UI:** [https://vertexaisearch.cloud.google.com/home/cid/gemini-enterprise-17877637_1787763712023](https://vertexaisearch.cloud.google.com/home/cid/gemini-enterprise-17877637_1787763712023)
- **Shared Private Login:** Username `rocket` | Password `Argon2026!`

## 1. Account Strategy: Rocket Companies (`[INT RKT]`)
Rocket Companies operates a 5-pillar homeownership ecosystem:
1. **Rocket Money** (Personal Finance, Subscriptions, Down-Payment Vaults)
2. **Redfin** (Top-of-Funnel Real Estate Search, MLS Listings & Tour Scheduling)
3. **Rocket Mortgage** (Loan Origination & *Rocket Logic* Underwriting)
4. **Rocket Close / Amrock** (Title, Appraisal & TRID Closing)
5. **Mr. Cooper Group** (Servicing Portfolio, *Synopsis* Call Analytics & Refi Recapture)

## 2. 2-Hour Executive Presentation Runbook

### Hour 1: Gemini Enterprise (Sobi / Spark, Agent Platform, Registry & GECX) (Luis Lopez, Sundar Chellappa, Ricky Merrefield & Jesus Chavez)
- **00:00 – 00:12 — 1. The Sea Change: From Passive Chat to Software-Generating Teammates** (*Gemini Enterprise (`global-gemini-enterprise`) & Spark (`sobi-<USER_ID>`)*) — Demo Ref `[1.3]`
  - One Unified Prompt Box across Web (`gemini.google.com/work`), Desktop, Mobile, and Microsoft Teams/Outlook.
  - Spark is a persistent digital teammate that writes and runs Python/Bash inside isolated gVisor sandboxes to build dashboards, audit TRID disclosures, and analyze Redfin MLS spreadsheets.
  - Model Choice Built-In: Run workloads on Gemini 4 Argon (`gemini-4-argon`), Gemini 3.8 Flash, or Claude Opus/Sonnet 5.5 under a single Google Cloud enterprise contract and security perimeter.
- **00:12 – 00:25 — 2. Query-in-Place Enterprise Grounding & 3-Object Agent Registry** (*Connecting O365 SharePoint, OneDrive, Encompass LOS, and BigQuery without Data Replication*) — Demo Ref `[2.1]`
  - Zero 'Storage Double Taxation': Query Rocket's SharePoint Online, Fannie/Freddie Selling Guides, and BigQuery Redfin/Mr. Cooper tables in-place.
  - RFC 530 3-Object Connector Architecture: `McpServer` (`agentregistry-<UUID>`), `AuthProvider` (`ge-auth-<FP64>`), and `AuthBinding` (`ge-bind-<FP64>`) preserve end-user 3LO Entra ID / O365 ACLs.
  - Centralized Governance: App Hub & Agent Registry (`ge-ai-app-*`) give Rocket Security a single pane of glass over every agent, tool, and MCP server.
- **00:25 – 00:40 — 3. Gemini Enterprise Agent Platform (GEAP) & Visual Agent Studio** (*Low-Code Underwriting Workflows + Code-First ADK Multi-Agent Orchestration*) — Demo Ref `[2.2]`
  - Visual Agent Studio (L200) lets Rocket Operations build condition-clearing agents with `RUNTIME_STAGE_BLOCKING` CEL Human-in-the-Loop approval gates.
  - Agent Development Kit (ADK L300) orchestrates stateful multi-agent teams across Rocket Money, Redfin, and Mr. Cooper Servicing.
  - Model Armor + Cloud Sensitive Data Protection (SDP) enforces GLBA ethical walls, masking SSNs and bank account numbers inline.
- **00:40 – 01:00 — 4. Gemini Enterprise for CX (GECX) & Multimodal Live API (The Sierra AI Killer)** (*Transforming Mr. Cooper Servicing, Escrow Shortages, Synopsis & Portfolio Recapture*) — Demo Ref `[3.4]`
  - Omnichannel GECX + Dialogflow CX handles high-volume Mr. Cooper escrow shortage journeys, official per-diem payoff quotes, and Form 1098 delivery.
  - CCAI Agent Assist upgrades Rocket Logic Synopsis from post-call batch summaries into real-time CFPB Regulation X loss-mitigation coaching.
  - Gemini Multimodal Live API delivers <200ms interruptible bidirectional voice for Refi Recapture—eliminating Sierra AI per-resolution fees.

### Hour 2: Google Antigravity 2.0, Sandboxed Code Execution, MCP & Gemini 4 Argon (Jesus Chavez, Joris Wynendaele & Google CE Mentors)
- **01:00 – 01:15 — 1. Meet Google Antigravity 2.0: The Agent-First Development Platform** (*Why Antigravity + Gemini 4 Argon Leaves Single-Threaded Claude Code Behind*) — Demo Ref `[1.5]`
  - Antigravity 2.0 Desktop IDE + `agy` CLI + Managed Agents API inside Gemini Enterprise.
  - Persistent Cloud Execution: Delegate an objective (Goal Mode), close your laptop, and let Antigravity subagents code, run browser tests, and verify builds in isolated gVisor sandboxes.
  - Powered by Gemini 4 Argon (`gemini-4-argon`) & Gemini 3.8 Flash: 2M context window, Context Caching, and OneQuota enterprise scale.
- **01:15 – 01:30 — 2. Model Context Protocol (MCP) & Cross-Funnel Subagent Orchestration** (*Unifying Rocket Money -> Redfin -> Rocket Mortgage -> Rocket Close via MCP*) — Demo Ref `[4.5]`
  - Standardized MCP Servers expose Redfin Tour Webhooks, Rocket Money Goal Vaults, O365 Banker Calendars, and Rocket Pricing Engines safely.
  - Dynamic Python Workflows (`run_workflow` with `parallel()` and `pipeline()`) fan out across multiple subagents with strict JSON schema contracts.
  - Live Walkthrough: Building the Redfin-to-Rocket Cross-Funnel Campaign Bot (`4.5`) in 15 lines of Antigravity workflow code.
- **01:30 – 01:45 — 3. DeepMind CodeMender & The Autonomous AI Software Factory** (*Zero-Touch Vulnerability Patching (`cm verify` / `cm fix`) & Legacy .NET Modernization*) — Demo Ref `[6.1]`
  - CodeMender traces OWASP CWE-89 SQLi and CWE-639 IDOR vulnerabilities across Rocket LOS APIs, reproduces exploits in a gVisor sandbox, and commits verified patches.
  - AI Software Factory Swarm (`workspace='share'`) converts a Product Requirements Document (PRD) into a tested FastAPI/.NET 9 Pull Request automatically.
  - Legacy C#/.NET Framework 4.8 WCF SOAP services refactored into containerized Cloud Run microservices in seconds.
- **01:45 – 02:00 — 4. Google CE Moonshots & Hackathon Kickoff Blueprint** (*Project Siren, Spatial Close (3D Maps + Imagen 4.0), HiveMind Swarm & Air-Tight*) — Demo Ref `[M.3]`
  - How to clone any of the 33 live Cloud Run reference architectures using the Reproduction Blueprints on this portal.
  - Accessing your GCP Sandbox Project, Vertex AI `gemini-4-argon` & `gemini-3.8-flash` endpoints, and Antigravity MCP starter kits.
  - Judging Rubric for Track 1 (CX), Track 2 (Ops/Underwriting), Track 3 (Mr. Cooper Servicing), and Track 4 (Wildcard Moonshots).
