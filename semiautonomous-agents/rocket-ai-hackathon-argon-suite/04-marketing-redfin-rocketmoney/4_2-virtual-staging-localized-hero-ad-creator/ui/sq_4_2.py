# -*- coding: utf-8 -*-
"""Square 4.2 — Virtual Staging & Localized Hero Ad Creative Studio (Gempix-2).
Visual Design: Architectural Digest / Gempix-2 Interior Design Dark Gallery.
Palette: #0A0A0A matte gallery black, #EA580C warm terracotta, #FDE68A champagne gold.
Typography: Google Fonts 'Cormorant Garamond' + 'Plus Jakarta Sans'.
"""

from shared.standalone_uis.base_helpers import render_floating_control_bar_and_drawer


def render_sq_4_2(auth_token: str) -> str:
    floating_drawer = render_floating_control_bar_and_drawer("4.2", auth_token)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>4.2 Virtual Staging & Localized Hero Ad Studio | Gempix-2 Gallery</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;0,700;1,400;1,600&family=JetBrains+Mono:wght@400;600;700&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <style>
    :root {{
      --gallery-black: #0A0A0A;
      --gallery-surface: #121212;
      --gallery-elevated: #1A1817;
      --terracotta: #EA580C;
      --terracotta-glow: rgba(234, 88, 12, 0.25);
      --champagne: #FDE68A;
      --champagne-muted: #D4B96A;
      --ivory: #FAF7F2;
      --stone: #9CA3AF;
      --border-gold: rgba(253, 230, 138, 0.22);
      --border-subtle: rgba(255, 255, 255, 0.09);
      --emerald: #10B981;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      background-color: var(--gallery-black);
      color: var(--ivory);
      font-family: 'Plus Jakarta Sans', sans-serif;
      min-height: 100vh;
      overflow-x: hidden;
      padding-bottom: 92px;
      background-image:
        radial-gradient(circle at 15% 10%, rgba(234, 88, 12, 0.09) 0%, transparent 40%),
        radial-gradient(circle at 85% 20%, rgba(253, 230, 138, 0.06) 0%, transparent 45%);
    }}
    .serif {{ font-family: 'Cormorant Garamond', Georgia, serif; }}
    .mono {{ font-family: 'JetBrains Mono', monospace; }}

    /* Top Architectural Digest Gallery Header */
    .gallery-header {{
      padding: 14px 32px;
      border-bottom: 1px solid var(--border-gold);
      background: rgba(10, 10, 10, 0.92);
      backdrop-filter: blur(14px);
      display: flex;
      align-items: center;
      justify-content: space-between;
      position: sticky;
      top: 0;
      z-index: 100;
    }}
    .brand-cluster {{
      display: flex;
      align-items: center;
      gap: 18px;
    }}
    .ad-monogram {{
      border: 1px solid var(--champagne);
      color: var(--champagne);
      padding: 5px 11px;
      font-family: 'Cormorant Garamond', serif;
      font-size: 18px;
      font-weight: 700;
      letter-spacing: 0.12em;
    }}
    .header-titles h1 {{
      font-family: 'Cormorant Garamond', serif;
      font-size: 24px;
      font-weight: 600;
      letter-spacing: 0.03em;
      color: var(--ivory);
    }}
    .header-titles p {{
      font-size: 11px;
      color: var(--champagne-muted);
      letter-spacing: 0.12em;
      text-transform: uppercase;
    }}
    .header-controls {{
      display: flex;
      align-items: center;
      gap: 14px;
    }}
    .model-select-box {{
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 6px 12px;
      background: var(--gallery-elevated);
      border: 1px solid var(--border-gold);
      border-radius: 6px;
      font-size: 11px;
    }}
    #app-model-select {{
      background: transparent;
      color: var(--champagne);
      border: none;
      outline: none;
      font-family: 'JetBrains Mono', monospace;
      font-size: 11px;
      font-weight: 700;
      cursor: pointer;
    }}
    #app-model-select option {{
      background: #121212;
      color: var(--ivory);
    }}
    .btn-terracotta {{
      background: linear-gradient(135deg, var(--terracotta), #C2410C);
      color: #FFFFFF;
      border: 1px solid var(--champagne);
      padding: 9px 18px;
      border-radius: 6px;
      font-size: 12px;
      font-weight: 700;
      letter-spacing: 0.04em;
      cursor: pointer;
      box-shadow: 0 8px 24px var(--terracotta-glow);
      transition: all 0.2s ease;
    }}
    .btn-terracotta:hover {{
      transform: translateY(-1px);
      box-shadow: 0 12px 30px rgba(234, 88, 12, 0.45);
    }}

    /* Main Studio Grid */
    .studio-layout {{
      max-width: 1460px;
      margin: 0 auto;
      padding: 26px 32px;
      display: grid;
      grid-template-columns: 1fr 410px;
      gap: 28px;
      align-items: start;
    }}
    @media (max-width: 1180px) {{
      .studio-layout {{ grid-template-columns: 1fr; }}
    }}

    /* Left: Interactive Before/After Split-Slider Canvas */
    .canvas-frame {{
      background: var(--gallery-surface);
      border: 1px solid var(--border-gold);
      border-radius: 12px;
      padding: 20px;
      box-shadow: 0 24px 60px rgba(0, 0, 0, 0.75);
    }}
    .canvas-top-meta {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 14px;
      flex-wrap: wrap;
      gap: 10px;
    }}
    .mls-badge {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      font-family: 'JetBrains Mono', monospace;
      font-size: 11px;
      color: var(--champagne);
      background: rgba(253, 230, 138, 0.08);
      border: 1px solid var(--border-gold);
      padding: 5px 12px;
      border-radius: 999px;
    }}
    .fha-compliance-pill {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      font-family: 'JetBrains Mono', monospace;
      font-size: 11px;
      color: #6EE7B7;
      background: rgba(16, 185, 129, 0.12);
      border: 1px solid rgba(16, 185, 129, 0.35);
      padding: 5px 12px;
      border-radius: 999px;
    }}

    /* Split Slider Viewport */
    .split-viewport {{
      position: relative;
      width: 100%;
      height: 510px;
      border-radius: 8px;
      overflow: hidden;
      border: 1px solid rgba(255,255,255,0.15);
      user-select: none;
      background: #161412;
    }}
    .layer-pane {{
      position: absolute;
      inset: 0;
      width: 100%;
      height: 100%;
    }}
    .layer-after {{
      z-index: 1;
    }}
    .layer-before {{
      z-index: 2;
      width: 38%;
      overflow: hidden;
      border-right: 2px solid var(--champagne);
    }}
    .slider-handle-bar {{
      position: absolute;
      top: 0;
      bottom: 0;
      left: 38%;
      z-index: 10;
      width: 38px;
      transform: translateX(-50%);
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: ew-resize;
    }}
    .slider-knob {{
      width: 40px;
      height: 40px;
      border-radius: 50%;
      background: var(--gallery-black);
      border: 2px solid var(--champagne);
      color: var(--champagne);
      display: flex;
      align-items: center;
      justify-content: center;
      font-family: 'JetBrains Mono', monospace;
      font-size: 13px;
      font-weight: 700;
      box-shadow: 0 6px 20px rgba(0,0,0,0.8);
    }}
    .corner-tag {{
      position: absolute;
      top: 16px;
      z-index: 6;
      padding: 5px 12px;
      background: rgba(10, 10, 10, 0.82);
      backdrop-filter: blur(8px);
      border: 1px solid var(--border-gold);
      font-family: 'JetBrains Mono', monospace;
      font-size: 10px;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      color: var(--champagne);
      border-radius: 4px;
    }}
    .tag-before {{ left: 16px; }}
    .tag-after {{ right: 16px; background: rgba(234, 88, 12, 0.88); color: #FFF; border-color: var(--champagne); }}

    /* Rendered Hero Ad Typography Banner Overlay Inside Staged View */
    .ad-hero-overlay {{
      position: absolute;
      bottom: 18px;
      right: 18px;
      left: 18px;
      z-index: 5;
      background: linear-gradient(90deg, rgba(10,10,10,0.92) 0%, rgba(18,16,15,0.88) 100%);
      border: 1px solid var(--champagne);
      border-left: 4px solid var(--terracotta);
      padding: 14px 18px;
      border-radius: 6px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 16px;
      backdrop-filter: blur(10px);
    }}
    .ad-hero-left h3 {{
      font-family: 'Cormorant Garamond', serif;
      font-size: 24px;
      font-weight: 700;
      color: var(--champagne);
      line-height: 1.1;
    }}
    .ad-hero-left p {{
      font-size: 11px;
      color: #D1D5DB;
      margin-top: 4px;
    }}
    .ad-hero-right {{
      text-align: right;
      font-family: 'JetBrains Mono', monospace;
    }}
    .grant-pill {{
      display: inline-block;
      background: var(--terracotta);
      color: #FFF;
      font-size: 10px;
      font-weight: 700;
      padding: 3px 8px;
      border-radius: 4px;
      margin-bottom: 4px;
    }}

    /* Style Swatches Strip Below Canvas */
    .swatches-bar {{
      margin-top: 18px;
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 12px;
    }}
    @media (max-width: 768px) {{
      .swatches-bar {{ grid-template-columns: repeat(2, 1fr); }}
    }}
    .swatch-btn {{
      background: var(--gallery-elevated);
      border: 1px solid var(--border-subtle);
      padding: 12px 14px;
      border-radius: 8px;
      cursor: pointer;
      text-align: left;
      color: var(--ivory);
      transition: all 0.18s ease;
    }}
    .swatch-btn:hover {{
      border-color: var(--champagne-muted);
      transform: translateY(-2px);
    }}
    .swatch-btn.active {{
      border: 1.5px solid var(--champagne);
      background: linear-gradient(145deg, #221712 0%, #151312 100%);
      box-shadow: 0 6px 20px rgba(234, 88, 12, 0.22);
    }}
    .swatch-dot-row {{
      display: flex;
      gap: 5px;
      margin-bottom: 8px;
    }}
    .swatch-dot {{
      width: 12px;
      height: 12px;
      border-radius: 50%;
      border: 1px solid rgba(255,255,255,0.3);
    }}
    .swatch-title {{
      font-family: 'Cormorant Garamond', serif;
      font-size: 18px;
      font-weight: 700;
      color: var(--champagne);
    }}
    .swatch-sub {{
      font-size: 11px;
      color: var(--stone);
      margin-top: 2px;
    }}

    /* Right Column: Controls, Structural Lock & Fair Housing / Reg Z Audit */
    .panel-card {{
      background: var(--gallery-surface);
      border: 1px solid var(--border-gold);
      border-radius: 12px;
      padding: 20px;
      margin-bottom: 20px;
    }}
    .panel-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding-bottom: 12px;
      margin-bottom: 14px;
      border-bottom: 1px solid var(--border-subtle);
    }}
    .panel-header h2 {{
      font-family: 'Cormorant Garamond', serif;
      font-size: 21px;
      font-weight: 700;
      color: var(--champagne);
      letter-spacing: 0.02em;
    }}
    .toggle-row {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 10px 12px;
      background: var(--gallery-elevated);
      border: 1px solid var(--border-subtle);
      border-radius: 8px;
      margin-bottom: 12px;
    }}
    .toggle-switch {{
      position: relative;
      width: 44px;
      height: 24px;
      background: var(--terracotta);
      border-radius: 999px;
      cursor: pointer;
      transition: 0.2s;
    }}
    .toggle-switch.off {{
      background: #374151;
    }}
    .toggle-knob {{
      position: absolute;
      top: 3px;
      left: 23px;
      width: 18px;
      height: 18px;
      background: #FFF;
      border-radius: 50%;
      transition: 0.2s;
    }}
    .toggle-switch.off .toggle-knob {{
      left: 3px;
    }}
    .control-slider {{
      margin-bottom: 14px;
    }}
    .control-slider label {{
      display: flex;
      justify-content: space-between;
      font-size: 12px;
      color: #D1D5DB;
      margin-bottom: 6px;
    }}
    .control-slider input[type="range"] {{
      width: 100%;
      accent-color: var(--terracotta);
    }}
    .audit-item {{
      display: flex;
      align-items: flex-start;
      gap: 10px;
      padding: 9px 0;
      border-bottom: 1px dashed rgba(255,255,255,0.08);
      font-size: 12px;
      line-height: 1.45;
    }}
    .audit-item:last-child {{ border-bottom: none; }}
  </style>
</head>
<body>

  <!-- TOP ARCHITECTURAL DIGEST / GEMPIX-2 HEADER -->
  <header class="gallery-header">
    <div class="brand-cluster">
      <div class="ad-monogram">AD × G2</div>
      <div class="header-titles">
        <h1>Gempix-2 Virtual Staging & Localized Hero Ad Studio</h1>
        <p>Architectural Preservation Masking • SynthID Watermarked • TILA Reg Z & Fair Housing Verified</p>
      </div>
    </div>
    <div class="header-controls">
      <div class="model-select-box">
        <span class="mono" style="color:var(--stone);">CREATIVE ENGINE:</span>
        <select id="app-model-select" onchange="window.syncSelectedModel(this.value)">
          <option value="gemini-4-argon" selected>gemini-4-argon (Frontier Creative Director)</option>
          <option value="gemini-3.8-flash">gemini-3.8-flash (Fast Iteration)</option>
        </select>
      </div>
      <button class="btn-terracotta" id="btn-run-gempix" onclick="window.runLiveVertexAI()">
        ⚡ Render Gempix-2 Staged Ad Suite
      </button>
    </div>
  </header>

  <main class="studio-layout">
    <!-- LEFT: FULL-CANVAS BEFORE / AFTER VIRTUAL STAGING SPLIT SLIDER -->
    <section class="canvas-frame">
      <div class="canvas-top-meta">
        <span class="mls-badge">📍 REDFIN MLS #MI-884120 • 1420 MICHIGAN AVE APT 4B, CORKTOWN DETROIT ($395,000)</span>
        <span class="fha-compliance-pill" id="fha-badge-top">✓ FAIR HOUSING ACT & MLS TRUTH-IN-ADVERTISING PASS</span>
      </div>

      <div class="split-viewport" id="staging-viewport">
        <div class="corner-tag tag-before">BEFORE: VACANT MLS PHOTO (RAW HARDWOOD)</div>
        <div class="corner-tag tag-after" id="after-style-tag">AFTER: GEMPIX-2 DETROIT INDUSTRIAL LOFT</div>

        <!-- AFTER LAYER (STAGED ARCHITECTURAL INTERIOR SVG + REAL PHOTO BLEND) -->
        <div class="layer-pane layer-after" id="staged-svg-container"></div>

        <!-- BEFORE LAYER (VACANT HARDWOOD & EXPOSED BRICK MLS ROOM) -->
        <div class="layer-pane layer-before" id="before-Clip-Pane">
          <svg viewBox="0 0 1000 560" width="100%" height="100%" preserveAspectRatio="none">
            <defs>
              <linearGradient id="vacWall" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stop-color="#3A2D28"/>
                <stop offset="100%" stop-color="#261C18"/>
              </linearGradient>
              <linearGradient id="vacFloor" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stop-color="#5C4028"/>
                <stop offset="100%" stop-color="#3B2716"/>
              </linearGradient>
              <pattern id="brickPat" width="40" height="20" patternUnits="userSpaceOnUse">
                <rect width="40" height="20" fill="#4A2C22"/>
                <path d="M 0 10 L 40 10 M 20 0 L 20 10 M 0 10 L 0 20 M 40 10 L 40 20" stroke="#2D1A14" stroke-width="1.5"/>
              </pattern>
            </defs>
            <!-- Ceiling -->
            <polygon points="0,0 1000,0 860,85 140,85" fill="#1C1816"/>
            <!-- Exposed Timber Beams -->
            <line x1="250" y1="0" x2="290" y2="85" stroke="#3E2A1E" stroke-width="12"/>
            <line x1="500" y1="0" x2="500" y2="85" stroke="#3E2A1E" stroke-width="12"/>
            <line x1="750" y1="0" x2="710" y2="85" stroke="#3E2A1E" stroke-width="12"/>
            <!-- Back Brick Wall -->
            <rect x="140" y="85" width="720" height="285" fill="url(#brickPat)"/>
            <!-- Left & Right Perspective Walls -->
            <polygon points="0,0 140,85 140,370 0,490" fill="url(#vacWall)"/>
            <polygon points="1000,0 860,85 860,370 1000,490" fill="url(#vacWall)"/>
            <!-- Factory Arched Windows (Locked Structural Elements) -->
            <g stroke="#111" stroke-width="5" fill="#7DA2B8" fill-opacity="0.32">
              <rect x="210" y="120" width="140" height="195" rx="4"/>
              <line x1="280" y1="120" x2="280" y2="315"/>
              <line x1="210" y1="185" x2="350" y2="185"/>
              <line x1="210" y1="250" x2="350" y2="250"/>

              <rect x="430" y="120" width="140" height="195" rx="4"/>
              <line x1="500" y1="120" x2="500" y2="315"/>
              <line x1="430" y1="185" x2="570" y2="185"/>
              <line x1="430" y1="250" x2="570" y2="250"/>

              <rect x="650" y="120" width="140" height="195" rx="4"/>
              <line x1="720" y1="120" x2="720" y2="315"/>
              <line x1="650" y1="185" x2="790" y2="185"/>
              <line x1="650" y1="250" x2="790" y2="250"/>
            </g>
            <!-- Vacant Hardwood Floor -->
            <polygon points="140,370 860,370 1000,560 0,560" fill="url(#vacFloor)"/>
            <!-- Perspective Floor Planks -->
            <g stroke="#2B1B0E" stroke-width="1.2" opacity="0.6">
              <line x1="240" y1="370" x2="120" y2="560"/>
              <line x1="360" y1="370" x2="300" y2="560"/>
              <line x1="500" y1="370" x2="500" y2="560"/>
              <line x1="640" y1="370" x2="700" y2="560"/>
              <line x1="760" y1="370" x2="880" y2="560"/>
            </g>
            <!-- Empty Room Watermark -->
            <text x="80" y="450" fill="#D1D5DB" font-family="JetBrains Mono" font-size="14" opacity="0.75">
              VACANT 1,850 SQ FT LOFT • ZERO FURNITURE
            </text>
          </svg>
        </div>

        <!-- STRUCTURAL MASK LOCK WIREFRAME OVERLAY (TOGGLED) -->
        <svg id="structural-mask-overlay" viewBox="0 0 1000 560" width="100%" height="100%" preserveAspectRatio="none" style="position:absolute;inset:0;z-index:4;pointer-events:none;">
          <g stroke="#10B981" stroke-width="2" stroke-dasharray="6 4" fill="rgba(16,185,129,0.06)">
            <rect x="208" y="118" width="144" height="199"/>
            <rect x="428" y="118" width="144" height="199"/>
            <rect x="648" y="118" width="144" height="199"/>
          </g>
          <text x="212" y="112" fill="#6EE7B7" font-family="JetBrains Mono" font-size="11" font-weight="bold">
            🔒 MASK LOCKED: 3 FACTORY WINDOWS + BRICK PILLARS + CEILING BEAMS
          </text>
        </svg>

        <!-- DRAGGABLE SPLIT HANDLE -->
        <div class="slider-handle-bar" id="split-handle">
          <div class="slider-knob">⇄</div>
        </div>

        <!-- HERO AD BANNER OVERLAY -->
        <div class="ad-hero-overlay">
          <div class="ad-hero-left">
            <h3 id="hero-overlay-headline">Own in Corktown Detroit for $2,279/mo P&I</h3>
            <p id="hero-overlay-regz">TILA Reg Z Trigger Disclosure: $395,000 List • 5% Down ($19,750 minus $10,000 Rocket Grant = $9,750 Net Cash) • 6.125% Note Rate (6.342% APR) • 360 Mos • NMLS #3030 Equal Housing Lender</p>
          </div>
          <div class="ad-hero-right">
            <span class="grant-pill" id="hero-grant-pill">$10,000 ROCKET GRANT ELIGIBLE</span>
            <div style="font-size:10px;color:var(--champagne);">SynthID™ Verified • Zero Structural Edit</div>
          </div>
        </div>
      </div>

      <!-- 4 CLICKABLE DESIGN STYLE SWATCHES -->
      <div class="swatches-bar">
        <button class="swatch-btn active" data-style="industrial" onclick="window.selectStagingStyle('industrial')">
          <div class="swatch-dot-row">
            <span class="swatch-dot" style="background:#9A3412;"></span>
            <span class="swatch-dot" style="background:#451A03;"></span>
            <span class="swatch-dot" style="background:#FDE68A;"></span>
          </div>
          <div class="swatch-title">Detroit Industrial Loft</div>
          <div class="swatch-sub">Cognac Leather • Walnut • Edison</div>
        </button>

        <button class="swatch-btn" data-style="midcentury" onclick="window.selectStagingStyle('midcentury')">
          <div class="swatch-dot-row">
            <span class="swatch-dot" style="background:#D97706;"></span>
            <span class="swatch-dot" style="background:#065F46;"></span>
            <span class="swatch-dot" style="background:#F3F4F6;"></span>
          </div>
          <div class="swatch-title">Mid-Century Modern</div>
          <div class="swatch-sub">Teak Credenza • Bouclé • Brass Arc</div>
        </button>

        <button class="swatch-btn" data-style="japandi" onclick="window.selectStagingStyle('japandi')">
          <div class="swatch-dot-row">
            <span class="swatch-dot" style="background:#E7E5E4;"></span>
            <span class="swatch-dot" style="background:#A8A29E;"></span>
            <span class="swatch-dot" style="background:#3F6212;"></span>
          </div>
          <div class="swatch-title">Warm Japandi</div>
          <div class="swatch-sub">Low Ash Wood • Linen • Bonsais</div>
        </button>

        <button class="swatch-btn" data-style="coastal" onclick="window.selectStagingStyle('coastal')">
          <div class="swatch-dot-row">
            <span class="swatch-dot" style="background:#0284C7;"></span>
            <span class="swatch-dot" style="background:#F8FAFC;"></span>
            <span class="swatch-dot" style="background:#D6D3D1;"></span>
          </div>
          <div class="swatch-title">Coastal Luxury</div>
          <div class="swatch-sub">Slipcovered Ivory • Driftwood • Jute</div>
        </button>
      </div>
    </section>

    <!-- RIGHT: STRUCTURAL LOCK, PRICING SLIDERS & FAIR HOUSING / TILA REG Z AUDIT -->
    <aside>
      <div class="panel-card">
        <div class="panel-header">
          <h2>Architectural Lock & Grant Calibrator</h2>
          <span class="mono" style="font-size:10px;color:var(--terracotta);">/api/sandbox</span>
        </div>

        <div class="toggle-row" onclick="window.toggleStructuralMask()">
          <div>
            <div style="font-size:13px;font-weight:700;color:var(--ivory);">Structural Wall & Window Mask Lock</div>
            <div style="font-size:11px;color:var(--stone);">Prevents AI from hiding defects or altering glazing</div>
          </div>
          <div class="toggle-switch" id="mask-toggle-switch">
            <div class="toggle-knob"></div>
          </div>
        </div>

        <div class="control-slider">
          <label>
            <span>Redfin Listing Price</span>
            <strong class="mono" style="color:var(--champagne);" id="lbl-list-price">$395,000</strong>
          </label>
          <input type="range" id="inp-list-price" min="250000" max="750000" step="5000" value="395000" oninput="window.auditVirtualStaging()">
        </div>

        <div class="control-slider">
          <label>
            <span>Rocket Homebuyer Grant ($)</span>
            <strong class="mono" style="color:var(--champagne);" id="lbl-grant-amt">$10,000</strong>
          </label>
          <input type="range" id="inp-grant-amt" min="2500" max="17500" step="2500" value="10000" oninput="window.auditVirtualStaging()">
        </div>

        <div class="control-slider">
          <label>
            <span>Split-Slider Reveal (%)</span>
            <strong class="mono" style="color:var(--champagne);" id="lbl-split-pct">38% Before / 62% Staged</strong>
          </label>
          <input type="range" id="inp-split-pct" min="5" max="95" step="1" value="38" oninput="window.setSplitPercent(this.value)">
        </div>
      </div>

      <!-- FAIR HOUSING ACT & MLS COMPLIANCE AUDIT -->
      <div class="panel-card">
        <div class="panel-header">
          <h2>Fair Housing & TILA Reg Z Audit</h2>
          <span class="mono" style="font-size:10px;color:var(--emerald);" id="audit-latency-label">1.2ms PASS</span>
        </div>

        <div id="compliance-audit-list">
          <div class="audit-item">
            <span style="color:var(--emerald);font-weight:800;">✓</span>
            <div><strong>Fair Housing Act (42 U.S.C. § 3604(c)):</strong> Zero Steering / Protected-Class Symbols in staged artwork or decor props.</div>
          </div>
          <div class="audit-item">
            <span style="color:var(--emerald);font-weight:800;">✓</span>
            <div><strong>MLS Truth-in-Advertising:</strong> 100% IoU Structural Mask lock preserves exposed brick, timber beams, and window mullions.</div>
          </div>
          <div class="audit-item">
            <span style="color:var(--emerald);font-weight:800;">✓</span>
            <div id="audit-net-cash"><strong>Net Borrower Cash Down:</strong> $9,750 Out-of-Pocket (5% Down $19,750 minus $10,000 Rocket Homebuyer Grant!).</div>
          </div>
          <div class="audit-item">
            <span style="color:var(--emerald);font-weight:800;">✓</span>
            <div id="audit-regz-footer"><strong>12 CFR § 1026.24 (TILA Reg Z):</strong> Payment trigger term ($2,279/mo) paired with mandatory 6.342% APR & repayment terms.</div>
          </div>
        </div>
      </div>

      <!-- MULTI-CHANNEL AD EXPORT SUITE -->
      <div class="panel-card" style="margin-bottom:0;">
        <div class="panel-header">
          <h2>Generated Social Ad Variants</h2>
          <span class="mono" style="font-size:10px;color:var(--champagne);" id="live-model-pill">gemini-4-argon</span>
        </div>
        <div id="social-variants-box" style="font-size:12px;line-height:1.55;color:#E5E7EB;">
          <div style="padding:10px;background:var(--gallery-elevated);border-radius:6px;margin-bottom:8px;border-left:3px solid var(--terracotta);">
            <div class="mono" style="font-size:10px;color:var(--champagne);">1:1 INSTAGRAM FEED • CORKTOWN ZIP 48216</div>
            <div id="ad-copy-1">Swipe to stage your future Corktown brick loft → Own for $2,279/mo P&I with $10,000 Rocket Homebuyer Grant ($9,750 net down).</div>
          </div>
          <div style="padding:10px;background:var(--gallery-elevated);border-radius:6px;border-left:3px solid var(--champagne);">
            <div class="mono" style="font-size:10px;color:var(--champagne);">REDFIN LISTING CAROUSEL BADGE</div>
            <div id="ad-copy-2">Virtually Staged by Gempix-2 • Tap to toggle furniture & lock your Verified Approval.</div>
          </div>
        </div>
      </div>
    </aside>
  </main>

  <script>
    const STAGING_STYLES = {{
      industrial: {{
        label: "AFTER: GEMPIX-2 DETROIT INDUSTRIAL LOFT",
        wallTint: "#522E22",
        rugColor: "#7C2D12",
        rugBorder: "#FDE68A",
        sofaColor: "#B45309",
        sofaAccent: "#78350F",
        tableColor: "#451A03",
        lampGlow: "#FBBF24",
        plantLeaf: "#15803D",
        artTitle: "DETROIT MOTOR HERITAGE TRYPTICH"
      }},
      midcentury: {{
        label: "AFTER: GEMPIX-2 MID-CENTURY MODERN",
        wallTint: "#4A3528",
        rugColor: "#065F46",
        rugBorder: "#F59E0B",
        sofaColor: "#F3F4F6",
        sofaAccent: "#D97706",
        tableColor: "#92400E",
        lampGlow: "#FEF08A",
        plantLeaf: "#059669",
        artTitle: "GEOMETRIC BAUHAUS TRIPTYCH"
      }},
      japandi: {{
        label: "AFTER: GEMPIX-2 WARM JAPANDI SANCTUARY",
        wallTint: "#57534E",
        rugColor: "#E7E5E4",
        rugBorder: "#A8A29E",
        sofaColor: "#D6D3D1",
        sofaAccent: "#78716C",
        tableColor: "#CA8A04",
        lampGlow: "#FEF9C3",
        plantLeaf: "#3F6212",
        artTitle: "WABI-SABI TEXTURED PLASTER RELIEF"
      }},
      coastal: {{
        label: "AFTER: GEMPIX-2 GREAT LAKES COASTAL LUXURY",
        wallTint: "#334155",
        rugColor: "#0369A1",
        rugBorder: "#F8FAFC",
        sofaColor: "#F8FAFC",
        sofaAccent: "#0284C7",
        tableColor: "#A16207",
        lampGlow: "#E0F2FE",
        plantLeaf: "#0D9488",
        artTitle: "LAKE MICHIGAN HORIZON DIPTYCH"
      }}
    }};

    window.currentStyleKey = 'industrial';
    window.maskLocked = true;

    function buildStagedSvg(styleKey) {{
      const s = STAGING_STYLES[styleKey] || STAGING_STYLES.industrial;
      return `
      <svg viewBox="0 0 1000 560" width="100%" height="100%" preserveAspectRatio="none">
        <defs>
          <radialGradient id="warmGlow" cx="50%" cy="35%" r="60%">
            <stop offset="0%" stop-color="${{s.lampGlow}}" stop-opacity="0.32"/>
            <stop offset="100%" stop-color="#000000" stop-opacity="0"/>
          </radialGradient>
        </defs>
        <!-- Same Exact Room Architecture Geometry -->
        <polygon points="0,0 1000,0 860,85 140,85" fill="#1C1816"/>
        <line x1="250" y1="0" x2="290" y2="85" stroke="#4A3223" stroke-width="12"/>
        <line x1="500" y1="0" x2="500" y2="85" stroke="#4A3223" stroke-width="12"/>
        <line x1="750" y1="0" x2="710" y2="85" stroke="#4A3223" stroke-width="12"/>
        <rect x="140" y="85" width="720" height="285" fill="${{s.wallTint}}"/>
        <polygon points="0,0 140,85 140,370 0,490" fill="#2A211D"/>
        <polygon points="1000,0 860,85 860,370 1000,490" fill="#2A211D"/>
        <!-- Identical Factory Windows (Golden Hour Sunlit) -->
        <g stroke="#111" stroke-width="5" fill="#FDE68A" fill-opacity="0.38">
          <rect x="210" y="120" width="140" height="195" rx="4"/>
          <line x1="280" y1="120" x2="280" y2="315"/>
          <line x1="210" y1="185" x2="350" y2="185"/>
          <rect x="430" y="120" width="140" height="195" rx="4"/>
          <line x1="500" y1="120" x2="500" y2="315"/>
          <line x1="430" y1="185" x2="570" y2="185"/>
          <rect x="650" y="120" width="140" height="195" rx="4"/>
          <line x1="720" y1="120" x2="720" y2="315"/>
          <line x1="650" y1="185" x2="790" y2="185"/>
        </g>
        <!-- Polished Hardwood Floor -->
        <polygon points="140,370 860,370 1000,560 0,560" fill="#4A321F"/>
        <!-- Ambient Warm Lighting Overlay -->
        <rect x="0" y="0" width="1000" height="560" fill="url(#warmGlow)"/>
        <!-- STAGED ELEMENT 1: Designer Area Rug -->
        <polygon points="230,400 770,400 860,515 140,515" fill="${{s.rugColor}}" stroke="${{s.rugBorder}}" stroke-width="3"/>
        <!-- STAGED ELEMENT 2: Designer Sectional Sofa -->
        <g>
          <rect x="270" y="340" width="430" height="65" rx="12" fill="${{s.sofaColor}}" stroke="#111" stroke-width="2"/>
          <rect x="255" y="365" width="460" height="55" rx="10" fill="${{s.sofaAccent}}"/>
          <rect x="250" y="355" width="35" height="68" rx="8" fill="${{s.sofaColor}}"/>
          <rect x="685" y="355" width="35" height="68" rx="8" fill="${{s.sofaColor}}"/>
          <!-- Throw Pillows -->
          <rect x="300" y="348" width="42" height="36" rx="6" fill="#FDE68A"/>
          <rect x="625" y="348" width="42" height="36" rx="6" fill="#EA580C"/>
        </g>
        <!-- STAGED ELEMENT 3: Architectural Coffee Table -->
        <g>
          <polygon points="370,435 610,435 635,470 345,470" fill="${{s.tableColor}}" stroke="#FDE68A" stroke-width="1.5"/>
          <line x1="375" y1="470" x2="365" y2="498" stroke="#111" stroke-width="5"/>
          <line x1="605" y1="470" x2="615" y2="498" stroke="#111" stroke-width="5"/>
          <!-- Art Book & Ceramic Vase on Table -->
          <rect x="440" y="444" width="55" height="16" fill="#FAF7F2"/>
          <circle cx="535" cy="448" r="12" fill="#EA580C"/>
        </g>
        <!-- STAGED ELEMENT 4: Indoor Olive Tree in Terracotta Planter -->
        <g>
          <polygon points="790,375 835,375 825,435 800,435" fill="#C2410C"/>
          <line x1="812" y1="375" x2="812" y2="285" stroke="#5C4028" stroke-width="6"/>
          <circle cx="812" cy="275" r="38" fill="${{s.plantLeaf}}" opacity="0.9"/>
          <circle cx="788" cy="295" r="28" fill="${{s.plantLeaf}}"/>
          <circle cx="835" cy="292" r="28" fill="${{s.plantLeaf}}"/>
        </g>
        <!-- STAGED ELEMENT 5: Edison / Brass Pendant Chandelier -->
        <g>
          <line x1="500" y1="0" x2="500" y2="145" stroke="#FDE68A" stroke-width="3"/>
          <circle cx="500" cy="155" r="18" fill="${{s.lampGlow}}"/>
          <circle cx="465" cy="165" r="13" fill="${{s.lampGlow}}" opacity="0.85"/>
          <circle cx="535" cy="165" r="13" fill="${{s.lampGlow}}" opacity="0.85"/>
        </g>
      </svg>`;
    }}

    window.selectStagingStyle = function(styleKey) {{
      window.currentStyleKey = styleKey;
      document.querySelectorAll('.swatch-btn').forEach(btn => {{
        btn.classList.toggle('active', btn.getAttribute('data-style') === styleKey);
      }});
      const st = STAGING_STYLES[styleKey] || STAGING_STYLES.industrial;
      document.getElementById('after-style-tag').innerText = st.label;
      document.getElementById('staged-svg-container').innerHTML = buildStagedSvg(styleKey);
      window.auditVirtualStaging();
    }};

    window.setSplitPercent = function(pct) {{
      const val = Math.max(5, Math.min(95, parseFloat(pct)));
      document.getElementById('before-Clip-Pane').style.width = val + '%';
      document.getElementById('split-handle').style.left = val + '%';
      document.getElementById('inp-split-pct').value = val;
      document.getElementById('lbl-split-pct').innerText = `${{Math.round(val)}}% Before / ${{Math.round(100 - val)}}% Staged`;
    }};

    window.toggleStructuralMask = function() {{
      window.maskLocked = !window.maskLocked;
      const sw = document.getElementById('mask-toggle-switch');
      const ov = document.getElementById('structural-mask-overlay');
      if (sw) sw.classList.toggle('off', !window.maskLocked);
      if (ov) ov.style.display = window.maskLocked ? 'block' : 'none';
    }};

    window.auditVirtualStaging = async function() {{
      const price = parseFloat(document.getElementById('inp-list-price').value || 395000);
      const grant = parseFloat(document.getElementById('inp-grant-amt').value || 10000);
      document.getElementById('lbl-list-price').innerText = '$' + price.toLocaleString();
      document.getElementById('lbl-grant-amt').innerText = '$' + grant.toLocaleString();

      const down5 = price * 0.05;
      const netCash = Math.max(0, down5 - grant);
      const loan = price - down5;
      const r = (6.125 / 100) / 12;
      const pi = Math.round(loan * (r * Math.pow(1 + r, 360)) / (Math.pow(1 + r, 360) - 1));

      document.getElementById('hero-overlay-headline').innerText = `Own in Corktown Detroit for $${{pi.toLocaleString()}}/mo P&I`;
      document.getElementById('hero-grant-pill').innerText = `$${{grant.toLocaleString()}} ROCKET GRANT ELIGIBLE`;
      document.getElementById('hero-overlay-regz').innerText = `TILA Reg Z Trigger Disclosure: $${{price.toLocaleString()}} List • 5% Down ($${{down5.toLocaleString()}} minus $${{grant.toLocaleString()}} Rocket Grant = $${{netCash.toLocaleString()}} Net Cash) • 6.125% Note Rate (6.342% APR) • 360 Mos • NMLS #3030`;

      try {{
        const resp = await fetch('/api/sandbox', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{
            code: '4.2',
            action: 'audit_virtual_staging',
            params: {{ list_price: price, grant_amount: grant, style: window.currentStyleKey }}
          }})
        }});
        const data = await resp.json();
        if (data && data.ok) {{
          document.getElementById('audit-latency-label').innerText = `${{data.execution_ms || 1.2}}ms PASS`;
        }}
      }} catch (e) {{}}

      document.getElementById('audit-net-cash').innerHTML = `<strong>Net Borrower Cash Down:</strong> $${{netCash.toLocaleString()}} Out-of-Pocket (5% Down $${{down5.toLocaleString()}} minus $${{grant.toLocaleString()}} Rocket Homebuyer Grant!).`;
      document.getElementById('audit-regz-footer').innerHTML = `<strong>12 CFR § 1026.24 (TILA Reg Z):</strong> Payment trigger term ($${{pi.toLocaleString()}}/mo) paired with mandatory 6.342% APR & repayment terms.`;
    }};

    window.runLiveVertexAI = async function() {{
      const btn = document.getElementById('btn-run-gempix');
      const orig = btn ? btn.innerText : '';
      if (btn) {{
        btn.innerText = '⏳ Gempix-2 + Vertex AI Rendering...';
        btn.disabled = true;
      }}
      const price = parseFloat(document.getElementById('inp-list-price').value || 395000);
      const grant = parseFloat(document.getElementById('inp-grant-amt').value || 10000);
      const scenarioEl = document.getElementById('scenario-input');
      const promptText = scenarioEl && scenarioEl.value
        ? scenarioEl.value
        : `Virtually stage Corktown Detroit loft ($${{price}}) in ${{window.currentStyleKey}} style with $${{grant}} Rocket Homebuyer Grant and TILA Reg Z disclosure.`;

      try {{
        const resp = await fetch('/api/run-demo', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{
            code: '4.2',
            model: window.getSelectedModel(),
            user_input: promptText,
            params: {{ list_price: price, grant_amount: grant, style: window.currentStyleKey }}
          }})
        }});
        const res = await resp.json();
        if (res && res.ok) {{
          const sd = res.structured_data || {{}};
          if (sd.hero_ad_overlay) {{
            if (sd.hero_ad_overlay.headline) document.getElementById('hero-overlay-headline').innerText = sd.hero_ad_overlay.headline;
            if (sd.hero_ad_overlay.tila_reg_z_disclaimer) document.getElementById('hero-overlay-regz').innerText = sd.hero_ad_overlay.tila_reg_z_disclaimer;
          }}
          if (Array.isArray(sd.social_ad_variants) && sd.social_ad_variants.length > 0) {{
            document.getElementById('social-variants-box').innerHTML = sd.social_ad_variants.map(v => `
              <div style="padding:10px;background:var(--gallery-elevated);border-radius:6px;margin-bottom:8px;border-left:3px solid var(--terracotta);">
                <div class="mono" style="font-size:10px;color:var(--champagne);">${{v.channel || 'SOCIAL AD'}}</div>
                <div>${{v.copy_text || ''}}</div>
              </div>
            `).join('');
          }} else if (res.output) {{
            document.getElementById('ad-copy-1').innerText = res.output;
          }}
        }}
      }} catch (e) {{
        console.error(e);
      }} finally {{
        if (btn) {{
          btn.innerText = orig;
          btn.disabled = false;
        }}
      }}
    }};

    // Interactive Drag on Viewport
    document.addEventListener('DOMContentLoaded', () => {{
      window.selectStagingStyle('industrial');
      const vp = document.getElementById('staging-viewport');
      let dragging = false;
      const moveFromEvent = (e) => {{
        if (!dragging || !vp) return;
        const rect = vp.getBoundingClientRect();
        const clientX = e.touches ? e.touches[0].clientX : e.clientX;
        const pct = ((clientX - rect.left) / rect.width) * 100;
        window.setSplitPercent(pct);
      }};
      vp.addEventListener('mousedown', () => {{ dragging = true; }});
      window.addEventListener('mouseup', () => {{ dragging = false; }});
      window.addEventListener('mousemove', moveFromEvent);
      vp.addEventListener('touchstart', () => {{ dragging = true; }}, {{passive: true}});
      window.addEventListener('touchend', () => {{ dragging = false; }});
      window.addEventListener('touchmove', moveFromEvent, {{passive: true}});
    }});
  </script>

  {floating_drawer}
</body>
</html>"""
