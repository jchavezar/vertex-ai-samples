# Square `[M.5]`: Project Air-Tight: Self-Healing Autonomous Compliance Swarm — Reproduction, Bespoke UI & Skill Guide

| Field | Value |
| :--- | :--- |
| **Square Code** | `M.5` |
| **Bespoke Application Title** | **Project Air-Tight // Autonomous 4-Stage Self-Healing Closing Disclosure Pipeline** (`project_airtight_self_healing_pipeline`) |
| **Business Domain** | 7. Google Customer Engineering Moonshots (Disruptive Gemini 4 Argon Prototypes) (`rocket-demo-moonshots`) |
| **Complexity Level** | `L300` |
| **Active Model & Runtime** | **`gemini-3.8-flash`** — Google ADK + Vertex AI Agent Engine Runtime (gemini-3.8-flash) |
| **Live Interactive Demo** | [https://rocket-demo-moonshots-254356041555.us-central1.run.app/?case=M.5](https://rocket-demo-moonshots-254356041555.us-central1.run.app/?case=M.5) *(Username: `rocket` / Password: `Argon2026!`)* |
| **Hosted Cloud Blueprint** | [https://rocket-hackathon-portal-254356041555.us-central1.run.app/docs/M.5](https://rocket-hackathon-portal-254356041555.us-central1.run.app/docs/M.5) |
| **Real Gemini Enterprise UI** | [Open Real Gemini Enterprise Web UI (`gemini-enterprise-17877637_1787763712023`)](https://vertexaisearch.cloud.google.com/home/cid/gemini-enterprise-17877637_1787763712023) · [Open Sobi (`/work`)](https://gemini.google.com/work) |
| **Agent Reproduction Skill** | [`skills/SKILL.md`](../skills/SKILL.md) |

---

## 1. Executive Summary & Bespoke UX Architecture

**Focus:** Detect TRID/RESPA disclosure breaches via Document AI, compute the cure credit, draft the Legal Settlement Addendum, and auto-patch the LOS via a headless browser agent.

**Description:**  
The ultimate zero-touch closing guardian: scans every Closing Disclosure 96 hours before signing, detects fee tolerance or APR breaches, calculates the exact cure, drafts the addendum, and uses an Antigravity headless browser agent to apply the credit in the LOS and re-verify.

**Bespoke UI Archetype (`project_airtight_self_healing_pipeline`):**  
Rather than displaying a generic text response, Square `[M.5]` renders **Project Air-Tight // Autonomous 4-Stage Self-Healing Closing Disclosure Pipeline** with structured visual artifacts (`Return JSON with keys: final_clearance_status, total_cure_applied, pipeline_stages (list of 4 stages {stage_num, agent_name, status, defect_detected, autonomous_patch_applied, verification_hash}), and patched_closing_disclosure_diff (list of {line_item, before_value, after_value, compliance_rule}).`).

---

## 2. Competitive Win-Back Strategy (Displacing AWS Bedrock, Anthropic Claude & Sierra AI)

> **Why Google Cloud Wins:** Closes the loop from 'AI detected a compliance issue' to 'Autonomous browser agent applied the $485 Section J cure credit in the legacy LOS UI and re-verified 0 violations'.

---

## 3. Target GCP & Antigravity Architecture

**Google Cloud Stack:** `Document AI` · `Gemini 4 Argon` · `Google Antigravity Headless Browser Subagent` · `Cloud Run`

```text
┌────────────────────────────────────────────────────────────────────────┐
│      M.5 PROJECT AIR-TIGHT: SELF-HEALING COMPLIANCE SWARM (L300)       │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [Draft Closing Disclosure v1: $485 Tolerance Breach + Vesting Typo]   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [Antigravity Self-Healing Loop (Gemini 4 Argon + Browser Agent)]      │
│  ├─► 1. Computes $485.00 Section J Lender Cure Credit                  │
│  ├─► 2. Reconciles 'Marcus A. Vance' against Driver's License OCR      │
│  ├─► 3. Browser Subagent updates LOS UI & regenerates CD v2 PDF        │
│  └─► 4. Re-runs Document AI verification -> 0 Violations (CERTIFIED)   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [Certified Closing Package Dispatched to Rocket Close Signing Table]  │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Step-by-Step Reproduction Instructions

1. Trigger the Air-Tight Cloud Run pipeline when a draft Closing Disclosure PDF lands in the pre-closing GCS bucket.
2. Run Document AI + `gemini-4-argon` to compute the exact Section J tolerance cure and cross-check borrower vesting names against government ID OCR.
3. Invoke the Antigravity Browser Subagent (Playwright in gVisor sandbox) to apply the cure credit in the LOS UI and re-verify the regenerated CD PDF.

### Quick Start (Run Standalone from This Folder)

```bash
# 1. Run the deterministic gVisor sandbox & bespoke artifact builder
python3 ./code/sandbox_tool.py

# 2. Execute the live gemini-3.8-flash structured agent
python3 ./code/agent.py
```

---

## 5. Verified Deterministic Sandbox & Bespoke Visual Artifact

```json
{
  "archetype": "project_airtight_self_healing_pipeline",
  "stage1": "3 Blocking Defects Caught: $250 Appraisal Rush (0% Bucket), $235 Recording Overage (10% Bucket), Middle Initial Vesting Mismatch",
  "stage2": "Computed $485.00 Mandatory Section J Lender Tolerance Cure + Reconciled 'Marcus A. Vance' to Michigan Driver's License OCR",
  "stage3": "Headless Playwright Subagent applied $485.00 Section J credit in LOS & regenerated Closing Disclosure v2 PDF",
  "stage4": "0 Violations Remaining \u2014 CERTIFIED CLEAR TO CLOSE (71 Hours Prior to Signing)"
}
```
