# Square `[4.4]`: Automated Multi-Format Video Tour & Rate Ad Producer — Reproduction, Bespoke UI & Skill Guide

| Field | Value |
| :--- | :--- |
| **Square Code** | `4.4` |
| **Bespoke Application Title** | **Veo 3.1 & Lyria // 9:16 Vertical Social Reel Storyboard & Audio Beat Studio** (`veo_vertical_reel_storyboard`) |
| **Business Domain** | 4. Marketing, Growth & Client Acquisition (Redfin, Rocket Money & DTC Funnel) (`rocket-demo-marketing`) |
| **Complexity Level** | `L300` |
| **Active Model & Runtime** | **`gemini-4-argon`** — Vertex AI Global Endpoint (gemini-4-argon) + Antigravity gVisor Sandbox |
| **Live Interactive Demo** | [https://rocket-demo-marketing-254356041555.us-central1.run.app/?case=4.4](https://rocket-demo-marketing-254356041555.us-central1.run.app/?case=4.4) *(Username: `rocket` / Password: `Argon2026!`)* |
| **Hosted Cloud Blueprint** | [https://rocket-hackathon-portal-254356041555.us-central1.run.app/docs/4.4](https://rocket-hackathon-portal-254356041555.us-central1.run.app/docs/4.4) |
| **Real Gemini Enterprise UI** | [Open Real Gemini Enterprise Web UI (`gemini-enterprise-17877637_1787763712023`)](https://vertexaisearch.cloud.google.com/home/cid/gemini-enterprise-17877637_1787763712023) · [Open Sobi (`/work`)](https://gemini.google.com/work) |
| **Agent Reproduction Skill** | [`skills/SKILL.md`](../skills/SKILL.md) |

---

## 1. Executive Summary & Bespoke UX Architecture

**Focus:** Transform static Redfin listing photos and rate promos into 9:16 vertical Shorts/Reels and 16:9 walkthrough videos via conversational editing.

**Description:**  
Feed Redfin listing photos and live Rocket rate promotions into Gemini Omni to generate 15-second vertical 9:16 Reels/TikToks with animated monthly payment captions, AI voiceover script, and SynthID watermarking.

**Bespoke UI Archetype (`veo_vertical_reel_storyboard`):**  
Rather than displaying a generic text response, Square `[4.4]` renders **Veo 3.1 & Lyria // 9:16 Vertical Social Reel Storyboard & Audio Beat Studio** with structured visual artifacts (`Return JSON with keys: reel_title, audio_track_spec, storyboard_frames (list of 4 frames {timecode, camera_motion, visual_scene, on_screen_typography, voiceover_line}), and reg_z_end_card.`).

---

## 2. Competitive Win-Back Strategy (Displacing AWS Bedrock, Anthropic Claude & Sierra AI)

> **Why Google Cloud Wins:** Gemini Omni enables multi-turn conversational video editing (blending listing photos, voiceover, and dynamic rate overlays) natively inside Gemini Enterprise Agent Platform.

---

## 3. Target GCP & Antigravity Architecture

**Google Cloud Stack:** `Gemini Omni Flash` · `Veo 3.1` · `Gemini 4 Argon Script & Caption Sync` · `SynthID`

```text
┌────────────────────────────────────────────────────────────────────────┐
│      4.4 GEMINI OMNI MULTI-FORMAT VIDEO TOUR & AD PRODUCER (L300)      │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [4 Redfin Listing Photos + Rate Promo + Conversational Edit Prompt]   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [Gemini Omni / Veo 3.1 + Gemini 4 Argon Storyboard Engine]            │
│  ├─► Scene 1 (0-3.5s): Exterior Dolly Zoom + Hook Caption              │
│  ├─► Scene 2 (3.5-7s): Kitchen Pan + "$2,695/mo P&I" Badge             │
│  ├─► Scene 3 (7-11s):  Primary Suite & Deck + Rate Drop Protector      │
│  └─► Scene 4 (11-15s): Redfin + Rocket 1-Tap Pre-Approval CTA          │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [9:16 Vertical Short + 16:9 YouTube Ad + SynthID Watermark]           │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Step-by-Step Reproduction Instructions

1. Pass Redfin listing image GCS URIs and camera motion prompts to Vertex AI video generation (`veo-3.0-generate-preview` / `gemini-omni`).
2. Use `gemini-4-argon` to synchronize the word-level WebVTT/ASS animated payment captions and voiceover script.
3. Publish to YouTube Shorts, Instagram Reels, and the Redfin mobile listing feed.

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
  "archetype": "veo_vertical_reel_storyboard",
  "frames": [
    {
      "time": "00:00 \u2013 00:03",
      "scene": "FPV Drone Swoop through Corktown Brick Loft Windows",
      "overlay": "STOP PAYING $2,650 DETROIT RENT \ud83d\uded1",
      "img": "/static/images/rocket_loft_before.jpg"
    },
    {
      "time": "00:03 \u2013 00:08",
      "scene": "Instant Gempix-2 / Veo Morph into Warm Cognac Leather Staged Loft",
      "overlay": "OWN FOR $2,190/MO P&I \u26a1",
      "img": "/static/images/rocket_loft_after_industrial.jpg"
    },
    {
      "time": "00:08 \u2013 00:12",
      "scene": "Split-Screen Chef Kitchen + Rocket Money $10k Grant Badge",
      "overlay": "+$10,000 ROCKET HOMEBUYER GRANT \ud83d\udcb0",
      "img": "/static/images/rocket_kitchen_homestyle.jpg"
    },
    {
      "time": "00:12 \u2013 00:15",
      "scene": "1-Tap Redfin Tour + Rocket Verified Approval End-Card",
      "overlay": "6.125% Rate (6.314% APR) \u2022 NMLS #3030",
      "img": "/static/images/rocket_loft_after_midcentury.jpg"
    }
  ]
}
```
