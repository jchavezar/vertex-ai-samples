# M365 Outlook Executive Assistant — Dual-Deployment Architecture

Welcome to the **M365 Outlook Executive Assistant** repository. This project showcases two complementary deployment topologies for enterprise Microsoft 365 Outlook integration:

1. **`local-adk-mcp/`**: Direct Local ADK + MSAL Implementation *(Ultra-Fast Latency Baseline)*
2. **`cloud-agent-platform/`**: Production Google Cloud Agent Platform Implementation *(Vertex AI Reasoning Engine + Agent Identity + Cloud Run MCP Gateway)*

---

## 📁 Repository Structure

```
custom_ui_mcp_outlook/
├── README.md                     # Master Repository Documentation
├── compare_latency.py            # Automated Latency Benchmark Script
│
├── local-adk-mcp/                # 100% Direct Local Deployment
│   ├── README.md                 # Local Architecture & Setup Guide
│   ├── backend/                  # FastAPI local backend & MSAL auth
│   ├── frontend/                 # Chat interface & evaluation table
│   └── evaluations/              # 100-case tri-modal benchmark suite
│
└── cloud-agent-platform/         # Agent Platform Production Deployment
    ├── README.md                 # Cloud Architecture & Deployment Guide
    ├── adk-agent/                # ADK Agent definition & Reasoning Engine deploy script
    ├── mcp-server/               # FastMCP Server deployed to Cloud Run
    └── custom-ui-production/     # Production UI frontend & SSE streaming backend
```

---

## 📊 Topology & Latency Comparison

| Topology | Model | Engine / Gateway | First Chunk Latency | Total Latency | Primary Use Case |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`local-adk-mcp`** | `gemini-3.6-flash` | Direct MSAL + Python Parallel Graph API | **1.2s** | **4.5s** | High-throughput local evaluation, testing & benchmarking |
| **`cloud-agent-platform`** | `gemini-3.6-flash` | Vertex AI Reasoning Engine + Cloud Run MCP Gateway | **8.6s** | **13.1s** | Production enterprise deployment with Agent Identity governance |

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

### 2. Production Deployment (`cloud-agent-platform`)
* 📖 **[Getting Started Guide](cloud-agent-platform/docs/getting_started.md)**
* 📐 **[Low-Level Design (LLD)](cloud-agent-platform/docs/low_level_design.md)**
```bash
cd cloud-agent-platform/custom-ui-production/backend
python3 -m uvicorn main:app --host 0.0.0.0 --port 8001
# Open Chat: http://localhost:8001/
```

### 📊 Evaluation Dashboard
* **No-Download Static Preview**: [Live HTML Evaluation Preview](https://htmlpreview.github.io/?https://github.com/jesusarguelles/vertex-ai-samples/blob/main/semiautonomous-agents/custom_ui_mcp_outlook/eval_dashboard_static.html)
* **Automated Latency Benchmark**:
  ```bash
  python3 compare_latency.py
  ```
