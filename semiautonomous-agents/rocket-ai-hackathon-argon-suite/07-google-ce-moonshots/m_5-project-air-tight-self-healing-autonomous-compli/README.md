# `[M.5]` Project Air-Tight: Self-Healing Autonomous Compliance Swarm

> **Dedicated Standalone Microservice Repository** (Separated from the 5-Pillar Flagship Studio)  
> **Bespoke App:** **Project Air-Tight // Autonomous 4-Stage Self-Healing Closing Disclosure Pipeline** (`project_airtight_self_healing_pipeline`)  
> **Department:** 7. Google Customer Engineering Moonshots (Disruptive Gemini 4 Argon Prototypes) (`L300`)  
> **Default Model & Runtime:** `Google ADK + Vertex AI Agent Engine Runtime (gemini-3.8-flash)`

---

## 🔗 Live Links & Resources

| Resource | Direct Link | Credentials / Notes |
| :--- | :--- | :--- |
| **🚀 Launch Live Interactive Sandbox** | [`https://rocket-hackathon-portal-254356041555.us-central1.run.app/square/M.5`](https://rocket-hackathon-portal-254356041555.us-central1.run.app/square/M.5) | Shared Login: `rocket` / `Argon2026!` |
| **📘 Hosted Blueprint & Reproduction Guide** | [`https://rocket-hackathon-portal-254356041555.us-central1.run.app/docs/M.5`](https://rocket-hackathon-portal-254356041555.us-central1.run.app/docs/M.5) | Step-by-step GCP guide & architecture |
| **🌐 Unified Single Source of Truth Portal** | [`https://rocket-hackathon-portal-254356041555.us-central1.run.app/`](https://rocket-hackathon-portal-254356041555.us-central1.run.app/) | Master Hub (Tab 4: Reference Library) |
| **🧠 Agent Skill Definition (`SKILL.md`)** | [`SKILL.md`](./SKILL.md) | Antigravity / Gemini CLI reusable skill |

---

## 💻 Source Code in This Standalone Repository

| File / Module | Purpose & Architectural Role | Stack & Model |
| :--- | :--- | :--- |
| [`app.py`](./app.py) | Standalone FastAPI server (`PORT=8080`) serving the bespoke UI + `/api/sandbox` + `/api/run` | `FastAPI`, `Uvicorn` |
| [`code/agent.py`](./code/agent.py) | Structured Vertex AI GenAI runner combining deterministic sandbox metrics with LLM synthesis | `gemini-3.8-flash` |
| [`code/sandbox_tool.py`](./code/sandbox_tool.py) | Deterministic Python gVisor calculation verifier & bespoke visual artifact builder | `Python 3.12` |
| [`ui/sq_m_5.py`](./ui/sq_m_5.py) | Custom UI renderer for **Project Air-Tight // Autonomous 4-Stage Self-Healing Closing Disclosure Pipeline** (`project_airtight_self_healing_pipeline`) | `HTML5 / CSS3 / JS` |
| [`ui/standalone_app.html`](./ui/standalone_app.html) | Pre-rendered zero-dependency standalone HTML application | `project_airtight_self_healing_pipeline` |
| [`SKILL.md`](./SKILL.md) | Agent skill contract with UI token palette, controls, and JSON output schema | `Antigravity / ADK` |
| [`mock_data/sample_payload.json`](./mock_data/sample_payload.json) | Realistic Rocket Mortgage / Redfin / Mr. Cooper test payload & verified output | `JSON` |
| [`Dockerfile`](./Dockerfile) & [`requirements.txt`](./requirements.txt) | 1-command Cloud Run deployment container definition | `Cloud Run` |

---

## ⚡ Quickstart: Run This Demo Standalone (`< 2 Minutes`)

```bash
# 1. Clone the repository and enter THIS specific demo's standalone folder
git clone https://github.com/jchavezar/vertex-ai-samples.git
cd vertex-ai-samples/semiautonomous-agents/rocket-ai-hackathon-argon-suite/07-google-ce-moonshots/m_5-project-air-tight-self-healing-autonomous-compli

# 2. Install dependencies & configure environment
pip install -r requirements.txt
cp .env.example .env

# 3. Verify the deterministic sandbox & agent runner in CLI
python3 -m code.sandbox_tool
python3 -m code.agent

# 4. Launch the standalone web microservice on http://localhost:8080
uvicorn app:app --host 0.0.0.0 --port 8080
```

### Deploy This Single Demo to Cloud Run

```bash
gcloud run deploy rocket-square-m-5 \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars="GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID,GOOGLE_CLOUD_LOCATION=global"
```
