# -*- coding: utf-8 -*-
"""Square 1.5: Competitive Rate-Match Co-Pilot — Standalone UI Design File.
Visual Archetype: NerdWallet / Bankrate Editorial Rate Comparison Site
(#FAF9F5 warm editorial ivory background, #008060 emerald trust green, #111827 crisp ink,
Fraunces serif headings + Plus Jakarta Sans comparison table)."""

from shared.standalone_uis.base_helpers import render_floating_control_bar_and_drawer


def render_sq_1_5(auth_token: str) -> str:
    controls = render_floating_control_bar_and_drawer("1.5", auth_token)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Rocket Mortgage · Competitive Rate-Match & Loan Estimate Comparison Co-Pilot</title>
  <link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,600;9..144,700;9..144,800&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=IBM+Plex+Mono:wght@500;600&display=swap" rel="stylesheet">
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
      background: #FAF9F5;
      color: #111827;
      min-height: 100vh;
      padding-bottom: 88px;
    }}
    .editorial-serif {{ font-family: 'Fraunces', Georgia, serif; }}
    .mono {{ font-family: 'IBM Plex Mono', monospace; }}

    /* NerdWallet / Bankrate Editorial Top Navigation */
    .nw-header {{
      background: #FFFFFF;
      border-bottom: 1px solid #E5E4DF;
      padding: 16px 32px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      position: sticky;
      top: 0;
      z-index: 100;
    }}
    .nw-trust-pill {{
      background: #E6F4F0;
      color: #008060;
      border: 1px solid #A7F3D0;
      font-size: 12px;
      font-weight: 700;
      padding: 5px 12px;
      border-radius: 999px;
    }}

    /* Editorial Container */
    .editorial-container {{
      max-width: 1320px;
      margin: 28px auto;
      padding: 0 32px;
    }}

    .hero-banner {{
      background: #FFFFFF;
      border: 1px solid #E5E4DF;
      border-radius: 16px;
      padding: 28px 32px;
      margin-bottom: 24px;
      display: flex;
      flex-wrap: wrap;
      justify-content: space-between;
      align-items: center;
      gap: 20px;
      box-shadow: 0 4px 16px rgba(17, 24, 39, 0.04);
    }}

    /* 3-Column Comparison Table Card */
    .comparison-shell {{
      background: #FFFFFF;
      border: 1px solid #E5E4DF;
      border-radius: 16px;
      overflow: hidden;
      box-shadow: 0 6px 24px rgba(17, 24, 39, 0.05);
      margin-bottom: 24px;
    }}
    .comp-table {{
      width: 100%;
      border-collapse: collapse;
      text-align: left;
    }}
    .comp-table th {{
      padding: 20px 22px;
      border-bottom: 2px solid #E5E4DF;
      vertical-align: top;
      font-size: 14px;
    }}
    .comp-table td {{
      padding: 15px 22px;
      border-bottom: 1px solid #F0EFEA;
      font-size: 14px;
    }}
    .col-trap {{
      background: #FFFBFB;
    }}
    .col-winner {{
      background: #F2FBF8;
      border-left: 2px solid #008060;
      border-right: 2px solid #008060;
    }}

    /* Buttons */
    .emerald-btn {{
      background: #008060;
      color: #FFFFFF;
      border: none;
      border-radius: 10px;
      padding: 12px 20px;
      font-family: inherit;
      font-size: 13.5px;
      font-weight: 700;
      cursor: pointer;
      transition: 0.15s;
      display: inline-flex;
      align-items: center;
      gap: 8px;
    }}
    .emerald-btn:hover {{ background: #00664C; }}

    .voice-track-btn {{
      background: #E6F4F0;
      color: #008060;
      border: 1px solid #86EFAC;
      border-radius: 10px;
      padding: 11px 18px;
      font-family: inherit;
      font-size: 13px;
      font-weight: 700;
      cursor: pointer;
      transition: 0.15s;
      display: inline-flex;
      align-items: center;
      gap: 8px;
    }}
    .voice-track-btn:hover {{ background: #D1FAE5; }}

    /* Bottom 2-Column Breakeven Horizon & Talk Track */
    .bottom-grid {{
      display: grid;
      grid-template-columns: 1.15fr 1fr;
      gap: 24px;
    }}
    @media (max-width: 1040px) {{
      .bottom-grid {{ grid-template-columns: 1fr; }}
    }}
    .ed-card {{
      background: #FFFFFF;
      border: 1px solid #E5E4DF;
      border-radius: 16px;
      padding: 24px;
      box-shadow: 0 4px 16px rgba(17, 24, 39, 0.04);
    }}
  </style>
</head>
<body>

  <!-- NERDWALLET / BANKRATE EDITORIAL HEADER -->
  <header class="nw-header">
    <div style="display:flex;align-items:center;gap:14px;">
      <div style="width:36px;height:36px;border-radius:8px;background:#008060;color:#FFFFFF;display:flex;align-items:center;justify-content:center;font-weight:800;font-size:18px;">✓</div>
      <div>
        <div class="editorial-serif" style="font-size:18px;font-weight:700;color:#111827;">Rocket Rate-Match Editorial Truth Engine</div>
        <div style="font-size:12px;color:#4B5563;">TRID Page-2 Fee Audit · Discount Point Breakeven Calculator · $450,000 Loan Estimate Comparison</div>
      </div>
    </div>

    <div style="display:flex;align-items:center;gap:12px;flex-wrap:wrap;">
      <span class="nw-trust-pill">★ Verified CFPB Loan Estimate Audit</span>
      <div style="background:#FAF9F5;border:1px solid #D1D5DB;padding:6px 12px;border-radius:8px;font-size:12px;display:flex;align-items:center;gap:6px;">
        <span style="color:#4B5563;font-weight:600;">Model:</span>
        <select id="app-model-select" onchange="window.syncSelectedModel(this.value)" style="background:transparent;color:#008060;font-weight:700;border:none;outline:none;font-family:inherit;font-size:12px;cursor:pointer;">
          <option value="gemini-4-argon">gemini-4-argon</option>
          <option value="gemini-3.8-flash">gemini-3.8-flash</option>
        </select>
      </div>
    </div>
  </header>

  <main class="editorial-container">

    <!-- EDITORIAL HERO BANNER -->
    <section class="hero-banner">
      <div style="max-width:740px;">
        <div style="font-size:12px;font-weight:800;color:#008060;text-transform:uppercase;letter-spacing:0.05em;">
          Consumer Rate-Match Transparency Audit
        </div>
        <h1 class="editorial-serif" style="font-size:28px;font-weight:700;color:#111827;margin-top:6px;line-height:1.25;">
          Why That Competitor "5.99% Teaser Rate" Actually Costs $9,550 Upfront in Hidden Section A Points
        </h1>
        <p style="font-size:14px;color:#4B5563;margin-top:8px;line-height:1.55;">
          Our side-by-side Loan Estimate audit exposes upfront discount points disguised behind low advertised rates—and calculates your exact net cumulative cost over your planned ownership horizon.
        </p>
      </div>

      <div style="display:flex;flex-direction:column;gap:10px;">
        <button class="voice-track-btn" onclick="playRateMatchTalkTrack(this)">
          🔊 Play Rate-Match Talk Track (Gemini 3.8 Live · Kore HD)
        </button>
        <button class="emerald-btn" id="audit-btn" onclick="window.runLiveVertexAI()">
          ✨ Run AI Rate-Match Strategy Audit
        </button>
      </div>
    </section>

    <!-- SIDE-BY-SIDE 3-OPTION LOAN ESTIMATE COMPARISON TABLE -->
    <section class="comparison-shell">
      <table class="comp-table">
        <thead>
          <tr>
            <th style="width:24%;background:#FAF9F5;">
              <div style="font-size:11px;color:#6B7280;text-transform:uppercase;font-weight:700;">Loan Estimate Line Item</div>
              <div class="editorial-serif" style="font-size:18px;margin-top:4px;color:#111827;">$450,000 Loan Amount</div>
            </th>
            <th class="col-trap" style="width:25%;">
              <span style="background:#FEE2E2;color:#991B1B;font-size:11px;font-weight:800;padding:3px 9px;border-radius:999px;">⚠️ HIGH-POINT TRAP</span>
              <div class="editorial-serif" style="font-size:18px;margin-top:8px;color:#991B1B;">Competitor 5.99% Teaser</div>
              <div style="font-size:12px;color:#6B7280;font-weight:500;margin-top:2px;">Online Lead-Gen Lender Quote</div>
            </th>
            <th class="col-winner" style="width:26%;">
              <span style="background:#008060;color:#FFFFFF;font-size:11px;font-weight:800;padding:3px 10px;border-radius:999px;">★ BEST 5-YEAR NET VALUE</span>
              <div class="editorial-serif" style="font-size:18px;margin-top:8px;color:#008060;">Rocket 6.125% Zero-Point</div>
              <div style="font-size:12px;color:#065F46;font-weight:600;margin-top:2px;">Keep $8,555 Cash in Your Pocket</div>
            </th>
            <th style="width:25%;background:#FFFFFF;">
              <span style="background:#E0F2FE;color:#0369A1;font-size:11px;font-weight:800;padding:3px 9px;border-radius:999px;">✓ RATE-MATCHED OPTION</span>
              <div class="editorial-serif" style="font-size:18px;margin-top:8px;color:#111827;">Rocket 5.99% Matched</div>
              <div style="font-size:12px;color:#4B5563;font-weight:500;margin-top:2px;">Matches 5.99% w/ $5,805 Fewer Fees</div>
            </th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><strong>Note Interest Rate / APR</strong></td>
            <td class="col-trap mono"><strong>5.990%</strong> (6.248% APR)</td>
            <td class="col-winner mono" style="color:#008060;"><strong>6.125%</strong> (6.168% APR)</td>
            <td class="mono"><strong>5.990%</strong> (6.094% APR)</td>
          </tr>
          <tr>
            <td><strong>Monthly Principal & Interest</strong></td>
            <td class="col-trap mono">$2,695 / mo</td>
            <td class="col-winner mono"><strong>$2,734 / mo</strong> (+$39/mo)</td>
            <td class="mono"><strong>$2,695 / mo</strong> (Exact Match)</td>
          </tr>
          <tr>
            <td><strong>LE Section A: Discount Points</strong></td>
            <td class="col-trap mono" style="color:#B91C1C;font-weight:700;">$7,875 (1.750 Points)</td>
            <td class="col-winner mono" style="color:#008060;font-weight:800;">$0 (0.000 Points)</td>
            <td class="mono" style="font-weight:700;">$2,812 (0.625 Points)</td>
          </tr>
          <tr>
            <td><strong>LE Section A: Underwriting / Origination</strong></td>
            <td class="col-trap mono" style="color:#B91C1C;">$1,675 Junk Admin Fees</td>
            <td class="col-winner mono" style="color:#008060;font-weight:700;">$995 Flat Processing</td>
            <td class="mono">$933 Rate-Match Credit</td>
          </tr>
          <tr>
            <td><strong>Total Section A Lender Charges</strong></td>
            <td class="col-trap mono" style="font-size:15px;font-weight:800;color:#B91C1C;">$9,550 Upfront</td>
            <td class="col-winner mono" style="font-size:15px;font-weight:800;color:#008060;">$995 Upfront (-$8,555!)</td>
            <td class="mono" style="font-size:15px;font-weight:800;color:#0369A1;">$3,745 Upfront (-$5,805!)</td>
          </tr>
          <tr>
            <td><strong>Net Cumulative Cost @ <span id="tbl-horizon-lbl">36</span> Months</strong></td>
            <td class="col-trap mono" id="tbl-cost-comp" style="font-weight:700;color:#B91C1C;">$106,570</td>
            <td class="col-winner mono" id="tbl-cost-zero" style="font-weight:800;color:#008060;">$99,419 (Saves $7,151!)</td>
            <td class="mono" id="tbl-cost-match" style="font-weight:700;">$100,765 (Saves $5,805!)</td>
          </tr>
        </tbody>
      </table>
    </section>

    <!-- BOTTOM GRID: INTERACTIVE BREAKEVEN CHART & TALK TRACK -->
    <section class="bottom-grid">

      <!-- Left: Interactive Breakeven Month Horizon Slider & SVG Chart -->
      <div class="ed-card">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;">
          <div>
            <h2 class="editorial-serif" style="font-size:20px;font-weight:700;">Interactive Breakeven Horizon Calculator</h2>
            <div style="font-size:12.5px;color:#4B5563;">It takes <strong>219 months (18.2 years)</strong> for the Competitor's $8,555 extra upfront points to break even against Rocket's $39/mo difference!</div>
          </div>
        </div>

        <div style="background:#FAF9F5;padding:14px 16px;border-radius:12px;border:1px solid #E5E4DF;margin-bottom:16px;">
          <div style="display:flex;justify-content:space-between;font-size:13px;font-weight:700;margin-bottom:6px;">
            <span>Planned Ownership / Refinance Horizon:</span>
            <span class="mono" id="lbl-horizon" style="color:#008060;">36 Months (3.0 Years)</span>
          </div>
          <input type="range" id="sl-horizon" min="12" max="84" step="6" value="36" style="width:100%;accent-color:#008060;" oninput="recalcBreakeven()">
          <div style="display:flex;justify-content:space-between;font-size:11px;color:#6B7280;margin-top:4px;">
            <span>12 Mos (1 Yr)</span>
            <span>36 Mos (Avg Refi Window)</span>
            <span>60 Mos (5 Yrs)</span>
            <span>84 Mos (7 Yrs)</span>
          </div>
        </div>

        <!-- Live SVG Breakeven Chart -->
        <svg viewBox="0 0 580 185" style="width:100%;height:185px;background:#FAF9F5;border:1px solid #E5E4DF;border-radius:12px;">
          <line x1="45" y1="35" x2="545" y2="35" stroke="#E5E7EB" stroke-dasharray="4 4"/>
          <line x1="45" y1="90" x2="545" y2="90" stroke="#E5E7EB" stroke-dasharray="4 4"/>
          <line x1="45" y1="145" x2="545" y2="145" stroke="#9CA3AF"/>
          <!-- Competitor High Upfront Cost Line (Red) -->
          <path d="M 45 52 L 545 42" fill="none" stroke="#DC2626" stroke-width="3" stroke-dasharray="6 4"/>
          <text x="55" y="46" fill="#DC2626" font-family="Plus Jakarta Sans" font-size="11" font-weight="700">Competitor 5.99% ($9,550 Upfront Points)</text>
          <!-- Rocket Zero-Point Advantage Line (Emerald) -->
          <path d="M 45 128 L 545 78" fill="none" stroke="#008060" stroke-width="3.5"/>
          <text x="55" y="138" fill="#008060" font-family="Plus Jakarta Sans" font-size="11" font-weight="700">Rocket 6.125% Zero-Point ($8,555 Less Cash at Closing)</text>
          <!-- Dynamic Horizon Marker -->
          <line id="svg-horizon-line" x1="210" y1="22" x2="210" y2="145" stroke="#111827" stroke-width="2"/>
          <circle id="svg-horizon-dot" cx="210" cy="110" r="6" fill="#008060"/>
          <text id="svg-horizon-label" x="218" y="96" fill="#111827" font-family="IBM Plex Mono" font-size="11" font-weight="700">Month 36: You Save $7,151 Net</text>
        </svg>
      </div>

      <!-- Right: Editorial Talk Track & AI Verdict -->
      <div class="ed-card" style="display:flex;flex-direction:column;justify-content:space-between;gap:14px;">
        <div>
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
            <span style="font-size:12px;font-weight:800;color:#008060;text-transform:uppercase;">🎙️ Banker Rate-Match Talk Track</span>
            <span class="mono" id="rm-model-badge" style="font-size:11px;background:#E6F4F0;color:#008060;padding:4px 8px;border-radius:6px;font-weight:700;">gemini-4-argon</span>
          </div>
          <div id="talk-track-box" style="font-size:14px;line-height:1.7;color:#1F2937;background:#FAF9F5;padding:18px;border-radius:12px;border:1px solid #E5E4DF;">
            "I looked right at Page 2, Section A of that competing 5.99% Loan Estimate. To show you 5.99%, they are charging you <strong>$7,875 in upfront discount points plus $1,675 in lender admin fees—$9,550 total out of your pocket</strong> at closing. Compared to our Rocket 6.125% zero-point option ($995 flat fee), you're paying $8,555 upfront just to save $39 a month. It would take <strong>18.2 years (219 months)</strong> just to break even! Or, if you truly want 5.99%, I can match 5.99% right now with our Rocket Rate-Match credit for <strong>$5,805 less</strong> in closing fees."
          </div>
        </div>

        <div style="background:#E6F4F0;border:1px solid #A7F3D0;border-radius:12px;padding:14px;display:flex;justify-content:space-between;align-items:center;">
          <div>
            <div style="font-size:12px;font-weight:800;color:#065F46;">Net Borrower Advantage Over <span id="summary-mos">36</span> Months</div>
            <div style="font-size:12px;color:#047857;">Rocket Zero-Point 6.125% vs. Competitor 5.99% Point Trap</div>
          </div>
          <div class="mono" id="summary-net-win" style="font-size:22px;font-weight:800;color:#008060;">+$7,151 Saved</div>
        </div>
      </div>

    </section>

  </main>

  {controls}

  <script>
    function recalcBreakeven() {{
      const mos = parseInt(document.getElementById('sl-horizon').value, 10) || 36;
      const yrs = (mos / 12).toFixed(1);
      document.getElementById('lbl-horizon').innerText = `${{mos}} Months (${{yrs}} Years)`;
      document.getElementById('tbl-horizon-lbl').innerText = mos;
      document.getElementById('summary-mos').innerText = mos;

      const compCost = 9550 + (2695 * mos);
      const zeroCost = 995 + (2734 * mos);
      const matchCost = 3745 + (2695 * mos);
      const netSaved = compCost - zeroCost;

      document.getElementById('tbl-cost-comp').innerText = '$' + compCost.toLocaleString();
      document.getElementById('tbl-cost-zero').innerText = `$${{zeroCost.toLocaleString()}} (Saves $${{netSaved.toLocaleString()}}!)`;
      document.getElementById('tbl-cost-match').innerText = `$${{matchCost.toLocaleString()}} (Saves $5,805!)`;
      document.getElementById('summary-net-win').innerText = '+$' + netSaved.toLocaleString() + ' Saved';

      // Move SVG Horizon Marker (12..84 -> x: 75..510)
      const xPos = Math.round(75 + ((mos - 12) / 72) * 435);
      const yPos = Math.round(128 - ((mos - 12) / 72) * 50);
      document.getElementById('svg-horizon-line').setAttribute('x1', xPos);
      document.getElementById('svg-horizon-line').setAttribute('x2', xPos);
      document.getElementById('svg-horizon-dot').setAttribute('cx', xPos);
      document.getElementById('svg-horizon-dot').setAttribute('cy', yPos);
      const textX = xPos > 340 ? xPos - 215 : xPos + 8;
      const lbl = document.getElementById('svg-horizon-label');
      lbl.setAttribute('x', textX);
      lbl.textContent = `Month ${{mos}}: You Save $${{netSaved.toLocaleString()}} Net`;
    }}

    function playRateMatchTalkTrack(btnEl) {{
      const txt = document.getElementById('talk-track-box').innerText.replace(/"/g, '');
      window.playLiveCallClip(
        txt,
        'Kore',
        'Rocket Mortgage Rate-Match Specialist',
        btnEl
      );
    }}

    window.runLiveVertexAI = async function() {{
      const btn = document.getElementById('audit-btn');
      const model = window.getSelectedModel();
      btn.innerText = '⏳ Auditing Loan Estimate (' + model + ')...';
      document.getElementById('rm-model-badge').innerText = model;

      const mos = parseInt(document.getElementById('sl-horizon').value, 10) || 36;

      try {{
        const res = await fetch('/api/run-demo', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{
            code: '1.5',
            model: model,
            params: {{
              loan_amount: 450000,
              competitor_rate: 5.99,
              competitor_section_a_fees: 9550,
              rocket_par_rate: 6.125,
              rocket_section_a_fees: 995,
              horizon_months: mos
            }}
          }})
        }});
        const data = await res.json();
        document.getElementById('rm-model-badge').innerText = data.model_used || model;
        if (data.structured_data && (data.structured_data.executive_summary || data.structured_data.instant_borrower_sms)) {{
          document.getElementById('talk-track-box').innerHTML =
            data.structured_data.executive_summary || data.structured_data.instant_borrower_sms;
        }} else if (data.output) {{
          document.getElementById('talk-track-box').innerHTML = data.output.replace(/\\n/g, '<br>');
        }}
      }} catch (e) {{
        console.error(e);
      }} finally {{
        btn.innerText = '✨ Run AI Rate-Match Strategy Audit';
      }}
    }};
  </script>
</body>
</html>"""
