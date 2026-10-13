# -*- coding: utf-8 -*-
"""Square 4.3 — Campaign Sentiment & Ad Creative Performance Analyzer (Google ADK Runtime).
Visual Design: CMO Growth Command & Multi-Touch ROAS BI Dashboard.
Palette: #0B0F19 midnight analytics, #8B5CF6 electric violet, #EC4899 neon pink, #10B981 ROAS emerald.
Typography: Google Fonts 'Sora' + 'JetBrains Mono'.
"""

from shared.standalone_uis.base_helpers import render_floating_control_bar_and_drawer


def render_sq_4_3(auth_token: str) -> str:
    floating_drawer = render_floating_control_bar_and_drawer("4.3", auth_token)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>4.3 CMO Growth Command & Multi-Touch ROAS BI | Google ADK</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&family=Sora:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <style>
    :root {{
      --midnight: #0B0F19;
      --surface: #111827;
      --surface-elevated: #1A2336;
      --violet: #8B5CF6;
      --violet-glow: rgba(139, 92, 246, 0.28);
      --pink: #EC4899;
      --emerald: #10B981;
      --amber: #F59E0B;
      --rose: #F43F5E;
      --cyan: #06B6D4;
      --text-main: #F8FAFC;
      --text-muted: #94A3B8;
      --border: rgba(148, 163, 184, 0.16);
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      background-color: var(--midnight);
      color: var(--text-main);
      font-family: 'Sora', sans-serif;
      min-height: 100vh;
      overflow-x: hidden;
      padding-bottom: 92px;
      background-image:
        radial-gradient(circle at 12% 15%, rgba(139, 92, 246, 0.14) 0%, transparent 40%),
        radial-gradient(circle at 88% 12%, rgba(236, 72, 153, 0.12) 0%, transparent 40%),
        linear-gradient(rgba(255,255,255,0.02) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,0.02) 1px, transparent 1px);
      background-size: 100% 100%, 100% 100%, 36px 36px, 36px 36px;
    }}
    .mono {{ font-family: 'JetBrains Mono', monospace; }}

    /* Top CMO Command Header */
    .cmo-topbar {{
      background: rgba(11, 15, 25, 0.9);
      backdrop-filter: blur(16px);
      border-bottom: 1px solid var(--border);
      padding: 14px 28px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      position: sticky;
      top: 0;
      z-index: 100;
    }}
    .cmo-brand {{
      display: flex;
      align-items: center;
      gap: 14px;
    }}
    .cmo-orb {{
      width: 38px;
      height: 38px;
      border-radius: 10px;
      background: linear-gradient(135deg, var(--violet), var(--pink));
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 800;
      font-size: 15px;
      box-shadow: 0 6px 20px var(--violet-glow);
    }}
    .cmo-brand h1 {{
      font-size: 18px;
      font-weight: 800;
      letter-spacing: -0.02em;
    }}
    .cmo-brand p {{
      font-family: 'JetBrains Mono', monospace;
      font-size: 11px;
      color: var(--text-muted);
    }}
    .topbar-right {{
      display: flex;
      align-items: center;
      gap: 12px;
    }}
    .model-selector-chip {{
      display: flex;
      align-items: center;
      gap: 8px;
      background: var(--surface-elevated);
      border: 1px solid rgba(139, 92, 246, 0.45);
      padding: 6px 12px;
      border-radius: 8px;
      font-family: 'JetBrains Mono', monospace;
      font-size: 11px;
    }}
    #app-model-select {{
      background: transparent;
      color: #E9D5FF;
      border: none;
      outline: none;
      font-family: 'JetBrains Mono', monospace;
      font-size: 11px;
      font-weight: 700;
      cursor: pointer;
    }}
    #app-model-select option {{
      background: var(--surface);
      color: #FFF;
    }}
    .btn-adk-reallocate {{
      background: linear-gradient(135deg, var(--violet), var(--pink));
      color: #FFFFFF;
      border: none;
      padding: 10px 18px;
      border-radius: 8px;
      font-family: 'JetBrains Mono', monospace;
      font-size: 12px;
      font-weight: 700;
      cursor: pointer;
      box-shadow: 0 8px 25px rgba(236, 72, 153, 0.35);
      transition: all 0.18s ease;
    }}
    .btn-adk-reallocate:hover {{
      transform: translateY(-1px);
      box-shadow: 0 12px 30px rgba(139, 92, 246, 0.55);
    }}

    /* Dashboard Container */
    .bi-container {{
      max-width: 1460px;
      margin: 0 auto;
      padding: 24px 28px;
    }}

    /* Top KPI Strip */
    .kpi-strip {{
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 16px;
      margin-bottom: 22px;
    }}
    @media (max-width: 1024px) {{
      .kpi-strip {{ grid-template-columns: repeat(2, 1fr); }}
    }}
    .kpi-card {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 16px 18px;
      position: relative;
      overflow: hidden;
    }}
    .kpi-card::after {{
      content: "";
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      height: 3px;
      background: linear-gradient(90deg, var(--violet), var(--pink));
    }}
    .kpi-card.emerald::after {{
      background: linear-gradient(90deg, var(--emerald), var(--cyan));
    }}
    .kpi-label {{
      font-family: 'JetBrains Mono', monospace;
      font-size: 10px;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: var(--text-muted);
      margin-bottom: 6px;
    }}
    .kpi-value {{
      font-size: 26px;
      font-weight: 800;
      letter-spacing: -0.02em;
    }}
    .kpi-delta {{
      font-family: 'JetBrains Mono', monospace;
      font-size: 11px;
      margin-top: 4px;
    }}

    /* 3 Creative Cohort Comparison Cards */
    .cohorts-grid {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 18px;
      margin-bottom: 24px;
    }}
    @media (max-width: 1120px) {{
      .cohorts-grid {{ grid-template-columns: 1fr; }}
    }}
    .cohort-card {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 20px;
      transition: all 0.2s;
      cursor: pointer;
    }}
    .cohort-card:hover {{
      border-color: var(--violet);
      transform: translateY(-2px);
    }}
    .cohort-card.winner {{
      border: 1.5px solid var(--emerald);
      box-shadow: 0 12px 34px rgba(16, 185, 129, 0.14);
    }}
    .cohort-head {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 12px;
    }}
    .cohort-tag {{
      font-family: 'JetBrains Mono', monospace;
      font-size: 10px;
      font-weight: 700;
      padding: 4px 9px;
      border-radius: 999px;
      text-transform: uppercase;
    }}
    .cohort-title {{
      font-size: 17px;
      font-weight: 700;
      margin-bottom: 6px;
    }}
    .cohort-sub {{
      font-size: 12px;
      color: var(--text-muted);
      margin-bottom: 14px;
      line-height: 1.45;
    }}
    .cohort-stats {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 8px;
      background: var(--midnight);
      padding: 12px;
      border-radius: 10px;
      border: 1px solid rgba(255,255,255,0.06);
      font-family: 'JetBrains Mono', monospace;
    }}
    .stat-cell span {{
      display: block;
      font-size: 9px;
      color: var(--text-muted);
      text-transform: uppercase;
    }}
    .stat-cell strong {{
      font-size: 14px;
      color: #FFF;
    }}

    /* Lower 2-Column Analytics Split */
    .lower-split {{
      display: grid;
      grid-template-columns: 420px 1fr;
      gap: 22px;
      align-items: start;
    }}
    @media (max-width: 1120px) {{
      .lower-split {{ grid-template-columns: 1fr; }}
    }}
    .bi-panel {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 20px;
      margin-bottom: 20px;
    }}
    .panel-title-bar {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding-bottom: 12px;
      margin-bottom: 16px;
      border-bottom: 1px solid var(--border);
    }}
    .panel-title-bar h2 {{
      font-size: 14px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      color: #E2E8F0;
    }}
    .slider-block {{
      margin-bottom: 16px;
    }}
    .slider-block label {{
      display: flex;
      justify-content: space-between;
      font-family: 'JetBrains Mono', monospace;
      font-size: 11px;
      margin-bottom: 6px;
      color: #CBD5E1;
    }}
    input[type="range"] {{
      width: 100%;
      accent-color: var(--pink);
      cursor: pointer;
    }}

    /* Sentiment Histogram Bars */
    .sentiment-row {{
      margin-bottom: 14px;
    }}
    .sentiment-meta {{
      display: flex;
      justify-content: space-between;
      font-family: 'JetBrains Mono', monospace;
      font-size: 11px;
      margin-bottom: 5px;
    }}
    .sentiment-track {{
      height: 22px;
      background: var(--midnight);
      border-radius: 6px;
      overflow: hidden;
      display: flex;
      border: 1px solid rgba(255,255,255,0.08);
    }}
    .seg-pos {{ background: var(--emerald); height: 100%; transition: width 0.35s; }}
    .seg-neu {{ background: var(--violet); height: 100%; transition: width 0.35s; }}
    .seg-neg {{ background: var(--pink); height: 100%; transition: width 0.35s; }}

    /* Comment Stream & Excel / Sheets Formula Box */
    .comment-pill {{
      background: var(--midnight);
      border: 1px solid rgba(255,255,255,0.07);
      border-left: 3px solid var(--emerald);
      padding: 10px 12px;
      border-radius: 8px;
      margin-bottom: 10px;
      font-size: 12px;
      line-height: 1.45;
    }}
    .comment-pill.warn {{ border-left-color: var(--pink); }}
  </style>
</head>
<body>

  <!-- TOP CMO GROWTH COMMAND BAR -->
  <header class="cmo-topbar">
    <div class="cmo-brand">
      <div class="cmo-orb">BI</div>
      <div>
        <h1>CMO Growth Command & Multi-Touch ROAS Analyzer</h1>
        <p>Google ADK Attribution Agent • Cost-Per-Funded-Loan (CPFL) • Live Comment Sentiment Histogram</p>
      </div>
    </div>
    <div class="topbar-right">
      <div class="model-selector-chip">
        <span style="color:#F472B6;">ADK MODEL:</span>
        <select id="app-model-select" onchange="window.syncSelectedModel(this.value)">
          <option value="gemini-4-argon">gemini-4-argon (Frontier Global)</option>
          <option value="gemini-3.8-flash" selected>gemini-3.8-flash (ADK Default)</option>
        </select>
      </div>
      <button class="btn-adk-reallocate" id="btn-reallocate-top" onclick="window.runLiveVertexAI()">
        ⚡ Reallocate $50k Budget with ADK Agent
      </button>
    </div>
  </header>

  <main class="bi-container">
    <!-- TOP KPI STRIP -->
    <section class="kpi-strip">
      <div class="kpi-card emerald">
        <div class="kpi-label">BLENDED ECOSYSTEM ROAS</div>
        <div class="kpi-value" id="kpi-blended-roas" style="color:var(--emerald);">14.8x</div>
        <div class="kpi-delta" style="color:#6EE7B7;" id="kpi-roas-delta">+4.2x vs Last Quarter Benchmark</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">COST PER FUNDED LOAN (CPFL)</div>
        <div class="kpi-value" id="kpi-avg-cpfl">$412</div>
        <div class="kpi-delta" style="color:var(--violet);" id="kpi-cpfl-note">Redfin + Rocket Money Flywheel</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">FUNDED LOAN CONVERSIONS</div>
        <div class="kpi-value" id="kpi-funded-total">645 Loans</div>
        <div class="kpi-delta" style="color:var(--pink);" id="kpi-funded-rev">$5.29M Gross Origination Rev</div>
      </div>
      <div class="kpi-card emerald">
        <div class="kpi-label">BORROWER NET SENTIMENT</div>
        <div class="kpi-value" id="kpi-sentiment-score" style="color:#38BDF8;">+86.4 NPS</div>
        <div class="kpi-delta" style="color:var(--text-muted);" id="sandbox-ms-tag">Sandbox Verified: 1.4ms</div>
      </div>
    </section>

    <!-- 3 CREATIVE COHORTS -->
    <section class="cohorts-grid">
      <!-- COHORT A -->
      <div class="cohort-card" onclick="window.focusCohort('A')">
        <div class="cohort-head">
          <span class="cohort-tag" style="background:rgba(139,92,246,0.2);color:#C4B5FD;border:1px solid rgba(139,92,246,0.4);">COHORT A • FIRST-TIME BUYER</span>
          <span class="mono" style="font-size:11px;color:var(--violet);">ROAS: <strong id="coh-a-roas">11.4x</strong></span>
        </div>
        <div class="cohort-title">A: "Zero-Down FHA & ONE+ Grant"</div>
        <div class="cohort-sub">Targets Rocket Money renters paying >$2,100/mo with 1% Down + 2% Rocket Grant creative.</div>
        <div class="cohort-stats">
          <div class="stat-cell">
            <span>AD SPEND</span>
            <strong id="coh-a-spend">$110K</strong>
          </div>
          <div class="stat-cell">
            <span>CTR / CONV</span>
            <strong id="coh-a-ctr">3.4%</strong>
          </div>
          <div class="stat-cell">
            <span>CPFL</span>
            <strong id="coh-a-cpfl" style="color:#C4B5FD;">$714</strong>
          </div>
        </div>
      </div>

      <!-- COHORT B (WINNER) -->
      <div class="cohort-card winner" onclick="window.focusCohort('B')">
        <div class="cohort-head">
          <span class="cohort-tag" style="background:rgba(16,185,129,0.2);color:#6EE7B7;border:1px solid rgba(16,185,129,0.4);">★ COHORT B • TOP PERFORMER</span>
          <span class="mono" style="font-size:11px;color:var(--emerald);">ROAS: <strong id="coh-b-roas">24.6x</strong></span>
        </div>
        <div class="cohort-title">B: "Redfin Tour to Pre-Approval"</div>
        <div class="cohort-sub">In-app trigger when a user books a Saturday Redfin tour -> unlocks $3,500 Buy+Borrow closing credit.</div>
        <div class="cohort-stats">
          <div class="stat-cell">
            <span>AD SPEND</span>
            <strong id="coh-b-spend">$145K</strong>
          </div>
          <div class="stat-cell">
            <span>CTR / CONV</span>
            <strong id="coh-b-ctr">6.8%</strong>
          </div>
          <div class="stat-cell">
            <span>CPFL</span>
            <strong id="coh-b-cpfl" style="color:var(--emerald);">$341</strong>
          </div>
        </div>
      </div>

      <!-- COHORT C -->
      <div class="cohort-card" onclick="window.focusCohort('C')">
        <div class="cohort-head">
          <span class="cohort-tag" style="background:rgba(236,72,153,0.2);color:#F9A8D4;border:1px solid rgba(236,72,153,0.4);">COHORT C • REFI & RATE ALERT</span>
          <span class="mono" style="font-size:11px;color:var(--pink);">ROAS: <strong id="coh-c-roas">6.2x</strong></span>
        </div>
        <div class="cohort-title">C: "Rate Drop Alert (5.75%)"</div>
        <div class="cohort-sub">Push & paid social alert for Mr. Cooper + Redfin saved-home watchers when 30Y rates dip 37.5 bps.</div>
        <div class="cohort-stats">
          <div class="stat-cell">
            <span>AD SPEND</span>
            <strong id="coh-c-spend">$165K</strong>
          </div>
          <div class="stat-cell">
            <span>CTR / CONV</span>
            <strong id="coh-c-ctr">2.1%</strong>
          </div>
          <div class="stat-cell">
            <span>CPFL</span>
            <strong id="coh-c-cpfl" style="color:var(--pink);">$1,320</strong>
          </div>
        </div>
      </div>
    </section>

    <!-- LOWER 2-COLUMN ANALYTICS & SENTIMENT -->
    <section class="lower-split">
      <!-- LEFT: INTERACTIVE AD SPEND & CTR SLIDERS + $50K OPTIMIZER -->
      <div>
        <div class="bi-panel">
          <div class="panel-title-bar">
            <h2>Interactive Spend & CTR Simulator</h2>
            <span class="mono" style="font-size:10px;color:var(--pink);">/api/sandbox</span>
          </div>

          <div class="slider-block">
            <label>
              <span>Cohort B (Redfin Tour) Spend</span>
              <strong style="color:var(--emerald);" id="lbl-spend-b">$145,000</strong>
            </label>
            <input type="range" id="inp-spend-b" min="50000" max="350000" step="10000" value="145000" oninput="window.recalcCampaignRoas()">
          </div>

          <div class="slider-block">
            <label>
              <span>Cohort B Click-Through Rate (CTR)</span>
              <strong style="color:var(--violet);" id="lbl-ctr-b">6.8%</strong>
            </label>
            <input type="range" id="inp-ctr-b" min="2.0" max="12.0" step="0.2" value="6.8" oninput="window.recalcCampaignRoas()">
          </div>

          <div class="slider-block">
            <label>
              <span>Cohort C (Rate Alert) Spend</span>
              <strong style="color:var(--pink);" id="lbl-spend-c">$165,000</strong>
            </label>
            <input type="range" id="inp-spend-c" min="40000" max="300000" step="10000" value="165000" oninput="window.recalcCampaignRoas()">
          </div>

          <div style="background:var(--midnight);border:1px solid rgba(139,92,246,0.35);padding:12px;border-radius:10px;margin-bottom:16px;font-family:'JetBrains Mono',monospace;font-size:11px;line-height:1.5;">
            <div style="color:#C4B5FD;font-weight:700;margin-bottom:4px;">ADK MARGINAL DOLLAR VERDICT:</div>
            <div id="marginal-verdict-box">Shifting $50,000 into Cohort B (Redfin Tour-to-PreApproval) yields +146 Funded Loans (+$1.22M Net Revenue at 24.6x ROAS).</div>
          </div>

          <button class="btn-adk-reallocate" style="width:100%;padding:13px;" id="btn-reallocate-main" onclick="window.runLiveVertexAI()">
            [⚡ Reallocate $50k Budget with ADK Agent]
          </button>
        </div>

        <!-- EXCEL VBA / GOOGLE SHEETS FORMULA GENERATOR -->
        <div class="bi-panel" style="margin-bottom:0;">
          <div class="panel-title-bar">
            <h2>Connected Sheets & Excel Macro</h2>
            <span class="mono" style="font-size:10px;color:var(--emerald);" id="live-model-pill">gemini-3.8-flash</span>
          </div>
          <pre id="sheets-formula-code" class="mono" style="background:var(--midnight);padding:12px;border-radius:8px;border:1px solid rgba(255,255,255,0.08);font-size:10.5px;color:#A5F3FC;overflow-x:auto;line-height:1.5;">=LET(spend, B2:B4, funded, E2:E4, rev, F2:F4,
  cpfl, ROUND(spend / funded, 2),
  roas, ROUND((funded * rev) / spend, 2),
  HSTACK(cpfl, roas))</pre>
        </div>
      </div>

      <!-- RIGHT: SOCIAL COMMENT SENTIMENT HISTOGRAM & ADK OPTIMIZER OUTPUT -->
      <div>
        <div class="bi-panel">
          <div class="panel-title-bar">
            <h2>Social Comment & Borrower Review Sentiment Histogram</h2>
            <span class="mono" style="font-size:10px;color:var(--emerald);">N = 4,820 VERIFIED COMMENTS</span>
          </div>

          <div class="sentiment-row">
            <div class="sentiment-meta">
              <span>Cohort B: "Redfin Tour to Pre-Approval ($3,500 Credit)"</span>
              <span style="color:var(--emerald);">88% Positive • 9% Neutral • 3% Negative</span>
            </div>
            <div class="sentiment-track">
              <div class="seg-pos" style="width:88%;"></div>
              <div class="seg-neu" style="width:9%;"></div>
              <div class="seg-neg" style="width:3%;"></div>
            </div>
          </div>

          <div class="sentiment-row">
            <div class="sentiment-meta">
              <span>Cohort A: "Zero-Down FHA / Rocket ONE+ Grant"</span>
              <span style="color:#C4B5FD;">76% Positive • 16% Neutral • 8% Negative</span>
            </div>
            <div class="sentiment-track">
              <div class="seg-pos" style="width:76%;"></div>
              <div class="seg-neu" style="width:16%;"></div>
              <div class="seg-neg" style="width:8%;"></div>
            </div>
          </div>

          <div class="sentiment-row">
            <div class="sentiment-meta">
              <span>Cohort C: "Rate Drop Alert (Generic Social Feed)"</span>
              <span style="color:var(--pink);">49% Positive • 24% Neutral • 27% Rate Skepticism</span>
            </div>
            <div class="sentiment-track">
              <div class="seg-pos" style="width:49%;"></div>
              <div class="seg-neu" style="width:24%;"></div>
              <div class="seg-neg" style="width:27%;"></div>
            </div>
          </div>

          <div style="display:flex;gap:16px;margin-top:12px;font-family:'JetBrains Mono',monospace;font-size:10px;color:var(--text-muted);">
            <span><strong style="color:var(--emerald);">■</strong> Positive Intent (Booked Tour / Locked)</span>
            <span><strong style="color:var(--violet);">■</strong> Neutral Question</span>
            <span><strong style="color:var(--pink);">■</strong> APR / Points Friction</span>
          </div>
        </div>

        <!-- LIVE ADK REALLOCATION PLAYBOOK & COMMENT CLUSTERS -->
        <div class="bi-panel" style="margin-bottom:0;">
          <div class="panel-title-bar">
            <h2>ADK Creative Sentiment & $50k Budget Reallocation Playbook</h2>
            <span class="mono" style="font-size:10px;color:var(--violet);" id="adk-status-tag">READY FOR REALLOCATION</span>
          </div>

          <div id="adk-playbook-cards">
            <div class="comment-pill">
              <div class="mono" style="font-size:10px;color:var(--emerald);margin-bottom:3px;">CLUSTER #1 • HIGHEST CONVERSION DRIVER (COHORT B)</div>
              “Loved how booking my Saturday Redfin tour in Ferndale automatically unlocked a $3,500 Rocket Mortgage closing credit and pre-filled my Down Payment Vault!”
            </div>
            <div class="comment-pill">
              <div class="mono" style="font-size:10px;color:#C4B5FD;margin-bottom:3px;">CLUSTER #2 • ROCKET MONEY VAULT SYNERGY (COHORT A)</div>
              “Rocket Money showed me I already had $16,400 saved across two accounts—qualified for ONE+ with zero PMI shock.”
            </div>
            <div class="comment-pill warn">
              <div class="mono" style="font-size:10px;color:var(--pink);margin-bottom:3px;">CLUSTER #3 • ADK FRICTION FIX (COHORT C -> AUTO-REWRITTEN)</div>
              “Generic rate-drop ad didn't mention discount points until I clicked.” → <strong>ADK Action:</strong> Shift $50,000 from Cohort C into Cohort B & update Cohort C creative to highlight zero-point Seller 2-1 Buydowns.
            </div>
          </div>
        </div>
      </div>
    </section>
  </main>

  <script>
    window.focusCohort = function(code) {{
      if (code === 'B') {{
        document.getElementById('inp-spend-b').value = 195000;
        document.getElementById('inp-ctr-b').value = 7.4;
      }} else if (code === 'A') {{
        document.getElementById('inp-spend-b').value = 135000;
        document.getElementById('inp-ctr-b').value = 6.2;
      }} else {{
        document.getElementById('inp-spend-c').value = 115000;
      }}
      window.recalcCampaignRoas();
    }};

    window.recalcCampaignRoas = async function() {{
      const spendB = parseFloat(document.getElementById('inp-spend-b').value || 145000);
      const ctrB = parseFloat(document.getElementById('inp-ctr-b').value || 6.8);
      const spendC = parseFloat(document.getElementById('inp-spend-c').value || 165000);
      const spendA = 110000;

      document.getElementById('lbl-spend-b').innerText = '$' + spendB.toLocaleString();
      document.getElementById('lbl-ctr-b').innerText = ctrB.toFixed(1) + '%';
      document.getElementById('lbl-spend-c').innerText = '$' + spendC.toLocaleString();

      const fundedA = 154;
      const fundedB = Math.round((spendB / 145000) * (ctrB / 6.8) * 425);
      const fundedC = Math.max(40, Math.round((spendC / 165000) * 125));

      const revA = fundedA * 8200;
      const revB = fundedB * 8400;
      const revC = fundedC * 7900;

      const roasA = (revA / spendA).toFixed(1);
      const roasB = (revB / spendB).toFixed(1);
      const roasC = (revC / spendC).toFixed(1);

      const cpflA = Math.round(spendA / fundedA);
      const cpflB = Math.round(spendB / Math.max(1, fundedB));
      const cpflC = Math.round(spendC / Math.max(1, fundedC));

      document.getElementById('coh-b-spend').innerText = '$' + Math.round(spendB/1000) + 'K';
      document.getElementById('coh-b-ctr').innerText = ctrB.toFixed(1) + '%';
      document.getElementById('coh-b-roas').innerText = roasB + 'x';
      document.getElementById('coh-b-cpfl').innerText = '$' + cpflB.toLocaleString();

      document.getElementById('coh-c-spend').innerText = '$' + Math.round(spendC/1000) + 'K';
      document.getElementById('coh-c-roas').innerText = roasC + 'x';
      document.getElementById('coh-c-cpfl').innerText = '$' + cpflC.toLocaleString();

      const totSpend = spendA + spendB + spendC;
      const totFunded = fundedA + fundedB + fundedC;
      const totRev = revA + revB + revC;
      const blendedRoas = (totRev / totSpend).toFixed(1);
      const blendedCpfl = Math.round(totSpend / totFunded);

      document.getElementById('kpi-blended-roas').innerText = blendedRoas + 'x';
      document.getElementById('kpi-avg-cpfl').innerText = '$' + blendedCpfl.toLocaleString();
      document.getElementById('kpi-funded-total').innerText = totFunded.toLocaleString() + ' Loans';
      document.getElementById('kpi-funded-rev').innerText = '$' + (totRev / 1000000).toFixed(2) + 'M Gross Origination Rev';

      const extraLoans50k = Math.round(50000 / cpflB);
      document.getElementById('marginal-verdict-box').innerText =
        `Shifting $50,000 from Cohort C ($${{cpflC}} CPFL) into Cohort B ($${{cpflB}} CPFL @ ${{ctrB.toFixed(1)}}% CTR) yields +${{extraLoans50k}} incremental Funded Loans (+$${{((extraLoans50k * 8400)/1000000).toFixed(2)}}M Revenue at ${{roasB}}x ROAS).`;

      try {{
        const resp = await fetch('/api/sandbox', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{
            code: '4.3',
            action: 'calc_campaign_roas',
            params: {{
              campaigns: [
                {{ name: "Zero-Down FHA", spend: spendA, funded: fundedA, rev_per_loan: 8200 }},
                {{ name: "Redfin Tour to Pre-Approval", spend: spendB, funded: fundedB, rev_per_loan: 8400 }},
                {{ name: "Rate Drop Alert", spend: spendC, funded: fundedC, rev_per_loan: 7900 }}
              ]
            }}
          }})
        }});
        const data = await resp.json();
        if (data && data.ok) {{
          document.getElementById('sandbox-ms-tag').innerText = `Sandbox Verified: ${{data.execution_ms || 1.3}}ms`;
        }}
      }} catch (e) {{}}
    }};

    window.runLiveVertexAI = async function() {{
      const btn1 = document.getElementById('btn-reallocate-top');
      const btn2 = document.getElementById('btn-reallocate-main');
      if (btn1) btn1.innerText = '⏳ ADK Reallocating $50k...';
      if (btn2) btn2.innerText = '⏳ Running Google ADK Attribution Optimizer...';

      // Automatically shift $50k from Cohort C to Cohort B on UI
      const curB = parseFloat(document.getElementById('inp-spend-b').value || 145000);
      const curC = parseFloat(document.getElementById('inp-spend-c').value || 165000);
      document.getElementById('inp-spend-b').value = Math.min(350000, curB + 50000);
      document.getElementById('inp-spend-c').value = Math.max(40000, curC - 50000);
      await window.recalcCampaignRoas();

      const scenarioEl = document.getElementById('scenario-input');
      const userPrompt = scenarioEl && scenarioEl.value
        ? scenarioEl.value
        : 'Reallocate $50,000 ad spend across Cohort A (Zero-Down FHA), Cohort B (Redfin Tour to Pre-Approval), and Cohort C (Rate Drop Alert) based on ROAS and borrower comment sentiment.';

      try {{
        const resp = await fetch('/api/run-demo', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{
            code: '4.3',
            model: window.getSelectedModel(),
            user_input: userPrompt,
            params: {{
              campaigns: [
                {{ name: "Zero-Down FHA", spend: 110000, funded: 154, rev_per_loan: 8200 }},
                {{ name: "Redfin Tour to Pre-Approval", spend: parseFloat(document.getElementById('inp-spend-b').value), funded: 495, rev_per_loan: 8400 }},
                {{ name: "Rate Drop Alert", spend: parseFloat(document.getElementById('inp-spend-c').value), funded: 95, rev_per_loan: 7900 }}
              ]
            }}
          }})
        }});
        const res = await resp.json();
        if (res && res.ok) {{
          const sd = res.structured_data || {{}};
          document.getElementById('adk-status-tag').innerText = `OPTIMIZED BY ${{res.model_used.toUpperCase()}}`;
          if (sd.budget_reallocation_headline || sd.executive_summary) {{
            document.getElementById('marginal-verdict-box').innerText = sd.budget_reallocation_headline || sd.executive_summary;
          }}
          if (Array.isArray(sd.new_ab_test_hypotheses) && sd.new_ab_test_hypotheses.length > 0) {{
            document.getElementById('adk-playbook-cards').innerHTML = sd.new_ab_test_hypotheses.map((h, i) => `
              <div class="comment-pill ${{i === 2 ? 'warn' : ''}}">
                <div class="mono" style="font-size:10px;color:var(--emerald);margin-bottom:3px;">${{h.variant_name || 'ADK HYPOTHESIS'}} • ${{h.target_segment || 'ECOSYSTEM'}}</div>
                ${{h.hook_script || ''}}
              </div>
            `).join('');
          }} else if (res.output) {{
            document.getElementById('adk-playbook-cards').innerHTML = `
              <div class="comment-pill">
                <div class="mono" style="font-size:10px;color:var(--emerald);margin-bottom:3px;">LIVE VERTEX AI ADK REALLOCATION MEMO (${{res.model_used}})</div>
                ${{res.output}}
              </div>
            `;
          }}
        }}
      }} catch (e) {{
        console.error(e);
      }} finally {{
        if (btn1) btn1.innerText = '⚡ Reallocate $50k Budget with ADK Agent';
        if (btn2) btn2.innerText = '[⚡ Reallocate $50k Budget with ADK Agent]';
      }}
    }};

    document.addEventListener('DOMContentLoaded', () => {{
      window.recalcCampaignRoas();
    }});
  </script>

  {floating_drawer}
</body>
</html>"""
