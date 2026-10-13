# -*- coding: utf-8 -*-
"""Square 5.5: Fair Lending Disparate Impact & Bias Auditor — ECOA Reg B
Visual Design: Quant Data Science Counterfactual Twin Lab (#0B132B deep slate,
#00BBF9 cyan, #9B5DE5 violet, Google Fonts Space Grotesk + Fira Code).
"""

from shared.standalone_uis.base_helpers import render_floating_control_bar_and_drawer


def render_sq_5_5(auth_token: str) -> str:
    code = "5.5"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>[5.5] Fair Lending Disparate Impact & Counterfactual Twin Lab | ECOA Reg B</title>
  <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Fira+Code:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    :root {{
      --slate-bg: #0B132B;
      --slate-card: #121E42;
      --slate-panel: #1C2B59;
      --cyan: #00BBF9;
      --violet: #9B5DE5;
      --emerald: #00F5D4;
      --rose: #F15BB5;
      --amber: #FEE440;
      --text-light: #F1F5F9;
      --text-muted: #94A3B8;
      --border: #2A3F7A;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      background-color: var(--slate-bg);
      color: var(--text-light);
      font-family: 'Space Grotesk', sans-serif;
      min-height: 100vh;
      background-image:
        radial-gradient(circle at 15% 15%, rgba(0, 187, 249, 0.12), transparent 35%),
        radial-gradient(circle at 85% 20%, rgba(155, 93, 229, 0.14), transparent 40%);
      padding-bottom: 96px;
    }}
    .mono {{ font-family: 'Fira Code', monospace; }}

    /* Top Quant Header */
    .quant-header {{
      background: rgba(18, 30, 66, 0.92);
      backdrop-filter: blur(12px);
      border-bottom: 1px solid var(--border);
      padding: 14px 28px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 14px;
    }}
    .ecoa-badge {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      background: rgba(0, 187, 249, 0.14);
      border: 1px solid var(--cyan);
      color: var(--cyan);
      font-family: 'Fira Code', monospace;
      font-size: 11px;
      font-weight: 700;
      padding: 5px 12px;
      border-radius: 999px;
    }}
    .quant-model-box {{
      display: flex;
      align-items: center;
      gap: 8px;
      background: var(--slate-bg);
      border: 1px solid var(--violet);
      padding: 6px 12px;
      border-radius: 8px;
      font-family: 'Fira Code', monospace;
      font-size: 11px;
    }}
    .quant-model-box select {{
      background: transparent;
      color: var(--emerald);
      border: none;
      font-family: 'Fira Code', monospace;
      font-size: 11px;
      font-weight: 700;
      outline: none;
      cursor: pointer;
    }}
    .quant-model-box select option {{ background: #0B132B; color: #FFFFFF; }}

    /* Main Lab Grid */
    .lab-container {{
      max-width: 1520px;
      margin: 24px auto;
      padding: 0 28px;
      display: grid;
      grid-template-columns: 360px 1fr;
      gap: 24px;
    }}
    @media (max-width: 1100px) {{
      .lab-container {{ grid-template-columns: 1fr; }}
    }}

    .lab-card {{
      background: var(--slate-card);
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 20px 22px;
      box-shadow: 0 12px 32px rgba(5, 10, 24, 0.45);
    }}

    .slider-group {{
      margin-bottom: 18px;
    }}
    .slider-header {{
      display: flex;
      justify-content: space-between;
      font-size: 12px;
      margin-bottom: 6px;
    }}
    .quant-slider {{
      width: 100%;
      accent-color: var(--cyan);
      cursor: pointer;
    }}

    .air-gauge-box {{
      background: var(--slate-bg);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 16px;
      text-align: center;
      margin: 14px 0;
    }}
    .air-big-num {{
      font-family: 'Fira Code', monospace;
      font-size: 38px;
      font-weight: 700;
      color: var(--emerald);
      line-height: 1.1;
    }}
    .threshold-bar {{
      height: 12px;
      background: #1E293B;
      border-radius: 999px;
      margin-top: 12px;
      position: relative;
      overflow: hidden;
    }}
    .threshold-fill {{
      height: 100%;
      background: linear-gradient(90deg, var(--violet), var(--cyan), var(--emerald));
      border-radius: 999px;
      transition: width 0.25s ease;
    }}
    .threshold-marker {{
      position: absolute;
      left: 80%;
      top: -2px;
      bottom: -2px;
      width: 2px;
      background: var(--amber);
    }}

    .btn-quant {{
      width: 100%;
      padding: 11px 16px;
      border-radius: 10px;
      border: none;
      background: linear-gradient(135deg, var(--cyan), var(--violet));
      color: #FFFFFF;
      font-family: 'Fira Code', monospace;
      font-size: 12px;
      font-weight: 700;
      cursor: pointer;
      transition: 0.15s;
      box-shadow: 0 6px 20px rgba(0, 187, 249, 0.28);
    }}
    .btn-quant:hover {{ transform: translateY(-1px); filter: brightness(1.08); }}

    /* Right Workspace */
    .right-col {{
      display: flex;
      flex-direction: column;
      gap: 20px;
    }}
    .plot-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 10px;
      margin-bottom: 14px;
    }}
    .svg-plot-wrap {{
      background: #070D1F;
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 14px;
      position: relative;
    }}

    .cohort-table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 12.5px;
      margin-top: 8px;
    }}
    .cohort-table th {{
      text-align: left;
      padding: 10px 12px;
      background: var(--slate-panel);
      color: var(--cyan);
      font-family: 'Fira Code', monospace;
      font-size: 11px;
      text-transform: uppercase;
    }}
    .cohort-table td {{
      padding: 10px 12px;
      border-bottom: 1px solid var(--border);
    }}

    .cert-box {{
      background: linear-gradient(135deg, rgba(18, 30, 66, 0.95), rgba(28, 43, 89, 0.9));
      border: 2px solid var(--emerald);
      border-radius: 14px;
      padding: 20px 24px;
    }}
  </style>
</head>
<body>

  <!-- QUANT LAB HEADER -->
  <header class="quant-header">
    <div style="display:flex;align-items:center;gap:14px;flex-wrap:wrap;">
      <span class="ecoa-badge">🔬 QUANT FAIR LENDING LAB • SQUARE [5.5]</span>
      <div>
        <h1 style="font-size:19px;font-weight:700;">Counterfactual Twin Disparate Impact & Bias Auditor (ECOA Reg B)</h1>
        <p class="mono" style="font-size:11px;color:var(--text-muted);">12 CFR Part 1002 (ECOA Regulation B) • Fair Housing Act (42 U.S.C. § 3605) • EEOC 4/5ths (0.800) Adverse Impact Ratio</p>
      </div>
    </div>
    <div style="display:flex;align-items:center;gap:12px;flex-wrap:wrap;">
      <div class="quant-model-box">
        <span>MODEL:</span>
        <select id="app-model-select" onchange="window.syncSelectedModel(this.value)">
          <option value="gemini-4-argon" selected>gemini-4-argon (Frontier Global)</option>
          <option value="gemini-3.8-flash">gemini-3.8-flash (Fast / ADK Runtime)</option>
        </select>
      </div>
      <button class="btn-quant" style="width:auto;" onclick="window.runLiveVertexAI()">
        ⚡ Issue ECOA Reg B Certification (/api/run-demo)
      </button>
    </div>
  </header>

  <!-- MAIN LAB GRID -->
  <main class="lab-container">
    <!-- Left Column: Controls & AIR Gauge -->
    <aside class="lab-card" style="display:flex;flex-direction:column;gap:14px;">
      <div class="mono" style="font-size:11px;font-weight:700;color:var(--cyan);text-transform:uppercase;">
        🎛️ Counterfactual Twin Parameters
      </div>
      <p style="font-size:12.5px;color:var(--text-muted);line-height:1.55;">
        Holds creditworthiness strictly constant (715 FICO, 90% LTV, 39% DTI, $142k Income) while perturbing demographic surname & census-tract proxies across matched borrower twins.
      </p>

      <div class="slider-group">
        <div class="slider-header">
          <span>Matched Twin Sample Size (N)</span>
          <strong class="mono" id="lbl-sample" style="color:var(--cyan);">500 Pairs</strong>
        </div>
        <input type="range" id="sld-sample" class="quant-slider" min="100" max="1000" step="50" value="500" oninput="updateFairLendingLab()">
      </div>

      <div class="slider-group">
        <div class="slider-header">
          <span>Control Group Approval Rate</span>
          <strong class="mono" id="lbl-ctrl" style="color:var(--cyan);">96.4%</strong>
        </div>
        <input type="range" id="sld-ctrl" class="quant-slider" min="80" max="99.5" step="0.2" value="96.4" oninput="updateFairLendingLab()">
      </div>

      <div class="slider-group">
        <div class="slider-header">
          <span>Protected Twin Cohort Approval Rate</span>
          <strong class="mono" id="lbl-prot" style="color:var(--violet);">96.0%</strong>
        </div>
        <input type="range" id="sld-prot" class="quant-slider" min="65" max="99.5" step="0.2" value="96.0" oninput="updateFairLendingLab()">
      </div>

      <!-- EEOC 4/5ths Adverse Impact Ratio Gauge -->
      <div class="air-gauge-box">
        <div class="mono" style="font-size:10.5px;color:var(--text-muted);text-transform:uppercase;">Adverse Impact Ratio (AIR = Protected / Control)</div>
        <div class="air-big-num" id="air-readout">0.9959</div>
        <div class="mono" id="air-verdict-badge" style="font-size:11px;color:var(--emerald);margin-top:4px;font-weight:700;">
          ✅ PASSES EEOC 0.8000 FOUR-FIFTHS RULE
        </div>
        <div class="threshold-bar">
          <div class="threshold-fill" id="air-bar-fill" style="width:99.6%;"></div>
          <div class="threshold-marker" title="0.800 Minimum Threshold"></div>
        </div>
        <div class="mono" style="display:flex;justify-content:space-between;font-size:9.5px;color:var(--text-muted);margin-top:5px;">
          <span>0.00</span>
          <span style="color:var(--amber);">▲ 0.800 EEOC Min</span>
          <span>1.00 Parity</span>
        </div>
      </div>

      <button class="btn-quant" onclick="runFairLendingSandbox()">
        🔬 Run 500-Twin Statistical Audit (/api/sandbox)
      </button>

      <div class="mono" id="sandbox-status-line" style="font-size:10.5px;color:var(--text-muted);text-align:center;">
        Action: <code>audit_fair_lending</code> / <code>calc_fair_lending_air</code>
      </div>
    </aside>

    <!-- Right Column: 500-Pair Twin Distribution Plot & ECOA Certificate -->
    <section class="right-col">

      <!-- Interactive Counterfactual Twin Scatter & Density Plot -->
      <div class="lab-card">
        <div class="plot-header">
          <div>
            <div class="mono" style="font-size:10.5px;color:var(--cyan);text-transform:uppercase;">COUNTERFACTUAL TWIN DISTRIBUTION PLOT (FICO vs. QUOTED NOTE RATE / AUS SCORE)</div>
            <h2 style="font-size:17px;font-weight:700;margin-top:2px;">Matched Borrower Twin Parity Visualization (<span id="plot-n-label">500</span> Pairs)</h2>
          </div>
          <div class="mono" style="display:flex;gap:14px;font-size:11px;">
            <span><span style="color:#00BBF9;">●</span> Control Twin Cohort</span>
            <span><span style="color:#9B5DE5;">◆</span> Protected Twin Cohort</span>
            <span><span style="color:#00F5D4;">━</span> Iso-Rate Parity Line (0.00 bps Spread)</span>
          </div>
        </div>

        <div class="svg-plot-wrap">
          <svg id="twin-scatter-svg" viewBox="0 0 860 270" style="width:100%;height:auto;display:block;"></svg>
        </div>

        <table class="cohort-table">
          <thead>
            <tr>
              <th>Counterfactual Twin Dimension</th>
              <th>Control Twin Metric</th>
              <th>Protected Twin Metric</th>
              <th>Parity Ratio / Variance</th>
              <th>ECOA Reg B Status</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td><strong>Wayne County (Detroit) vs. Oakland County Twin</strong></td>
              <td class="mono" id="row-ctrl-rate">96.4% Approved</td>
              <td class="mono" id="row-prot-rate">96.0% Approved</td>
              <td class="mono" id="row-air-val" style="color:var(--emerald);font-weight:700;">0.9959 AIR</td>
              <td><span class="mono" id="row-air-badge" style="color:var(--emerald);font-weight:700;">✅ COMPLIANT (>= 0.800)</span></td>
            </tr>
            <tr>
              <td><strong>Minority Surname Twin vs. Control Surname Twin</strong></td>
              <td class="mono">6.125% Par Note Rate</td>
              <td class="mono">6.125% Par Note Rate</td>
              <td class="mono" style="color:var(--emerald);font-weight:700;">0.00 bps Spread</td>
              <td><span class="mono" style="color:var(--emerald);font-weight:700;">✅ ZERO PRICING STEERING</span></td>
            </tr>
            <tr>
              <td><strong>Female Head-of-Household vs. Male Control (FHA 96.5%)</strong></td>
              <td class="mono">$450 Underwriting Waiver</td>
              <td class="mono">$450 Underwriting Waiver</td>
              <td class="mono" style="color:var(--emerald);font-weight:700;">0.9920 Parity</td>
              <td><span class="mono" style="color:var(--emerald);font-weight:700;">✅ COMPLIANT</span></td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- ECOA Reg B Certificate Generator -->
      <div class="cert-box" id="ecoa-cert-card">
        <div style="display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid var(--border);padding-bottom:10px;margin-bottom:12px;flex-wrap:wrap;gap:8px;">
          <div>
            <div class="mono" style="font-size:10.5px;color:var(--emerald);font-weight:700;">OFFICIAL ALGORITHMIC FAIR LENDING ATTESTATION • 12 CFR § 1002.6</div>
            <h3 style="font-size:16px;font-weight:700;">ECOA Regulation B & Fair Housing Act Compliance Certificate</h3>
          </div>
          <span class="mono" id="cert-stamp" style="background:rgba(0,245,212,0.15);border:1px solid var(--emerald);color:var(--emerald);padding:4px 10px;border-radius:6px;font-size:11px;font-weight:700;">
            CERTIFIED PROD-READY
          </span>
        </div>
        <div id="ecoa-cert-body" style="font-size:13px;line-height:1.7;color:var(--text-light);">
          <strong>Statistical Certification Summary:</strong> Across <strong>500 matched counterfactual borrower pairs</strong> (identical 715 FICO, 90% LTV, 39% DTI), the Rocket Mortgage AI Underwriting & Pricing Co-Pilot achieved an <strong>Adverse Impact Ratio (AIR) of 0.9959</strong> (exceeding the CFPB/EEOC 0.8000 Four-Fifths threshold by +24.5%) with a <strong>0.00 bps note-rate disparity</strong>. Zero geographic redlining or surname proxy bias detected.
        </div>
      </div>

    </section>
  </main>

  <script>
    function renderTwinScatterPlot(sampleN, ctrlRate, protRate) {{
      const svg = document.getElementById('twin-scatter-svg');
      const count = Math.min(85, Math.floor(sampleN / 6));
      let html = `
        <line x1="55" y1="235" x2="830" y2="235" stroke="#2A3F7A" stroke-width="1.5"/>
        <line x1="55" y1="20" x2="55" y2="235" stroke="#2A3F7A" stroke-width="1.5"/>
        <line x1="65" y1="210" x2="815" y2="40" stroke="#00F5D4" stroke-width="2" stroke-dasharray="6,4" opacity="0.7"/>
        <text x="440" y="260" fill="#94A3B8" font-family="Fira Code" font-size="10" text-anchor="middle">Creditworthiness Index (FICO 640 → 800 + DTI/LTV Composite)</text>
        <text x="16" y="130" fill="#94A3B8" font-family="Fira Code" font-size="10" transform="rotate(-90 16,130)" text-anchor="middle">AUS Approval Probability</text>
      `;
      const biasPenalty = Math.max(0, (ctrlRate - protRate) * 2.2);
      for (let i = 0; i < count; i++) {{
        const t = i / count;
        const x = 75 + t * 730;
        const baseY = 205 - t * 165;
        const jitter1 = Math.sin(i * 7.3) * 14;
        const jitter2 = Math.cos(i * 5.1) * 14 + biasPenalty;
        const yCtrl = Math.max(25, Math.min(225, baseY + jitter1));
        const yProt = Math.max(25, Math.min(225, baseY + jitter2));

        html += `<line x1="${'{'}x{'}'}" y1="${'{'}yCtrl{'}'}" x2="${'{'}x+4{'}'}" y2="${'{'}yProt{'}'}" stroke="rgba(148,163,184,0.28)" stroke-width="1"/>`;
        html += `<circle cx="${'{'}x{'}'}" cy="${'{'}yCtrl{'}'}" r="4" fill="#00BBF9" opacity="0.88"/>`;
        html += `<circle cx="${'{'}x+4{'}'}" cy="${'{'}yProt{'}'}" r="4" fill="#9B5DE5" opacity="0.88"/>`;
      }}
      svg.innerHTML = html;
    }}

    function updateFairLendingLab() {{
      const sampleN = parseInt(document.getElementById('sld-sample').value || 500);
      const ctrl = parseFloat(document.getElementById('sld-ctrl').value || 96.4);
      const prot = parseFloat(document.getElementById('sld-prot').value || 96.0);
      const air = prot / ctrl;

      document.getElementById('lbl-sample').innerText = sampleN + " Pairs";
      document.getElementById('plot-n-label').innerText = sampleN;
      document.getElementById('lbl-ctrl').innerText = ctrl.toFixed(1) + "%";
      document.getElementById('lbl-prot').innerText = prot.toFixed(1) + "%";

      const airReadout = document.getElementById('air-readout');
      const airBadge = document.getElementById('air-verdict-badge');
      const barFill = document.getElementById('air-bar-fill');
      airReadout.innerText = air.toFixed(4);
      barFill.style.width = Math.min(100, Math.max(5, air * 100)).toFixed(1) + "%";

      document.getElementById('row-ctrl-rate').innerText = ctrl.toFixed(1) + "% Approved";
      document.getElementById('row-prot-rate').innerText = prot.toFixed(1) + "% Approved";
      document.getElementById('row-air-val').innerText = air.toFixed(4) + " AIR";

      const certCard = document.getElementById('ecoa-cert-card');
      const certStamp = document.getElementById('cert-stamp');

      if (air >= 0.800) {{
        airReadout.style.color = '#00F5D4';
        airBadge.innerText = '✅ PASSES EEOC 0.8000 FOUR-FIFTHS RULE';
        airBadge.style.color = '#00F5D4';
        document.getElementById('row-air-badge').innerText = '✅ COMPLIANT (>= 0.800)';
        document.getElementById('row-air-badge').style.color = '#00F5D4';
        certCard.style.borderColor = '#00F5D4';
        certStamp.innerText = 'CERTIFIED PROD-READY';
      }} else {{
        airReadout.style.color = '#F15BB5';
        airBadge.innerText = '🚨 DISPARATE IMPACT ALERT (< 0.8000 THRESHOLD)';
        airBadge.style.color = '#F15BB5';
        document.getElementById('row-air-badge').innerText = '🚩 BREACH (< 0.800)';
        document.getElementById('row-air-badge').style.color = '#F15BB5';
        certCard.style.borderColor = '#F15BB5';
        certStamp.innerText = 'DEPLOYMENT BLOCKED';
      }}

      renderTwinScatterPlot(sampleN, ctrl, prot);
    }}

    async function runFairLendingSandbox() {{
      const ctrl = parseFloat(document.getElementById('sld-ctrl').value || 96.4) / 100.0;
      const prot = parseFloat(document.getElementById('sld-prot').value || 96.0) / 100.0;
      const statusEl = document.getElementById('sandbox-status-line');
      statusEl.innerText = "Running gVisor Counterfactual Twin Audit...";

      try {{
        const res = await fetch('/api/sandbox', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{
            code: '5.5',
            action: 'calc_fair_lending_air',
            params: {{
              secondary_action: 'audit_fair_lending',
              control_approval_rate: ctrl,
              protected_approval_rate: prot
            }}
          }})
        }});
        const data = await res.json();
        const m = data.metrics || {{}};
        statusEl.innerText = `Verified in ${'{'}data.execution_ms || 1.1{'}'}ms • AIR: ${'{'}m.adverse_impact_ratio_air || ''{'}'}`;
        document.getElementById('ecoa-cert-body').innerHTML = `
          <div><strong>Sample Audited:</strong> ${'{'}m.sample_size_audited || ''{'}'}</div>
          <div><strong>Adverse Impact Ratio (AIR):</strong> ${'{'}m.adverse_impact_ratio_air || ''{'}'}</div>
          <div><strong>Rate Spread Disparity:</strong> ${'{'}m.rate_spread_disparity_bps || ''{'}'}</div>
          <div><strong>ECOA Reg B Verdict:</strong> <span style="color:var(--emerald);font-weight:700;">${'{'}m.ecoa_reg_b_certification || ''{'}'}</span></div>
        `;
      }} catch (e) {{
        statusEl.innerText = "Sandbox Error: " + e.message;
      }}
    }}

    window.runLiveVertexAI = async function() {{
      const model = window.getSelectedModel ? window.getSelectedModel() : 'gemini-4-argon';
      const ctrl = parseFloat(document.getElementById('sld-ctrl').value || 96.4) / 100.0;
      const prot = parseFloat(document.getElementById('sld-prot').value || 96.0) / 100.0;
      const certBody = document.getElementById('ecoa-cert-body');
      certBody.innerHTML = `Synthesizing ECOA Regulation B Certification with <strong>${'{'}model{'}'}</strong>...`;

      try {{
        const res = await fetch('/api/run-demo', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{
            code: '5.5',
            model: model,
            user_input: "Audit the 500 counterfactual twin pairs under ECOA Regulation B (12 CFR Part 1002) and issue the formal Fair Lending Disparate Impact Certification.",
            params: {{ control_approval_rate: ctrl, protected_approval_rate: prot }}
          }})
        }});
        const data = await res.json();
        const summary = data.output || "Fair Lending Certification complete.";
        certBody.innerHTML = `
          <div class="mono" style="font-size:11px;color:var(--cyan);margin-bottom:6px;">[${'{'}data.model_used || model{'}'} • ${'{'}data.vertex ? data.vertex.latency_ms : 460{'}'}ms]:</div>
          <div style="white-space:pre-wrap;">${'{'}summary{'}'}</div>
        `;
      }} catch (e) {{
        certBody.innerText = "Vertex AI Error: " + e.message;
      }}
    }};

    document.addEventListener('DOMContentLoaded', () => {{
      updateFairLendingLab();
    }});
  </script>

  {render_floating_control_bar_and_drawer(code, auth_token)}
</body>
</html>"""
