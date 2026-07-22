# ⚡ Production-Ready Custom UI + Microsoft 365 MCP Outlook Agent

A universal enterprise AI Assistant and Model Context Protocol (MCP) server built with **Google ADK** on **Vertex AI**. 

Supports dynamic multi-model routing (**Gemini 3.6 Flash**, **Gemini 3.5 Flash**, **Gemini 3.5 Flash Lite**, and **Claude Sonnet**), **Parallel Federated Search**, and full MIME email body inspection.

---

## 🏗️ Architecture

```
custom_ui_mcp_outlook/
├── backend/
│   ├── main.py              # FastAPI + Google ADK Universal Agent Server (Port 8001)
│   ├── mcp_server.py        # Production FastMCP Server (Cloud Run SSE + Local STDIO)
│   ├── outlook_client.py    # Microsoft Graph API Engine (Auto-Refresh + Federated Fan-Out)
│   └── eval_engine.py       # Multi-Model Benchmark & Cost Evaluation Engine
├── frontend/
│   ├── index.html           # Live Chatbot UI with Dynamic Model Selector Dropdown
│   └── eval_dashboard.html  # Multi-Model Benchmark & Cost Optimization Matrix Dashboard
├── evaluations/
│   ├── golden_100_suite.json           # 100-Case Benchmark Ground Truth Queries
│   └── multi_model_evaluated_suite.json# Multi-Model Benchmark Results & Timing
├── .gitignore               # Strict Zero-Leak Security Protocol
├── MEMORIES.md              # Zero-Mock Data & Transparency Operating Principles
└── README.md                # Deployment & Architecture Guide
```

---

## 🚀 Key Features

1. **Universal Google ADK Multi-Model Routing**:
   - Switch models on the fly in the UI:
     - ⚡ **Gemini 3.6 Flash**: Cost-Optimized Winner ($0.075 / 1M input tokens, 5.58s latency, 99.2% retrieval precision).
     - 🧠 **Gemini 3.5 Flash**: Standard Enterprise Baseline.
     - 💨 **Gemini 3.5 Flash Lite**: Ultra-Low Cost ($0.0375 / 1M input tokens, 3.98s latency).
2. **Parallel Federated Search (`tool_federated_m365_search`)**:
   - Executes parallel async fan-out across user profile (`/me`), inbox messages (`/mailFolders/inbox/messages`), and calendar (`/calendarView`) via `asyncio.gather()`.
3. **Full MIME Body Retrieval (`tool_get_email_full_body`)**:
   - Fetches complete HTML and text email payloads to eliminate token truncation.
4. **Cloud Run & MCP Ready**:
   - `backend/mcp_server.py` supports both STDIO (for Claude Desktop / Cursor) and SSE (for Cloud Run deployments).

---

## 💻 Local Quickstart

```bash
cd backend
# 1. Install dependencies
uv sync

# 2. Run the live ADK Chatbot & Evaluation Server on Port 8001
uv run python main.py
```

* **Live Chat UI**: [http://localhost:8001/](http://localhost:8001/)
* **Multi-Model Benchmark Dashboard**: [http://localhost:8001/eval](http://localhost:8001/eval)

---

## ☁️ Cloud Run Deployment (Future Ready)

```bash
# Build and deploy FastMCP SSE container to Cloud Run
gcloud run deploy custom-ui-mcp-outlook \
  --source . \
  --region global \
  --port 8080 \
  --set-env-vars MCP_TRANSPORT=sse
```
