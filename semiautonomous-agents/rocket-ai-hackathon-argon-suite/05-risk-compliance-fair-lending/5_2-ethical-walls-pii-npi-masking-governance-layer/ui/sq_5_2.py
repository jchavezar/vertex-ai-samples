# -*- coding: utf-8 -*-
"""Square 5.2: Fair Lending Disparate Impact Tester — Vertex AI + BigQuery ML
Design Style: The Economist / Stata Quantitative Econometrics Report
(#FFFFFF crisp white report canvas, #E3120B Economist red top hairline rule,
#0F172A ink, #0284C7 chart blue, Bricolage Grotesque + IBM Plex Sans).
"""

from shared.standalone_uis.base_helpers import render_floating_control_bar_and_drawer


def render_sq_5_2(auth_token: str) -> str:
    code = "5.2"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Fair Lending Disparate Impact Tester | Quantitative Econometrics Report</title>
  <link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,600;12..96,700;12..96,800&family=IBM+Plex+Sans:ital,wght@0,400;0,500;0,600;0,700;1,400&family=IBM+Plex+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    :root {{
      --canvas: #FFFFFF;
      --surface-gray: #F8FAFC;
      --economist-red: #E3120B;
      --ink: #0F172A;
      --ink-secondary: #475569;
      --chart-blue: #0284C7;
      --chart-navy: #0369A1;
      --pass-green: #15803D;
      --pass-bg: #F0FDF4;
      --fail-red: #B91C1C;
      --fail-bg: #FEF2F2;
      --rule: #CBD5E1;
      --rule-light: #E2E8F0;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      background-color: var(--canvas);
      color: var(--ink);
      font-family: 'IBM Plex Sans', -apple-system, BlinkMacSystemFont, sans-serif;
      border-top: 6px solid var(--economist-red);
      min-height: 100vh;
      padding-bottom: 88px;
    }}
    .mono {{ font-family: 'IBM Plex Mono', monospace; }}
    .display {{ font-family: 'Bricolage Grotesque', sans-serif; }}

    /* Top Economist / Stata Header */
    .report-header {{
      max-width: 1400px;
      margin: 0 auto;
      padding: 20px 32px 18px;
      border-bottom: 2px solid var(--ink);
      display: flex;
      justify-content: space-between;
      align-items: flex-end;
      flex-wrap: wrap;
      gap: 16px;
    }}
    .economist-tag {{
      display: inline-block;
      background: var(--economist-red);
      color: #FFFFFF;
      font-weight: 700;
      font-size: 11px;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      padding: 4px 10px;
      margin-bottom: 8px;
    }}
    .report-title {{
      font-family: 'Bricolage Grotesque', sans-serif;
      font-size: 28px;
      font-weight: 800;
      color: var(--ink);
      letter-spacing: -0.02em;
      line-height: 1.15;
    }}
    .report-sub {{
      font-size: 14px;
      color: var(--ink-secondary);
      margin-top: 4px;
    }}
    .header-controls {{
      display: flex;
      align-items: center;
      gap: 12px;
      flex-wrap: wrap;
    }}
    .model-box {{
      display: flex;
      align-items: center;
      gap: 6px;
      background: var(--surface-gray);
      border: 1px solid var(--rule);
      padding: 6px 12px;
      border-radius: 4px;
      font-size: 12px;
      font-weight: 600;
    }}
    .model-box select {{
      background: transparent;
      border: none;
      font-family: 'IBM Plex Mono', monospace;
      font-size: 12px;
      font-weight: 700;
      color: var(--chart-navy);
      outline: none;
      cursor: pointer;
    }}
    .audio-btn {{
      background: var(--ink);
      color: #FFFFFF;
      border: none;
      padding: 10px 16px;
      border-radius: 4px;
      font-family: 'IBM Plex Sans', sans-serif;
      font-size: 13px;
      font-weight: 600;
      cursor: pointer;
      transition: 0.15s;
    }}
    .audio-btn:hover {{ background: #1E293B; }}

    /* KPI Strip (Stata Summary Statistics) */
    .stata-strip {{
      max-width: 1400px;
      margin: 0 auto;
      padding: 16px 32px;
      border-bottom: 1px solid var(--rule);
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 20px;
      background: #FCFDFE;
    }}
    @media (max-width: 900px) {{
      .stata-strip {{ grid-template-columns: repeat(2, 1fr); }}
    }}
    .kpi-cell {{
      border-left: 3px solid var(--chart-blue);
      padding-left: 14px;
    }}
    .kpi-cell.alert {{ border-left-color: var(--economist-red); }}
    .kpi-label {{
      font-size: 11px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: var(--ink-secondary);
    }}
    .kpi-val {{
      font-family: 'IBM Plex Mono', monospace;
      font-size: 24px;
      font-weight: 700;
      margin-top: 2px;
    }}
    .kpi-sub {{
      font-size: 12px;
      color: var(--ink-secondary);
      margin-top: 2px;
    }}

    /* Main Two-Column Econometrics Layout */
    .econ-grid {{
      max-width: 1400px;
      margin: 24px auto;
      padding: 0 32px;
      display: grid;
      grid-template-columns: 1.05fr 1.15fr;
      gap: 32px;
    }}
    @media (max-width: 1040px) {{
      .econ-grid {{ grid-template-columns: 1fr; }}
    }}

    .econ-section {{
      border-top: 2px solid var(--ink);
      padding-top: 14px;
      display: flex;
      flex-direction: column;
      gap: 18px;
    }}
    .sec-head {{
      display: flex;
      justify-content: space-between;
      align-items: baseline;
    }}
    .sec-title {{
      font-family: 'Bricolage Grotesque', sans-serif;
      font-size: 19px;
      font-weight: 700;
      color: var(--ink);
    }}
    .sec-caption {{
      font-size: 12.5px;
      color: var(--ink-secondary);
    }}

    /* Feature Drop Toggles (Less Discriminatory Alternative Simulator) */
    .feature-card {{
      background: var(--surface-gray);
      border: 1px solid var(--rule-light);
      border-radius: 4px;
      padding: 14px 16px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 14px;
      transition: 0.15s;
    }}
    .feature-card.dropped {{
      background: #F0FDF4;
      border-color: #86EFAC;
    }}
    .feat-name {{
      font-weight: 700;
      font-size: 14px;
      color: var(--ink);
      display: flex;
      align-items: center;
      gap: 8px;
    }}
    .feat-desc {{
      font-size: 12.5px;
      color: var(--ink-secondary);
      margin-top: 3px;
    }}
    .toggle-btn {{
      padding: 7px 13px;
      border-radius: 4px;
      font-family: 'IBM Plex Mono', monospace;
      font-size: 11.5px;
      font-weight: 600;
      cursor: pointer;
      border: 1px solid var(--rule);
      background: #FFFFFF;
      color: var(--ink);
      white-space: nowrap;
    }}
    .toggle-btn.active-drop {{
      background: var(--pass-green);
      color: #FFFFFF;
      border-color: var(--pass-green);
    }}

    /* Horizontal Statistical Bar Charts (The Economist Style) */
    .chart-box {{
      background: #FFFFFF;
      border: 1px solid var(--rule);
      padding: 20px 22px;
      position: relative;
    }}
    .chart-header {{
      border-left: 4px solid var(--economist-red);
      padding-left: 10px;
      margin-bottom: 18px;
    }}
    .chart-title {{
      font-weight: 700;
      font-size: 15px;
      color: var(--ink);
    }}
    .chart-subtitle {{
      font-size: 12px;
      color: var(--ink-secondary);
    }}
    .bar-row {{
      margin-bottom: 16px;
    }}
    .bar-label-line {{
      display: flex;
      justify-content: space-between;
      font-size: 12.5px;
      font-weight: 600;
      margin-bottom: 5px;
    }}
    .bar-track {{
      height: 24px;
      background: #F1F5F9;
      position: relative;
      border-radius: 2px;
      overflow: visible;
    }}
    .bar-fill {{
      height: 100%;
      background: var(--chart-blue);
      transition: width 0.35s cubic-bezier(0.16, 1, 0.3, 1), background-color 0.25s;
      border-radius: 2px;
    }}
    .bar-fill.fail {{ background: var(--economist-red); }}
    .bar-fill.pass {{ background: var(--chart-blue); }}
    .threshold-line {{
      position: absolute;
      left: 80%;
      top: -6px;
      bottom: -6px;
      width: 2px;
      background: var(--ink);
      z-index: 4;
    }}
    .threshold-tag {{
      position: absolute;
      left: 80%;
      top: -22px;
      transform: translateX(-50%);
      font-family: 'IBM Plex Mono', monospace;
      font-size: 10px;
      font-weight: 700;
      background: var(--ink);
      color: #FFFFFF;
      padding: 1px 5px;
      border-radius: 2px;
      white-space: nowrap;
    }}

    /* Stata Regression Table */
    .stata-table {{
      width: 100%;
      border-collapse: collapse;
      font-family: 'IBM Plex Mono', monospace;
      font-size: 12px;
      border-top: 2px solid var(--ink);
      border-bottom: 2px solid var(--ink);
    }}
    .stata-table th {{
      text-align: left;
      padding: 8px 10px;
      border-bottom: 1px solid var(--ink);
      color: var(--ink);
      font-weight: 700;
    }}
    .stata-table td {{
      padding: 8px 10px;
      border-bottom: 1px solid var(--rule-light);
    }}
    .status-badge {{
      display: inline-block;
      padding: 2px 8px;
      border-radius: 3px;
      font-weight: 700;
      font-size: 11px;
    }}
    .status-badge.fail {{ background: var(--fail-bg); color: var(--fail-red); border: 1px solid #FECACA; }}
    .status-badge.pass {{ background: var(--pass-bg); color: var(--pass-green); border: 1px solid #BBF7D0; }}

    .action-btn {{
      background: var(--chart-blue);
      color: #FFFFFF;
      border: none;
      padding: 10px 16px;
      border-radius: 4px;
      font-family: 'IBM Plex Sans', sans-serif;
      font-size: 13px;
      font-weight: 600;
      cursor: pointer;
    }}
    .action-btn:hover {{ background: var(--chart-navy); }}
    .ai-memo {{
      background: var(--surface-gray);
      border: 1px solid var(--rule);
      padding: 14px;
      font-size: 13px;
      line-height: 1.6;
      display: none;
      white-space: pre-wrap;
    }}
  </style>
</head>
<body>

  <!-- Top Economist / Stata Report Header -->
  <header class="report-header">
    <div>
      <span class="economist-tag">QUANTITATIVE ECONOMETRICS REPORT · ECOA / REG B &amp; EEOC 4/5THS RULE</span>
      <h1 class="report-title">Fair Lending Disparate Impact Tester</h1>
      <p class="report-sub">
        Rocket Automated Underwriting Model (`v4.8-Candidate`) · HMDA Cohort Sample `N = 142,850` Applications
      </p>
    </div>
    <div class="header-controls">
      <div class="model-box">
        <span>Model:</span>
        <select id="app-model-select" onchange="window.syncSelectedModel(this.value)">
          <option value="gemini-4-argon">gemini-4-argon</option>
          <option value="gemini-3.8-flash">gemini-3.8-flash</option>
        </select>
      </div>
      <button class="audio-btn" onclick="window.playEconometricsAudio(this)">
        🔊 Listen to Fair Lending Econometrics Debrief
      </button>
    </div>
  </header>

  <!-- Stata Summary Metrics Strip -->
  <section class="stata-strip">
    <div class="kpi-cell alert" id="air-kpi-cell">
      <div class="kpi-label">Adverse Impact Ratio (AIR · Minority / Ref)</div>
      <div class="kpi-val" id="air-kpi-val" style="color:var(--economist-red);">0.762 [FAIL]</div>
      <div class="kpi-sub">Statutory EEOC 4/5ths Threshold: <strong>≥ 0.800</strong></div>
    </div>
    <div class="kpi-cell">
      <div class="kpi-label">Two-Sample Z-Stat (p-value)</div>
      <div class="kpi-val" id="zstat-val">-4.82 (p &lt; 0.001)</div>
      <div class="kpi-sub" id="zstat-sub">Statistically Significant Disparity</div>
    </div>
    <div class="kpi-cell">
      <div class="kpi-label">Model ROC-AUC (Default Prediction)</div>
      <div class="kpi-val" id="auc-val" style="color:var(--chart-blue);">0.844</div>
      <div class="kpi-sub">Target Credit Risk Floor: ≥ 0.835</div>
    </div>
    <div class="kpi-cell">
      <div class="kpi-label">CFPB Less Discriminatory Alt (LDA)</div>
      <div class="kpi-val" id="lda-status" style="color:var(--economist-red);">ACTION REQ</div>
      <div class="kpi-sub" id="lda-sub">Toggle proxy features below to remediate</div>
    </div>
  </section>

  <!-- Main Two-Column Econometrics Workspace -->
  <main class="econ-grid">
    <!-- Left Column: Feature Drop Toggles (Less Discriminatory Alternative Simulator) -->
    <section class="econ-section">
      <div class="sec-head">
        <div>
          <h2 class="sec-title">1. Less Discriminatory Alternative (LDA) Feature Ablation</h2>
          <p class="sec-caption">Drop high-disparity proxy variables from `Rocket-AUS-v4.8` and observe live AIR recalculation.</p>
        </div>
      </div>

      <!-- Feature 1: Non-Traditional Rent History Penalty -->
      <div class="feature-card" id="feat-card-rent">
        <div>
          <div class="feat-name">
            <span>Var 14: Non-Traditional Rent History Penalty</span>
            <span class="status-badge fail" id="badge-rent">SHAP Disparity: +0.132 AIR Penalty</span>
          </div>
          <div class="feat-desc">
            Penalizes applicants paying rent via peer-to-peer apps (Zelle/Venmo) rather than institutional property management portals.
          </div>
        </div>
        <button class="toggle-btn" id="btn-drop-rent" onclick="window.toggleFeature('rent')">
          Drop Feature from Model
        </button>
      </div>

      <!-- Feature 2: ZIP-3 Aggregate HPI Volatility Index -->
      <div class="feature-card" id="feat-card-zip">
        <div>
          <div class="feat-name">
            <span>Var 22: Census Tract HPI 5-Yr Volatility Weight</span>
            <span class="status-badge fail" id="badge-zip">SHAP Disparity: +0.028 AIR Penalty</span>
          </div>
          <div class="feat-desc">
            Applies higher reserve requirement in neighborhoods with high historical appraisal variance (geographic redlining proxy risk).
          </div>
        </div>
        <button class="toggle-btn" id="btn-drop-zip" onclick="window.toggleFeature('zip')">
          Drop Feature from Model
        </button>
      </div>

      <!-- Feature 3: Positive Cash-Flow Bank Statement Inclusion -->
      <div class="feature-card" id="feat-card-cashflow">
        <div>
          <div class="feat-name">
            <span>Var 31: 12-Mo Verified Utility &amp; Cash-Flow Inclusion</span>
            <span class="status-badge pass">Fairness Booster (+0.019 AIR)</span>
          </div>
          <div class="feat-desc">
            Credits thin-file first-time homebuyers for 12 consecutive on-time utility and telecom drafts verified via Plaid.
          </div>
        </div>
        <button class="toggle-btn" id="btn-drop-cashflow" onclick="window.toggleFeature('cashflow')">
          Enable Booster (+0.019)
        </button>
      </div>

      <!-- Quick Remediation Preset -->
      <div style="display:flex;gap:10px;flex-wrap:wrap;padding-top:6px;">
        <button class="action-btn" onclick="window.applyRecommendedLDA()">
          ✓ Apply Recommended LDA Spec (Drop Rent Penalty → 0.894 PASS)
        </button>
        <button class="toggle-btn" onclick="window.resetBaseline()">
          Reset to Unmitigated Baseline (0.762 FAIL)
        </button>
      </div>

      <!-- Stata Output Table -->
      <div>
        <div class="mono" style="font-size:11px;font-weight:700;color:var(--ink-secondary);margin-bottom:6px;">
          STATA / BIGQUERY ML LOGIT DECOMPOSITION · PROTECTED CLASS COHORTS (HMDA 2026)
        </div>
        <table class="stata-table">
          <thead>
            <tr>
              <th>Demographic Cohort</th>
              <th>Sample (N)</th>
              <th>Approval Rate</th>
              <th>AIR vs. Ref</th>
              <th>EEOC 4/5ths</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>Reference Group (Non-Hispanic White)</td>
              <td>88,410</td>
              <td>78.4%</td>
              <td>1.000</td>
              <td><span class="status-badge pass">REFERENCE</span></td>
            </tr>
            <tr>
              <td>Black / African American Applicants</td>
              <td>26,120</td>
              <td id="rate-black">59.7%</td>
              <td id="air-black" style="font-weight:700;">0.762</td>
              <td id="status-black"><span class="status-badge fail">FAIL (&lt;0.80)</span></td>
            </tr>
            <tr>
              <td>Hispanic / Latino Applicants</td>
              <td>21,490</td>
              <td id="rate-hisp">62.1%</td>
              <td id="air-hisp" style="font-weight:700;">0.792</td>
              <td id="status-hisp"><span class="status-badge fail">FAIL (&lt;0.80)</span></td>
            </tr>
            <tr>
              <td>Female Head-of-Household</td>
              <td>34,900</td>
              <td id="rate-fem">74.1%</td>
              <td id="air-fem" style="font-weight:700;">0.945</td>
              <td id="status-fem"><span class="status-badge pass">PASS (≥0.80)</span></td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <!-- Right Column: Horizontal Statistical Bar Charts & Vertex AI Econometric Memo -->
    <section class="econ-section">
      <div class="sec-head">
        <div>
          <h2 class="sec-title">2. Adverse Impact Ratio (AIR) vs. EEOC 0.800 Statutory Floor</h2>
          <p class="sec-caption">Horizontal econometric comparison before and after removing `Non-Traditional Rent History Penalty`.</p>
        </div>
      </div>

      <div class="chart-box">
        <div class="chart-header">
          <div class="chart-title">Adverse Impact Ratio by Protected Class Cohort</div>
          <div class="chart-subtitle">Ratio of Protected Cohort Approval Rate to Reference Cohort (1.00 = Parity · 0.80 = EEOC Minimum)</div>
        </div>

        <div style="margin-top:28px;position:relative;">
          <!-- Row 1: Black / African American -->
          <div class="bar-row">
            <div class="bar-label-line">
              <span>Black / African American Cohort</span>
              <span class="mono" id="chart-lbl-black" style="color:var(--economist-red);font-weight:700;">AIR: 0.762 (FAIL)</span>
            </div>
            <div class="bar-track">
              <div class="threshold-tag">EEOC 4/5ths Floor (0.800)</div>
              <div class="threshold-line"></div>
              <div class="bar-fill fail" id="chart-bar-black" style="width:76.2%;"></div>
            </div>
          </div>

          <!-- Row 2: Hispanic / Latino -->
          <div class="bar-row">
            <div class="bar-label-line">
              <span>Hispanic / Latino Cohort</span>
              <span class="mono" id="chart-lbl-hisp" style="color:var(--economist-red);font-weight:700;">AIR: 0.792 (FAIL)</span>
            </div>
            <div class="bar-track">
              <div class="threshold-line"></div>
              <div class="bar-fill fail" id="chart-bar-hisp" style="width:79.2%;"></div>
            </div>
          </div>

          <!-- Row 3: Female Head of Household -->
          <div class="bar-row">
            <div class="bar-label-line">
              <span>Female Head-of-Household Cohort</span>
              <span class="mono" id="chart-lbl-fem" style="color:var(--chart-blue);font-weight:700;">AIR: 0.945 (PASS)</span>
            </div>
            <div class="bar-track">
              <div class="threshold-line"></div>
              <div class="bar-fill pass" id="chart-bar-fem" style="width:94.5%;"></div>
            </div>
          </div>

          <!-- Row 4: Baseline Reference -->
          <div class="bar-row" style="margin-bottom:4px;">
            <div class="bar-label-line">
              <span>Reference Benchmark Cohort</span>
              <span class="mono" style="color:#475569;font-weight:700;">AIR: 1.000 (PARITY)</span>
            </div>
            <div class="bar-track">
              <div class="threshold-line"></div>
              <div class="bar-fill pass" style="width:100%;background:#64748B;"></div>
            </div>
          </div>
        </div>
      </div>

      <!-- Econometric Finding Callout -->
      <div style="background:#F8FAFC;border:1px solid var(--rule);border-left:4px solid var(--chart-blue);padding:16px 18px;font-size:13.5px;line-height:1.6;">
        <div class="mono" style="font-size:11px;font-weight:700;color:var(--chart-navy);text-transform:uppercase;margin-bottom:4px;">
          ECONOMETRIC FINDING · LESS DISCRIMINATORY ALTERNATIVE (LDA) CERTIFICATION
        </div>
        <p id="econ-narrative">
          In the baseline candidate model (<code>v4.8-Baseline</code>), <strong>Var 14 (Non-Traditional Rent History Penalty)</strong> depresses the Black/African American Adverse Impact Ratio to <strong>0.762</strong>, violating the EEOC 4/5ths threshold (<code>0.800</code>). Dropping Var 14 raises the AIR to <strong>0.894 PASS</strong> while preserving credit ROC-AUC at <strong>0.842</strong> (only a -0.002 delta, statistically indistinguishable at α = 0.05).
        </p>
      </div>

      <div style="display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap;">
        <button class="action-btn" onclick="window.runLiveVertexAI()">
          ⚡ Generate Formal CFPB Fair Lending LDA Filing via Vertex AI
        </button>
        <span class="mono" style="font-size:11.5px;color:var(--ink-secondary);">
          BigQuery Table: <code>vtxdemos.rocket_hmda.aus_v48_audit</code>
        </span>
      </div>

      <div id="ai-econ-output" class="ai-memo"></div>
    </section>
  </main>

  <script>
    const state = {{
      rentDropped: false,
      zipDropped: false,
      cashflowBoost: false
    }};

    function recalculateAIR() {{
      let blackAir = 0.762;
      let hispAir = 0.792;
      let femAir = 0.945;
      let auc = 0.844;

      if (state.rentDropped) {{
        blackAir += 0.132;
        hispAir += 0.104;
        femAir += 0.018;
        auc -= 0.002;
      }}
      if (state.zipDropped) {{
        blackAir += 0.028;
        hispAir += 0.024;
        auc -= 0.001;
      }}
      if (state.cashflowBoost) {{
        blackAir += 0.019;
        hispAir += 0.021;
        auc += 0.003;
      }}

      blackAir = Math.min(0.985, blackAir);
      hispAir = Math.min(0.985, hispAir);
      femAir = Math.min(0.990, femAir);

      const blackPass = blackAir >= 0.800;
      const hispPass = hispAir >= 0.800;
      const allPass = blackPass && hispPass;

      // Update Top KPI
      const kpiCell = document.getElementById('air-kpi-cell');
      const kpiVal = document.getElementById('air-kpi-val');
      kpiVal.innerText = `${{blackAir.toFixed(3)}} [${{allPass ? 'PASS' : 'FAIL'}}]`;
      kpiVal.style.color = allPass ? 'var(--pass-green)' : 'var(--economist-red)';
      kpiCell.style.borderLeftColor = allPass ? 'var(--pass-green)' : 'var(--economist-red)';

      document.getElementById('zstat-val').innerText = allPass ? "-1.14 (p = 0.254)" : "-4.82 (p < 0.001)";
      document.getElementById('zstat-sub').innerText = allPass ? "No Statistically Significant Disparity" : "Statistically Significant Disparity";
      document.getElementById('auc-val').innerText = auc.toFixed(3);

      const ldaSt = document.getElementById('lda-status');
      ldaSt.innerText = allPass ? "CERTIFIED PASS" : "ACTION REQ";
      ldaSt.style.color = allPass ? "var(--pass-green)" : "var(--economist-red)";
      document.getElementById('lda-sub').innerText = allPass ? "Complies with ECOA & EEOC 4/5ths Rule" : "Toggle proxy features below to remediate";

      // Update Table & Bars
      const blackRate = (78.4 * blackAir).toFixed(1) + "%";
      const hispRate = (78.4 * hispAir).toFixed(1) + "%";
      const femRate = (78.4 * femAir).toFixed(1) + "%";

      document.getElementById('rate-black').innerText = blackRate;
      document.getElementById('air-black').innerText = blackAir.toFixed(3);
      document.getElementById('status-black').innerHTML = blackPass
        ? '<span class="status-badge pass">PASS (≥0.80)</span>'
        : '<span class="status-badge fail">FAIL (&lt;0.80)</span>';

      document.getElementById('rate-hisp').innerText = hispRate;
      document.getElementById('air-hisp').innerText = hispAir.toFixed(3);
      document.getElementById('status-hisp').innerHTML = hispPass
        ? '<span class="status-badge pass">PASS (≥0.80)</span>'
        : '<span class="status-badge fail">FAIL (&lt;0.80)</span>';

      document.getElementById('rate-fem').innerText = femRate;
      document.getElementById('air-fem').innerText = femAir.toFixed(3);

      const barB = document.getElementById('chart-bar-black');
      barB.style.width = (blackAir * 100).toFixed(1) + "%";
      barB.className = "bar-fill " + (blackPass ? "pass" : "fail");
      const lblB = document.getElementById('chart-lbl-black');
      lblB.innerText = `AIR: ${{blackAir.toFixed(3)}} (${{blackPass ? 'PASS' : 'FAIL'}})`;
      lblB.style.color = blackPass ? 'var(--chart-blue)' : 'var(--economist-red)';

      const barH = document.getElementById('chart-bar-hisp');
      barH.style.width = (hispAir * 100).toFixed(1) + "%";
      barH.className = "bar-fill " + (hispPass ? "pass" : "fail");
      const lblH = document.getElementById('chart-lbl-hisp');
      lblH.innerText = `AIR: ${{hispAir.toFixed(3)}} (${{hispPass ? 'PASS' : 'FAIL'}})`;
      lblH.style.color = hispPass ? 'var(--chart-blue)' : 'var(--economist-red)';

      const barF = document.getElementById('chart-bar-fem');
      barF.style.width = (femAir * 100).toFixed(1) + "%";
      document.getElementById('chart-lbl-fem').innerText = `AIR: ${{femAir.toFixed(3)}} (PASS)`;
    }}

    window.toggleFeature = function(feat) {{
      if (feat === 'rent') {{
        state.rentDropped = !state.rentDropped;
        document.getElementById('feat-card-rent').classList.toggle('dropped', state.rentDropped);
        const b = document.getElementById('btn-drop-rent');
        b.classList.toggle('active-drop', state.rentDropped);
        b.innerText = state.rentDropped ? "✓ Dropped (LDA Active)" : "Drop Feature from Model";
      }} else if (feat === 'zip') {{
        state.zipDropped = !state.zipDropped;
        document.getElementById('feat-card-zip').classList.toggle('dropped', state.zipDropped);
        const b = document.getElementById('btn-drop-zip');
        b.classList.toggle('active-drop', state.zipDropped);
        b.innerText = state.zipDropped ? "✓ Dropped (LDA Active)" : "Drop Feature from Model";
      }} else if (feat === 'cashflow') {{
        state.cashflowBoost = !state.cashflowBoost;
        document.getElementById('feat-card-cashflow').classList.toggle('dropped', state.cashflowBoost);
        const b = document.getElementById('btn-drop-cashflow');
        b.classList.toggle('active-drop', state.cashflowBoost);
        b.innerText = state.cashflowBoost ? "✓ Booster Enabled" : "Enable Booster (+0.019)";
      }}
      recalculateAIR();
    }};

    window.applyRecommendedLDA = function() {{
      state.rentDropped = true;
      state.zipDropped = false;
      state.cashflowBoost = false;
      document.getElementById('feat-card-rent').classList.add('dropped');
      const b = document.getElementById('btn-drop-rent');
      b.classList.add('active-drop');
      b.innerText = "✓ Dropped (LDA Active)";
      document.getElementById('feat-card-zip').classList.remove('dropped');
      document.getElementById('btn-drop-zip').classList.remove('active-drop');
      document.getElementById('btn-drop-zip').innerText = "Drop Feature from Model";
      document.getElementById('feat-card-cashflow').classList.remove('dropped');
      document.getElementById('btn-drop-cashflow').classList.remove('active-drop');
      document.getElementById('btn-drop-cashflow').innerText = "Enable Booster (+0.019)";
      recalculateAIR();
    }};

    window.resetBaseline = function() {{
      state.rentDropped = false;
      state.zipDropped = false;
      state.cashflowBoost = false;
      ['rent', 'zip', 'cashflow'].forEach(k => {{
        document.getElementById('feat-card-' + k).classList.remove('dropped');
        document.getElementById('btn-drop-' + k).classList.remove('active-drop');
      }});
      document.getElementById('btn-drop-rent').innerText = "Drop Feature from Model";
      document.getElementById('btn-drop-zip').innerText = "Drop Feature from Model";
      document.getElementById('btn-drop-cashflow').innerText = "Enable Booster (+0.019)";
      recalculateAIR();
    }};

    window.playEconometricsAudio = function(btnEl) {{
      const msg = "Fair Lending Econometrics Debrief for Rocket Automated Underwriting Version 4.8. Across 142,850 HMDA applications, our baseline candidate model exhibited an Adverse Impact Ratio of 0.762 for Black and African American applicants, falling below the EEOC four-fifths threshold of 0.800. SHAP decomposition isolated Variable 14, the Non-Traditional Rent History Penalty, as the primary driver. Dropping Variable 14 raises the Adverse Impact Ratio to 0.894 PASS while retaining a 0.842 ROC-AUC.";
      window.playLiveCallClip(msg, "Puck", "Rocket Chief Fair Lending Econometrician", btnEl);
    }};

    window.runLiveVertexAI = async function() {{
      const out = document.getElementById('ai-econ-output');
      out.style.display = 'block';
      const model = window.getSelectedModel ? window.getSelectedModel() : 'gemini-4-argon';
      out.textContent = `Running Vertex AI Fair Lending econometric review (${{model}})...`;
      const prompt = `Draft a CFPB Regulation B Less Discriminatory Alternative (LDA) econometric certification memo. Baseline AIR: 0.762 FAIL. After dropping Non-Traditional Rent History Penalty: AIR improves to 0.894 PASS, ROC-AUC remains 0.842.`;
      try {{
        const res = await fetch('/api/run-demo', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{ code: '5.2', model: model, scenario: prompt }})
        }});
        const data = await res.json();
        out.textContent = data.output || data.text || "Econometric certification generated.";
      }} catch (e) {{
        out.textContent = "Error: " + e.message;
      }}
    }};
  </script>

  {render_floating_control_bar_and_drawer(code, auth_token)}
</body>
</html>
"""
