# M365 Outlook Executive Assistant — Dual-Deployment Architecture

Welcome to the **M365 Outlook Executive Assistant** repository. This project showcases three complementary deployment topologies and integrations for enterprise Microsoft 365 Outlook:

1. **`local-adk-mcp/`**: Direct Local ADK + MSAL Implementation *(Ultra-Fast Latency Baseline)*
2. **`remote-agentruntime-mcp/`**: Production Google Cloud Agent Platform Implementation *(Vertex AI Reasoning Engine + Agent Identity + Cloud Run MCP Gateway)*
3. **`ge-streamassist/`**: Split-Pane Executive Chat & Approvals Sandbox *(Gemini Enterprise streamAssist + MS Graph direct reply pipeline)*

---

## 📁 Repository Structure

```
custom_ui_mcp_outlook/
├── README.md                     # Master Repository Documentation
│
├── docs/
│   └── security_and_identity.md  # Unified Entra ID, WIF, and IAM trust guide
│
├── screenshots/                  # High-resolution screenshots of each solution
│
├── evaluations/                  # 100-case tri-modal benchmark suite and metrics
│   ├── eval_dashboard_static.html# Visual performance dashboard
│   ├── golden_100_suite.json     # Ground truth Q&A dataset
│   └── update_tri_modal.py       # Metrics processing & dashboard generation script
│
├── local-adk-mcp/                # 100% Direct Local Deployment
│   ├── README.md                 # Local Architecture & Setup Guide
│   ├── backend/                  # FastAPI local backend & MSAL auth
│   └── docs/                     # LLD and configuration guides
│
├── remote-agentruntime-mcp/      # Agent Platform Production Deployment
│   ├── README.md                 # Cloud Architecture & Deployment Guide
│   ├── adk-agent/                # ADK Agent definition & Reasoning Engine deploy script
│   ├── mcp-server/               # FastMCP Server deployed to Cloud Run
│   └── custom-ui-production/     # Production UI frontend & SSE streaming backend
│
└── ge-streamassist/              # Split-pane Executive Workspace sandbox
    ├── README.md                 # Sandbox Architecture & Approvals Guide
    ├── backend/                  # FastAPI streamAssist backend
    └── frontend/                 # React split-pane inbox dashboard
```

---

## 📊 Topology & Latency Comparison

| Topology | Model | Engine / Gateway | First Chunk Latency | Total Latency | Primary Use Case |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`local-adk-mcp`** | `gemini-3.6-flash` | Direct MSAL + Python Parallel Graph API | **1.2s** | **4.5s** | High-throughput local evaluation, testing & benchmarking |
| **`remote-agentruntime-mcp`** | `gemini-3.6-flash` | Vertex AI Reasoning Engine + Cloud Run MCP Gateway | **8.6s** | **13.1s** | Production enterprise deployment with Agent Identity governance |
| **`ge-streamassist`** | `gemini-3.6-flash` | Search App streamAssist + WIF Identity | **0.9s** | **3.8s** | Split-pane visual approvals and direct reply integrations |

---

## 🎨 UI/UX Features Highlights

* **Yazdani Star Spinner (`✳ ✻ ❋ ✽ ※ ✷ ✸`)**: Morphing star animation with glow effect while model reasons.
* **Animated Sweep Text**: Shimmer gradient text (`Analyzing intent & Microsoft Graph data...`).
* **Live Execution Timer**: Real-time millisecond counter (`⏱️ X.Xs`).
* **Ultra-Compact Tool Accordion**: Collapsible details trace element (`🛠️ Triggered Tools`) that keeps the chat window 100% clean.
* **Dynamic OAuth Button Visibility**: Auto-hides "Connect Outlook" when connected state is active.

---

## 🚀 Quick Start & Documentation Index

### 1. Local Deployment (`local-adk-mcp`)
* 📖 **[Getting Started Guide](local-adk-mcp/docs/getting_started.md)**
* 📐 **[Low-Level Design (LLD)](local-adk-mcp/docs/low_level_design.md)**
```bash
cd local-adk-mcp
PYTHONPATH=. .venv/bin/python3 backend/main.py
# Open Chat: http://localhost:8005/
# Open Evaluation: http://localhost:8005/eval
```

### 2. Production Deployment (`remote-agentruntime-mcp`)
* 📖 **[Getting Started Guide](remote-agentruntime-mcp/docs/getting_started.md)**
* 📐 **[Low-Level Design (LLD)](remote-agentruntime-mcp/docs/low_level_design.md)**
```bash
cd remote-agentruntime-mcp/custom-ui-production/backend
python3 -m uvicorn main:app --host 0.0.0.0 --port 8001
# Open Chat: http://localhost:8001/
```

### 📊 Evaluation Dashboard
* **No-Download Static Preview**: [Live HTML Evaluation Preview](https://htmlpreview.github.io/?https://github.com/jesusarguelles/vertex-ai-samples/blob/main/semiautonomous-agents/custom_ui_mcp_outlook/evaluations/eval_dashboard_static.html)
* **Automated Latency Benchmark**:
  ```bash
  python3 evaluations/compare_latency.py
  ```
