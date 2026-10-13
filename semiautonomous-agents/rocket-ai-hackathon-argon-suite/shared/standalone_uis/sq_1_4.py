# -*- coding: utf-8 -*-
"""Square 1.4: Pre-Approval Refresh Assistant — Standalone UI Design File.
Visual Archetype: Apple Wallet / Clean Consumer Mobile- & Desktop-Friendly Banking App
(#F5F5F7 light warm gray background, #0071E3 clean blue CTA, #FFFFFF elevated certificate card,
DM Sans + Merriweather serif for the official Rocket Mortgage Verified Pre-Approval Letter)."""

from shared.standalone_uis.base_helpers import render_floating_control_bar_and_drawer


def render_sq_1_4(auth_token: str) -> str:
    controls = render_floating_control_bar_and_drawer("1.4", auth_token)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Rocket Mortgage · Saturday Open-House Pre-Approval Refresh Assistant</title>
  <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=Merriweather:ital,wght@0,400;0,700;1,400&family=IBM+Plex+Mono:wght@500;600&display=swap" rel="stylesheet">
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: 'DM Sans', -apple-system, BlinkMacSystemFont, sans-serif;
      background: #F5F5F7;
      color: #1D1D1F;
      min-height: 100vh;
      padding-bottom: 88px;
    }}
    .serif {{ font-family: 'Merriweather', Georgia, serif; }}
    .mono {{ font-family: 'IBM Plex Mono', monospace; }}

    /* Apple Wallet / Consumer Banking Header */
    .wallet-header {{
      background: rgba(255, 255, 255, 0.92);
      backdrop-filter: blur(16px);
      border-bottom: 1px solid #E5E5EA;
      padding: 14px 32px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      position: sticky;
      top: 0;
      z-index: 100;
    }}
    .apple-pill {{
      background: #E8F2FF;
      color: #0071E3;
      font-size: 12px;
      font-weight: 700;
      padding: 5px 12px;
      border-radius: 999px;
    }}

    /* 2-Column Workspace */
    .wallet-grid {{
      max-width: 1320px;
      margin: 28px auto;
      padding: 0 28px;
      display: grid;
      grid-template-columns: 440px 1fr;
      gap: 28px;
      align-items: start;
    }}
    @media (max-width: 1040px) {{
      .wallet-grid {{ grid-template-columns: 1fr; }}
    }}

    /* Left Consumer Controls Card */
    .adjuster-card {{
      background: #FFFFFF;
      border-radius: 20px;
      border: 1px solid #E5E5EA;
      padding: 24px;
      box-shadow: 0 8px 28px rgba(0, 0, 0, 0.04);
      display: flex;
      flex-direction: column;
      gap: 18px;
    }}
    .stepper-row {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      background: #F5F5F7;
      padding: 10px 14px;
      border-radius: 14px;
      border: 1px solid #E5E5EA;
    }}
    .step-btn {{
      width: 38px;
      height: 38px;
      border-radius: 10px;
      border: 1px solid #D2D2D7;
      background: #FFFFFF;
      color: #0071E3;
      font-size: 20px;
      font-weight: 700;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
    }}
    .step-btn:hover {{ background: #E8F2FF; }}

    /* Guardrail Status Banner */
    .guardrail-box {{
      padding: 14px 16px;
      border-radius: 14px;
      font-size: 13px;
      line-height: 1.5;
      transition: 0.2s;
    }}
    .guardrail-pass {{
      background: #ECFDF5;
      border: 1px solid #A7F3D0;
      color: #065F46;
    }}
    .guardrail-fail {{
      background: #FEF2F2;
      border: 1px solid #FECACA;
      color: #991B1B;
    }}

    /* Buttons */
    .blue-cta-btn {{
      background: #0071E3;
      color: #FFFFFF;
      border: none;
      border-radius: 12px;
      padding: 13px 18px;
      font-family: inherit;
      font-size: 14px;
      font-weight: 700;
      cursor: pointer;
      transition: 0.15s;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      width: 100%;
    }}
    .blue-cta-btn:hover {{ background: #005BB5; }}

    .voice-read-btn {{
      background: #F5F5F7;
      color: #0071E3;
      border: 1px solid #D2D2D7;
      border-radius: 12px;
      padding: 11px 16px;
      font-family: inherit;
      font-size: 13px;
      font-weight: 700;
      cursor: pointer;
      transition: 0.15s;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      width: 100%;
    }}
    .voice-read-btn:hover {{ background: #E8F2FF; border-color: #93C5FD; }}

    /* Official Printable Pre-Approval Certificate Card */
    .certificate-shell {{
      background: #FFFFFF;
      border-radius: 20px;
      border: 1px solid #D2D2D7;
      padding: 36px 42px;
      box-shadow: 0 12px 36px rgba(0, 0, 0, 0.06);
      position: relative;
    }}
    .cert-seal {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 6px 14px;
      border-radius: 999px;
      background: #ECFDF5;
      border: 1px solid #A7F3D0;
      color: #047857;
      font-family: 'DM Sans', sans-serif;
      font-size: 12px;
      font-weight: 700;
    }}
    .cert-grid {{
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 14px;
      margin: 22px 0;
      padding: 18px;
      background: #F9FAFB;
      border: 1px solid #E5E7EB;
      border-radius: 14px;
      font-family: 'DM Sans', sans-serif;
    }}
  </style>
</head>
<body>

  <!-- APPLE WALLET / CLEAN CONSUMER BANKING BAR -->
  <header class="wallet-header">
    <div style="display:flex;align-items:center;gap:12px;">
      <div style="width:36px;height:36px;border-radius:10px;background:#0071E3;color:#FFFFFF;display:flex;align-items:center;justify-content:center;font-weight:800;font-size:16px;">R</div>
      <div>
        <div style="font-size:16px;font-weight:800;color:#1D1D1F;">Rocket Mortgage · Pre-Approval Refresh Assistant</div>
        <div style="font-size:12px;color:#6E6E73;">Saturday Open-House Instant Offer Letter Customizer · Underwriting Cap Guardrail</div>
      </div>
    </div>

    <div style="display:flex;align-items:center;gap:12px;">
      <span class="apple-pill">✓ Max Verified Cap: $475,000</span>
      <div style="background:#F5F5F7;border:1px solid #D2D2D7;padding:6px 12px;border-radius:10px;font-size:12px;display:flex;align-items:center;gap:6px;">
        <span style="color:#6E6E73;font-weight:600;">Model:</span>
        <select id="app-model-select" onchange="window.syncSelectedModel(this.value)" style="background:transparent;color:#0071E3;font-weight:700;border:none;outline:none;font-family:inherit;font-size:12px;cursor:pointer;">
          <option value="gemini-4-argon">gemini-4-argon</option>
          <option value="gemini-3.8-flash">gemini-3.8-flash</option>
        </select>
      </div>
    </div>
  </header>

  <main class="wallet-grid">

    <!-- LEFT COLUMN: SATURDAY OPEN-HOUSE OFFER BID ADJUSTER -->
    <aside class="adjuster-card">
      <div>
        <div style="font-size:12px;font-weight:700;color:#0071E3;text-transform:uppercase;letter-spacing:0.04em;">
          Saturday Open-House Bid Adjuster
        </div>
        <h2 style="font-size:20px;font-weight:800;margin-top:4px;">Tailor Exact Offer Price</h2>
        <p style="font-size:13px;color:#6E6E73;margin-top:4px;line-height:1.45;">
          Generate an exact-dollar Pre-Approval Letter so the listing agent sees your offer strength without exposing your $475,000 maximum approval ceiling.
        </p>
      </div>

      <!-- Offer Price Stepper ($420k - $525k) -->
      <div>
        <div style="display:flex;justify-content:space-between;font-size:12.5px;font-weight:700;margin-bottom:6px;">
          <span>Offer Bid Price ($420k – $525k):</span>
          <span class="mono" style="color:#0071E3;" id="lbl-offer-step">$455,000</span>
        </div>
        <div class="stepper-row">
          <button class="step-btn" onclick="stepOfferPrice(-5000)" title="Decrease $5,000">−</button>
          <div style="text-align:center;flex:1;padding:0 12px;">
            <input type="range" id="sl-offer" min="420000" max="525000" step="5000" value="455000" style="width:100%;accent-color:#0071E3;" oninput="recalcCertificate()">
          </div>
          <button class="step-btn" onclick="stepOfferPrice(5000)" title="Increase $5,000">+</button>
        </div>
      </div>

      <!-- Property Tax Slider -->
      <div>
        <div style="display:flex;justify-content:space-between;font-size:12.5px;font-weight:600;margin-bottom:5px;">
          <span style="color:#6E6E73;">Annual Property Taxes:</span>
          <strong class="mono" id="lbl-tax">$5,400 / yr ($450/mo)</strong>
        </div>
        <input type="range" id="sl-tax" min="3600" max="9600" step="300" value="5400" style="width:100%;accent-color:#0071E3;" oninput="recalcCertificate()">
      </div>

      <!-- Monthly HOA Slider -->
      <div>
        <div style="display:flex;justify-content:space-between;font-size:12.5px;font-weight:600;margin-bottom:5px;">
          <span style="color:#6E6E73;">Monthly HOA Dues:</span>
          <strong class="mono" id="lbl-hoa">$85 / mo</strong>
        </div>
        <input type="range" id="sl-hoa" min="0" max="450" step="15" value="85" style="width:100%;accent-color:#0071E3;" oninput="recalcCertificate()">
      </div>

      <!-- Instant Max Approval Cap Guardrail Indicator -->
      <div id="guardrail-banner" class="guardrail-box guardrail-pass">
        <strong>✓ Instant Guardrail Passed ($20,000 Headroom):</strong> Your $455,000 offer is within your $475,000 Verified Approval Cap and maintains a 36.8% Back-End DTI.
      </div>

      <button class="blue-cta-btn" id="refresh-cert-btn" onclick="window.runLiveVertexAI()">
        ✨ Refresh Official Pre-Approval Letter
      </button>

      <button class="voice-read-btn" onclick="playSummaryAudio(this)">
        🔊 Read Pre-Approval Summary Aloud (Gemini 3.8 Live)
      </button>
    </aside>

    <!-- RIGHT COLUMN: PRINTABLE OFFICIAL ROCKET MORTGAGE VERIFIED PRE-APPROVAL CERTIFICATE -->
    <section class="certificate-shell">
      <div style="display:flex;justify-content:space-between;align-items:flex-start;border-bottom:2px solid #1D1D1F;padding-bottom:18px;flex-wrap:wrap;gap:12px;">
        <div>
          <div style="font-size:12px;font-weight:800;letter-spacing:0.08em;color:#D92228;text-transform:uppercase;">
            ROCKET MORTGAGE, LLC · NMLS #3030
          </div>
          <h1 class="serif" style="font-size:24px;font-weight:700;color:#1D1D1F;margin-top:4px;">
            Official Verified Pre-Approval Certificate
          </h1>
          <div style="font-size:12.5px;color:#6E6E73;margin-top:2px;">
            1050 Woodward Ave, Detroit, MI 48226 · Desktop Underwriter® (DU®) Approve/Eligible
          </div>
        </div>
        <div style="text-align:right;">
          <span class="cert-seal" id="cert-seal-badge">✓ VERIFIED APPROVAL ACTIVE</span>
          <div class="mono" style="font-size:11px;color:#6E6E73;margin-top:6px;">
            Cert ID: <strong id="cert-id-label">RKT-VPA-2026-8841</strong>
          </div>
        </div>
      </div>

      <!-- Structured Certificate Metrics -->
      <div class="cert-grid">
        <div>
          <div style="font-size:11px;color:#6E6E73;text-transform:uppercase;font-weight:700;">Borrowers</div>
          <div style="font-size:15px;font-weight:700;color:#1D1D1F;margin-top:2px;">Marcus & Elena Vance</div>
        </div>
        <div>
          <div style="font-size:11px;color:#6E6E73;text-transform:uppercase;font-weight:700;">Certified Offer Purchase Price</div>
          <div class="mono" id="cert-offer-price" style="font-size:18px;font-weight:800;color:#0071E3;margin-top:2px;">$455,000.00</div>
        </div>
        <div>
          <div style="font-size:11px;color:#6E6E73;text-transform:uppercase;font-weight:700;">Loan Program & Down Payment</div>
          <div style="font-size:14px;font-weight:700;color:#1D1D1F;margin-top:2px;" id="cert-loan-structure">30-Year Fixed Conventional (10% Down · $409,500 Loan)</div>
        </div>
        <div>
          <div style="font-size:11px;color:#6E6E73;text-transform:uppercase;font-weight:700;">Estimated Total Monthly PITI + HOA</div>
          <div class="mono" id="cert-piti" style="font-size:15px;font-weight:700;color:#059669;margin-top:2px;">$3,148 / mo (36.8% DTI · Passed)</div>
        </div>
      </div>

      <!-- Formal Serif Letter Body -->
      <div class="serif" id="cert-letter-body" style="font-size:14.5px;line-height:1.8;color:#1D1D1F;">
        To Whom It May Concern (Listing Agent & Seller):<br><br>
        This letter certifies that <strong>Marcus & Elena Vance</strong> have completed Rocket Mortgage's <strong>Verified Approval</strong> underwriting review. Rocket Mortgage has verified their credit profile (middle FICO 748), W-2 employment income, and liquid down payment assets via direct institution verification.<br><br>
        Based on a purchase offer price of <strong>$455,000</strong> with <strong>10% down ($45,500)</strong>, annual property taxes of <strong>$5,400</strong>, and HOA dues of <strong>$85/month</strong>, this transaction satisfies all Fannie Mae Conforming and Rocket Mortgage debt-to-income and reserve guardrails, subject only to an acceptable property appraisal and clear title commitment.
      </div>

      <!-- Signature & Print Actions -->
      <div style="margin-top:26px;padding-top:18px;border-top:1px solid #E5E5EA;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:14px;">
        <div>
          <div class="serif" style="font-style:italic;font-size:16px;font-weight:700;color:#1D1D1F;">Jordan Sterling, Sr. Mortgage Banker</div>
          <div style="font-size:12px;color:#6E6E73;">Rocket Mortgage, LLC · NMLS #1049281 · Equal Housing Lender</div>
        </div>
        <div style="display:flex;gap:10px;align-items:center;">
          <span class="mono" id="cert-model-badge" style="font-size:11px;background:#E8F2FF;color:#0071E3;padding:5px 10px;border-radius:6px;font-weight:700;">gemini-4-argon</span>
          <button onclick="window.print()" style="background:#1D1D1F;color:#FFFFFF;border:none;padding:9px 16px;border-radius:10px;font-family:inherit;font-size:12.5px;font-weight:700;cursor:pointer;">
            🖨️ Print / Save PDF Certificate
          </button>
        </div>
      </div>
    </section>

  </main>

  {controls}

  <script>
    const MAX_APPROVAL_CAP = 475000;

    function calcMonthlyPI(principal, annualRate) {{
      const r = (annualRate / 100) / 12;
      return principal * (r * Math.pow(1 + r, 360)) / (Math.pow(1 + r, 360) - 1);
    }}

    function stepOfferPrice(delta) {{
      const sl = document.getElementById('sl-offer');
      let nextVal = parseInt(sl.value, 10) + delta;
      nextVal = Math.max(420000, Math.min(525000, nextVal));
      sl.value = nextVal;
      recalcCertificate();
    }}

    function recalcCertificate() {{
      const offer = parseFloat(document.getElementById('sl-offer').value);
      const taxYr = parseFloat(document.getElementById('sl-tax').value);
      const hoaMo = parseFloat(document.getElementById('sl-hoa').value);

      const loanAmt = Math.round(offer * 0.90);
      const downAmt = Math.round(offer * 0.10);
      const pi = Math.round(calcMonthlyPI(loanAmt, 6.125));
      const taxMo = Math.round(taxYr / 12);
      const insMo = 125;
      const pmiMo = 92;
      const totalPiti = pi + taxMo + insMo + pmiMo + hoaMo;
      const dti = ((totalPiti + 785) / 10650 * 100).toFixed(1);

      document.getElementById('lbl-offer-step').innerText = '$' + offer.toLocaleString();
      document.getElementById('lbl-tax').innerText = '$' + taxYr.toLocaleString() + ' / yr ($' + taxMo + '/mo)';
      document.getElementById('lbl-hoa').innerText = '$' + hoaMo + ' / mo';

      document.getElementById('cert-offer-price').innerText = '$' + offer.toLocaleString() + '.00';
      document.getElementById('cert-loan-structure').innerText =
        `30-Year Fixed Conventional (10% Down · $${{loanAmt.toLocaleString()}} Loan)`;
      document.getElementById('cert-piti').innerText =
        `$${{totalPiti.toLocaleString()}} / mo (${{dti}}% DTI)`;

      const guardEl = document.getElementById('guardrail-banner');
      const sealEl = document.getElementById('cert-seal-badge');

      if (offer <= MAX_APPROVAL_CAP) {{
        const headroom = MAX_APPROVAL_CAP - offer;
        guardEl.className = 'guardrail-box guardrail-pass';
        guardEl.innerHTML =
          `<strong>✓ Instant Guardrail Passed ($${{headroom.toLocaleString()}} Headroom):</strong> Your $${{offer.toLocaleString()}} offer is within your $${{MAX_APPROVAL_CAP.toLocaleString()}} Verified Approval Cap and maintains a ${{dti}}% Back-End DTI.`;
        sealEl.style.background = '#ECFDF5';
        sealEl.style.color = '#047857';
        sealEl.innerText = '✓ VERIFIED APPROVAL ACTIVE';
      }} else {{
        const overAmt = offer - MAX_APPROVAL_CAP;
        guardEl.className = 'guardrail-box guardrail-fail';
        guardEl.innerHTML =
          `<strong>⚠️ Underwriting Guardrail Alert (+$${{overAmt.toLocaleString()}} Over Cap):</strong> Offer of $${{offer.toLocaleString()}} exceeds your $475,000 Verified Approval Ceiling. Increase down payment by $${{overAmt.toLocaleString()}} or request Banker Exception.`;
        sealEl.style.background = '#FEF2F2';
        sealEl.style.color = '#991B1B';
        sealEl.innerText = '⚠️ REQUIRES BANKER EXCEPTION (> $475K)';
      }}

      document.getElementById('cert-letter-body').innerHTML =
        `To Whom It May Concern (Listing Agent & Seller):<br><br>` +
        `This letter certifies that <strong>Marcus & Elena Vance</strong> have completed Rocket Mortgage's <strong>Verified Approval</strong> underwriting review. Rocket Mortgage has verified their credit profile (middle FICO 748), W-2 employment income, and liquid down payment assets via direct institution verification.<br><br>` +
        `Based on a purchase offer price of <strong>$${{offer.toLocaleString()}}</strong> with <strong>10% down ($${{downAmt.toLocaleString()}})</strong>, annual property taxes of <strong>$${{taxYr.toLocaleString()}}</strong>, and HOA dues of <strong>$${{hoaMo}}/month</strong>, estimated monthly housing payment is <strong>$${{totalPiti.toLocaleString()}}/mo (${{dti}}% DTI)</strong>.`;
    }}

    function playSummaryAudio(btnEl) {{
      const offer = parseFloat(document.getElementById('sl-offer').value);
      const statusText = offer <= MAX_APPROVAL_CAP
        ? `Your refreshed Verified Pre-Approval Certificate for four hundred fifty-five thousand dollars is ready to attach to your Saturday open-house offer. It keeps twenty thousand dollars of confidential headroom below your four hundred seventy-five thousand dollar maximum cap.`
        : `Heads up: your selected offer price of $${{offer.toLocaleString()}} is above your four hundred seventy-five thousand dollar verified cap. You can either bridge the difference from your Rocket Money Vault or tap to alert your Senior Banker.`;
      window.playLiveCallClip(
        statusText,
        'Aoede',
        'Rocket Mortgage Pre-Approval Assistant',
        btnEl
      );
    }}

    window.runLiveVertexAI = async function() {{
      const btn = document.getElementById('refresh-cert-btn');
      const model = window.getSelectedModel();
      btn.innerText = '⏳ Refreshing Certificate (' + model + ')...';
      document.getElementById('cert-model-badge').innerText = model;

      const offer = parseFloat(document.getElementById('sl-offer').value);
      const taxYr = parseFloat(document.getElementById('sl-tax').value);
      const hoaMo = parseFloat(document.getElementById('sl-hoa').value);

      try {{
        const res = await fetch('/api/run-demo', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{
            code: '1.4',
            model: model,
            params: {{
              price: offer,
              max_cap: MAX_APPROVAL_CAP,
              annual_tax: taxYr,
              monthly_hoa: hoaMo
            }}
          }})
        }});
        const data = await res.json();
        document.getElementById('cert-model-badge').innerText = data.model_used || model;
        if (data.structured_data && (data.structured_data.capital_allocation_advice || data.structured_data.executive_summary)) {{
          document.getElementById('cert-letter-body').innerHTML =
            data.structured_data.capital_allocation_advice || data.structured_data.executive_summary;
        }} else if (data.output) {{
          document.getElementById('cert-letter-body').innerHTML = data.output.replace(/\\n/g, '<br>');
        }}
      }} catch (e) {{
        console.error(e);
      }} finally {{
        btn.innerText = '✨ Refresh Official Pre-Approval Letter';
      }}
    }};
  </script>
</body>
</html>"""
