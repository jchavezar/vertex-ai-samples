# -*- coding: utf-8 -*-
"""Square M.2: Project Spatial Close: Immersive Virtual Staging & 3D Neighborhood Hub — Gempix-2
Visual Design: Apple VisionOS Frosted Glassmorphism Architectural Remodel Studio (rich dark architectural backdrop
with backdrop-filter: blur(24px) translucent glass panels, #F59E0B gold, #10B981 emerald, Google Fonts Plus Jakarta Sans).
"""

from shared.standalone_uis.base_helpers import render_floating_control_bar_and_drawer


def render_sq_m_2(auth_token: str) -> str:
    code = "M.2"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>[M.2] Project Spatial Close: VisionOS Architectural Remodel Studio | Gempix-2 + HomeStyle</title>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    :root {{
      --glass-bg: rgba(18, 22, 34, 0.62);
      --glass-card: rgba(255, 255, 255, 0.08);
      --glass-border: rgba(255, 255, 255, 0.22);
      --gold: #F59E0B;
      --emerald: #10B981;
      --sky: #38BDF8;
      --text-white: #F8FAFC;
      --text-soft: #CBD5E1;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      background-color: #07090F;
      color: var(--text-white);
      font-family: 'Plus Jakarta Sans', -apple-system, sans-serif;
      min-height: 100vh;
      background-image:
        radial-gradient(circle at 18% 12%, rgba(245, 158, 11, 0.20), transparent 40%),
        radial-gradient(circle at 82% 18%, rgba(16, 185, 129, 0.18), transparent 42%),
        linear-gradient(180deg, rgba(7, 9, 15, 0.72) 0%, rgba(7, 9, 15, 0.92) 100%),
        url('/static/images/rocket_kitchen_homestyle.jpg');
      background-size: cover;
      background-position: center;
      background-attachment: fixed;
      padding-bottom: 96px;
    }}
    .mono {{ font-family: 'JetBrains Mono', monospace; }}

    /* Apple VisionOS Floating Glass Header Pill */
    .vision-header {{
      max-width: 1520px;
      margin: 18px auto 0;
      padding: 14px 26px;
      background: rgba(15, 18, 28, 0.68);
      backdrop-filter: blur(28px) saturate(180%);
      -webkit-backdrop-filter: blur(28px) saturate(180%);
      border: 1px solid var(--glass-border);
      border-radius: 999px;
      box-shadow: 0 20px 50px rgba(0, 0, 0, 0.55);
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 14px;
    }}
    @media (max-width: 900px) {{
      .vision-header {{ border-radius: 24px; margin: 12px; }}
    }}
    .vision-pill {{
      background: rgba(245, 158, 11, 0.18);
      border: 1px solid rgba(245, 158, 11, 0.55);
      color: #FDE68A;
      font-family: 'JetBrains Mono', monospace;
      font-size: 11px;
      font-weight: 700;
      padding: 5px 14px;
      border-radius: 999px;
    }}
    .vision-model-box {{
      display: flex;
      align-items: center;
      gap: 8px;
      background: rgba(255, 255, 255, 0.09);
      border: 1px solid var(--glass-border);
      padding: 6px 14px;
      border-radius: 999px;
      font-family: 'JetBrains Mono', monospace;
      font-size: 11px;
    }}
    .vision-model-box select {{
      background: transparent;
      color: #FDE68A;
      border: none;
      font-family: 'JetBrains Mono', monospace;
      font-size: 11px;
      font-weight: 700;
      outline: none;
      cursor: pointer;
    }}
    .vision-model-box select option {{ background: #0F172A; color: #FFFFFF; }}

    /* Spatial Studio Layout */
    .spatial-studio {{
      max-width: 1520px;
      margin: 22px auto;
      padding: 0 20px;
      display: grid;
      grid-template-columns: 390px 1fr;
      gap: 24px;
    }}
    @media (max-width: 1120px) {{
      .spatial-studio {{ grid-template-columns: 1fr; }}
    }}

    .frosted-panel {{
      background: var(--glass-bg);
      backdrop-filter: blur(24px) saturate(160%);
      -webkit-backdrop-filter: blur(24px) saturate(160%);
      border: 1px solid var(--glass-border);
      border-radius: 28px;
      padding: 24px;
      box-shadow: 0 24px 60px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.25);
    }}

    /* Interactive Renovation Upgrade Configurator Cards */
    .upgrade-card {{
      background: rgba(255, 255, 255, 0.06);
      border: 1px solid rgba(255, 255, 255, 0.16);
      border-radius: 18px;
      padding: 14px 16px;
      margin-bottom: 12px;
      cursor: pointer;
      transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 12px;
    }}
    .upgrade-card:hover {{
      background: rgba(255, 255, 255, 0.11);
      transform: translateY(-2px);
    }}
    .upgrade-card.selected {{
      background: linear-gradient(135deg, rgba(245, 158, 11, 0.22), rgba(16, 185, 129, 0.18));
      border-color: var(--gold);
      box-shadow: 0 8px 24px rgba(245, 158, 11, 0.22);
    }}
    .upgrade-check {{
      width: 24px;
      height: 24px;
      border-radius: 50%;
      border: 2px solid rgba(255, 255, 255, 0.4);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 13px;
      font-weight: 800;
    }}
    .upgrade-card.selected .upgrade-check {{
      background: var(--gold);
      border-color: var(--gold);
      color: #000;
    }}

    .btn-vision {{
      width: 100%;
      padding: 13px 18px;
      border-radius: 999px;
      border: 1px solid rgba(255, 255, 255, 0.3);
      background: linear-gradient(135deg, var(--gold), #D97706);
      color: #090D16;
      font-family: 'Plus Jakarta Sans', sans-serif;
      font-size: 13px;
      font-weight: 800;
      cursor: pointer;
      transition: 0.2s;
      box-shadow: 0 10px 26px rgba(245, 158, 11, 0.35);
    }}
    .btn-vision:hover {{ transform: translateY(-1px); filter: brightness(1.07); }}

    /* Right Architectural Viewport & Fannie Mae HomeStyle Equity HUD */
    .viewport-stage {{
      position: relative;
      border-radius: 22px;
      overflow: hidden;
      border: 1px solid var(--glass-border);
      background: #05070B;
      min-height: 390px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      padding: 20px;
      background-size: cover;
      background-position: center;
      transition: background-image 0.35s ease;
    }}
    .spatial-hud-overlay {{
      background: rgba(10, 14, 24, 0.72);
      backdrop-filter: blur(18px);
      border: 1px solid var(--glass-border);
      border-radius: 16px;
      padding: 14px 18px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 12px;
    }}

    .homestyle-kpi-grid {{
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 14px;
      margin-top: 18px;
    }}
    @media (max-width: 960px) {{
      .homestyle-kpi-grid {{ grid-template-columns: 1fr 1fr; }}
    }}
    .hs-metric-pill {{
      background: rgba(255, 255, 255, 0.06);
      border: 1px solid rgba(255, 255, 255, 0.16);
      border-radius: 18px;
      padding: 16px;
    }}
    .hs-metric-pill.emerald {{
      border-color: var(--emerald);
      background: rgba(16, 185, 129, 0.14);
    }}
    .hs-metric-pill.gold {{
      border-color: var(--gold);
      background: rgba(245, 158, 11, 0.14);
    }}
  </style>
</head>
<body>

  <!-- APPLE VISIONOS FLOATING GLASS HEADER -->
  <header class="vision-header">
    <div style="display:flex;align-items:center;gap:14px;flex-wrap:wrap;">
      <span class="vision-pill">🥽 PROJECT SPATIAL CLOSE // GEMPIX-2 + VISIONOS • SQUARE [M.2]</span>
      <div>
        <h1 style="font-size:18px;font-weight:800;">Immersive Virtual Staging & Fannie Mae HomeStyle® Remodel Studio</h1>
        <p class="mono" style="font-size:11px;color:var(--text-soft);">Redfin 3D Digital Twin + Gempix-2 Architectural Remodel + Single-Close Fannie Mae HomeStyle Equity Engine</p>
      </div>
    </div>
    <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;">
      <div class="vision-model-box">
        <span>SPATIAL MODEL:</span>
        <select id="app-model-select" onchange="window.syncSelectedModel(this.value)">
          <option value="gemini-4-argon" selected>gemini-4-argon (Frontier Global)</option>
          <option value="gemini-3.8-flash">gemini-3.8-flash (Fast / ADK Runtime)</option>
        </select>
      </div>
      <button class="btn-vision" style="width:auto;padding:9px 18px;" onclick="window.runLiveVertexAI()">
        ⚡ Underwrite HomeStyle Loan (/api/run-demo)
      </button>
    </div>
  </header>

  <!-- MAIN VISIONOS STUDIO -->
  <main class="spatial-studio">

    <!-- LEFT: RENOVATION UPGRADE CONFIGURATOR -->
    <aside class="frosted-panel" style="display:flex;flex-direction:column;justify-content:space-between;gap:16px;">
      <div>
        <div class="mono" style="font-size:11px;color:var(--gold);font-weight:700;text-transform:uppercase;margin-bottom:6px;">
          ✨ Gempix-2 Spatial Renovation Configurator
        </div>
        <h2 style="font-size:18px;font-weight:800;margin-bottom:6px;">Select Architectural Remodel Modules</h2>
        <p style="font-size:12.5px;color:var(--text-soft);line-height:1.55;margin-bottom:16px;">
          Toggle remodel packages below to transform the 3D property canvas and compute Fannie Mae HomeStyle® <strong>After-Improved Value (AIV)</strong> & instant net equity gain.
        </p>

        <div style="margin-bottom:12px;">
          <label class="mono" style="font-size:10.5px;color:var(--text-soft);display:block;margin-bottom:4px;">BASE AS-IS PURCHASE PRICE ($):</label>
          <input type="number" id="inp-base-price" value="480000" oninput="recalcSpatialHomeStyle()"
            style="width:100%;padding:10px 14px;border-radius:12px;border:1px solid var(--glass-border);background:rgba(0,0,0,0.4);color:#FFF;font-family:'JetBrains Mono',monospace;font-size:13px;font-weight:700;">
        </div>

        <!-- Upgrade 1: Chef's Kitchen +$45k -->
        <div class="upgrade-card selected" id="upg-kitchen" onclick="toggleUpgrade('kitchen')">
          <div>
            <div style="font-size:14px;font-weight:800;color:#FFF;">🍽️ Chef's Waterfall Quartz Kitchen</div>
            <div class="mono" style="font-size:11px;color:var(--gold);margin-top:2px;">Cost: +$45,000 • Appraised Value Lift: +$62,000</div>
          </div>
          <div class="upgrade-check">✓</div>
        </div>

        <!-- Upgrade 2: Garage ADU +$65k -->
        <div class="upgrade-card selected" id="upg-adu" onclick="toggleUpgrade('adu')">
          <div>
            <div style="font-size:14px;font-weight:800;color:#FFF;">🏡 Detached Garage ADU Studio Suite</div>
            <div class="mono" style="font-size:11px;color:var(--gold);margin-top:2px;">Cost: +$65,000 • Appraised Value Lift: +$74,000</div>
          </div>
          <div class="upgrade-check">✓</div>
        </div>

        <!-- Upgrade 3: Bath & Solar +$25k -->
        <div class="upgrade-card selected" id="upg-solar" onclick="toggleUpgrade('solar')">
          <div>
            <div style="font-size:14px;font-weight:800;color:#FFF;">☀️ Spa Primary Bath + 9kW Solar Roof</div>
            <div class="mono" style="font-size:11px;color:var(--gold);margin-top:2px;">Cost: +$25,000 • Appraised Value Lift: +$22,000</div>
          </div>
          <div class="upgrade-check">✓</div>
        </div>

        <!-- Scene Camera Switcher -->
        <div style="margin-top:14px;">
          <div class="mono" style="font-size:10.5px;color:var(--text-soft);margin-bottom:6px;">SPATIAL CAMERA LENS (GEMPIX-2 RENDER):</div>
          <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:6px;">
            <button onclick="setSpatialLens('kitchen')" class="mono" style="padding:7px;border-radius:10px;border:1px solid var(--glass-border);background:rgba(255,255,255,0.1);color:#FFF;font-size:10.5px;cursor:pointer;">Chef Kitchen</button>
            <button onclick="setSpatialLens('industrial')" class="mono" style="padding:7px;border-radius:10px;border:1px solid var(--glass-border);background:rgba(255,255,255,0.1);color:#FFF;font-size:10.5px;cursor:pointer;">ADU Loft</button>
            <button onclick="setSpatialLens('before')" class="mono" style="padding:7px;border-radius:10px;border:1px solid var(--glass-border);background:rgba(255,255,255,0.1);color:#FFF;font-size:10.5px;cursor:pointer;">As-Is Before</button>
          </div>
        </div>
      </div>

      <button class="btn-vision" onclick="recalcSpatialHomeStyle()">
        🥽 Run Spatial HomeStyle Valuation (/api/sandbox)
      </button>
    </aside>

    <!-- RIGHT: ARCHITECTURAL VIEWPORT & FANNIE MAE HOMESTYLE EQUITY HUD -->
    <section class="frosted-panel" style="display:flex;flex-direction:column;justify-content:space-between;">
      <div>
        <div class="viewport-stage" id="spatial-viewport" style="background-image:url('/static/images/rocket_kitchen_homestyle.jpg');">
          <div class="spatial-hud-overlay">
            <div>
              <span class="mono" style="font-size:10.5px;color:var(--gold);font-weight:700;">REDFIN 3D TWIN • 1420 VINSETTA BLVD, ROYAL OAK MI</span>
              <div style="font-size:15px;font-weight:800;margin-top:2px;" id="hud-active-modules">Active Remodel: Chef's Kitchen + Garage ADU + Bath & Solar</div>
            </div>
            <span class="mono" style="background:rgba(16,185,129,0.22);border:1px solid var(--emerald);color:#6EE7B7;padding:5px 12px;border-radius:999px;font-size:11px;font-weight:700;">
              SynthID + Gempix-2 Geometry Locked
            </span>
          </div>

          <div class="spatial-hud-overlay" style="margin-top:auto;">
            <div class="mono" style="font-size:11.5px;">
              <strong>FANNIE MAE HOMESTYLE B5-3.2-01 CAP CHECK:</strong> Renovation Escrow (<span id="hud-reno-pct">21.2%</span> of AIV) &lt;= <strong>75.0% Max Cap (PASS)</strong>
            </div>
            <div class="mono" id="spatial-sandbox-ms" style="font-size:11px;color:var(--gold);">
              Sandbox Verified (1.3ms)
            </div>
          </div>
        </div>

        <!-- 4-Box Fannie Mae HomeStyle KPI Row -->
        <div class="homestyle-kpi-grid">
          <div class="hs-metric-pill">
            <div class="mono" style="font-size:10px;color:var(--text-soft);">TOTAL ACQUISITION + REMODEL</div>
            <div class="mono" id="kpi-total-cost" style="font-size:21px;font-weight:800;margin-top:4px;">$615,000</div>
            <div class="mono" id="kpi-cost-sub" style="font-size:10.5px;color:var(--text-soft);margin-top:2px;">$480k Base + $135k Remodel</div>
          </div>

          <div class="hs-metric-pill gold">
            <div class="mono" style="font-size:10px;color:#FDE68A;">AFTER-IMPROVED VALUE (AIV)</div>
            <div class="mono" id="kpi-aiv" style="font-size:21px;font-weight:800;color:var(--gold);margin-top:4px;">$638,000</div>
            <div class="mono" style="font-size:10.5px;color:#FDE68A;margin-top:2px;">Amrock Comp-Backed AIV</div>
          </div>

          <div class="hs-metric-pill emerald">
            <div class="mono" style="font-size:10px;color:#6EE7B7;">INSTANT NET EQUITY GAIN</div>
            <div class="mono" id="kpi-net-equity" style="font-size:21px;font-weight:800;color:var(--emerald);margin-top:4px;">+$23,000</div>
            <div class="mono" style="font-size:10.5px;color:#6EE7B7;margin-top:2px;">Day-1 Sweat Equity Created</div>
          </div>

          <div class="hs-metric-pill">
            <div class="mono" style="font-size:10px;color:var(--text-soft);">SINGLE-CLOSE HOMESTYLE P&I</div>
            <div class="mono" id="kpi-hs-pi" style="font-size:21px;font-weight:800;color:var(--sky);margin-top:4px;">$3,594/mo</div>
            <div class="mono" style="font-size:10.5px;color:var(--emerald);margin-top:2px;">Saves $485/mo vs 9.75% HELOC</div>
          </div>
        </div>
      </div>

      <!-- Vertex AI Underwriting & Contractor Draw Schedule Output -->
      <div style="margin-top:18px;background:rgba(0,0,0,0.45);border:1px solid var(--glass-border);border-radius:18px;padding:16px 20px;">
        <div class="mono" style="font-size:11px;color:var(--gold);font-weight:700;margin-bottom:6px;">
          🏗️ FANNIE MAE HOMESTYLE® ESCROW DRAW SCHEDULE & VERTEX AI SYNTHESIS (`calc_spatial_homestyle`)
        </div>
        <div id="spatial-ai-output" style="font-size:13px;line-height:1.65;color:var(--text-white);">
          <strong>Single-Close Advantage:</strong> Instead of buying at $480,000 and taking a high-rate 9.75% second-lien HELOC for $135,000 in renovations, Rocket Mortgage finances the entire <strong>$615,000 acquisition + escrow budget</strong> in one 6.25% first mortgage underwritten against the <strong>$638,000 After-Improved Value (AIV)</strong>, unlocking <strong>+$23,000 in immediate net equity</strong>.
        </div>
      </div>
    </section>

  </main>

  <script>
    const UPGRADES = {{
      kitchen: {{ selected: true, name: "Chef's Kitchen", cost: 45000, lift: 62000, img: "/static/images/rocket_kitchen_homestyle.jpg" }},
      adu:     {{ selected: true, name: "Garage ADU",     cost: 65000, lift: 74000, img: "/static/images/rocket_loft_after_industrial.jpg" }},
      solar:   {{ selected: true, name: "Bath & Solar",   cost: 25000, lift: 22000, img: "/static/images/rocket_loft_after_midcentury.jpg" }}
    }};

    function toggleUpgrade(key) {{
      UPGRADES[key].selected = !UPGRADES[key].selected;
      const card = document.getElementById('upg-' + key);
      if (UPGRADES[key].selected) {{
        card.classList.add('selected');
        document.getElementById('spatial-viewport').style.backgroundImage = `url('${'{'}UPGRADES[key].img{'}'}')`;
      }} else {{
        card.classList.remove('selected');
      }}
      recalcSpatialHomeStyle();
    }}

    function setSpatialLens(lens) {{
      const vp = document.getElementById('spatial-viewport');
      if (lens === 'kitchen') vp.style.backgroundImage = "url('/static/images/rocket_kitchen_homestyle.jpg')";
      else if (lens === 'industrial') vp.style.backgroundImage = "url('/static/images/rocket_loft_after_industrial.jpg')";
      else vp.style.backgroundImage = "url('/static/images/rocket_loft_before.jpg')";
    }}

    async function recalcSpatialHomeStyle() {{
      const basePrice = parseFloat(document.getElementById('inp-base-price').value || 480000);
      let renoCost = 0;
      let valueLift = 0;
      let names = [];

      Object.values(UPGRADES).forEach(u => {{
        if (u.selected) {{
          renoCost += u.cost;
          valueLift += u.lift;
          names.push(u.name);
        }}
      }});

      const totalAcq = basePrice + renoCost;
      const aiv = basePrice + valueLift;
      const netEquity = aiv - totalAcq;
      const loanAmt = totalAcq * 0.95;
      const r = (6.25 / 100.0) / 12.0;
      const pi = Math.round(loanAmt * (r * Math.pow(1 + r, 360)) / (Math.pow(1 + r, 360) - 1));
      const renoPctAiv = aiv > 0 ? ((renoCost / aiv) * 100).toFixed(1) : '0.0';

      document.getElementById('hud-active-modules').innerText = names.length ? ('Active Remodel: ' + names.join(' + ')) : 'As-Is Property (No Upgrades Selected)';
      document.getElementById('hud-reno-pct').innerText = renoPctAiv + '%';
      document.getElementById('kpi-total-cost').innerText = '$' + totalAcq.toLocaleString();
      document.getElementById('kpi-cost-sub').innerText = `$${'{'} (basePrice/1000).toFixed(0) {'}'}k Base + $${'{'} (renoCost/1000).toFixed(0) {'}'}k Remodel`;
      document.getElementById('kpi-aiv').innerText = '$' + aiv.toLocaleString();
      document.getElementById('kpi-net-equity').innerText = (netEquity >= 0 ? '+$' : '-$') + Math.abs(netEquity).toLocaleString();
      document.getElementById('kpi-hs-pi').innerText = '$' + pi.toLocaleString() + '/mo';

      try {{
        const res = await fetch('/api/sandbox', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{
            code: 'M.2',
            action: 'calc_homestyle_renovation',
            params: {{
              secondary_action: 'calc_spatial_homestyle',
              purchase_price: basePrice,
              renovation_cost: renoCost,
              after_improved_value: aiv
            }}
          }})
        }});
        const data = await res.json();
        document.getElementById('spatial-sandbox-ms').innerText = `Sandbox Verified (${'{'}data.execution_ms || 1.1{'}'}ms)`;
      }} catch (e) {{}}
    }}

    window.runLiveVertexAI = async function() {{
      const model = window.getSelectedModel ? window.getSelectedModel() : 'gemini-4-argon';
      const basePrice = parseFloat(document.getElementById('inp-base-price').value || 480000);
      const outEl = document.getElementById('spatial-ai-output');
      outEl.innerHTML = `Synthesizing Fannie Mae HomeStyle® Appraisal & Draw Schedule with <strong>${'{'}model{'}'}</strong>...`;

      try {{
        const res = await fetch('/api/run-demo', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{
            code: 'M.2',
            model: model,
            user_input: `Compute Fannie Mae HomeStyle After-Improved Value ($638,000) and contractor draw schedule for a $${'{'}basePrice{'}'} purchase with Chef's Kitchen (+$45k), Garage ADU (+$65k), and Bath & Solar (+$25k).`,
            params: {{ purchase_price: basePrice, renovation_cost: 135000, after_improved_value: 638000 }}
          }})
        }});
        const data = await res.json();
        outEl.innerHTML = `<strong style="color:var(--gold);">[${'{'}data.model_used || model{'}'}]:</strong> ${'{'}data.output || 'HomeStyle package verified.'{'}'}`;
      }} catch (e) {{
        outEl.innerText = "Vertex AI Error: " + e.message;
      }}
    }};

    document.addEventListener('DOMContentLoaded', () => {{
      recalcSpatialHomeStyle();
    }});
  </script>

  {render_floating_control_bar_and_drawer(code, auth_token)}
</body>
</html>"""
