<p align="center">
  <img src="https://fonts.gstatic.com/s/i/productlogos/googleg/v6/24px.svg" width="48" alt="Google Cloud" />
</p>

<h1 align="center">semiautonomous-agents</h1>

<p align="center">
  <em>Production-tested agentic patterns built on Google ADK, Vertex AI, and MCP</em>
</p>

<p align="center">
  <a href="https://github.com/jchavezar/vertex-ai-samples"><img src="https://img.shields.io/badge/Vertex_AI-Samples-4285F4?style=for-the-badge&logo=googlecloud&logoColor=white" alt="Vertex AI Samples" /></a>
  <a href="#whats-here"><img src="https://img.shields.io/badge/projects-27-34A853?style=for-the-badge" alt="27 Projects" /></a>
  <a href="#-mcp-servers"><img src="https://img.shields.io/badge/MCP_Servers-6-FF6F00?style=for-the-badge" alt="MCP Servers" /></a>
  <a href="https://github.com/jchavezar/vertex-ai-samples/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-Apache_2.0-blue?style=for-the-badge" alt="License" /></a>
</p>

<p align="center">
  <a href="#-enterprise-search--portals">Portals</a>&nbsp;&nbsp;·&nbsp;&nbsp;<a href="#-mcp-servers">MCP Servers</a>&nbsp;&nbsp;·&nbsp;&nbsp;<a href="#-rag--document-intelligence">RAG</a>&nbsp;&nbsp;·&nbsp;&nbsp;<a href="#-agent-platforms">Platforms</a>&nbsp;&nbsp;·&nbsp;&nbsp;<a href="#-consumer--domain-apps">Apps</a>&nbsp;&nbsp;·&nbsp;&nbsp;<a href="#-testing--utilities">Utilities</a>
</p>

---

## Featured

<table>
<tr>
<td width="50%" align="center">
<a href="./streamassist-oauth-flow/"><strong>StreamAssist OAuth Flow</strong></a><br/>
<em>WIF-powered SharePoint search with full auth trace sidebar</em><br/><br/>
<a href="./streamassist-oauth-flow/"><img src="./streamassist-oauth-flow/docs/demo.gif" width="100%" /></a>
</td>
<td width="50%" align="center">
<a href="./ge-sharepoint-cloudid/"><strong>SharePoint — Google Cloud Identity</strong></a><br/>
<em>Same power, zero WIF — native Google Identity Services</em><br/><br/>
<a href="./ge-sharepoint-cloudid/"><img src="./ge-sharepoint-cloudid/screenshots/demo.gif" width="100%" /></a>
</td>
</tr>
<tr>
<td width="50%" align="center">
<a href="./adk-secret-snow-demo/"><strong>SecretOps — ADK + Secret Manager</strong></a><br/>
<em>IT ops agent with secure credentials and ServiceNow MCP</em><br/><br/>
<a href="./adk-secret-snow-demo/"><img src="./adk-secret-snow-demo/assets/demo.gif" width="100%" /></a>
</td>
<td width="50%" align="center">
<a href="./sharepoint_wif_portal/"><strong>SharePoint WIF Portal</strong></a><br/>
<em>The reference implementation — Entra to GCP, zero credentials</em><br/><br/>
<a href="./sharepoint_wif_portal/"><img src="./sharepoint_wif_portal/assets/portal-demo.gif" width="100%" /></a>
</td>
</tr>
</table>

---

## What's New

> [!TIP]
> **April 2026** — Two new projects and major README upgrades across the board.

| Date | Project | What Changed |
|:-----|:--------|:-------------|
| Apr 14 | [**ge-sharepoint-cloudid**](./ge-sharepoint-cloudid/) | **NEW** — SharePoint search via native Google Cloud Identity (no WIF) |
| Apr 12 | [**a2a-protocol-dojo**](./a2a-protocol-dojo/) | Interactive A2A protocol tutorial with streamed agent communication |
| Apr 10 | [**knowledge-base-mcp**](./knowledge-base-mcp/) | Session ingestion pipeline + backfill tools |
| Apr 8 | [**adk-secret-snow-demo**](./adk-secret-snow-demo/) | Switched to ADK built-in `google_search` with `AgentTool` |
| Apr 5 | [**streamassist-oauth-flow**](./streamassist-oauth-flow/) | HD demo GIF + sequence diagrams + expandable prerequisites |

---

## What's Here

27 projects across 6 categories. Every project runs on **Google Cloud** with **Vertex AI** as the backbone.

```
Google ADK ██████████████████████████████ 15    React 19   ████████████████████████  11
FastAPI    ████████████████████████       11    Vertex AI  ██████████████████████████████ 15
MCP (FastMCP) ████████████               6     Agent Engine ██████████               5
Discovery Engine ██████████████           7     pgvector   ████                      2
```

---

## 🏢 Enterprise Search & Portals

Full-stack portals bridging Microsoft identity to Google Cloud search infrastructure.

| Project | What It Does | Stack |
|:--------|:-------------|:------|
| [**sharepoint_wif_portal**](./sharepoint_wif_portal/) | Enterprise search portal — Entra ID to Google Cloud with zero credential storage. The reference implementation. | ![Python](https://img.shields.io/badge/-Python-3776AB?logo=python&logoColor=white&style=flat-square) ![React](https://img.shields.io/badge/-React-61DAFB?logo=react&logoColor=black&style=flat-square) ![ADK](https://img.shields.io/badge/-ADK-4285F4?style=flat-square) |
| [**servicedesk-sharepoint-portal**](./servicedesk-sharepoint-portal/) | Discovery Engine (SharePoint) + ServiceNow MCP in a single agent portal | ![Python](https://img.shields.io/badge/-Python-3776AB?logo=python&logoColor=white&style=flat-square) ![React](https://img.shields.io/badge/-React-61DAFB?logo=react&logoColor=black&style=flat-square) ![MCP](https://img.shields.io/badge/-MCP-FF6F00?style=flat-square) |
| [**servicenow-mcp-portal**](./servicenow-mcp-portal/) | Agent Engine + ServiceNow via MCP with MSAL-authenticated React frontend | ![Python](https://img.shields.io/badge/-Python-3776AB?logo=python&logoColor=white&style=flat-square) ![React](https://img.shields.io/badge/-React-61DAFB?logo=react&logoColor=black&style=flat-square) ![MCP](https://img.shields.io/badge/-MCP-FF6F00?style=flat-square) |
| [**gemini-enterprise-sharepoint-agent**](./gemini-enterprise-sharepoint-agent/) | ADK Agent registered in Gemini Enterprise — searches SharePoint via Discovery Engine + WIF | ![Python](https://img.shields.io/badge/-Python-3776AB?logo=python&logoColor=white&style=flat-square) ![ADK](https://img.shields.io/badge/-ADK-4285F4?style=flat-square) ![WIF](https://img.shields.io/badge/-WIF-34A853?style=flat-square) |
| [**streamassist-oauth-flow**](./streamassist-oauth-flow/) | Custom StreamAssist portal — users authorize once, then chat with SharePoint-grounded answers | ![Python](https://img.shields.io/badge/-Python-3776AB?logo=python&logoColor=white&style=flat-square) ![React](https://img.shields.io/badge/-React-61DAFB?logo=react&logoColor=black&style=flat-square) ![WIF](https://img.shields.io/badge/-WIF-34A853?style=flat-square) |
| [**ge-sharepoint-cloudid**](./ge-sharepoint-cloudid/) | Federated SharePoint search via Google Cloud Identity — no WIF, no STS, no MSAL | ![Python](https://img.shields.io/badge/-Python-3776AB?logo=python&logoColor=white&style=flat-square) ![React](https://img.shields.io/badge/-React-61DAFB?logo=react&logoColor=black&style=flat-square) ![GIS](https://img.shields.io/badge/-GIS-4285F4?style=flat-square) |

## 🔌 MCP Servers

Standalone [Model Context Protocol](https://modelcontextprotocol.io/) servers that plug into any MCP-compatible agent or IDE.

| Project | APIs Exposed | Stack |
|:--------|:-------------|:------|
| [**gworkspace-mcp-server**](./gworkspace-mcp-server/) | Gmail, Drive, Calendar, Docs, Sheets, Photos | ![Python](https://img.shields.io/badge/-Python-3776AB?logo=python&logoColor=white&style=flat-square) ![FastMCP](https://img.shields.io/badge/-FastMCP-FF6F00?style=flat-square) |
| [**ms365-mcp-server**](./ms365-mcp-server/) | Outlook, SharePoint, OneDrive, Teams, Calendar | ![Python](https://img.shields.io/badge/-Python-3776AB?logo=python&logoColor=white&style=flat-square) ![FastMCP](https://img.shields.io/badge/-FastMCP-FF6F00?style=flat-square) |
| [**plaid-mcp-server**](./plaid-mcp-server/) | Bank transactions, balances, subscriptions | ![Python](https://img.shields.io/badge/-Python-3776AB?logo=python&logoColor=white&style=flat-square) ![FastMCP](https://img.shields.io/badge/-FastMCP-FF6F00?style=flat-square) |
| [**amex-mcp**](./amex-mcp/) | Financial transactions — hybrid semantic + structured search with Gemini enrichment | ![Python](https://img.shields.io/badge/-Python-3776AB?logo=python&logoColor=white&style=flat-square) ![FastMCP](https://img.shields.io/badge/-FastMCP-FF6F00?style=flat-square) |
| [**knowledge-base-mcp**](./knowledge-base-mcp/) | Semantic search over Claude Code transcripts — problem-solution pattern extraction | ![Python](https://img.shields.io/badge/-Python-3776AB?logo=python&logoColor=white&style=flat-square) ![FastMCP](https://img.shields.io/badge/-FastMCP-FF6F00?style=flat-square) |

## 📚 RAG & Document Intelligence

Retrieval-augmented generation pipelines with different chunking and embedding strategies.

| Project | Approach | Stack |
|:--------|:---------|:------|
| [**hierarchical-rag-pgvector**](./hierarchical-rag-pgvector/) | Parent-child chunking with Cloud SQL pgvector — precision retrieval without losing document context | ![Python](https://img.shields.io/badge/-Python-3776AB?logo=python&logoColor=white&style=flat-square) ![React](https://img.shields.io/badge/-React-61DAFB?logo=react&logoColor=black&style=flat-square) ![pgvector](https://img.shields.io/badge/-pgvector-336791?style=flat-square) |
| [**multimodal-doc-search**](./multimodal-doc-search/) | Multimodal document intelligence — images, tables, and text in a unified semantic search + chat | ![Python](https://img.shields.io/badge/-Python-3776AB?logo=python&logoColor=white&style=flat-square) ![React](https://img.shields.io/badge/-React-61DAFB?logo=react&logoColor=black&style=flat-square) ![pgvector](https://img.shields.io/badge/-pgvector-336791?style=flat-square) |

## 🤖 Agent Platforms

Multi-agent orchestration, protocol tutorials, and observability.

| Project | What It Does | Stack |
|:--------|:-------------|:------|
| [**vertex-multi-agent-workbench**](./vertex-multi-agent-workbench/) | Enterprise agent platform — multi-model support (Gemini + Claude), MCP connectivity, ADK + LangGraph | ![Python](https://img.shields.io/badge/-Python-3776AB?logo=python&logoColor=white&style=flat-square) ![React](https://img.shields.io/badge/-React-61DAFB?logo=react&logoColor=black&style=flat-square) ![ADK](https://img.shields.io/badge/-ADK-4285F4?style=flat-square) |
| [**a2a-protocol-dojo**](./a2a-protocol-dojo/) | Interactive 7-lesson tutorial for Google's Agent-to-Agent (A2A) protocol with live agent communication | ![Python](https://img.shields.io/badge/-Python-3776AB?logo=python&logoColor=white&style=flat-square) ![React](https://img.shields.io/badge/-React-61DAFB?logo=react&logoColor=black&style=flat-square) ![A2A](https://img.shields.io/badge/-A2A-EA4335?style=flat-square) |
| [**observability-orchestra**](./observability-orchestra/) | Multi-model Agent Engine testing with Cloud Trace and Cloud Logging instrumentation | ![Python](https://img.shields.io/badge/-Python-3776AB?logo=python&logoColor=white&style=flat-square) ![ADK](https://img.shields.io/badge/-ADK-4285F4?style=flat-square) |
| [**cross-project-adk-agent**](./cross-project-adk-agent/) | Deploy an ADK agent in Project A, register and use it from Project B's Gemini Enterprise | ![Python](https://img.shields.io/badge/-Python-3776AB?logo=python&logoColor=white&style=flat-square) ![ADK](https://img.shields.io/badge/-ADK-4285F4?style=flat-square) |
| [**adk-secret-snow-demo**](./adk-secret-snow-demo/) | IT ops agent — Secret Manager credentials, ServiceNow MCP, Google Search grounding | ![Python](https://img.shields.io/badge/-Python-3776AB?logo=python&logoColor=white&style=flat-square) ![ADK](https://img.shields.io/badge/-ADK-4285F4?style=flat-square) ![MCP](https://img.shields.io/badge/-MCP-FF6F00?style=flat-square) |
| [**adk-secret-manager-demo**](./adk-secret-manager-demo/) | Semiautonomous agent with secure secret handling via Google Secret Manager + Vertex AI | ![Python](https://img.shields.io/badge/-Python-3776AB?logo=python&logoColor=white&style=flat-square) ![ADK](https://img.shields.io/badge/-ADK-4285F4?style=flat-square) |

## 🌆 Consumer & Domain Apps

End-user applications blending agentic intelligence with polished UIs.

| Project | What It Does | Stack |
|:--------|:-------------|:------|
| [**vibes_nyc**](./vibes_nyc/) | Mood-to-venue matching — underground NYC spots with multi-source vibe fingerprinting | ![Python](https://img.shields.io/badge/-Python-3776AB?logo=python&logoColor=white&style=flat-square) ![React](https://img.shields.io/badge/-React-61DAFB?logo=react&logoColor=black&style=flat-square) ![Gemini](https://img.shields.io/badge/-Gemini_2.5-4285F4?style=flat-square) |
| [**global-pulse**](./global-pulse/) | International news intelligence — 15+ sources, veracity scoring, multi-language analysis | ![Python](https://img.shields.io/badge/-Python-3776AB?logo=python&logoColor=white&style=flat-square) ![React](https://img.shields.io/badge/-React-61DAFB?logo=react&logoColor=black&style=flat-square) ![Gemini](https://img.shields.io/badge/-Gemini_2.5-4285F4?style=flat-square) |
| [**nexus-tax-intelligence**](./nexus-tax-intelligence/) | AI tax advisory platform — Discovery Engine grounding + PDF report generation for executives | ![Python](https://img.shields.io/badge/-Python-3776AB?logo=python&logoColor=white&style=flat-square) ![React](https://img.shields.io/badge/-React-61DAFB?logo=react&logoColor=black&style=flat-square) ![Gemini](https://img.shields.io/badge/-Gemini_2.5-4285F4?style=flat-square) |
| [**gemini-websocket-chat**](./gemini-websocket-chat/) | Terminal-aesthetic mobile PWA — real-time Gemini chat over WebSocket with Zustand state | ![Python](https://img.shields.io/badge/-Python-3776AB?logo=python&logoColor=white&style=flat-square) ![React](https://img.shields.io/badge/-React-61DAFB?logo=react&logoColor=black&style=flat-square) |

## 🧪 Testing & Utilities

Probes, harnesses, and scaffolding for validating infrastructure and auth flows.

| Project | Purpose | Stack |
|:--------|:--------|:------|
| [**adk-script-runner**](./adk-script-runner/) | Minimal ADK smoke test — agent generates, saves, and executes bash scripts at runtime | ![Python](https://img.shields.io/badge/-Python-3776AB?logo=python&logoColor=white&style=flat-square) ![ADK](https://img.shields.io/badge/-ADK-4285F4?style=flat-square) |
| [**discovery-engine-latency-probe**](./discovery-engine-latency-probe/) | StreamAssist latency benchmarking under real-world auth conditions | ![Python](https://img.shields.io/badge/-Python-3776AB?logo=python&logoColor=white&style=flat-square) |
| [**streamassist-wif-auth-tester**](./streamassist-wif-auth-tester/) | Interactive tester for the Entra ID → WIF/STS → Discovery Engine auth chain | ![Python](https://img.shields.io/badge/-Python-3776AB?logo=python&logoColor=white&style=flat-square) ![Flask](https://img.shields.io/badge/-Flask-000?logo=flask&style=flat-square) |
| [**nextjs-test-harness**](./nextjs-test-harness/) | Next.js scaffold for frontend experimentation | ![TypeScript](https://img.shields.io/badge/-TypeScript-3178C6?logo=typescript&logoColor=white&style=flat-square) ![Next.js](https://img.shields.io/badge/-Next.js-000?logo=next.js&style=flat-square) |

---

## Architecture

> [!NOTE]
> Every project connects to the same Google Cloud backbone. Identity flows bridge Microsoft Entra or Google Cloud Identity to Vertex AI services. MCP servers expose external APIs as tools that any agent can use.

```mermaid
graph LR
    subgraph Identity["Identity Layer"]
        ENTRA[Microsoft Entra ID]
        WIF[Workforce Identity Federation]
        GIS[Google Cloud Identity]
    end

    subgraph Agents["Agent Layer"]
        ADK[Google ADK Agents]
        AE[Agent Engine]
        A2A[A2A Protocol]
    end

    subgraph Data["Data & Retrieval"]
        DE[Discovery Engine]
        PG[Cloud SQL pgvector]
        FS[Firestore]
    end

    subgraph MCP["MCP Servers"]
        GW[Google Workspace]
        MS[Microsoft 365]
        PL[Plaid / Amex]
        KB[Knowledge Base]
    end

    subgraph UI["Frontends"]
        REACT[React 19 + Vite]
        GE[Gemini Enterprise]
    end

    ENTRA --> WIF --> AE
    GIS --> DE
    ADK --> AE
    A2A --> ADK
    AE --> DE & PG & FS
    AE --> MCP
    REACT --> AE
    REACT --> DE
    GE --> AE
```

<details>
<summary><strong>Identity flow comparison</strong></summary>

| | WIF Path | Google Cloud Identity Path |
|---|---|---|
| Identity | Entra ID (MSAL.js) | Google Identity Services |
| Token chain | Entra JWT → STS → GCP token | Google auth code → GCP token |
| WIF required | Yes (Pool + Provider) | No |
| Entra apps | 2 (Portal + Connector) | 1 (Connector only) |
| Projects | sharepoint_wif_portal, streamassist-oauth-flow | ge-sharepoint-cloudid |

</details>

---

## Quick Start

Most projects follow the same pattern:

```bash
# 1. Backend
cd <project>/backend
uv sync && uv run python main.py

# 2. Frontend (if applicable)
cd <project>/frontend
npm install && npm run dev
```

> [!TIP]
> All Python projects use [**uv**](https://docs.astral.sh/uv/) for dependency management. Run `uv sync` instead of `pip install`.

> [!IMPORTANT]
> Projects with auth flows (WIF, GIS, MSAL) require environment variables. Check each project's `.env.example` for the required config.

---

## License

Apache 2.0 — See [LICENSE](../LICENSE)
