---
name: replicating-adk-gemini-enterprise-e2e
description: Expert guide for building, testing, deploying, and registering Google ADK Agents to Vertex AI Agent Engine with Cloud Trace, Cloud Logging, and Gemini Enterprise.
---

# Replicating ADK Agent on Vertex AI Agent Engine & Gemini Enterprise

This skill provides step-by-step instructions for Antigravity agents to reproduce, deploy, verify, and demonstrate an enterprise ADK Agent from scratch, with automated **EBC Fast-Path Layer** for instant live boardroom demos.

---

## ⚡ EBC Fast-Demo Mode (Zero-Wait Live Presentations)

When presenting to customers in an Executive Briefing Center (EBC) or re-running demonstrations:

1. **Instant Health & Re-Use Check (< 1s)**:
   ```bash
   # Reuses live Vertex AI Reasoning Engine & Gemini Enterprise Agent instantly
   cd semiautonomous-agents/adk-gemini-enterprise-e2e
   uv run python deploy.py
   uv run python register.py
   ```
2. **Instant Live Boardroom Test (< 2s)**:
   ```bash
   uv run python scripts/test_gemini_enterprise.py "Perform an acquisition valuation for Apex Global ($650M EBITDA, 9.5% growth, 9% WACC, 13x exit multiple) and audit under SR 11-7."
   ```

3. **Forcing Cold Rebuilds / Fresh Code Changes**:
   * If code changes or fresh cloud provisioning is explicitly requested:
     ```bash
     uv run python deploy.py new
     uv run python register.py new
     ```

---

## 🛠️ Step-by-Step Reproduction Blueprint (From Scratch)

### ⚠️ Mandatory HITL Checkpoint
If `PROJECT_ID`, `REGION`, `STAGING_BUCKET`, or `GE_PROJECT_NUMBER` are not in `.env`, the agent must ask:
> "Ask the human for PROJECT_ID, REGION, STAGING_BUCKET, and GE_PROJECT_NUMBER before proceeding if they are not in .env. Do NOT proceed until confirmed."

### Dependencies
```bash
uv add "google-cloud-aiplatform[adk,agent_engines]" google-genai requests google-auth rich pydantic cloudpickle python-dotenv
```

### 1. Environment & Setup
Verify ADC authentication and staging bucket:
```bash
uv run agy-recipes/adk-gemini-enterprise-e2e/scripts/setup.py
```

### 2. Local Agent Smoke Testing (Offline)
Run the offline ADK runner to verify tool declarations and function calls:
```bash
cd semiautonomous-agents/adk-gemini-enterprise-e2e
uv run python scripts/test_local.py
```

### 3. Deploy to Vertex AI Agent Engine Runtime
Deploys `reasoning_engines.AdkApp` with `enable_tracing=True` for OpenTelemetry, Cloud Trace, and Cloud Logging:
```bash
uv run python deploy.py
```

### 4. Register into Gemini Enterprise
Registers the deployed Reasoning Engine with Discovery Engine v1alpha Assist API and shares it with `ALL_USERS`:
```bash
uv run python register.py
```

### 5. Verification via Live Gemini Enterprise A2A
Test the live agent via Discovery Engine A2A stream endpoint:
```bash
uv run python scripts/test_gemini_enterprise.py
```
