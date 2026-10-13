# Square `[6.2]`: AI Software Factory: Autonomous PRD-to-Pull-Request Architect — Reproduction, Bespoke UI & Skill Guide

| Field | Value |
| :--- | :--- |
| **Square Code** | `6.2` |
| **Bespoke Application Title** | **Google Antigravity 2.0 Swarm // Autonomous PRD-to-Pull-Request Software Factory** (`antigravity_swarm_software_factory`) |
| **Business Domain** | 6. SDLC & AI Software Factory (CodeMender Security, Antigravity Swarm & .NET Modernization) (`rocket-demo-sdlc`) |
| **Complexity Level** | `L300` |
| **Active Model & Runtime** | **`gemini-4-argon`** — Vertex AI Global Endpoint (gemini-4-argon) + Antigravity gVisor Sandbox |
| **Live Interactive Demo** | [https://rocket-demo-sdlc-254356041555.us-central1.run.app/?case=6.2](https://rocket-demo-sdlc-254356041555.us-central1.run.app/?case=6.2) *(Username: `rocket` / Password: `Argon2026!`)* |
| **Hosted Cloud Blueprint** | [https://rocket-hackathon-portal-254356041555.us-central1.run.app/docs/6.2](https://rocket-hackathon-portal-254356041555.us-central1.run.app/docs/6.2) |
| **Real Gemini Enterprise UI** | [Open Real Gemini Enterprise Web UI (`gemini-enterprise-17877637_1787763712023`)](https://vertexaisearch.cloud.google.com/home/cid/gemini-enterprise-17877637_1787763712023) · [Open Sobi (`/work`)](https://gemini.google.com/work) |
| **Agent Reproduction Skill** | [`skills/SKILL.md`](../skills/SKILL.md) |

---

## 1. Executive Summary & Bespoke UX Architecture

**Focus:** Ingest a Rocket Product Requirements Document (PRD), spawn parallel Antigravity coding & testing subagents, execute tests in sandbox containers, and open a verified PR.

**Description:**  
Show Michael Evans (VP AI Eng) and Jenny Smolek (EVP Eng) the future of software engineering: drop a product spec into Antigravity Goal Mode, watch 4 specialized subagents (Architect, Backend Coder, Frontend Builder, QA Tester) build and verify the feature in parallel.

**Bespoke UI Archetype (`antigravity_swarm_software_factory`):**  
Rather than displaying a generic text response, Square `[6.2]` renders **Google Antigravity 2.0 Swarm // Autonomous PRD-to-Pull-Request Software Factory** with structured visual artifacts (`Return JSON with keys: pr_number_and_title, biweekly_math_verification ({standard_months, accelerated_months, years_shaved, lifetime_interest_saved}), subagent_lanes (list of 4 lanes {agent_role, workspace_branch, files_authored, test_status}), and generated_fastapi_endpoint_code.`).

---

## 2. Competitive Win-Back Strategy (Displacing AWS Bedrock, Anthropic Claude & Sierra AI)

> **Why Google Cloud Wins:** Unlike single-threaded local CLI tools (Claude Code), Antigravity Swarm runs persistent, cloud-hosted parallel subagents in isolated workspaces (`workspace='share'`) that keep working even when the developer closes their laptop.

---

## 3. Target GCP & Antigravity Architecture

**Google Cloud Stack:** `Google Antigravity 2.0 Swarm` · `Gemini Enterprise Spark (Goal Mode)` · `Gemini 4 Argon` · `Cloud Build / Cloud Run Sandbox`

```text
┌────────────────────────────────────────────────────────────────────────┐
│       6.2 AI SOFTWARE FACTORY: AUTONOMOUS PR ARCHITECT (L300)          │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [Input PRD: "Rocket Instant Bi-Weekly Principal Accelerator API"]     │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [Google Antigravity Swarm / Goal Mode (Gemini 4 Argon)]               │
│  ├─► Agent 1 (Architect): Designs OpenAPI Spec & Math Invariants       │
│  ├─► Agent 2 (Coder):     Writes FastAPI Endpoint & Amortization Loop  │
│  ├─► Agent 3 (QA Sandbox): Runs 6 Pytest edge-case tests in gVisor     │
│  └─► Agent 4 (Reviewer):   Verifies 0 lint/security issues & opens PR  │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [Verified Pull Request (#PR-4092): Shaves 6.4 Yrs & Saves $112,480]   │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Step-by-Step Reproduction Instructions

1. Launch Antigravity Swarm or `run_workflow` with `pipeline([architect_agent, coder_agent, qa_sandbox_agent, pr_reviewer_agent])`.
2. Each coding agent works in an isolated `workspace='share'` branch and executes `pytest` inside the gVisor sandbox.
3. Once all tests pass, the orchestrator submits the merged Pull Request.

### Quick Start (Run Standalone from This Folder)

```bash
# 1. Run the deterministic gVisor sandbox & bespoke artifact builder
python3 ./code/sandbox_tool.py

# 2. Execute the live gemini-4-argon structured agent
python3 ./code/agent.py
```

---

## 5. Verified Deterministic Sandbox & Bespoke Visual Artifact

```json
{
  "archetype": "antigravity_swarm_software_factory",
  "pr_status": "PR #4092 Ready to Merge \u2022 4 Subagents Completed \u2022 6/6 Sandbox Unit Tests Passed",
  "interest_saved": "$139,369.68 Saved in Total Interest",
  "years_shaved": "266 Months (22.2 Yrs) -> SHAVES 7.8 YEARS off mortgage!",
  "lanes": [
    {
      "agent": "architect-agent",
      "branch": "jj:biweekly-spec",
      "artifact": "specs/biweekly_openapi.yaml",
      "status": "\u2705 MERGED"
    },
    {
      "agent": "backend-quant-agent",
      "branch": "jj:biweekly-engine",
      "artifact": "services/amortization_biweekly.py",
      "status": "\u2705 6/6 PYTEST PASS"
    },
    {
      "agent": "ui-component-agent",
      "branch": "jj:biweekly-slider",
      "artifact": "components/BiweeklySavingsCard.tsx",
      "status": "\u2705 LIGHTHOUSE 100"
    },
    {
      "agent": "qa-security-agent",
      "branch": "jj:biweekly-audit",
      "artifact": "tests/test_truth_in_lending_apr.py",
      "status": "\u2705 REG Z VERIFIED"
    }
  ]
}
```
