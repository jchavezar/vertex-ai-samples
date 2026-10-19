# `[2.3]` Automated W-2 & Paystub Entity Extraction & Variance Pipeline

> **Dedicated Standalone Microservice Repository** (Separated from the 5-Pillar Flagship Studio)  
> **Bespoke App:** **Google Cloud Document AI // W-2 & Paystub OCR Bounding-Box & 5% Variance Inspector** (`docai_paystub_w2_ocr_inspector`)  
> **Department:** 2. Operations, Underwriting & Closing (Rocket Logic Fulfillment & Rocket Close Title) (`L200–L300`)  
> **Default Model & Runtime:** `Vertex AI Global Endpoint (gemini-4-argon) + Antigravity gVisor Sandbox`

---

## 🔗 Live Links & Resources

| Resource | Direct Link | Credentials / Notes |
| :--- | :--- | :--- |
| **🚀 Launch Live Interactive Sandbox** | [`https://rocket-hackathon-portal-254356041555.us-central1.run.app/square/2.3`](https://rocket-hackathon-portal-254356041555.us-central1.run.app/square/2.3) | Shared Login: `rocket` / `Argon2026!` |
| **📘 Hosted Blueprint & Reproduction Guide** | [`https://rocket-hackathon-portal-254356041555.us-central1.run.app/docs/2.3`](https://rocket-hackathon-portal-254356041555.us-central1.run.app/docs/2.3) | Step-by-step GCP guide & architecture |
| **🌐 Unified Single Source of Truth Portal** | [`https://rocket-hackathon-portal-254356041555.us-central1.run.app/`](https://rocket-hackathon-portal-254356041555.us-central1.run.app/) | Master Hub (Tab 4: Reference Library) |
| **🧠 Agent Skill Definition (`SKILL.md`)** | [`SKILL.md`](./SKILL.md) | Antigravity / Gemini CLI reusable skill |

---

## 💻 Source Code in This Standalone Repository

| File / Module | Purpose & Architectural Role | Stack & Model |
| :--- | :--- | :--- |
| [`app.py`](./app.py) | Standalone FastAPI server (`PORT=8080`) serving the bespoke UI + `/api/sandbox` + `/api/run` | `FastAPI`, `Uvicorn` |
| [`code/agent.py`](./code/agent.py) | Structured Vertex AI GenAI runner combining deterministic sandbox metrics with LLM synthesis | `gemini-4-argon` |
| [`code/sandbox_tool.py`](./code/sandbox_tool.py) | Deterministic Python gVisor calculation verifier & bespoke visual artifact builder | `Python 3.12` |
| [`ui/sq_2_3.py`](./ui/sq_2_3.py) | Custom UI renderer for **Google Cloud Document AI // W-2 & Paystub OCR Bounding-Box & 5% Variance Inspector** (`docai_paystub_w2_ocr_inspector`) | `HTML5 / CSS3 / JS` |
| [`ui/standalone_app.html`](./ui/standalone_app.html) | Pre-rendered zero-dependency standalone HTML application | `docai_paystub_w2_ocr_inspector` |
| [`SKILL.md`](./SKILL.md) | Agent skill contract with UI token palette, controls, and JSON output schema | `Antigravity / ADK` |
| [`mock_data/sample_payload.json`](./mock_data/sample_payload.json) | Realistic Rocket Mortgage / Redfin / Mr. Cooper test payload & verified output | `JSON` |
| [`Dockerfile`](./Dockerfile) & [`requirements.txt`](./requirements.txt) | 1-command Cloud Run deployment container definition | `Cloud Run` |

---

## ⚡ Quickstart: Run This Demo Standalone (`< 2 Minutes`)

```bash
# 1. Clone the repository and enter THIS specific demo's standalone folder
git clone https://github.com/jchavezar/vertex-ai-samples.git
cd vertex-ai-samples/semiautonomous-agents/rocket-ai-hackathon-argon-suite/02-underwriting-and-closing/2_3-automated-w-2-paystub-entity-extraction-variance

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
gcloud run deploy rocket-square-2-3 \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars="GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID,GOOGLE_CLOUD_LOCATION=global"
```
