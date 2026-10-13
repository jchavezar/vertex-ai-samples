# -*- coding: utf-8 -*-
"""Square 1.4: Dynamic Loan Pricing & Amortization Co-Pilot — Standalone UI Design File.
Visual Archetype: Monark™ / Rocket Money Sovereign Wealth & Capital OS Dashboard
(Wealth Obsidian #07090E, Champagne Gold #D4AF37, Emerald Mint #10B981, Space Grotesk + JetBrains Mono,
Left Wealth Sidebar + Interactive Rocket Money Vault Transfer Dial + Multi-Curve SVG Amortization Chart)."""

from shared.standalone_uis.base_helpers import render_floating_control_bar_and_drawer


def render_sq_1_4(auth_token: str) -> str:
    controls = render_floating_control_bar_and_drawer("1.4", auth_token)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Monark™ x Rocket Money Capital & Amortization OS</title>
  <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=JetBrains+Mono:wght@400;600;700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: 'Inter', sans-serif;
      background: #07090E;
      color: #F8FAFC;
      min-height: 100vh;
      display: grid;
      grid-template-columns: 250px 1fr;
    }}
    @media (max-width: 960px) {{
      body {{ grid-template-columns: 1fr; }}
      .wealth-sidebar {{ display: none; }}
    }}
    .mono {{ font-family: 'JetBrains Mono', monospace; }}
    .grotesk {{ font-family: 'Space Grotesk', sans-serif; }}

    /* Left Wealth Navigation Sidebar */
    .wealth-sidebar {{
      background: #0B0E17;
      border-right: 1px solid #1C2333;
      padding: 24px 18px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
    }}
    .gold-badge {{
      background: linear-gradient(135deg, rgba(212,175,55,0.2), rgba(16,185,129,0.15));
      border: 1px solid rgba(212,175,55,0.45);
      color: #FDE68A;
      padding: 4px 10px;
      border-radius: 6px;
      font-size: 10px;
      font-weight: 700;
      letter-spacing: 0.08em;
      text-transform: uppercase;
    }}
    .nav-item {{
      padding: 11px 14px;
      border-radius: 10px;
      font-size: 13px;
      font-weight: 600;
      color: #94A3B8;
      display: flex;
      align-items: center;
      gap: 10px;
      cursor: pointer;
      margin-bottom: 4px;
    }}
    .nav-item.active {{
      background: linear-gradient(90deg, rgba(212,175,55,0.16), transparent);
      color: #FDE68A;
      border-left: 3px solid #D4AF37;
    }}

    /* Main Financial OS Canvas */
    .fintech-main {{
      padding: 28px 36px 90px 36px;
      overflow-y: auto;
    }}
    .kpi-strip {{
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 16px;
      margin: 22px 0;
    }}
    @media (max-width: 1100px) {{
      .kpi-strip {{ grid-template-columns: repeat(2, 1fr); }}
    }}
    .wealth-card {{
      background: #0F1420;
      border: 1px solid #1E293B;
      border-radius: 16px;
      padding: 20px;
      position: relative;
      overflow: hidden;
    }}
    .wealth-card.gold-glow {{
      border-color: rgba(212,175,55,0.5);
      box-shadow: 0 12px 32px rgba(212,175,55,0.08);
    }}
    .ltv-pill {{
      padding: 8px 16px;
      border-radius: 10px;
      border: 1px solid #263147;
      background: #131A29;
      color: #CBD5E1;
      font-family: 'JetBrains Mono', monospace;
      font-size: 12px;
      font-weight: 700;
      cursor: pointer;
      transition: 0.2s;
    }}
    .ltv-pill.active {{
      background: linear-gradient(135deg, #D4AF37, #B45309);
      color: #07090E;
      border-color: #FDE68A;
    }}
    .gold-btn {{
      background: linear-gradient(135deg, #D4AF37, #10B981);
      color: #07090E;
      border: none;
      padding: 11px 20px;
      border-radius: 10px;
      font-weight: 800;
      font-size: 12.5px;
      cursor: pointer;
    }}
  </style>
</head>
<body>

  <!-- LEFT SOVEREIGN WEALTH SIDEBAR -->
  <aside class="wealth-sidebar">
    <div>
      <div style="display:flex;align-items:center;gap:10px;margin-bottom:24px;">
        <div style="width:36px;height:36px;border-radius:10px;background:linear-gradient(135deg,#D4AF37,#10B981);display:flex;align-items:center;justify-content:center;color:#07090E;font-weight:900;font-size:18px;">M</div>
        <div>
          <div class="grotesk" style="font-weight:700;font-size:16px;color:#FFF;">MONARK™ // ROCKET</div>
          <div class="mono" style="font-size:10px;color:#D4AF37;">CAPITAL & AMORTIZATION OS</div>
        </div>
      </div>

      <div class="nav-item active" onclick="setLtvPreset(540000)">💎 LTV & LLPA Tier Optimizer</div>
      <div class="nav-item" onclick="setLtvPreset(650000)">🏦 Rocket Money Vault Bridge</div>
      <div class="nav-item" onclick="setLtvPreset(425000)">📈 30-Yr Amortization Ledger</div>
      <div class="nav-item" onclick="window.runLiveVertexAI()">🤖 AI CFO Capital Strategy</div>
    </div>

    <div style="background:#131A29;border:1px solid #263147;border-radius:12px;padding:14px;">
      <div class="mono" style="font-size:10px;color:#D4AF37;text-transform:uppercase;margin-bottom:4px;">Rocket Money Linked Vault</div>
      <div class="mono" style="font-size:18px;font-weight:700;color:#10B981;">$81,400.00</div>
      <div style="font-size:11px;color:#94A3B8;margin-top:2px;">High-Yield Savings (4.35% APY)</div>
    </div>
  </aside>

  <!-- MAIN FINTECH CANVAS -->
  <main class="fintech-main">
    <div style="display:flex;flex-wrap:wrap;justify-content:space-between;align-items:center;gap:14px;border-bottom:1px solid #1E293B;padding-bottom:18px;">
      <div>
        <span class="gold-badge">gVisor Deterministic Financial Sandbox • Square 1.4</span>
        <h1 class="grotesk" style="font-size:28px;font-weight:700;margin-top:6px;">Dynamic Loan Pricing, LLPA Cliff & PMI Drop-Off Engine</h1>
      </div>
      <div style="display:flex;align-items:center;gap:12px;">
        <div class="mono" style="background:#0F1420;padding:8px 14px;border-radius:10px;border:1px solid #263147;font-size:11px;">
          Model:
          <select id="app-model-select" onchange="window.syncSelectedModel(this.value)" style="background:transparent;color:#FDE68A;font-weight:700;border:none;outline:none;font-family:'JetBrains Mono',monospace;font-size:11px;cursor:pointer;">
            <option value="gemini-4-argon" style="background:#07090E;">gemini-4-argon</option>
            <option value="gemini-3.8-flash" style="background:#07090E;">gemini-3.8-flash</option>
          </select>
        </div>
        <button class="gold-btn" onclick="window.runLiveVertexAI()" id="cfo-btn">⚡ Run CFO Capital Synthesis</button>
      </div>
    </div>

    <!-- 4 KPI WEALTH CARDS -->
    <div class="kpi-strip">
      <div class="wealth-card">
        <div class="mono" style="font-size:11px;color:#94A3B8;text-transform:uppercase;">90% LTV Baseline (10% Down)</div>
        <div class="mono" style="font-size:24px;font-weight:700;color:#F8FAFC;margin:8px 0;" id="kpi-90-piti">$3,962.03/mo</div>
        <div class="mono" style="font-size:11px;color:#F43F5E;" id="kpi-90-sub">Loan $486,000 @ 6.125% + $166 PMI</div>
      </div>

      <div class="wealth-card gold-glow">
        <div class="mono" style="font-size:11px;color:#FDE68A;text-transform:uppercase;">85% LTV Optimized (15% Down) ★</div>
        <div class="mono" style="font-size:24px;font-weight:700;color:#10B981;margin:8px 0;" id="kpi-85-piti">$3,675.29/mo</div>
        <div class="mono" style="font-size:11px;color:#FDE68A;" id="kpi-85-sub">Loan $459,000 @ 5.990% + $92 PMI</div>
      </div>

      <div class="wealth-card">
        <div class="mono" style="font-size:11px;color:#94A3B8;text-transform:uppercase;">Monthly Cash-Flow Saved</div>
        <div class="mono" style="font-size:24px;font-weight:700;color:#D4AF37;margin:8px 0;" id="kpi-mo-sav">$286.74/mo</div>
        <div class="mono" style="font-size:11px;color:#10B981;">12.74% Tax-Free Effective Yield on $27k</div>
      </div>

      <div class="wealth-card">
        <div class="mono" style="font-size:11px;color:#94A3B8;text-transform:uppercase;">60-Month Cumulative Savings</div>
        <div class="mono" style="font-size:24px;font-weight:700;color:#38BDF8;margin:8px 0;" id="kpi-5yr-sav">$17,204.40</div>
        <div class="mono" style="font-size:11px;color:#94A3B8;">PMI Auto-Drops at Month 54 (78% LTV)</div>
      </div>
    </div>

    <!-- INTERACTIVE CONTROLS + SVG MULTI-CURVE AMORTIZATION CHART -->
    <div style="display:grid;grid-template-columns:380px 1fr;gap:20px;">
      <div class="wealth-card" style="display:flex;flex-direction:column;gap:18px;">
        <div class="grotesk" style="font-size:16px;font-weight:700;color:#FDE68A;">🎛️ Capital Allocation Controls</div>

        <div>
          <div class="mono" style="display:flex;justify-content:space-between;font-size:12px;margin-bottom:6px;">
            <span style="color:#94A3B8;">Target Property Price:</span>
            <strong id="lbl-price" style="color:#FDE68A;">$540,000</strong>
          </div>
          <input type="range" id="sl-price" min="320000" max="950000" step="10000" value="540000" style="width:100%;accent-color:#D4AF37;" oninput="recalcPricing()">
        </div>

        <div>
          <div class="mono" style="font-size:11px;color:#94A3B8;margin-bottom:8px;">Click Property Price Presets:</div>
          <div style="display:flex;gap:8px;flex-wrap:wrap;">
            <button class="ltv-pill" onclick="setLtvPreset(420000)">$420k Starter</button>
            <button class="ltv-pill active" onclick="setLtvPreset(540000)">$540k Move-Up</button>
            <button class="ltv-pill" onclick="setLtvPreset(720000)">$720k Premier</button>
          </div>
        </div>

        <div style="background:#0B0E17;border:1px solid #1E293B;border-radius:12px;padding:14px;">
          <div class="mono" style="font-size:10px;color:#10B981;text-transform:uppercase;margin-bottom:6px;">AI CFO Arbitrage Verdict</div>
          <div id="cfo-verdict-box" style="font-size:12.5px;line-height:1.6;color:#CBD5E1;">
            Shifting <strong>$27,000</strong> from your Rocket Money Vault (earning 4.35% taxable APY) to cross the <strong>85% LTV Fannie Mae LLPA cliff</strong> lowers your note rate to <strong>5.990%</strong> and cuts private MI from 0.41% to 0.24%, generating a <strong>12.7% risk-free return</strong>.
          </div>
        </div>
      </div>

      <!-- SVG Multi-Curve 30-Year Principal & Interest Visualizer -->
      <div class="wealth-card">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">
          <div>
            <div class="grotesk" style="font-size:16px;font-weight:700;">30-Year Cumulative Equity & Interest Curve (90% LTV vs. 85% LTV)</div>
            <div class="mono" style="font-size:11px;color:#94A3B8;">Gold = 85% LTV Accelerated Equity • Coral Dashed = 90% LTV Baseline</div>
          </div>
          <span class="mono" id="chart-model-tag" style="font-size:11px;color:#10B981;background:rgba(16,185,129,0.12);padding:4px 10px;border-radius:6px;">gVisor Math Verified</span>
        </div>

        <svg viewBox="0 0 680 230" style="width:100%;height:230px;background:#090C14;border-radius:12px;border:1px solid #1E293B;">
          <!-- Grid lines -->
          <line x1="50" y1="30" x2="650" y2="30" stroke="#1E293B" stroke-dasharray="4 4"/>
          <line x1="50" y1="95" x2="650" y2="95" stroke="#1E293B" stroke-dasharray="4 4"/>
          <line x1="50" y1="160" x2="650" y2="160" stroke="#1E293B" stroke-dasharray="4 4"/>
          <line x1="50" y1="200" x2="650" y2="200" stroke="#334155"/>
          <!-- 90% LTV Curve -->
          <path d="M 50 195 Q 260 155, 640 55" fill="none" stroke="#F43F5E" stroke-width="2.5" stroke-dasharray="6 4"/>
          <!-- 85% LTV Curve -->
          <path id="svg-opt-curve" d="M 50 185 Q 240 120, 640 28" fill="none" stroke="#D4AF37" stroke-width="3.5"/>
          <!-- PMI Drop Marker -->
          <circle cx="210" cy="142" r="6" fill="#10B981"/>
          <text x="222" y="146" fill="#10B981" font-family="JetBrains Mono" font-size="11" font-weight="bold">Month 54: Automatic 78% LTV PMI Drop (-$92/mo)</text>
          <text x="55" y="218" fill="#94A3B8" font-family="JetBrains Mono" font-size="10">Year 1</text>
          <text x="330" y="218" fill="#94A3B8" font-family="JetBrains Mono" font-size="10">Year 15</text>
          <text x="605" y="218" fill="#94A3B8" font-family="JetBrains Mono" font-size="10">Year 30</text>
        </svg>
      </div>
    </div>
  </main>

  {controls}

  <script>
    function setLtvPreset(price) {{
      document.getElementById('sl-price').value = price;
      recalcPricing();
    }}

    async function recalcPricing() {{
      const price = parseFloat(document.getElementById('sl-price').value);
      document.getElementById('lbl-price').innerText = '$' + price.toLocaleString();
      const res = await fetch('/api/sandbox', {{
        method: 'POST',
        headers: {{'Content-Type': 'application/json'}},
        body: JSON.stringify({{code: '1.4', action: 'calc_dynamic_pricing', params: {{price: price}}}})
      }});
      const data = await res.json();
      if (data.ok && data.metrics) {{
        const m = data.metrics;
        const p90 = ((m.scenario_90_ltv || '').split('=')[1] || '').trim();
        const p85 = ((m.scenario_85_ltv || '').split('=')[1] || '').trim();
        if (p90) document.getElementById('kpi-90-piti').innerText = p90;
        if (p85) document.getElementById('kpi-85-piti').innerText = p85;
        document.getElementById('kpi-90-sub').innerText = (m.scenario_90_ltv || '').split('=')[0];
        document.getElementById('kpi-85-sub').innerText = (m.scenario_85_ltv || '').split('=')[0];
        document.getElementById('kpi-mo-sav').innerText = ((m.monthly_piti_savings || '').split(' ')[0] || '');
        document.getElementById('kpi-5yr-sav').innerText = ((m.five_year_interest_pmi_saved || '').split(' ')[0] || '');
      }}
    }}

    window.runLiveVertexAI = async function() {{
      const btn = document.getElementById('cfo-btn');
      const model = window.getSelectedModel();
      btn.innerText = '⏳ Synthesizing on ' + model + '...';
      const price = parseFloat(document.getElementById('sl-price').value);
      try {{
        const res = await fetch('/api/run-demo', {{
          method: 'POST',
          headers: {{'Content-Type': 'application/json'}},
          body: JSON.stringify({{code: '1.4', model: model, params: {{price: price}}}})
        }});
        const data = await res.json();
        document.getElementById('chart-model-tag').innerText = (data.model_used || model) + ' Verified';
        if (data.structured_data && (data.structured_data.capital_allocation_advice || data.structured_data.executive_summary)) {{
          document.getElementById('cfo-verdict-box').innerHTML = data.structured_data.capital_allocation_advice || data.structured_data.executive_summary;
        }} else if (data.output) {{
          document.getElementById('cfo-verdict-box').innerText = data.output;
        }}
      }} catch (e) {{}}
      finally {{
        btn.innerText = '⚡ Run CFO Capital Synthesis';
      }}
    }};
  </script>
</body>
</html>"""
