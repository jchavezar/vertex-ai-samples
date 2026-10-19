# Square `[2.5]`: Rocket Close (Amrock) Title Exception & Municipal Lien Matcher — Reproduction, Bespoke UI & Skill Guide

| Field | Value |
| :--- | :--- |
| **Square Code** | `2.5` |
| **Bespoke Application Title** | **Rocket Close (Amrock) // Schedule B-II Title Exception & ALTA Endorsement Clearer** (`amrock_title_curative_map`) |
| **Business Domain** | 2. Operations, Underwriting & Closing (Rocket Logic Fulfillment & Rocket Close Title) (`rocket-demo-underwriting`) |
| **Complexity Level** | `L300` |
| **Active Model & Runtime** | **`gemini-3.8-flash`** — Gemini Enterprise streamAssist API (v1alpha) + gemini-3.8-flash |
| **Live Interactive Demo** | [https://rocket-hackathon-portal-254356041555.us-central1.run.app/square/2.5](https://rocket-hackathon-portal-254356041555.us-central1.run.app/square/2.5) *(Username: `rocket` / Password: `Argon2026!`)* |
| **Hosted Cloud Blueprint** | [https://rocket-hackathon-portal-254356041555.us-central1.run.app/docs/2.5](https://rocket-hackathon-portal-254356041555.us-central1.run.app/docs/2.5) |
| **Real Gemini Enterprise UI** | [Open Real Gemini Enterprise Web UI (`gemini-enterprise-17877637_1787763712023`)](https://vertexaisearch.cloud.google.com/home/cid/gemini-enterprise-17877637_1787763712023) · [Open Sobi (`/work`)](https://gemini.google.com/work) |
| **Agent Reproduction Skill** | [`skills/SKILL.md`](../skills/SKILL.md) |

---

## 1. Executive Summary & Bespoke UX Architecture

**Focus:** Ground title clearance decisions against Rocket Close precedent repositories and ALTA endorsement rules to eliminate curative bottlenecks.

**Description:**  
When a Schedule B-II Title Commitment reveals an unreleased prior mortgage, solar UCC-1 fixture filing, or Detroit utility easement, cross-reference Rocket Close curative precedents and ALTA endorsement standards automatically.

**Bespoke UI Archetype (`amrock_title_curative_map`):**  
Rather than displaying a generic text response, Square `[2.5]` renders **Rocket Close (Amrock) // Schedule B-II Title Exception & ALTA Endorsement Clearer** with structured visual artifacts (`Return JSON with keys: clear_to_close_status, schedule_b_exceptions (list of {item_no, defect_type, description, curative_resolution, treaty_or_alta_ref, auto_cleared}), and dispatched_vendor_packets (list of strings).`).

---

## 2. Competitive Win-Back Strategy (Displacing AWS Bedrock, Anthropic Claude & Sierra AI)

> **Why Google Cloud Wins:** Matches title exceptions against 10M+ historical Amrock / Rocket Close curative files in BigQuery + Vertex AI Search in <800ms.

---

## 3. Target GCP & Antigravity Architecture

**Google Cloud Stack:** `Vertex AI Search & Grounding` · `Gemini 4 Argon` · `BigQuery Title Precedent Store`

```text
┌────────────────────────────────────────────────────────────────────────┐
│     2.5 ROCKET CLOSE TITLE EXCEPTION & LIEN MATCHER (L300 GROUNDING)   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [Schedule B-II Title Commitment: Unreleased Lien, Easement, UCC-1]    │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [Vertex AI Grounding: Rocket Close / Amrock Curative Knowledge Base]  │
│  ├─► Michigan Mutual Indemnity Treaty Database                         │
│  ├─► Fannie Mae B7-2-05 Acceptable Title Exceptions                    │
│  └─► ALTA Endorsement Manual (ALTA 9, ALTA 28.1, UCC-3 Solar Rules)    │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [Curative Clearance Memo + Auto-Dispatched Sunrun UCC-3 Subordination]│
└────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Step-by-Step Reproduction Instructions

1. Index Rocket Close (Amrock) curative underwriting bulletins, state mutual indemnity treaties, and ALTA endorsement guides into a Vertex AI Search datastore.
2. Pass Schedule B-II exceptions from the title commitment into `gemini-4-argon` with Vertex AI Grounding enabled.
3. Output structured clearance status (`AUTO_CLEARED_INDEMNITY`, `CLEARED_WITH_ALTA_ENDORSEMENT`, or `REQUIRES_SUBORDINATION`) directly to the Rocket Close portal.

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
  "archetype": "amrock_title_curative_map",
  "status": "CONDITIONAL CLEAR TO CLOSE (1 Automated Vendor Subordination Pending)",
  "exceptions": [
    {
      "item": "Schedule B-II Item #8",
      "defect": "Unreleased 2018 Prior Mortgage ($210k Flagstar)",
      "resolution": "AUTO-CLEARED \u2014 Covered under Michigan Master Mutual Indemnity Treaty + 2021 Payoff Receipt",
      "state": "CLEARED"
    },
    {
      "item": "Schedule B-II Item #11",
      "defect": "0.4 ft Roof Eave Overhang into DTE Utility Easement",
      "resolution": "AUTO-CLEARED \u2014 Minor 0.4 ft roof eave overhang insured via ALTA 28.1 Encroachment Endorsement",
      "state": "CLEARED"
    },
    {
      "item": "Schedule B-II Item #14",
      "defect": "Active UCC-1 Solar Fixture Filing (Sunrun Inc.)",
      "resolution": "ACTION DISPATCHED \u2014 Auto-requested Sunrun Standard Fannie Mae UCC-3 Subordination Agreement",
      "state": "DISPATCHED"
    }
  ]
}
```
