# -*- coding: utf-8 -*-
"""Square 4.3 — Hyper-Local First-Time Buyer Guide (Metro Detroit & Royal Oak Editorial Magazine).
Visual Design: New York Times Real Estate / Dwell Architectural Neighborhood Magazine.
Palette: #FBF9F5 archival warm magazine paper, #1C1917 editorial ink black, #9A3412 terracotta accents.
Typography: Google Fonts 'Playfair Display', 'Source Serif 4', and 'Plus Jakarta Sans'.
"""

from shared.standalone_uis.base_helpers import render_floating_control_bar_and_drawer


def render_sq_4_3(auth_token: str) -> str:
    floating_drawer = render_floating_control_bar_and_drawer("4.3", auth_token)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Metro Detroit & Royal Oak First-Time Buyer Guide | NYT Real Estate × Dwell Editorial</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,600;0,700;0,800;1,600&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;0,8..60,700;1,8..60,400&display=swap" rel="stylesheet">
  <style>
    :root {{
      --paper: #FBF9F5;
      --paper-card: #FFFFFF;
      --paper-tint: #F4EFE6;
      --ink: #1C1917;
      --ink-body: #292524;
      --ink-muted: #57534E;
      --ink-subtle: #78716C;
      --terracotta: #9A3412;
      --terracotta-dark: #7C2D12;
      --terracotta-soft: #FFEDD5;
      --sage-green: #15803D;
      --sage-bg: #DCFCE7;
      --rule-heavy: 2px solid #1C1917;
      --rule-light: 1px solid #D6D3D1;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      background-color: var(--paper);
      color: var(--ink-body);
      font-family: 'Source Serif 4', Georgia, serif;
      min-height: 100vh;
      overflow-x: hidden;
      padding-bottom: 96px;
      line-height: 1.6;
    }}
    .sans {{ font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif; }}
    .display-serif {{ font-family: 'Playfair Display', Georgia, serif; }}

    /* Top Editorial Masthead Ribbon */
    .editorial-topbar {{
      background: var(--paper);
      border-bottom: 1px solid #D6D3D1;
      padding: 10px 28px;
      font-family: 'Plus Jakarta Sans', sans-serif;
      font-size: 12px;
    }}
    .editorial-topbar-inner {{
      max-width: 1360px;
      margin: 0 auto;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 14px;
      flex-wrap: wrap;
    }}
    .edition-meta {{
      display: flex;
      align-items: center;
      gap: 14px;
      color: var(--ink-muted);
      font-weight: 600;
    }}
    .terracotta-tag {{
      background: var(--terracotta);
      color: #FFFFFF;
      font-weight: 700;
      font-size: 11px;
      padding: 3px 9px;
      border-radius: 4px;
      letter-spacing: 0.04em;
      text-transform: uppercase;
    }}
    .topbar-controls {{
      display: flex;
      align-items: center;
      gap: 10px;
      flex-wrap: wrap;
    }}
    .model-select-pill {{
      display: flex;
      align-items: center;
      gap: 6px;
      background: var(--paper-card);
      border: 1px solid #D6D3D1;
      padding: 5px 10px;
      border-radius: 6px;
      font-weight: 600;
    }}
    #app-model-select {{
      border: none;
      background: transparent;
      font-family: 'Plus Jakarta Sans', sans-serif;
      font-size: 12px;
      font-weight: 700;
      color: var(--terracotta);
      outline: none;
      cursor: pointer;
    }}
    .btn-terracotta {{
      background: var(--terracotta);
      color: #FFFFFF;
      border: none;
      border-radius: 6px;
      padding: 8px 15px;
      font-family: 'Plus Jakarta Sans', sans-serif;
      font-size: 12.5px;
      font-weight: 700;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 7px;
      transition: background 0.15s ease;
    }}
    .btn-terracotta:hover {{
      background: var(--terracotta-dark);
    }}

    /* Magazine Masthead */
    .magazine-header {{
      max-width: 1360px;
      margin: 0 auto;
      padding: 28px 28px 20px;
      text-align: center;
      border-bottom: var(--rule-heavy);
    }}
    .magazine-kicker {{
      font-family: 'Plus Jakarta Sans', sans-serif;
      font-size: 11.5px;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 0.14em;
      color: var(--terracotta);
      margin-bottom: 8px;
    }}
    .magazine-headline {{
      font-family: 'Playfair Display', Georgia, serif;
      font-size: clamp(30px, 4vw, 52px);
      font-weight: 800;
      color: var(--ink);
      line-height: 1.08;
      letter-spacing: -0.02em;
    }}
    .magazine-deck {{
      max-width: 820px;
      margin: 12px auto 0;
      font-size: 17px;
      color: var(--ink-muted);
      font-style: italic;
    }}

    /* Main Container */
    .editorial-main {{
      max-width: 1360px;
      margin: 0 auto;
      padding: 24px 28px;
    }}

    /* Interactive 4-Neighborhood Selector Bar */
    .neighborhood-strip-label {{
      font-family: 'Plus Jakarta Sans', sans-serif;
      font-size: 12px;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: var(--terracotta);
      margin-bottom: 10px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}
    .neighborhood-tabs {{
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 14px;
      margin-bottom: 26px;
    }}
    @media (max-width: 980px) {{
      .neighborhood-tabs {{ grid-template-columns: repeat(2, 1fr); }}
    }}
    .hood-card {{
      background: var(--paper-card);
      border: 1px solid #D6D3D1;
      border-top: 3px solid transparent;
      border-radius: 8px;
      padding: 15px 16px;
      cursor: pointer;
      transition: all 0.16s ease;
      font-family: 'Plus Jakarta Sans', sans-serif;
    }}
    .hood-card:hover {{
      border-color: var(--ink);
    }}
    .hood-card.active {{
      border-color: var(--terracotta);
      border-top: 4px solid var(--terracotta);
      background: #FFFDF9;
      box-shadow: 0 6px 18px rgba(154, 52, 18, 0.08);
    }}
    .hood-name {{
      font-family: 'Playfair Display', Georgia, serif;
      font-size: 18px;
      font-weight: 700;
      color: var(--ink);
    }}
    .hood-zip {{
      font-size: 11.5px;
      font-weight: 700;
      color: var(--terracotta);
      margin-top: 2px;
    }}
    .hood-stats {{
      display: flex;
      justify-content: space-between;
      margin-top: 10px;
      padding-top: 8px;
      border-top: 1px solid #E7E5E4;
      font-size: 12px;
      color: var(--ink-muted);
    }}
    .hood-stats strong {{
      color: var(--ink);
    }}

    /* Editorial Feature Grid */
    .editorial-grid {{
      display: grid;
      grid-template-columns: 1.15fr 1fr;
      gap: 28px;
      align-items: start;
    }}
    @media (max-width: 1060px) {{
      .editorial-grid {{ grid-template-columns: 1fr; }}
    }}

    .article-card {{
      background: var(--paper-card);
      border: 1px solid #D6D3D1;
      border-radius: 10px;
      padding: 24px 26px;
      margin-bottom: 22px;
    }}
    .article-kicker {{
      font-family: 'Plus Jakarta Sans', sans-serif;
      font-size: 11px;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 0.1em;
      color: var(--terracotta);
      margin-bottom: 6px;
    }}
    .article-title {{
      font-family: 'Playfair Display', Georgia, serif;
      font-size: 26px;
      font-weight: 700;
      color: var(--ink);
      line-height: 1.2;
      margin-bottom: 12px;
    }}
    .article-prose {{
      font-size: 16px;
      color: var(--ink-body);
      margin-bottom: 16px;
    }}
    .dropcap::first-letter {{
      font-family: 'Playfair Display', Georgia, serif;
      float: left;
      font-size: 46px;
      line-height: 0.85;
      padding-right: 10px;
      padding-top: 4px;
      color: var(--terracotta);
      font-weight: 800;
    }}

    .arch-callout-grid {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 12px;
      background: var(--paper-tint);
      padding: 14px;
      border-radius: 8px;
      border: 1px solid #E7E5E4;
      font-family: 'Plus Jakarta Sans', sans-serif;
      margin-bottom: 18px;
    }}
    .arch-stat-lbl {{
      font-size: 11px;
      font-weight: 700;
      color: var(--ink-muted);
      text-transform: uppercase;
    }}
    .arch-stat-val {{
      font-size: 16px;
      font-weight: 800;
      color: var(--ink);
      margin-top: 3px;
    }}

    /* MSHDA $10,000 + Detroit $25,000 Grant Calculator */
    .grant-calc-card {{
      background: var(--paper-card);
      border: 1px solid #D6D3D1;
      border-top: 4px solid var(--terracotta);
      border-radius: 10px;
      padding: 22px 24px;
      margin-bottom: 22px;
      font-family: 'Plus Jakarta Sans', sans-serif;
    }}
    .grant-option {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 12px 14px;
      border: 1px solid #E7E5E4;
      border-radius: 8px;
      margin-bottom: 10px;
      cursor: pointer;
      background: #FCFBF9;
      transition: all 0.15s ease;
    }}
    .grant-option.checked {{
      background: #FFF7ED;
      border-color: var(--terracotta);
    }}
    .grant-check-left {{
      display: flex;
      align-items: center;
      gap: 12px;
    }}
    .grant-checkbox {{
      width: 20px;
      height: 20px;
      accent-color: var(--terracotta);
      cursor: pointer;
    }}
    .grant-amount-pill {{
      font-weight: 800;
      font-size: 14px;
      color: var(--terracotta);
      background: var(--terracotta-soft);
      padding: 4px 10px;
      border-radius: 6px;
      white-space: nowrap;
    }}

    .cash-to-close-summary {{
      background: var(--paper-tint);
      border: 1px solid #D6D3D1;
      border-radius: 8px;
      padding: 16px;
      margin-top: 14px;
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 12px;
    }}
    @media (max-width: 640px) {{
      .cash-to-close-summary {{ grid-template-columns: 1fr; }}
    }}

    /* Rent-vs-Buy 5-Year Wealth Comparison Table */
    .wealth-table-wrap {{
      overflow-x: auto;
      margin-top: 12px;
      font-family: 'Plus Jakarta Sans', sans-serif;
    }}
    table.wealth-table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 13px;
    }}
    table.wealth-table th {{
      text-align: left;
      padding: 10px 12px;
      border-bottom: 2px solid var(--ink);
      font-size: 11.5px;
      font-weight: 800;
      text-transform: uppercase;
      color: var(--ink-muted);
      background: var(--paper-tint);
    }}
    table.wealth-table td {{
      padding: 10px 12px;
      border-bottom: 1px solid #E7E5E4;
      color: var(--ink-body);
      font-weight: 600;
    }}
    table.wealth-table tr.year-5-row {{
      background: #FFF7ED;
      font-weight: 800;
    }}
    .wealth-pos {{
      color: var(--sage-green);
      font-weight: 800;
    }}
    .rent-neg {{
      color: var(--terracotta);
    }}

    /* Audio Guide Bar */
    .audio-guide-box {{
      background: var(--paper-tint);
      border: 1px solid #D6D3D1;
      border-radius: 10px;
      padding: 16px 18px;
      margin-top: 16px;
      font-family: 'Plus Jakarta Sans', sans-serif;
    }}
    .ai-editorial-output {{
      background: var(--paper-card);
      border: 1px solid #D6D3D1;
      border-left: 4px solid var(--terracotta);
      border-radius: 8px;
      padding: 16px 18px;
      margin-top: 18px;
      font-family: 'Plus Jakarta Sans', sans-serif;
      font-size: 13px;
      white-space: pre-wrap;
      line-height: 1.6;
    }}
  </style>
</head>
<body>

  <!-- Top Editorial Utility Bar -->
  <header class="editorial-topbar">
    <div class="editorial-topbar-inner">
      <div class="edition-meta">
        <span class="terracotta-tag">Architectural &amp; Living Guide</span>
        <span>Metro Detroit &amp; Oakland County First-Time Buyer Issue</span>
        <span>Redfin &times; Rocket Mortgage Editorial Desk</span>
      </div>

      <div class="topbar-controls">
        <div class="model-select-pill">
          <span>Editorial AI:</span>
          <select id="app-model-select" onchange="window.syncSelectedModel(this.value)">
            <option value="gemini-4-argon">Gemini 4 Argon (Frontier)</option>
            <option value="gemini-3.8-flash">Gemini 3.8 Flash (Fast)</option>
          </select>
        </div>
        <button class="btn-terracotta" onclick="window.runLiveVertexAI()">
          Generate Custom Neighborhood Dossier
        </button>
      </div>
    </div>
  </header>

  <!-- Magazine Masthead -->
  <section class="magazine-header">
    <div class="magazine-kicker">The Michigan Architecture &amp; Homeownership Quarterly</div>
    <h1 class="magazine-headline">Where First-Time Buyers Are Putting Down Roots in Metro Detroit</h1>
    <p class="magazine-deck">
      An interactive architectural field guide to Royal Oak, Ferndale, Corktown Detroit, and Dearborn—pairing MSHDA $10,000 &amp; Detroit $25,000 down payment grants with five-year equity forecasts.
    </p>
  </section>

  <main class="editorial-main">
    <!-- Interactive 4-Neighborhood Selector -->
    <div class="neighborhood-strip-label">
      <span>Select a Metro Detroit Neighborhood to Explore Architecture, Grants &amp; 5-Year Wealth Math</span>
      <span id="active-hood-pill" style="color:var(--ink);">Active Feature: Royal Oak 48067</span>
    </div>

    <section class="neighborhood-tabs">
      <div class="hood-card active" id="hood-royaloak" onclick="window.selectNeighborhood('royaloak')">
        <div class="hood-name">Royal Oak</div>
        <div class="hood-zip">ZIP 48067 · Vinsetta Park &amp; Downtown</div>
        <div class="hood-stats">
          <span>Median: <strong>$365,000</strong></span>
          <span>Walk Score: <strong>84</strong></span>
        </div>
      </div>

      <div class="hood-card" id="hood-ferndale" onclick="window.selectNeighborhood('ferndale')">
        <div class="hood-name">Ferndale</div>
        <div class="hood-zip">ZIP 48220 · Nine Mile &amp; Livernois Corridor</div>
        <div class="hood-stats">
          <span>Median: <strong>$315,000</strong></span>
          <span>Walk Score: <strong>86</strong></span>
        </div>
      </div>

      <div class="hood-card" id="hood-corktown" onclick="window.selectNeighborhood('corktown')">
        <div class="hood-name">Corktown Detroit</div>
        <div class="hood-zip">ZIP 48216 · Michigan Central &amp; Historic Row</div>
        <div class="hood-stats">
          <span>Median: <strong>$295,000</strong></span>
          <span>Detroit Grant: <strong>$25,000</strong></span>
        </div>
      </div>

      <div class="hood-card" id="hood-dearborn" onclick="window.selectNeighborhood('dearborn')">
        <div class="hood-name">West Dearborn</div>
        <div class="hood-zip">ZIP 48124 · Morley &amp; Cherry Hill Historic</div>
        <div class="hood-stats">
          <span>Median: <strong>$285,000</strong></span>
          <span>Walk Score: <strong>79</strong></span>
        </div>
      </div>
    </section>

    <!-- Main Editorial Columns -->
    <div class="editorial-grid">
      <!-- Left Column: Magazine Architectural Essay + Rent-vs-Buy 5-Year Wealth Table -->
      <div>
        <article class="article-card">
          <div class="article-kicker" id="essay-kicker">Neighborhood Architectural Profile · Royal Oak 48067</div>
          <h2 class="article-title" id="essay-title">
            Tree-Lined 1920s Craftsman Bungalows &amp; Farmers Market Weekends in Royal Oak
          </h2>
          <p class="article-prose dropcap" id="essay-p1">
            Along the maple-shaded avenues of Vinsetta Park and Knowles Street, 1920s brick Craftsman bungalows and Tudor cottages offer first-time buyers something increasingly rare: authentic hardwood millwork, deep front porches, and a ten-minute stroll to the Saturday Royal Oak Farmers Market.
          </p>
          <p class="article-prose" id="essay-p2">
            While luxury infill colonials trade above $650,000, well-preserved three-bedroom bungalows between Eleven Mile and Twelve Mile Road regularly close between $340,000 and $375,000—qualifying directly for Michigan's MSHDA MI Home Loan $10,000 Down Payment Assistance program.
          </p>

          <div class="arch-callout-grid">
            <div>
              <div class="arch-stat-lbl">Signature Style</div>
              <div class="arch-stat-val" id="arch-style-val">1926 Brick Craftsman</div>
            </div>
            <div>
              <div class="arch-stat-lbl">5-Yr Appreciation</div>
              <div class="arch-stat-val" id="arch-appr-val">+4.6% / yr Projected</div>
            </div>
            <div>
              <div class="arch-stat-lbl">Avg 2-Bed Rent</div>
              <div class="arch-stat-val" id="arch-rent-val">$2,240 / month</div>
            </div>
          </div>

          <!-- Audio Guide Button (Gemini 3.8 Live · Aoede HD) -->
          <div class="audio-guide-box">
            <div style="display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap;margin-bottom:8px;">
              <div>
                <div style="font-size:13.5px;font-weight:800;color:var(--ink);">
                  Curated Neighborhood Audio Essay (Synced to Selected ZIP &amp; Grants)
                </div>
                <div style="font-size:11.5px;color:var(--ink-muted);">
                  Narrated in 24kHz HD via Gemini 3.8 Live · Voice: Aoede HD
                </div>
              </div>
              <button class="btn-terracotta" id="btn-audio-guide" onclick="window.playNeighborhoodAudioGuide(this)">
                🔊 Listen to Neighborhood Audio Guide (Gemini 3.8 Live · Aoede HD)
              </button>
            </div>
            <div id="audio-guide-script" style="font-size:12.5px;color:var(--ink-body);background:#FFFFFF;padding:10px 12px;border-radius:6px;border:1px solid #E7E5E4;">
              "Welcome to Royal Oak 48067. Famous for its 1920s brick Craftsman bungalows and walkable downtown farmers market, Royal Oak has a starter median price of $365,000. By pairing the $10,000 MSHDA down payment assistance grant with a $5,000 Rocket first-generation credit, your out-of-pocket cash to close drops to just $4,528—building $84,900 in net home equity over the next five years."
            </div>
          </div>
        </article>

        <!-- Rent-vs-Buy 5-Year Wealth Comparison Table -->
        <div class="article-card">
          <div class="article-kicker">Five-Year Financial Ledger</div>
          <h3 class="display-serif" style="font-size:22px;color:var(--ink);margin-bottom:4px;">
            Rent-vs-Buy 5-Year Wealth Comparison (<span id="table-hood-label">Royal Oak 48067</span>)
          </h3>
          <p class="sans" style="font-size:12.5px;color:var(--ink-muted);margin-bottom:10px;">
            Compares signing a lease at <span id="table-rent-lbl">$2,240/mo</span> (with 4% annual rent hikes) against owning a <span id="table-price-lbl">$365,000</span> home with Rocket Mortgage + Down Payment Grants.
          </p>

          <div class="wealth-table-wrap">
            <table class="wealth-table">
              <thead>
                <tr>
                  <th>Timeline</th>
                  <th>Cumulative Rent Paid (0% Equity)</th>
                  <th>Home Value (4.6% Appr.)</th>
                  <th>Principal Paid + Grant Equity</th>
                  <th>Total Homeowner Net Equity</th>
                </tr>
              </thead>
              <tbody id="wealth-table-body"></tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Right Column: Interactive MSHDA $10,000 + Detroit $25,000 Grant Calculator -->
      <div>
        <div class="grant-calc-card">
          <div class="article-kicker">Interactive Michigan Down Payment Stacker</div>
          <h3 class="display-serif" style="font-size:23px;color:var(--ink);margin-bottom:6px;">
            MSHDA $10,000 DPA + Detroit $25,000 Grant Calculator
          </h3>
          <p style="font-size:12.5px;color:var(--ink-muted);margin-bottom:16px;">
            Stack eligible Michigan state, municipal, and Rocket Mortgage assistance programs to calculate your exact cash-to-close.
          </p>

          <!-- Price Slider -->
          <div style="background:var(--paper-tint);padding:14px;border-radius:8px;margin-bottom:14px;">
            <div style="display:flex;justify-content:space-between;font-size:12.5px;font-weight:700;margin-bottom:6px;">
              <span>Target Starter Home Purchase Price</span>
              <span style="color:var(--terracotta);font-weight:800;" id="calc-price-display">$365,000</span>
            </div>
            <input type="range" id="calc-price-slider" min="220000" max="520000" step="5000" value="365000" style="width:100%;accent-color:var(--terracotta);cursor:pointer;" oninput="window.recalculateGrantsAndWealth()">
          </div>

          <!-- Grant 1: MSHDA $10,000 -->
          <div class="grant-option checked" id="grant-mshda" onclick="window.toggleGrantOption('grant-mshda')">
            <div class="grant-check-left">
              <input type="checkbox" class="grant-checkbox" checked onclick="event.stopPropagation();window.toggleGrantOption('grant-mshda')">
              <div>
                <div style="font-size:13.5px;font-weight:800;color:var(--ink);">MSHDA MI Home Loan Down Payment Assistance</div>
                <div style="font-size:11.5px;color:var(--ink-muted);">Statewide 0% interest, non-amortizing subordinate assistance up to $10,000</div>
              </div>
            </div>
            <span class="grant-amount-pill">-$10,000</span>
          </div>

          <!-- Grant 2: Detroit $25,000 -->
          <div class="grant-option" id="grant-detroit" onclick="window.toggleGrantOption('grant-detroit')">
            <div class="grant-check-left">
              <input type="checkbox" class="grant-checkbox" onclick="event.stopPropagation();window.toggleGrantOption('grant-detroit')">
              <div>
                <div style="font-size:13.5px;font-weight:800;color:var(--ink);">Detroit Down Payment Assistance Program (DPA)</div>
                <div style="font-size:11.5px;color:var(--ink-muted);">Up to $25,000 forgivable grant for eligible Detroit ZIPs (e.g. Corktown 48216)</div>
              </div>
            </div>
            <span class="grant-amount-pill">-$25,000</span>
          </div>

          <!-- Grant 3: Rocket ONE+ / Community Credit $5,000 -->
          <div class="grant-option checked" id="grant-rocket" onclick="window.toggleGrantOption('grant-rocket')">
            <div class="grant-check-left">
              <input type="checkbox" class="grant-checkbox" checked onclick="event.stopPropagation();window.toggleGrantOption('grant-rocket')">
              <div>
                <div style="font-size:13.5px;font-weight:800;color:var(--ink);">Rocket Purchase Plus / First-Time Buyer Credit</div>
                <div style="font-size:11.5px;color:var(--ink-muted);">Closing cost &amp; mortgage insurance grant credit on qualifying census tracts</div>
              </div>
            </div>
            <span class="grant-amount-pill">-$5,000</span>
          </div>

          <!-- Cash to Close Breakdown -->
          <div class="cash-to-close-summary">
            <div>
              <div style="font-size:11px;font-weight:700;color:var(--ink-muted);text-transform:uppercase;">Gross Down (3.5%) + Closing</div>
              <div style="font-size:18px;font-weight:800;color:var(--ink);margin-top:3px;" id="gross-cash-needed">$19,528</div>
            </div>
            <div>
              <div style="font-size:11px;font-weight:700;color:var(--ink-muted);text-transform:uppercase;">Total Stacked Grants</div>
              <div style="font-size:18px;font-weight:800;color:var(--sage-green);margin-top:3px;" id="total-grants-applied">-$15,000</div>
            </div>
            <div>
              <div style="font-size:11px;font-weight:700;color:var(--terracotta);text-transform:uppercase;">Net Buyer Cash to Close</div>
              <div style="font-size:21px;font-weight:800;color:var(--terracotta);margin-top:2px;" id="net-cash-to-close">$4,528</div>
            </div>
          </div>

          <!-- Live Vertex AI Output -->
          <div class="ai-editorial-output" id="vertex-ai-output">
            <strong>First-Time Buyer Editorial Desk Ready:</strong> Select any neighborhood above or click <em>"Generate Custom Neighborhood Dossier"</em> to synthesize a hyper-local block-by-block buying guide and MSHDA eligibility checklist with <span id="live-model-pill">gemini-4-argon</span>.
          </div>
        </div>
      </div>
    </div>
  </main>

  <script>
    const HOOD_DATA = {{
      royaloak: {{
        name: "Royal Oak 48067",
        kicker: "Neighborhood Architectural Profile · Royal Oak 48067",
        title: "Tree-Lined 1920s Craftsman Bungalows & Farmers Market Weekends in Royal Oak",
        p1: "Along the maple-shaded avenues of Vinsetta Park and Knowles Street, 1920s brick Craftsman bungalows and Tudor cottages offer first-time buyers something increasingly rare: authentic hardwood millwork, deep front porches, and a ten-minute stroll to the Saturday Royal Oak Farmers Market.",
        p2: "While luxury infill colonials trade above $650,000, well-preserved three-bedroom bungalows between Eleven Mile and Twelve Mile Road regularly close between $340,000 and $375,000—qualifying directly for Michigan's MSHDA MI Home Loan $10,000 Down Payment Assistance program.",
        style: "1926 Brick Craftsman",
        apprRate: 0.046,
        rent: 2240,
        price: 365000,
        detroitEligible: false
      }},
      ferndale: {{
        name: "Ferndale 48220",
        kicker: "Neighborhood Architectural Profile · Ferndale 48220",
        title: "Walkable Arts District Bungalows & Mid-Century Ranch Homes Along Nine Mile",
        p1: "Just north of Eight Mile along the tree-canopied streets of Drayton, Pinecrest, and Saratoga, Ferndale blends independent coffee roasters and record shops with charming 1930s bungalows and fenced backyard studios.",
        p2: "With a starter median price around $315,000, first-time buyers pairing MSHDA's $10,000 assistance with Rocket's $5,000 Purchase Plus credit can step from a $2,050/month apartment into full homeownership with less than $2,200 out of pocket.",
        style: "1938 Arts & Crafts Bungalow",
        apprRate: 0.048,
        rent: 2050,
        price: 315000,
        detroitEligible: false
      }},
      corktown: {{
        name: "Corktown Detroit 48216",
        kicker: "Neighborhood Architectural Profile · Corktown Detroit 48216",
        title: "Victorian Workers' Cottages & Brick Lofts Shadowing Michigan Central Station",
        p1: "Detroit's oldest surviving neighborhood is experiencing an architectural renaissance anchored by the restored Michigan Central innovation campus, Roosevelt Park, and Michigan Avenue's acclaimed dining corridor.",
        p2: "Qualifying Corktown buyers can combine the $25,000 Detroit Down Payment Assistance Grant with Rocket's $5,000 closing credit—covering virtually 100% of down payment and closing costs on a $295,000 historic brick townhome or loft.",
        style: "1895 Victorian Row Cottage",
        apprRate: 0.054,
        rent: 2150,
        price: 295000,
        detroitEligible: true
      }},
      dearborn: {{
        name: "West Dearborn 48124",
        kicker: "Neighborhood Architectural Profile · West Dearborn 48124",
        title: "Classic Red-Brick Colonials, River Rouge Trails & Vibrant Michigan Ave Cafés",
        p1: "West Dearborn's Morley and Cherry Hill neighborhoods are celebrated for solid 1940s red-brick colonials, slate-style rooflines, and walkable access to artisanal Yemeni coffee houses, bakeries, and Ford Field Park.",
        p2: "At a median starter price of $285,000, stacking the $10,000 MSHDA MI Home Loan DPA with Rocket's $5,000 credit leaves first-time buyers needing just $528 in net cash at the closing table.",
        style: "1942 Red-Brick Colonial",
        apprRate: 0.044,
        rent: 1980,
        price: 285000,
        detroitEligible: false
      }}
    }};

    let activeHoodKey = 'royaloak';

    window.selectNeighborhood = function(key) {{
      activeHoodKey = key;
      const h = HOOD_DATA[key] || HOOD_DATA.royaloak;
      ['royaloak', 'ferndale', 'corktown', 'dearborn'].forEach(k => {{
        const el = document.getElementById('hood-' + k);
        if (el) el.classList.toggle('active', k === key);
      }});

      document.getElementById('active-hood-pill').textContent = 'Active Feature: ' + h.name;
      document.getElementById('essay-kicker').textContent = h.kicker;
      document.getElementById('essay-title').textContent = h.title;
      document.getElementById('essay-p1').textContent = h.p1;
      document.getElementById('essay-p2').textContent = h.p2;
      document.getElementById('arch-style-val').textContent = h.style;
      document.getElementById('arch-appr-val').textContent = '+' + (h.apprRate * 100).toFixed(1) + '% / yr Projected';
      document.getElementById('arch-rent-val').textContent = '$' + h.rent.toLocaleString() + ' / month';

      document.getElementById('calc-price-slider').value = h.price;

      // Auto-toggle Detroit $25K grant if Corktown selected
      const detroitEl = document.getElementById('grant-detroit');
      if (detroitEl) {{
        detroitEl.classList.toggle('checked', h.detroitEligible);
        const cb = detroitEl.querySelector('input[type="checkbox"]');
        if (cb) cb.checked = h.detroitEligible;
      }}

      window.recalculateGrantsAndWealth();
    }};

    window.toggleGrantOption = function(id) {{
      const el = document.getElementById(id);
      if (!el) return;
      el.classList.toggle('checked');
      const cb = el.querySelector('input[type="checkbox"]');
      if (cb) cb.checked = el.classList.contains('checked');
      window.recalculateGrantsAndWealth();
    }};

    window.recalculateGrantsAndWealth = function() {{
      const h = HOOD_DATA[activeHoodKey] || HOOD_DATA.royaloak;
      const price = parseInt(document.getElementById('calc-price-slider').value || h.price, 10);
      document.getElementById('calc-price-display').textContent = '$' + price.toLocaleString();

      const grossDown = Math.round(price * 0.035);
      const estClosing = Math.round(price * 0.0185);
      const grossCash = grossDown + estClosing;

      let totalGrants = 0;
      if (document.getElementById('grant-mshda').classList.contains('checked')) totalGrants += 10000;
      if (document.getElementById('grant-detroit').classList.contains('checked')) totalGrants += 25000;
      if (document.getElementById('grant-rocket').classList.contains('checked')) totalGrants += 5000;

      const netCash = Math.max(500, grossCash - totalGrants);

      document.getElementById('gross-cash-needed').textContent = '$' + grossCash.toLocaleString();
      document.getElementById('total-grants-applied').textContent = '-$' + totalGrants.toLocaleString();
      document.getElementById('net-cash-to-close').textContent = '$' + netCash.toLocaleString();

      document.getElementById('table-hood-label').textContent = h.name;
      document.getElementById('table-rent-lbl').textContent = '$' + h.rent.toLocaleString() + '/mo';
      document.getElementById('table-price-lbl').textContent = '$' + price.toLocaleString();

      // Build 5-Year Rent vs Buy Wealth Table
      const tbody = document.getElementById('wealth-table-body');
      let rowsHtml = '';
      let cumRent = 0;
      let monthlyRent = h.rent;
      let fiveYrEquity = 0;

      for (let yr = 1; yr <= 5; yr++) {{
        cumRent += Math.round(monthlyRent * 12);
        monthlyRent = monthlyRent * 1.04;

        const homeVal = Math.round(price * Math.pow(1 + h.apprRate, yr));
        const principalPaid = Math.round(price * 0.0135 * yr);
        const totalEquity = (homeVal - price) + grossDown + principalPaid + Math.min(totalGrants, 15000);
        if (yr === 5) fiveYrEquity = totalEquity;

        const rowCls = yr === 5 ? ' class="year-5-row"' : '';
        rowsHtml += '<tr' + rowCls + '>' +
          '<td>Year ' + yr + (yr === 5 ? ' (5-Yr Milestone)' : '') + '</td>' +
          '<td class="rent-neg">-$' + cumRent.toLocaleString() + '</td>' +
          '<td>$' + homeVal.toLocaleString() + '</td>' +
          '<td>$' + (principalPaid + grossDown).toLocaleString() + '</td>' +
          '<td class="wealth-pos">+$' + totalEquity.toLocaleString() + '</td>' +
        '</tr>';
      }}
      if (tbody) tbody.innerHTML = rowsHtml;

      const audioScript = document.getElementById('audio-guide-script');
      if (audioScript) {{
        audioScript.textContent =
          '"Welcome to ' + h.name + '. Featuring ' + h.style + ' architecture and a target starter price of $' + price.toLocaleString() +
          ', stacking $' + totalGrants.toLocaleString() + ' in Michigan and Rocket down payment grants brings your estimated cash to close down to just $' +
          netCash.toLocaleString() + '—while building an estimated $' + fiveYrEquity.toLocaleString() + ' in homeowner equity over five years."';
      }}
    }};

    window.playNeighborhoodAudioGuide = function(btnEl) {{
      const scriptEl = document.getElementById('audio-guide-script');
      const text = scriptEl ? scriptEl.textContent.replace(/^"|"$/g, '') : "Welcome to the Metro Detroit First-Time Homebuyer Guide.";
      window.playLiveCallClip(
        text,
        "Aoede",
        "NYT Real Estate & Rocket Neighborhood Guide",
        btnEl
      );
    }};

    window.runLiveVertexAI = async function() {{
      const model = window.getSelectedModel ? window.getSelectedModel() : "gemini-4-argon";
      const outEl = document.getElementById('vertex-ai-output');
      const h = HOOD_DATA[activeHoodKey] || HOOD_DATA.royaloak;
      const price = document.getElementById('calc-price-display').textContent;
      const grants = document.getElementById('total-grants-applied').textContent;
      const netCash = document.getElementById('net-cash-to-close').textContent;
      const drawerInput = document.getElementById('scenario-input');
      const scenarioText = (drawerInput && drawerInput.value.trim())
        ? drawerInput.value.trim() + " | Neighborhood: " + h.name + ", Price: " + price + ", Grants: " + grants + ", Net Cash: " + netCash
        : "Write an editorial New York Times Real Estate & Dwell style first-time buyer guide for " + h.name + " at a purchase price of " + price + " utilizing " + grants + " in MSHDA/Detroit down payment assistance (Net Cash to Close: " + netCash + ").";

      if (outEl) {{
        outEl.innerHTML = "<strong>⏳ Composing Hyper-Local First-Time Buyer Editorial Dossier via Vertex AI (" + model + ")...</strong>";
      }}
      try {{
        const res = await fetch('/api/run-demo', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{
            square: "4.3",
            model: model,
            scenario: scenarioText
          }})
        }});
        const data = await res.json();
        if (outEl) {{
          outEl.textContent = data.output || data.text || "Editorial dossier complete.";
        }}
      }} catch (err) {{
        if (outEl) {{
          outEl.textContent = "Unable to reach Vertex AI endpoint: " + err.message;
        }}
      }}
    }};

    document.addEventListener('DOMContentLoaded', () => {{
      window.recalculateGrantsAndWealth();
    }});
  </script>

  {floating_drawer}
</body>
</html>"""
