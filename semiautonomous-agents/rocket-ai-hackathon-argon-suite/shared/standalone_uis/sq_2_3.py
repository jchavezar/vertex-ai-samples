# -*- coding: utf-8 -*-
"""Square 2.3 Standalone Full-Screen UI:
Automated W-2 & Paystub Entity Extraction & 5% Variance Pipeline
Aesthetic: Document AI Optical Darkroom & Laser Bounding-Box Inspector (#090A0F darkroom canvas, #84CC16 laser lime OCR boxes, #EC4899 magenta variance alerts)."""

from shared.standalone_uis.base_helpers import render_floating_control_bar_and_drawer


def render_sq_2_3(auth_token: str) -> str:
    floating_bar = render_floating_control_bar_and_drawer("2.3", auth_token)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>2.3 // Document AI Optical Darkroom — W-2 &amp; Paystub Laser Bounding-Box Inspector</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700;800&family=Syne:wght@600;700;800&display=swap" rel="stylesheet">
  <style>
    :root {{
      --darkroom: #090A0F;
      --panel: #11131C;
      --panel-elev: #171A26;
      --laser-lime: #84CC16;
      --laser-glow: rgba(132, 204, 22, 0.22);
      --magenta: #EC4899;
      --magenta-glow: rgba(236, 72, 153, 0.22);
      --cyan: #06B6D4;
      --text: #F8FAFC;
      --muted: #94A3B8;
      --border: #262B3D;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      background: var(--darkroom);
      color: var(--text);
      font-family: 'JetBrains Mono', monospace;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      background-image:
        radial-gradient(circle at 18% 20%, rgba(132, 204, 22, 0.07), transparent 35%),
        radial-gradient(circle at 85% 75%, rgba(236, 72, 153, 0.08), transparent 40%);
    }}

    /* Optical Darkroom Header */
    .darkroom-header {{
      background: rgba(17, 19, 28, 0.92);
      backdrop-filter: blur(12px);
      border-bottom: 1px solid var(--border);
      padding: 14px 26px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      flex-wrap: wrap;
    }}
    .scanner-brand {{
      display: flex;
      align-items: center;
      gap: 14px;
    }}
    .laser-reticle {{
      width: 38px;
      height: 38px;
      border: 2px solid var(--laser-lime);
      border-radius: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
      color: var(--laser-lime);
      font-weight: 800;
      box-shadow: 0 0 16px var(--laser-glow);
    }}
    .scanner-title {{
      font-family: 'Syne', sans-serif;
      font-size: 20px;
      font-weight: 800;
      letter-spacing: -0.02em;
      color: #FFFFFF;
    }}
    .scanner-sub {{
      font-size: 11px;
      color: var(--muted);
    }}
    .header-controls {{
      display: flex;
      align-items: center;
      gap: 12px;
      flex-wrap: wrap;
    }}
    .model-select-box {{
      background: var(--panel-elev);
      border: 1px solid var(--border);
      padding: 6px 12px;
      border-radius: 6px;
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 11px;
    }}
    .model-select-box select {{
      background: transparent;
      color: var(--laser-lime);
      border: none;
      font-family: 'JetBrains Mono', monospace;
      font-size: 11px;
      font-weight: 700;
      outline: none;
      cursor: pointer;
    }}
    .model-select-box select option {{
      background: #090A0F;
      color: #FFF;
    }}
    .btn-laser {{
      background: var(--laser-lime);
      color: #090A0F;
      border: none;
      padding: 8px 16px;
      border-radius: 6px;
      font-family: 'JetBrains Mono', monospace;
      font-size: 11.5px;
      font-weight: 800;
      cursor: pointer;
      box-shadow: 0 0 18px var(--laser-glow);
    }}

    /* Split-Screen Optical Scanner */
    .scanner-grid {{
      display: grid;
      grid-template-columns: 1.15fr 0.85fr;
      gap: 22px;
      padding: 22px 26px 86px 26px;
      flex: 1;
    }}
    @media (max-width: 1100px) {{
      .scanner-grid {{ grid-template-columns: 1fr; }}
    }}

    /* Left Pane: Visual W-2 & ADP Paystub Optical Lightbox */
    .lightbox-pane {{
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 20px;
      display: flex;
      flex-direction: column;
      gap: 18px;
      position: relative;
      overflow: hidden;
    }}
    .lightbox-bar {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 11px;
      color: var(--laser-lime);
      border-bottom: 1px solid var(--border);
      padding-bottom: 10px;
    }}

    /* Simulated Physical Document Specimen with Laser OCR Bounding Boxes */
    .doc-specimen {{
      background: #F8FAFC;
      color: #0F172A;
      border-radius: 8px;
      padding: 18px;
      border: 2px solid #334155;
      box-shadow: 0 14px 35px rgba(0,0,0,0.6);
      position: relative;
    }}
    .doc-specimen-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-bottom: 2px solid #0F172A;
      padding-bottom: 8px;
      margin-bottom: 12px;
      font-size: 11.5px;
      font-weight: 800;
    }}
    .w2-grid {{
      display: grid;
      grid-template-columns: 1.2fr 1fr 1fr;
      gap: 10px;
    }}
    @media (max-width: 720px) {{
      .w2-grid {{ grid-template-columns: 1fr; }}
    }}
    .ocr-bbox {{
      position: relative;
      border: 2px solid #65A30D;
      background: rgba(132, 204, 22, 0.14);
      border-radius: 6px;
      padding: 8px 10px;
      cursor: pointer;
      transition: all 0.15s ease;
    }}
    .ocr-bbox:hover, .ocr-bbox.active-box {{
      border-color: var(--magenta);
      background: rgba(236, 72, 153, 0.18);
      box-shadow: 0 0 0 3px rgba(236, 72, 153, 0.25);
      transform: translateY(-1px);
    }}
    .ocr-tag {{
      position: absolute;
      top: -9px;
      right: 6px;
      background: #090A0F;
      color: var(--laser-lime);
      font-size: 9px;
      font-weight: 700;
      padding: 1px 6px;
      border-radius: 3px;
      border: 1px solid var(--laser-lime);
    }}
    .ocr-bbox.active-box .ocr-tag {{
      color: var(--magenta);
      border-color: var(--magenta);
    }}
    .box-label {{
      font-size: 9.5px;
      color: #475569;
      text-transform: uppercase;
      font-weight: 700;
    }}
    .box-val {{
      font-size: 14px;
      font-weight: 800;
      color: #0F172A;
      margin-top: 3px;
    }}

    /* Right Pane: 5% Variance Gauge, Sliders & DBA Entity Resolver */
    .inspector-pane {{
      display: flex;
      flex-direction: column;
      gap: 16px;
    }}
    .gauge-card {{
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 20px;
      display: flex;
      flex-direction: column;
      gap: 14px;
    }}
    .variance-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}
    .variance-badge {{
      padding: 5px 12px;
      border-radius: 999px;
      font-size: 11px;
      font-weight: 800;
      background: var(--magenta-glow);
      color: var(--magenta);
      border: 1px solid var(--magenta);
    }}
    .variance-badge.pass {{
      background: var(--laser-glow);
      color: var(--laser-lime);
      border-color: var(--laser-lime);
    }}

    .meter-track {{
      height: 16px;
      background: #05060A;
      border: 1px solid var(--border);
      border-radius: 999px;
      overflow: hidden;
      position: relative;
    }}
    .meter-fill {{
      height: 100%;
      width: 78%;
      background: linear-gradient(90deg, var(--laser-lime) 0%, #F59E0B 60%, var(--magenta) 100%);
      transition: width 0.25s ease;
    }}
    .meter-limit-line {{
      position: absolute;
      left: 50%;
      top: 0;
      bottom: 0;
      width: 2px;
      background: #FFFFFF;
    }}

    .slider-controls {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 12px;
    }}
    .dark-slider {{
      background: var(--panel-elev);
      border: 1px solid var(--border);
      padding: 10px 12px;
      border-radius: 8px;
    }}
    .dark-slider label {{
      display: flex;
      justify-content: space-between;
      font-size: 11px;
      margin-bottom: 6px;
      color: var(--muted);
    }}
    .dark-slider input[type=range] {{
      width: 100%;
      accent-color: var(--laser-lime);
      cursor: pointer;
    }}

    .telemetry-kv-grid {{
      display: grid;
      grid-template-columns: 1fr;
      gap: 10px;
    }}
    .kv-row {{
      background: var(--panel-elev);
      border: 1px solid var(--border);
      border-left: 3px solid var(--laser-lime);
      padding: 10px 12px;
      border-radius: 6px;
    }}
    .kv-row.alert {{
      border-left-color: var(--magenta);
    }}
    .kv-k {{
      font-size: 10px;
      text-transform: uppercase;
      color: var(--muted);
    }}
    .kv-v {{
      font-size: 12.5px;
      font-weight: 700;
      color: #FFF;
      margin-top: 3px;
    }}
  </style>
</head>
<body>

  <!-- OPTICAL DARKROOM HEADER -->
  <header class="darkroom-header">
    <div class="scanner-brand">
      <div class="laser-reticle">[OCR]</div>
      <div>
        <div class="scanner-title">Document AI Optical Darkroom // W-2 &amp; Paystub 5% Variance Pipeline</div>
        <div class="scanner-sub">Square 2.3 • Laser Bounding-Box Inspector • Corporate DBA Entity Resolution (Stellantis NV == FCA US LLC)</div>
      </div>
    </div>
    <div class="header-controls">
      <div class="model-select-box">
        <span>Active Model:</span>
        <select id="app-model-select" onchange="window.syncSelectedModel(this.value)">
          <option value="gemini-4-argon" selected>gemini-4-argon (Frontier Global)</option>
          <option value="gemini-3.8-flash">gemini-3.8-flash (Fast Runtime)</option>
        </select>
      </div>
      <button class="btn-laser" onclick="window.runLiveVertexAI()">⚡ Run Optical Variance Audit</button>
    </div>
  </header>

  <!-- SPLIT-SCREEN DOCUMENT SCANNER & VARIANCE GAUGE -->
  <main class="scanner-grid">
    <!-- LEFT PANE: REALISTIC 2025 IRS FORM W-2 & ADP YTD PAYSTUB WITH CLICKABLE BOUNDING BOXES -->
    <section class="lightbox-pane">
      <div class="lightbox-bar">
        <span>● LASER OCR BOUNDING-BOX OVERLAY ACTIVE (CLICK ANY BOX TO INSPECT)</span>
        <span id="selected-bbox-indicator">Selected: Box 1 Wages ($110,000.00 • 99.8% Conf)</span>
      </div>

      <!-- Specimen 1: 2025 IRS Form W-2 -->
      <div class="doc-specimen">
        <div class="doc-specimen-header">
          <span>OMB No. 1545-0008 // 2025 FORM W-2 WAGE AND TAX STATEMENT</span>
          <span style="color:#DC2626;">Copy B — To Be Filed With Employee's FEDERAL Tax Return</span>
        </div>
        <div class="w2-grid">
          <div class="ocr-bbox" onclick="window.selectBbox(this, 'Employer FEIN (Box b)', '38-2678910 — FCA US LLC (Parent: Stellantis NV)', '99.9%')">
            <span class="ocr-tag">FEIN • 99.9%</span>
            <div class="box-label">b. Employer Identification Number (FEIN)</div>
            <div class="box-val">38-2678910</div>
            <div style="font-size:11px;color:#334155;margin-top:2px;">FCA US LLC • 1000 Chrysler Dr, Auburn Hills MI</div>
          </div>
          <div class="ocr-bbox active-box" onclick="window.selectBbox(this, 'Box 1 Taxable Wages', '$110,000.00 (2025 Full Year)', '99.8%')">
            <span class="ocr-tag">BOX 1 • 99.8%</span>
            <div class="box-label">1. Wages, tips, other compensation</div>
            <div class="box-val">$110,000.00</div>
          </div>
          <div class="ocr-bbox" onclick="window.selectBbox(this, 'Box 5 Medicare Wages', '$116,600.00 (Includes $6,600 401k Deferral)', '99.7%')">
            <span class="ocr-tag">BOX 5 • 99.7%</span>
            <div class="box-label">5. Medicare wages and tips</div>
            <div class="box-val">$116,600.00</div>
          </div>
        </div>
      </div>

      <!-- Specimen 2: 2026 ADP YTD Paystub (Period Ending Sept 30, 2026 — 9.0 Months Elapsed) -->
      <div class="doc-specimen">
        <div class="doc-specimen-header">
          <span>ADP EARNINGS STATEMENT // PAY PERIOD: 09/16/2026 – 09/30/2026 (9.0 MOS YTD)</span>
          <span style="color:#0284C7;">Paystub DBA: STELLANTIS NORTH AMERICA</span>
        </div>
        <div class="w2-grid">
          <div class="ocr-bbox" onclick="window.selectBbox(this, 'Paystub Employer DBA', 'STELLANTIS NV (Matched via FEIN 38-2678910 to FCA US LLC)', '99.6%')">
            <span class="ocr-tag">DBA • 99.6%</span>
            <div class="box-label">Paystub Employer Entity</div>
            <div class="box-val">STELLANTIS NV</div>
            <div style="font-size:10.5px;color:#059669;margin-top:2px;">✓ FEIN 38-2678910 Match</div>
          </div>
          <div class="ocr-bbox" onclick="window.selectBbox(this, 'YTD Base Salary (9.0 Months)', '$82,500.00 ($9,166.67/mo Run Rate)', '99.9%')">
            <span class="ocr-tag">YTD BASE • 99.9%</span>
            <div class="box-label">YTD Regular Base Earnings (9 Mos)</div>
            <div class="box-val" id="bbox-ytd-base">$82,500.00</div>
            <div style="font-size:10.5px;color:#475569;">= $9,166.67 / month</div>
          </div>
          <div class="ocr-bbox" onclick="window.selectBbox(this, 'YTD Overtime Earnings (9.0 Months)', '$4,950.00 ($550.00/mo Run Rate)', '99.5%')">
            <span class="ocr-tag">YTD OT • 99.5%</span>
            <div class="box-label">YTD Overtime Earnings (9 Mos)</div>
            <div class="box-val">$4,950.00</div>
            <div style="font-size:10.5px;color:#475569;">= $550.00 / month</div>
          </div>
        </div>
      </div>

      <!-- Active OCR Token Inspector Drawer -->
      <div style="background:var(--panel-elev);border:1px solid var(--border);border-radius:8px;padding:12px 14px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;">
        <div>
          <div style="font-size:10px;color:var(--laser-lime);text-transform:uppercase;">Active Document AI Field Extraction</div>
          <div id="bbox-detail-text" style="font-size:13px;font-weight:700;color:#FFF;margin-top:2px;">Box 1 Taxable Wages: $110,000.00 (2025 Full Year)</div>
        </div>
        <span id="bbox-conf-pill" style="background:var(--laser-glow);color:var(--laser-lime);border:1px solid var(--laser-lime);padding:4px 10px;border-radius:4px;font-size:11px;font-weight:700;">Confidence: 99.8%</span>
      </div>
    </section>

    <!-- RIGHT PANE: LIVE 5% VARIANCE GAUGE & FORM 1003 AUTO-REMEDIATION -->
    <section class="inspector-pane">
      <div class="gauge-card">
        <div class="variance-header">
          <div>
            <div style="font-size:10.5px;color:var(--muted);text-transform:uppercase;">Form 1003 vs. Documented OCR Income</div>
            <h3 style="font-family:'Syne',sans-serif;font-size:19px;color:#FFF;margin-top:2px;">5.0% Variance Tolerance Gate</h3>
          </div>
          <span class="variance-badge" id="variance-status-pill">+8.06% BREACH (&gt; 5.0% CAP)</span>
        </div>

        <div class="meter-track">
          <div class="meter-fill" id="variance-meter-bar"></div>
          <div class="meter-limit-line" title="5.0% Maximum Underwriting Variance Threshold"></div>
        </div>
        <div style="display:flex;justify-content:space-between;font-size:10.5px;color:var(--muted);">
          <span>0.0% Exact Match</span>
          <span style="color:#FFF;font-weight:700;">▲ 5.0% GSE Tolerance Limit</span>
          <span style="color:var(--magenta);">10.0%+ Severe Variance</span>
        </div>

        <div class="slider-controls">
          <div class="dark-slider">
            <label>
              <span>1003 Stated Monthly</span>
              <strong id="lbl-stated" style="color:var(--magenta);">$10,500/mo</strong>
            </label>
            <input type="range" id="sl-stated" min="8500" max="12500" step="100" value="10500" oninput="window.reconcileVariance()" />
          </div>
          <div class="dark-slider">
            <label>
              <span>9-Mo YTD Base Salary</span>
              <strong id="lbl-ytd" style="color:var(--laser-lime);">$82,500</strong>
            </label>
            <input type="range" id="sl-ytd" min="66000" max="99000" step="1500" value="82500" oninput="window.reconcileVariance()" />
          </div>
        </div>

        <div class="telemetry-kv-grid">
          <div class="kv-row">
            <div class="kv-k">Corporate DBA &amp; FEIN Entity Resolution</div>
            <div class="kv-v" id="kv-dba">MATCH CONFIRMED — 'Stellantis NV' == 'FCA US LLC' (FEIN 38-2678910)</div>
          </div>
          <div class="kv-row">
            <div class="kv-k">Documented Monthly Income (Base + 9-Mo YTD OT)</div>
            <div class="kv-v" id="kv-doc">$9,716.67/mo (Base $9,166.67/mo + 9-Mo YTD Overtime $550.00/mo)</div>
          </div>
          <div class="kv-row alert" id="kv-var-card">
            <div class="kv-k">Stated vs. Documented Variance</div>
            <div class="kv-v" id="kv-var" style="color:var(--magenta);">+8.06% (+$783.33/mo over-stated -&gt; BREACHES 5.0% Tolerance Threshold!)</div>
          </div>
          <div class="kv-row">
            <div class="kv-k">Rocket Logic LOS Auto-Adjustment &amp; AI Synthesis (<span id="live-model-pill">gemini-4-argon</span>)</div>
            <div class="kv-v" id="kv-los" style="color:var(--laser-lime);">Update Form 1003 Qualifying Income to $9,716.67/mo and recalculate DTI.</div>
          </div>
        </div>
      </div>
    </section>
  </main>

  <script>
    window.selectBbox = function(el, title, valueText, conf) {{
      document.querySelectorAll('.ocr-bbox').forEach(b => b.classList.remove('active-box'));
      el.classList.add('active-box');
      document.getElementById('selected-bbox-indicator').innerText = `Selected: ${{title}} (${{conf}} Conf)`;
      document.getElementById('bbox-detail-text').innerText = `${{title}}: ${{valueText}}`;
      document.getElementById('bbox-conf-pill').innerText = `Confidence: ${{conf}}`;
    }};

    window.reconcileVariance = async function() {{
      const stated = parseFloat(document.getElementById('sl-stated').value || 10500);
      const ytdBase = parseFloat(document.getElementById('sl-ytd').value || 82500);
      document.getElementById('lbl-stated').innerText = '$' + stated.toLocaleString() + '/mo';
      document.getElementById('lbl-ytd').innerText = '$' + ytdBase.toLocaleString();
      document.getElementById('bbox-ytd-base').innerText = '$' + ytdBase.toLocaleString() + '.00';

      try {{
        const res = await fetch('/api/sandbox', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{
            code: '2.3',
            action: 'reconcile_paystub_w2',
            params: {{ stated_monthly: stated, ytd_base_9m: ytdBase, ytd_ot_9m: 4950 }}
          }})
        }});
        const data = await res.json();
        if (data.ok && data.metrics) {{
          document.getElementById('kv-dba').innerText = data.metrics.entity_dba_resolution || '';
          document.getElementById('kv-doc').innerText = data.metrics.documented_monthly_income || '';
          document.getElementById('kv-var').innerText = data.metrics.stated_vs_documented_variance || '';
          document.getElementById('kv-los').innerText = data.metrics.los_auto_adjustment || '';

          const docMo = (ytdBase / 9.0) + (4950.0 / 9.0);
          const vPct = Math.abs(((stated - docMo) / docMo) * 100.0);
          const widthPct = Math.min(100, Math.round((vPct / 10.0) * 100));
          document.getElementById('variance-meter-bar').style.width = widthPct + '%';

          const pill = document.getElementById('variance-status-pill');
          if (vPct <= 5.0) {{
            pill.className = 'variance-badge pass';
            pill.innerText = `${{vPct.toFixed(2)}}% WITHIN 5.0% TOLERANCE ✓`;
            document.getElementById('kv-var').style.color = 'var(--laser-lime)';
          }} else {{
            pill.className = 'variance-badge';
            pill.innerText = `+${{vPct.toFixed(2)}}% BREACH (> 5.0% CAP)`;
            document.getElementById('kv-var').style.color = 'var(--magenta)';
          }}
        }}
      }} catch (e) {{
        console.error(e);
      }}
    }};

    window.runLiveVertexAI = async function() {{
      const model = window.getSelectedModel ? window.getSelectedModel() : 'gemini-4-argon';
      const stated = parseFloat(document.getElementById('sl-stated').value || 10500);
      const ytdBase = parseFloat(document.getElementById('sl-ytd').value || 82500);
      const losEl = document.getElementById('kv-los');
      losEl.innerText = `Synthesizing Optical Audit via Vertex AI (${{model}})...`;

      try {{
        const res = await fetch('/api/run-demo', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{
            code: '2.3',
            model: model,
            params: {{ stated_monthly: stated, ytd_base_9m: ytdBase, ytd_ot_9m: 4950 }}
          }})
        }});
        const data = await res.json();
        const sd = data.structured_data || {{}};
        losEl.innerText = sd.los_remediation_action || data.output || 'Form 1003 updated.';
      }} catch (e) {{
        losEl.innerText = 'Optical audit complete.';
      }}
    }};
  </script>

  {floating_bar}
</body>
</html>"""
