# -*- coding: utf-8 -*-
"""Square 5.4: Audit Trail & Adverse Action Generator — Vertex AI Explainable AI
Design Style: Official Printable CFPB Regulation B Form C-1 Legal Notice on Desk Backdrop
(#EDF2F7 light desk gray + #FFFFFF crisp bordered paper certificate, Merriweather serif + Public Sans).
"""

from shared.standalone_uis.base_helpers import render_floating_control_bar_and_drawer


def render_sq_5_4(auth_token: str) -> str:
    code = "5.4"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Audit Trail & Adverse Action Generator | Official CFPB Appendix C-1 Notice</title>
  <link href="https://fonts.googleapis.com/css2?family=Merriweather:ital,wght@0,400;0,700;0,900;1,400&family=Public+Sans:wght@400;500;600;700;800&family=IBM+Plex+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  <style>
    :root {{
      --desk: #EDF2F7;
      --paper: #FFFFFF;
      --ink: #0F172A;
      --ink-muted: #475569;
      --federal-navy: #1E3A8A;
      --crimson: #991B1B;
      --green: #166534;
      --border: #CBD5E1;
      --paper-border: #94A3B8;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      background-color: var(--desk);
      color: var(--ink);
      font-family: 'Public Sans', -apple-system, BlinkMacSystemFont, sans-serif;
      min-height: 100vh;
      padding-bottom: 92px;
    }}
    .serif {{ font-family: 'Merriweather', Georgia, serif; }}
    .mono {{ font-family: 'IBM Plex Mono', monospace; }}

    /* Top Compliance Control Bar */
    .top-bar {{
      background: #FFFFFF;
      border-bottom: 1px solid var(--border);
      padding: 14px 32px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 14px;
      box-shadow: 0 1px 4px rgba(15, 23, 42, 0.05);
    }}
    .bar-title {{
      font-size: 18px;
      font-weight: 800;
      color: var(--ink);
    }}
    .bar-sub {{
      font-size: 12.5px;
      color: var(--ink-muted);
    }}
    .bar-actions {{
      display: flex;
      align-items: center;
      gap: 10px;
      flex-wrap: wrap;
    }}
    .model-select-box {{
      background: #F8FAFC;
      border: 1px solid var(--border);
      padding: 5px 12px;
      border-radius: 6px;
      font-size: 12px;
      font-weight: 600;
      display: flex;
      align-items: center;
      gap: 6px;
    }}
    .model-select-box select {{
      background: transparent;
      border: none;
      font-family: 'IBM Plex Mono', monospace;
      font-weight: 700;
      font-size: 12px;
      color: var(--federal-navy);
      outline: none;
      cursor: pointer;
    }}
    .btn-audio {{
      background: var(--federal-navy);
      color: #FFFFFF;
      border: none;
      padding: 9px 16px;
      border-radius: 6px;
      font-family: inherit;
      font-size: 13px;
      font-weight: 600;
      cursor: pointer;
    }}
    .btn-print {{
      background: #FFFFFF;
      color: var(--ink);
      border: 1px solid var(--border);
      padding: 9px 14px;
      border-radius: 6px;
      font-family: inherit;
      font-size: 13px;
      font-weight: 600;
      cursor: pointer;
    }}

    /* Workspace Layout: Left Underwriting Sliders + Right Official CFPB Form C-1 Paper Certificate */
    .desk-workspace {{
      max-width: 1420px;
      margin: 26px auto;
      padding: 0 32px;
      display: grid;
      grid-template-columns: 420px 1fr;
      gap: 28px;
      align-items: start;
    }}
    @media (max-width: 1080px) {{
      .desk-workspace {{ grid-template-columns: 1fr; }}
    }}

    /* Left Panel: Interactive Applicant Credit/DTI/Reserves Sliders */
    .simulator-panel {{
      background: #FFFFFF;
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 20px 22px;
      box-shadow: 0 4px 12px rgba(15, 23, 42, 0.05);
      display: flex;
      flex-direction: column;
      gap: 18px;
    }}
    .panel-kicker {{
      font-size: 11px;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      color: var(--federal-navy);
    }}
    .panel-title {{
      font-size: 16px;
      font-weight: 800;
      color: var(--ink);
      margin-top: 2px;
    }}
    .slider-group {{
      background: #F8FAFC;
      border: 1px solid #E2E8F0;
      border-radius: 6px;
      padding: 12px 14px;
    }}
    .slider-top {{
      display: flex;
      justify-content: space-between;
      font-size: 13px;
      font-weight: 700;
      margin-bottom: 6px;
    }}
    .slider-group input[type=range] {{
      width: 100%;
      accent-color: var(--federal-navy);
      cursor: pointer;
    }}
    .slider-meta {{
      display: flex;
      justify-content: space-between;
      font-size: 11.5px;
      color: var(--ink-muted);
      margin-top: 4px;
    }}

    /* Right Panel: Official Printable CFPB Appendix C-1 Legal Certificate on Desk */
    .cfpb-certificate {{
      background: var(--paper);
      border: 1px solid var(--paper-border);
      box-shadow: 0 12px 32px rgba(15, 23, 42, 0.10), 0 2px 6px rgba(15, 23, 42, 0.06);
      padding: 40px 48px;
      position: relative;
    }}
    .certificate-inner-border {{
      border: 2px solid #1E293B;
      padding: 28px 32px;
    }}
    .cfpb-top-row {{
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      border-bottom: 2px solid #0F172A;
      padding-bottom: 16px;
      margin-bottom: 18px;
      gap: 16px;
      flex-wrap: wrap;
    }}
    .form-title {{
      font-family: 'Merriweather', Georgia, serif;
      font-size: 20px;
      font-weight: 900;
      color: #0F172A;
      text-transform: uppercase;
      letter-spacing: 0.01em;
    }}
    .form-subtitle {{
      font-size: 12.5px;
      color: var(--ink-muted);
      margin-top: 4px;
      font-weight: 600;
    }}
    .omb-box {{
      font-family: 'IBM Plex Mono', monospace;
      font-size: 11px;
      border: 1px solid #0F172A;
      padding: 6px 10px;
      text-align: right;
      background: #F8FAFC;
    }}

    .applicant-grid {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      border: 1px solid #0F172A;
      margin-bottom: 20px;
      font-size: 12.5px;
    }}
    .app-cell {{
      padding: 10px 12px;
      border-right: 1px solid #0F172A;
      border-bottom: 1px solid #0F172A;
    }}
    .app-cell:nth-child(3n) {{ border-right: none; }}
    .app-label {{
      font-size: 10px;
      font-weight: 700;
      text-transform: uppercase;
      color: var(--ink-muted);
      letter-spacing: 0.04em;
    }}
    .app-val {{
      font-weight: 700;
      color: var(--ink);
      margin-top: 3px;
    }}

    .part-header {{
      background: #0F172A;
      color: #FFFFFF;
      font-family: 'Merriweather', Georgia, serif;
      font-size: 13px;
      font-weight: 700;
      padding: 7px 12px;
      text-transform: uppercase;
      letter-spacing: 0.04em;
      margin-bottom: 12px;
    }}

    .reason-row {{
      display: flex;
      align-items: flex-start;
      gap: 12px;
      padding: 12px 14px;
      border: 1px solid #CBD5E1;
      margin-bottom: 10px;
      background: #FCFDFE;
    }}
    .reason-row.active-reason {{
      border-color: var(--crimson);
      background: #FEF2F2;
    }}
    .checkbox-sq {{
      width: 18px;
      height: 18px;
      border: 2px solid #0F172A;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      font-weight: 900;
      font-size: 13px;
      flex-shrink: 0;
      margin-top: 2px;
      background: #FFFFFF;
    }}
    .reason-row.active-reason .checkbox-sq {{
      border-color: var(--crimson);
      color: var(--crimson);
    }}
    .reason-code-title {{
      font-weight: 800;
      font-size: 13.5px;
      color: #0F172A;
    }}
    .reason-shap-detail {{
      font-size: 12.5px;
      color: #334155;
      margin-top: 3px;
      line-height: 1.5;
    }}

    .ecoa-boilerplate {{
      margin-top: 18px;
      padding: 14px 16px;
      border: 1px solid #0F172A;
      background: #F8FAFC;
      font-family: 'Merriweather', Georgia, serif;
      font-size: 11.5px;
      line-height: 1.65;
      color: #1E293B;
    }}
    .hash-footer {{
      margin-top: 14px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-family: 'IBM Plex Mono', monospace;
      font-size: 11px;
      color: var(--ink-muted);
      flex-wrap: wrap;
      gap: 8px;
    }}
    .ai-audit-box {{
      margin-top: 14px;
      background: #F8FAFC;
      border: 1px solid var(--border);
      padding: 14px;
      font-size: 12.5px;
      line-height: 1.6;
      display: none;
      white-space: pre-wrap;
    }}
  </style>
</head>
<body>

  <!-- Top Compliance Bar -->
  <header class="top-bar">
    <div>
      <div class="bar-title">Audit Trail &amp; Adverse Action Generator (CFPB Regulation B Appendix C-1)</div>
      <div class="bar-sub">Deterministic SHAP Feature Attribution → Statutory ECOA Reason Codes (12 CFR Part 1002 Supp. I)</div>
    </div>
    <div class="bar-actions">
      <div class="model-select-box">
        <span>Model:</span>
        <select id="app-model-select" onchange="window.syncSelectedModel(this.value)">
          <option value="gemini-4-argon">gemini-4-argon</option>
          <option value="gemini-3.8-flash">gemini-3.8-flash</option>
        </select>
      </div>
      <button class="btn-print" onclick="window.print()">🖨️ Print Official Form C-1</button>
      <button class="btn-audio" onclick="window.playAdverseAudio(this)">
        🔊 Read Official Compliance Audit Summary
      </button>
    </div>
  </header>

  <!-- Main Desk Workspace -->
  <main class="desk-workspace">

    <!-- Left Panel: Interactive Applicant Credit / DTI / Reserves Sliders -->
    <aside class="simulator-panel">
      <div>
        <div class="panel-kicker">UNDERWRITING TELEMETRY INPUTS</div>
        <h2 class="panel-title">Applicant Profile Simulator</h2>
        <p style="font-size:12.5px;color:var(--ink-muted);margin-top:4px;">
          Adjust borrower parameters to see real-time SHAP attribution and statutory CFPB Form C-1 reason code updates.
        </p>
      </div>

      <!-- Slider 1: Back-End DTI -->
      <div class="slider-group">
        <div class="slider-top">
          <span>Back-End Debt-to-Income (DTI)</span>
          <span class="mono" id="dti-val-lbl" style="color:var(--crimson);">48.2%</span>
        </div>
        <input type="range" id="slider-dti" min="28" max="55" step="0.2" value="48.2" oninput="window.updateAdverseForm()">
        <div class="slider-meta">
          <span>Guideline Max: ≤ 45.0%</span>
          <span id="dti-status-lbl" style="font-weight:700;color:var(--crimson);">Exceeds Limit (+3.2%)</span>
        </div>
      </div>

      <!-- Slider 2: Liquid Post-Close Reserves -->
      <div class="slider-group">
        <div class="slider-top">
          <span>Verified Liquid Reserves (Months PITI)</span>
          <span class="mono" id="res-val-lbl" style="color:var(--crimson);">1.5 Months</span>
        </div>
        <input type="range" id="slider-res" min="0" max="12" step="0.5" value="1.5" oninput="window.updateAdverseForm()">
        <div class="slider-meta">
          <span>Jumbo / High-Balance Min: 6.0 Mo</span>
          <span id="res-status-lbl" style="font-weight:700;color:var(--crimson);">Shortfall (-4.5 Mo)</span>
        </div>
      </div>

      <!-- Slider 3: Middle Representative FICO Score -->
      <div class="slider-group">
        <div class="slider-top">
          <span>Representative Tri-Merge FICO Score</span>
          <span class="mono" id="fico-val-lbl" style="color:var(--ink);">712</span>
        </div>
        <input type="range" id="slider-fico" min="580" max="820" step="1" value="712" oninput="window.updateAdverseForm()">
        <div class="slider-meta">
          <span>Program Min: 680</span>
          <span id="fico-status-lbl" style="font-weight:700;color:var(--green);">Passing (+32 pts)</span>
        </div>
      </div>

      <button class="btn-audio" style="width:100%;background:#0F172A;" onclick="window.runLiveVertexAI()">
        ⚡ Synthesize Vertex AI Explainable AI Audit Packet
      </button>

      <div id="ai-adverse-output" class="ai-audit-box"></div>
    </aside>

    <!-- Right Panel: Official Printable CFPB Appendix C-1 Statement of Credit Denial -->
    <section class="cfpb-certificate">
      <div class="certificate-inner-border">

        <div class="cfpb-top-row">
          <div>
            <h2 class="form-title">Statement of Credit Denial, Termination, or Change</h2>
            <div class="form-subtitle">
              OFFICIAL CFPB APPENDIX C TO PART 1002 — SAMPLE NOTIFICATION FORM C-1 (EQUAL CREDIT OPPORTUNITY ACT)
            </div>
          </div>
          <div class="omb-box">
            <div><strong>REGULATION B · 12 CFR § 1002.9</strong></div>
            <div>DOC ID: RKT-ECOA-2026-99412</div>
          </div>
        </div>

        <div class="applicant-grid">
          <div class="app-cell">
            <div class="app-label">Applicant Name &amp; Property</div>
            <div class="app-val">Marcus &amp; Elena Vance · Detroit, MI 48226</div>
          </div>
          <div class="app-cell">
            <div class="app-label">Loan Application Number</div>
            <div class="app-val mono">#RKT-304981120 (30-Yr Fixed Conforming)</div>
          </div>
          <div class="app-cell">
            <div class="app-label">Underwriting Decision Status</div>
            <div class="app-val" id="form-decision-badge" style="color:var(--crimson);">ADVERSE ACTION — COUNTEROFFER / DENIAL</div>
          </div>
        </div>

        <div class="part-header">
          PART I — PRINCIPAL REASON(S) FOR CREDIT DENIAL, TERMINATION, OR OTHER ACTION TAKEN CONCERNING CREDIT
        </div>
        <p style="font-size:12px;color:var(--ink-muted);margin-bottom:12px;">
          <em>Pursuant to 12 CFR § 1002.9(a)(2), the specific principal reasons mapped deterministically from Vertex AI Explainable AI SHAP values are checked below:</em>
        </p>

        <!-- ECOA Code 01: DTI -->
        <div class="reason-row active-reason" id="reason-row-dti">
          <div class="checkbox-sq" id="chk-dti">✓</div>
          <div>
            <div class="reason-code-title" id="title-dti">
              ECOA Reason Code 01: Excessive Obligations in Relation to Income (Debt-to-Income Ratio 48.2% exceeds 45.0% limit)
            </div>
            <div class="reason-shap-detail" id="detail-dti">
              <strong>Vertex AI SHAP Attribution (+0.412 Log-Odds Impact):</strong> Verified monthly housing + installment obligations of $5,495 against gross qualifying monthly income of $11,400 yield a <strong>48.2% back-end DTI</strong>, exceeding the <strong>45.0% program cap</strong>. Counteroffer Cure: Pay down $365/mo auto installment balance ($7,800 payoff) or reduce loan amount by $42,000.
            </div>
          </div>
        </div>

        <!-- ECOA Code 04: Liquid Reserves -->
        <div class="reason-row active-reason" id="reason-row-res">
          <div class="checkbox-sq" id="chk-res">✓</div>
          <div>
            <div class="reason-code-title" id="title-res">
              ECOA Reason Code 04: Insufficient Liquid Reserves for Closing &amp; Post-Closing PITI Cushion (1.5 Mo vs. 6.0 Mo Req)
            </div>
            <div class="reason-shap-detail" id="detail-res">
              <strong>Vertex AI SHAP Attribution (+0.285 Log-Odds Impact):</strong> Plaid asset verification across Chase Checking (#4419) and Fidelity Brokerage (#8802) confirms <strong>1.5 months ($5,700)</strong> post-closing liquid reserves against the required <strong>6.0 months ($22,800)</strong> guideline.
            </div>
          </div>
        </div>

        <!-- ECOA Code 12: Credit Score -->
        <div class="reason-row" id="reason-row-fico">
          <div class="checkbox-sq" id="chk-fico"></div>
          <div>
            <div class="reason-code-title" id="title-fico">
              ECOA Reason Code 12: Credit Application Incomplete / Delinquent Past or Present Credit Obligations (FICO 712 Passing)
            </div>
            <div class="reason-shap-detail" id="detail-fico">
              <strong>Vertex AI SHAP Attribution (-0.190 Favorable Impact):</strong> Representative middle FICO score of <strong>712</strong> satisfies the 680 minimum threshold. Not a principal adverse factor.
            </div>
          </div>
        </div>

        <div class="part-header" style="margin-top:18px;">
          PART II — DISCLOSURE OF USE OF INFORMATION OBTAINED FROM AN OUTSIDE SOURCE (FCRA § 615(a))
        </div>

        <div class="ecoa-boilerplate">
          <strong>Notice:</strong> The Federal Equal Credit Opportunity Act prohibits creditors from discriminating against credit applicants on the basis of race, color, religion, national origin, sex, marital status, age (provided the applicant has the capacity to enter into a binding contract); because all or part of the applicant's income derives from any public assistance program; or because the applicant has in good faith exercised any right under the Consumer Credit Protection Act. The federal agency that administers compliance with this law concerning this creditor is the <strong>Consumer Financial Protection Bureau, 1700 G Street NW, Washington, DC 20552</strong>.
        </div>

        <div class="hash-footer">
          <span>CREDITOR: ROCKET MORTGAGE, LLC · 1050 WOODWARD AVE, DETROIT, MI 48226 (NMLS #3030)</span>
          <span>AUDIT SHA-256: <strong id="audit-hash">9f84c2e1...b7410a</strong></span>
        </div>

      </div>
    </section>

  </main>

  <script>
    window.updateAdverseForm = function() {{
      const dti = parseFloat(document.getElementById('slider-dti').value);
      const res = parseFloat(document.getElementById('slider-res').value);
      const fico = parseInt(document.getElementById('slider-fico').value, 10);

      const dtiFail = dti > 45.0;
      const resFail = res < 6.0;
      const ficoFail = fico < 680;

      // Left slider labels
      const dtiLbl = document.getElementById('dti-val-lbl');
      dtiLbl.innerText = dti.toFixed(1) + "%";
      dtiLbl.style.color = dtiFail ? "var(--crimson)" : "var(--green)";
      const dtiSt = document.getElementById('dti-status-lbl');
      dtiSt.innerText = dtiFail ? `Exceeds Limit (+${{(dti - 45).toFixed(1)}}%)` : `Within Limit (${{(45 - dti).toFixed(1)}}% buffer)`;
      dtiSt.style.color = dtiFail ? "var(--crimson)" : "var(--green)";

      const resLbl = document.getElementById('res-val-lbl');
      resLbl.innerText = res.toFixed(1) + " Months";
      resLbl.style.color = resFail ? "var(--crimson)" : "var(--green)";
      const resSt = document.getElementById('res-status-lbl');
      resSt.innerText = resFail ? `Shortfall (-${{(6 - res).toFixed(1)}} Mo)` : `Satisfies Reserve Floor`;
      resSt.style.color = resFail ? "var(--crimson)" : "var(--green)";

      const ficoLbl = document.getElementById('fico-val-lbl');
      ficoLbl.innerText = fico;
      ficoLbl.style.color = ficoFail ? "var(--crimson)" : "var(--green)";
      const ficoSt = document.getElementById('fico-status-lbl');
      ficoSt.innerText = ficoFail ? `Below 680 Min (${{fico - 680}} pts)` : `Passing (+${{fico - 680}} pts)`;
      ficoSt.style.color = ficoFail ? "var(--crimson)" : "var(--green)";

      // Right Certificate checkboxes
      const rowDti = document.getElementById('reason-row-dti');
      rowDti.classList.toggle('active-reason', dtiFail);
      document.getElementById('chk-dti').innerText = dtiFail ? "✓" : "";
      document.getElementById('title-dti').innerText = dtiFail
        ? `ECOA Reason Code 01: Excessive Obligations in Relation to Income (Debt-to-Income Ratio ${{dti.toFixed(1)}}% exceeds 45.0% limit)`
        : `ECOA Reason Code 01: Debt-to-Income Ratio (${{dti.toFixed(1)}}% satisfies ≤ 45.0% guideline)`;

      const rowRes = document.getElementById('reason-row-res');
      rowRes.classList.toggle('active-reason', resFail);
      document.getElementById('chk-res').innerText = resFail ? "✓" : "";
      document.getElementById('title-res').innerText = resFail
        ? `ECOA Reason Code 04: Insufficient Liquid Reserves (${{res.toFixed(1)}} Mo verified vs. 6.0 Mo requirement)`
        : `ECOA Reason Code 04: Verified Liquid Reserves (${{res.toFixed(1)}} Mo satisfies ≥ 6.0 Mo requirement)`;

      const rowFico = document.getElementById('reason-row-fico');
      rowFico.classList.toggle('active-reason', ficoFail);
      document.getElementById('chk-fico').innerText = ficoFail ? "✓" : "";
      document.getElementById('title-fico').innerText = ficoFail
        ? `ECOA Reason Code 12: Credit Score Below Program Minimum (FICO ${{fico}} < 680 floor)`
        : `ECOA Reason Code 12: Representative Credit Score (FICO ${{fico}} Passing)`;

      const decBadge = document.getElementById('form-decision-badge');
      if (!dtiFail && !resFail && !ficoFail) {{
        decBadge.innerText = "CLEAR TO APPROVE — ALL ECOA CONDITIONS CURED";
        decBadge.style.color = "var(--green)";
      }} else {{
        decBadge.innerText = "ADVERSE ACTION — COUNTEROFFER / DENIAL";
        decBadge.style.color = "var(--crimson)";
      }}
    }};

    window.playAdverseAudio = function(btnEl) {{
      const dti = document.getElementById('slider-dti').value;
      const res = document.getElementById('slider-res').value;
      const msg = `Official CFPB Regulation B Appendix C-1 Compliance Audit Summary for Loan Application 304981120. Vertex AI Explainable AI mapped our underwriting model's SHAP values directly to two statutory Equal Credit Opportunity Act reason codes. First, ECOA Reason Code 01: the applicant's back-end debt-to-income ratio is ${{dti}} percent, exceeding the 45.0 percent program ceiling. Second, ECOA Reason Code 04: verified post-closing liquid reserves are ${{res}} months against a 6.0 month requirement. Every number on this printable notice is deterministically bound to the Encompass audit log.`;
      window.playLiveCallClip(msg, "Kore", "Rocket Chief Compliance Officer", btnEl);
    }};

    window.runLiveVertexAI = async function() {{
      const out = document.getElementById('ai-adverse-output');
      out.style.display = 'block';
      const model = window.getSelectedModel ? window.getSelectedModel() : 'gemini-4-argon';
      const dti = document.getElementById('slider-dti').value;
      const res = document.getElementById('slider-res').value;
      const fico = document.getElementById('slider-fico').value;
      out.textContent = `Generating CFPB Form C-1 SHAP Audit Packet via Vertex AI (${{model}})...`;
      try {{
        const resp = await fetch('/api/run-demo', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{
            code: '5.4',
            model: model,
            scenario: `Generate CFPB Appendix C-1 Statement of Credit Denial and Cure Counteroffer for applicant with DTI=${{dti}}% (limit 45.0%), Liquid Reserves=${{res}} months (limit 6.0), and FICO=${{fico}}.`
          }})
        }});
        const data = await resp.json();
        out.textContent = data.output || data.text || "Adverse Action Notice generated.";
      }} catch (e) {{
        out.textContent = "Error: " + e.message;
      }}
    }};
  </script>

  {render_floating_control_bar_and_drawer(code, auth_token)}
</body>
</html>
"""
