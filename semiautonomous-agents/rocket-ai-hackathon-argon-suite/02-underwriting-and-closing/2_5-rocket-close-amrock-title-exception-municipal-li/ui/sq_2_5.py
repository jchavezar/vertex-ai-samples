# -*- coding: utf-8 -*-
"""Square 2.5 Standalone Full-Screen UI:
Closing Disclosure (CD) Tolerance Auditor (CFPB TILA-RESPA Integrated Disclosure 12 CFR § 1026.19(e)/(f) Workpaper)
Design Style: Deloitte / PwC TRID Audit Workpaper & Reconciliation Sheet (#F8FAFC crisp accounting paper, #0F766E deep accounting teal, #FFFFFF side-by-side reconciliation table, IBM Plex Sans + tabular numerals).
"""

from shared.standalone_uis.base_helpers import render_floating_control_bar_and_drawer


def render_sq_2_5(auth_token: str) -> str:
    floating_bar = render_floating_control_bar_and_drawer("2.5", auth_token)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>2.5 · Closing Disclosure (CD) Tolerance Auditor — TRID 12 CFR § 1026.19 Workpaper</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600;700&family=IBM+Plex+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    :root {{
      --audit-paper: #F8FAFC;
      --audit-card: #FFFFFF;
      --teal: #0F766E;
      --teal-dark: #115E59;
      --teal-soft: #F0FDFA;
      --ink: #0F172A;
      --muted: #475569;
      --border: #CBD5E1;
      --crimson: #B91C1C;
      --crimson-soft: #FEF2F2;
      --emerald: #047857;
      --emerald-soft: #ECFDF5;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      background: var(--audit-paper);
      color: var(--ink);
      font-family: 'IBM Plex Sans', -apple-system, BlinkMacSystemFont, sans-serif;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      font-variant-numeric: tabular-nums;
    }}

    /* Deloitte / PwC Accounting Teal Top Bar */
    .trid-topbar {{
      background: var(--teal);
      color: #FFFFFF;
      padding: 14px 28px;
      border-bottom: 3px solid var(--teal-dark);
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      flex-wrap: wrap;
      box-shadow: 0 3px 12px rgba(15, 118, 110, 0.2);
    }}
    .trid-brand {{
      display: flex;
      align-items: center;
      gap: 14px;
    }}
    .trid-badge {{
      background: #FFFFFF;
      color: var(--teal-dark);
      font-family: 'IBM Plex Mono', monospace;
      font-weight: 700;
      font-size: 13px;
      padding: 6px 10px;
      border-radius: 6px;
    }}
    .trid-title {{
      font-size: 18px;
      font-weight: 700;
      letter-spacing: -0.01em;
    }}
    .trid-sub {{
      font-size: 12px;
      color: #CCFBF1;
    }}
    .topbar-controls {{
      display: flex;
      align-items: center;
      gap: 12px;
      flex-wrap: wrap;
    }}
    .model-box {{
      background: rgba(255,255,255,0.15);
      border: 1px solid rgba(255,255,255,0.3);
      padding: 6px 12px;
      border-radius: 6px;
      font-size: 12px;
      display: flex;
      align-items: center;
      gap: 8px;
    }}
    .model-box select {{
      background: transparent;
      border: none;
      color: #FFFFFF;
      font-family: inherit;
      font-size: 12px;
      font-weight: 700;
      outline: none;
      cursor: pointer;
    }}
    .model-box select option {{
      background: #0F172A;
      color: #FFFFFF;
    }}
    .btn-trid-audio {{
      background: #FFFFFF;
      color: var(--teal-dark);
      border: none;
      padding: 8px 14px;
      border-radius: 6px;
      font-family: inherit;
      font-size: 12.5px;
      font-weight: 700;
      cursor: pointer;
    }}
    .btn-trid-cure {{
      background: #0F172A;
      color: #FFFFFF;
      border: 1px solid #334155;
      padding: 8px 16px;
      border-radius: 6px;
      font-family: inherit;
      font-size: 12.5px;
      font-weight: 700;
      cursor: pointer;
    }}

    /* Executive TRID Bucket Summary Strip */
    .bucket-strip {{
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 16px;
      padding: 20px 28px 0 28px;
      max-width: 1520px;
      margin: 0 auto;
      width: 100%;
    }}
    @media (max-width: 980px) {{
      .bucket-strip {{ grid-template-columns: repeat(2, 1fr); }}
    }}
    .bucket-card {{
      background: #FFFFFF;
      border: 1px solid var(--border);
      border-top: 4px solid var(--teal);
      border-radius: 8px;
      padding: 15px 18px;
      box-shadow: 0 1px 4px rgba(15, 23, 42, 0.04);
    }}
    .bucket-card.cure {{
      border-top-color: var(--crimson);
      background: var(--crimson-soft);
    }}
    .bucket-lbl {{
      font-size: 11px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.04em;
      color: var(--muted);
    }}
    .bucket-val {{
      font-family: 'IBM Plex Mono', monospace;
      font-size: 22px;
      font-weight: 700;
      color: var(--ink);
      margin-top: 5px;
    }}
    .bucket-sub {{
      font-size: 11.5px;
      color: var(--muted);
      margin-top: 3px;
    }}

    /* Main 2-Column Reconciliation Table & Interactive Sliders */
    .workpaper-grid {{
      display: grid;
      grid-template-columns: 1.35fr 0.85fr;
      gap: 20px;
      padding: 20px 28px 90px 28px;
      max-width: 1520px;
      margin: 0 auto;
      width: 100%;
    }}
    @media (max-width: 1140px) {{
      .workpaper-grid {{ grid-template-columns: 1fr; }}
    }}

    .recon-card {{
      background: #FFFFFF;
      border: 1px solid var(--border);
      border-radius: 8px;
      overflow: hidden;
      box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04);
    }}
    .recon-header {{
      background: #F1F5F9;
      border-bottom: 2px solid var(--teal);
      padding: 14px 20px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 10px;
    }}
    .recon-table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 13px;
    }}
    .recon-table th {{
      background: #F8FAFC;
      text-align: left;
      padding: 10px 14px;
      font-size: 11px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.04em;
      color: var(--muted);
      border-bottom: 1px solid var(--border);
    }}
    .recon-table th.num, .recon-table td.num {{
      text-align: right;
      font-family: 'IBM Plex Mono', monospace;
    }}
    .recon-table td {{
      padding: 11px 14px;
      border-bottom: 1px solid #E2E8F0;
    }}
    .recon-table tr.bucket-row td {{
      background: var(--teal-soft);
      color: var(--teal-dark);
      font-weight: 700;
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: 0.04em;
      padding: 8px 14px;
    }}
    .recon-table tr.cure-row td {{
      background: var(--crimson-soft);
      color: var(--crimson);
      font-weight: 700;
      border-top: 2px solid var(--crimson);
      border-bottom: 2px solid var(--crimson);
    }}
    .pill-pass {{
      display: inline-block;
      padding: 2px 8px;
      border-radius: 999px;
      font-size: 10.5px;
      font-weight: 700;
      background: var(--emerald-soft);
      color: var(--emerald);
      border: 1px solid #A7F3D0;
    }}
    .pill-cure {{
      display: inline-block;
      padding: 2px 8px;
      border-radius: 999px;
      font-size: 10.5px;
      font-weight: 700;
      background: var(--crimson-soft);
      color: var(--crimson);
      border: 1px solid #FECACA;
    }}

    /* Right Column: Interactive Fee Sliders & Cure Calculator */
    .side-col {{
      display: flex;
      flex-direction: column;
      gap: 18px;
    }}
    .audit-panel {{
      background: #FFFFFF;
      border: 1px solid var(--border);
      border-top: 4px solid var(--teal);
      border-radius: 8px;
      padding: 18px 20px;
      box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04);
    }}
    .slider-box {{
      background: #F8FAFC;
      border: 1px solid #E2E8F0;
      border-radius: 6px;
      padding: 12px 14px;
      margin-top: 12px;
    }}
    .slider-box input[type="range"] {{
      width: 100%;
      accent-color: var(--teal);
      margin-top: 6px;
      cursor: pointer;
    }}
  </style>
</head>
<body>

  <!-- DELOITTE / PWC TRID AUDIT WORKPAPER HEADER -->
  <header class="trid-topbar">
    <div class="trid-brand">
      <div class="trid-badge">TRID · §1026.19</div>
      <div>
        <div class="trid-title">Closing Disclosure (CD) Tolerance Auditor · LE vs. CD Fee Reconciliation Workpaper</div>
        <div class="trid-sub">CFPB TILA-RESPA Integrated Disclosure Rule (12 CFR § 1026.19(e)/(f)) · 0% Zero-Tolerance &amp; 10% Cumulative Bucket Audit</div>
      </div>
    </div>
    <div class="topbar-controls">
      <div class="model-box">
        <span>TRID Compliance Model:</span>
        <select id="app-model-select" onchange="window.syncSelectedModel(this.value)">
          <option value="gemini-4-argon" selected>gemini-4-argon (12 CFR § 1026.19 Audit)</option>
          <option value="gemini-3.8-flash">gemini-3.8-flash (Instant Fee Recon)</option>
        </select>
      </div>
      <button class="btn-trid-audio" onclick="window.playTridAudioSummary(this)">
        🔊 Listen to TRID Compliance Officer Summary
      </button>
      <button class="btn-trid-cure" onclick="window.runLiveVertexAI()">
        Certify Lender Tolerance Cure
      </button>
    </div>
  </header>

  <!-- 4-BUCKET EXECUTIVE KPI STRIP -->
  <section class="bucket-strip">
    <div class="bucket-card">
      <div class="bucket-lbl">0% Zero-Tolerance Bucket Overage</div>
      <div class="bucket-val" id="kpi-zero-over" style="color:var(--crimson);">+$250.00</div>
      <div class="bucket-sub">Lender Origination &amp; Appraisal Fees (0% Cap)</div>
    </div>
    <div class="bucket-card">
      <div class="bucket-lbl">10% Cumulative Bucket Variance</div>
      <div class="bucket-val" id="kpi-ten-over" style="color:var(--crimson);">+20.9% (+$235 Over Cap)</div>
      <div class="bucket-sub" id="kpi-ten-sub">LE Baseline $2,150 · 110% Cap = $2,365.00</div>
    </div>
    <div class="bucket-card">
      <div class="bucket-lbl">Unlimited Bucket (Shopped / Prepaid)</div>
      <div class="bucket-val" style="color:var(--emerald);">$0.00 Cure</div>
      <div class="bucket-sub">Owner's Title &amp; Prepaid Daily Interest (Exempt)</div>
    </div>
    <div class="bucket-card cure">
      <div class="bucket-lbl">Mandatory 12 CFR § 1026.19(f) Lender Cure</div>
      <div class="bucket-val" id="kpi-total-cure" style="color:var(--crimson);">$485.00</div>
      <div class="bucket-sub">Auto-Applied to CD Section J Lender Credits</div>
    </div>
  </section>

  <!-- MAIN 2-COLUMN RECONCILIATION WORKPAPER -->
  <main class="workpaper-grid">
    <!-- LEFT: SIDE-BY-SIDE LOAN ESTIMATE (LE) VS CLOSING DISCLOSURE (CD) TABLE -->
    <div class="recon-card">
      <div class="recon-header">
        <div>
          <div style="font-size:15.5px;font-weight:700;color:var(--ink);">Loan Estimate (LE) vs. Final Closing Disclosure (CD) Fee Reconciliation</div>
          <div style="font-size:12px;color:var(--muted);">Loan #RKT-9948120 · Initial LE Issued 09/18/2026 · Final CD Issued 10/21/2026 (No Valid Changed Circumstance)</div>
        </div>
        <span style="font-family:'IBM Plex Mono',monospace;font-size:11.5px;background:var(--teal-soft);color:var(--teal-dark);padding:4px 10px;border-radius:4px;font-weight:700;">Workpaper WP-TRID-205</span>
      </div>

      <table class="recon-table">
        <thead>
          <tr>
            <th>CD Section &amp; Fee Line Item</th>
            <th class="num">Disclosed LE</th>
            <th class="num">Final CD</th>
            <th class="num">Variance ($)</th>
            <th>TRID Tolerance Ruling</th>
          </tr>
        </thead>
        <tbody>
          <tr class="bucket-row">
            <td colspan="5">Bucket 1 — 0% Zero-Tolerance Category (12 CFR § 1026.19(e)(3)(i))</td>
          </tr>
          <tr>
            <td><strong>Sec A · Rocket Mortgage Origination &amp; Underwriting Fee</strong></td>
            <td class="num">$1,250.00</td>
            <td class="num" id="cell-orig-cd">$1,500.00</td>
            <td class="num" id="cell-orig-var" style="color:var(--crimson);font-weight:700;">+$250.00</td>
            <td><span class="pill-cure" id="badge-orig">CURE REQUIRED (+$250.00)</span></td>
          </tr>
          <tr>
            <td><strong>Sec B · Appraisal Fee (Amrock AMC — Did Not Shop)</strong></td>
            <td class="num">$650.00</td>
            <td class="num">$650.00</td>
            <td class="num">$0.00</td>
            <td><span class="pill-pass">COMPLIANT (0.0%)</span></td>
          </tr>
          <tr>
            <td><strong>Sec E · Municipal Transfer Taxes</strong></td>
            <td class="num">$1,840.00</td>
            <td class="num">$1,840.00</td>
            <td class="num">$0.00</td>
            <td><span class="pill-pass">COMPLIANT (0.0%)</span></td>
          </tr>

          <tr class="bucket-row">
            <td colspan="5">Bucket 2 — 10% Cumulative Tolerance Category (12 CFR § 1026.19(e)(3)(ii))</td>
          </tr>
          <tr>
            <td><strong>Sec B · Title Settlement &amp; Lender's Title Policy (Provider on WSSP)</strong></td>
            <td class="num">$1,850.00</td>
            <td class="num">$2,150.00</td>
            <td class="num">+$300.00</td>
            <td><span class="pill-pass">POOLED IN 10% BUCKET</span></td>
          </tr>
          <tr>
            <td><strong>Sec E · County Deed &amp; Mortgage Recording Fees</strong></td>
            <td class="num">$300.00</td>
            <td class="num" id="cell-rec-cd">$450.00</td>
            <td class="num" id="cell-rec-var">+$150.00</td>
            <td><span class="pill-pass">POOLED IN 10% BUCKET</span></td>
          </tr>
          <tr style="background:#F8FAFC;font-weight:700;">
            <td><strong>10% Cumulative Bucket Subtotal (110% Max Permitted = $2,365.00)</strong></td>
            <td class="num">$2,150.00</td>
            <td class="num" id="cell-ten-cd">$2,600.00</td>
            <td class="num" id="cell-ten-var" style="color:var(--crimson);">+$450.00 (+20.9%)</td>
            <td><span class="pill-cure" id="badge-ten">EXCEEDS 10% CAP BY $235.00</span></td>
          </tr>

          <tr class="bucket-row">
            <td colspan="5">Bucket 3 — Unlimited Tolerance Category (12 CFR § 1026.19(e)(3)(iii))</td>
          </tr>
          <tr>
            <td><strong>Sec F · Prepaid Hazard Insurance &amp; Daily Per-Diem Interest</strong></td>
            <td class="num">$2,120.00</td>
            <td class="num">$2,290.00</td>
            <td class="num">+$170.00</td>
            <td><span class="pill-pass">EXEMPT · UNLIMITED BUCKET</span></td>
          </tr>

          <tr class="cure-row">
            <td colspan="2">Total Mandatory Lender Tolerance Cure Credit (CD Page 2, Section J)</td>
            <td class="num" colspan="2" id="cell-total-cure" style="font-size:16px;">-$485.00 CURE CREDIT</td>
            <td>12 CFR § 1026.19(f)(2)(v)</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- RIGHT: INTERACTIVE SLIDERS & COMPLIANCE OFFICER MEMO -->
    <div class="side-col">
      <div class="audit-panel">
        <div style="display:flex;justify-content:space-between;align-items:center;">
          <h3 style="font-size:15px;font-weight:700;color:var(--ink);">Interactive TRID Fee &amp; Cure Calculator</h3>
          <span style="font-family:'IBM Plex Mono',monospace;font-size:11px;color:var(--teal);font-weight:700;">Live 12 CFR § 1026.19 Math</span>
        </div>
        <p style="font-size:12px;color:var(--muted);margin-top:4px;">Adjust Final CD Lender Origination Fee (0% Bucket) and County Recording Fee (10% Bucket) to test automatic Lender Cure calculation.</p>

        <div class="slider-box">
          <div style="display:flex;justify-content:space-between;font-size:12.5px;font-weight:700;">
            <span>Final CD Lender Origination Fee (LE = $1,250)</span>
            <span id="lbl-orig" style="font-family:'IBM Plex Mono',monospace;color:var(--crimson);">$1,500.00</span>
          </div>
          <input type="range" id="sl-orig" min="1250" max="2000" step="25" value="1500" oninput="window.recalcTridCure()" />
        </div>

        <div class="slider-box">
          <div style="display:flex;justify-content:space-between;font-size:12.5px;font-weight:700;">
            <span>Final CD County Recording Fee (LE = $300)</span>
            <span id="lbl-rec" style="font-family:'IBM Plex Mono',monospace;color:var(--teal-dark);">$450.00</span>
          </div>
          <input type="range" id="sl-rec" min="150" max="800" step="25" value="450" oninput="window.recalcTridCure()" />
        </div>
      </div>

      <div class="audit-panel">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
          <h3 style="font-size:15px;font-weight:700;color:var(--ink);">TRID Compliance Officer Certification</h3>
          <span id="live-model-pill" style="font-family:'IBM Plex Mono',monospace;font-size:11px;color:var(--teal);font-weight:700;">gemini-4-argon</span>
        </div>
        <div id="trid-audit-output" style="font-size:12.5px;line-height:1.6;color:var(--ink);background:#F8FAFC;padding:14px;border:1px solid #E2E8F0;border-radius:6px;">
          <strong>CFPB TRID RECONCILIATION AUDIT (12 CFR § 1026.19(f)):</strong><br/>
          • <strong>0% Zero-Tolerance Cure ($250.00):</strong> Lender Origination increased from $1,250.00 on the LE to $1,500.00 on the CD without a valid Changed Circumstance. Full $250.00 overage must be cured.<br/>
          • <strong>10% Cumulative Bucket Cure ($235.00):</strong> Aggregate 10% bucket fees rose from $2,150.00 to $2,600.00 (+20.9%), exceeding the $2,365.00 (110%) cap by $235.00.<br/>
          • <strong>Total Section J Cure Credit:</strong> <strong>$485.00</strong> ($250.00 + $235.00) automatically credited prior to consummation.
        </div>
      </div>
    </div>
  </main>

  <script>
    window.recalcTridCure = function() {{
      const origLe = 1250;
      const origCd = parseFloat(document.getElementById('sl-orig').value || 1500);
      const recLe = 300;
      const recCd = parseFloat(document.getElementById('sl-rec').value || 450);
      const titleLe = 1850;
      const titleCd = 2150;

      const zeroOver = Math.max(0, origCd - origLe);
      const tenLeTotal = titleLe + recLe; // 2150
      const tenCap = tenLeTotal * 1.10; // 2365
      const tenCdTotal = titleCd + recCd;
      const tenVar = tenCdTotal - tenLeTotal;
      const tenPct = (tenVar / tenLeTotal) * 100.0;
      const tenCure = Math.max(0, tenCdTotal - tenCap);
      const totalCure = zeroOver + tenCure;

      document.getElementById('lbl-orig').innerText = '$' + origCd.toFixed(2);
      document.getElementById('lbl-rec').innerText = '$' + recCd.toFixed(2);

      document.getElementById('cell-orig-cd').innerText = '$' + origCd.toLocaleString('en-US', {{minimumFractionDigits:2}});
      document.getElementById('cell-orig-var').innerText = '+$' + zeroOver.toFixed(2);
      document.getElementById('badge-orig').innerText = zeroOver > 0 ? 'CURE REQUIRED (+$' + zeroOver.toFixed(2) + ')' : 'COMPLIANT ($0.00)';
      document.getElementById('badge-orig').className = zeroOver > 0 ? 'pill-cure' : 'pill-pass';

      document.getElementById('cell-rec-cd').innerText = '$' + recCd.toFixed(2);
      document.getElementById('cell-rec-var').innerText = (recCd - recLe >= 0 ? '+$' : '-$') + Math.abs(recCd - recLe).toFixed(2);

      document.getElementById('cell-ten-cd').innerText = '$' + tenCdTotal.toLocaleString('en-US', {{minimumFractionDigits:2}});
      document.getElementById('cell-ten-var').innerText = '+$' + tenVar.toFixed(2) + ' (+' + tenPct.toFixed(1) + '%)';
      document.getElementById('badge-ten').innerText = tenCure > 0 ? 'EXCEEDS 10% CAP BY $' + tenCure.toFixed(2) : 'WITHIN 10% CAP ($0 CURE)';
      document.getElementById('badge-ten').className = tenCure > 0 ? 'pill-cure' : 'pill-pass';

      document.getElementById('cell-total-cure').innerText = '-$' + totalCure.toFixed(2) + ' CURE CREDIT';
      document.getElementById('kpi-zero-over').innerText = '+$' + zeroOver.toFixed(2);
      document.getElementById('kpi-ten-over').innerText = '+' + tenPct.toFixed(1) + '% (+$' + tenCure.toFixed(0) + ' Over Cap)';
      document.getElementById('kpi-total-cure').innerText = '$' + totalCure.toFixed(2);
    }};

    window.playTridAudioSummary = function(btnEl) {{
      const totalCure = document.getElementById('kpi-total-cure').innerText;
      const script = "TRID Closing Disclosure Compliance Summary under 12 CFR Section 1026.19. Comparing the initial Loan Estimate to the final Closing Disclosure reveals a 250 dollar zero-tolerance overage on the lender origination fee and a 235 dollar overage above the 110 percent cap in the 10 percent cumulative bucket for title and county recording fees. To ensure full CFPB compliance prior to closing, a mandatory lender tolerance cure credit of " + totalCure + " has been applied to Section J on Page 2 of the Closing Disclosure.";
      if (window.playLiveCallClip) {{
        window.playLiveCallClip(script, "Fenrir", "Chief TRID Compliance Officer", btnEl);
      }}
    }};

    window.runLiveVertexAI = async function() {{
      const model = window.getSelectedModel ? window.getSelectedModel() : 'gemini-4-argon';
      const totalCure = document.getElementById('kpi-total-cure').innerText;
      const outEl = document.getElementById('trid-audit-output');
      outEl.innerHTML = '<em>Running Vertex AI (' + model + ') 12 CFR § 1026.19(f) Closing Disclosure Tolerance Audit...</em>';
      try {{
        const res = await fetch('/api/run-demo', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{
            code: '2.5',
            model: model,
            user_input: 'Generate a CFPB TRID 12 CFR 1026.19(f) Closing Disclosure Tolerance Audit memo certifying a Section J Lender Cure Credit of ' + totalCure + ' across the 0% Zero-Tolerance and 10% Cumulative buckets.'
          }})
        }});
        const data = await res.json();
        const text = data.output || data.response || data.result || '';
        if (text) {{
          outEl.innerHTML = '<strong>VERTEX AI (' + model.toUpperCase() + ') TRID CURE CERTIFICATION:</strong><br/>' + text.replace(/\\n/g, '<br/>');
        }} else {{
          outEl.innerHTML = '<strong>TRID CURE CERTIFIED (' + model + '):</strong> Mandatory Lender Tolerance Cure Credit of <strong>' + totalCure + '</strong> applied to CD Section J per 12 CFR § 1026.19(f)(2)(v).';
        }}
      }} catch (e) {{
        outEl.innerHTML = '<strong>TRID CURE CERTIFIED:</strong> Mandatory Lender Tolerance Cure Credit of <strong>' + totalCure + '</strong> applied to CD Section J per 12 CFR § 1026.19(f)(2)(v).';
      }}
    }};
  </script>

  {floating_bar}
</body>
</html>"""
