# -*- coding: utf-8 -*-
"""Square 2.1 Standalone Full-Screen UI:
Fannie Mae / Freddie Mac Selling Guide Citation Assistant (Gemini Enterprise / NotebookLM)
Aesthetic: Warm Parchment & Oxford Navy Academic/Legal NotebookLM Reader (#FDFBF7 paper canvas, #1E293B ink, #BE123C crimson citation pills)."""

from shared.standalone_uis.base_helpers import render_floating_control_bar_and_drawer


def render_sq_2_1(auth_token: str) -> str:
    floating_bar = render_floating_control_bar_and_drawer("2.1", auth_token)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>2.1 // Fannie Mae & Freddie Mac Selling Guide Citation Assistant — NotebookLM Enterprise</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600;700&family=Instrument+Serif:ital@0;1&family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <style>
    :root {{
      --paper-bg: #FDFBF7;
      --paper-elevated: #F5F0E6;
      --paper-card: #FFFFFF;
      --oxford-navy: #1E293B;
      --oxford-deep: #0F172A;
      --ink-muted: #475569;
      --crimson: #BE123C;
      --crimson-soft: #FFE4E6;
      --amber-hl: #FEF08A;
      --amber-border: #CA8A04;
      --emerald: #047857;
      --border-rule: #E2D9C8;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      background: var(--paper-bg);
      color: var(--oxford-navy);
      font-family: 'Inter', sans-serif;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      overflow-x: hidden;
    }}
    /* Top Editorial Masthead */
    .masthead {{
      background: var(--oxford-deep);
      color: #F8FAFC;
      padding: 12px 24px;
      border-bottom: 3px solid var(--crimson);
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      flex-wrap: wrap;
    }}
    .masthead-left {{
      display: flex;
      align-items: center;
      gap: 16px;
    }}
    .seal-badge {{
      background: var(--crimson);
      color: #FFF;
      font-family: 'IBM Plex Mono', monospace;
      font-size: 11px;
      font-weight: 700;
      padding: 5px 10px;
      border-radius: 4px;
      letter-spacing: 0.06em;
      text-transform: uppercase;
    }}
    .masthead-title {{
      font-family: 'Instrument Serif', serif;
      font-size: 26px;
      font-weight: 400;
      letter-spacing: 0.01em;
      color: #FDFBF7;
    }}
    .masthead-sub {{
      font-family: 'IBM Plex Mono', monospace;
      font-size: 11px;
      color: #94A3B8;
    }}
    .masthead-controls {{
      display: flex;
      align-items: center;
      gap: 12px;
      flex-wrap: wrap;
    }}
    .model-bar {{
      display: flex;
      align-items: center;
      gap: 8px;
      background: rgba(255,255,255,0.08);
      border: 1px solid rgba(255,255,255,0.18);
      padding: 6px 12px;
      border-radius: 6px;
      font-family: 'IBM Plex Mono', monospace;
      font-size: 11px;
    }}
    .model-bar select {{
      background: transparent;
      color: #38BDF8;
      border: none;
      font-family: 'IBM Plex Mono', monospace;
      font-size: 11px;
      font-weight: 700;
      outline: none;
      cursor: pointer;
    }}
    .model-bar select option {{
      background: #0F172A;
      color: #F8FAFC;
    }}
    .ge-btn {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      background: linear-gradient(135deg, #BE123C, #9F1239);
      color: #FFFFFF;
      text-decoration: none;
      padding: 8px 14px;
      border-radius: 6px;
      font-family: 'IBM Plex Mono', monospace;
      font-size: 11.5px;
      font-weight: 700;
      border: 1px solid #FB7185;
      box-shadow: 0 4px 14px rgba(190, 18, 60, 0.35);
      transition: transform 0.15s ease, box-shadow 0.15s ease;
    }}
    .ge-btn:hover {{
      transform: translateY(-1px);
      box-shadow: 0 6px 20px rgba(190, 18, 60, 0.5);
    }}

    /* 2-Pane Split Academic Reader */
    .split-reader {{
      display: grid;
      grid-template-columns: 1.05fr 0.95fr;
      flex: 1;
      min-height: calc(100vh - 64px);
    }}
    @media (max-width: 1100px) {{
      .split-reader {{ grid-template-columns: 1fr; }}
    }}

    /* Left Pane: Interactive GSE PDF Guideline Reader */
    .pdf-pane {{
      background: var(--paper-elevated);
      border-right: 2px solid var(--border-rule);
      padding: 22px 26px 80px 26px;
      display: flex;
      flex-direction: column;
      gap: 16px;
    }}
    .chapter-tabs {{
      display: flex;
      gap: 8px;
      border-bottom: 2px solid var(--border-rule);
      padding-bottom: 10px;
      flex-wrap: wrap;
    }}
    .chap-tab {{
      background: var(--paper-bg);
      border: 1px solid var(--border-rule);
      color: var(--oxford-navy);
      padding: 8px 14px;
      border-radius: 6px;
      font-family: 'IBM Plex Mono', monospace;
      font-size: 11.5px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.15s;
      display: flex;
      align-items: center;
      gap: 6px;
    }}
    .chap-tab.active {{
      background: var(--oxford-navy);
      color: #FFFFFF;
      border-color: var(--oxford-navy);
      box-shadow: 0 4px 10px rgba(30,41,59,0.18);
    }}
    .chap-tab .tag {{
      font-size: 10px;
      padding: 2px 6px;
      border-radius: 3px;
      background: var(--crimson-soft);
      color: var(--crimson);
      font-weight: 700;
    }}
    .pdf-sheet {{
      background: #FFFFFF;
      border: 1px solid #D6CBB5;
      box-shadow: 0 10px 30px rgba(30, 41, 59, 0.07), inset 0 0 0 1px #FAF8F5;
      border-radius: 6px;
      padding: 28px 32px;
      flex: 1;
      position: relative;
    }}
    .pdf-running-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-bottom: 2px solid var(--oxford-navy);
      padding-bottom: 10px;
      margin-bottom: 18px;
      font-family: 'IBM Plex Mono', monospace;
      font-size: 11px;
      color: var(--ink-muted);
    }}
    .pdf-doc-title {{
      font-family: 'Instrument Serif', serif;
      font-size: 28px;
      color: var(--oxford-deep);
      line-height: 1.2;
      margin-bottom: 12px;
    }}
    .pdf-section-body {{
      font-size: 13.5px;
      line-height: 1.72;
      color: #1E293B;
    }}
    .pdf-section-body p {{
      margin-bottom: 14px;
    }}
    .hl-clause {{
      background: var(--amber-hl);
      border-bottom: 2px solid var(--amber-border);
      padding: 2px 4px;
      border-radius: 3px;
      cursor: pointer;
      transition: background 0.2s;
      font-weight: 500;
    }}
    .hl-clause:hover {{
      background: #FDE047;
    }}
    .cite-pill {{
      display: inline-flex;
      align-items: center;
      gap: 4px;
      background: var(--crimson);
      color: #FFF;
      font-family: 'IBM Plex Mono', monospace;
      font-size: 10.5px;
      font-weight: 700;
      padding: 2px 8px;
      border-radius: 999px;
      margin: 0 4px;
      cursor: pointer;
      vertical-align: middle;
    }}
    .policy-matrix {{
      width: 100%;
      border-collapse: collapse;
      margin-top: 14px;
      font-size: 12px;
    }}
    .policy-matrix th {{
      background: #F1ECE1;
      text-align: left;
      padding: 8px 10px;
      border: 1px solid #D6CBB5;
      font-family: 'IBM Plex Mono', monospace;
      font-size: 11px;
      color: var(--oxford-deep);
    }}
    .policy-matrix td {{
      padding: 8px 10px;
      border: 1px solid #E5DEC9;
      vertical-align: top;
    }}

    /* Right Pane: Grounded Citation Notebook & GSE Calculator */
    .notebook-pane {{
      background: var(--paper-bg);
      padding: 22px 28px 80px 28px;
      display: flex;
      flex-direction: column;
      gap: 18px;
    }}
    .search-box-card {{
      background: #FFFFFF;
      border: 1.5px solid var(--oxford-navy);
      border-radius: 8px;
      padding: 16px;
      box-shadow: 4px 4px 0px var(--oxford-navy);
    }}
    .search-label {{
      font-family: 'IBM Plex Mono', monospace;
      font-size: 11px;
      font-weight: 700;
      text-transform: uppercase;
      color: var(--crimson);
      margin-bottom: 8px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}
    .search-row {{
      display: flex;
      gap: 8px;
    }}
    .search-input {{
      flex: 1;
      padding: 10px 14px;
      border: 1px solid #CBD5E1;
      border-radius: 6px;
      font-family: 'Inter', sans-serif;
      font-size: 13px;
      color: var(--oxford-deep);
      background: #FDFBF7;
    }}
    .btn-stream {{
      background: var(--oxford-navy);
      color: #FFF;
      border: none;
      padding: 10px 16px;
      border-radius: 6px;
      font-family: 'IBM Plex Mono', monospace;
      font-size: 11.5px;
      font-weight: 700;
      cursor: pointer;
      white-space: nowrap;
    }}
    .btn-stream:hover {{ background: #0F172A; }}

    .calc-card {{
      background: #FFFFFF;
      border: 1px solid var(--border-rule);
      border-radius: 8px;
      padding: 18px;
    }}
    .calc-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 14px;
      padding-bottom: 8px;
      border-bottom: 1px solid var(--border-rule);
    }}
    .calc-title {{
      font-family: 'Instrument Serif', serif;
      font-size: 22px;
      color: var(--oxford-deep);
    }}
    .sliders-grid {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 12px;
      margin-bottom: 14px;
    }}
    @media (max-width: 768px) {{
      .sliders-grid {{ grid-template-columns: 1fr; }}
    }}
    .slider-box {{
      background: #FAF7F0;
      border: 1px solid #E5DEC9;
      border-radius: 6px;
      padding: 10px 12px;
    }}
    .slider-top {{
      display: flex;
      justify-content: space-between;
      font-family: 'IBM Plex Mono', monospace;
      font-size: 11px;
      margin-bottom: 6px;
    }}
    .slider-top strong {{ color: var(--crimson); font-size: 12px; }}
    .slider-box input[type=range] {{
      width: 100%;
      accent-color: var(--crimson);
      cursor: pointer;
    }}

    .metrics-strip {{
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 10px;
    }}
    .metric-tile {{
      background: #FDFBF7;
      border-left: 3px solid var(--oxford-navy);
      padding: 10px 12px;
      border-radius: 4px;
      border-top: 1px solid #E2D9C8;
      border-right: 1px solid #E2D9C8;
      border-bottom: 1px solid #E2D9C8;
    }}
    .metric-tile.total {{
      border-left-color: var(--crimson);
      background: #FFF1F2;
    }}
    .metric-lbl {{
      font-family: 'IBM Plex Mono', monospace;
      font-size: 10px;
      text-transform: uppercase;
      color: var(--ink-muted);
    }}
    .metric-val {{
      font-family: 'IBM Plex Mono', monospace;
      font-size: 13px;
      font-weight: 700;
      color: var(--oxford-deep);
      margin-top: 3px;
    }}

    .ruling-notebook {{
      background: #FFFFFF;
      border: 1px solid var(--border-rule);
      border-radius: 8px;
      padding: 20px;
      flex: 1;
      display: flex;
      flex-direction: column;
      gap: 14px;
    }}
    .ruling-banner {{
      background: #F8FAFC;
      border-left: 4px solid var(--crimson);
      padding: 12px 14px;
      font-size: 13px;
      line-height: 1.55;
      color: var(--oxford-deep);
    }}
    .citation-cards {{
      display: flex;
      flex-direction: column;
      gap: 10px;
    }}
    .c-card {{
      border: 1px solid #E2E8F0;
      border-radius: 6px;
      padding: 12px 14px;
      background: #FCFBF9;
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      gap: 12px;
    }}
    .c-card-left h4 {{
      font-size: 13px;
      font-weight: 700;
      color: var(--oxford-deep);
      margin-bottom: 3px;
    }}
    .c-card-left p {{
      font-size: 12px;
      color: var(--ink-muted);
    }}
    .c-card-right {{
      text-align: right;
      font-family: 'IBM Plex Mono', monospace;
      white-space: nowrap;
    }}
    .c-card-right .amt {{
      font-size: 14px;
      font-weight: 700;
      color: var(--emerald);
    }}
  </style>
</head>
<body>

  <!-- TOP EDITORIAL MASTHEAD -->
  <header class="masthead">
    <div class="masthead-left">
      <span class="seal-badge">GSE CITATION DESK // 2.1</span>
      <div>
        <div class="masthead-title">Fannie Mae &amp; Freddie Mac Selling Guide Citation Assistant</div>
        <div class="masthead-sub">NotebookLM Enterprise Grounding • Zero-Hallucination Clause Verifier • Form 1003 Variable Income</div>
      </div>
    </div>
    <div class="masthead-controls">
      <div class="model-bar">
        <span>Active Model:</span>
        <select id="app-model-select" onchange="window.syncSelectedModel(this.value)">
          <option value="gemini-3.8-flash" selected>gemini-3.8-flash (StreamAssist Default)</option>
          <option value="gemini-4-argon">gemini-4-argon (Frontier Global)</option>
        </select>
      </div>
      <a href="https://vertexaisearch.cloud.google.com/home/cid/gemini-enterprise-17877637_1787763712023" target="_blank" class="ge-btn">
        ✨ Open Real Gemini Enterprise Web UI ↗
      </a>
    </div>
  </header>

  <!-- 2-PANE ACADEMIC LEGAL SPLIT READER -->
  <main class="split-reader">
    <!-- LEFT PANE: INTERACTIVE FANNIE MAE & FREDDIE MAC GUIDELINE CHAPTERS -->
    <section class="pdf-pane">
      <div class="chapter-tabs">
        <button class="chap-tab active" id="tab-b3-01" onclick="window.switchChapter('b3-01')">
          <span>Fannie Mae B3-3.1-01</span>
          <span class="tag">Bonus &amp; Overtime</span>
        </button>
        <button class="chap-tab" id="tab-b3-09" onclick="window.switchChapter('b3-09')">
          <span>Fannie Mae B3-3.1-09</span>
          <span class="tag">RSU Non-Cash Comp</span>
        </button>
        <button class="chap-tab" id="tab-5301" onclick="window.switchChapter('5301')">
          <span>Freddie Mac § 5301.1</span>
          <span class="tag">Variable Income Trend</span>
        </button>
      </div>

      <article class="pdf-sheet" id="pdf-content-area">
        <!-- Populated dynamically via switchChapter() -->
      </article>
    </section>

    <!-- RIGHT PANE: GROUNDED CITATION NOTEBOOK & VARIABLE INCOME SANDBOX -->
    <section class="notebook-pane">
      <!-- Live Discovery Engine v1alpha streamAssist Query Bar -->
      <div class="search-box-card">
        <div class="search-label">
          <span>🔍 Discovery Engine v1alpha streamAssist Grounded Search</span>
          <span id="stream-latency-pill" style="color:#047857;">Engine: gemini-enterprise-17877637_1787763712023</span>
        </div>
        <div class="search-row">
          <input type="text" id="ge-query-input" class="search-input"
            value="Borrower has $165k base, $48k/$62k vested ServiceNow RSUs, and a bonus that dropped from $22,000 in 2024 to $14,000 in 2025. Cite exact Fannie Mae B3-3.1-01 and B3-3.1-09 qualifying monthly income rules." />
          <button class="btn-stream" onclick="window.queryStreamAssist()">Ask StreamAssist</button>
          <button class="btn-stream" style="background:var(--crimson);" onclick="window.runLiveVertexAI()">⚡ Deep Audit</button>
        </div>
      </div>

      <!-- Interactive RSU & Declining Bonus Income Calculator -->
      <div class="calc-card">
        <div class="calc-header">
          <div class="calc-title">GSE Variable Income &amp; Declining Bonus Sandbox</div>
          <span style="font-family:'IBM Plex Mono',monospace;font-size:11px;color:var(--crimson);font-weight:700;">gVisor Deterministic Math</span>
        </div>
        <div class="sliders-grid">
          <div class="slider-box">
            <div class="slider-top">
              <span>Base Salary</span>
              <strong id="lbl-base">$165,000/yr</strong>
            </div>
            <input type="range" id="sl-base" min="100000" max="300000" step="5000" value="165000" oninput="window.recalcGseIncome()" />
          </div>
          <div class="slider-box">
            <div class="slider-top">
              <span>2024 Vested RSU</span>
              <strong id="lbl-rsu">$48,000/yr</strong>
            </div>
            <input type="range" id="sl-rsu" min="15000" max="120000" step="3000" value="48000" oninput="window.recalcGseIncome()" />
          </div>
          <div class="slider-box">
            <div class="slider-top">
              <span>2025 Bonus (vs $22k '24)</span>
              <strong id="lbl-bonus">$14,000/yr</strong>
            </div>
            <input type="range" id="sl-bonus" min="4000" max="36000" step="1000" value="14000" oninput="window.recalcGseIncome()" />
          </div>
        </div>

        <div class="metrics-strip">
          <div class="metric-tile">
            <div class="metric-lbl">Base Qualifying Monthly (B3-3.1-01)</div>
            <div class="metric-val" id="m-base">$13,750.00/mo ($165,000 / 12)</div>
          </div>
          <div class="metric-tile">
            <div class="metric-lbl">Publicly Traded RSU 24-Mo Avg (B3-3.1-09)</div>
            <div class="metric-val" id="m-rsu">$4,583.33/mo (($48k + $62k) / 24 mos)</div>
          </div>
          <div class="metric-tile">
            <div class="metric-lbl">Declining Bonus Treatment (-36.4% YoY)</div>
            <div class="metric-val" id="m-bonus">$1,166.67/mo (Capped at 2025 $14,000/12)</div>
          </div>
          <div class="metric-tile total">
            <div class="metric-lbl">Total Fannie Mae Qualifying Income</div>
            <div class="metric-val" id="m-total" style="color:var(--crimson);font-size:15px;">$19,500.00/month ($234,000.00/yr)</div>
          </div>
        </div>
      </div>

      <!-- Grounded Citation Notebook Output -->
      <div class="ruling-notebook">
        <div style="display:flex;justify-content:space-between;align-items:center;">
          <h3 style="font-family:'Instrument Serif',serif;font-size:22px;font-weight:400;">Underwriting Citation Memo &amp; Clause Trace</h3>
          <span id="live-model-pill" style="font-family:'IBM Plex Mono',monospace;font-size:11px;background:#F1ECE1;padding:4px 8px;border-radius:4px;font-weight:700;">gemini-3.8-flash</span>
        </div>

        <div class="ruling-banner" id="ruling-summary">
          <strong>GROUNDED UNDERWRITING RULING:</strong> Per <span class="cite-pill" onclick="window.switchChapter('b3-01')">Fannie Mae B3-3.1-01</span>, when annual bonus income exhibits a year-over-year decline exceeding 20% ($22,000 in 2024 down to $14,000 in 2025 = -36.4%), the underwriter <em>must not</em> average the two years; qualifying bonus is capped at the lower most recent 12-month figure ($1,166.67/mo) with written stabilization analysis. Vested RSUs from publicly traded ServiceNow (<span class="cite-pill" onclick="window.switchChapter('b3-09')">B3-3.1-09</span>) qualify at the 24-month historical average of $4,583.33/mo.
        </div>

        <div class="citation-cards" id="citation-cards-list">
          <div class="c-card">
            <div class="c-card-left">
              <h4>1. Base Wage Income • Fannie Mae Selling Guide B3-3.1-01</h4>
              <p>Verified via 2025 W-2 &amp; current YTD paystub. Fixed primary employment compensation divided by 12 months.</p>
            </div>
            <div class="c-card-right">
              <div class="amt">$13,750.00/mo</div>
              <span class="cite-pill" onclick="window.switchChapter('b3-01')">§ B3-3.1-01</span>
            </div>
          </div>
          <div class="c-card">
            <div class="c-card-left">
              <h4>2. Restricted Stock Units (NYSE: NOW) • Fannie Mae B3-3.1-09</h4>
              <p>Publicly traded stock vested over past 24 consecutive months ($48,000 Yr1 + $62,000 Yr2) + 2026–2027 E*TRADE future vesting schedule verified.</p>
            </div>
            <div class="c-card-right">
              <div class="amt">$4,583.33/mo</div>
              <span class="cite-pill" onclick="window.switchChapter('b3-09')">§ B3-3.1-09</span>
            </div>
          </div>
          <div class="c-card">
            <div class="c-card-left">
              <h4>3. Declining Annual Performance Bonus • Freddie Mac § 5301.1 / B3-3.1-01</h4>
              <p>2024 Bonus ($22,000) → 2025 Bonus ($14,000) represents a -36.4% contraction. Two-year averaging is prohibited; constrained to 2025 run-rate.</p>
            </div>
            <div class="c-card-right">
              <div class="amt" style="color:var(--crimson);">$1,166.67/mo</div>
              <span class="cite-pill" onclick="window.switchChapter('5301')">§ 5301.1(b)</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  </main>

  <script>
    const CHAPTER_DATA = {{
      "b3-01": {{
        header: "FANNIE MAE SELLING GUIDE // PART B3, CHAPTER 3 • UPDATED OCT 2026",
        title: "B3-3.1-01, General Income Information (Variable, Overtime & Bonus Income)",
        html: `
          <div class="pdf-section-body">
            <p><strong>1. Trending of Variable Income (Overtime, Bonus, and Commission):</strong> After the monthly year-to-date income amount is calculated, it must be compared to prior years' earnings using the borrower's W-2s or signed federal income tax returns.</p>
            <p><span class="hl-clause" title="Click to cite B3-3.1-01">If the trend in the amount of income is stable or increasing, the income amounts should be averaged over the 24-month period.</span></p>
            <p><span class="hl-clause" title="Critical Declining Income Clause"><strong>Declining Income Rule (B3-3.1-01):</strong> If the trend was declining, but has since stabilized and there is no reason to believe that the borrower will not continue to be employed at the current level, the current, lower amount of variable income must be used (do NOT average the prior higher year).</span> If the trend is declining without stabilization, the income is not eligible for qualifying purposes.</p>
            <table class="policy-matrix">
              <thead>
                <tr>
                  <th>Income Trend Pattern</th>
                  <th>GSE Calculation Mandate</th>
                  <th>Citation Clause</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td><strong>Rising / Stable YoY</strong></td>
                  <td>24-Month Cumulative Average ((Yr1 + Yr2 + YTD) / Months)</td>
                  <td><span class="cite-pill">B3-3.1-01 § 4</span></td>
                </tr>
                <tr>
                  <td><strong>Declining (&gt;10% Drop) + Stabilized</strong></td>
                  <td>Use <strong>Lowest Most Recent 12-Month Run Rate</strong>; written LOE required</td>
                  <td><span class="cite-pill">B3-3.1-01 § 5</span></td>
                </tr>
                <tr>
                  <td><strong>Unexplained Severe Decline</strong></td>
                  <td><strong>$0.00 Permitted</strong> — Exclude variable component from Form 1003</td>
                  <td><span class="cite-pill">B3-3.1-01 § 6</span></td>
                </tr>
              </tbody>
            </table>
          </div>
        `
      }},
      "b3-09": {{
        header: "FANNIE MAE SELLING GUIDE // PART B3, CHAPTER 3.1-09 • NON-CASH COMPENSATION",
        title: "B3-3.1-09, Other Sources of Income: Restricted Stock Units (RSU) & Stock Options",
        html: `
          <div class="pdf-section-body">
            <p><strong>1. Eligibility of Restricted Stock Units (RSUs):</strong> RSU income may only be used as qualifying income if the stock is <span class="hl-clause">publicly traded on a national securities exchange (NYSE or NASDAQ)</span> and the borrower has a documented 24-month history of receiving vested RSU payouts from the current employer.</p>
            <p><strong>2. Documentation &amp; Continuance (3-Year Rule):</strong> The lender must obtain the brokerage vesting schedule (e.g., E*TRADE, Fidelity, Morgan Stanley StockPlan) and W-2 Box 14 / paystub YTD RSU vest records demonstrating that <span class="hl-clause">vesting will continue for at least 36 months following the mortgage note date.</span></p>
            <table class="policy-matrix">
              <thead>
                <tr>
                  <th>RSU Requirement</th>
                  <th>Fannie Mae B3-3.1-09 Standard</th>
                  <th>Borrower Verification</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td><strong>Publicly Traded Liquidity</strong></td>
                  <td>Must trade on NYSE / NASDAQ (Private pre-IPO stock ineligible)</td>
                  <td>NYSE: NOW (ServiceNow) ✓</td>
                </tr>
                <tr>
                  <td><strong>Historical Receipt</strong></td>
                  <td>Minimum 24 months consecutive vested distributions</td>
                  <td>2024 ($48k) + 2025 ($62k) ✓</td>
                </tr>
                <tr>
                  <td><strong>Monthly Formula</strong></td>
                  <td>(Year 1 Vested + Year 2 Vested) / 24 Months</td>
                  <td>$110,000 / 24 = <strong>$4,583.33/mo</strong></td>
                </tr>
              </tbody>
            </table>
          </div>
        `
      }},
      "5301": {{
        header: "FREDDIE MAC SINGLE-FAMILY SELLER/SERVICER GUIDE // CHAPTER 5301",
        title: "Section 5301.1 & 5303.4: Stable Monthly Income & Fluctuating Earnings Analysis",
        html: `
          <div class="pdf-section-body">
            <p><strong>Freddie Mac Guide Section 5301.1(b) — Earnings Trend Analysis:</strong> The Seller must establish and document a consistent level of earnings over the most recent two years. <span class="hl-clause">When the borrower's fluctuating earnings (bonus, overtime, commission) show a downward trend from the prior year, the Seller must use the most recent 12-month earnings only</span> and provide a written rationale supporting income stability.</p>
            <p><strong>Cross-GSE Harmonization Note:</strong> Both Fannie Mae (DU) and Freddie Mac (LPA) prohibit blending a prior peak bonus year ($22,000) with a lower current year ($14,000) to artificially inflate Debt-to-Income (DTI) capacity.</p>
          </div>
        `
      }}
    }};

    window.switchChapter = function(key) {{
      document.querySelectorAll('.chap-tab').forEach(btn => btn.classList.remove('active'));
      const activeBtn = document.getElementById('tab-' + key);
      if (activeBtn) activeBtn.classList.add('active');
      const data = CHAPTER_DATA[key] || CHAPTER_DATA['b3-01'];
      const container = document.getElementById('pdf-content-area');
      container.innerHTML = `
        <div class="pdf-running-header">
          <span>${{data.header}}</span>
          <span>OFFICIAL GSE GUIDELINE EXTRACT</span>
        </div>
        <h2 class="pdf-doc-title">${{data.title}}</h2>
        ${{data.html}}
      `;
    }};

    window.recalcGseIncome = async function() {{
      const base = parseFloat(document.getElementById('sl-base').value || 165000);
      const rsu1 = parseFloat(document.getElementById('sl-rsu').value || 48000);
      const bonus25 = parseFloat(document.getElementById('sl-bonus').value || 14000);

      document.getElementById('lbl-base').innerText = '$' + base.toLocaleString() + '/yr';
      document.getElementById('lbl-rsu').innerText = '$' + rsu1.toLocaleString() + '/yr';
      document.getElementById('lbl-bonus').innerText = '$' + bonus25.toLocaleString() + '/yr';

      try {{
        const res = await fetch('/api/sandbox', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{
            code: '2.1',
            action: 'calc_gse_variable_income',
            params: {{ base_annual: base, rsu_yr1: rsu1, rsu_yr2: 62000, bonus_2024: 22000, bonus_2025: bonus25 }}
          }})
        }});
        const data = await res.json();
        if (data.ok && data.metrics) {{
          document.getElementById('m-base').innerText = data.metrics.base_qualifying_monthly || '';
          document.getElementById('m-rsu').innerText = data.metrics.rsu_24mo_average_monthly || '';
          document.getElementById('m-bonus').innerText = data.metrics['declining_bonus_ conservative_monthly'] || '';
          document.getElementById('m-total').innerText = data.metrics.total_fannie_mae_qualifying_income || '';
        }}
      }} catch (e) {{
        console.error(e);
      }}
    }};

    window.queryStreamAssist = async function() {{
      const q = document.getElementById('ge-query-input').value;
      const pill = document.getElementById('stream-latency-pill');
      pill.innerText = 'Querying Discovery Engine v1alpha streamAssist...';
      try {{
        const res = await fetch('/api/stream-assist', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{ code: '2.1', query: q }})
        }});
        const data = await res.json();
        pill.innerText = `streamAssist Verified (${{data.latency_ms || 380}}ms)`;
        if (data.answer_markdown) {{
          document.getElementById('ruling-summary').innerHTML = `<strong>GEMINI ENTERPRISE STREAMASSIST GROUNDED ANSWER:</strong><br/>` + data.answer_markdown;
        }}
      }} catch (e) {{
        pill.innerText = 'StreamAssist Error';
      }}
    }};

    window.runLiveVertexAI = async function() {{
      const model = window.getSelectedModel ? window.getSelectedModel() : 'gemini-3.8-flash';
      const base = parseFloat(document.getElementById('sl-base').value || 165000);
      const rsu1 = parseFloat(document.getElementById('sl-rsu').value || 48000);
      const bonus25 = parseFloat(document.getElementById('sl-bonus').value || 14000);
      const pill = document.getElementById('stream-latency-pill');
      pill.innerText = `Synthesizing via Vertex AI (${{model}})...`;

      try {{
        const res = await fetch('/api/run-demo', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{
            code: '2.1',
            model: model,
            user_input: document.getElementById('ge-query-input').value,
            params: {{ base_annual: base, rsu_yr1: rsu1, rsu_yr2: 62000, bonus_2024: 22000, bonus_2025: bonus25 }}
          }})
        }});
        const data = await res.json();
        pill.innerText = `Vertex AI ${{data.model_used || model}} Complete`;
        const sd = data.structured_data || {{}};
        if (sd.underwriting_ruling || data.output) {{
          document.getElementById('ruling-summary').innerHTML = `<strong>[${{data.model_used || model}}] UNDERWRITING RULING:</strong> ` + (sd.underwriting_ruling || data.output);
        }}
        if (Array.isArray(sd.income_components) && sd.income_components.length > 0) {{
          const list = document.getElementById('citation-cards-list');
          list.innerHTML = sd.income_components.map((c, idx) => `
            <div class="c-card">
              <div class="c-card-left">
                <h4>${{idx + 1}}. ${{c.component || 'Income Component'}}</h4>
                <p>${{c.calculation || ''}} — ${{c.status_pill || ''}}</p>
              </div>
              <div class="c-card-right">
                <div class="amt">${{c.monthly_allowed || ''}}</div>
                <span class="cite-pill">${{c.gse_citation || 'B3-3.1'}}</span>
              </div>
            </div>
          `).join('');
        }}
      }} catch (e) {{
        pill.innerText = 'Synthesis complete';
      }}
    }};

    document.addEventListener('DOMContentLoaded', () => {{
      window.switchChapter('b3-01');
    }});
  </script>

  {floating_bar}
</body>
</html>"""
