# -*- coding: utf-8 -*-
"""Square 4.1 — Redfin Listing-to-Video Studio (Veo 3.1 + Gemini 4 Argon).
Visual Design: Authentic Redfin / Zillow Real Estate Property Listing Page + Clean Storyboard Creator.
Palette: #FFFFFF pure white background, #C82021 Redfin Red brand header & primary buttons, #F7F7F7 warm stone cards.
Typography: Google Fonts 'Plus Jakarta Sans'.
"""

from shared.standalone_uis.base_helpers import render_floating_control_bar_and_drawer


def render_sq_4_1(auth_token: str) -> str:
    floating_drawer = render_floating_control_bar_and_drawer("4.1", auth_token)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>418 Elmhurst Ave, Royal Oak, MI 48067 | Redfin Listing-to-Video Studio</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <style>
    :root {{
      --bg-white: #FFFFFF;
      --stone-card: #F7F7F7;
      --stone-hover: #EFEFEF;
      --border-light: #E2E8F0;
      --border-stone: #E5E5E5;
      --redfin-red: #C82021;
      --redfin-red-dark: #A31617;
      --redfin-red-tint: #FDF2F2;
      --text-dark: #1E293B;
      --text-main: #222222;
      --text-muted: #595959;
      --text-subtle: #767676;
      --green-badge: #15803D;
      --green-bg: #DCFCE7;
      --blue-accent: #1D4ED8;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      background-color: var(--bg-white);
      color: var(--text-main);
      font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
      min-height: 100vh;
      overflow-x: hidden;
      padding-bottom: 96px;
      line-height: 1.5;
    }}

    /* Top Redfin Navigation Header */
    .redfin-header {{
      background: var(--bg-white);
      border-bottom: 1px solid var(--border-stone);
      position: sticky;
      top: 0;
      z-index: 100;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
    }}
    .redfin-header-inner {{
      max-width: 1380px;
      margin: 0 auto;
      padding: 12px 24px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      flex-wrap: wrap;
    }}
    .brand-cluster {{
      display: flex;
      align-items: center;
      gap: 14px;
    }}
    .redfin-logo {{
      background: var(--redfin-red);
      color: #FFFFFF;
      font-weight: 800;
      font-size: 18px;
      letter-spacing: -0.03em;
      padding: 6px 12px;
      border-radius: 6px;
      display: inline-flex;
      align-items: center;
      gap: 6px;
    }}
    .co-brand-tag {{
      font-size: 13px;
      font-weight: 700;
      color: var(--text-main);
      display: flex;
      align-items: center;
      gap: 8px;
    }}
    .co-brand-pill {{
      background: var(--redfin-red-tint);
      color: var(--redfin-red);
      border: 1px solid #F5C2C2;
      font-size: 11px;
      font-weight: 700;
      padding: 3px 9px;
      border-radius: 999px;
    }}
    .search-bar-mock {{
      flex: 1;
      max-width: 420px;
      display: flex;
      align-items: center;
      background: var(--stone-card);
      border: 1px solid #D4D4D4;
      border-radius: 8px;
      padding: 6px 12px;
      gap: 8px;
    }}
    .search-bar-mock select {{
      width: 100%;
      border: none;
      background: transparent;
      font-family: inherit;
      font-size: 13px;
      font-weight: 600;
      color: var(--text-main);
      outline: none;
      cursor: pointer;
    }}
    .header-actions {{
      display: flex;
      align-items: center;
      gap: 10px;
      flex-wrap: wrap;
    }}
    .model-select-box {{
      display: flex;
      align-items: center;
      gap: 6px;
      background: var(--stone-card);
      border: 1px solid var(--border-stone);
      padding: 6px 10px;
      border-radius: 8px;
      font-size: 12px;
      font-weight: 600;
    }}
    #app-model-select {{
      border: none;
      background: transparent;
      font-family: inherit;
      font-size: 12px;
      font-weight: 700;
      color: var(--redfin-red);
      outline: none;
      cursor: pointer;
    }}
    .btn-redfin {{
      background: var(--redfin-red);
      color: #FFFFFF;
      border: none;
      border-radius: 8px;
      padding: 9px 16px;
      font-family: inherit;
      font-size: 13px;
      font-weight: 700;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 7px;
      transition: background 0.15s ease, transform 0.1s ease;
    }}
    .btn-redfin:hover {{
      background: var(--redfin-red-dark);
    }}
    .btn-outline {{
      background: #FFFFFF;
      color: var(--text-main);
      border: 1px solid #CCCCCC;
      border-radius: 8px;
      padding: 8px 14px;
      font-family: inherit;
      font-size: 13px;
      font-weight: 600;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      transition: all 0.15s ease;
    }}
    .btn-outline:hover {{
      border-color: var(--text-main);
      background: var(--stone-card);
    }}

    /* Main Listing Container */
    .page-container {{
      max-width: 1380px;
      margin: 0 auto;
      padding: 20px 24px;
    }}

    /* Listing Breadcrumb & Top Summary Ribbon */
    .breadcrumb-row {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      font-size: 12px;
      color: var(--text-muted);
      margin-bottom: 14px;
      flex-wrap: wrap;
      gap: 8px;
    }}
    .status-pill {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      background: var(--green-bg);
      color: var(--green-badge);
      font-weight: 700;
      font-size: 11px;
      padding: 4px 10px;
      border-radius: 999px;
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }}
    .status-dot {{
      width: 7px;
      height: 7px;
      border-radius: 50%;
      background: var(--green-badge);
    }}

    .listing-hero-header {{
      display: flex;
      align-items: flex-end;
      justify-content: space-between;
      gap: 24px;
      padding-bottom: 18px;
      border-bottom: 1px solid var(--border-stone);
      margin-bottom: 20px;
      flex-wrap: wrap;
    }}
    .address-block h1 {{
      font-size: clamp(22px, 2.6vw, 30px);
      font-weight: 800;
      color: var(--text-main);
      letter-spacing: -0.02em;
    }}
    .address-sub {{
      font-size: 14px;
      color: var(--text-muted);
      font-weight: 500;
      margin-top: 3px;
    }}
    .key-stats-row {{
      display: flex;
      align-items: center;
      gap: 28px;
      flex-wrap: wrap;
    }}
    .stat-item {{
      display: flex;
      flex-direction: column;
    }}
    .stat-val {{
      font-size: 24px;
      font-weight: 800;
      color: var(--text-main);
      letter-spacing: -0.02em;
    }}
    .stat-val.red {{
      color: var(--redfin-red);
    }}
    .stat-lbl {{
      font-size: 12px;
      color: var(--text-muted);
      font-weight: 600;
    }}

    /* Architectural Photo Gallery Grid */
    .gallery-section-title {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 10px;
    }}
    .gallery-grid {{
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 14px;
      margin-bottom: 26px;
    }}
    @media (max-width: 980px) {{
      .gallery-grid {{ grid-template-columns: repeat(2, 1fr); }}
    }}
    .gallery-card {{
      background: var(--stone-card);
      border: 2px solid var(--border-stone);
      border-radius: 12px;
      overflow: hidden;
      cursor: pointer;
      transition: all 0.18s ease;
      position: relative;
    }}
    .gallery-card:hover {{
      transform: translateY(-2px);
      border-color: #B0B0B0;
      box-shadow: 0 8px 20px rgba(0,0,0,0.06);
    }}
    .gallery-card.active {{
      border-color: var(--redfin-red);
      box-shadow: 0 8px 22px rgba(200, 32, 33, 0.15);
    }}
    .gallery-svg-wrap {{
      width: 100%;
      height: 152px;
      background: #EAECEF;
      display: block;
      position: relative;
    }}
    .gallery-time-badge {{
      position: absolute;
      top: 10px;
      left: 10px;
      background: rgba(255, 255, 255, 0.94);
      color: var(--text-main);
      font-size: 11px;
      font-weight: 800;
      padding: 3px 8px;
      border-radius: 6px;
      border: 1px solid var(--border-stone);
    }}
    .gallery-room-tag {{
      position: absolute;
      bottom: 10px;
      right: 10px;
      background: var(--redfin-red);
      color: #FFFFFF;
      font-size: 10.5px;
      font-weight: 700;
      padding: 3px 8px;
      border-radius: 6px;
    }}
    .gallery-meta {{
      padding: 11px 13px;
      background: #FFFFFF;
    }}
    .gallery-meta-title {{
      font-size: 13.5px;
      font-weight: 700;
      color: var(--text-main);
    }}
    .gallery-meta-sub {{
      font-size: 11.5px;
      color: var(--text-muted);
      margin-top: 2px;
    }}

    /* Workspace Split: Left = Interactive Pricing & 4-Scene Storyboard, Right = Live 9:16 Social Reel Player */
    .studio-grid {{
      display: grid;
      grid-template-columns: 1.55fr 1fr;
      gap: 24px;
      align-items: start;
    }}
    @media (max-width: 1080px) {{
      .studio-grid {{ grid-template-columns: 1fr; }}
    }}

    .stone-panel {{
      background: var(--stone-card);
      border: 1px solid var(--border-stone);
      border-radius: 14px;
      padding: 20px 22px;
      margin-bottom: 20px;
    }}
    .panel-header {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 16px;
      flex-wrap: wrap;
      gap: 10px;
    }}
    .panel-title {{
      font-size: 17px;
      font-weight: 800;
      color: var(--text-main);
      display: flex;
      align-items: center;
      gap: 8px;
    }}
    .panel-subtitle {{
      font-size: 12.5px;
      color: var(--text-muted);
      margin-top: 2px;
    }}

    /* Interactive Listing Price & Rate Sliders */
    .sliders-grid {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 16px;
      background: #FFFFFF;
      border: 1px solid var(--border-stone);
      border-radius: 10px;
      padding: 16px;
    }}
    @media (max-width: 760px) {{
      .sliders-grid {{ grid-template-columns: 1fr; }}
    }}
    .slider-box label {{
      display: flex;
      justify-content: space-between;
      font-size: 12px;
      font-weight: 700;
      color: var(--text-muted);
      margin-bottom: 8px;
    }}
    .slider-val-highlight {{
      color: var(--redfin-red);
      font-weight: 800;
      font-size: 13.5px;
    }}
    input[type="range"] {{
      width: 100%;
      accent-color: var(--redfin-red);
      cursor: pointer;
    }}
    .payment-breakdown-strip {{
      margin-top: 14px;
      background: #FFFFFF;
      border: 1px solid var(--border-stone);
      border-left: 4px solid var(--redfin-red);
      border-radius: 8px;
      padding: 12px 16px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 12px;
    }}
    .payment-pill-group {{
      display: flex;
      align-items: center;
      gap: 18px;
      flex-wrap: wrap;
      font-size: 12.5px;
      color: var(--text-muted);
    }}
    .payment-pill-group strong {{
      color: var(--text-main);
      font-weight: 800;
    }}

    /* 4-Scene Social Reel Storyboard Cards */
    .storyboard-list {{
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 14px;
    }}
    @media (max-width: 720px) {{
      .storyboard-list {{ grid-template-columns: 1fr; }}
    }}
    .scene-card {{
      background: #FFFFFF;
      border: 2px solid var(--border-stone);
      border-radius: 12px;
      padding: 15px;
      cursor: pointer;
      transition: all 0.16s ease;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      gap: 10px;
    }}
    .scene-card:hover {{
      border-color: #B5B5B5;
    }}
    .scene-card.active {{
      border-color: var(--redfin-red);
      background: #FFFDFD;
      box-shadow: 0 6px 18px rgba(200, 32, 33, 0.08);
    }}
    .scene-top {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 8px;
    }}
    .scene-time-pill {{
      background: var(--redfin-red);
      color: #FFFFFF;
      font-size: 11px;
      font-weight: 800;
      padding: 3px 9px;
      border-radius: 6px;
    }}
    .scene-camera-tag {{
      font-size: 11px;
      font-weight: 700;
      color: var(--text-muted);
      background: var(--stone-card);
      padding: 3px 8px;
      border-radius: 6px;
      border: 1px solid var(--border-stone);
    }}
    .scene-heading {{
      font-size: 15px;
      font-weight: 800;
      color: var(--text-main);
    }}
    .scene-caption-input {{
      width: 100%;
      border: 1px solid #DCDCDC;
      border-radius: 7px;
      padding: 7px 10px;
      font-family: inherit;
      font-size: 12.5px;
      font-weight: 600;
      color: var(--text-main);
      background: var(--stone-card);
    }}
    .scene-caption-input:focus {{
      outline: none;
      border-color: var(--redfin-red);
      background: #FFFFFF;
    }}
    .scene-narration {{
      font-size: 12px;
      color: var(--text-muted);
      background: #F9FAFB;
      padding: 8px 10px;
      border-radius: 7px;
      border-left: 3px solid #CBD5E1;
    }}

    /* Voiceover Script & Gemini 3.8 Live Audio Bar */
    .voiceover-card {{
      background: #FFFFFF;
      border: 1px solid var(--border-stone);
      border-radius: 12px;
      padding: 16px 18px;
      margin-top: 16px;
    }}
    .voiceover-header {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      margin-bottom: 10px;
      flex-wrap: wrap;
    }}
    .voiceover-script-box {{
      width: 100%;
      border: 1px solid var(--border-stone);
      border-radius: 8px;
      padding: 11px 13px;
      font-family: inherit;
      font-size: 13.5px;
      line-height: 1.55;
      color: var(--text-main);
      background: var(--stone-card);
      resize: vertical;
    }}

    /* Right Column: 9:16 Social Reel Preview Studio */
    .reel-preview-panel {{
      background: var(--stone-card);
      border: 1px solid var(--border-stone);
      border-radius: 14px;
      padding: 20px;
      position: sticky;
      top: 76px;
    }}
    .phone-frame {{
      width: 100%;
      max-width: 340px;
      margin: 0 auto;
      background: #FFFFFF;
      border: 8px solid #262626;
      border-radius: 32px;
      overflow: hidden;
      box-shadow: 0 16px 36px rgba(0,0,0,0.12);
      position: relative;
      aspect-ratio: 9 / 15.5;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
    }}
    .reel-canvas-bg {{
      position: absolute;
      inset: 0;
      z-index: 1;
      background: #F3F4F6;
      display: flex;
      flex-direction: column;
    }}
    .reel-top-overlay {{
      position: relative;
      z-index: 3;
      padding: 14px 14px 8px;
      background: linear-gradient(180deg, rgba(0,0,0,0.55) 0%, transparent 100%);
      color: #FFFFFF;
    }}
    .reel-progress-segments {{
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 4px;
      margin-bottom: 10px;
    }}
    .reel-seg {{
      height: 3.5px;
      border-radius: 99px;
      background: rgba(255,255,255,0.35);
      overflow: hidden;
    }}
    .reel-seg-fill {{
      height: 100%;
      width: 0%;
      background: #FFFFFF;
      transition: width 0.25s ease;
    }}
    .reel-seg.active .reel-seg-fill {{
      width: 100%;
      background: var(--redfin-red);
    }}
    .reel-brand-row {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      font-size: 11.5px;
      font-weight: 700;
    }}
    .reel-bottom-overlay {{
      position: relative;
      z-index: 3;
      padding: 16px 14px;
      background: linear-gradient(0deg, rgba(0,0,0,0.78) 0%, rgba(0,0,0,0.35) 75%, transparent 100%);
      color: #FFFFFF;
    }}
    .reel-scene-badge {{
      display: inline-block;
      background: var(--redfin-red);
      color: #FFFFFF;
      font-size: 10.5px;
      font-weight: 800;
      padding: 3px 9px;
      border-radius: 5px;
      margin-bottom: 7px;
    }}
    .reel-caption-box {{
      font-size: 15px;
      font-weight: 800;
      line-height: 1.3;
      margin-bottom: 8px;
      text-shadow: 0 1px 3px rgba(0,0,0,0.5);
    }}
    .reel-mortgage-card {{
      background: rgba(255, 255, 255, 0.96);
      color: var(--text-main);
      border-radius: 10px;
      padding: 10px 12px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      box-shadow: 0 4px 12px rgba(0,0,0,0.18);
    }}
    .reel-mortgage-price {{
      font-size: 16px;
      font-weight: 800;
      color: var(--redfin-red);
    }}
    .reel-controls-bar {{
      margin-top: 14px;
      display: flex;
      gap: 8px;
      justify-content: center;
      flex-wrap: wrap;
    }}

    /* AI Synthesis Output Card */
    .ai-output-card {{
      margin-top: 18px;
      background: #FFFFFF;
      border: 1px solid var(--border-stone);
      border-top: 3px solid var(--redfin-red);
      border-radius: 12px;
      padding: 16px 18px;
      font-size: 13px;
      color: var(--text-main);
      white-space: pre-wrap;
      line-height: 1.6;
    }}
  </style>
</head>
<body>

  <!-- Authentic Redfin Header -->
  <header class="redfin-header">
    <div class="redfin-header-inner">
      <div class="brand-cluster">
        <div class="redfin-logo">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
            <path d="M3 10.5L12 3l9 7.5V21a1 1 0 0 1-1 1h-5v-6H9v6H4a1 1 0 0 1-1-1v-10.5z"/>
          </svg>
          REDFIN
        </div>
        <div class="co-brand-tag">
          <span>Listing-to-Video Studio</span>
          <span class="co-brand-pill">Rocket Mortgage Instant Reel</span>
        </div>
      </div>

      <div class="search-bar-mock">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#767676" stroke-width="2.2">
          <circle cx="11" cy="11" r="8"/><path d="M21 21l-4.3-4.3"/>
        </svg>
        <select id="listing-selector" onchange="window.switchRedfinListing(this.value)" aria-label="Select MLS Property">
          <option value="elmhurst" selected>418 Elmhurst Ave, Royal Oak, MI 48067 · $460,000 (MLS #202604189)</option>
          <option value="maplewood">912 W Maplehurst St, Ferndale, MI 48220 · $389,000 (MLS #202604412)</option>
          <option value="linden">1420 Linden Rd, Birmingham, MI 48009 · $675,000 (MLS #202604805)</option>
        </select>
      </div>

      <div class="header-actions">
        <div class="model-select-box">
          <span>AI Engine:</span>
          <select id="app-model-select" onchange="window.syncSelectedModel(this.value)">
            <option value="gemini-4-argon">Gemini 4 Argon (Frontier)</option>
            <option value="gemini-3.8-flash">Gemini 3.8 Flash (Fast)</option>
          </select>
        </div>
        <button class="btn-redfin" onclick="window.runLiveVertexAI()">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.3">
            <polygon points="5 3 19 12 5 21 5 3"/>
          </svg>
          Generate Reel Script & Veo Prompts
        </button>
      </div>
    </div>
  </header>

  <main class="page-container">
    <!-- Breadcrumb -->
    <div class="breadcrumb-row">
      <div>Michigan &rsaquo; Oakland County &rsaquo; Royal Oak &rsaquo; 48067 &rsaquo; <strong id="crumb-address">418 Elmhurst Ave</strong></div>
      <div style="display:flex;align-items:center;gap:10px;">
        <span class="status-pill"><span class="status-dot"></span> Active Redfin Premier Listing · Listed 2 Hours Ago</span>
        <span style="font-weight:700;color:var(--redfin-red);">Redfin Estimate: <span id="redfin-est-val">$464,500</span></span>
      </div>
    </div>

    <!-- Listing Key Facts Header -->
    <section class="listing-hero-header">
      <div class="address-block">
        <h1 id="prop-street">418 Elmhurst Ave</h1>
        <div class="address-sub" id="prop-city-zip">Royal Oak, MI 48067 · Vinsetta Park Historic District</div>
      </div>

      <div class="key-stats-row">
        <div class="stat-item">
          <span class="stat-val" id="header-price-val">$460,000</span>
          <span class="stat-lbl">List Price</span>
        </div>
        <div class="stat-item">
          <span class="stat-val" id="header-beds-val">4</span>
          <span class="stat-lbl">Beds</span>
        </div>
        <div class="stat-item">
          <span class="stat-val" id="header-baths-val">2.5</span>
          <span class="stat-lbl">Baths</span>
        </div>
        <div class="stat-item">
          <span class="stat-val" id="header-sqft-val">2,280</span>
          <span class="stat-lbl">Sq. Ft. ($202/sq.ft.)</span>
        </div>
        <div class="stat-item">
          <span class="stat-val red" id="header-pmt-val">$2,884/mo</span>
          <span class="stat-lbl">Est. Rocket Mortgage Payment</span>
        </div>
      </div>
    </section>

    <!-- 4 Architectural Listing Photo Gallery Cards -->
    <div class="gallery-section-title">
      <div style="font-size:14px;font-weight:800;color:var(--text-main);">
        MLS High-Resolution Architectural Photos (Click any photo to preview Scene in Reel Storyboard)
      </div>
      <div style="font-size:12px;color:var(--text-muted);font-weight:600;">
        4 Curated Keyframes &rarr; 15-Second Vertical Social Reel (9:16)
      </div>
    </div>

    <section class="gallery-grid">
      <!-- Scene 0: 00:00 Curb Appeal -->
      <div class="gallery-card active" id="gal-card-0" onclick="window.selectStoryboardScene(0)">
        <div class="gallery-svg-wrap">
          <span class="gallery-time-badge">Scene 1 · 00:00–00:04</span>
          <span class="gallery-room-tag">00:00 Curb Appeal</span>
          <svg viewBox="0 0 400 220" width="100%" height="100%" preserveAspectRatio="xMidYMid slice">
            <rect width="400" height="220" fill="#DBEAFE"/>
            <rect y="168" width="400" height="52" fill="#86EFAC"/>
            <path d="M175 168 L225 168 L245 220 L155 220 Z" fill="#CBD5E1"/>
            <!-- Craftsman Bungalow House -->
            <polygon points="75,95 200,32 325,95" fill="#7C2D12"/>
            <rect x="95" y="95" width="210" height="75" fill="#F8FAFC" stroke="#94A3B8" stroke-width="2"/>
            <!-- Brick Wainscoting -->
            <rect x="95" y="140" width="210" height="30" fill="#B91C1C" opacity="0.82"/>
            <!-- Gables & Dormer -->
            <polygon points="160,68 200,44 240,68" fill="#FEF3C7" stroke="#7C2D12" stroke-width="2"/>
            <!-- Front Porch Columns -->
            <rect x="112" y="102" width="10" height="66" fill="#FFFFFF"/>
            <rect x="278" y="102" width="10" height="66" fill="#FFFFFF"/>
            <!-- Warm Lit Windows -->
            <rect x="128" y="106" width="38" height="28" rx="2" fill="#FDE68A" stroke="#475569" stroke-width="2"/>
            <rect x="234" y="106" width="38" height="28" rx="2" fill="#FDE68A" stroke="#475569" stroke-width="2"/>
            <!-- Redfin Sign -->
            <rect x="52" y="132" width="6" height="44" fill="#FFFFFF"/>
            <rect x="34" y="138" width="36" height="22" rx="3" fill="#C82021"/>
            <!-- Trees -->
            <circle cx="42" cy="115" r="28" fill="#16A34A"/>
            <circle cx="358" cy="112" r="32" fill="#15803D"/>
          </svg>
        </div>
        <div class="gallery-meta">
          <div class="gallery-meta-title">00:00 Curb Appeal · Craftsman Porch</div>
          <div class="gallery-meta-sub">Brick front porch, mature Royal Oak oaks &amp; sunlit lawn</div>
        </div>
      </div>

      <!-- Scene 1: 00:04 Chef's Kitchen -->
      <div class="gallery-card" id="gal-card-1" onclick="window.selectStoryboardScene(1)">
        <div class="gallery-svg-wrap">
          <span class="gallery-time-badge">Scene 2 · 00:04–00:09</span>
          <span class="gallery-room-tag">00:04 Chef's Kitchen</span>
          <svg viewBox="0 0 400 220" width="100%" height="100%" preserveAspectRatio="xMidYMid slice">
            <rect width="400" height="220" fill="#FAF5FF"/>
            <rect width="400" height="165" fill="#F8FAFC"/>
            <rect y="165" width="400" height="55" fill="#D6D3D1"/>
            <!-- Shaker Cabinets -->
            <rect x="30" y="25" width="140" height="70" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="2"/>
            <rect x="230" y="25" width="140" height="70" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="2"/>
            <!-- Range Hood -->
            <polygon points="180,20 220,20 235,75 165,75" fill="#94A3B8"/>
            <!-- Waterfall Quartz Island -->
            <rect x="75" y="122" width="250" height="56" rx="4" fill="#1E293B"/>
            <rect x="70" y="114" width="260" height="12" rx="3" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="2"/>
            <!-- Brass Pendant Lights -->
            <line x1="140" y1="0" x2="140" y2="52" stroke="#B45309" stroke-width="2"/>
            <circle cx="140" cy="58" r="10" fill="#FDE68A" stroke="#B45309" stroke-width="2"/>
            <line x1="260" y1="0" x2="260" y2="52" stroke="#B45309" stroke-width="2"/>
            <circle cx="260" cy="58" r="10" fill="#FDE68A" stroke="#B45309" stroke-width="2"/>
          </svg>
        </div>
        <div class="gallery-meta">
          <div class="gallery-meta-title">00:04 Chef's Kitchen · Quartz Island</div>
          <div class="gallery-meta-sub">10-ft waterfall Calacatta quartz island &amp; 36" Wolf range</div>
        </div>
      </div>

      <!-- Scene 2: 00:09 Backyard Pergola -->
      <div class="gallery-card" id="gal-card-2" onclick="window.selectStoryboardScene(2)">
        <div class="gallery-svg-wrap">
          <span class="gallery-time-badge">Scene 3 · 00:09–00:13</span>
          <span class="gallery-room-tag">00:09 Backyard Pergola</span>
          <svg viewBox="0 0 400 220" width="100%" height="100%" preserveAspectRatio="xMidYMid slice">
            <rect width="400" height="145" fill="#FEF3C7"/>
            <rect y="145" width="400" height="75" fill="#86EFAC"/>
            <!-- Bluestone Patio -->
            <rect x="55" y="150" width="290" height="48" rx="4" fill="#94A3B8"/>
            <!-- Cedar Pergola Frame -->
            <rect x="75" y="48" width="12" height="110" fill="#9A3412"/>
            <rect x="313" y="48" width="12" height="110" fill="#9A3412"/>
            <rect x="60" y="42" width="280" height="12" fill="#B45309"/>
            <!-- Bistro String Lights -->
            <circle cx="115" cy="62" r="5" fill="#FDE047"/>
            <circle cx="165" cy="66" r="5" fill="#FDE047"/>
            <circle cx="215" cy="66" r="5" fill="#FDE047"/>
            <circle cx="265" cy="62" r="5" fill="#FDE047"/>
            <!-- Firepit & Lounge -->
            <ellipse cx="200" cy="168" rx="34" ry="12" fill="#475569"/>
            <polygon points="190,165 200,142 210,165" fill="#F97316"/>
          </svg>
        </div>
        <div class="gallery-meta">
          <div class="gallery-meta-title">00:09 Backyard Pergola · Patio Oasis</div>
          <div class="gallery-meta-sub">Custom cedar pergola, bistro lights &amp; fenced firepit yard</div>
        </div>
      </div>

      <!-- Scene 3: 00:13 Rocket Mortgage Payment Breakdown -->
      <div class="gallery-card" id="gal-card-3" onclick="window.selectStoryboardScene(3)">
        <div class="gallery-svg-wrap">
          <span class="gallery-time-badge">Scene 4 · 00:13–00:15</span>
          <span class="gallery-room-tag">00:13 Payment Card</span>
          <svg viewBox="0 0 400 220" width="100%" height="100%" preserveAspectRatio="xMidYMid slice">
            <rect width="400" height="220" fill="#FDF2F2"/>
            <rect x="36" y="34" width="328" height="156" rx="14" fill="#FFFFFF" stroke="#C82021" stroke-width="2.5"/>
            <rect x="56" y="52" width="140" height="20" rx="5" fill="#C82021"/>
            <text x="65" y="66" fill="#FFFFFF" font-family="sans-serif" font-size="11" font-weight="bold">ROCKET MORTGAGE</text>
            <text x="56" y="104" fill="#1E293B" font-family="sans-serif" font-size="24" font-weight="bold" id="svg-card-pmt">$2,884 / mo</text>
            <text x="56" y="128" fill="#595959" font-family="sans-serif" font-size="12" font-weight="600">30-Yr Fixed · 6.125% APR · 10% Down</text>
            <rect x="56" y="146" width="288" height="26" rx="6" fill="#DCFCE7"/>
            <text x="70" y="163" fill="#15803D" font-family="sans-serif" font-size="11.5" font-weight="bold">Redfin + Rocket Preferred Closing Credit: -$2,500</text>
          </svg>
        </div>
        <div class="gallery-meta">
          <div class="gallery-meta-title">00:13 Rocket Mortgage Payment Breakdown</div>
          <div class="gallery-meta-sub">Live P&amp;I + taxes end-card with 1-tap pre-approval CTA</div>
        </div>
      </div>
    </section>

    <!-- Main Studio Grid -->
    <div class="studio-grid">
      <!-- Left Column: Interactive Pricing Sliders + 4-Scene Storyboard Editor -->
      <div>
        <!-- Interactive Listing Price & Rate Sliders -->
        <div class="stone-panel">
          <div class="panel-header">
            <div>
              <div class="panel-title">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#C82021" stroke-width="2.2">
                  <line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>
                </svg>
                Interactive Listing Price &amp; Rocket Mortgage Rate Calculator
              </div>
              <div class="panel-subtitle">
                Adjust list price, interest rate, or down payment to dynamically update Scene 4 (`00:13`) and the voiceover script.
              </div>
            </div>
            <span class="co-brand-pill">Live Payment Sync</span>
          </div>

          <div class="sliders-grid">
            <div class="slider-box">
              <label>
                <span>Listing Price</span>
                <span class="slider-val-highlight" id="price-slider-label">$460,000</span>
              </label>
              <input type="range" id="price-slider" min="320000" max="750000" step="5000" value="460000" oninput="window.recalculateReelPayment()">
              <div style="display:flex;justify-content:space-between;font-size:11px;color:var(--text-subtle);margin-top:4px;">
                <span>$320K</span><span>$460K List</span><span>$750K</span>
              </div>
            </div>

            <div class="slider-box">
              <label>
                <span>30-Yr Interest Rate</span>
                <span class="slider-val-highlight" id="rate-slider-label">6.125%</span>
              </label>
              <input type="range" id="rate-slider" min="4.75" max="7.50" step="0.125" value="6.125" oninput="window.recalculateReelPayment()">
              <div style="display:flex;justify-content:space-between;font-size:11px;color:var(--text-subtle);margin-top:4px;">
                <span>4.75%</span><span>6.125%</span><span>7.50%</span>
              </div>
            </div>

            <div class="slider-box">
              <label>
                <span>Down Payment</span>
                <span class="slider-val-highlight" id="down-slider-label">10% ($46,000)</span>
              </label>
              <input type="range" id="down-slider" min="3.5" max="25" step="0.5" value="10" oninput="window.recalculateReelPayment()">
              <div style="display:flex;justify-content:space-between;font-size:11px;color:var(--text-subtle);margin-top:4px;">
                <span>3.5% FHA</span><span>10%</span><span>25%</span>
              </div>
            </div>
          </div>

          <div class="payment-breakdown-strip">
            <div class="payment-pill-group">
              <span>Principal &amp; Interest: <strong id="pi-dollar-val">$2,516/mo</strong></span>
              <span>Prop. Taxes &amp; Home Ins: <strong id="tax-dollar-val">$368/mo</strong></span>
              <span>Loan Amount: <strong id="loan-dollar-val">$414,000</strong></span>
            </div>
            <div style="font-size:15px;font-weight:800;color:var(--redfin-red);">
              Total Reel End-Card Payment: <span id="total-pmt-inline">$2,884/mo</span>
            </div>
          </div>
        </div>

        <!-- 4-Scene Social Reel Storyboard Creator -->
        <div class="stone-panel">
          <div class="panel-header">
            <div>
              <div class="panel-title">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#C82021" stroke-width="2.2">
                  <rect x="2" y="2" width="20" height="20" rx="2.18" ry="2.18"/><line x1="7" y1="2" x2="7" y2="22"/><line x1="17" y1="2" x2="17" y2="22"/><line x1="2" y1="12" x2="22" y2="12"/>
                </svg>
                4-Scene Social Reel Storyboard Creator (15-Second Vertical Video)
              </div>
              <div class="panel-subtitle">
                Click any scene card to preview on the 9:16 canvas or customize the on-screen hook caption.
              </div>
            </div>
          </div>

          <div class="storyboard-list">
            <!-- Storyboard Card 0 -->
            <div class="scene-card active" id="scene-card-0" onclick="window.selectStoryboardScene(0)">
              <div class="scene-top">
                <span class="scene-time-pill">00:00 Curb Appeal</span>
                <span class="scene-camera-tag">Veo 3.1 · Gimbal Push-In</span>
              </div>
              <div class="scene-heading">Scene 1: Vinsetta Park Craftsman Exterior</div>
              <input type="text" class="scene-caption-input" id="caption-input-0" value="Just Listed in Royal Oak · 418 Elmhurst Ave ($460,000)" oninput="window.updateSceneCaption(0, this.value)" onclick="event.stopPropagation()">
              <div class="scene-narration" id="narration-0">
                "Just listed in Royal Oak's coveted Vinsetta Park—welcome to 418 Elmhurst Avenue, a sunlit 4-bedroom Craftsman at $460,000."
              </div>
            </div>

            <!-- Storyboard Card 1 -->
            <div class="scene-card" id="scene-card-1" onclick="window.selectStoryboardScene(1)">
              <div class="scene-top">
                <span class="scene-time-pill">00:04 Chef's Kitchen</span>
                <span class="scene-camera-tag">Veo 3.1 · Smooth Orbit Pan</span>
              </div>
              <div class="scene-heading">Scene 2: 10-Ft Calacatta Quartz Island</div>
              <input type="text" class="scene-caption-input" id="caption-input-1" value="Chef's Waterfall Quartz Island + 36&quot; Pro Range" oninput="window.updateSceneCaption(1, this.value)" onclick="event.stopPropagation()">
              <div class="scene-narration" id="narration-1">
                "Step inside to 2,280 square feet featuring a ten-foot waterfall quartz island, custom white shaker cabinetry, and brass pendants."
              </div>
            </div>

            <!-- Storyboard Card 2 -->
            <div class="scene-card" id="scene-card-2" onclick="window.selectStoryboardScene(2)">
              <div class="scene-top">
                <span class="scene-time-pill">00:09 Backyard Pergola</span>
                <span class="scene-camera-tag">Veo 3.1 · Golden Hour Crane</span>
              </div>
              <div class="scene-heading">Scene 3: Cedar Pergola &amp; Bluestone Patio</div>
              <input type="text" class="scene-caption-input" id="caption-input-2" value="Private Cedar Pergola, Bistro Lights &amp; Firepit" oninput="window.updateSceneCaption(2, this.value)" onclick="event.stopPropagation()">
              <div class="scene-narration" id="narration-2">
                "French doors open to your private backyard retreat with a custom cedar pergola, bluestone patio, and built-in firepit."
              </div>
            </div>

            <!-- Storyboard Card 3 -->
            <div class="scene-card" id="scene-card-3" onclick="window.selectStoryboardScene(3)">
              <div class="scene-top">
                <span class="scene-time-pill">00:13 Rocket Mortgage Payment Breakdown</span>
                <span class="scene-camera-tag">Dynamic Rate Graphics</span>
              </div>
              <div class="scene-heading">Scene 4: Instant Monthly Payment End-Card</div>
              <input type="text" class="scene-caption-input" id="caption-input-3" value="Own for $2,884/mo · 6.125% Rate · $2,500 Redfin Credit" oninput="window.updateSceneCaption(3, this.value)" onclick="event.stopPropagation()">
              <div class="scene-narration" id="narration-3">
                "Lock in an estimated $2,884 per month at 6.125% with Rocket Mortgage, plus a $2,500 Redfin closing credit."
              </div>
            </div>
          </div>

          <!-- Voiceover Script & Gemini 3.8 Live 24kHz HD Audio Trigger -->
          <div class="voiceover-card">
            <div class="voiceover-header">
              <div>
                <div style="font-size:14px;font-weight:800;color:var(--text-main);">
                  15-Second Property Video Voiceover Script (Synced to Price &amp; Rate Sliders)
                </div>
                <div style="font-size:12px;color:var(--text-muted);">
                  Synthesized via Gemini 3.8 Live 24kHz Native HD Audio (Voice: Aoede HD)
                </div>
              </div>
              <button class="btn-redfin" id="btn-play-voiceover" onclick="window.playReelVoiceover(this)">
                🔊 Play Reel Voiceover (Gemini 3.8 Live · Aoede HD)
              </button>
            </div>
            <textarea id="voiceover-script-textarea" class="voiceover-script-box" rows="3">Just listed in Royal Oak's Vinsetta Park! Welcome to 418 Elmhurst Avenue—a 4-bedroom, 2.5-bath Craftsman listed at $460,000. Inside its 2,280 square feet, enjoy a chef's waterfall quartz kitchen and a private backyard cedar pergola. Own this home for an estimated $2,884 a month at 6.125% with Rocket Mortgage, including a $2,500 Redfin closing credit!</textarea>
          </div>

          <!-- Live Vertex AI Output Box -->
          <div class="ai-output-card" id="vertex-ai-output">
            <strong>Redfin + Rocket Mortgage Video Director Ready:</strong> Click <em>"Generate Reel Script &amp; Veo Prompts"</em> in the top header or <em>"Re-Synthesize with Selected Model"</em> in the drawer to generate localized Instagram/TikTok ad hooks and Veo 3.1 scene motion prompts with <span id="live-model-pill">gemini-4-argon</span>.
          </div>
        </div>
      </div>

      <!-- Right Column: Live 9:16 Social Reel Preview Player -->
      <aside class="reel-preview-panel">
        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px;">
          <div>
            <div style="font-size:15px;font-weight:800;color:var(--text-main);">Live 9:16 Social Reel Preview</div>
            <div style="font-size:12px;color:var(--text-muted);">Instagram Reels · TikTok · YouTube Shorts</div>
          </div>
          <span class="co-brand-pill" id="active-scene-indicator">00:00 Curb Appeal</span>
        </div>

        <div class="phone-frame">
          <!-- Dynamic Scene Illustration Inside Phone -->
          <div class="reel-canvas-bg" id="phone-svg-stage"></div>

          <!-- Top Overlay -->
          <div class="reel-top-overlay">
            <div class="reel-progress-segments">
              <div class="reel-seg active" id="reel-seg-0"><div class="reel-seg-fill"></div></div>
              <div class="reel-seg" id="reel-seg-1"><div class="reel-seg-fill"></div></div>
              <div class="reel-seg" id="reel-seg-2"><div class="reel-seg-fill"></div></div>
              <div class="reel-seg" id="reel-seg-3"><div class="reel-seg-fill"></div></div>
            </div>
            <div class="reel-brand-row">
              <span>@RedfinDetroit &times; @RocketMortgage</span>
              <span style="background:rgba(0,0,0,0.45);padding:2px 7px;border-radius:4px;">MLS #202604189</span>
            </div>
          </div>

          <!-- Bottom Overlay -->
          <div class="reel-bottom-overlay">
            <span class="reel-scene-badge" id="phone-scene-badge">00:00 Curb Appeal</span>
            <div class="reel-caption-box" id="phone-caption-text">
              Just Listed in Royal Oak · 418 Elmhurst Ave ($460,000)
            </div>
            <div class="reel-mortgage-card">
              <div>
                <div style="font-size:10.5px;font-weight:700;color:var(--text-muted);text-transform:uppercase;">Rocket Mortgage Est.</div>
                <div class="reel-mortgage-price" id="phone-pmt-val">$2,884/mo</div>
                <div style="font-size:10.5px;color:var(--text-muted);" id="phone-rate-sub">6.125% Rate · 10% Down</div>
              </div>
              <div style="background:var(--redfin-red);color:#FFFFFF;font-size:11px;font-weight:800;padding:7px 11px;border-radius:7px;">
                Get Pre-Approved
              </div>
            </div>
          </div>
        </div>

        <div class="reel-controls-bar">
          <button class="btn-outline" onclick="window.stepReelScene(-1)">&larr; Prev Scene</button>
          <button class="btn-redfin" onclick="window.autoPlayStoryboardTour()">&#9654; Play 4-Scene Tour</button>
          <button class="btn-outline" onclick="window.stepReelScene(1)">Next Scene &rarr;</button>
        </div>
      </aside>
    </div>
  </main>

  <script>
    const LISTINGS_DB = {{
      elmhurst: {{
        street: "418 Elmhurst Ave",
        cityZip: "Royal Oak, MI 48067 · Vinsetta Park Historic District",
        price: 460000,
        est: "$464,500",
        beds: "4",
        baths: "2.5",
        sqft: "2,280",
        rate: 6.125,
        downPct: 10
      }},
      maplewood: {{
        street: "912 W Maplehurst St",
        cityZip: "Ferndale, MI 48220 · Drayton Avenue Walkable District",
        price: 389000,
        est: "$394,000",
        beds: "3",
        baths: "2.0",
        sqft: "1,740",
        rate: 6.000,
        downPct: 10
      }},
      linden: {{
        street: "1420 Linden Rd",
        cityZip: "Birmingham, MI 48009 · Quarton Lake Estates",
        price: 675000,
        est: "$682,000",
        beds: "4",
        baths: "3.5",
        sqft: "3,120",
        rate: 6.125,
        downPct: 15
      }}
    }};

    let currentSceneIndex = 0;
    let tourTimer = null;

    const SCENE_TIMESTAMPS = [
      "00:00 Curb Appeal",
      "00:04 Chef's Kitchen",
      "00:09 Backyard Pergola",
      "00:13 Rocket Mortgage Payment Breakdown"
    ];

    window.selectStoryboardScene = function(idx) {{
      currentSceneIndex = idx;
      for (let i = 0; i < 4; i++) {{
        const gal = document.getElementById('gal-card-' + i);
        const sc = document.getElementById('scene-card-' + i);
        const seg = document.getElementById('reel-seg-' + i);
        if (gal) gal.classList.toggle('active', i === idx);
        if (sc) sc.classList.toggle('active', i === idx);
        if (seg) seg.classList.toggle('active', i <= idx);
      }}
      const badge = document.getElementById('phone-scene-badge');
      const topInd = document.getElementById('active-scene-indicator');
      if (badge) badge.textContent = SCENE_TIMESTAMPS[idx];
      if (topInd) topInd.textContent = SCENE_TIMESTAMPS[idx];

      const capInput = document.getElementById('caption-input-' + idx);
      const phoneCap = document.getElementById('phone-caption-text');
      if (capInput && phoneCap) {{
        phoneCap.textContent = capInput.value;
      }}

      const sourceGalSvg = document.querySelector('#gal-card-' + idx + ' svg');
      const phoneStage = document.getElementById('phone-svg-stage');
      if (sourceGalSvg && phoneStage) {{
        phoneStage.innerHTML = sourceGalSvg.outerHTML;
        const svgEl = phoneStage.querySelector('svg');
        if (svgEl) {{
          svgEl.setAttribute('width', '100%');
          svgEl.setAttribute('height', '100%');
          svgEl.setAttribute('preserveAspectRatio', 'xMidYMid slice');
        }}
      }}
    }};

    window.updateSceneCaption = function(idx, val) {{
      if (idx === currentSceneIndex) {{
        const phoneCap = document.getElementById('phone-caption-text');
        if (phoneCap) phoneCap.textContent = val;
      }}
    }};

    window.stepReelScene = function(delta) {{
      const next = (currentSceneIndex + delta + 4) % 4;
      window.selectStoryboardScene(next);
    }};

    window.autoPlayStoryboardTour = function() {{
      if (tourTimer) {{
        clearInterval(tourTimer);
        tourTimer = null;
      }}
      window.selectStoryboardScene(0);
      let step = 0;
      tourTimer = setInterval(() => {{
        step++;
        if (step >= 4) {{
          clearInterval(tourTimer);
          tourTimer = null;
          return;
        }}
        window.selectStoryboardScene(step);
      }}, 1800);
    }};

    window.recalculateReelPayment = function() {{
      const price = parseFloat(document.getElementById('price-slider').value || 460000);
      const rate = parseFloat(document.getElementById('rate-slider').value || 6.125);
      const downPct = parseFloat(document.getElementById('down-slider').value || 10);

      const downDollar = Math.round(price * (downPct / 100));
      const loanAmount = price - downDollar;
      const monthlyRate = (rate / 100) / 12;
      const n = 360;
      const pi = Math.round(loanAmount * (monthlyRate * Math.pow(1 + monthlyRate, n)) / (Math.pow(1 + monthlyRate, n) - 1));
      const taxesIns = Math.round((price * 0.0096) / 12);
      const totalPmt = pi + taxesIns;

      const fmtPrice = '$' + price.toLocaleString();
      const fmtPmt = '$' + totalPmt.toLocaleString() + '/mo';

      document.getElementById('price-slider-label').textContent = fmtPrice;
      document.getElementById('rate-slider-label').textContent = rate.toFixed(3).replace(/\\.?0+$/, '') + '%';
      document.getElementById('down-slider-label').textContent = downPct + '% ($' + downDollar.toLocaleString() + ')';

      document.getElementById('header-price-val').textContent = fmtPrice;
      document.getElementById('header-pmt-val').textContent = fmtPmt;
      document.getElementById('pi-dollar-val').textContent = '$' + pi.toLocaleString() + '/mo';
      document.getElementById('tax-dollar-val').textContent = '$' + taxesIns.toLocaleString() + '/mo';
      document.getElementById('loan-dollar-val').textContent = '$' + loanAmount.toLocaleString();
      document.getElementById('total-pmt-inline').textContent = fmtPmt;

      document.getElementById('phone-pmt-val').textContent = fmtPmt;
      document.getElementById('phone-rate-sub').textContent = rate.toFixed(3).replace(/\\.?0+$/, '') + '% Rate · ' + downPct + '% Down';

      const svgCardPmt = document.getElementById('svg-card-pmt');
      if (svgCardPmt) svgCardPmt.textContent = '$' + totalPmt.toLocaleString() + ' / mo';

      const street = document.getElementById('prop-street').textContent;
      const beds = document.getElementById('header-beds-val').textContent;
      const baths = document.getElementById('header-baths-val').textContent;
      const sqft = document.getElementById('header-sqft-val').textContent;

      const cap0 = document.getElementById('caption-input-0');
      const cap3 = document.getElementById('caption-input-3');
      if (cap0) cap0.value = 'Just Listed · ' + street + ' (' + fmtPrice + ')';
      if (cap3) cap3.value = 'Own for ' + fmtPmt + ' · ' + rate.toFixed(2) + '% Rate · $2,500 Redfin Credit';

      const nar3 = document.getElementById('narration-3');
      if (nar3) {{
        nar3.textContent = '"Lock in an estimated ' + fmtPmt + ' at ' + rate.toFixed(2) + '% with Rocket Mortgage, plus a $2,500 Redfin closing credit."';
      }}

      const voBox = document.getElementById('voiceover-script-textarea');
      if (voBox) {{
        voBox.value = 'Just listed in Royal Oak! Welcome to ' + street + '—a ' + beds + '-bedroom, ' + baths + '-bath Craftsman listed at ' + fmtPrice + '. Inside its ' + sqft + ' square feet, enjoy a chef\\'s waterfall quartz kitchen and a private backyard cedar pergola. Own this home for an estimated ' + fmtPmt + ' at ' + rate.toFixed(2) + '% with Rocket Mortgage, including a $2,500 Redfin closing credit!';
      }}

      window.selectStoryboardScene(currentSceneIndex);
    }};

    window.switchRedfinListing = function(key) {{
      const item = LISTINGS_DB[key] || LISTINGS_DB.elmhurst;
      document.getElementById('crumb-address').textContent = item.street;
      document.getElementById('prop-street').textContent = item.street;
      document.getElementById('prop-city-zip').textContent = item.cityZip;
      document.getElementById('redfin-est-val').textContent = item.est;
      document.getElementById('header-beds-val').textContent = item.beds;
      document.getElementById('header-baths-val').textContent = item.baths;
      document.getElementById('header-sqft-val').textContent = item.sqft;

      document.getElementById('price-slider').value = item.price;
      document.getElementById('rate-slider').value = item.rate;
      document.getElementById('down-slider').value = item.downPct;
      window.recalculateReelPayment();
    }};

    window.playReelVoiceover = function(btnEl) {{
      const voBox = document.getElementById('voiceover-script-textarea');
      const scriptText = voBox ? voBox.value.trim() : "Welcome to 418 Elmhurst Avenue in Royal Oak, Michigan.";
      window.playLiveCallClip(
        scriptText,
        "Aoede",
        "Redfin & Rocket Mortgage Listing Video Host",
        btnEl
      );
    }};

    window.runLiveVertexAI = async function() {{
      const model = window.getSelectedModel ? window.getSelectedModel() : "gemini-4-argon";
      const outEl = document.getElementById('vertex-ai-output');
      const street = document.getElementById('prop-street').textContent;
      const price = document.getElementById('price-slider-label').textContent;
      const rate = document.getElementById('rate-slider-label').textContent;
      const pmt = document.getElementById('total-pmt-inline').textContent;
      const drawerInput = document.getElementById('scenario-input');
      const promptText = (drawerInput && drawerInput.value.trim())
        ? drawerInput.value.trim() + "\\nProperty: " + street + " (" + price + "), Rate: " + rate + ", Est. Payment: " + pmt
        : "Create a 4-scene 15-second Redfin + Rocket Mortgage Instagram Reel storyboard and Veo 3.1 camera prompts for " + street + " listed at " + price + " with an estimated monthly payment of " + pmt + " at " + rate + ".";

      if (outEl) {{
        outEl.innerHTML = "<strong>⏳ Generating 4-Scene Storyboard &amp; Veo 3.1 Camera Prompts via Vertex AI (" + model + ")...</strong>";
      }}
      try {{
        const res = await fetch('/api/run-demo', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{
            square: "4.1",
            model: model,
            scenario: promptText
          }})
        }});
        const data = await res.json();
        if (outEl) {{
          outEl.textContent = data.output || data.text || "Storyboard synthesis complete.";
        }}
      }} catch (err) {{
        if (outEl) {{
          outEl.textContent = "Unable to reach Vertex AI endpoint: " + err.message;
        }}
      }}
    }};

    document.addEventListener('DOMContentLoaded', () => {{
      window.selectStoryboardScene(0);
    }});
  </script>

  {floating_drawer}
</body>
</html>"""
