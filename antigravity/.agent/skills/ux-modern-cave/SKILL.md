---
description: Implements the "Modern Cave" design system—a neofuturistic, organic, and monolithic UX/UI style featuring horizontal scroll journeys, earthy color palettes, and brutalist typography.
---

# Skill: UX Modern Cave (Neo-Monolith)

This skill provides the blueprints, assets, and principles for constructing the **"Modern Cave"** aesthetic—a high-fidelity, neofuturistic design language that blends brutalist structures with organic, earth-toned palettes.

## 1. Core Design Philosophy

*   **Monolithic Structure:** UIs should feel like carved stone or heavy metal slabs. Use large, solid backgrounds with subtle (or no) noise.
*   **Horizontal Journey:** Prefer horizontal scrolling for narrative progression (e.g., "Topology A" vs. "Topology B").
*   **Typography:** Use `Inter` or `Space Mono` (Google Fonts). Headers should be uppercase, tracked widely (`tracking-widest`), and treated as architectural elements.
*   **Palette:**
    *   **Backgrounds:** Deep Slate (`#0f172a`), Void Black (`#020617`), Earthen Clay (`#2d2d2a`).
    *   **Accents:** Neon Cyan (`#22d3ee`), Industrial Orange (`#f97316`), Hacker Green (`#22c55e`), Electric Rose (`#fda4af` for alerts).

## 2. Documentation Standards (README.md)

Every project MUST follow this specific visual and narrative structure. **NO PLAIN MARKDOWN HEADERS.**

### A. Immersive Headers (SVG)
Replace standard `## Headers` with custom-generated, full-width SVG banners that include:
1.  **Terminal Aesthetic:** Window controls, bash prompts (`root@system:~# base_init.sh`).
2.  **Live Code Injection:** The background MUST feature animated, scrolling code snippets relevant to the section (e.g., React components for the UI section, Python for the backend).
3.  **Neon Accents:** Glowing lines and text to simulate a CRT or HUD.

### B. High-Fidelity Diagrams (Static SVG Only)
**NEVER** use dynamic Mermaid rendering (e.g., ` ```mermaid `) in GitHub READMEs. It fails on contrast and clipping.
**ALWAYS** pre-render diagrams using `mermaid-cli` with a strict **High Contrast / Minimalist** theme.

**Required Protocol:**
1.  **Source:** Create a `diagram_name.mmd` file.
2.  **Config:** Use a `mermaid_config.json` that forces:
    *   `noteBkg`: `#1e293b` (Dark Slate) - **CRITICAL** to avoid yellow notes.
    *   `noteTextColor`: `#fda4af` (Neon Rose).
    *   `actorBkg`: `#0f172a` (Void).
    *   `background`: `transparent`.
3.  **Generate:** `npx -y @mermaid-js/mermaid-cli -i source.mmd -o output.svg -c config.json -b transparent`
4.  **Embed:** `<img src="./assets/diagram.svg" width="100%">`

### C. Narrative Topology (The "Dual Path")
Structure the documentation to guide the user from "Zero-Code" to "Custom Architect".
*   **Topology A (Ground Zero):** The foundation. Native integration, standard outputs, minimum viable product. (e.g., "Native Gemini Interface").
*   **Topology B (The Evolution):** The advanced implementation. Custom UIs, direct API usage, specialized logic. (e.g., "Custom Neo-Monolith").
*   **Identity Bridge:** Explicitly state that **Workload Identity Federation (WIF)** is the universal bridge for *both* paths, not just the custom one.

## 3. Implementation Assets

### Generator Script Template (`_docs_generator/`)
Keep all generation logic (Python scripts, Mermaid sources) in a dedicated `_docs_generator/` folder to keep the root clean.

### Grid Layouts
Use HTML `<table>` grids for complex layouts (Steps + Screenshots) instead of linear markdown. This creates a dashboard-like feel.

```html
<table>
  <tr>
    <td valign="top">
      <kbd>EXECUTE</kbd> Command or Action.<br/><br/>
      <kbd>DEFINE</kbd> Explanation of the step.<br/><br/>
      <kbd>RESULT</kbd> Expected outcome.
    </td>
    <td width="400">
      <img src="..." />
    </td>
  </tr>
</table>
```
