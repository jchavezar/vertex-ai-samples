# -*- coding: utf-8 -*-
"""Square 2.4 Standalone Full-Screen UI:
Appraisal Report Anomaly Detector (Fannie Mae Form 1004 URAR & UAD / SSR Collateral Underwriter Desk Review)
Design Style: Fannie Mae Form 1004 URAR Real Estate Appraisal Report & MLS Comparable Grid (#F7F5F0 warm buff appraisal paper, #1E3A8A navy ink, #047857 compliant green, #B91C1C guideline flag red, Lora serif headings + DM Sans grid).
"""

from shared.standalone_uis.base_helpers import render_floating_control_bar_and_drawer


def render_sq_2_4(auth_token: str) -> str:
    floating_bar = render_floating_control_bar_and_drawer("2.4", auth_token)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>2.4 · Appraisal Report Anomaly Detector — Fannie Mae Form 1004 URAR &amp; MLS Comparable Grid</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600;700&family=Lora:ital,wght@0,600;0,700;1,600&display=swap" rel="stylesheet">
  <style>
    :root {{
      --urar-paper: #F7F5F0;
      --urar-card: #FFFFFF;
      --navy-ink: #1E3A8A;
      --navy-deep: #172554;
      --navy-soft: #EFF6FF;
      --comp-green: #047857;
      --comp-green-soft: #ECFDF5;
      --flag-red: #B91C1C;
      --flag-red-soft: #FEF2F2;
      --ink: #1E293B;
      --muted: #57534E;
      --border: #D6D3D1;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      background: var(--urar-paper);
      color: var(--ink);
      font-family: 'DM Sans', -apple-system, BlinkMacSystemFont, sans-serif;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      font-variant-numeric: tabular-nums;
    }}

    /* Top Fannie Mae Form 1004 URAR Masthead */
    .urar-header {{
      background: var(--navy-ink);
      color: #FFFFFF;
      padding: 14px 28px;
      border-bottom: 4px solid #D97706;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      flex-wrap: wrap;
      box-shadow: 0 3px 12px rgba(30, 58, 138, 0.2);
    }}
    .urar-brand {{
      display: flex;
      align-items: center;
      gap: 14px;
    }}
    .urar-seal {{
      background: #FFFFFF;
      color: var(--navy-ink);
      font-family: 'Lora', serif;
      font-weight: 700;
      font-size: 13px;
      padding: 6px 10px;
      border-radius: 6px;
    }}
    .urar-title {{
      font-family: 'Lora', serif;
      font-size: 20px;
      font-weight: 700;
    }}
    .urar-sub {{
      font-size: 12px;
      color: #DBEAFE;
    }}
    .header-controls {{
      display: flex;
      align-items: center;
      gap: 12px;
      flex-wrap: wrap;
    }}
    .model-picker {{
      background: rgba(255,255,255,0.14);
      border: 1px solid rgba(255,255,255,0.3);
      padding: 6px 12px;
      border-radius: 6px;
      font-size: 12px;
      display: flex;
      align-items: center;
      gap: 8px;
    }}
    .model-picker select {{
      background: transparent;
      border: none;
      color: #FFFFFF;
      font-family: inherit;
      font-size: 12px;
      font-weight: 700;
      outline: none;
      cursor: pointer;
    }}
    .model-picker select option {{
      background: #172554;
      color: #FFFFFF;
    }}
    .btn-audio-desk {{
      background: #FFFFFF;
      color: var(--navy-ink);
      border: none;
      padding: 8px 14px;
      border-radius: 6px;
      font-family: inherit;
      font-size: 12.5px;
      font-weight: 700;
      cursor: pointer;
    }}
    .btn-urar-audit {{
      background: #047857;
      color: #FFFFFF;
      border: 1px solid #34D399;
      padding: 8px 16px;
      border-radius: 6px;
      font-family: inherit;
      font-size: 12.5px;
      font-weight: 700;
      cursor: pointer;
    }}

    /* Main Appraisal Workbench Layout */
    .appraisal-container {{
      max-width: 1540px;
      margin: 0 auto;
      width: 100%;
      padding: 20px 28px 90px 28px;
      display: flex;
      flex-direction: column;
      gap: 20px;
    }}

    /* Top Interactive Comp #3 Adjustment Sandbox & 15% Net / 25% Gross Progress Bars */
    .sandbox-strip {{
      display: grid;
      grid-template-columns: 1.05fr 0.95fr;
      gap: 20px;
    }}
    @media (max-width: 1080px) {{
      .sandbox-strip {{ grid-template-columns: 1fr; }}
    }}
    .paper-panel {{
      background: var(--urar-card);
      border: 1px solid var(--border);
      border-top: 3px solid var(--navy-ink);
      border-radius: 8px;
      padding: 18px 20px;
      box-shadow: 0 2px 8px rgba(30, 41, 59, 0.05);
    }}
    .panel-title {{
      font-family: 'Lora', serif;
      font-size: 17px;
      font-weight: 700;
      color: var(--navy-ink);
      margin-bottom: 10px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}
    .slider-grid {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 14px;
      margin-top: 8px;
    }}
    .slider-card {{
      background: #FAF8F5;
      border: 1px solid #E7E5E4;
      border-radius: 6px;
      padding: 12px 14px;
    }}
    .slider-card input[type="range"] {{
      width: 100%;
      accent-color: var(--navy-ink);
      margin-top: 6px;
      cursor: pointer;
    }}
    .prog-row {{
      margin-bottom: 12px;
    }}
    .prog-top {{
      display: flex;
      justify-content: space-between;
      font-size: 12.5px;
      font-weight: 700;
      margin-bottom: 5px;
    }}
    .prog-track {{
      width: 100%;
      height: 12px;
      background: #E2E8F0;
      border-radius: 999px;
      overflow: hidden;
    }}
    .prog-fill {{
      height: 100%;
      transition: width 0.2s, background 0.2s;
    }}

    /* Form 1004 URAR Side-by-Side Comparable Sales Grid */
    .urar-grid-card {{
      background: #FFFFFF;
      border: 1px solid var(--border);
      border-radius: 8px;
      overflow-x: auto;
      box-shadow: 0 2px 10px rgba(30, 41, 59, 0.06);
    }}
    .urar-table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 13px;
    }}
    .urar-table th {{
      background: #EFF6FF;
      color: var(--navy-ink);
      border: 1px solid #CBD5E1;
      padding: 11px 14px;
      text-align: left;
      font-family: 'Lora', serif;
      font-size: 13.5px;
    }}
    .urar-table td {{
      border: 1px solid #E2E8F0;
      padding: 9px 14px;
      vertical-align: middle;
    }}
    .urar-table tr.cat-row td {{
      background: #F7F5F0;
      font-weight: 700;
      font-size: 11.5px;
      text-transform: uppercase;
      letter-spacing: 0.04em;
      color: var(--navy-ink);
    }}
    .urar-table td.comp3-col {{
      background: #FFFBEB;
    }}
    .urar-table td.comp3-violation {{
      background: var(--flag-red-soft);
      color: var(--flag-red);
      font-weight: 700;
    }}
    .badge-ok {{
      display: inline-block;
      padding: 2px 8px;
      border-radius: 999px;
      font-size: 11px;
      font-weight: 700;
      background: var(--comp-green-soft);
      color: var(--comp-green);
      border: 1px solid #A7F3D0;
    }}
    .badge-flag {{
      display: inline-block;
      padding: 2px 8px;
      border-radius: 999px;
      font-size: 11px;
      font-weight: 700;
      background: var(--flag-red-soft);
      color: var(--flag-red);
      border: 1px solid #FECACA;
    }}
  </style>
</head>
<body>

  <!-- FANNIE MAE FORM 1004 URAR HEADER -->
  <header class="urar-header">
    <div class="urar-brand">
      <div class="urar-seal">FORM 1004 · URAR</div>
      <div>
        <div class="urar-title">Appraisal Report Anomaly Detector · Uniform Residential Appraisal Report &amp; MLS Grid</div>
        <div class="urar-sub">Subject Property: 418 Elmhurst Ave, Royal Oak, MI 48067 · Appraised Value: $460,000 · Collateral Underwriter (CU) Score: 3.8</div>
      </div>
    </div>
    <div class="header-controls">
      <div class="model-picker">
        <span>Collateral Model:</span>
        <select id="app-model-select" onchange="window.syncSelectedModel(this.value)">
          <option value="gemini-4-argon" selected>gemini-4-argon (Appraisal Desk Review)</option>
          <option value="gemini-3.8-flash">gemini-3.8-flash (UAD Grid Check)</option>
        </select>
      </div>
      <button class="btn-audio-desk" onclick="window.playAppraisalDeskAudio(this)">
        🔊 Play Appraiser Desk Review Audio
      </button>
      <button class="btn-urar-audit" onclick="window.runLiveVertexAI()">
        Generate Desk Review Deficiency Notice
      </button>
    </div>
  </header>

  <main class="appraisal-container">
    <!-- TOP SANDBOX: COMP #3 SLIDERS & FANNIE MAE 15% NET / 25% GROSS PROGRESS BARS -->
    <section class="sandbox-strip">
      <div class="paper-panel">
        <div class="panel-title">
          <span>Interactive Comparable #3 Sensitivity Controls</span>
          <span style="font-family:'IBM Plex Mono',monospace;font-size:11.5px;color:var(--navy-ink);">Fannie Mae B4-1.3-09</span>
        </div>
        <p style="font-size:12.5px;color:var(--muted);">Adjust Comparable Sale #3's proximity distance and Gross Living Area (GLA) dollar adjustment to inspect real-time Fannie Mae Net (15%) and Gross (25%) adjustment guideline thresholds.</p>

        <div class="slider-grid">
          <div class="slider-card">
            <div style="display:flex;justify-content:space-between;font-size:12.5px;font-weight:700;">
              <span>Comp #3 Proximity Distance</span>
              <span id="lbl-dist" style="font-family:'IBM Plex Mono',monospace;color:var(--flag-red);">2.8 Miles (Suburban &gt; 1.0 mi)</span>
            </div>
            <input type="range" id="sl-dist" min="0.4" max="4.5" step="0.2" value="2.8" oninput="window.recalcComp3()" />
          </div>

          <div class="slider-card">
            <div style="display:flex;justify-content:space-between;font-size:12.5px;font-weight:700;">
              <span>Comp #3 GLA Adjustment ($)</span>
              <span id="lbl-gla" style="font-family:'IBM Plex Mono',monospace;color:var(--flag-red);">+$52,000</span>
            </div>
            <input type="range" id="sl-gla" min="10000" max="75000" step="2000" value="52000" oninput="window.recalcComp3()" />
          </div>
        </div>
      </div>

      <div class="paper-panel">
        <div class="panel-title">
          <span>Comp #3 Fannie Mae 15% Net / 25% Gross Adjustment Guidelines</span>
          <span id="comp3-overall-badge" class="badge-flag">EXCEEDS 15% NET / 25% GROSS</span>
        </div>

        <div class="prog-row">
          <div class="prog-top">
            <span>Net Adjustment % of Sale Price (15.0% Fannie Mae Benchmark)</span>
            <span id="lbl-net-pct" style="font-family:'IBM Plex Mono',monospace;color:var(--flag-red);">+19.3% ($82,000 / $425,000)</span>
          </div>
          <div class="prog-track">
            <div class="prog-fill" id="bar-net" style="width:77%;background:var(--flag-red);"></div>
          </div>
        </div>

        <div class="prog-row" style="margin-bottom:0;">
          <div class="prog-top">
            <span>Gross Adjustment % of Sale Price (25.0% Fannie Mae Benchmark)</span>
            <span id="lbl-gross-pct" style="font-family:'IBM Plex Mono',monospace;color:var(--flag-red);">27.8% ($118,000 / $425,000)</span>
          </div>
          <div class="prog-track">
            <div class="prog-fill" id="bar-gross" style="width:88%;background:var(--flag-red);"></div>
          </div>
        </div>
      </div>
    </section>

    <!-- SIDE-BY-SIDE FORM 1004 URAR COMPARABLE SALES GRID -->
    <section class="urar-grid-card">
      <table class="urar-table">
        <thead>
          <tr>
            <th style="width:22%;">Form 1004 Sales Comparison Feature</th>
            <th style="width:19.5%;">Subject Property<br/><span style="font-size:11.5px;font-family:'DM Sans',sans-serif;font-weight:500;">418 Elmhurst Ave, Royal Oak</span></th>
            <th style="width:19.5%;">Comparable Sale #1<br/><span style="font-size:11.5px;font-family:'DM Sans',sans-serif;font-weight:500;">512 Catalpa Dr, Royal Oak</span></th>
            <th style="width:19.5%;">Comparable Sale #2<br/><span style="font-size:11.5px;font-family:'DM Sans',sans-serif;font-weight:500;">704 Forestdale Rd, Royal Oak</span></th>
            <th style="width:19.5%;background:#FEF2F2;color:var(--flag-red);">Comparable Sale #3 (Flagged)<br/><span style="font-size:11.5px;font-family:'DM Sans',sans-serif;font-weight:500;">1940 Coolidge Hwy, Berkley</span></th>
          </tr>
        </thead>
        <tbody>
          <tr class="cat-row"><td colspan="5">Proximity, Sale Price &amp; UAD Verification</td></tr>
          <tr>
            <td><strong>Proximity to Subject</strong></td>
            <td>Subject Property</td>
            <td>0.38 miles N <span class="badge-ok">Within 1.0 mi</span></td>
            <td>0.64 miles SE <span class="badge-ok">Within 1.0 mi</span></td>
            <td class="comp3-violation" id="cell-c3-dist">2.80 miles W (Cross-Boundary)</td>
          </tr>
          <tr>
            <td><strong>Sale Price</strong></td>
            <td style="font-family:'IBM Plex Mono',monospace;font-weight:700;">$460,000 (Contract)</td>
            <td style="font-family:'IBM Plex Mono',monospace;font-weight:700;">$455,000</td>
            <td style="font-family:'IBM Plex Mono',monospace;font-weight:700;">$468,000</td>
            <td class="comp3-col" style="font-family:'IBM Plex Mono',monospace;font-weight:700;">$425,000</td>
          </tr>
          <tr class="cat-row"><td colspan="5">Value Adjustments (UAD Quality, Condition &amp; Gross Living Area)</td></tr>
          <tr>
            <td><strong>Site / Location</strong></td>
            <td>N;Res;Suburban (6,500 sf)</td>
            <td>N;Res ($0)</td>
            <td>N;Res ($0)</td>
            <td class="comp3-col">B;Arterial (+$18,000)</td>
          </tr>
          <tr>
            <td><strong>Quality &amp; Condition (UAD)</strong></td>
            <td>Q3 / C2 (Remodeled Kitchen)</td>
            <td>Q3 / C2 ($0)</td>
            <td>Q3 / C3 (+$10,000)</td>
            <td class="comp3-col">Q4 / C3 (+$30,000)</td>
          </tr>
          <tr>
            <td><strong>Gross Living Area (GLA @ $95/sf)</strong></td>
            <td>2,180 sq. ft.</td>
            <td>2,120 sq. ft. (+$5,700)</td>
            <td>2,290 sq. ft. (-$10,450)</td>
            <td class="comp3-violation" id="cell-c3-gla">1,632 sq. ft. (+$52,000)</td>
          </tr>
          <tr>
            <td><strong>Basement &amp; Finished Rooms Below</strong></td>
            <td>1,000 sf / 600 sf Fin</td>
            <td>1,000 sf / 600 sf ($0)</td>
            <td>1,000 sf / 0 sf (+$12,000)</td>
            <td class="comp3-col">1,000 sf / 850 sf (-$18,000)</td>
          </tr>
          <tr class="cat-row"><td colspan="5">Net &amp; Gross Adjustment Summary (Fannie Mae B4-1.3-09)</td></tr>
          <tr>
            <td><strong>Net Adjustment (Total $ / %)</strong></td>
            <td>—</td>
            <td style="font-family:'IBM Plex Mono',monospace;color:var(--comp-green);font-weight:700;">+$5,700 (+1.25%) <span class="badge-ok">PASS</span></td>
            <td style="font-family:'IBM Plex Mono',monospace;color:var(--comp-green);font-weight:700;">+$11,550 (+2.47%) <span class="badge-ok">PASS</span></td>
            <td class="comp3-violation" id="cell-c3-net" style="font-family:'IBM Plex Mono',monospace;">+$82,000 (+19.3%) [&gt;15% Flag]</td>
          </tr>
          <tr>
            <td><strong>Gross Adjustment (Total $ / %)</strong></td>
            <td>—</td>
            <td style="font-family:'IBM Plex Mono',monospace;color:var(--comp-green);font-weight:700;">$5,700 (1.25%) <span class="badge-ok">PASS</span></td>
            <td style="font-family:'IBM Plex Mono',monospace;color:var(--comp-green);font-weight:700;">$32,450 (6.93%) <span class="badge-ok">PASS</span></td>
            <td class="comp3-violation" id="cell-c3-gross" style="font-family:'IBM Plex Mono',monospace;">$118,000 (27.8%) [&gt;25% Flag]</td>
          </tr>
          <tr>
            <td><strong>Adjusted Sale Price of Comparables</strong></td>
            <td style="font-family:'IBM Plex Mono',monospace;font-weight:800;color:var(--navy-ink);">$460,000 Indicated</td>
            <td style="font-family:'IBM Plex Mono',monospace;font-weight:800;">$460,700</td>
            <td style="font-family:'IBM Plex Mono',monospace;font-weight:800;">$479,550</td>
            <td class="comp3-col" id="cell-c3-adjprice" style="font-family:'IBM Plex Mono',monospace;font-weight:800;">$507,000</td>
          </tr>
        </tbody>
      </table>
    </section>

    <!-- APPRAISAL DESK REVIEW MEMORANDUM -->
    <section class="paper-panel">
      <div class="panel-title">
        <span>Collateral Underwriter (CU) &amp; Appraiser Desk Review Determination</span>
        <span id="live-model-pill" style="font-family:'IBM Plex Mono',monospace;font-size:11.5px;color:var(--navy-ink);">gemini-4-argon</span>
      </div>
      <div id="appraisal-review-output" style="font-size:13px;line-height:1.65;color:var(--ink);background:#FAF8F5;padding:14px 16px;border:1px solid #E7E5E4;border-radius:6px;">
        <strong>FORM 1004 COLLATERAL DESK REVIEW FINDING:</strong><br/>
        • <strong>Comparable #1 &amp; #2 Compliant:</strong> Located within 0.64 miles in Royal Oak with Net Adjustments of 1.25% and 2.47%, strongly supporting the $460,000 contract price.<br/>
        • <strong>Comparable #3 Anomaly Flagged (B4-1.3-09):</strong> Comp #3 is located 2.80 miles away across municipal lines and requires a +$52,000 GLA adjustment, resulting in <strong>+19.3% Net</strong> (exceeding the 15% benchmark) and <strong>27.8% Gross</strong> (exceeding the 25% benchmark). Revision request prepared for licensed appraiser to supply a closer Royal Oak bracketed sale or market commentary.
      </div>
    </section>
  </main>

  <script>
    window.recalcComp3 = function() {{
      const dist = parseFloat(document.getElementById('sl-dist').value || 2.8);
      const glaAdj = parseFloat(document.getElementById('sl-gla').value || 52000);
      const salePrice = 425000;
      const otherPos = 48000; // +$18k site + $30k Q4/C3
      const otherNeg = 18000; // -$18k basement

      const netDollar = otherPos + glaAdj - otherNeg;
      const grossDollar = otherPos + glaAdj + otherNeg;
      const netPct = (netDollar / salePrice) * 100.0;
      const grossPct = (grossDollar / salePrice) * 100.0;
      const adjPrice = salePrice + netDollar;

      document.getElementById('lbl-dist').innerText = dist.toFixed(1) + (dist > 1.0 ? ' Miles (Suburban > 1.0 mi)' : ' Miles (Compliant <= 1.0 mi)');
      document.getElementById('lbl-gla').innerText = '+$' + glaAdj.toLocaleString();
      document.getElementById('cell-c3-dist').innerText = dist.toFixed(2) + ' miles W ' + (dist > 1.0 ? '(Exceeds 1.0 mi)' : '(Within 1.0 mi)');
      document.getElementById('cell-c3-gla').innerText = '1,632 sq. ft. (+$' + glaAdj.toLocaleString() + ')';
      document.getElementById('cell-c3-net').innerText = '+$' + netDollar.toLocaleString() + ' (+' + netPct.toFixed(1) + '%) ' + (netPct > 15 ? '[>15% Flag]' : '[PASS]');
      document.getElementById('cell-c3-gross').innerText = '$' + grossDollar.toLocaleString() + ' (' + grossPct.toFixed(1) + '%) ' + (grossPct > 25 ? '[>25% Flag]' : '[PASS]');
      document.getElementById('cell-c3-adjprice').innerText = '$' + adjPrice.toLocaleString();

      document.getElementById('lbl-net-pct').innerText = '+' + netPct.toFixed(1) + '% ($' + netDollar.toLocaleString() + ' / $425,000)';
      document.getElementById('lbl-gross-pct').innerText = grossPct.toFixed(1) + '% ($' + grossDollar.toLocaleString() + ' / $425,000)';

      const barNet = document.getElementById('bar-net');
      barNet.style.width = Math.min(100, (netPct / 25) * 100) + '%';
      barNet.style.background = netPct > 15 ? 'var(--flag-red)' : 'var(--comp-green)';

      const barGross = document.getElementById('bar-gross');
      barGross.style.width = Math.min(100, (grossPct / 35) * 100) + '%';
      barGross.style.background = grossPct > 25 ? 'var(--flag-red)' : 'var(--comp-green)';

      const badge = document.getElementById('comp3-overall-badge');
      if (netPct > 15 || grossPct > 25 || dist > 1.0) {{
        badge.className = 'badge-flag';
        badge.innerText = 'EXCEEDS FANNIE MAE BENCHMARK';
      }} else {{
        badge.className = 'badge-ok';
        badge.innerText = 'WITHIN 15% NET / 25% GROSS';
      }}
    }};

    window.playAppraisalDeskAudio = function(btnEl) {{
      const netTxt = document.getElementById('lbl-net-pct').innerText;
      const grossTxt = document.getElementById('lbl-gross-pct').innerText;
      const script = "Collateral Underwriter Desk Review for 418 Elmhurst Avenue, Royal Oak, Michigan, appraised at 460,000 dollars. Comparable sales 1 and 2 are located within 0.64 miles and have minimal net adjustments under 2.5 percent. However, Comparable Sale 3 is flagged for Fannie Mae B4-1.3-09 review with a net adjustment of " + netTxt + " against the 15 percent guideline and a gross adjustment of " + grossTxt + " against the 25 percent guideline.";
      if (window.playLiveCallClip) {{
        window.playLiveCallClip(script, "Charon", "Chief Residential Appraiser", btnEl);
      }}
    }};

    window.runLiveVertexAI = async function() {{
      const model = window.getSelectedModel ? window.getSelectedModel() : 'gemini-4-argon';
      const outEl = document.getElementById('appraisal-review-output');
      const netTxt = document.getElementById('lbl-net-pct').innerText;
      const grossTxt = document.getElementById('lbl-gross-pct').innerText;
      outEl.innerHTML = '<em>Running Vertex AI (' + model + ') Form 1004 URAR Collateral Desk Review...</em>';
      try {{
        const res = await fetch('/api/run-demo', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{
            code: '2.4',
            model: model,
            user_input: 'Generate a Fannie Mae Form 1004 Appraisal Desk Review memo for 418 Elmhurst Ave, Royal Oak ($460,000) where Comp #3 has Net Adjustment ' + netTxt + ' and Gross Adjustment ' + grossTxt + '.'
          }})
        }});
        const data = await res.json();
        const text = data.output || data.response || data.result || '';
        if (text) {{
          outEl.innerHTML = '<strong>VERTEX AI (' + model.toUpperCase() + ') DESK REVIEW RULING:</strong><br/>' + text.replace(/\\n/g, '<br/>');
        }} else {{
          outEl.innerHTML = '<strong>FORM 1004 DESK REVIEW COMPLETE (' + model + '):</strong> Comp #3 flagged for 15% Net / 25% Gross addendum commentary per Fannie Mae B4-1.3-09.';
        }}
      }} catch (e) {{
        outEl.innerHTML = '<strong>FORM 1004 DESK REVIEW COMPLETE:</strong> Comp #3 flagged for 15% Net / 25% Gross addendum commentary per Fannie Mae B4-1.3-09.';
      }}
    }};
  </script>

  {floating_bar}
</body>
</html>"""
