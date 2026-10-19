# `[3.2]` Self-Service Payoff Quote & IRS Form 1098 Voice/Chat Bot

> **Dedicated Standalone Microservice Repository** (Separated from the 5-Pillar Flagship Studio)  
> **Bespoke App:** **Mr. Cooper Self-Service // Official Per-Diem Payoff Quote & IRS Form 1098 Generator** (`payoff_1098_document_generator`)  
> **Department:** 3. Client Experience & Servicing (Mr. Cooper Portfolio, Escrow, Synopsis & Recapture) (`L200`)  
> **Default Model & Runtime:** `Google ADK + Vertex AI Agent Engine Runtime (gemini-3.8-flash)`

---

## 🔗 Live Links & Resources

| Resource | Direct Link | Credentials / Notes |
| :--- | :--- | :--- |
| **🚀 Launch Live Interactive Sandbox** | [`https://rocket-hackathon-portal-254356041555.us-central1.run.app/square/3.2`](https://rocket-hackathon-portal-254356041555.us-central1.run.app/square/3.2) | Shared Login: `rocket` / `Argon2026!` |
| **📘 Hosted Blueprint & Reproduction Guide** | [`https://rocket-hackathon-portal-254356041555.us-central1.run.app/docs/3.2`](https://rocket-hackathon-portal-254356041555.us-central1.run.app/docs/3.2) | Step-by-step GCP guide & architecture |
| **🌐 Unified Single Source of Truth Portal** | [`https://rocket-hackathon-portal-254356041555.us-central1.run.app/`](https://rocket-hackathon-portal-254356041555.us-central1.run.app/) | Master Hub (Tab 4: Reference Library) |
| **🧠 Agent Skill Definition (`SKILL.md`)** | [`SKILL.md`](./SKILL.md) | Antigravity / Gemini CLI reusable skill |

---

## 💻 Source Code in This Standalone Repository

| File / Module | Purpose & Architectural Role | Stack & Model |
| :--- | :--- | :--- |
| [`app.py`](./app.py) | Standalone FastAPI server (`PORT=8080`) serving the bespoke UI + `/api/sandbox` + `/api/run` | `FastAPI`, `Uvicorn` |
| [`code/agent.py`](./code/agent.py) | Structured Vertex AI GenAI runner combining deterministic sandbox metrics with LLM synthesis | `gemini-3.8-flash` |
| [`code/sandbox_tool.py`](./code/sandbox_tool.py) | Deterministic Python gVisor calculation verifier & bespoke visual artifact builder | `Python 3.12` |
| [`ui/sq_3_2.py`](./ui/sq_3_2.py) | Custom UI renderer for **Mr. Cooper Self-Service // Official Per-Diem Payoff Quote & IRS Form 1098 Generator** (`payoff_1098_document_generator`) | `HTML5 / CSS3 / JS` |
| [`ui/standalone_app.html`](./ui/standalone_app.html) | Pre-rendered zero-dependency standalone HTML application | `payoff_1098_document_generator` |
| [`SKILL.md`](./SKILL.md) | Agent skill contract with UI token palette, controls, and JSON output schema | `Antigravity / ADK` |
| [`mock_data/sample_payload.json`](./mock_data/sample_payload.json) | Realistic Rocket Mortgage / Redfin / Mr. Cooper test payload & verified output | `JSON` |
| [`Dockerfile`](./Dockerfile) & [`requirements.txt`](./requirements.txt) | 1-command Cloud Run deployment container definition | `Cloud Run` |

---

## ⚡ Quickstart: Run This Demo Standalone (`< 2 Minutes`)

```bash
# 1. Clone the repository and enter THIS specific demo's standalone folder
git clone https://github.com/jchavezar/vertex-ai-samples.git
cd vertex-ai-samples/semiautonomous-agents/rocket-ai-hackathon-argon-suite/03-servicing-and-mister-cooper/3_2-self-service-payoff-quote-irs-form-1098-voice-ch

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
gcloud run deploy rocket-square-3-2 \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars="GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID,GOOGLE_CLOUD_LOCATION=global"
```
