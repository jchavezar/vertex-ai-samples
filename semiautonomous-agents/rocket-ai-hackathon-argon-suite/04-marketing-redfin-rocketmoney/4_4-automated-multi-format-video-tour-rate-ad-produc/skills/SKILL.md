---
name: rocket-square-4_4
description: Blueprint skill to build and reproduce Rocket AI Hackathon Square [4.4] (Automated Multi-Format Video Tour & Rate Ad Producer) with bespoke UI archetype `veo_vertical_reel_storyboard`, deterministic gVisor sandbox math, and `gemini-4-argon` routing.
---

# Skill: Reproduce Square `[4.4]` — Automated Multi-Format Video Tour & Rate Ad Producer

## 1. Bespoke UI/UX Design Specification
- **Application Title:** `Veo 3.1 & Lyria // 9:16 Vertical Social Reel Storyboard & Audio Beat Studio`
- **UI Archetype Slug:** `veo_vertical_reel_storyboard` (`layout_mode: vertical_phone_reel`)
- **Color Palette:** Primary Accent `#A855F7` · Secondary Accent `#F43F5E` · Surface `#0B0714`
- **Interactive Controls:** `[]`
- **Anti-Pattern Rule:** NEVER render raw unformatted markdown or a generic chat box for this use case. Always bind the output to the structured visual components defined in `mock_data/sample_payload.json` (`bespoke_visual_artifact`) and `output_schema_hint`.

## 2. Model & Runtime Routing Policy
- **Assigned Model:** `gemini-4-argon`
- **Runtime Badge:** `Vertex AI Global Endpoint (gemini-4-argon) + Antigravity gVisor Sandbox`
- **Routing Rationale:** Direct Vertex AI Global Endpoint invocation (gemini-4-argon)
- **Real Gemini Enterprise Engine (for Grounding / streamAssist):** `projects/254356041555/locations/global/collections/default_collection/engines/gemini-enterprise-17877637_1787763712023` ([Open Real Web UI](https://vertexaisearch.cloud.google.com/home/cid/gemini-enterprise-17877637_1787763712023))

## 3. Structured Output Schema Contract
```text
Return JSON with keys: reel_title, audio_track_spec, storyboard_frames (list of 4 frames {timecode, camera_motion, visual_scene, on_screen_typography, voiceover_line}), and reg_z_end_card.
```

## 4. Verification Workflow
1. Run `python3 code/sandbox_tool.py` to execute the deterministic gVisor math check and generate the bespoke visual artifact JSON.
2. Run `python3 code/agent.py` to invoke `gemini-4-argon` with `response_mime_type="application/json"` and validate the structured decision cards.
