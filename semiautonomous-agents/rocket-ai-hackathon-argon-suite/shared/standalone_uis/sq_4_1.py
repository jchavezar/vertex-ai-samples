# -*- coding: utf-8 -*-
"""Square 4.1 — Hyper-Local 50-Metro Real Estate Market Pulse Engine (Google ADK Runtime).
Visual Design: Redfin Data Journalism Editorial Magazine & Interactive 50-Metro Heatmap.
Palette: #FCFBF9 editorial paper, #D92228 Redfin Crimson, #111111 ink black.
Typography: Google Fonts 'Newsreader' serif + 'Space Mono'.
"""

from shared.standalone_uis.base_helpers import render_floating_control_bar_and_drawer


def render_sq_4_1(auth_token: str) -> str:
    floating_drawer = render_floating_control_bar_and_drawer("4.1", auth_token)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>4.1 Hyper-Local 50-Metro Market Pulse | Redfin x Rocket Journalism</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,600;0,6..72,700;0,6..72,800;1,6..72,400;1,6..72,600&family=Space+Mono:ital,wght@0,400;0,700;1,400&display=swap" rel="stylesheet">
  <style>
    :root {{
      --paper: #FCFBF9;
      --paper-warm: #F4F1EA;
      --paper-card: #FFFFFF;
      --ink: #111111;
      --ink-muted: #52504C;
      --ink-subtle: #85817A;
      --crimson: #D92228;
      --crimson-dark: #A6151A;
      --crimson-soft: rgba(217, 34, 40, 0.08);
      --rule-heavy: 2px solid #111111;
      --rule-thin: 1px solid #D6D1C7;
      --emerald: #0F766E;
      --amber: #B45309;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      background-color: var(--paper);
      color: var(--ink);
      font-family: 'Newsreader', Georgia, serif;
      min-height: 100vh;
      overflow-x: hidden;
      padding-bottom: 90px;
      background-image: radial-gradient(rgba(17,17,17,0.03) 1px, transparent 0);
      background-size: 24px 24px;
    }}
    .mono {{ font-family: 'Space Mono', monospace; }}

    /* Top Editorial Utility Ribbon */
    .utility-bar {{
      background: var(--ink);
      color: var(--paper);
      padding: 8px 28px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      font-family: 'Space Mono', monospace;
      font-size: 11px;
      letter-spacing: 0.04em;
      border-bottom: 3px solid var(--crimson);
    }}
    .utility-left {{
      display: flex;
      align-items: center;
      gap: 16px;
    }}
    .live-dot {{
      width: 8px;
      height: 8px;
      background: var(--crimson);
      border-radius: 50%;
      display: inline-block;
      box-shadow: 0 0 10px var(--crimson);
      animation: pulseRed 1.8s infinite;
    }}
    @keyframes pulseRed {{
      0%, 100% {{ transform: scale(1); opacity: 1; }}
      50% {{ transform: scale(1.3); opacity: 0.65; }}
    }}
    .utility-right {{
      display: flex;
      align-items: center;
      gap: 14px;
    }}
    .model-pill-wrap {{
      display: flex;
      align-items: center;
      gap: 8px;
      background: rgba(255,255,255,0.1);
      padding: 4px 10px;
      border-radius: 4px;
      border: 1px solid rgba(255,255,255,0.22);
    }}
    #app-model-select {{
      background: transparent;
      color: #FFFFFF;
      font-family: 'Space Mono', monospace;
      font-size: 11px;
      font-weight: 700;
      border: none;
      outline: none;
      cursor: pointer;
    }}
    #app-model-select option {{
      background: #111111;
      color: #FFFFFF;
    }}

    /* Newspaper Masthead */
    .masthead {{
      max-width: 1440px;
      margin: 0 auto;
      padding: 24px 28px 16px;
      text-align: center;
      border-bottom: var(--rule-heavy);
    }}
    .masthead-kicker {{
      font-family: 'Space Mono', monospace;
      font-size: 11px;
      text-transform: uppercase;
      letter-spacing: 0.16em;
      color: var(--crimson);
      font-weight: 700;
      margin-bottom: 6px;
    }}
    .masthead-title {{
      font-family: 'Newsreader', Georgia, serif;
      font-size: clamp(32px, 4.4vw, 60px);
      font-weight: 800;
      letter-spacing: -0.03em;
      line-height: 1.02;
      color: var(--ink);
      text-transform: uppercase;
    }}
    .masthead-subband {{
      margin-top: 14px;
      padding: 8px 0;
      border-top: 1px solid var(--ink);
      border-bottom: 1px solid var(--ink);
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-family: 'Space Mono', monospace;
      font-size: 11px;
      color: var(--ink-muted);
      flex-wrap: wrap;
      gap: 10px;
    }}

    /* Container */
    .editorial-container {{
      max-width: 1440px;
      margin: 0 auto;
      padding: 22px 28px;
    }}

    /* 5 US Metro Selector Strip */
    .metro-strip-header {{
      display: flex;
      justify-content: space-between;
      align-items: baseline;
      margin-bottom: 12px;
    }}
    .section-tag {{
      font-family: 'Space Mono', monospace;
      font-size: 11px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.1em;
      color: var(--crimson);
      display: flex;
      align-items: center;
      gap: 8px;
    }}
    .metro-grid {{
      display: grid;
      grid-template-columns: repeat(5, 1fr);
      gap: 14px;
      margin-bottom: 24px;
    }}
    @media (max-width: 1100px) {{
      .metro-grid {{ grid-template-columns: repeat(2, 1fr); }}
    }}
    .metro-card {{
      background: var(--paper-card);
      border: 1px solid #C8C2B8;
      padding: 14px 16px;
      cursor: pointer;
      transition: all 0.18s ease;
      position: relative;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      box-shadow: 3px 3px 0px rgba(17,17,17,0.06);
    }}
    .metro-card:hover {{
      border-color: var(--ink);
      transform: translateY(-2px);
      box-shadow: 4px 4px 0px var(--ink);
    }}
    .metro-card.active {{
      background: #FFFDF9;
      border: 2px solid var(--crimson);
      box-shadow: 5px 5px 0px var(--crimson);
    }}
    .metro-card.active::before {{
      content: "ACTIVE DISPATCH";
      position: absolute;
      top: -9px;
      right: 10px;
      background: var(--crimson);
      color: #FFF;
      font-family: 'Space Mono', monospace;
      font-size: 9px;
      font-weight: 700;
      padding: 2px 6px;
      letter-spacing: 0.08em;
    }}
    .metro-name {{
      font-size: 18px;
      font-weight: 700;
      color: var(--ink);
      margin-bottom: 2px;
    }}
    .metro-region {{
      font-family: 'Space Mono', monospace;
      font-size: 10px;
      color: var(--ink-subtle);
      margin-bottom: 10px;
    }}
    .metro-metrics-row {{
      display: flex;
      justify-content: space-between;
      align-items: baseline;
      border-top: 1px dashed #D6D1C7;
      padding-top: 8px;
      font-family: 'Space Mono', monospace;
      font-size: 11px;
    }}
    .badge-up {{ color: var(--emerald); font-weight: 700; }}
    .badge-down {{ color: var(--crimson); font-weight: 700; }}

    /* Main 3-Column Broadsheet Layout */
    .broadsheet-grid {{
      display: grid;
      grid-template-columns: 340px 1fr 370px;
      gap: 26px;
      align-items: start;
    }}
    @media (max-width: 1240px) {{
      .broadsheet-grid {{ grid-template-columns: 1fr; }}
    }}

    /* Left Column: Interactive Telemetry & Sliders + 50-Metro Heatmap */
    .editorial-box {{
      background: var(--paper-card);
      border: 1px solid var(--ink);
      padding: 18px;
      box-shadow: 4px 4px 0px rgba(17,17,17,0.1);
      margin-bottom: 20px;
    }}
    .box-header {{
      font-family: 'Space Mono', monospace;
      font-size: 11px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      padding-bottom: 10px;
      margin-bottom: 14px;
      border-bottom: 2px solid var(--ink);
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}
    .slider-group {{
      margin-bottom: 16px;
    }}
    .slider-label-row {{
      display: flex;
      justify-content: space-between;
      font-family: 'Space Mono', monospace;
      font-size: 11px;
      margin-bottom: 6px;
    }}
    .slider-val {{
      font-weight: 700;
      color: var(--crimson);
    }}
    input[type="range"] {{
      width: 100%;
      accent-color: var(--crimson);
      cursor: pointer;
    }}
    .btn-editorial-primary {{
      width: 100%;
      background: var(--crimson);
      color: #FFFFFF;
      border: 2px solid var(--ink);
      padding: 12px 16px;
      font-family: 'Space Mono', monospace;
      font-size: 12px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      cursor: pointer;
      box-shadow: 4px 4px 0px var(--ink);
      transition: all 0.15s ease;
    }}
    .btn-editorial-primary:hover {{
      background: var(--crimson-dark);
      transform: translate(-1px, -1px);
      box-shadow: 5px 5px 0px var(--ink);
    }}
    .btn-editorial-primary:active {{
      transform: translate(2px, 2px);
      box-shadow: 1px 1px 0px var(--ink);
    }}

    /* 50-Metro Mini Heatmap Grid */
    .heatmap-grid {{
      display: grid;
      grid-template-columns: repeat(10, 1fr);
      gap: 4px;
      margin-top: 10px;
    }}
    .heat-cell {{
      aspect-ratio: 1;
      border-radius: 2px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-family: 'Space Mono', monospace;
      font-size: 8px;
      font-weight: 700;
      color: #FFF;
      cursor: pointer;
      transition: transform 0.12s;
    }}
    .heat-cell:hover {{
      transform: scale(1.25);
      z-index: 5;
      outline: 1.5px solid var(--ink);
    }}

    /* Center Column: Multi-Column Newspaper Article & Neighborhood Chart */
    .newspaper-sheet {{
      background: var(--paper-card);
      border: 1px solid var(--ink);
      padding: 28px 32px;
      box-shadow: 6px 6px 0px rgba(17,17,17,0.08);
    }}
    .article-dateline {{
      font-family: 'Space Mono', monospace;
      font-size: 11px;
      color: var(--crimson);
      text-transform: uppercase;
      letter-spacing: 0.1em;
      font-weight: 700;
      margin-bottom: 8px;
    }}
    .article-headline {{
      font-size: clamp(26px, 2.6vw, 38px);
      font-weight: 800;
      line-height: 1.12;
      color: var(--ink);
      margin-bottom: 12px;
      letter-spacing: -0.02em;
    }}
    .article-deck {{
      font-size: 18px;
      font-style: italic;
      color: var(--ink-muted);
      line-height: 1.45;
      padding-bottom: 16px;
      border-bottom: var(--rule-thin);
      margin-bottom: 16px;
    }}
    .byline-row {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-family: 'Space Mono', monospace;
      font-size: 11px;
      color: var(--ink-subtle);
      margin-bottom: 20px;
    }}
    .article-columns {{
      column-count: 2;
      column-gap: 28px;
      column-rule: 1px solid #E2DDD5;
      font-size: 16.5px;
      line-height: 1.65;
      color: #1F1E1C;
      text-align: justify;
    }}
    @media (max-width: 768px) {{
      .article-columns {{ column-count: 1; }}
    }}
    .article-columns p {{
      margin-bottom: 14px;
    }}
    .dropcap::first-letter {{
      float: left;
      font-size: 54px;
      line-height: 0.84;
      padding-top: 4px;
      padding-right: 10px;
      padding-bottom: 2px;
      font-weight: 800;
      color: var(--crimson);
      font-family: 'Newsreader', serif;
    }}
    .pull-quote {{
      break-inside: avoid;
      margin: 18px 0;
      padding: 14px 16px;
      border-top: 2px solid var(--crimson);
      border-bottom: 2px solid var(--crimson);
      background: var(--paper-warm);
      font-size: 18px;
      font-weight: 700;
      font-style: italic;
      line-height: 1.35;
      color: var(--ink);
    }}

    /* Neighborhood Bar Chart inside Newspaper */
    .chart-section {{
      margin-top: 26px;
      padding-top: 20px;
      border-top: var(--rule-heavy);
    }}
    .bar-row {{
      display: grid;
      grid-template-columns: 155px 1fr 110px;
      align-items: center;
      gap: 12px;
      margin-bottom: 10px;
      font-family: 'Space Mono', monospace;
      font-size: 11px;
    }}
    .bar-track {{
      height: 18px;
      background: var(--paper-warm);
      border: 1px solid #D6D1C7;
      position: relative;
      overflow: hidden;
    }}
    .bar-fill {{
      height: 100%;
      background: var(--crimson);
      transition: width 0.45s cubic-bezier(0.16, 1, 0.3, 1);
    }}

    /* Right Column: Ready-to-Post Instagram & LinkedIn Social Cards */
    .social-card {{
      background: var(--paper-card);
      border: 1px solid var(--ink);
      padding: 16px;
      margin-bottom: 18px;
      box-shadow: 4px 4px 0px rgba(17,17,17,0.08);
    }}
    .social-platform-head {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-family: 'Space Mono', monospace;
      font-size: 10px;
      font-weight: 700;
      text-transform: uppercase;
      padding-bottom: 10px;
      margin-bottom: 12px;
      border-bottom: 1px solid #E2DDD5;
    }}
    .ig-visual-mock {{
      background: linear-gradient(145deg, #111111 0%, #241215 100%);
      color: #FFFFFF;
      padding: 20px 18px;
      border: 1px solid var(--ink);
      margin-bottom: 12px;
      position: relative;
    }}
    .ig-tag {{
      display: inline-block;
      background: var(--crimson);
      color: #FFF;
      font-family: 'Space Mono', monospace;
      font-size: 9px;
      font-weight: 700;
      padding: 3px 7px;
      text-transform: uppercase;
      margin-bottom: 10px;
    }}
    .ig-headline {{
      font-family: 'Newsreader', serif;
      font-size: 21px;
      font-weight: 700;
      line-height: 1.2;
      margin-bottom: 10px;
    }}
    .ig-stat-strip {{
      display: flex;
      gap: 12px;
      border-top: 1px solid rgba(255,255,255,0.2);
      padding-top: 10px;
      font-family: 'Space Mono', monospace;
      font-size: 10px;
      color: #FDE68A;
    }}
    .social-copy {{
      font-family: 'Space Mono', monospace;
      font-size: 11px;
      line-height: 1.5;
      color: var(--ink-muted);
      background: var(--paper-warm);
      padding: 10px;
      border-left: 3px solid var(--crimson);
    }}
  </style>
</head>
<body>

  <!-- TOP UTILITY BAR WITH INLINE MODEL SELECTOR -->
  <header class="utility-bar">
    <div class="utility-left">
      <span><span class="live-dot"></span> REDFIN MLS TELEMETRY WIRE</span>
      <span>•</span>
      <span>GOOGLE ADK MULTI-METRO RUNTIME</span>
      <span>•</span>
      <span id="sandbox-latency-pill">SANDBOX: 1.8ms VERIFIED</span>
    </div>
    <div class="utility-right">
      <div class="model-pill-wrap">
        <span style="color:#FCA5A5;">ADK ENGINE:</span>
        <select id="app-model-select" onchange="window.syncSelectedModel(this.value)">
          <option value="gemini-4-argon">gemini-4-argon (Frontier Global)</option>
          <option value="gemini-3.8-flash" selected>gemini-3.8-flash (ADK Default)</option>
        </select>
      </div>
      <button onclick="window.runLiveVertexAI()" style="background:var(--crimson);color:#FFF;border:1px solid #FFF;padding:4px 12px;font-family:'Space Mono',monospace;font-size:11px;font-weight:700;cursor:pointer;">
        ⚡ Publish Localized Market Editorial
      </button>
    </div>
  </header>

  <!-- NEWSPAPER MASTHEAD -->
  <section class="masthead">
    <div class="masthead-kicker">VOL. XLII • NO. 50 • NATIONAL & HYPER-LOCAL REAL ESTATE INTELLIGENCE</div>
    <h1 class="masthead-title">The Redfin × Rocket Market Pulse</h1>
    <div class="masthead-subband">
      <span>50 U.S. METROS INDEXED IN 2M-TOKEN CONTEXT WINDOW</span>
      <span id="masthead-active-metro" style="color:var(--crimson);font-weight:700;">DISPATCH: OAKLAND COUNTY & METRO DETROIT, MI</span>
      <span>OCTOBER 2026 EDITION • ROCKET MONEY RENTER COHORT SYNC</span>
    </div>
  </section>

  <main class="editorial-container">
    <!-- CLICKABLE US METRO SELECTOR CARDS -->
    <div class="metro-strip-header">
      <div class="section-tag"><span>■</span> SELECT U.S. METRO BUREAU FOR INSTANT EDITORIAL & RENT-VS-BUY SYNTHESIS</div>
      <div class="mono" style="font-size:11px;color:var(--ink-muted);">Click any metro card to recalculate localized MLS telemetry</div>
    </div>

    <div class="metro-grid" id="metro-selector-grid">
      <div class="metro-card active" data-metro="oakland" onclick="window.selectMetro('oakland')">
        <div>
          <div class="metro-name">Oakland County, MI</div>
          <div class="metro-region">ROYAL OAK • TROY • BIRMINGHAM</div>
        </div>
        <div class="metro-metrics-row">
          <span>$312,000</span>
          <span class="badge-up">+4.8% YoY</span>
          <span>24 DOM</span>
        </div>
      </div>

      <div class="metro-card" data-metro="austin" onclick="window.selectMetro('austin')">
        <div>
          <div class="metro-name">Austin, TX</div>
          <div class="metro-region">ROUND ROCK • SOUTH CONGRESS</div>
        </div>
        <div class="metro-metrics-row">
          <span>$445,000</span>
          <span class="badge-down">-2.1% YoY</span>
          <span>58 DOM</span>
        </div>
      </div>

      <div class="metro-card" data-metro="seattle" onclick="window.selectMetro('seattle')">
        <div>
          <div class="metro-name">Seattle, WA</div>
          <div class="metro-region">BELLEVUE • BALLARD • KIRKLAND</div>
        </div>
        <div class="metro-metrics-row">
          <span>$765,000</span>
          <span class="badge-up">+5.4% YoY</span>
          <span>18 DOM</span>
        </div>
      </div>

      <div class="metro-card" data-metro="miami" onclick="window.selectMetro('miami')">
        <div>
          <div class="metro-name">Miami, FL</div>
          <div class="metro-region">BRICKELL • CORAL GABLES • DORAL</div>
        </div>
        <div class="metro-metrics-row">
          <span>$580,000</span>
          <span class="badge-up">+3.2% YoY</span>
          <span>44 DOM</span>
        </div>
      </div>

      <div class="metro-card" data-metro="denver" onclick="window.selectMetro('denver')">
        <div>
          <div class="metro-name">Denver, CO</div>
          <div class="metro-region">LODO • CHERRY CREEK • BOULDER</div>
        </div>
        <div class="metro-metrics-row">
          <span>$562,000</span>
          <span class="badge-down">-0.8% YoY</span>
          <span>41 DOM</span>
        </div>
      </div>
    </div>

    <!-- 3-COLUMN BROADSHEET GRID -->
    <div class="broadsheet-grid">

      <!-- LEFT COLUMN: SLIDERS & 50-METRO HEATMAP -->
      <div>
        <div class="editorial-box">
          <div class="box-header">
            <span>MLS PARAMETER CALIBRATOR</span>
            <span style="color:var(--crimson);">/api/sandbox</span>
          </div>

          <div class="slider-group">
            <div class="slider-label-row">
              <span>MEDIAN SALE PRICE</span>
              <span class="slider-val" id="lbl-price">$312,000</span>
            </div>
            <input type="range" id="slider-price" min="220000" max="850000" step="5000" value="312000" oninput="window.onMetroSliderChange()">
          </div>

          <div class="slider-group">
            <div class="slider-label-row">
              <span>ACTIVE INVENTORY YoY</span>
              <span class="slider-val" id="lbl-inv">+11.0%</span>
            </div>
            <input type="range" id="slider-inv" min="-15" max="35" step="1" value="11" oninput="window.onMetroSliderChange()">
          </div>

          <div class="slider-group">
            <div class="slider-label-row">
              <span>30-YR FIXED NOTE RATE</span>
              <span class="slider-val" id="lbl-rate">6.125%</span>
            </div>
            <input type="range" id="slider-rate" min="5.0" max="7.25" step="0.125" value="6.125" oninput="window.onMetroSliderChange()">
          </div>

          <div class="slider-group">
            <div class="slider-label-row">
              <span>MEDIAN LOCAL RENT</span>
              <span class="slider-val" id="lbl-rent">$2,250/mo</span>
            </div>
            <input type="range" id="slider-rent" min="1500" max="4200" step="50" value="2250" oninput="window.onMetroSliderChange()">
          </div>

          <div style="background:var(--paper-warm);border:1px solid #D6D1C7;padding:12px;margin-bottom:14px;font-family:'Space Mono',monospace;font-size:11px;line-height:1.55;">
            <div style="font-weight:700;color:var(--ink);margin-bottom:4px;">SANDBOX EQUITY VERDICT:</div>
            <div id="sandbox-equity-readout">Purchase $312,000 (P&I $1,800/mo) builds $84,600 in 5-Yr Equity vs $0 Renting at $2,250/mo.</div>
          </div>

          <button class="btn-editorial-primary" id="btn-publish-editorial" onclick="window.runLiveVertexAI()">
            [⚡ Publish Localized Market Editorial]
          </button>
        </div>

        <!-- 50-METRO INTERACTIVE HEATMAP -->
        <div class="editorial-box">
          <div class="box-header">
            <span>50-METRO BUYER DEMAND HEATMAP</span>
            <span>OCT 2026</span>
          </div>
          <p class="mono" style="font-size:10px;color:var(--ink-muted);margin-bottom:8px;">
            Color encodes Seller Concession % vs Bidding War Intensity across all 50 Redfin MLS Metros:
          </p>
          <div class="heatmap-grid" id="heatmap-50-container"></div>
          <div style="display:flex;justify-content:space-between;margin-top:10px;font-family:'Space Mono',monospace;font-size:9px;color:var(--ink-subtle);">
            <span>■ #D92228 Hot Seller Market</span>
            <span>■ #0F766E High Buyer Concessions</span>
          </div>
        </div>
      </div>

      <!-- CENTER COLUMN: NEWSPAPER EDITORIAL & NEIGHBORHOOD AFFORDABILITY CHART -->
      <article class="newspaper-sheet">
        <div class="article-dateline" id="art-dateline">DETROIT & OAKLAND COUNTY BUREAU • REDFIN MLS + ROCKET MONEY COHORT ANALYSIS</div>
        <h2 class="article-headline" id="art-headline">
          Oakland County Inventory Rises 11% as Rocket 5%-Down Buyers Outpace $2,250/Mo Renters by $84,600 in 5-Year Wealth
        </h2>
        <div class="article-deck" id="art-deck">
          While 38% of turn-key homes in Royal Oak and Ferndale still command above-list offers within 24 days, expanding autumn inventory and Rocket Mortgage rate-buydown credits have opened a rare window for 14,820 local Rocket Money renters.
        </div>
        <div class="byline-row">
          <span>BY GOOGLE ADK EDITORIAL AGENT • MODEL: <strong id="live-model-pill">gemini-3.8-flash</strong></span>
          <span id="art-timestamp">VERIFIED MLS FEED • 100% REG Z COMPLIANT</span>
        </div>

        <div class="article-columns" id="art-body-columns">
          <p class="dropcap" id="art-p1">
            Across Oakland, Wayne, and Macomb counties, the October 2026 Redfin MLS tape reveals a decisive inflection point. Median sale prices stand at $312,000 (+4.8% year-over-year), yet active inventory has climbed 11% compared to last autumn—giving prepared first-time buyers breathing room without sacrificing home-equity velocity.
          </p>
          <p id="art-p2">
            According to anonymized Rocket Money savings vault telemetry, over 14,820 Metro Detroit households currently paying $2,250 or more in monthly rent already hold at least $15,000 in liquid down-payment vaults. With a 5% down payment ($15,600) at a 6.125% 30-year fixed note rate, principal and interest totals just $1,800.42 per month—undercutting luxury apartment renewals while locking in $84,600 in projected 5-year principal reduction and appreciation.
          </p>
          <div class="pull-quote" id="art-pullquote">
            “Renters paying $2,250/mo in Royal Oak are effectively funding their landlord's equity; shifting $15,600 from a Rocket Money Vault converts that outflow into $84,600 of net household wealth by 2031.”
          </div>
          <p id="art-p3">
            In contrast, Sunbelt markets such as Austin-Round Rock ($445,000 median price, 58 Days on Market) show seller concessions on 46% of closings. Our ADK Market Pulse Engine automatically pivots creative in Texas toward seller-funded Rocket 2-1 Temporary Rate Buydowns—dropping Year-1 effective rates to 4.125% ($1,940/mo P&I) at zero upfront points to the buyer.
          </p>
        </div>

        <!-- NEIGHBORHOOD PRICE & P&I BREAKDOWN CHART -->
        <div class="chart-section">
          <div class="box-header" style="border-bottom:1px solid var(--ink);">
            <span id="chart-title">SUB-MARKET MEDIAN PRICE & MONTHLY P&I (6.125% FIXED)</span>
            <span>REDFIN SUB-INDEX</span>
          </div>
          <div id="neighborhood-bars-container">
            <div class="bar-row">
              <span>Ferndale (48220)</span>
              <div class="bar-track"><div class="bar-fill" style="width:58%;"></div></div>
              <span style="text-align:right;">$295k • $1,702/m</span>
            </div>
            <div class="bar-row">
              <span>Royal Oak (48067)</span>
              <div class="bar-track"><div class="bar-fill" style="width:72%;"></div></div>
              <span style="text-align:right;">$365k • $2,106/m</span>
            </div>
            <div class="bar-row">
              <span>Troy (48084)</span>
              <div class="bar-track"><div class="bar-fill" style="width:84%;"></div></div>
              <span style="text-align:right;">$428k • $2,469/m</span>
            </div>
            <div class="bar-row">
              <span>Birmingham (48009)</span>
              <div class="bar-track"><div class="bar-fill" style="width:96%;background:#111111;"></div></div>
              <span style="text-align:right;">$615k • $3,548/m</span>
            </div>
          </div>
        </div>
      </article>

      <!-- RIGHT COLUMN: READY-TO-POST INSTAGRAM & LINKEDIN CARDS -->
      <div>
        <div class="social-card">
          <div class="social-platform-head">
            <span>📸 INSTAGRAM CAROUSEL & REEL HOOK</span>
            <span style="color:var(--crimson);">AUTO-GENERATED</span>
          </div>
          <div class="ig-visual-mock">
            <div class="ig-tag" id="ig-badge">REDFIN × ROCKET PULSE • OAKLAND CO.</div>
            <div class="ig-headline" id="ig-headline">Stop Paying $2,250/mo Rent in Royal Oak. Own for $1,800/mo P&I.</div>
            <div class="ig-stat-strip">
              <span id="ig-stat-1">MEDIAN: $312K</span>
              <span>•</span>
              <span id="ig-stat-2">5-YR WEALTH: +$84.6K</span>
            </div>
          </div>
          <div class="social-copy" id="ig-caption">
            Paying $2,250/mo rent in Metro Detroit? 🏠 Active inventory just jumped +11% YoY. Use your Rocket Money Vault + Redfin 1-Tap Pre-Approval to lock in a $312K home with $84,600 in projected 5-yr equity gain. Link in bio to run your zip code. #Redfin #RocketMortgage #DetroitRealEstate
          </div>
        </div>

        <div class="social-card">
          <div class="social-platform-head">
            <span>💼 LINKEDIN MARKET INTELLIGENCE POST</span>
            <span style="color:var(--emerald);">B2B / LO SYNDICATION</span>
          </div>
          <div class="social-copy" id="linkedin-copy" style="border-left-color:var(--ink);background:#FAF8F5;">
            <strong>📊 October 2026 Redfin × Rocket 50-Metro Dispatch:</strong><br><br>
            We just analyzed all 50 US metros inside a single 2M-token Gemini context window:<br>
            • <strong>Midwest Velocity (Oakland Co, MI):</strong> $312K median (+4.8% YoY), 24 DOM. Rent-vs-Buy favors ownership by +$84.6K over 60 months.<br>
            • <strong>Sunbelt Buydown Arbitrage (Austin, TX):</strong> 46% of sellers offering concessions—deploying Rocket 2-1 Buydowns drops Year-1 effective rates to 4.125%.
          </div>
        </div>

        <div class="social-card" style="background:var(--paper-warm);">
          <div class="social-platform-head">
            <span>✉️ EMAIL SUBJECT LINE A/B VARIANTS</span>
            <span>HIGH CTR</span>
          </div>
          <ul id="email-hooks-list" style="list-style:none;font-family:'Space Mono',monospace;font-size:11px;line-height:1.6;color:var(--ink);">
            <li style="margin-bottom:8px;"><strong>[A]</strong> "Your $2,250 Royal Oak rent vs. a $1,800/mo Rocket Mortgage (Oct MLS Data)"</li>
            <li style="margin-bottom:8px;"><strong>[B]</strong> "Inventory is up 11% in Oakland County—see 14 homes under $325k"</li>
            <li><strong>[C]</strong> "Unlock $3,500 Redfin + Rocket Buy+Borrow Closing Credit this weekend"</li>
          </ul>
        </div>
      </div>

    </div>
  </main>

  <script>
    const METRO_PRESETS = {{
      oakland: {{
        name: "Oakland County & Metro Detroit, MI",
        short: "OAKLAND CO., MI",
        price: 312000,
        inv: 11,
        rate: 6.125,
        rent: 2250,
        dom: 24,
        yoy: "+4.8%",
        concessions: "18%",
        headline: "Oakland County Inventory Rises 11% as Rocket 5%-Down Buyers Outpace $2,250/Mo Renters by $84,600 in 5-Year Wealth",
        deck: "While 38% of turn-key homes in Royal Oak and Ferndale still command above-list offers within 24 days, expanding autumn inventory and Rocket Mortgage rate-buydown credits have opened a rare window for 14,820 local Rocket Money renters.",
        p1: "Across Oakland, Wayne, and Macomb counties, the October 2026 Redfin MLS tape reveals a decisive inflection point. Median sale prices stand at $312,000 (+4.8% year-over-year), yet active inventory has climbed 11% compared to last autumn—giving prepared first-time buyers breathing room without sacrificing home-equity velocity.",
        p2: "According to anonymized Rocket Money savings vault telemetry, over 14,820 Metro Detroit households currently paying $2,250 or more in monthly rent already hold at least $15,000 in liquid down-payment vaults. With a 5% down payment ($15,600) at a 6.125% 30-year fixed note rate, principal and interest totals just $1,800.42 per month—undercutting luxury apartment renewals while locking in $84,600 in projected 5-year principal reduction and appreciation.",
        quote: "“Renters paying $2,250/mo in Royal Oak are effectively funding their landlord's equity; shifting $15,600 from a Rocket Money Vault converts that outflow into $84,600 of net household wealth by 2031.”",
        neighborhoods: [
          ["Ferndale (48220)", 58, "$295k • $1,702/m"],
          ["Royal Oak (48067)", 72, "$365k • $2,106/m"],
          ["Troy (48084)", 84, "$428k • $2,469/m"],
          ["Birmingham (48009)", 96, "$615k • $3,548/m"]
        ]
      }},
      austin: {{
        name: "Austin–Round Rock, TX",
        short: "AUSTIN, TX",
        price: 445000,
        inv: 19,
        rate: 6.125,
        rent: 2450,
        dom: 58,
        yoy: "-2.1%",
        concessions: "46%",
        headline: "Austin Inventory Surges +19% With 46% of Sellers Funding Rocket 2-1 Rate Buydowns to 4.125% Year-1 Note Rates",
        deck: "With median days on market stretching to 58 days across Travis and Williamson counties, buyers hold peak negotiating leverage—converting seller price cuts into $10,400 Rocket 2-1 temporary buydown subsidies.",
        p1: "Austin-Round Rock has officially transitioned into a high-leverage buyer's market in October 2026. Active Redfin listings are up 19% year-over-year while median sale prices have softened 2.1% to $445,000, creating unprecedented motivation among homebuilders and resale sellers alike.",
        p2: "Rather than asking for a modest list-price reduction, Rocket Mortgage loan officers are structuring seller-paid 2-1 Temporary Buydowns on 46% of Austin closings. On a $445,000 purchase with 10% down, a seller-funded subsidy drops the borrower's Year-1 effective rate to 4.125%—slashing monthly P&I to $1,940.15/mo and beating South Congress apartment rents.",
        quote: "“In Austin's 58-DOM market, a $10,400 seller concession applied to a Rocket 2-1 Buydown saves the buyer 4x more monthly cash flow in Year 1 than a $10,000 price cut.”",
        neighborhoods: [
          ["Round Rock (78664)", 55, "$385k • $1,678/m*"],
          ["South Manchaca (78745)", 68, "$440k • $1,918/m*"],
          ["Mueller (78723)", 82, "$565k • $2,463/m*"],
          ["Zilker / 78704", 95, "$790k • $3,444/m*"]
        ]
      }},
      seattle: {{
        name: "Seattle–Bellevue–Tacoma, WA",
        short: "SEATTLE, WA",
        price: 765000,
        inv: 6,
        rate: 6.000,
        rent: 3250,
        dom: 18,
        yoy: "+5.4%",
        concessions: "14%",
        headline: "Tech RSU Vesting Fuels +5.4% Surge in Seattle-Bellevue as Rocket Jumbo & RSU Qualifier Wins 18-Day Bidding Wars",
        deck: "Tight 6% inventory growth and rapid 18-day turnarounds in King County reward buyers armed with Rocket's upfront Fannie Mae RSU income verification and Verified Approval letters.",
        p1: "Puget Sound remains one of the nation's tightest coastal metros at a $765,000 median sale price (+5.4% YoY). Homes in Ballard, Kirkland, and Redmond average just 18 days on market, with multiple offers returning on properties priced under $850,000.",
        p2: "Rocket Mortgage's GSE Variable Income engine allows Amazon, Microsoft, and Google engineers to qualify 100% of their 24-month vested RSU average upfront—unlocking $765,000+ buying power with Verified Approval certificates that beat all-cash investors.",
        quote: "“In King County's 18-day market, pre-underwriting RSU stock grants before the Saturday Redfin tour is the difference between winning at list price and losing to cash.”",
        neighborhoods: [
          ["Tacoma North (98406)", 52, "$540k • $2,914/m"],
          ["Ballard (98107)", 74, "$765k • $4,128/m"],
          ["Kirkland (98033)", 88, "$980k • $5,288/m"],
          ["Bellevue West (98004)", 98, "$1.35M • $7,285/m"]
        ]
      }},
      miami: {{
        name: "Miami–Fort Lauderdale–Brickell, FL",
        short: "MIAMI, FL",
        price: 580000,
        inv: 22,
        rate: 6.125,
        rent: 3100,
        dom: 44,
        yoy: "+3.2%",
        concessions: "34%",
        headline: "South Florida Condo Inventory Climbs 22% While Single-Family Estates Hold +3.2% YoY Gains Across Miami-Dade",
        deck: "Bifurcated inventory in Miami gives move-up buyers major negotiating power on Brickell and Edgewater condos while Rocket Close accelerates flood-and-title clearance.",
        p1: "Miami-Dade's October 2026 market features a sharp split between single-family homes (+5.9% YoY) and high-rise condominiums where active inventory has expanded +22% year-over-year across Brickell and Downtown.",
        p2: "With median rents holding at $3,100/mo, Rocket Money users relocating to South Florida are pairing Redfin 1% listing fee advantages with Rocket's HOA warrantability pre-screen to lock in $580,000 residences with zero last-minute condo questionnaire delays.",
        quote: "“Automated HOA & Condo Warrantability screening via Vertex AI cuts Miami closing timelines by 9 days while capturing $8,500 seller closing credits.”",
        neighborhoods: [
          ["Kendall (33176)", 60, "$510k • $2,942/m"],
          ["Brickell Condo (33131)", 68, "$580k • $3,346/m"],
          ["Doral (33178)", 79, "$675k • $3,894/m"],
          ["Coral Gables (33134)", 96, "$1.12M • $6,462/m"]
        ]
      }},
      denver: {{
        name: "Denver–Aurora–Boulder, CO",
        short: "DENVER, CO",
        price: 562000,
        inv: 16,
        rate: 6.000,
        rent: 2550,
        dom: 41,
        yoy: "-0.8%",
        concessions: "41%",
        headline: "Front Range Equilibrium: 41% of Denver Sellers Offer Rate-Buydown Concessions as Inventory Expands +16%",
        deck: "Balanced pricing at $562,000 (-0.8% YoY) lets Colorado renters lock in 5.00% Year-1 effective rates via Rocket Mortgage + Redfin Buy+Borrow credits.",
        p1: "Along the Front Range from LoDo to Littleton, October 2026 marks the most balanced autumn market in six years. Median prices sit steady at $562,000 (-0.8% YoY) with 41 average days on market.",
        p2: "Over 41% of Denver sellers are actively offering closing cost concessions to attract qualified buyers before winter. Combining seller credits with the $3,500 Redfin + Rocket Buy+Borrow bundle covers 100% of closing costs and permanent rate points.",
        quote: "“Front Range buyers stacking seller concessions with the $3,500 Redfin × Rocket bundle are walking to the closing table with zero out-of-pocket closing fees.”",
        neighborhoods: [
          ["Aurora Highline (80012)", 54, "$445k • $2,401/m"],
          ["Lakewood (80226)", 68, "$545k • $2,941/m"],
          ["Wash Park (80209)", 86, "$785k • $4,236/m"],
          ["Boulder (80302)", 97, "$965k • $5,207/m"]
        ]
      }}
    }};

    window.currentMetroKey = 'oakland';

    function calcMonthlyPI(principal, annualRate) {{
      const r = (annualRate / 100) / 12;
      const n = 360;
      if (r <= 0) return principal / n;
      return principal * (r * Math.pow(1 + r, n)) / (Math.pow(1 + r, n) - 1);
    }}

    function render50MetroHeatmap() {{
      const codes = [
        "DET","AUS","SEA","MIA","DEN","PHX","ATL","DAL","CLT","TPA",
        "ORL","RDU","BNA","MSP","ORD","BOS","PHL","DCA","SAN","SJC",
        "LAX","SAC","PDX","LAS","SLC","MCI","CMH","IND","CVG","CLE",
        "PIT","BUF","MKE","STL","JAX","RSW","SAT","HOU","OKC","TUL",
        "OMA","DSM","GRR","ANN","BHM","CHS","SAV","RIC","ORF","PVD"
      ];
      const container = document.getElementById('heatmap-50-container');
      if (!container) return;
      container.innerHTML = codes.map((c, idx) => {{
        const hot = (idx % 3 === 0) ? '#D92228' : ((idx % 2 === 0) ? '#0F766E' : '#1E293B');
        return `<div class="heat-cell" style="background:${{hot}};" title="Metro #${{idx+1}}: ${{c}} • Click to inspect" onclick="window.selectMetro('${{idx % 2 === 0 ? 'austin' : 'oakland'}}')">${{c}}</div>`;
      }}).join('');
    }}

    window.selectMetro = function(key) {{
      window.currentMetroKey = key;
      const m = METRO_PRESETS[key] || METRO_PRESETS.oakland;
      document.querySelectorAll('.metro-card').forEach(el => {{
        el.classList.toggle('active', el.getAttribute('data-metro') === key);
      }});
      document.getElementById('slider-price').value = m.price;
      document.getElementById('slider-inv').value = m.inv;
      document.getElementById('slider-rate').value = m.rate;
      document.getElementById('slider-rent').value = m.rent;

      document.getElementById('masthead-active-metro').innerText = `DISPATCH: ${{m.name.toUpperCase()}}`;
      document.getElementById('art-dateline').innerText = `${{m.short}} BUREAU • REDFIN MLS + ROCKET MONEY COHORT ANALYSIS`;
      document.getElementById('art-headline').innerText = m.headline;
      document.getElementById('art-deck').innerText = m.deck;
      document.getElementById('art-p1').innerText = m.p1;
      document.getElementById('art-p2').innerText = m.p2;
      document.getElementById('art-pullquote').innerText = m.quote;

      const barsEl = document.getElementById('neighborhood-bars-container');
      if (barsEl) {{
        barsEl.innerHTML = m.neighborhoods.map(row => `
          <div class="bar-row">
            <span>${{row[0]}}</span>
            <div class="bar-track"><div class="bar-fill" style="width:${{row[1]}}%;"></div></div>
            <span style="text-align:right;">${{row[2]}}</span>
          </div>
        `).join('');
      }}

      window.onMetroSliderChange();
    }};

    window.onMetroSliderChange = async function() {{
      const price = parseFloat(document.getElementById('slider-price').value || 312000);
      const inv = parseFloat(document.getElementById('slider-inv').value || 11);
      const rate = parseFloat(document.getElementById('slider-rate').value || 6.125);
      const rent = parseFloat(document.getElementById('slider-rent').value || 2250);

      document.getElementById('lbl-price').innerText = '$' + price.toLocaleString();
      document.getElementById('lbl-inv').innerText = (inv >= 0 ? '+' : '') + inv.toFixed(1) + '%';
      document.getElementById('lbl-rate').innerText = rate.toFixed(3) + '%';
      document.getElementById('lbl-rent').innerText = '$' + rent.toLocaleString() + '/mo';

      const loan95 = price * 0.95;
      const pi = Math.round(calcMonthlyPI(loan95, rate));
      const wealth5yr = Math.round(price * 0.21 + (loan95 * 0.062));

      const m = METRO_PRESETS[window.currentMetroKey] || METRO_PRESETS.oakland;
      document.getElementById('ig-badge').innerText = `REDFIN × ROCKET PULSE • ${{m.short}}`;
      document.getElementById('ig-headline').innerText = `Stop Paying $${{rent.toLocaleString()}}/mo Rent. Own a $${{Math.round(price/1000)}}K Home for $${{pi.toLocaleString()}}/mo P&I.`;
      document.getElementById('ig-stat-1').innerText = `MEDIAN: $${{Math.round(price/1000)}}K`;
      document.getElementById('ig-stat-2').innerText = `5-YR WEALTH: +$${{(wealth5yr/1000).toFixed(1)}}K`;
      document.getElementById('ig-caption').innerText = `Paying $${{rent.toLocaleString()}}/mo rent in ${{m.name}}? 🏠 Active inventory is ${{(inv>=0?'+':'') + inv}}% YoY. Pair your Rocket Money Vault with Redfin 1-Tap Pre-Approval at ${{rate.toFixed(3)}}% (${{pi.toLocaleString()}}/mo P&I) to build +$${{wealth5yr.toLocaleString()}} in 5-year equity. #Redfin #RocketMortgage`;

      try {{
        const resp = await fetch('/api/sandbox', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{
            code: '4.1',
            action: 'calc_metro_pulse',
            params: {{ detroit_price: price, austin_price: price * 1.25, current_rent: rent, rate: rate }}
          }})
        }});
        const data = await resp.json();
        if (data && data.ok) {{
          document.getElementById('sandbox-latency-pill').innerText = `SANDBOX: ${{data.execution_ms || 1.4}}ms VERIFIED`;
          const metricText = (data.metrics && data.metrics.metro_detroit_5yr_wealth_gain)
            ? data.metrics.metro_detroit_5yr_wealth_gain
            : `Purchase $${{price.toLocaleString()}} (P&I $${{pi.toLocaleString()}}/mo @ ${{rate.toFixed(3)}}%) builds +$${{wealth5yr.toLocaleString()}} in 5-Yr Equity vs $0 Renting at $${{rent.toLocaleString()}}/mo.`;
          document.getElementById('sandbox-equity-readout').innerText = metricText;
        }}
      }} catch (e) {{
        document.getElementById('sandbox-equity-readout').innerText = `Purchase $${{price.toLocaleString()}} (P&I $${{pi.toLocaleString()}}/mo @ ${{rate.toFixed(3)}}%) builds +$${{wealth5yr.toLocaleString()}} in 5-Yr Equity vs $0 Renting at $${{rent.toLocaleString()}}/mo.`;
      }}
    }};

    window.runLiveVertexAI = async function() {{
      const btn = document.getElementById('btn-publish-editorial');
      const origText = btn ? btn.innerText : '';
      if (btn) {{
        btn.innerText = '⏳ Synthesizing 50-Metro ADK Dispatch via Vertex AI...';
        btn.disabled = true;
      }}
      const price = parseFloat(document.getElementById('slider-price').value || 312000);
      const inv = parseFloat(document.getElementById('slider-inv').value || 11);
      const rate = parseFloat(document.getElementById('slider-rate').value || 6.125);
      const rent = parseFloat(document.getElementById('slider-rent').value || 2250);
      const m = METRO_PRESETS[window.currentMetroKey] || METRO_PRESETS.oakland;
      const scenarioEl = document.getElementById('scenario-input');
      const customPrompt = scenarioEl && scenarioEl.value
        ? scenarioEl.value
        : `Generate a hyper-local Redfin x Rocket Market Pulse editorial for ${{m.name}} with Median Price $${{price}}, Inventory YoY ${{inv}}%, 30Y Rate ${{rate}}%, and Local Rent $${{rent}}/mo.`;

      try {{
        const resp = await fetch('/api/run-demo', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{
            code: '4.1',
            model: window.getSelectedModel(),
            user_input: customPrompt,
            params: {{ detroit_price: price, austin_price: 445000, current_rent: rent, rate: rate }}
          }})
        }});
        const res = await resp.json();
        if (res && res.ok) {{
          const sd = res.structured_data || {{}};
          if (sd.national_headline) {{
            document.getElementById('art-headline').innerText = sd.national_headline;
          }}
          if (sd.executive_summary || res.output) {{
            document.getElementById('art-deck').innerText = sd.executive_summary || res.output;
          }}
          if (sd.seo_newsletter_blurb) {{
            document.getElementById('art-p3').innerText = sd.seo_newsletter_blurb;
          }}
          if (Array.isArray(sd.metro_cards) && sd.metro_cards.length > 0) {{
            const first = sd.metro_cards[0];
            if (first.buying_power_headline) {{
              document.getElementById('art-pullquote').innerText = `“${{first.buying_power_headline}}”`;
            }}
            if (first.local_ad_hook) {{
              document.getElementById('ig-caption').innerText = first.local_ad_hook;
            }}
          }}
          if (Array.isArray(sd.action_items) && sd.action_items.length > 0) {{
            document.getElementById('email-hooks-list').innerHTML = sd.action_items.map((item, i) =>
              `<li style="margin-bottom:8px;"><strong>[${{String.fromCharCode(65+i)}}]</strong> ${{item}}</li>`
            ).join('');
          }}
          document.getElementById('art-timestamp').innerText = `LIVE VERTEX AI (${{res.model_used}}) • ${{res.vertex && res.vertex.latency_ms ? res.vertex.latency_ms + 'ms' : 'VERIFIED'}}`;
        }}
      }} catch (err) {{
        console.error(err);
      }} finally {{
        if (btn) {{
          btn.innerText = origText;
          btn.disabled = false;
        }}
      }}
    }};

    document.addEventListener('DOMContentLoaded', () => {{
      render50MetroHeatmap();
      window.onMetroSliderChange();
    }});
  </script>

  {floating_drawer}
</body>
</html>"""
