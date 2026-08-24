# Recipe: Legacy to AI-Native Modernization Hub

This recipe automates the deployment, health verification, and teardown of the **Antigravity Legacy to AI-Native Modernization Hub** (Executive Briefing Center Showcase).

---

## Overview

- **Source Code Location:** `semiautonomous-agents/legacy-to-ai-modernization-hub`
- **Frontend Framework:** React 19 + Tailwind CSS + Lucide Icons (Port: `5178`)
- **Backend Framework:** Python FastAPI + Uvicorn + Google GenAI (Port: `8008`)
- **LLM Reasoning Engine:** Gemini 2.5 Flash / Gemini 3 Flash Preview
- **GCP APIs Enabled:**
  - `aiplatform.googleapis.com` (Vertex AI)
  - `generativelanguage.googleapis.com` (Google GenAI)

---

## Required IAM Permissions / Roles

When running against Google Cloud Vertex AI:
- `roles/aiplatform.user`
- `roles/serviceusage.serviceUsageViewer`

---

## Automated Execution

### Setup / Deploy
```bash
uv run agy-recipes/legacy-to-ai-modernization/scripts/setup.py
```

### Health & Verification Test
```bash
uv run agy-recipes/legacy-to-ai-modernization/scripts/test_recipe.py
```

### Teardown / Cleanup
```bash
uv run agy-recipes/legacy-to-ai-modernization/scripts/teardown.py
```
