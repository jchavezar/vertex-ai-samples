# -*- coding: utf-8 -*-
"""Square 1.3: Cross-Brand Purchase Concierge — Standalone UI Design File.
Visual Archetype: Authentic Redfin / Airbnb Consumer Home-Buying Marketplace
(#FFFFFF pure white canvas, #D92228 Redfin Red primary CTA, #F7F7F7 warm filter bar,
Plus Jakarta Sans font, rounded 16px property cards).
Consumer Home-Shopping Portal for Royal Oak & Ferndale, MI."""

from shared.standalone_uis.base_helpers import render_floating_control_bar_and_drawer


def render_sq_1_3(auth_token: str) -> str:
    controls = render_floating_control_bar_and_drawer("1.3", auth_token)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Redfin × Rocket Mortgage × Rocket Money · Cross-Brand Purchase Concierge</title>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=IBM+Plex+Mono:wght@500;600&display=swap" rel="stylesheet">
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
      background: #FFFFFF;
      color: #222222;
      min-height: 100vh;
      padding-bottom: 88px;
    }}
    .mono {{ font-family: 'IBM Plex Mono', monospace; }}

    /* Redfin / Airbnb Marketplace Navigation Header */
    .rf-navbar {{
      background: #FFFFFF;
      border-bottom: 1px solid #EBEBEB;
      padding: 14px 32px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      position: sticky;
      top: 0;
      z-index: 100;
    }}
    .rf-logo-cluster {{
      display: flex;
      align-items: center;
      gap: 12px;
    }}
    .rf-badge {{
      background: #D92228;
      color: #FFFFFF;
      font-weight: 800;
      font-size: 14px;
      padding: 6px 12px;
      border-radius: 8px;
      letter-spacing: -0.02em;
    }}
    .bundle-pill {{
      background: #FFF1F2;
      color: #BE123C;
      border: 1px solid #FECDD3;
      font-size: 12px;
      font-weight: 700;
      padding: 5px 12px;
      border-radius: 999px;
    }}

    /* Marketplace Warm Filter Bar */
    .rf-filter-bar {{
      background: #F7F7F7;
      border-bottom: 1px solid #EBEBEB;
      padding: 16px 32px;
    }}
    .filter-inner {{
      max-width: 1320px;
      margin: 0 auto;
      display: grid;
      grid-template-columns: 1.4fr 1fr 1fr auto;
      gap: 18px;
      align-items: center;
    }}
    @media (max-width: 1080px) {{
      .filter-inner {{ grid-template-columns: 1fr; }}
    }}
    .filter-box {{
      background: #FFFFFF;
      border: 1px solid #DDDDDD;
      border-radius: 12px;
      padding: 10px 14px;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
    }}
    .filter-label {{
      font-size: 11px;
      font-weight: 700;
      color: #717171;
      text-transform: uppercase;
      letter-spacing: 0.03em;
      margin-bottom: 4px;
      display: flex;
      justify-content: space-between;
    }}

    /* Main Marketplace Grid */
    .market-container {{
      max-width: 1320px;
      margin: 28px auto;
      padding: 0 32px;
      display: grid;
      grid-template-columns: 1.25fr 1fr;
      gap: 28px;
      align-items: start;
    }}
    @media (max-width: 1080px) {{
      .market-container {{ grid-template-columns: 1fr; }}
    }}

    /* Rounded 16px Property Showcase Card */
    .property-card {{
      background: #FFFFFF;
      border: 1px solid #E5E7EB;
      border-radius: 16px;
      overflow: hidden;
      box-shadow: 0 8px 28px rgba(0, 0, 0, 0.06);
    }}
    .property-art {{
      position: relative;
      height: 255px;
      background: linear-gradient(180deg, #E0F2FE 0%, #F0FDF4 100%);
      display: flex;
      align-items: center;
      justify-content: center;
      border-bottom: 1px solid #EBEBEB;
    }}
    .listing-tag {{
      position: absolute;
      top: 16px;
      left: 16px;
      background: #FFFFFF;
      color: #222222;
      font-weight: 800;
      font-size: 12px;
      padding: 6px 12px;
      border-radius: 999px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.12);
    }}
    .credit-tag {{
      position: absolute;
      top: 16px;
      right: 16px;
      background: #D92228;
      color: #FFFFFF;
      font-weight: 800;
      font-size: 12px;
      padding: 6px 14px;
      border-radius: 999px;
      box-shadow: 0 2px 8px rgba(217,34,40,0.35);
    }}

    /* Buttons */
    .rf-btn-primary {{
      background: #D92228;
      color: #FFFFFF;
      border: none;
      border-radius: 12px;
      padding: 13px 20px;
      font-family: inherit;
      font-size: 14px;
      font-weight: 700;
      cursor: pointer;
      transition: 0.15s;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
    }}
    .rf-btn-primary:hover {{ background: #B81B20; }}

    .rf-btn-audio {{
      background: #FFF1F2;
      color: #D92228;
      border: 1px solid #FECDD3;
      border-radius: 12px;
      padding: 11px 16px;
      font-family: inherit;
      font-size: 13px;
      font-weight: 700;
      cursor: pointer;
      transition: 0.15s;
      display: inline-flex;
      align-items: center;
      gap: 8px;
      width: 100%;
      justify-content: center;
    }}
    .rf-btn-audio:hover {{ background: #FFE4E6; }}

    /* Bundle Breakdown Card */
    .bundle-card {{
      background: #FFFFFF;
      border: 1px solid #E5E7EB;
      border-radius: 16px;
      padding: 24px;
      box-shadow: 0 6px 24px rgba(0, 0, 0, 0.05);
      display: flex;
      flex-direction: column;
      gap: 16px;
    }}
    .bundle-row {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 12px 14px;
      border-radius: 12px;
      background: #F7F7F7;
      font-size: 13.5px;
    }}
    .bundle-highlight {{
      background: #ECFDF5;
      border: 1px solid #A7F3D0;
      color: #065F46;
      padding: 14px 16px;
      border-radius: 12px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}
  </style>
</head>
<body>

  <!-- REDFIN / AIRBNB MARKETPLACE HEADER -->
  <header class="rf-navbar">
    <div class="rf-logo-cluster">
      <span class="rf-badge">REDFIN × ROCKET</span>
      <div>
        <div style="font-size:16px;font-weight:800;color:#222222;">Cross-Brand Purchase Concierge</div>
        <div style="font-size:12px;color:#717171;">Royal Oak & Ferndale, MI · Unified Home Search + Rocket Money Vault + Instant Closing Credits</div>
      </div>
    </div>

    <div style="display:flex;align-items:center;gap:12px;">
      <span class="bundle-pill">★ Rocket Preferred Bundle Active</span>
      <div style="background:#F7F7F7;border:1px solid #DDDDDD;padding:6px 12px;border-radius:10px;font-size:12px;display:flex;align-items:center;gap:6px;">
        <span style="color:#717171;font-weight:600;">Model:</span>
        <select id="app-model-select" onchange="window.syncSelectedModel(this.value)" style="background:transparent;color:#D92228;font-weight:700;border:none;outline:none;font-family:inherit;font-size:12px;cursor:pointer;">
          <option value="gemini-4-argon">gemini-4-argon</option>
          <option value="gemini-3.8-flash">gemini-3.8-flash</option>
        </select>
      </div>
    </div>
  </header>

  <!-- TOP MARKETPLACE SEARCH & SLIDER BAR -->
  <section class="rf-filter-bar">
    <div class="filter-inner">
      <div class="filter-box">
        <div class="filter-label">
          <span>📍 Select Oakland County Listing</span>
          <span style="color:#D92228;">MLS Active</span>
        </div>
        <select id="prop-select" onchange="onPropertyChange()" style="width:100%;border:none;outline:none;font-family:inherit;font-size:14px;font-weight:700;color:#222222;background:transparent;cursor:pointer;">
          <option value="0">418 Elmhurst Ave, Royal Oak · $460,000</option>
          <option value="1">812 Livernois St, Ferndale · $395,000</option>
          <option value="2">1204 Vinsetta Blvd, Royal Oak · $575,000</option>
        </select>
      </div>

      <div class="filter-box">
        <div class="filter-label">
          <span>Down Payment (%)</span>
          <strong class="mono" id="lbl-down-pct" style="color:#222222;">10% ($46,000)</strong>
        </div>
        <input type="range" id="sl-down" min="5" max="25" step="5" value="10" style="width:100%;accent-color:#D92228;" oninput="recalcConcierge()">
      </div>

      <div class="filter-box">
        <div class="filter-label">
          <span>Rocket Money Goal Vault</span>
          <strong class="mono" id="lbl-vault" style="color:#059669;">$58,500</strong>
        </div>
        <input type="range" id="sl-vault" min="25000" max="140000" step="2500" value="58500" style="width:100%;accent-color:#059669;" oninput="recalcConcierge()">
      </div>

      <button class="rf-btn-primary" id="concierge-btn" onclick="window.runLiveVertexAI()">
        ✨ Personalize Bundle Offer
      </button>
    </div>
  </section>

  <!-- MAIN MARKETPLACE SHOWCASE -->
  <main class="market-container">

    <!-- LEFT: PROPERTY SHOWCASE CARD WITH ARCHITECTURAL HOUSE ILLUSTRATION -->
    <div class="property-card">
      <div class="property-art">
        <span class="listing-tag" id="badge-neighborhood">🔥 Hot Home · Royal Oak Tree Section</span>
        <span class="credit-tag" id="badge-credit">+$4,600 Combined Closing Credit</span>

        <!-- Architectural Craftsman House SVG Illustration -->
        <svg width="360" height="200" viewBox="0 0 360 200" fill="none" xmlns="http://www.w3.org/2000/svg">
          <!-- Sun & Clouds -->
          <circle cx="295" cy="44" r="22" fill="#FDE68A"/>
          <!-- Lawn -->
          <rect x="20" y="168" width="320" height="16" rx="8" fill="#86EFAC"/>
          <!-- Main House Body -->
          <rect x="75" y="86" width="210" height="82" fill="#FFFFFF" stroke="#1E293B" stroke-width="3"/>
          <!-- Craftsman Roof -->
          <polygon points="58,86 180,28 302,86" fill="#D92228" stroke="#1E293B" stroke-width="3"/>
          <!-- Center Dormer -->
          <polygon points="145,62 180,38 215,62" fill="#FFFFFF" stroke="#1E293B" stroke-width="2.5"/>
          <rect x="168" y="48" width="24" height="14" fill="#BAE6FD" stroke="#1E293B" stroke-width="2"/>
          <!-- Front Porch Gables & Columns -->
          <rect x="152" y="118" width="56" height="50" fill="#F8FAFC" stroke="#1E293B" stroke-width="2.5"/>
          <rect x="168" y="126" width="24" height="42" fill="#1E293B"/>
          <circle cx="187" cy="148" r="2.2" fill="#FDE68A"/>
          <!-- Left & Right Picture Windows -->
          <rect x="95" y="104" width="42" height="34" rx="3" fill="#BAE6FD" stroke="#1E293B" stroke-width="2.5"/>
          <line x1="116" y1="104" x2="116" y2="138" stroke="#1E293B" stroke-width="2"/>
          <rect x="223" y="104" width="42" height="34" rx="3" fill="#BAE6FD" stroke="#1E293B" stroke-width="2.5"/>
          <line x1="244" y1="104" x2="244" y2="138" stroke="#1E293B" stroke-width="2"/>
          <!-- Trees -->
          <circle cx="52" cy="136" r="22" fill="#4ADE80" stroke="#1E293B" stroke-width="2.5"/>
          <line x1="52" y1="158" x2="52" y2="170" stroke="#1E293B" stroke-width="3"/>
          <circle cx="310" cy="136" r="22" fill="#4ADE80" stroke="#1E293B" stroke-width="2.5"/>
          <line x1="310" y1="158" x2="310" y2="170" stroke="#1E293B" stroke-width="3"/>
        </svg>
      </div>

      <div style="padding:24px;">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:12px;flex-wrap:wrap;">
          <div>
            <h1 id="prop-title" style="font-size:24px;font-weight:800;color:#222222;">418 Elmhurst Ave, Royal Oak, MI 48073</h1>
            <div id="prop-specs" style="font-size:14px;color:#717171;margin-top:4px;font-weight:500;">
              3 Beds · 2.5 Baths · 1,940 Sq.Ft. · Renovated Craftsman Bungalow · Walk to Downtown Royal Oak
            </div>
          </div>
          <div style="text-align:right;">
            <div class="mono" id="prop-price" style="font-size:26px;font-weight:800;color:#222222;">$460,000</div>
            <div style="font-size:12px;color:#059669;font-weight:700;">Est. <span id="prop-piti">$3,184</span>/mo PITI</div>
          </div>
        </div>

        <div style="margin-top:18px;">
          <button class="rf-btn-audio" onclick="playConciergeTourAudio(this)">
            🔊 Hear Concierge Home Tour Audio (Gemini 3.8 Live · Aoede HD)
          </button>
        </div>

        <div style="margin-top:18px;padding-top:18px;border-top:1px solid #EBEBEB;">
          <div style="font-size:12px;font-weight:700;color:#717171;text-transform:uppercase;margin-bottom:8px;">
            🏡 AI Cross-Brand Concierge Advisory (<span id="concierge-model-tag">gemini-4-argon</span>)
          </div>
          <div id="concierge-output-box" style="font-size:14px;line-height:1.65;color:#222222;background:#F7F7F7;padding:16px;border-radius:12px;border:1px solid #EBEBEB;">
            <strong>418 Elmhurst Ave ($460,000)</strong> fits squarely inside your <strong>$58,500 Rocket Money Down Payment Vault</strong>! Putting <strong>10% down ($46,000)</strong> leaves you with <strong>$12,500 in liquid reserves</strong>—plus our <strong>$4,600 Combined Redfin + Rocket Closing Credit</strong> covers nearly 65% of your Oakland County title and escrow closing costs.
          </div>
        </div>
      </div>
    </div>

    <!-- RIGHT: REDFIN + ROCKET MORTGAGE + ROCKET MONEY BUNDLE BREAKDOWN -->
    <aside class="bundle-card">
      <div>
        <div style="font-size:12px;font-weight:800;color:#D92228;text-transform:uppercase;letter-spacing:0.04em;">
          Unified Ecosystem Breakdown
        </div>
        <h2 style="font-size:20px;font-weight:800;color:#222222;margin-top:4px;">
          Redfin + Rocket Mortgage + Rocket Money Bundle
        </h2>
      </div>

      <!-- Combined Closing Credit Banner -->
      <div class="bundle-highlight">
        <div>
          <div style="font-size:12px;font-weight:700;text-transform:uppercase;">Combined Closing Credit Unlocked</div>
          <div style="font-size:12.5px;opacity:0.9;margin-top:2px;">Redfin Partner Rebate ($2,300) + Rocket Purchase Plus ($2,300)</div>
        </div>
        <div class="mono" id="val-combined-credit" style="font-size:24px;font-weight:800;">$4,600</div>
      </div>

      <div class="bundle-row">
        <span><strong>1. Home Purchase Price</strong> (Redfin MLS)</span>
        <span class="mono" id="bd-price" style="font-weight:700;">$460,000</span>
      </div>
      <div class="bundle-row">
        <span><strong>2. Down Payment</strong> (<span id="bd-down-pct">10%</span>)</span>
        <span class="mono" id="bd-down-amt" style="font-weight:700;">$46,000</span>
      </div>
      <div class="bundle-row">
        <span><strong>3. Rocket Mortgage Loan Amount</strong> (6.125% 30-Yr)</span>
        <span class="mono" id="bd-loan-amt" style="font-weight:700;">$414,000</span>
      </div>
      <div class="bundle-row">
        <span><strong>4. Est. Closing Costs after $4,600 Credit</strong></span>
        <span class="mono" id="bd-net-closing" style="font-weight:700;color:#059669;">$2,950</span>
      </div>
      <div class="bundle-row" style="background:#FFF1F2;border:1px solid #FECDD3;">
        <span><strong>Total Cash to Close vs. Rocket Money Vault</strong></span>
        <span class="mono" id="bd-cash-status" style="font-weight:800;color:#059669;">$48,950 Needed · $9,550 Cushion!</span>
      </div>

      <div style="background:#F7F7F7;border-radius:12px;padding:14px;font-size:13px;line-height:1.55;color:#484848;">
        <strong>Why Bundle Redfin + Rocket?</strong> Your Redfin Lead Agent and Rocket Loan Officer share a single live closing timeline, automatically applying your <strong>1% combined closing credit</strong> directly to your Closing Disclosure.
      </div>

      <button class="rf-btn-primary" style="width:100%;" onclick="alert('Saturday Private Redfin Tour + Verified Rocket Pre-Approval Packet scheduled for 418 Elmhurst Ave!')">
        📅 Schedule Saturday Redfin Tour + Lock $4,600 Credit
      </button>
    </aside>

  </main>

  {controls}

  <script>
    const LISTINGS = [
      {{
        address: '418 Elmhurst Ave, Royal Oak, MI 48073',
        price: 460000,
        badge: '🔥 Hot Home · Royal Oak Tree Section',
        specs: '3 Beds · 2.5 Baths · 1,940 Sq.Ft. · Renovated Craftsman Bungalow · Walk to Downtown Royal Oak',
        credit: 4600,
        tourScript: 'Welcome to four eighteen Elmhurst Avenue in Royal Oak, listed at four hundred sixty thousand dollars. Because you linked your Rocket Money Down Payment Vault with fifty-eight thousand five hundred dollars saved, you qualify for our Redfin and Rocket Mortgage Cross-Brand Purchase Bundle. That gives you an instant four thousand six hundred dollar combined closing cost credit, leaving you nearly ten thousand dollars in cash reserves after closing!'
      }},
      {{
        address: '812 Livernois St, Ferndale, MI 48220',
        price: 395000,
        badge: '✨ New Listing · West Ferndale',
        specs: '3 Beds · 2 Baths · 1,680 Sq.Ft. · Mid-Century Brick Ranch · Chef Kitchen & Fenced Yard',
        credit: 3950,
        tourScript: 'Welcome to eight twelve Livernois Street in Ferndale, listed at three hundred ninety-five thousand dollars. With ten percent down from your Rocket Money Vault and your combined Redfin plus Rocket closing credit, your total monthly payment drops well below your target budget while keeping over sixteen thousand dollars in post-closing liquidity.'
      }},
      {{
        address: '1204 Vinsetta Blvd, Royal Oak, MI 48067',
        price: 575000,
        badge: '🌳 Premier Boulevard · Vinsetta Historic',
        specs: '4 Beds · 3.5 Baths · 2,620 Sq.Ft. · Classic Tudor Revival on Tree-Lined Vinsetta Blvd',
        credit: 5750,
        tourScript: 'Welcome to twelve oh four Vinsetta Boulevard in Royal Oak, listed at five hundred seventy-five thousand dollars. By bundling Redfin and Rocket Mortgage, you unlock a five thousand seven hundred fifty dollar closing credit that offsets your Oakland County escrow setup.'
      }}
    ];

    function calcMonthlyPI(principal, annualRate) {{
      const r = (annualRate / 100) / 12;
      return principal * (r * Math.pow(1 + r, 360)) / (Math.pow(1 + r, 360) - 1);
    }}

    function onPropertyChange() {{
      recalcConcierge();
    }}

    function recalcConcierge() {{
      const idx = parseInt(document.getElementById('prop-select').value, 10) || 0;
      const item = LISTINGS[idx];
      const downPct = parseFloat(document.getElementById('sl-down').value);
      const vault = parseFloat(document.getElementById('sl-vault').value);

      const downAmt = Math.round(item.price * (downPct / 100));
      const loanAmt = item.price - downAmt;
      const credit = (idx === 0 && downPct === 10) ? 4600 : Math.round(item.price * 0.01);
      const baseClosing = 7550;
      const netClosing = Math.max(950, baseClosing - credit);
      const cashNeeded = downAmt + netClosing;
      const cushion = vault - cashNeeded;

      const pi = Math.round(calcMonthlyPI(loanAmt, 6.125));
      const taxesIns = Math.round(item.price * 0.0165 / 12);
      const piti = pi + taxesIns;

      document.getElementById('lbl-down-pct').innerText = downPct + '% ($' + downAmt.toLocaleString() + ')';
      document.getElementById('lbl-vault').innerText = '$' + vault.toLocaleString();

      document.getElementById('badge-neighborhood').innerText = item.badge;
      document.getElementById('badge-credit').innerText = '+$' + credit.toLocaleString() + ' Combined Closing Credit';
      document.getElementById('prop-title').innerText = item.address;
      document.getElementById('prop-specs').innerText = item.specs;
      document.getElementById('prop-price').innerText = '$' + item.price.toLocaleString();
      document.getElementById('prop-piti').innerText = '$' + piti.toLocaleString();

      document.getElementById('val-combined-credit').innerText = '$' + credit.toLocaleString();
      document.getElementById('bd-price').innerText = '$' + item.price.toLocaleString();
      document.getElementById('bd-down-pct').innerText = downPct + '%';
      document.getElementById('bd-down-amt').innerText = '$' + downAmt.toLocaleString();
      document.getElementById('bd-loan-amt').innerText = '$' + loanAmt.toLocaleString();
      document.getElementById('bd-net-closing').innerText = '$' + netClosing.toLocaleString();

      const statusEl = document.getElementById('bd-cash-status');
      if (cushion >= 0) {{
        statusEl.style.color = '#059669';
        statusEl.innerText = '$' + cashNeeded.toLocaleString() + ' Needed · $' + cushion.toLocaleString() + ' Cushion!';
      }} else {{
        statusEl.style.color = '#D92228';
        statusEl.innerText = '$' + cashNeeded.toLocaleString() + ' Needed · Short $' + Math.abs(cushion).toLocaleString();
      }}
    }}

    function playConciergeTourAudio(btnEl) {{
      const idx = parseInt(document.getElementById('prop-select').value, 10) || 0;
      window.playLiveCallClip(
        LISTINGS[idx].tourScript,
        'Aoede',
        'Redfin × Rocket Purchase Concierge',
        btnEl
      );
    }}

    window.runLiveVertexAI = async function() {{
      const btn = document.getElementById('concierge-btn');
      const model = window.getSelectedModel();
      btn.innerText = '⏳ Personalizing (' + model + ')...';
      document.getElementById('concierge-model-tag').innerText = model;

      const idx = parseInt(document.getElementById('prop-select').value, 10) || 0;
      const item = LISTINGS[idx];
      const downPct = parseFloat(document.getElementById('sl-down').value);
      const vault = parseFloat(document.getElementById('sl-vault').value);

      try {{
        const res = await fetch('/api/run-demo', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{
            code: '1.3',
            model: model,
            params: {{
              property_address: item.address,
              price: item.price,
              down_pct: downPct,
              rocket_money_vault: vault,
              combined_closing_credit: 4600
            }}
          }})
        }});
        const data = await res.json();
        document.getElementById('concierge-model-tag').innerText = data.model_used || model;
        if (data.structured_data && (data.structured_data.executive_summary || data.structured_data.banker_objection_script)) {{
          document.getElementById('concierge-output-box').innerHTML =
            data.structured_data.executive_summary || data.structured_data.banker_objection_script;
        }} else if (data.output) {{
          document.getElementById('concierge-output-box').innerHTML = data.output.replace(/\\n/g, '<br>');
        }}
      }} catch (e) {{
        console.error(e);
      }} finally {{
        btn.innerText = '✨ Personalize Bundle Offer';
      }}
    }};
  </script>
</body>
</html>"""
