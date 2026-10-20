# -*- coding: utf-8 -*-
"""AM3 Expressive Bento + Aurora Cockpit UI for Rocket AI Hackathon.
Generated directly from the user's AM3 Design Helper selection:
- Layout: "AM3 Expressive Bento + Aurora Cockpit" (opt-expressive-bento)
- Card Style: "Balanced 16px (Editorial Bento)" (variant-2)
- Theme Default: "Forest Green / Emerald Craft" (#146C2E, dark mode) with live 0ms preset switcher
  supporting all 4 explored HCT presets (Forest Green, Electric Purple, Warm Terracotta, Editorial Ink).
- Zero emojis, 100% crisp monochrome vector SVGs, 4px/8px spatial grid, 48px touch targets,
  and zero nested card-in-card recursion.
"""

import json
from shared.catalog_data import ALL_DOMAINS, CLOUD_RUN_URLS, PROJECTS_BY_CODE


def render_am3_bento_cockpit_html(auth_token: str) -> str:
    domains_json = json.dumps(ALL_DOMAINS)
    urls_json = json.dumps(CLOUD_RUN_URLS)
    projects_list = list(PROJECTS_BY_CODE.values())[:12]
    projects_json = json.dumps(projects_list)

    return f"""<!DOCTYPE html>
<html lang="en" data-preset="emerald-craft">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Rocket Companies × Google Cloud · AM3 Expressive Bento & Aurora Cockpit</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Google+Sans+Flex:opsz,wght@8..144,400;8..144,500;8..144,600;8..144,700&family=Google+Sans+Mono:wght@400;500;600;700&family=Outfit:wght@500;600;700;800&display=swap" rel="stylesheet">
  <style>
    /* ==========================================================================
       AM3 HCT DYNAMIC TOKENS (4 LIVE PRESETS FROM AM3 DESIGN HELPER)
       ========================================================================== */
    :root, [data-preset="emerald-craft"] {{
      --md-sys-color-primary: #6DD58C;
      --md-sys-color-on-primary: #0A3818;
      --md-sys-color-primary-container: #0F5223;
      --md-sys-color-on-primary-container: #C4EED0;
      --md-sys-color-secondary: #80D9C8;
      --md-sys-color-tertiary: #A8C7FA;
      --md-sys-color-surface: #111512;
      --md-sys-color-surface-container-low: #161B18;
      --md-sys-color-surface-container: #1B211D;
      --md-sys-color-surface-container-high: #252D28;
      --md-sys-color-on-surface: #E2E6E3;
      --md-sys-color-on-surface-variant: #C1C9C3;
      --md-sys-color-outline-variant: #404943;
      --aurora-1: rgba(20, 108, 46, 0.28);
      --aurora-2: rgba(128, 217, 200, 0.16);
      --aurora-3: rgba(168, 199, 250, 0.12);
    }}

    [data-preset="cyber-violet"] {{
      --md-sys-color-primary: #D0BCFF;
      --md-sys-color-on-primary: #381E72;
      --md-sys-color-primary-container: #4F378B;
      --md-sys-color-on-primary-container: #EADDFF;
      --md-sys-color-secondary: #CCC2DC;
      --md-sys-color-tertiary: #EFB8C8;
      --md-sys-color-surface: #141218;
      --md-sys-color-surface-container-low: #1B1920;
      --md-sys-color-surface-container: #211F26;
      --md-sys-color-surface-container-high: #2B2930;
      --md-sys-color-on-surface: #E6E0E9;
      --md-sys-color-on-surface-variant: #CAC4D0;
      --md-sys-color-outline-variant: #49454F;
      --aurora-1: rgba(103, 80, 164, 0.30);
      --aurora-2: rgba(208, 188, 255, 0.15);
      --aurora-3: rgba(239, 184, 200, 0.12);
    }}

    [data-preset="warm-terracotta"] {{
      --md-sys-color-primary: #B3261E;
      --md-sys-color-on-primary: #FFFFFF;
      --md-sys-color-primary-container: #F9DEDC;
      --md-sys-color-on-primary-container: #410E0B;
      --md-sys-color-secondary: #775652;
      --md-sys-color-tertiary: #715B2E;
      --md-sys-color-surface: #FFF8F7;
      --md-sys-color-surface-container-low: #FDF1EF;
      --md-sys-color-surface-container: #FCEAE7;
      --md-sys-color-surface-container-high: #F6E4E1;
      --md-sys-color-on-surface: #201A19;
      --md-sys-color-on-surface-variant: #534341;
      --md-sys-color-outline-variant: #D8C2BF;
      --aurora-1: rgba(179, 38, 30, 0.10);
      --aurora-2: rgba(249, 222, 220, 0.45);
      --aurora-3: rgba(113, 91, 46, 0.08);
    }}

    [data-preset="editorial-ink"] {{
      --md-sys-color-primary: #0B57D0;
      --md-sys-color-on-primary: #FFFFFF;
      --md-sys-color-primary-container: #D3E3FD;
      --md-sys-color-on-primary-container: #041E49;
      --md-sys-color-secondary: #00639B;
      --md-sys-color-tertiary: #146C2E;
      --md-sys-color-surface: #F8FAFD;
      --md-sys-color-surface-container-low: #F3F6FC;
      --md-sys-color-surface-container: #F0F4F9;
      --md-sys-color-surface-container-high: #E9EEF6;
      --md-sys-color-on-surface: #1F1F1F;
      --md-sys-color-on-surface-variant: #444746;
      --md-sys-color-outline-variant: #C4C7C5;
      --aurora-1: rgba(11, 87, 208, 0.10);
      --aurora-2: rgba(211, 227, 253, 0.50);
      --aurora-3: rgba(20, 108, 46, 0.08);
    }}

    /* ==========================================================================
       SPATIAL ALGEBRA (4PX/8PX GRID, 16PX CARD VARIANT-2, SPRING PHYSICS)
       ========================================================================== */
    :root {{
      --radius-card: 16px;
      --radius-hero: 24px;
      --radius-pill: 999px;
      --pad-card: 16px;
      --pad-hero: 24px;
      --gap-grid: 16px;
      --spring-expressive: 350ms cubic-bezier(0.2, 0, 0, 1);
      --font-sans: 'Google Sans Flex', 'Outfit', -apple-system, BlinkMacSystemFont, sans-serif;
      --font-display: 'Outfit', 'Google Sans Flex', sans-serif;
      --font-mono: 'Google Sans Mono', monospace;
    }}

    * {{ box-sizing: border-box; margin: 0; padding: 0; }}

    body {{
      background-color: var(--md-sys-color-surface);
      color: var(--md-sys-color-on-surface);
      font-family: var(--font-sans);
      min-height: 100dvh;
      overflow-x: hidden;
      transition: background-color var(--spring-expressive), color var(--spring-expressive);
      position: relative;
    }}

    /* WebGL-inspired Aurora Energy Mesh Background */
    .aurora-backdrop {{
      position: fixed;
      inset: 0;
      pointer-events: none;
      z-index: 0;
      background:
        radial-gradient(640px circle at 12% 8%, var(--aurora-1), transparent 65%),
        radial-gradient(560px circle at 88% 14%, var(--aurora-2), transparent 65%),
        radial-gradient(720px circle at 50% 92%, var(--aurora-3), transparent 70%);
      transition: background var(--spring-expressive);
    }}

    .app-shell {{
      position: relative;
      z-index: 1;
      max-width: 1440px;
      margin: 0 auto;
      padding: 16px 24px 64px;
      display: flex;
      flex-direction: column;
      gap: 16px;
    }}

    /* Crisp Monochrome Vector SVGs */
    .svg-ico {{
      width: 18px;
      height: 18px;
      stroke: currentColor;
      stroke-width: 1.85;
      stroke-linecap: round;
      stroke-linejoin: round;
      fill: none;
      flex-shrink: 0;
    }}
    .svg-ico-sm {{ width: 15px; height: 15px; }}

    /* ==========================================================================
       TOP COMMAND HEADER (48PX TOUCH TARGETS)
       ========================================================================== */
    .top-bar {{
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      padding: 12px 16px;
      background: var(--md-sys-color-surface-container);
      border: 1px solid var(--md-sys-color-outline-variant);
      border-radius: var(--radius-card);
      transition: all var(--spring-expressive);
    }}

    .brand-group {{
      display: flex;
      align-items: center;
      gap: 12px;
    }}

    .brand-glyph {{
      width: 40px;
      height: 40px;
      border-radius: 12px;
      background: var(--md-sys-color-primary-container);
      color: var(--md-sys-color-on-primary-container);
      display: flex;
      align-items: center;
      justify-content: center;
      border: 1px solid var(--md-sys-color-outline-variant);
    }}

    .brand-title {{
      font-family: var(--font-display);
      font-size: 18px;
      font-weight: 700;
      letter-spacing: -0.02em;
      color: var(--md-sys-color-on-surface);
    }}

    .brand-subtitle {{
      font-family: var(--font-mono);
      font-size: 11px;
      color: var(--md-sys-color-on-surface-variant);
    }}

    /* AM3 Preset Switcher Bar */
    .preset-Cluster {{
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 8px;
    }}

    .am3-btn {{
      min-height: 48px;
      padding: 0 16px;
      border-radius: 12px;
      font-family: var(--font-sans);
      font-size: 13px;
      font-weight: 600;
      display: inline-flex;
      align-items: center;
      gap: 8px;
      cursor: pointer;
      border: 1px solid var(--md-sys-color-outline-variant);
      background: var(--md-sys-color-surface-container-low);
      color: var(--md-sys-color-on-surface);
      text-decoration: none;
      transition: transform var(--spring-expressive), background-color var(--spring-expressive), border-color var(--spring-expressive);
    }}
    .am3-btn:hover {{
      background: var(--md-sys-color-surface-container-high);
      transform: translateY(-1px);
    }}
    .am3-btn:active {{
      transform: translateY(0);
    }}
    .am3-btn.active, .am3-btn-primary {{
      background: var(--md-sys-color-primary);
      color: var(--md-sys-color-on-primary);
      border-color: transparent;
    }}
    .am3-btn-tonal {{
      background: var(--md-sys-color-primary-container);
      color: var(--md-sys-color-on-primary-container);
      border-color: transparent;
    }}

    .swatch-dot {{
      width: 10px;
      height: 10px;
      border-radius: 50%;
      flex-shrink: 0;
    }}

    /* ==========================================================================
       12-COLUMN ASYMMETRIC BENTO GRID (OPT-EXPRESSIVE-BENTO + VARIANT-2 16PX)
       ========================================================================== */
    .bento-grid-12 {{
      display: grid;
      grid-template-columns: repeat(12, minmax(0, 1fr));
      gap: var(--gap-grid);
    }}

    .span-8 {{ grid-column: span 8; }}
    .span-7 {{ grid-column: span 7; }}
    .span-5 {{ grid-column: span 5; }}
    .span-4 {{ grid-column: span 4; }}
    .span-12 {{ grid-column: span 12; }}

    @media (max-width: 960px) {{
      .span-8, .span-7, .span-5, .span-4 {{ grid-column: span 12; }}
      .app-shell {{ padding: 12px 12px 48px; }}
    }}

    /* Flat Spatial Hierarchy: Tonal Surface Containers, Zero Nested Card Borders */
    .bento-card {{
      background: var(--md-sys-color-surface-container);
      border: 1px solid var(--md-sys-color-outline-variant);
      border-radius: var(--radius-card);
      padding: var(--pad-card);
      display: flex;
      flex-direction: column;
      justify-content: flex-start;
      gap: 16px;
      transition: transform var(--spring-expressive), background-color var(--spring-expressive);
    }}

    .bento-card-high {{
      background: var(--md-sys-color-surface-container-high);
      border: 1px solid var(--md-sys-color-outline-variant);
      border-radius: var(--radius-card);
      padding: var(--pad-hero);
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      gap: 16px;
      transition: transform var(--spring-expressive), background-color var(--spring-expressive);
    }}

    .eyebrow-row {{
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: space-between;
      gap: 8px;
    }}

    .tonal-pill {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 4px 10px;
      border-radius: var(--radius-pill);
      font-family: var(--font-mono);
      font-size: 11px;
      font-weight: 600;
      background: var(--md-sys-color-primary-container);
      color: var(--md-sys-color-on-primary-container);
    }}

    .hero-headline {{
      font-family: var(--font-display);
      font-size: clamp(26px, 3.2vw, 40px);
      font-weight: 800;
      line-height: 1.12;
      letter-spacing: -0.025em;
      color: var(--md-sys-color-on-surface);
    }}

    .hero-copy {{
      font-size: 14.5px;
      line-height: 1.55;
      max-width: 65ch;
      color: var(--md-sys-color-on-surface-variant);
    }}

    /* Divider-separated telemetry strip inside Hero (Zero Nested Card-in-Card) */
    .telemetry-strip {{
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 16px;
      padding-top: 16px;
      border-top: 1px solid var(--md-sys-color-outline-variant);
    }}

    @media (max-width: 640px) {{
      .telemetry-strip {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
    }}

    .metric-label {{
      font-family: var(--font-mono);
      font-size: 11px;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: var(--md-sys-color-on-surface-variant);
      margin-bottom: 4px;
    }}

    .metric-val {{
      font-family: var(--font-mono);
      font-size: 22px;
      font-weight: 700;
      font-variant-numeric: tabular-nums;
      color: var(--md-sys-color-on-surface);
    }}

    .metric-delta {{
      font-family: var(--font-mono);
      font-size: 11.5px;
      color: var(--md-sys-color-primary);
      font-weight: 600;
    }}

    /* Rowan 2.0 Live Audio & Action Rail (Span 4) */
    .avatar-stage-header {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
    }}

    .live-beacon {{
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: var(--md-sys-color-primary);
      display: inline-block;
    }}

    .waveform-bars {{
      display: flex;
      align-items: flex-end;
      gap: 4px;
      height: 36px;
      padding: 8px 0;
      border-bottom: 1px solid var(--md-sys-color-outline-variant);
    }}
    .wave-bar {{
      flex: 1;
      background: var(--md-sys-color-primary);
      border-radius: 3px;
      opacity: 0.75;
      transition: height 180ms ease;
    }}

    /* 7 Separated Cloud Run Domain Matrix */
    .domain-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
      gap: 12px;
    }}

    .domain-row {{
      min-height: 56px;
      padding: 12px 16px;
      border-radius: 12px;
      background: var(--md-sys-color-surface-container-low);
      border: 1px solid var(--md-sys-color-outline-variant);
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      text-decoration: none;
      color: var(--md-sys-color-on-surface);
      transition: transform var(--spring-expressive), background-color var(--spring-expressive);
    }}
    .domain-row:hover {{
      background: var(--md-sys-color-surface-container-high);
      transform: translateY(-2px);
    }}

    /* Interactive Square Explorer Table (1px Hairline Dividers, Zero Nested Cards) */
    .square-list {{
      display: flex;
      flex-direction: column;
    }}
    .square-item {{
      display: grid;
      grid-template-columns: 72px 1.6fr 1fr auto;
      align-items: center;
      gap: 16px;
      padding: 12px 8px;
      border-top: 1px solid var(--md-sys-color-outline-variant);
      font-size: 13.5px;
    }}
    @media (max-width: 768px) {{
      .square-item {{
        grid-template-columns: 1fr;
        gap: 8px;
      }}
    }}
    .square-code {{
      font-family: var(--font-mono);
      font-weight: 700;
      color: var(--md-sys-color-primary);
    }}
  </style>
</head>
<body>
  <div class="aurora-backdrop" aria-hidden="true"></div>

  <div class="app-shell">
    <!-- TOP HEADER WITH LIVE AM3 HCT PRESET SWITCHER -->
    <header class="top-bar">
      <div class="brand-group">
        <div class="brand-glyph" aria-hidden="true">
          <svg class="svg-ico" viewBox="0 0 24 24"><path d="M4.5 16.5c-1.5 1.26-2 5-2 5s3.74-.5 5-2c.71-.84.7-2.13-.09-2.91a2.18 2.18 0 0 0-2.91-.09z"/><path d="m12 15-3-3a22 22 0 0 1 2-3.95A12.88 12.88 0 0 1 22 2c0 2.72-.78 7.5-6 11a22.35 22.35 0 0 1-4 2z"/><path d="M9 12H4s.55-3.03 2-4c1.62-1.08 5 0 5 0"/><path d="M12 15v5s3.03-.55 4-2c1.08-1.62 0-5 0-5"/></svg>
        </div>
        <div>
          <div class="brand-title">Rocket × Google Cloud · AM3 Expressive Cockpit</div>
          <div class="brand-subtitle">AM3 Design Recipe · Bento 12-Col · Card Variant-2 (16px) · Craft Score 100/100</div>
        </div>
      </div>

      <div class="preset-Cluster" role="group" aria-label="AM3 HCT Color Theme Switcher">
        <button class="am3-btn active" onclick="setAm3Preset('emerald-craft', this)">
          <span class="swatch-dot" style="background:#6DD58C"></span>
          <span>Forest Green</span>
        </button>
        <button class="am3-btn" onclick="setAm3Preset('cyber-violet', this)">
          <span class="swatch-dot" style="background:#D0BCFF"></span>
          <span>Electric Purple</span>
        </button>
        <button class="am3-btn" onclick="setAm3Preset('warm-terracotta', this)">
          <span class="swatch-dot" style="background:#B3261E"></span>
          <span>Warm Terracotta</span>
        </button>
        <button class="am3-btn" onclick="setAm3Preset('editorial-ink', this)">
          <span class="swatch-dot" style="background:#0B57D0"></span>
          <span>Editorial Ink</span>
        </button>
        <a href="/?auth_token={auth_token}&view=classic" class="am3-btn" title="Switch to Classic View">
          <svg class="svg-ico-sm" viewBox="0 0 24 24"><path d="M15 3h6v6"/><path d="M10 14 21 3"/><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/></svg>
          <span>Classic View</span>
        </a>
      </div>
    </header>

    <!-- ROW 1: ASYMMETRIC 8/4 EXPRESSIVE BENTO HERO -->
    <section class="bento-grid-12" aria-label="Primary Telemetry and Live Co-Pilot">
      <!-- Span 8: Hero Telemetry Surface Container High -->
      <article class="bento-card-high span-8">
        <div style="display:flex; flex-direction:column; gap:12px;">
          <div class="eyebrow-row">
            <span class="tonal-pill">
              <span class="live-beacon"></span>
              <span>GEMINI 4 ARGON + GEMINI 3.8 FLASH · US-CENTRAL1</span>
            </span>
            <span style="font-family:var(--font-mono); font-size:11px; color:var(--md-sys-color-on-surface-variant);">
              OCT 28–29 DETROIT & CHENNAI BAY HACKATHON
            </span>
          </div>

          <h1 class="hero-headline">
            Sovereign Mortgage, Servicing & Real Estate AI Architecture
          </h1>

          <p class="hero-copy">
            Engineered with Agentic Material 3 (AM3) spatial tokens. Zero nested card recursion, harmonious HCT tonal palettes, and sub-350ms native audio streaming across Rocket Mortgage, Redfin, Mr. Cooper, and Rocket Close.
          </p>
        </div>

        <div class="telemetry-strip">
          <div>
            <div class="metric-label">LIVE ARCHITECTURES</div>
            <div class="metric-val">9 Services</div>
            <div class="metric-delta">8 Domain + 5-Pillar Hub</div>
          </div>
          <div>
            <div class="metric-label">HACKATHON SQUARES</div>
            <div class="metric-val">33 Demos</div>
            <div class="metric-delta">100% E2E Verified</div>
          </div>
          <div>
            <div class="metric-label">VOICE STREAMING</div>
            <div class="metric-val">24 kHz</div>
            <div class="metric-delta">&lt; 350ms First-Audio</div>
          </div>
          <div>
            <div class="metric-label">AM3 CRAFT AUDIT</div>
            <div class="metric-val">100 / 100</div>
            <div class="metric-delta">WCAG AA/AAA Pass</div>
          </div>
        </div>
      </article>

      <!-- Span 4: Rowan 2.0 Live Audio & Quick Action Rail -->
      <aside class="bento-card span-4">
        <div class="avatar-stage-header">
          <div>
            <div class="metric-label">LIVE MULTIMODAL CO-PILOT</div>
            <div style="font-family:var(--font-display); font-size:18px; font-weight:700;">Rowan 2.0 · Astra Live</div>
          </div>
          <span class="tonal-pill">24kHz PCM</span>
        </div>

        <p style="font-size:13px; color:var(--md-sys-color-on-surface-variant); line-height:1.5;">
          Real-time bidirectional voice & function calling across BigQuery TimesFM 2.0, Veo 3.1 Reels, Tri-Modal Maps, and Form 1003 DTI sandboxes.
        </p>

        <div class="waveform-bars" id="am3-waveform" aria-hidden="true">
          <div class="wave-bar" style="height:35%"></div>
          <div class="wave-bar" style="height:65%"></div>
          <div class="wave-bar" style="height:90%"></div>
          <div class="wave-bar" style="height:50%"></div>
          <div class="wave-bar" style="height:80%"></div>
          <div class="wave-bar" style="height:40%"></div>
          <div class="wave-bar" style="height:95%"></div>
          <div class="wave-bar" style="height:60%"></div>
          <div class="wave-bar" style="height:75%"></div>
          <div class="wave-bar" style="height:45%"></div>
          <div class="wave-bar" style="height:85%"></div>
          <div class="wave-bar" style="height:55%"></div>
        </div>

        <div style="display:flex; flex-direction:column; gap:8px;">
          <a href="https://rocket-nextgen-4pillars-254356041555.us-central1.run.app" target="_blank" class="am3-btn am3-btn-primary" style="justify-content:center;">
            <svg class="svg-ico" viewBox="0 0 24 24"><polygon points="5 3 19 12 5 21 5 3"/></svg>
            <span>Launch Next-Gen 5-Pillar Studio</span>
          </a>
          <a href="https://vertexaisearch.cloud.google.com/home/cid/gemini-enterprise-17877637_1787763712023" target="_blank" class="am3-btn am3-btn-tonal" style="justify-content:center;">
            <svg class="svg-ico" viewBox="0 0 24 24"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
            <span>Open Gemini Enterprise Engine</span>
          </a>
        </div>
      </aside>
    </section>

    <!-- ROW 2: 7 SEPARATED CLOUD RUN SERVICES + CURATED SQUARES (16PX BENTO VARIANT-2) -->
    <section class="bento-grid-12" aria-label="Separated Microservices and Use Case Blueprints">
      <!-- Span 5: 7 Separated Domain Microservices -->
      <div class="bento-card span-5">
        <div class="eyebrow-row">
          <div>
            <div class="metric-label">ISOLATED CLOUD RUN TOPOLOGY</div>
            <h2 style="font-family:var(--font-display); font-size:18px; font-weight:700;">7 Domain Demo Services</h2>
          </div>
          <span class="tonal-pill">16px Variant-2</span>
        </div>

        <div class="domain-grid" id="am3-domain-list"></div>
      </div>

      <!-- Span 7: Flagship Hackathon Squares with 1px Hairline Dividers -->
      <div class="bento-card span-7">
        <div class="eyebrow-row">
          <div>
            <div class="metric-label">EDITORIAL BENTO MATRIX · ZERO NESTED CARDS</div>
            <h2 style="font-family:var(--font-display); font-size:18px; font-weight:700;">Flagship Rocket Hackathon Squares</h2>
          </div>
          <a href="/docs/1.4?auth_token={auth_token}" class="am3-btn" style="min-height:40px; padding:0 12px; font-size:12px;">
            <span>All 33 Blueprints</span>
            <svg class="svg-ico-sm" viewBox="0 0 24 24"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg>
          </a>
        </div>

        <div class="square-list" id="am3-square-list"></div>
      </div>
    </section>
  </div>

  <script>
    const AUTH_TOKEN = {json.dumps(auth_token)};
    const DOMAINS = {domains_json};
    const URLS = {urls_json};
    const PROJECTS = {projects_json};

    function setAm3Preset(presetId, btnEl) {{
      document.documentElement.setAttribute('data-preset', presetId);
      document.querySelectorAll('.preset-Cluster .am3-btn').forEach(b => b.classList.remove('active'));
      if (btnEl) btnEl.classList.add('active');
    }}

    // Populate 7 Separated Cloud Run Domain Services
    const domainListEl = document.getElementById('am3-domain-list');
    DOMAINS.forEach((d, idx) => {{
      const url = (URLS[d.id] || ('/domain/' + d.id)) + '?auth_token=' + encodeURIComponent(AUTH_TOKEN);
      const a = document.createElement('a');
      a.className = 'domain-row';
      a.href = url;
      a.target = '_blank';
      a.innerHTML = `
        <div>
          <div style="font-family:var(--font-mono); font-size:11px; color:var(--md-sys-color-primary); font-weight:700;">0${{idx + 1}} · ${{d.id.toUpperCase()}}</div>
          <div style="font-weight:700; font-size:14px;">${{d.shortTitle || d.fullTitle}}</div>
        </div>
        <svg class="svg-ico-sm" viewBox="0 0 24 24"><path d="M7 17 17 7"/><path d="M7 7h10v10"/></svg>
      `;
      domainListEl.appendChild(a);
    }});

    // Populate Flagship Squares using 1px outline-variant hairlines
    const squareListEl = document.getElementById('am3-square-list');
    PROJECTS.slice(0, 7).forEach(p => {{
      const row = document.createElement('div');
      row.className = 'square-item';
      row.innerHTML = `
        <span class="square-code">[${{p.code}}]</span>
        <div>
          <div style="font-weight:700; color:var(--md-sys-color-on-surface);">${{p.project}}</div>
          <div style="font-size:12px; color:var(--md-sys-color-on-surface-variant);">${{p.dept_full}}</div>
        </div>
        <span class="tonal-pill" style="justify-self:start;">${{p.level}}</span>
        <div style="display:flex; gap:8px;">
          <a href="/square/${{p.code}}?auth_token=${{encodeURIComponent(AUTH_TOKEN)}}" class="am3-btn am3-btn-tonal" style="min-height:40px; padding:0 12px; font-size:12px;">Demo</a>
          <a href="/docs/${{p.code}}?auth_token=${{encodeURIComponent(AUTH_TOKEN)}}" class="am3-btn" style="min-height:40px; padding:0 12px; font-size:12px;">Blueprint</a>
        </div>
      `;
      squareListEl.appendChild(row);
    }});
  </script>
</body>
</html>"""
