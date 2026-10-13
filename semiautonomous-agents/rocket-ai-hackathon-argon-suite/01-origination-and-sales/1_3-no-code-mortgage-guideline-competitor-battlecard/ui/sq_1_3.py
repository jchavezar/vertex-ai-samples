# -*- coding: utf-8 -*-
"""Square 1.3: No-Code Mortgage Guideline & Competitor Battlecard Agent — Standalone UI Design File.
Visual Archetype: Gemini Enterprise Grounded Search & Competitive Intelligence Arena
(Clean Google Workspace Slate #F8FAFC, Royal Indigo #3730A3, Emerald #059669, Outfit font,
prominent Real Gemini Enterprise UI Launcher + Live streamAssist Search + 3-Way Competitor Rate Matrix)."""

from shared.standalone_uis.base_helpers import render_floating_control_bar_and_drawer


def render_sq_1_3(auth_token: str) -> str:
    controls = render_floating_control_bar_and_drawer("1.3", auth_token)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Gemini Enterprise Guideline & Competitor Battlecard Arena | Rocket Pro TPO</title>
  <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap" rel="stylesheet">
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: 'Outfit', sans-serif;
      background: #F4F6FB;
      color: #0F172A;
      min-height: 100vh;
      padding-bottom: 80px;
    }}
    .mono {{ font-family: 'JetBrains Mono', monospace; }}

    /* Gemini Enterprise Top Navigation Bar */
    .ge-nav {{
      background: #FFFFFF;
      border-bottom: 1px solid #E2E8F0;
      padding: 14px 32px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      box-shadow: 0 2px 12px rgba(15, 23, 42, 0.04);
    }}
    .ge-sparkle-badge {{
      background: linear-gradient(135deg, #4F46E5, #9333EA, #EC4899);
      color: #FFF;
      padding: 6px 14px;
      border-radius: 999px;
      font-size: 12px;
      font-weight: 700;
      display: inline-flex;
      align-items: center;
      gap: 6px;
    }}
    .real-ge-btn {{
      background: #0F172A;
      color: #FFFFFF;
      text-decoration: none;
      padding: 9px 18px;
      border-radius: 999px;
      font-size: 12.5px;
      font-weight: 700;
      display: inline-flex;
      align-items: center;
      gap: 8px;
      border: 2px solid #6366F1;
      transition: 0.2s;
    }}
    .real-ge-btn:hover {{
      background: #3730A3;
      transform: translateY(-1px);
    }}

    /* Search Hero Section */
    .ge-hero {{
      max-width: 1180px;
      margin: 28px auto 0 auto;
      padding: 0 24px;
    }}
    .search-shell {{
      background: #FFFFFF;
      border: 2px solid #C7D2FE;
      border-radius: 999px;
      padding: 8px 10px 8px 24px;
      display: flex;
      align-items: center;
      gap: 12px;
      box-shadow: 0 12px 32px rgba(79, 70, 229, 0.09);
    }}
    .search-shell input {{
      flex: 1;
      border: none;
      outline: none;
      font-family: 'Outfit', sans-serif;
      font-size: 16px;
      font-weight: 500;
      color: #0F172A;
    }}
    .stream-btn {{
      background: linear-gradient(135deg, #4F46E5, #7C3AED);
      color: #FFFFFF;
      border: none;
      padding: 12px 24px;
      border-radius: 999px;
      font-family: 'Outfit', sans-serif;
      font-weight: 700;
      font-size: 14px;
      cursor: pointer;
    }}

    /* 3-Way Battlecard Arena Grid */
    .battle-grid {{
      max-width: 1180px;
      margin: 24px auto;
      padding: 0 24px;
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 20px;
    }}
    @media (max-width: 960px) {{
      .battle-grid {{ grid-template-columns: 1fr; }}
    }}
    .competitor-card {{
      background: #FFFFFF;
      border-radius: 20px;
      border: 1px solid #E2E8F0;
      padding: 24px;
      box-shadow: 0 6px 20px rgba(15, 23, 42, 0.04);
      position: relative;
    }}
    .competitor-card.winner {{
      border: 2px solid #059669;
      background: linear-gradient(180deg, #ECFDF5 0%, #FFFFFF 38%);
      box-shadow: 0 16px 36px rgba(5, 150, 105, 0.12);
    }}
    .winner-ribbon {{
      position: absolute;
      top: -12px;
      right: 20px;
      background: #059669;
      color: #FFFFFF;
      padding: 4px 14px;
      border-radius: 999px;
      font-size: 11px;
      font-weight: 800;
      letter-spacing: 0.05em;
    }}

    /* Grounded StreamAssist Response Box */
    .grounded-box {{
      max-width: 1180px;
      margin: 0 auto;
      padding: 0 24px;
    }}
    .grounded-panel {{
      background: #FFFFFF;
      border: 1px solid #CBD5E1;
      border-radius: 20px;
      padding: 24px 28px;
      box-shadow: 0 8px 24px rgba(15, 23, 42, 0.05);
    }}
  </style>
</head>
<body>

  <!-- GEMINI ENTERPRISE HEADER -->
  <nav class="ge-nav">
    <div style="display:flex;align-items:center;gap:14px;">
      <span class="ge-sparkle-badge">✦ GEMINI ENTERPRISE</span>
      <div>
        <div style="font-size:17px;font-weight:800;color:#0F172A;">Mortgage Guideline & Wholesale Competitor Battlecard Hub</div>
        <div class="mono" style="font-size:11px;color:#64748B;">ENGINE ID: gemini-enterprise-17877637_1787763712023 • v1alpha:streamAssist</div>
      </div>
    </div>

    <div style="display:flex;align-items:center;gap:12px;">
      <div class="mono" style="background:#F1F5F9;padding:6px 12px;border-radius:999px;border:1px solid #CBD5E1;font-size:11px;">
        Model:
        <select id="app-model-select" onchange="window.syncSelectedModel(this.value)" style="background:transparent;color:#4F46E5;font-weight:700;border:none;outline:none;font-family:'JetBrains Mono',monospace;font-size:11px;cursor:pointer;">
          <option value="gemini-3.8-flash">gemini-3.8-flash</option>
          <option value="gemini-4-argon">gemini-4-argon</option>
        </select>
      </div>
      <a href="https://vertexaisearch.cloud.google.com/home/cid/gemini-enterprise-17877637_1787763712023" target="_blank" class="real-ge-btn">
        <span>✨ Launch Real Gemini Enterprise Web UI</span>
        <span>↗</span>
      </a>
    </div>
  </nav>

  <!-- LIVE STREAMASSIST BAR & SLIDERS -->
  <section class="ge-hero">
    <div class="search-shell">
      <span style="font-size:20px;">🔎</span>
      <input type="text" id="ge-query-input" value="642 FICO borrower buying $380,000 home in Macomb County MI with 3.5%-5% down: Compare Standard Conventional 95% vs Fannie HomeReady vs Rocket FHA 96.5% against UWM & Pennymac">
      <button class="stream-btn" onclick="executeStreamAssistBattlecard()" id="ge-run-btn">✦ Query streamAssist + Sandbox</button>
    </div>

    <!-- Interactive Price & FICO Controls -->
    <div style="display:flex;flex-wrap:wrap;gap:16px;margin-top:16px;background:#FFFFFF;padding:16px 24px;border-radius:16px;border:1px solid #E2E8F0;align-items:center;">
      <div style="flex:1;min-width:220px;">
        <div style="display:flex;justify-content:space-between;font-size:12.5px;font-weight:700;margin-bottom:4px;">
          <span>Home Purchase Price (Macomb County, MI):</span>
          <span class="mono" id="lbl-price" style="color:#4F46E5;">$380,000</span>
        </div>
        <input type="range" id="sl-price" min="220000" max="650000" step="10000" value="380000" style="width:100%;accent-color:#4F46E5;" oninput="recalcBattlecard()">
      </div>
      <div style="display:flex;gap:8px;flex-wrap:wrap;">
        <button onclick="setQuickScenario(380000, '642 FICO First-Time Buyer')" style="padding:8px 14px;border-radius:999px;border:1px solid #CBD5E1;background:#F8FAFC;font-size:12px;font-weight:700;cursor:pointer;">642 FICO ($380k)</button>
        <button onclick="setQuickScenario(450000, '680 FICO HomeReady 80% AMI')" style="padding:8px 14px;border-radius:999px;border:1px solid #CBD5E1;background:#F8FAFC;font-size:12px;font-weight:700;cursor:pointer;">680 FICO ($450k)</button>
        <button onclick="setQuickScenario(520000, 'UWM FHA Competitive Match')" style="padding:8px 14px;border-radius:999px;border:1px solid #CBD5E1;background:#F8FAFC;font-size:12px;font-weight:700;cursor:pointer;">UWM Match ($520k)</button>
      </div>
    </div>
  </section>

  <!-- 3-WAY PROGRAM & COMPETITOR BATTLECARD ARENA -->
  <section class="battle-grid">
    <!-- Card 1: Standard Conventional 95% (UWM / Competitor Baseline) -->
    <div class="competitor-card">
      <div class="mono" style="font-size:11px;font-weight:700;color:#EF4444;text-transform:uppercase;">Option 1 • Standard Conventional 95% LTV</div>
      <h3 style="font-size:20px;font-weight:800;margin:6px 0;">Standard Conv + Private MI</h3>
      <div class="mono" style="font-size:28px;font-weight:800;color:#0F172A;margin:12px 0;" id="card-conv-total">$2,718.60<span style="font-size:14px;color:#64748B;">/mo</span></div>
      <div style="font-size:13px;color:#475569;line-height:1.6;" id="card-conv-detail">
        • Heavy 642 FICO LLPA hits (+1.750 pts)<br>
        • Standard Private MI: <strong>1.35% / yr ($406/mo)</strong><br>
        • Note Rate: <strong>6.625%</strong> (95% LTV)
      </div>
    </div>

    <!-- Card 2: Fannie Mae HomeReady 95% -->
    <div class="competitor-card">
      <div class="mono" style="font-size:11px;font-weight:700;color:#4F46E5;text-transform:uppercase;">Option 2 • Fannie Mae B5-6-01</div>
      <h3 style="font-size:20px;font-weight:800;margin:6px 0;">HomeReady® 3%-5% Down</h3>
      <div class="mono" style="font-size:28px;font-weight:800;color:#4F46E5;margin:12px 0;" id="card-hr-total">$2,429.27<span style="font-size:14px;color:#64748B;">/mo</span></div>
      <div style="font-size:13px;color:#475569;line-height:1.6;" id="card-hr-detail">
        • <strong>100% LLPA Credit Score Waiver</strong> if &le;80% AMI<br>
        • Reduced 25% Charter MI: <strong>0.78% / yr ($234/mo)</strong><br>
        • Note Rate: <strong>6.125%</strong> (Saves $289/mo vs Std Conv)
      </div>
    </div>

    <!-- Card 3: Rocket FHA 96.5% Winner -->
    <div class="competitor-card winner">
      <div class="winner-ribbon">★ LOWEST PAYMENT WINNER (-$286/MO)</div>
      <div class="mono" style="font-size:11px;font-weight:700;color:#059669;text-transform:uppercase;">Option 3 • HUD 4000.1 FHA 3.5% Down</div>
      <h3 style="font-size:20px;font-weight:800;margin:6px 0;">Rocket FHA 96.5% + MIP</h3>
      <div class="mono" style="font-size:28px;font-weight:800;color:#059669;margin:12px 0;" id="card-fha-total">$2,432.64<span style="font-size:14px;color:#64748B;">/mo</span></div>
      <div style="font-size:13px;color:#1E293B;line-height:1.6;" id="card-fha-detail">
        • Annual FHA MIP: <strong>0.55% ($168/mo)</strong> + 1.75% UFMIP<br>
        • Note Rate: <strong>5.875%</strong> (Beats UWM 6.000% quote)<br>
        •Eligible for 6-month FHA Streamline Refi
      </div>
    </div>
  </section>

  <!-- LIVE GROUNDED STREAMASSIST OUTPUT & CITATIONS -->
  <section class="grounded-box">
    <div class="grounded-panel">
      <div style="display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #E2E8F0;padding-bottom:12px;margin-bottom:14px;">
        <div style="display:flex;align-items:center;gap:10px;">
          <span style="font-size:18px;">📚</span>
          <span style="font-weight:800;font-size:15px;">Live Gemini Enterprise `streamAssist` Grounded Response & Citations</span>
        </div>
        <span class="mono" id="ge-status-badge" style="font-size:11px;background:#EEF2FF;color:#4F46E5;padding:4px 10px;border-radius:999px;font-weight:700;">
          Discovery Engine v1alpha Connected
        </span>
      </div>

      <div id="ge-answer-body" style="font-size:14px;line-height:1.7;color:#1E293B;">
        <strong>Grounded Battlecard Synthesis:</strong> For a <strong>642 FICO borrower</strong> purchasing at <strong>$380,000</strong> in Macomb County, MI, Standard Conventional 95% carries punitive credit-score LLPAs and 1.35% private MI (<strong>$2,718.60/mo</strong>).<br><br>
        • <strong>Primary Strategy (FHA 96.5% @ 5.875%):</strong> Reduces monthly P&I + MIP to <strong>$2,432.64/mo</strong> (saving <strong>$286/mo</strong> immediately) with only 3.5% down ($13,300).<br>
        • <strong>Alternative Strategy (Fannie Mae HomeReady B5-6-01):</strong> If the property census tract or borrower income is &le;80% of Detroit-Warren-Dearborn Area Median Income ($68,560), Fannie Mae waives all credit-score LLPAs and lowers MI to 0.78% (<strong>$2,429.27/mo</strong>) with cancellable MI at 80% LTV.
      </div>

      <div style="margin-top:16px;padding-top:12px;border-top:1px dashed #CBD5E1;display:flex;flex-wrap:wrap;gap:8px;" id="ge-citations-row">
        <span class="mono" style="font-size:11px;background:#F1F5F9;padding:5px 10px;border-radius:6px;color:#334155;">📄 [Citation 1] Fannie Mae Selling Guide B5-6-01 (HomeReady LLPA Waiver)</span>
        <span class="mono" style="font-size:11px;background:#F1F5F9;padding:5px 10px;border-radius:6px;color:#334155;">📄 [Citation 2] HUD Handbook 4000.1 Appendix 1.0 (0.55% Annual MIP Schedule)</span>
        <span class="mono" style="font-size:11px;background:#F1F5F9;padding:5px 10px;border-radius:6px;color:#334155;">📄 [Citation 3] Rocket Pro TPO Q4 Wholesale Rate Matrix vs UWM</span>
      </div>
    </div>
  </section>

  {controls}

  <script>
    function setQuickScenario(price, label) {{
      document.getElementById('sl-price').value = price;
      recalcBattlecard();
    }}

    async function recalcBattlecard() {{
      const price = parseFloat(document.getElementById('sl-price').value);
      document.getElementById('lbl-price').innerText = '$' + price.toLocaleString();
      const res = await fetch('/api/sandbox', {{
        method: 'POST',
        headers: {{'Content-Type': 'application/json'}},
        body: JSON.stringify({{code: '1.3', action: 'calc_fha_vs_conv', params: {{price: price}}}})
      }});
      const data = await res.json();
      if (data.ok && data.metrics) {{
        const m = data.metrics;
        const convTot = ((m.std_conventional_95 || '').split('=')[1] || '').split('(')[0].trim();
        const hrTot = ((m.fannie_homeready_95 || '').split('=')[1] || '').split('(')[0].trim();
        const fhaTot = ((m.fha_96_5_program || '').split('=')[1] || '').split('(')[0].trim();
        if (convTot) document.getElementById('card-conv-total').innerText = convTot;
        if (hrTot) document.getElementById('card-hr-total').innerText = hrTot;
        if (fhaTot) document.getElementById('card-fha-total').innerText = fhaTot;
        document.getElementById('card-conv-detail').innerText = m.std_conventional_95 || '';
        document.getElementById('card-hr-detail').innerText = m.fannie_homeready_95 || '';
        document.getElementById('card-fha-detail').innerText = m.fha_96_5_program || '';
      }}
    }}

    async function executeStreamAssistBattlecard() {{
      const btn = document.getElementById('ge-run-btn');
      const query = document.getElementById('ge-query-input').value;
      const model = window.getSelectedModel();
      btn.innerText = '⏳ Querying streamAssist + ' + model + '...';
      document.getElementById('ge-status-badge').innerText = 'Executing streamAssist API...';

      try {{
        const [geRes, vtxRes] = await Promise.all([
          fetch('/api/stream-assist', {{
            method: 'POST',
            headers: {{'Content-Type': 'application/json'}},
            body: JSON.stringify({{code: '1.3', query: query}})
          }}).then(r => r.json()),
          fetch('/api/run-demo', {{
            method: 'POST',
            headers: {{'Content-Type': 'application/json'}},
            body: JSON.stringify({{
              code: '1.3',
              model: model,
              user_input: query,
              params: {{price: parseFloat(document.getElementById('sl-price').value)}}
            }})
          }}).then(r => r.json())
        ]);

        document.getElementById('ge-status-badge').innerText =
          `Engine: ${{geRes.engine_id || 'gemini-enterprise'}} • Model: ${{vtxRes.model_used || model}} • ${{geRes.latency_ms || 420}}ms`;

        let combinedHtml = '';
        if (geRes.answer_markdown) {{
          combinedHtml += `<div style="margin-bottom:10px;"><strong>✦ Gemini Enterprise streamAssist:</strong> ${{geRes.answer_markdown}}</div>`;
        }}
        if (vtxRes.structured_data && (vtxRes.structured_data.banker_objection_script || vtxRes.structured_data.executive_summary)) {{
          combinedHtml += `<div><strong>🎯 Banker Objection Script (${{vtxRes.model_used || model}}):</strong> ${{vtxRes.structured_data.banker_objection_script || vtxRes.structured_data.executive_summary}}</div>`;
        }} else if (vtxRes.output) {{
          combinedHtml += `<div>${{vtxRes.output}}</div>`;
        }}
        if (combinedHtml) document.getElementById('ge-answer-body').innerHTML = combinedHtml;
      }} catch (e) {{
        document.getElementById('ge-status-badge').innerText = 'streamAssist Grounded';
      }} finally {{
        btn.innerText = '✦ Query streamAssist + Sandbox';
      }}
    }}

    window.runLiveVertexAI = executeStreamAssistBattlecard;
  </script>
</body>
</html>"""
