# Weil, Gotshal & Manges LLP — GCP AI & Legal-Tech Innovation Workshop
## Session Alignment, Agenda Strategy & Agentic Showcase Blueprint

> **Target Date**: September 9, 2026  
> **Format**: Morning Discovery Workshop (9:00 AM – 1:00 PM) | Executive Briefing with Ravi (2:00 PM)  
> **Location**: Google Cloud Campus (California)  
> **Repository Folder**: `~/IdeaProjects/vertex-ai-samples/semiautonomous-agents/weil-legal-agentic-showcase`

---

## 1. Executive Summary & Context

Weil, Gotshal & Manges LLP ("Weil") is evaluating Google Cloud AI architecture to modernize high-stakes legal workflows, consolidate fragmented tools into a single-pane-of-glass agentic cockpit interface, and build an autonomous agentic foundation.

During the August 27, 2026 preparatory session with Weil leadership (**Andrew Simon** - Chief Innovation Officer / Tech Strategy, **Ian Miller** - Tech Architecture, **Steve Kedem**, and **Daulton Cockerell**), clear divisions of technical focus and priorities were established.

Specifically:
- **The Data & Retrieval Layer (Session 2)**: Handled by **Roberto Santana** *(Product Manager Lead, Vertex AI Embeddings)* and **Farzan & Luke** *(Unified Data Cloud)*. They will lead the deep-dive on dense vector stores (`gemini-embedding-2`, `text-embedding-005`), BM25 keyword search, graph entity resolution (FalkorDB / Spanner Graph), and ethical wall filtering at the retrieval layer.
- **The Agentic Architecture, Orchestration & Harness (Sessions 3 & 4)**: Handled by **Jesus Chavez** *(Customer Engineer, AI)*. This is the **centerpiece demo and presentation**, focusing on multi-agent systems via Google ADK (Agent Development Kit), context orchestration harnesses, Model Context Protocol (MCP) gateways, and UI consolidation.

---

## 2. Complete Workshop Schedule & Role Ownership

| Time | Session | Leads & Ownership | Key Discussion Topics & Deliverables |
| :--- | :--- | :--- | :--- |
| **09:00 AM – 09:45 AM** | **Session 1: Customer Discovery & Vision Alignment** | **All Leads** *(Sofi Mehta, Jesus Chavez, Brian Squibb)* | • Current state across practice groups at Weil (M&A due diligence, litigation search, contract intelligence).<br>• Fragmentation pain points across dozens of disconnected legal tools.<br>• Alignment on success criteria for the day. |
| **09:45 AM – 10:45 AM** | **Session 2: Advanced Legal Data Layer & Hybrid Retrieval** | **Roberto Santana** *(PM Lead, Vertex Embeddings)*<br>**Farzan & Luke** *(Unified Data Cloud)*<br>*Partners: Eran Lewis (ScaNN), Jagan Athreya (Spanner)* | • **Hybrid Search Architecture**: Vertex AI Vector Search (Dense) + BM25 (Sparse keyword) for legal precision.<br>• **Graph & Relational Grounding**: Entity resolution (parties, corporate relationships, precedent cases) via FalkorDB / Spanner Graph + AlloyDB.<br>• **Ethical Wall Filtering**: Filtering client data across ethical walls at the rank/rerank layer.<br>• **Models**: `gemini-embedding-2`, `text-embedding-005`. |
| **10:45 AM – 11:00 AM** | **Coffee & Bio Break** | Informal buffer & networking | |
| **11:00 AM – 12:00 PM** | **Session 3: Agentic Architecture, Orchestration & Harness** | **Jesus Chavez** *(CE, AI)* | • **Multi-Agent Orchestration**: Google Agent Development Kit (ADK) / Vertex AI Reasoning Engine for legal agents (intake, research, redlining, citation verification).<br>• **Deterministic Harness & Evaluation**: Guardrails, grounding verification, audit trails, and LLM-as-a-judge evaluation frameworks.<br>• **Tool-Calling & MCP Ecosystem**: Connecting iManage, internal legal DMS, and external engines via Model Context Protocol (MCP) gateways.<br>• **Client Lenses**: Supporting the **SCS Platform / Benchmark** and **Privacy Pro** *(modular clause assembly)*. |
| **12:00 PM – 12:45 PM** | **Session 4: Unified AI Experience & Interface Consolidation** | **Jesus Chavez** *(CE, AI)* | • **Single-Pane-of-Glass Strategy**: Consolidating 45,000+ fragmented surfaces into 1 unified, context-aware legal assistant portal.<br>• **Dynamic UI & Workspace Integration**: Real-time streaming responses, artifact previews, and interactive redlining workflows.<br>• **Enterprise Security & Compliance**: Fine-grained RBAC, tenant isolation, zero-data-leakage guarantee. |
| **12:45 PM – 01:00 PM** | **Session 5: Synthesis & Executive Briefing Prep** | **All Leads** | • Synthesizing morning discoveries, architectural decisions, and top use cases.<br>• Finalizing talking points for the 2:00 PM meeting with Ravi. |
| **01:00 PM – 02:00 PM** | **Lunch Break & Executive Transition** | Networking lunch | Preparation for executive arrival. |
| **02:00 PM – 03:00 PM** | **Executive Session with Ravi** | **Ravi & Executive Delegation** | C-Suite strategic partnership alignment and roadmap commitment. |

---

## 3. Key Insights & Customer Requirements (From Weil Transcript)

### A. The "Privacy Pro" Use Case (Document Assembly via "Legos")
- **Andrew Simon's Concept**: Legal documents are like "Legos"—modular, standardized structural blocks with strict logical and corporate relationships.
- **The Need**: An agentic system that can intelligently assemble, reorder, and validate legal clauses based on deal parameters, verifying cross-dependencies and compliance automatically.

### B. The "SCS Platform" & Benchmark
- Weil's existing platform (currently operating in Azure) that underpins their benchmark for processing large volumes of complex legal data and answering multi-step legal questions.
- A key goal for the workshop is to evaluate how this platform can be modernized and accelerated using Google Cloud AI and Vertex AI.

### C. Agent Harnesses Outside Antigravity
- Andrew explicitly requested guidance on Google Cloud's orchestration ecosystem:
  > *"Context orchestration and agent harnesses... what Google is offering here outside Antigravity as a harness... what else is working for your customers?"*
- Demonstrating the **Google Agent Development Kit (ADK)** with state management, deterministic validation, tool callbacks, and evaluation frameworks directly addresses this inquiry.

### D. Model Strategy: Open-Weight (Gemma) vs. Frontier (Gemini)
- Weil uses open-weight models (e.g., Gemma 2 / 4) for "tissue paper applications"—routine, stable workflows like German power-of-attorney generation where frozen weights prevent unintended behavioral shifts.
- They look to frontier Gemini models (`gemini-3.8-flash`, `gemini-3.7-flash`, `gemini-3-pro-preview`) for complex reasoning, multi-agent synthesis, and multimodal clause interpretation.

### E. Single-Pane-of-Glass Interface Consolidation
- Weil currently suffers from tool proliferation ("45,000 legal surfaces") including Harvey, Thomson Reuters, iManage, etc.
- They want a single cockpit where an attorney can initiate research, redline documents, assemble contracts, and query precedents without context switching.

---

## 4. The Dedicated Presentation Slide Blueprint

### Title:
**Autonomous Multi-Agent Orchestration & The Deterministic Legal Harness**
### Subtitle:
*From Fragmented Tools to a Governed, Self-Auditing Legal AI Intelligence Platform on Google Cloud*

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ Vertex AI & Google Agent Development Kit (ADK)              Proprietary & Confidential │
│ Autonomous Multi-Agent Orchestration & The Deterministic Legal Harness                 │
│ Unifying Domain-Specific Subagents under a Zero-Leak, Verifiable Execution Fabric      │
├────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                        │
│   ┌────────────────────────────────────────────────────────────────────────────────┐   │
│   │                 ORCHESTRATION LAYER (Google ADK Coordinator)                   │   │
│   │   Intent Decomposition • State Management • Dynamic Tool Routing & Callbacks   │   │
│   └──────────────────────────────────────┬─────────────────────────────────────────┘   │
│                                          │                                             │
│       ┌──────────────────┬───────────────┴───────────────┬──────────────────┐          │
│       ▼                  ▼                               ▼                  ▼          │
│  ┌──────────────┐  ┌──────────────┐                ┌──────────────┐  ┌──────────────┐  │
│  │ 📄 ASSEMBLY  │  │ 🔍 CITATION  │                │ 🛡️ ETHICAL   │  │ ✍️ REDLINE   │  │
│  │    AGENT     │  │    AGENT     │                │  WALL AGENT  │  │    AGENT     │  │
│  │ "Privacy Pro"│  │ Precedent &  │                │ Boundary &   │  │ Structured   │  │
│  │ Modular Lego │  │ Case Law     │                │ Client Data  │  │ Diffs & Risk │  │
│  │ Clauses      │  │ Verification │                │ Sanitization │  │ Scoring      │  │
│  └──────┬───────┘  └──────┬───────┘                └──────┬───────┘  └──────┬───────┘  │
│         └─────────────────┼───────────────────────────────┼─────────────────┘          │
│                           ▼                               ▼                            │
│   ┌────────────────────────────────────────────────────────────────────────────────┐   │
│   │                    DETERMINISTIC HARNESS & EVALUATION                          │   │
│   │   LLM-as-a-Judge • Citation Grounding Check • Model Context Protocol (MCP)     │   │
│   └────────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                        │
│   [ KEY WEIL VALUE ]: Transforms isolated legal workflows (iManage, Harvey, internal   │
│   templates) into 1 unified, auditable agentic cockpit with zero data leakage.         │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 5. The Live Interactive Demo Blueprint: "Weil Legal Agentic Platform"

### Stack:
- **Frontend**: React 19 + TypeScript + Vite + Tailwind CSS + Lucide Icons + Framer Motion.
- **Backend**: FastAPI (Python 3.12) + Google Agent Development Kit (ADK) / Vertex AI SDK (`gemini-3.8-flash` / `gemini-3.7-flash`).
- **Protocol**: Zero-Leak Protocol (strict `.env` protection, zero credentials committed).

### Core Interactive Features:
1. **Live Multi-Agent Deliberation (SSE Real-Time Stream)**:
   - Visual 4-lane parallel execution showing the Coordinator, Assembly, Citation, and Ethical Wall agents thinking simultaneously.
   - Real-time token streaming with color-coded thought logs.
2. **Interactive "Lego" Document Assembler ("Privacy Pro" Simulation)**:
   - Drag-and-drop or agent-assembled modular legal clauses (e.g., Indemnification, Non-Compete, Governing Law, GDPR/Schrems II Data Transfer).
   - Instant visual dependency check (e.g., Clause 4 requires Clause 2 definition).
3. **Deterministic Harness & Audit Inspector**:
   - Live modal showing citation verification (green checkmarks for verified precedent cases, red alerts for ungrounded citations).
   - Ethical wall filter pass: proves that Client B confidential data was scrubbed before output was generated for Client A.
4. **Single-Pane-of-Glass Legal Cockpit**:
   - Combines document preview, agent chat, precedent search, and structured diff redlining in one unified screen.

---

## 6. Directory Structure for Workshop Assets

```
weil-legal-agentic-showcase/
├── .gitignore                           # Ironclad Zero-Leak rules
├── README.md                            # High-level overview & launch instructions
├── SESSION_ALIGNMENT_AND_STRATEGY.md    # This comprehensive briefing file
├── slides/                              # Presentation markdown, diagrams, and assets
│   ├── slide_agentic_orchestration.md   # Exact slide content & speaker notes
│   └── diagrams/                        # Mermaid & visual architecture diagrams
├── backend/                             # FastAPI + Google ADK agent service
│   ├── main.py                          # Agent endpoints & SSE streaming
│   ├── agents/                          # ADK Agent definitions (Assembly, Citation, etc.)
│   ├── harness/                         # Evaluation, MCP tools & ethical wall filters
│   └── requirements.txt                 # Backend dependencies
└── frontend/                            # React 19 + TypeScript + Tailwind single-pane portal
    ├── src/                             # Agent cockpit, Lego clause builder, audit trail
    ├── package.json
    └── vite.config.ts
```
