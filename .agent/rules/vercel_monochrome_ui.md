---
trigger: always_on
description: "Mandatory Vercel Architecture Monochrome UI/UX (Light Mode by Default + Dynamic Light/Dark Toggle) & Claude-Code Shrinking Shining Ink Loading Animation standard for all web apps, dashboards, and UIs."
---

# Mandatory UI/UX Standard: Vercel Monochrome Architecture (Light Default + Dynamic Dark/Light Toggle) + Claude-Code Ink Loader

Whenever the user asks to create, design, scaffold, or update ANY web application, UI/UX, dashboard, chat interface, or frontend component, you **MUST ALWAYS** enforce the following design system by default without exception:

## 1. Visual Architecture: Minimalist Monochrome Vercel Style (Light Mode Default + Dynamic Dark Toggle)
- **Default Theme**: **LIGHT MODE BY DEFAULT** (`data-theme="light"` or default CSS `:root` variables).
- **Mandatory Dynamic Theme Toggle Button**:
  - Every UI **MUST** include a crisp architectural **Light / Dark Toggle Button** (`☀️ Light` / `🌙 Dark` or icon toggle) in the top header bar that dynamically switches `data-theme="light"` and `data-theme="dark"` on the root element.
- **Color Palette (Strict Monochrome CSS Variables)**:
  - **Light Mode (`:root`, Default)**:
    - **Canvas Background**: Crisp architectural off-white (`#FAFAFA`) with subtle `48px` hairline grid (`#EAEAEA`).
    - **Surface / Cards**: Pure White (`#FFFFFF`), elevated header/telemetry bar (`#FAFAFA`).
    - **Borders & Hairlines**: Crisp 1px structural borders (`1px solid #EAEAEA`), hover/focus highlighting to `#111111`.
    - **Primary Typography**: Pure Obsidian Black (`#09090B` or `#111111`), tight tracking (`-0.02em`), Inter / Geist Sans.
    - **Secondary / Telemetry Typography**: Neutral monochrome gray (`#666666`), `JetBrains Mono` / `Geist Mono` uppercase labels (`letter-spacing: 0.06em`, `font-size: 11px`).
    - **Primary Action Button**: Pure Black background (`#000000`) with Pure White text (`#FFFFFF`), hover `#27272A`.
  - **Dark Mode (`[data-theme="dark"]`)**:
    - **Canvas Background**: Pure OLED Black (`#000000`) with `#111111` hairline grid.
    - **Surface / Cards**: `#0A0A0A` to `#111111`.
    - **Borders & Hairlines**: `1px solid #222222`, hover/focus `#EDEDED`.
    - **Primary Typography**: Crisp Pure White (`#EDEDED` or `#FFFFFF`).
    - **Secondary / Telemetry Typography**: Neutral gray (`#888888`).
    - **Primary Action Button**: Pure White background (`#FFFFFF`) with Pure Black text (`#000000`), hover `#D4D4D8`.

## 2. Thinking & Waiting State: Theme-Aware Claude-Code "Shrinking & Shining Ink" Loader
Whenever the UI is waiting for an LLM response, streaming audio/text, executing a tool call, or performing an agent handoff, you **MUST** display the **Claude-Code Shrinking & Shining Ink Animation** (`.shrinking-shining-ink`) paired with a monochrome shimmer text sweep (`.sweep-text`):
- **Light Mode Ink Droplet**: Deep obsidian liquid ink (`radial-gradient(circle at 30% 30%, #52525b, #18181b, #000000)`) with dark shimmer text sweep.
- **Dark Mode Ink Droplet**: Luminous silver/white ink (`radial-gradient(circle at 30% 30%, #ffffff, #a1a1aa, #18181b)`) with white shimmer text sweep.
- Consult the global skill `vercel-monochrome-ui` for the exact CSS variables and keyframes.
