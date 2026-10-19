# Square `[4.2]`: Virtual Staging & Localized Hero Ad Creator — Reproduction, Bespoke UI & Skill Guide

| Field | Value |
| :--- | :--- |
| **Square Code** | `4.2` |
| **Bespoke Application Title** | **Nano Banana 2 / Gempix-2 // Interactive Corktown Loft Virtual Staging & TILA Ad Studio** (`imagen_virtual_staging_comparator`) |
| **Business Domain** | 4. Marketing, Growth & Client Acquisition (Redfin, Rocket Money & DTC Funnel) (`rocket-demo-marketing`) |
| **Complexity Level** | `L200–L300` |
| **Active Model & Runtime** | **`gemini-4-argon`** — Vertex AI Global Endpoint (gemini-4-argon) + Antigravity gVisor Sandbox |
| **Live Interactive Demo** | [https://rocket-hackathon-portal-254356041555.us-central1.run.app/square/4.2](https://rocket-hackathon-portal-254356041555.us-central1.run.app/square/4.2) *(Username: `rocket` / Password: `Argon2026!`)* |
| **Hosted Cloud Blueprint** | [https://rocket-hackathon-portal-254356041555.us-central1.run.app/docs/4.2](https://rocket-hackathon-portal-254356041555.us-central1.run.app/docs/4.2) |
| **Real Gemini Enterprise UI** | [Open Real Gemini Enterprise Web UI (`gemini-enterprise-17877637_1787763712023`)](https://vertexaisearch.cloud.google.com/home/cid/gemini-enterprise-17877637_1787763712023) · [Open Sobi (`/work`)](https://gemini.google.com/work) |
| **Agent Reproduction Skill** | [`skills/SKILL.md`](../skills/SKILL.md) |

---

## 1. Executive Summary & Bespoke UX Architecture

**Focus:** Transform empty Redfin interior listing photos into virtually staged rooms with crisp rendered typography promoting local down-payment grants.

**Description:**  
Give Redfin listing agents and Rocket marketers instant virtual staging (Detroit Industrial Loft, Mid-Century Warm Craftsman, Coastal Minimalist) plus localized ad banners with rendered rate & grant overlays.

**Bespoke UI Archetype (`imagen_virtual_staging_comparator`):**  
Rather than displaying a generic text response, Square `[4.2]` renders **Nano Banana 2 / Gempix-2 // Interactive Corktown Loft Virtual Staging & TILA Ad Studio** with structured visual artifacts (`Return JSON with keys: selected_design_theme, staging_elements_added (list of strings), hero_ad_overlay ({headline, payment_callout, grant_badge, tila_reg_z_disclaimer}), and social_ad_variants (list of {channel, copy_text, cta_button}).`).

---

## 2. Competitive Win-Back Strategy (Displacing AWS Bedrock, Anthropic Claude & Sierra AI)

> **Why Google Cloud Wins:** Native multi-turn conversational image editing (Nano Banana 2) preserves exact room geometry, window frames, and hardwood flooring while rendering pixel-perfect ad typography.

---

## 3. Target GCP & Antigravity Architecture

**Google Cloud Stack:** `Imagen 4.0 / Nano Banana 2` · `Gemini 4 Argon Creative Director` · `SynthID Watermarking`

```text
┌────────────────────────────────────────────────────────────────────────┐
│       4.2 VIRTUAL STAGING & LOCALIZED HERO AD CREATOR (L200-300)       │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [Empty Redfin Listing Photo + Style Selection + Local Grant Data]     │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [Imagen 4.0 / Nano Banana 2 Inpainting + Gemini 4 Argon Reg Z Check]    │
│  ├─► Locks structural masks (windows, walls, ceiling beams)            │
│  ├─► Renders furniture + crisp typography overlay + SynthID            │
│  └─► Auto-appends TILA Reg Z APR disclosure for payment ads            │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [Interactive Before/After Staged Room + Compliant Paid Social Ads]    │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Step-by-Step Reproduction Instructions

1. Call Vertex AI Imagen 4.0 (`imagen-4.0-generate-001` / Nano Banana editing) with the room image and structural preservation mask.
2. Use `gemini-4-argon` to compute the exact monthly payment and automatically generate the mandatory TILA Regulation Z (12 CFR § 1026.24) APR footer whenever a monthly payment trigger term is rendered on the ad.

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
  "archetype": "imagen_virtual_staging_comparator",
  "before_img": "/static/images/rocket_loft_before.jpg",
  "after_industrial": "/static/images/rocket_loft_after_industrial.jpg",
  "after_midcentury": "/static/images/rocket_loft_after_midcentury.jpg",
  "headline": "Own This Corktown Loft for $2,190/mo P&I + $10,000 Rocket Grant",
  "tila_footer": "6.125% Note Rate (6.314% APR) \u2022 30-Yr Fixed \u2022 Equal Housing Lender NMLS #3030"
}
```
