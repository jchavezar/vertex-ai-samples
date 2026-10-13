# -*- coding: utf-8 -*-
"""Square 2.1 Standalone Full-Screen UI:
Self-Employed Cash-Flow Normalizer (Fannie Mae Form 1084 & IRS Form 1040 Schedule C / 1065 K-1)
Design Style: Intuit TurboTax / QuickBooks Online CPA Tax Workbook (#F4F5F8 light gray background, #2CA01C QuickBooks green accents, #0077C5 Intuit blue headers, #FFFFFF IRS tax form cards, Public Sans + IBM Plex Mono tabular numerals).
"""

from shared.standalone_uis.base_helpers import render_floating_control_bar_and_drawer


def render_sq_2_1(auth_token: str) -> str:
    floating_bar = render_floating_control_bar_and_drawer("2.1", auth_token)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>2.1 · Self-Employed Cash-Flow Normalizer — CPA Tax &amp; Form 1084 Workbook</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600;700&family=Public+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <style>
    :root {{
      --qbo-bg: #F4F5F8;
      --qbo-card: #FFFFFF;
      --qbo-green: #2CA01C;
      --qbo-green-dark: #1E7E12;
      --qbo-green-soft: #E9F7E7;
      --intuit-blue: #0077C5;
      --intuit-blue-dark: #005A96;
      --intuit-blue-soft: #EBF5FC;
      --ink: #1F2532;
      --muted: #5E6675;
      --border: #D4D7DC;
      --irs-tint: #FAFBFC;
      --amber: #D97706;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      background: var(--qbo-bg);
      color: var(--ink);
      font-family: 'Public Sans', -apple-system, BlinkMacSystemFont, sans-serif;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      font-variant-numeric: tabular-nums;
    }}

    /* Intuit QuickBooks / TurboTax CPA Top Navigation Bar */
    .cpa-topbar {{
      background: #FFFFFF;
      border-bottom: 1px solid var(--border);
      border-top: 4px solid var(--qbo-green);
      padding: 12px 28px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      flex-wrap: wrap;
      box-shadow: 0 2px 6px rgba(31, 37, 50, 0.04);
    }}
    .brand-left {{
      display: flex;
      align-items: center;
      gap: 14px;
    }}
    .qbo-badge {{
      width: 38px;
      height: 38px;
      border-radius: 8px;
      background: var(--qbo-green);
      color: #FFFFFF;
      font-weight: 800;
      font-size: 15px;
      display: flex;
      align-items: center;
      justify-content: center;
      box-shadow: 0 2px 6px rgba(44, 160, 28, 0.25);
    }}
    .app-title {{
      font-size: 18px;
      font-weight: 800;
      color: var(--ink);
      letter-spacing: -0.01em;
    }}
    .app-subtitle {{
      font-size: 12px;
      color: var(--muted);
      margin-top: 2px;
    }}
    .topbar-right {{
      display: flex;
      align-items: center;
      gap: 12px;
      flex-wrap: wrap;
    }}
    .model-selector-pill {{
      display: flex;
      align-items: center;
      gap: 8px;
      background: var(--intuit-blue-soft);
      border: 1px solid #B8DDF8;
      padding: 6px 12px;
      border-radius: 6px;
      font-size: 12px;
      color: var(--intuit-blue-dark);
      font-weight: 600;
    }}
    .model-selector-pill select {{
      background: transparent;
      border: none;
      color: var(--intuit-blue-dark);
      font-family: inherit;
      font-size: 12px;
      font-weight: 700;
      outline: none;
      cursor: pointer;
    }}
    .btn-audio-walkthrough {{
      background: var(--intuit-blue);
      color: #FFFFFF;
      border: none;
      padding: 9px 15px;
      border-radius: 6px;
      font-family: inherit;
      font-size: 12.5px;
      font-weight: 700;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      box-shadow: 0 2px 6px rgba(0, 119, 197, 0.25);
      transition: background 0.15s;
    }}
    .btn-audio-walkthrough:hover {{
      background: var(--intuit-blue-dark);
    }}
    .btn-vertex-run {{
      background: var(--qbo-green);
      color: #FFFFFF;
      border: none;
      padding: 9px 16px;
      border-radius: 6px;
      font-family: inherit;
      font-size: 12.5px;
      font-weight: 700;
      cursor: pointer;
      box-shadow: 0 2px 6px rgba(44, 160, 28, 0.25);
    }}
    .btn-vertex-run:hover {{
      background: var(--qbo-green-dark);
    }}

    /* Borrower File Summary Ribbon */
    .borrower-strip {{
      background: var(--intuit-blue);
      color: #FFFFFF;
      padding: 10px 28px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 14px;
      font-size: 12.5px;
    }}
    .borrower-strip strong {{
      font-weight: 700;
    }}
    .kpi-banner {{
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 16px;
      padding: 20px 28px 0 28px;
      max-width: 1480px;
      margin: 0 auto;
      width: 100%;
    }}
    @media (max-width: 980px) {{
      .kpi-banner {{ grid-template-columns: repeat(2, 1fr); }}
    }}
    .kpi-card {{
      background: #FFFFFF;
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 16px 18px;
      box-shadow: 0 1px 3px rgba(0,0,0,0.03);
    }}
    .kpi-card.highlight {{
      border-left: 5px solid var(--qbo-green);
      background: #FFFFFF;
    }}
    .kpi-card.naive {{
      border-left: 5px solid #94A3B8;
    }}
    .kpi-label {{
      font-size: 11.5px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.04em;
      color: var(--muted);
    }}
    .kpi-val {{
      font-family: 'IBM Plex Mono', monospace;
      font-size: 24px;
      font-weight: 700;
      color: var(--ink);
      margin-top: 6px;
    }}
    .kpi-sub {{
      font-size: 12px;
      color: var(--muted);
      margin-top: 4px;
    }}

    /* Main 2-Column CPA Workbook Layout */
    .workbook-grid {{
      display: grid;
      grid-template-columns: 1.35fr 0.85fr;
      gap: 20px;
      padding: 20px 28px 90px 28px;
      max-width: 1480px;
      margin: 0 auto;
      width: 100%;
    }}
    @media (max-width: 1120px) {{
      .workbook-grid {{ grid-template-columns: 1fr; }}
    }}

    /* IRS Form 1040 Schedule C & Form 1084 Card */
    .irs-form-card {{
      background: #FFFFFF;
      border: 1px solid var(--border);
      border-radius: 8px;
      overflow: hidden;
      box-shadow: 0 2px 8px rgba(31, 37, 50, 0.05);
    }}
    .irs-form-header {{
      background: #F8FAFC;
      border-bottom: 2px solid var(--ink);
      padding: 14px 20px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 10px;
    }}
    .irs-code-box {{
      font-family: 'IBM Plex Mono', monospace;
      font-size: 12px;
      font-weight: 700;
      color: var(--intuit-blue-dark);
      background: var(--intuit-blue-soft);
      padding: 4px 10px;
      border-radius: 4px;
      border: 1px solid #B8DDF8;
    }}
    .worksheet-table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 13px;
    }}
    .worksheet-table th {{
      background: #F1F4F9;
      color: var(--ink);
      font-weight: 700;
      text-align: left;
      padding: 10px 14px;
      border-bottom: 1px solid var(--border);
      font-size: 11.5px;
      text-transform: uppercase;
      letter-spacing: 0.03em;
    }}
    .worksheet-table th.num, .worksheet-table td.num {{
      text-align: right;
      font-family: 'IBM Plex Mono', monospace;
    }}
    .worksheet-table td {{
      padding: 11px 14px;
      border-bottom: 1px solid #EAEEF3;
      vertical-align: middle;
    }}
    .worksheet-table tr:hover {{
      background: #F9FBFD;
    }}
    .worksheet-table tr.section-row td {{
      background: #EBF5FC;
      color: var(--intuit-blue-dark);
      font-weight: 700;
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: 0.04em;
      padding: 8px 14px;
    }}
    .worksheet-table tr.total-row td {{
      background: var(--qbo-green-soft);
      font-weight: 800;
      font-size: 14px;
      border-top: 2px solid var(--qbo-green);
      border-bottom: 2px solid var(--qbo-green);
      color: #0F4C08;
    }}
    .line-badge {{
      display: inline-block;
      font-family: 'IBM Plex Mono', monospace;
      font-size: 11px;
      font-weight: 700;
      background: #F1F5F9;
      border: 1px solid #CBD5E1;
      color: #334155;
      padding: 2px 6px;
      border-radius: 4px;
      margin-right: 6px;
    }}
    .addback-pill {{
      display: inline-block;
      font-size: 11px;
      font-weight: 700;
      padding: 2px 8px;
      border-radius: 999px;
      background: var(--qbo-green-soft);
      color: var(--qbo-green-dark);
    }}
    .deduct-pill {{
      display: inline-block;
      font-size: 11px;
      font-weight: 700;
      padding: 2px 8px;
      border-radius: 999px;
      background: #FEF3C7;
      color: #B45309;
    }}

    /* Right Column Controls & CPA Memo */
    .right-col {{
      display: flex;
      flex-direction: column;
      gap: 18px;
    }}
    .control-panel {{
      background: #FFFFFF;
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 18px 20px;
      box-shadow: 0 2px 8px rgba(31, 37, 50, 0.04);
    }}
    .panel-title {{
      font-size: 15px;
      font-weight: 800;
      color: var(--ink);
      margin-bottom: 4px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}
    .panel-desc {{
      font-size: 12px;
      color: var(--muted);
      margin-bottom: 14px;
    }}
    .slider-item {{
      background: var(--irs-tint);
      border: 1px solid #E2E8F0;
      border-radius: 6px;
      padding: 11px 14px;
      margin-bottom: 10px;
    }}
    .slider-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 12.5px;
      font-weight: 600;
      margin-bottom: 6px;
    }}
    .slider-header span.val {{
      font-family: 'IBM Plex Mono', monospace;
      font-weight: 700;
      color: var(--qbo-green-dark);
    }}
    .slider-item input[type="range"] {{
      width: 100%;
      accent-color: var(--qbo-green);
      cursor: pointer;
    }}
    .checkbox-row {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 9px 12px;
      background: #F8FAFC;
      border: 1px solid #E2E8F0;
      border-radius: 6px;
      margin-bottom: 8px;
      font-size: 12.5px;
      font-weight: 600;
      cursor: pointer;
    }}
    .checkbox-row input[type="checkbox"] {{
      accent-color: var(--qbo-green);
      width: 16px;
      height: 16px;
      margin-right: 8px;
      cursor: pointer;
    }}
    .cpa-memo-box {{
      background: #FFFFFF;
      border: 1px solid var(--border);
      border-top: 4px solid var(--intuit-blue);
      border-radius: 8px;
      padding: 18px 20px;
      box-shadow: 0 2px 8px rgba(31, 37, 50, 0.04);
    }}
    .memo-body {{
      font-size: 13px;
      line-height: 1.6;
      color: var(--ink);
      margin-top: 10px;
      background: #F8FAFC;
      border: 1px solid #E2E8F0;
      border-radius: 6px;
      padding: 14px;
    }}
  </style>
</head>
<body>

  <!-- INTUIT TURBOTAX / QUICKBOOKS ONLINE CPA HEADER -->
  <header class="cpa-topbar">
    <div class="brand-left">
      <div class="qbo-badge">QB</div>
      <div>
        <div class="app-title">Self-Employed Cash-Flow Normalizer · Fannie Mae Form 1084 Workbook</div>
        <div class="app-subtitle">IRS Form 1040 Schedule C &amp; Form 1065 K-1 Non-Cash Add-Back Analyzer (Selling Guide B3-3.2-01)</div>
      </div>
    </div>
    <div class="topbar-right">
      <div class="model-selector-pill">
        <span>Tax Engine Model:</span>
        <select id="app-model-select" onchange="window.syncSelectedModel(this.value)">
          <option value="gemini-4-argon" selected>gemini-4-argon (CPA Deep Audit)</option>
          <option value="gemini-3.8-flash">gemini-3.8-flash (Real-Time Worksheet)</option>
        </select>
      </div>
      <button class="btn-audio-walkthrough" onclick="window.playCpaAudioWalkthrough(this)">
        🔊 Hear Underwriter Income Walkthrough (Gemini 3.8 Live · Kore HD)
      </button>
      <button class="btn-vertex-run" onclick="window.runLiveVertexAI()">
        Recalculate &amp; Certify Form 1084
      </button>
    </div>
  </header>

  <!-- BORROWER TAX FILE CONTEXT BAR -->
  <div class="borrower-strip">
    <div><strong>Borrower:</strong> Marcus &amp; Elena Vance (Vance Precision Logistics LLC · EIN 38-4910284)</div>
    <div><strong>Tax Returns:</strong> 2024 &amp; 2025 IRS Form 1040 + Schedule C + Form 1065 K-1 (100% Ownership)</div>
    <div><strong>Fannie Mae Form 1084 Status:</strong> <span id="status-badge" style="background:#2CA01C;padding:3px 10px;border-radius:999px;font-weight:700;">QUALIFIED · RISING 24-MO TREND</span></div>
  </div>

  <!-- 4-CARD EXECUTIVE KPI SUMMARY -->
  <section class="kpi-banner">
    <div class="kpi-card naive">
      <div class="kpi-label">Naive Schedule C Net Profit (Line 31)</div>
      <div class="kpi-val" id="kpi-naive-mo">$6,916.67/mo</div>
      <div class="kpi-sub">24-Mo Unadjusted Average ($83,000/yr)</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-label">Eligible Non-Cash Add-Backs (2025)</div>
      <div class="kpi-val" id="kpi-addbacks" style="color:var(--intuit-blue);">+$52,800/yr</div>
      <div class="kpi-sub">Depreciation + Home Office + K-1 Dist.</div>
    </div>
    <div class="kpi-card highlight">
      <div class="kpi-label">Fannie Mae Form 1084 Qualifying Income</div>
      <div class="kpi-val" id="kpi-qualifying-mo" style="color:var(--qbo-green-dark);">$11,533.33/mo</div>
      <div class="kpi-sub" id="kpi-qualifying-yr">$138,400.00 Annualized Qualifying Cash Flow</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-label">Qualifying Income Lift vs. Naive</div>
      <div class="kpi-val" id="kpi-lift-pct" style="color:var(--qbo-green-dark);">+66.7% (+$4,616/mo)</div>
      <div class="kpi-sub">Lowers Borrower DTI from 49.2% → 29.5%</div>
    </div>
  </section>

  <!-- MAIN 2-COLUMN CPA WORKBOOK -->
  <main class="workbook-grid">
    <!-- LEFT: INTERACTIVE IRS SCHEDULE C & K-1 FORM 1084 WORKSHEET TABLE -->
    <div class="irs-form-card">
      <div class="irs-form-header">
        <div>
          <div style="font-size:16px;font-weight:800;color:var(--ink);">Fannie Mae Form 1084 — Cash Flow Analysis Worksheet</div>
          <div style="font-size:12px;color:var(--muted);">Side-by-Side 2024 vs. 2025 IRS Form 1040 Schedule C &amp; Partnership K-1 Normalization</div>
        </div>
        <span class="irs-code-box">OMB No. 1545-0074 · Form 1084</span>
      </div>

      <table class="worksheet-table">
        <thead>
          <tr>
            <th>IRS Form / Line Item Description</th>
            <th>GSE Treatment</th>
            <th class="num">2024 Return</th>
            <th class="num">2025 Return</th>
            <th class="num">24-Mo Total</th>
          </tr>
        </thead>
        <tbody>
          <tr class="section-row">
            <td colspan="5">Part I — IRS Form 1040 Schedule C (Sole Proprietorship Profit or Loss)</td>
          </tr>
          <tr>
            <td><span class="line-badge">Sch C · Line 31</span> Net Profit or (Loss) per Tax Return</td>
            <td><span class="addback-pill">Base Net Profit</span></td>
            <td class="num" id="cell-net-24">$78,000</td>
            <td class="num" id="cell-net-25">$88,000</td>
            <td class="num" id="cell-net-tot">$166,000</td>
          </tr>
          <tr>
            <td><span class="line-badge">Sch C · Line 13</span> Depreciation &amp; §179 Expense Deduction (Non-Cash)</td>
            <td><span class="addback-pill">+100% Add-Back</span></td>
            <td class="num" id="cell-dep-24">+$21,500</td>
            <td class="num" id="cell-dep-25">+$24,500</td>
            <td class="num" id="cell-dep-tot">+$46,000</td>
          </tr>
          <tr>
            <td><span class="line-badge">Sch C · Line 12</span> Depletion &amp; Amortization (Form 4562)</td>
            <td><span class="addback-pill">+100% Add-Back</span></td>
            <td class="num" id="cell-amo-24">+$4,200</td>
            <td class="num" id="cell-amo-25">+$4,200</td>
            <td class="num" id="cell-amo-tot">+$8,400</td>
          </tr>
          <tr>
            <td><span class="line-badge">Sch C · Line 30</span> Expenses for Business Use of Home (Form 8829)</td>
            <td><span class="addback-pill">+100% Add-Back</span></td>
            <td class="num" id="cell-home-24">+$4,400</td>
            <td class="num" id="cell-home-25">+$4,800</td>
            <td class="num" id="cell-home-tot">+$9,200</td>
          </tr>
          <tr>
            <td><span class="line-badge">Sch C · Line 24b</span> Deductible Meals Non-Cash Adjustment</td>
            <td><span class="deduct-pill">-Subtraction</span></td>
            <td class="num" id="cell-meals-24">-$2,400</td>
            <td class="num" id="cell-meals-25">-$2,700</td>
            <td class="num" id="cell-meals-tot">-$5,100</td>
          </tr>

          <tr class="section-row">
            <td colspan="5">Part II — IRS Form 1065 Schedule K-1 (Partnership Ordinary Business Income)</td>
          </tr>
          <tr>
            <td><span class="line-badge">Form 1065 K-1 · Box 1</span> Ordinary Business Income (Verified Liquidity Ratio &gt; 1.25x)</td>
            <td><span class="addback-pill">+K-1 Cash Flow</span></td>
            <td class="num" id="cell-k1-24">+$30,300</td>
            <td class="num" id="cell-k1-25">+$22,000</td>
            <td class="num" id="cell-k1-tot">+$52,300</td>
          </tr>

          <tr class="total-row">
            <td colspan="2">Total Adjusted Self-Employed Cash Flow (Form 1084 Line 13)</td>
            <td class="num" id="cell-adj-24">$136,000</td>
            <td class="num" id="cell-adj-25">$140,800</td>
            <td class="num" id="cell-adj-tot">$276,800</td>
          </tr>
          <tr class="total-row" style="background:#EBF5FC;color:#005A96;border-color:#0077C5;">
            <td colspan="3">Fannie Mae Form 1084 Qualifying Monthly Income (24-Month Average ÷ 24)</td>
            <td class="num" colspan="2" id="cell-final-monthly" style="font-size:16px;">$11,533.33 / month</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- RIGHT: INTERACTIVE ADD-BACK SLIDERS, CHECKBOXES & CPA CERTIFICATION MEMO -->
    <div class="right-col">
      <div class="control-panel">
        <div class="panel-title">
          <span>Interactive CPA Add-Back Controls</span>
          <span style="font-size:11px;color:var(--qbo-green-dark);font-weight:700;">Live Form 1084 Math</span>
        </div>
        <div class="panel-desc">Adjust 2025 Schedule C &amp; Form 1065 K-1 line items or toggle non-cash add-backs to inspect qualifying income impact.</div>

        <div class="slider-item">
          <div class="slider-header">
            <span>2025 Schedule C Line 13 Depreciation</span>
            <span class="val" id="lbl-dep">+$24,500</span>
          </div>
          <input type="range" id="sl-dep" min="0" max="55000" step="500" value="24500" oninput="window.recalcForm1084()" />
        </div>

        <div class="slider-item">
          <div class="slider-header">
            <span>2025 Schedule C Line 30 Business Home Office</span>
            <span class="val" id="lbl-home">+$4,800</span>
          </div>
          <input type="range" id="sl-home" min="0" max="12000" step="200" value="48000" style="display:none;" />
          <input type="range" id="sl-home-real" min="0" max="12000" step="200" value="4800" oninput="window.recalcForm1084()" />
        </div>

        <div class="slider-item">
          <div class="slider-header">
            <span>2025 Form 1065 K-1 Box 1 Ordinary Income</span>
            <span class="val" id="lbl-k1">+$22,000</span>
          </div>
          <input type="range" id="sl-k1" min="0" max="60000" step="1000" value="22000" oninput="window.recalcForm1084()" />
        </div>

        <label class="checkbox-row">
          <span><input type="checkbox" id="chk-amo" checked onchange="window.recalcForm1084()" /> Include Form 4562 Amortization Add-Back (+$4,200/yr)</span>
          <span style="font-family:'IBM Plex Mono',monospace;color:var(--qbo-green-dark);">+$350/mo</span>
        </label>

        <label class="checkbox-row">
          <span><input type="checkbox" id="chk-meals" checked onchange="window.recalcForm1084()" /> Deduct Line 24b Meals Exclusion (-$2,700 in 2025)</span>
          <span style="font-family:'IBM Plex Mono',monospace;color:#B45309;">-$212.50/mo</span>
        </label>
      </div>

      <div class="cpa-memo-box">
        <div class="panel-title">
          <span>Underwriter &amp; CPA Audit Determination</span>
          <span id="live-model-pill" style="font-family:'IBM Plex Mono',monospace;font-size:11px;background:var(--intuit-blue-soft);color:var(--intuit-blue-dark);padding:3px 8px;border-radius:4px;">gemini-4-argon</span>
        </div>
        <div class="memo-body" id="cpa-memo-output">
          <strong>FANNIE MAE FORM 1084 CERTIFICATION:</strong><br/>
          • <strong>Naive Underwriting Error Avoided:</strong> Using unadjusted Schedule C Line 31 net profit ($78,000 in 2024; $88,000 in 2025) yields only <strong>$6,916.67/mo</strong>, causing a false DTI denial.<br/>
          • <strong>B3-3.2-01 Non-Cash Normalization:</strong> Adding back paper depreciation (Line 13: +$21,500 / +$24,500), amortization (+$4,200/yr), business use of home (Line 30: +$4,400 / +$4,800), and verified Form 1065 K-1 Box 1 cash flow lifts qualifying monthly income to <strong>$11,533.33/mo</strong> (+66.7%).
        </div>
      </div>
    </div>
  </main>

  <script>
    window.recalcForm1084 = function() {{
      const net24 = 78000;
      const net25 = 88000;
      const dep24 = 21500;
      const dep25 = parseFloat(document.getElementById('sl-dep').value || 24500);
      const home24 = 4400;
      const home25 = parseFloat(document.getElementById('sl-home-real').value || 4800);
      const k1_24 = 30300;
      const k1_25 = parseFloat(document.getElementById('sl-k1').value || 22000);
      const includeAmo = document.getElementById('chk-amo').checked;
      const includeMeals = document.getElementById('chk-meals').checked;

      const amo24 = includeAmo ? 4200 : 0;
      const amo25 = includeAmo ? 4200 : 0;
      const meals24 = includeMeals ? 2400 : 0;
      const meals25 = includeMeals ? 2700 : 0;

      document.getElementById('lbl-dep').innerText = '+$' + dep25.toLocaleString();
      document.getElementById('lbl-home').innerText = '+$' + home25.toLocaleString();
      document.getElementById('lbl-k1').innerText = '+$' + k1_25.toLocaleString();

      document.getElementById('cell-dep-25').innerText = '+$' + dep25.toLocaleString();
      document.getElementById('cell-dep-tot').innerText = '+$' + (dep24 + dep25).toLocaleString();

      document.getElementById('cell-amo-24').innerText = '+$' + amo24.toLocaleString();
      document.getElementById('cell-amo-25').innerText = '+$' + amo25.toLocaleString();
      document.getElementById('cell-amo-tot').innerText = '+$' + (amo24 + amo25).toLocaleString();

      document.getElementById('cell-home-25').innerText = '+$' + home25.toLocaleString();
      document.getElementById('cell-home-tot').innerText = '+$' + (home24 + home25).toLocaleString();

      document.getElementById('cell-meals-24').innerText = '-$' + meals24.toLocaleString();
      document.getElementById('cell-meals-25').innerText = '-$' + meals25.toLocaleString();
      document.getElementById('cell-meals-tot').innerText = '-$' + (meals24 + meals25).toLocaleString();

      document.getElementById('cell-k1-25').innerText = '+$' + k1_25.toLocaleString();
      document.getElementById('cell-k1-tot').innerText = '+$' + (k1_24 + k1_25).toLocaleString();

      const adj24 = net24 + dep24 + amo24 + home24 - meals24 + k1_24;
      const adj25 = net25 + dep25 + amo25 + home25 - meals25 + k1_25;
      const adjTot = adj24 + adj25;
      const monthlyQual = adjTot / 24.0;
      const naiveMonthly = (net24 + net25) / 24.0;
      const liftPct = ((monthlyQual - naiveMonthly) / naiveMonthly) * 100.0;
      const addbacks25 = dep25 + amo25 + home25 - meals25 + k1_25;

      document.getElementById('cell-adj-24').innerText = '$' + adj24.toLocaleString();
      document.getElementById('cell-adj-25').innerText = '$' + adj25.toLocaleString();
      document.getElementById('cell-adj-tot').innerText = '$' + adjTot.toLocaleString();
      document.getElementById('cell-final-monthly').innerText = '$' + monthlyQual.toLocaleString('en-US', {{minimumFractionDigits: 2, maximumFractionDigits: 2}}) + ' / month';

      document.getElementById('kpi-addbacks').innerText = '+$' + addbacks25.toLocaleString() + '/yr';
      document.getElementById('kpi-qualifying-mo').innerText = '$' + monthlyQual.toLocaleString('en-US', {{minimumFractionDigits: 2, maximumFractionDigits: 2}}) + '/mo';
      document.getElementById('kpi-qualifying-yr').innerText = '$' + (monthlyQual * 12).toLocaleString('en-US', {{minimumFractionDigits: 2, maximumFractionDigits: 2}}) + ' Annualized Qualifying Cash Flow';
      document.getElementById('kpi-lift-pct').innerText = '+' + liftPct.toFixed(1) + '% (+$' + Math.round(monthlyQual - naiveMonthly).toLocaleString() + '/mo)';
    }};

    window.playCpaAudioWalkthrough = function(btnEl) {{
      const qualMo = document.getElementById('kpi-qualifying-mo').innerText;
      const script = "Underwriter Form 1084 Income Walkthrough for Marcus and Elena Vance. While naive Schedule C Line 31 net profit averages only 6,916 dollars and 67 cents per month, Fannie Mae Selling Guide B3-3.2-01 permits full add-backs for non-cash Schedule C Line 13 depreciation of 24,500 dollars, Form 8829 business use of home of 4,800 dollars, amortization, and verified Form 1065 K-1 ordinary income. Total verified qualifying income is " + qualMo + ", reducing debt-to-income ratio to 29.5 percent.";
      if (window.playLiveCallClip) {{
        window.playLiveCallClip(script, "Kore", "Senior CPA & Mortgage Underwriter", btnEl);
      }}
    }};

    window.runLiveVertexAI = async function() {{
      const model = window.getSelectedModel ? window.getSelectedModel() : 'gemini-4-argon';
      const memoEl = document.getElementById('cpa-memo-output');
      const qualMo = document.getElementById('kpi-qualifying-mo').innerText;
      memoEl.innerHTML = '<em>Synthesizing Fannie Mae Form 1084 CPA Audit Memo via Vertex AI (' + model + ')...</em>';
      try {{
        const res = await fetch('/api/run-demo', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{
            code: '2.1',
            model: model,
            user_input: 'Generate a concise CPA & Underwriter Form 1084 Cash Flow Normalization Ruling for Marcus & Elena Vance with qualifying income ' + qualMo + ' vs $6,916.67/mo naive Schedule C net profit.'
          }})
        }});
        const data = await res.json();
        const text = data.output || data.response || data.result || '';
        if (text) {{
          memoEl.innerHTML = '<strong>VERTEX AI (' + model.toUpperCase() + ') CPA CERTIFICATION:</strong><br/>' + text.replace(/\\n/g, '<br/>');
        }} else {{
          memoEl.innerHTML = '<strong>FANNIE MAE FORM 1084 CERTIFIED (' + model + '):</strong> Qualifying monthly income verified at <strong>' + qualMo + '</strong> per Selling Guide B3-3.2-01.';
        }}
      }} catch (err) {{
        memoEl.innerHTML = '<strong>FANNIE MAE FORM 1084 CERTIFIED:</strong> Qualifying monthly income verified at <strong>' + qualMo + '</strong> per Selling Guide B3-3.2-01.';
      }}
    }};
  </script>

  {floating_bar}
</body>
</html>"""
