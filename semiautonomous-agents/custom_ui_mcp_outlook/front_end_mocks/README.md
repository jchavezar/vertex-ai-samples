# Next-Generation Universal Chat Window - Design Mocks & UX Specification

Welcome to the **Next-Generation Universal Chat Window** design system and interactive frontend mock options created for the `custom_ui_mcp_outlook` project inside `vertex-ai-samples/semiautonomous-agents`.

This showcase combines the best UX/UI innovations from **Claude Desktop**, **Gemini Enterprise**, **ChatGPT Studio**, and **Claude Code CLI** into a unified, high-performing frontend architecture.

---

## 🌟 Key UX/UI Innovations & Best Practices

1. **Claude Code Dynamic Ink Loader (`.shrinking-shining-ink`)**:
   - Replicates the organic fluid ink droplet animation with morphing keyframes (`ink-morph`), scale pulsing (`ink-pulse`), and radial shimmering glow (`ink-shine`).
   - Accompanied by a monochrome linear text sweep (`.sweep-text`) for real-time status updates.

2. **Yazdani Morphing Glyph Spinner (`.yazdani-spinner`)**:
   - Shifting typographic Unicode character sequence (`✳` ➔ `✻` ➔ `❋` ➔ `✽` ➔ `※` ➔ `✷` ➔ `✸`) with glow pulses for deep reasoning and multi-agent topology steps.

3. **MCP Connector Telemetry & Control Bar**:
   - Native integration pills for **M365 Outlook MCP**, **Atlassian Jira MCP**, **Google Workspace MCP**, and **GitHub Copilot MCP**.
   - Displays real-time connection status dots, permission toggles, tool execution logs, and sub-30ms latency stats.

4. **Dynamic Token Budget Barometer**:
   - Live visual token barometer (`18.4k / 200k tokens`) to track token window consumption dynamically.

5. **Split-Screen Artifact Canvas**:
   - Side-by-side execution workspace for live email drafts, code diffs, JSON payloads, and markdown documentation.

---

## 🎨 The 3 Design Mock Options

| Mock Option | Aesthetic & Vibe | Key Signature Features | Best Used For |
| :--- | :--- | :--- | :--- |
| **Option 1: Claude Enterprise Dock** (`mock1_claude_hybrid.html`) | Minimalist Dark Slate Luxury (`#07090E`), Deep Indigo accents (`#6366F1`) | Tri-column split layout, Claude Ink Loader, Artifact Canvas, Token Barometer | Enterprise productivity, deep coding & draft editing |
| **Option 2: Gemini Quantum HUD** (`mock2_gemini_hud.html`) | Cyberpunk Glassmorphism HUD (`#09090E`), Neon Cyan (`#06B6D4`) | Floating spatial HUD, Yazdani Glyph Morphing, Subagent Topology Graph, Grounded Source Mesh | Multi-Agent orchestration, complex cross-datasource research |
| **Option 3: ChatGPT Omni-Studio** (`mock3_studio_canvas.html`) | Warm Obsidian & Champagne Gold (`#1C1917`), Amber (`#F59E0B`) | Live Voice Equalizer spectrum, Slash Command popover (`/`), Modular Studio Grid Tiles | Voice-first interaction, quick command execution, widget dashboards |

---

## 📁 Directory Structure

```
front_end_mocks/
├── index.html                     # Master Showcase Hub with live tab switcher
├── mock1_claude_hybrid.html       # Option 1: Claude Desktop + Enterprise Artifact Workspace
├── mock2_gemini_hud.html          # Option 2: Gemini Quantum HUD & Grounded Mesh
├── mock3_studio_canvas.html       # Option 3: ChatGPT NextGen Dynamic Command Studio
├── css/
│   ├── design_system.css          # Design tokens, keyframe animations (ink, yazdani, sweep, voice)
│   └── components.css             # Glassmorphism panels, chat bubbles, prompt dock, MCP badges
├── js/
│   ├── mcp_simulator.js           # Simulated MCP connectors engine for Outlook, Jira, Workspace
│   └── animations.js              # Ink loader controller, typewriter stream, token barometer
└── README.md                      # Design system documentation
```

---

## 🚀 How to Launch & Preview

To preview the interactive mocks in your browser:

```bash
# Navigate to the mocks directory
cd ~/IdeaProjects/vertex-ai-samples/semiautonomous-agents/custom_ui_mcp_outlook/front_end_mocks

# Open directly in browser on macOS:
open index.html

# Or serve via python HTTP server:
python3 -m http.server 8080
```
Then open `http://localhost:8080` in your web browser to test all 3 interactive mocks and switch between them live.

---

## ⚙️ Model Support Specs
Supported and targeted models for deployment:
- `gemini-3-pro-preview`
- `gemini-3-flash-preview`
- `gemini-2.5-pro`
- `gemini-2.5-flash`
