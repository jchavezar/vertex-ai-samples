# Google Cloud • Agentic Cloud Assist Error Remediation Hub

An autonomous, next-generation agentic error detection and proactive remediation platform on Google Cloud that integrates **Cloud Logging**, the **Gemini Cloud Assist REST API (`geminicloudassist.googleapis.com/v1alpha`)**, and a **Google ADK Agent with built-in Google Search**.

---

## 🏛️ Architecture & Features

```mermaid
flowchart LR
    A[1. Cloud Logging Telemetry\nHistorical Windows: 15m - 7d] -->|Instant Cache / ReAct| B[2. 4-Container Cloud Assist Engine]
    B -->|Clickable Sandbox CLI Execution| C[One-Click Terminal Command Engine\nExecutes safely in Linux Sandbox]
    B -->|Orchestrate Parallel Sandbox Fixes| D[Parallel Antigravity Sandbox Pool\nSubagent-1 | Subagent-2 | Subagent-N]
    D -->|Barrier Consolidator| E[Zero-Drop Self-Healing Verification Report]
    B -->|Context Injection| F[Way-Right ADK Chatbot\nGoogle Search Built-In + Claude Ink]
```

### 1. Left Panel — Cloud Logging Error List & Time Filter
- Queries historical Cloud Logging error telemetry (`severity >= ERROR`) combined with representative Cloud Run 500 (OOMKilled), Cloud SQL maintenance locks, GKE CrashLoopBackOff, and Cloud Storage IAM 403 errors.
- Time range filter (`Last 15m`, `Last 1h`, `Last 6h`, `Last 24h`, `Last 7d`) replicating Google Cloud Console UX.

### 2. Middle Panel — 6-Container Hybrid Split-Plane Diagnostic Engine
Executes the full 5-stage Hybrid Agentic Flow (`/api/hybrid-flow`) and populates six structured interactive containers:
1. **5-Stage Hybrid Split-Plane Execution Flow & Policy Gate (`HybridAgentFlowCard`)**: Visualizes the step-by-step pipeline (`1. DETECT -> 2. DIAGNOSE -> 3. ADK SEARCH -> 4. SANDBOX VERIFY -> 5. POLICY GATE`) and automatically classifies each action as **🟢 AUTONOMOUS** (low risk, auto-executed in sandbox) or **🟡 REQUIRES HIL APPROVAL** (high impact, interactive Human-In-The-Loop confirmation gate).
2. **Executive Investigation Recap (`ExecutiveRecapCard`)**: Executive summary of diagnostic strategy, findings, and constraints (`OBSERVATION_TYPE_INVESTIGATION_RECAP`).
3. **Ranked Root-Cause Hypotheses & Clickable Sandbox CLI Execution (`HypothesesCard`)**: AI confidence relevance scores (`[-1.0, 1.0]`), clear root cause explanations, and **Interactive Clickable `⚡ Run in Sandbox` buttons** that execute `gcloud` fix commands directly against `/api/execute-remediation`.
4. **Autonomous Parallel Sandbox Subagents (`ParallelSandboxCard`)**: Implements the official **Google Antigravity Managed Agent Sandbox pattern (`generativelanguage.googleapis.com/v1beta/interactions`)**. Dispatches parallel subagents inside independent Linux sandboxes (`Subagent-1`, `Subagent-2`, `Subagent-N`) and consolidates 100% of execution traces into a unified self-healing report (`/api/orchestrate-parallel`).
5. **Proactive Remediation Roadmap (`RemediationStepsCard`)**: Formats recovery instructions into structured interactive cards with inline parameter highlighting (`STEP 01`, `STEP 02`, `STEP 03`).
6. **Autonomous ReAct Diagnostic Trace (`ReActEvidenceCard`)**: Complete audit trace of live `gcloud` check queries (`gcloud run services describe...`, `gcloud sql operations list...`) and pass/fail indicators (`OBSERVATION_TYPE_OTHER`).

### 3. Way-Right Side Panel — Google ADK Agent (`gemini-3.1-flash-lite` GA • Global) + Google Search & Claude "Ink" Spinner
- **Agentic Chatbot (`ChatbotDrawer`)**: Powered by **GA `gemini-3.1-flash-lite` in region `global`** per user preference, achieving **6.6X FASTER execution (`2,733 ms` / `2.7s` vs `18.0s`)** compared to 2.5 Flash.
- **Rich Visual Output Formatting (`RichTextRenderer`)**: Automatically transforms markdown headings (`###`), numbered steps, bullet points, and code blocks (````bash`) into interactive visual section badges (`📌`), emerald checklists, and dark glassmorphic Code Boxes equipped with One-Click `Copy` and `⚡ Run in Sandbox` buttons.
- **Built-In Google Search (`google_search`)**: Autonomously searches Reddit (`r/googlecloud`), StackOverflow, and official Google Cloud documentation for verified edge-case fixes.
- **Claude Code "Ink" Spinner (`ClaudeInkSpinner`)**: Dynamic, glowing multi-bar gradient waveform animation displayed while the agent thinks and queries tools.

---

## 📂 Project Structure (Production vs. Testing Separation)

```
cloud-assist-error-remediation-hub/
├── README.md                           # Documentation & architecture overview
├── backend/                            # Production FastAPI backend + Google ADK agent
│   ├── pyproject.toml                  # Managed strictly by uv
│   ├── main.py                         # FastAPI server listening on 127.0.0.1:8088
│   ├── app/
│   │   ├── config.py                   # load_dotenv(override=True) + explicit GCP project/region
│   │   ├── services/
│   │   │   ├── cloud_logging_service.py # Cloud Logging telemetry query + time filter
│   │   │   ├── cloud_assist_service.py  # 4-step Gemini Cloud Assist REST API orchestrator
│   │   │   └── adk_chatbot_service.py   # Google ADK agent + built-in google_search
│   │   └── models/
│   │       └── schemas.py              # Pydantic structured schemas
├── frontend/                           # Production Vite React 19 + TypeScript + Tailwind CSS UI
│   ├── package.json
│   ├── vite.config.ts                  # Serves on 127.0.0.1:5173
│   └── src/
│       ├── App.tsx                     # Main dashboard layout
│       └── components/                 # Glassmorphic panels & dynamic Claude Code Ink animation
└── tests/                              # SEPARATED TESTING FOLDER (Isolated from production)
    └── backend_tests/
        └── test_services.py            # Automated pytest suite (uv run pytest)
```

---

## 🚀 Running Locally

### 1. Run Production Backend (`backend/`)
```bash
cd backend
uv run --default-index https://pypi.org/simple python main.py
# Serves API on http://127.0.0.1:8088
```

### 2. Run Production Frontend (`frontend/`)
```bash
cd frontend
npm run dev
# Open UI at http://127.0.0.1:5180
```

### 3. Run Automated Tests (`tests/`)
```bash
cd backend
uv run --default-index https://pypi.org/simple pytest ../tests/backend_tests/test_services.py
```
