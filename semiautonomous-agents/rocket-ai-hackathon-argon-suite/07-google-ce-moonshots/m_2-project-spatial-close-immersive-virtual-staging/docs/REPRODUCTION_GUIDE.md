# Square `[M.2]`: Project Spatial Close: Immersive Virtual Staging & 3D Neighborhood Hub — Reproduction, Bespoke UI & Skill Guide

| Field | Value |
| :--- | :--- |
| **Square Code** | `M.2` |
| **Bespoke Application Title** | **Project Spatial Close // 3D Royal Oak Neighborhood Solar & Fannie HomeStyle Renovation Hub** (`project_spatial_close_3d_homestyle`) |
| **Business Domain** | 7. Google Customer Engineering Moonshots (Disruptive Gemini 4 Argon Prototypes) (`rocket-demo-moonshots`) |
| **Complexity Level** | `L300` |
| **Active Model & Runtime** | **`gemini-4-argon`** — Vertex AI Global Endpoint (gemini-4-argon) + Antigravity gVisor Sandbox |
| **Live Interactive Demo** | [https://rocket-hackathon-portal-254356041555.us-central1.run.app/square/M.2](https://rocket-hackathon-portal-254356041555.us-central1.run.app/square/M.2) *(Username: `rocket` / Password: `Argon2026!`)* |
| **Hosted Cloud Blueprint** | [https://rocket-hackathon-portal-254356041555.us-central1.run.app/docs/M.2](https://rocket-hackathon-portal-254356041555.us-central1.run.app/docs/M.2) |
| **Real Gemini Enterprise UI** | [Open Real Gemini Enterprise Web UI (`gemini-enterprise-17877637_1787763712023`)](https://vertexaisearch.cloud.google.com/home/cid/gemini-enterprise-17877637_1787763712023) · [Open Sobi (`/work`)](https://gemini.google.com/work) |
| **Agent Reproduction Skill** | [`skills/SKILL.md`](../skills/SKILL.md) |

---

## 1. Executive Summary & Bespoke UX Architecture

**Focus:** Combine conversational 3D interior staging + solar/renovation ROI with Google Maps Photorealistic 3D neighborhood flybys and equity projections.

**Description:**  
Let Redfin buyers remodel a fixer-upper with their voice ('Knock down this non-load-bearing kitchen wall, add a quartz waterfall island, and finance the $45,000 remodel into a Fannie Mae HomeStyle Renovation loan') while inspecting 5-year neighborhood appreciation.

**Bespoke UI Archetype (`project_spatial_close_3d_homestyle`):**  
Rather than displaying a generic text response, Square `[M.2]` renders **Project Spatial Close // 3D Royal Oak Neighborhood Solar & Fannie HomeStyle Renovation Hub** with structured visual artifacts (`Return JSON with keys: instant_equity_created, homestyle_vs_heloc ({homestyle_single_pi, separate_heloc_combined_pi, monthly_savings}), renovation_line_items (list of {scope_item, contractor_budget, appraised_value_add, roi_multiple}), and neighborhood_3d_telemetry ({solar_exposure, commute_to_detroit_mins, school_district}).`).

---

## 2. Competitive Win-Back Strategy (Displacing AWS Bedrock, Anthropic Claude & Sierra AI)

> **Why Google Cloud Wins:** Only Google combines frontier multimodal generation (Gemini Omni + Imagen 3) with First-Party Google Maps Photorealistic 3D Tiles and Solar API.

---

## 3. Target GCP & Antigravity Architecture

**Google Cloud Stack:** `Gemini Omni` · `Imagen 3` · `Google Maps Photorealistic 3D Tiles API` · `Gemini 4 Argon Renovation ROI Engine`

```text
┌────────────────────────────────────────────────────────────────────────┐
│     M.2 PROJECT SPATIAL CLOSE: 3D STAGING & HOMESTYLE HUB (L300)       │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [Redfin Fixer-Upper ($385k) + Voice Remodel Prompt ($55k Budget)]     │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [Imagen 3 Spatial Inpainting + Google Maps 3D Tiles + Argon Math]     │
│  ├─► Visualizes Remodeled Chef's Kitchen + 4-Season Sunroom            │
│  ├─► Computes Fannie Mae HomeStyle AIV ($485k) -> +$45k Instant Equity │
│  └─► Overlays Google Maps 3D Flyby & Rooftop Solar API Savings         │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [Interactive 3D Spatial Remodel Viewer + Single-Close Loan Approval]  │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Step-by-Step Reproduction Instructions

1. Enable Google Maps Photorealistic 3D Tiles API (`tile.googleapis.com`) and Solar API (`solar.googleapis.com`) alongside Vertex AI.
2. Use Imagen 3 mask-free conversational editing to render the before/after kitchen renovation.
3. Run `gemini-4-argon` with the Fannie Mae HomeStyle Renovation (`B5-3.2-01`) calculator to compare a single-close renovation mortgage against a post-close HELOC.

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
  "archetype": "project_spatial_close_3d_homestyle",
  "kitchen_img": "/static/images/rocket_kitchen_homestyle.jpg",
  "acq_total": "$440,000.00 ($385,000 Purchase + $55,000 Escrowed Kitchen/Sunroom Renovation)",
  "aiv_equity": "$485,000.00 -> Creates +$45,000.00 in Instant Day-1 Renovation Equity!",
  "payment": "$2,573.70/mo P&I on $418,000 Loan (Saves ~$485/mo vs separate 9.75% Second-Lien HELOC)"
}
```
