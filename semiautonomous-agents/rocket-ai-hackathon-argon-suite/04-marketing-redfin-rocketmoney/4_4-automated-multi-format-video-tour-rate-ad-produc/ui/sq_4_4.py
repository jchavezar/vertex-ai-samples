# -*- coding: utf-8 -*-
"""Square 4.4 — Ad Copy & Fair-Lending Guardrail (Figma / Notion Light Creative Marketing Campaign Review Studio).
Visual Design: Figma / Notion Light Creative Marketing Campaign Review Studio.
Palette: #FFFFFF clean white canvas, #F3F4F6 light studio sidebar, #2563EB review blue, #16A34A ECOA approved green, #DC2626 flagged phrase red.
Typography: Google Fonts 'Plus Jakarta Sans'.
"""

from shared.standalone_uis.base_helpers import render_floating_control_bar_and_drawer


def render_sq_4_4(auth_token: str) -> str:
    floating_drawer = render_floating_control_bar_and_drawer("4.4", auth_token)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Ad Copy & Fair-Lending Guardrail | Figma × Notion Creative Compliance Studio</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <style>
    :root {{
      --canvas-white: #FFFFFF;
      --sidebar-gray: #F3F4F6;
      --surface-soft: #F9FAFB;
      --border-light: #E5E7EB;
      --border-medium: #D1D5DB;
      --review-blue: #2563EB;
      --review-blue-dark: #1D4ED8;
      --review-blue-soft: #EFF6FF;
      --ecoa-green: #16A34A;
      --ecoa-green-soft: #DCFCE7;
      --flag-red: #DC2626;
      --flag-red-soft: #FEE2E2;
      --amber-warn: #D97706;
      --amber-soft: #FEF3C7;
      --text-main: #111827;
      --text-muted: #4B5563;
      --text-subtle: #6B7280;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      background-color: var(--canvas-white);
      color: var(--text-main);
      font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
      min-height: 100vh;
      overflow-x: hidden;
      padding-bottom: 96px;
      line-height: 1.5;
    }}

    /* Top Figma / Notion Studio Toolbar */
    .studio-toolbar {{
      background: var(--canvas-white);
      border-bottom: 1px solid var(--border-light);
      position: sticky;
      top: 0;
      z-index: 100;
      padding: 11px 22px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 14px;
      flex-wrap: wrap;
    }}
    .toolbar-left {{
      display: flex;
      align-items: center;
      gap: 12px;
    }}
    .figma-badge {{
      background: var(--review-blue);
      color: #FFFFFF;
      font-weight: 800;
      font-size: 13px;
      padding: 6px 12px;
      border-radius: 8px;
      display: inline-flex;
      align-items: center;
      gap: 6px;
    }}
    .workspace-crumb {{
      font-size: 13.5px;
      font-weight: 700;
      color: var(--text-main);
      display: flex;
      align-items: center;
      gap: 8px;
    }}
    .status-compliance-pill {{
      font-size: 11.5px;
      font-weight: 800;
      padding: 4px 10px;
      border-radius: 999px;
      display: inline-flex;
      align-items: center;
      gap: 6px;
    }}
    .status-compliance-pill.flagged {{
      background: var(--flag-red-soft);
      color: var(--flag-red);
      border: 1px solid #FCA5A5;
    }}
    .status-compliance-pill.approved {{
      background: var(--ecoa-green-soft);
      color: var(--ecoa-green);
      border: 1px solid #86EFAC;
    }}

    .toolbar-right {{
      display: flex;
      align-items: center;
      gap: 10px;
      flex-wrap: wrap;
    }}
    .model-select-wrap {{
      display: flex;
      align-items: center;
      gap: 6px;
      background: var(--sidebar-gray);
      border: 1px solid var(--border-light);
      padding: 6px 10px;
      border-radius: 8px;
      font-size: 12px;
      font-weight: 600;
    }}
    #app-model-select {{
      border: none;
      background: transparent;
      font-family: inherit;
      font-size: 12px;
      font-weight: 700;
      color: var(--review-blue);
      outline: none;
      cursor: pointer;
    }}
    .btn-blue {{
      background: var(--review-blue);
      color: #FFFFFF;
      border: none;
      border-radius: 8px;
      padding: 8px 15px;
      font-family: inherit;
      font-size: 12.5px;
      font-weight: 700;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 7px;
      transition: background 0.15s ease;
    }}
    .btn-blue:hover {{
      background: var(--review-blue-dark);
    }}
    .btn-green {{
      background: var(--ecoa-green);
      color: #FFFFFF;
      border: none;
      border-radius: 8px;
      padding: 8px 15px;
      font-family: inherit;
      font-size: 12.5px;
      font-weight: 700;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 7px;
      transition: opacity 0.15s ease;
    }}
    .btn-green:hover {{
      opacity: 0.92;
    }}
    .btn-secondary {{
      background: var(--canvas-white);
      color: var(--text-main);
      border: 1px solid var(--border-medium);
      border-radius: 8px;
      padding: 8px 13px;
      font-family: inherit;
      font-size: 12.5px;
      font-weight: 600;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 6px;
    }}
    .btn-secondary:hover {{
      background: var(--sidebar-gray);
    }}

    /* Studio Layout: Left Sidebar + Center Canvas + Right Redline Inspector */
    .studio-workspace {{
      display: grid;
      grid-template-columns: 270px 1fr 390px;
      min-height: calc(100vh - 58px);
    }}
    @media (max-width: 1180px) {{
      .studio-workspace {{ grid-template-columns: 1fr; }}
    }}

    /* Left Studio Sidebar (#F3F4F6) */
    .studio-sidebar {{
      background: var(--sidebar-gray);
      border-right: 1px solid var(--border-light);
      padding: 18px 16px;
      display: flex;
      flex-direction: column;
      gap: 18px;
    }}
    .sidebar-section-label {{
      font-size: 11px;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      color: var(--text-subtle);
      margin-bottom: 8px;
    }}
    .campaign-preset-btn {{
      width: 100%;
      text-align: left;
      background: var(--canvas-white);
      border: 1px solid var(--border-light);
      border-radius: 10px;
      padding: 11px 12px;
      margin-bottom: 8px;
      cursor: pointer;
      font-family: inherit;
      transition: all 0.15s ease;
    }}
    .campaign-preset-btn:hover {{
      border-color: var(--review-blue);
    }}
    .campaign-preset-btn.active {{
      border: 2px solid var(--review-blue);
      background: var(--review-blue-soft);
    }}
    .preset-title {{
      font-size: 13px;
      font-weight: 700;
      color: var(--text-main);
    }}
    .preset-sub {{
      font-size: 11.5px;
      color: var(--text-muted);
      margin-top: 2px;
    }}

    .statute-checklist {{
      background: var(--canvas-white);
      border: 1px solid var(--border-light);
      border-radius: 10px;
      padding: 12px;
      font-size: 12px;
      display: flex;
      flex-direction: column;
      gap: 8px;
    }}
    .statute-item {{
      display: flex;
      align-items: flex-start;
      gap: 8px;
      color: var(--text-muted);
    }}

    /* Center Multi-Channel Ad Preview Board (#FFFFFF) */
    .studio-canvas {{
      background: var(--canvas-white);
      padding: 22px 26px;
    }}
    .canvas-header {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      margin-bottom: 18px;
      flex-wrap: wrap;
    }}
    .ad-preview-grid {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 18px;
      margin-bottom: 22px;
    }}
    @media (max-width: 960px) {{
      .ad-preview-grid {{ grid-template-columns: 1fr; }}
    }}

    .channel-card {{
      background: var(--surface-soft);
      border: 1px solid var(--border-light);
      border-radius: 14px;
      overflow: hidden;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      box-shadow: 0 4px 12px rgba(17, 24, 39, 0.03);
    }}
    .channel-card-top {{
      background: var(--sidebar-gray);
      padding: 10px 14px;
      border-bottom: 1px solid var(--border-light);
      display: flex;
      align-items: center;
      justify-content: space-between;
      font-size: 12px;
      font-weight: 700;
      color: var(--text-main);
    }}
    .channel-body {{
      padding: 16px;
      flex: 1;
      display: flex;
      flex-direction: column;
      gap: 10px;
      background: var(--canvas-white);
    }}
    .channel-visual-banner {{
      height: 96px;
      border-radius: 8px;
      background: linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%);
      border: 1px solid #BFDBFE;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 10px;
      text-align: center;
      font-weight: 800;
      font-size: 13px;
      color: var(--review-blue-dark);
    }}
    .ad-copy-rendered {{
      font-size: 13.5px;
      color: var(--text-main);
      line-height: 1.55;
    }}
    .flagged-span {{
      background: var(--flag-red-soft);
      color: var(--flag-red);
      border-bottom: 2px wavy var(--flag-red);
      font-weight: 700;
      padding: 1px 4px;
      border-radius: 4px;
    }}
    .approved-span {{
      background: var(--ecoa-green-soft);
      color: var(--ecoa-green);
      font-weight: 700;
      padding: 1px 5px;
      border-radius: 4px;
    }}
    .channel-footer {{
      padding: 10px 14px;
      background: var(--surface-soft);
      border-top: 1px solid var(--border-light);
      font-size: 11px;
      color: var(--text-subtle);
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}

    /* Live Editor & Audio Bar */
    .copy-editor-panel {{
      background: var(--surface-soft);
      border: 1px solid var(--border-light);
      border-radius: 12px;
      padding: 16px 18px;
    }}
    .copy-textarea {{
      width: 100%;
      border: 1px solid var(--border-medium);
      border-radius: 8px;
      padding: 11px 13px;
      font-family: inherit;
      font-size: 13.5px;
      color: var(--text-main);
      background: var(--canvas-white);
      line-height: 1.55;
      margin-top: 8px;
      resize: vertical;
    }}
    .copy-textarea:focus {{
      outline: none;
      border-color: var(--review-blue);
    }}

    /* Right Redline Scanner Column */
    .redline-inspector {{
      background: var(--sidebar-gray);
      border-left: 1px solid var(--border-light);
      padding: 18px;
      display: flex;
      flex-direction: column;
      gap: 14px;
    }}
    .scanner-score-card {{
      background: var(--canvas-white);
      border: 1px solid var(--border-light);
      border-radius: 12px;
      padding: 16px;
    }}
    .violation-card {{
      background: var(--canvas-white);
      border: 1px solid #FCA5A5;
      border-left: 4px solid var(--flag-red);
      border-radius: 10px;
      padding: 12px 14px;
      font-size: 12.5px;
    }}
    .violation-card.resolved {{
      border-color: #86EFAC;
      border-left-color: var(--ecoa-green);
    }}
    .violation-phrase {{
      font-weight: 800;
      color: var(--flag-red);
      font-size: 13px;
    }}
    .violation-card.resolved .violation-phrase {{
      color: var(--ecoa-green);
    }}
    .violation-law {{
      font-size: 11px;
      font-weight: 700;
      color: var(--review-blue);
      margin-top: 3px;
    }}
    .violation-fix {{
      font-size: 12px;
      color: var(--text-muted);
      margin-top: 5px;
    }}

    .ai-compliance-memo {{
      background: var(--canvas-white);
      border: 1px solid var(--border-light);
      border-top: 3px solid var(--review-blue);
      border-radius: 10px;
      padding: 14px;
      font-size: 12.5px;
      line-height: 1.55;
      white-space: pre-wrap;
    }}
  </style>
</head>
<body>

  <!-- Top Figma / Notion Studio Toolbar -->
  <header class="studio-toolbar">
    <div class="toolbar-left">
      <div class="figma-badge">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.3">
          <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
        </svg>
        FAIR-LENDING STUDIO
      </div>
      <div class="workspace-crumb">
        <span>Rocket &times; Redfin Q4 Campaign Board</span>
        <span id="top-compliance-badge" class="status-compliance-pill flagged">
          &#9888; 4 ECOA / FHA Phrases Flagged
        </span>
      </div>
    </div>

    <div class="toolbar-right">
      <div class="model-select-wrap">
        <span>Compliance Model:</span>
        <select id="app-model-select" onchange="window.syncSelectedModel(this.value)">
          <option value="gemini-4-argon">Gemini 4 Argon (Frontier)</option>
          <option value="gemini-3.8-flash">Gemini 3.8 Flash (Fast)</option>
        </select>
      </div>

      <button class="btn-green" onclick="window.autoRewriteCompliantCampaign()">
        &#10003; Auto-Rewrite Compliant Campaign
      </button>

      <button class="btn-blue" id="btn-hear-compliant" onclick="window.hearCompliantAdReadout(this)">
        🔊 Hear Compliant Ad Readout (Gemini 3.8 Live)
      </button>

      <button class="btn-secondary" onclick="window.runLiveVertexAI()">
        Run Full Legal Memo
      </button>
    </div>
  </header>

  <div class="studio-workspace">
    <!-- Left Studio Sidebar (#F3F4F6) -->
    <aside class="studio-sidebar">
      <div>
        <div class="sidebar-section-label">Campaign Drafts in Review</div>
        <button class="campaign-preset-btn active" id="preset-btn-0" onclick="window.loadCampaignPreset(0)">
          <div class="preset-title">1. Royal Oak Starter Home Promo</div>
          <div class="preset-sub">Flags: Familial status &amp; age targeting</div>
        </button>
        <button class="campaign-preset-btn" id="preset-btn-1" onclick="window.loadCampaignPreset(1)">
          <div class="preset-title">2. Downtown Detroit Loft Refi</div>
          <div class="preset-sub">Flags: Income source &amp; disability phrasing</div>
        </button>
        <button class="campaign-preset-btn" id="preset-btn-2" onclick="window.loadCampaignPreset(2)">
          <div class="preset-title">3. Suburban Move-Up Co-Brand</div>
          <div class="preset-sub">Flags: Exclusive neighborhood steering</div>
        </button>
      </div>

      <div>
        <div class="sidebar-section-label">Statutory Guardrails Active</div>
        <div class="statute-checklist">
          <div class="statute-item">
            <strong style="color:var(--review-blue);">ECOA Reg B</strong>
            <span>12 CFR § 1002.4(b) — Prohibits discouraging applicants on age, marital status, or public assistance.</span>
          </div>
          <div class="statute-item">
            <strong style="color:var(--review-blue);">Fair Housing</strong>
            <span>42 U.S.C. § 3604(c) — Bars ad copy indicating preference on familial status, religion, disability, or national origin.</span>
          </div>
          <div class="statute-item">
            <strong style="color:var(--review-blue);">UDAAP / TILA</strong>
            <span>Requires representative APR disclosure alongside triggered promotional rates.</span>
          </div>
        </div>
      </div>

      <button class="btn-secondary" style="width:100%;justify-content:center;" onclick="window.resetToFlaggedDraft()">
        &#8635; Reset to Unedited Draft (Show Redlines)
      </button>
    </aside>

    <!-- Center Multi-Channel Ad Preview Board (#FFFFFF) -->
    <main class="studio-canvas">
      <div class="canvas-header">
        <div>
          <h1 style="font-size:20px;font-weight:800;color:var(--text-main);">Multi-Channel Ad Preview Board</h1>
          <p style="font-size:12.5px;color:var(--text-muted);">
            Live redline highlights prohibited demographic targeting phrases across Instagram Story, Google Search, and Redfin Postcard formats.
          </p>
        </div>
        <div style="display:flex;gap:8px;">
          <button class="btn-green" onclick="window.autoRewriteCompliantCampaign()">
            Auto-Rewrite Compliant Campaign
          </button>
        </div>
      </div>

      <!-- 3 Multi-Channel Ad Cards -->
      <section class="ad-preview-grid">
        <!-- Channel 1: Instagram Story Card -->
        <div class="channel-card">
          <div class="channel-card-top">
            <span>Instagram Story Card (9:16)</span>
            <span id="ch1-badge" style="color:var(--flag-red);">Redline Alert</span>
          </div>
          <div class="channel-body">
            <div class="channel-visual-banner" id="ch1-banner">
              Redfin &times; Rocket Mortgage · 418 Elmhurst Ave, Royal Oak
            </div>
            <div style="font-size:11px;font-weight:800;color:var(--review-blue);text-transform:uppercase;">Story Primary Hook</div>
            <div class="ad-copy-rendered" id="ch1-copy"></div>
          </div>
          <div class="channel-footer">
            <span>Equal Housing Lender · NMLS #3030</span>
            <span>CTA: Get Pre-Approved</span>
          </div>
        </div>

        <!-- Channel 2: Google Search Ad Preview -->
        <div class="channel-card">
          <div class="channel-card-top">
            <span>Google Search Ad Preview</span>
            <span id="ch2-badge" style="color:var(--flag-red);">Redline Alert</span>
          </div>
          <div class="channel-body">
            <div style="font-size:11px;color:var(--text-subtle);">Sponsored · rocketmortgage.com/redfin-offer</div>
            <div style="font-size:15px;font-weight:800;color:var(--review-blue);" id="ch2-headline">
              Rocket Mortgage® Official | Royal Oak 3.5% Down Options
            </div>
            <div class="ad-copy-rendered" id="ch2-copy"></div>
          </div>
          <div class="channel-footer">
            <span>Rep. APR 6.125% Disclosed</span>
            <span>Ad Strength: High</span>
          </div>
        </div>

        <!-- Channel 3: Redfin Co-Branded Postcard -->
        <div class="channel-card">
          <div class="channel-card-top">
            <span>Redfin Co-Branded Postcard</span>
            <span id="ch3-badge" style="color:var(--flag-red);">Redline Alert</span>
          </div>
          <div class="channel-body">
            <div class="channel-visual-banner" style="background:linear-gradient(135deg,#FEF2F2 0%,#FEE2E2 100%);border-color:#FECACA;color:#991B1B;">
              Direct Mail 6&times;9 Postcard · ZIP 48067 &amp; 48220
            </div>
            <div style="font-size:11px;font-weight:800;color:#991B1B;text-transform:uppercase;">Postcard Body Copy</div>
            <div class="ad-copy-rendered" id="ch3-copy"></div>
          </div>
          <div class="channel-footer">
            <span>HUD Equal Housing Opportunity Logo</span>
            <span>QR Pre-Approval Link</span>
          </div>
        </div>
      </section>

      <!-- Live Unified Ad Copy Editor -->
      <section class="copy-editor-panel">
        <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:10px;">
          <div>
            <div style="font-size:14px;font-weight:800;color:var(--text-main);">
              Live Campaign Master Copy Editor (Type or Click Auto-Rewrite to Test Guardrail)
            </div>
            <div style="font-size:12px;color:var(--text-muted);">
              Scanner checks in real time for phrases like <code>"young couples"</code>, <code>"empty nesters"</code>, <code>"able-bodied"</code>, <code>"stable W-2 earners"</code>, or <code>"exclusive neighborhood"</code>.
            </div>
          </div>
          <button class="btn-blue" onclick="window.hearCompliantAdReadout(document.getElementById('btn-hear-compliant'))">
            🔊 Hear Compliant Ad Readout (Gemini 3.8 Live)
          </button>
        </div>
        <textarea id="master-copy-textarea" class="copy-textarea" rows="3" oninput="window.scanMasterCopy()"></textarea>
      </section>
    </main>

    <!-- Right Column: Live ECOA / Fair Housing Redline Scanner -->
    <aside class="redline-inspector">
      <div class="scanner-score-card">
        <div style="display:flex;align-items:center;justify-content:space-between;">
          <span style="font-size:12px;font-weight:800;text-transform:uppercase;color:var(--text-subtle);">
            ECOA &amp; Fair Housing Audit
          </span>
          <span id="inspector-score-pill" style="font-size:12px;font-weight:800;color:var(--flag-red);">
            HOLD FOR REVISION
          </span>
        </div>
        <div style="font-size:24px;font-weight:800;margin-top:4px;" id="inspector-headline">
          4 Prohibited Phrases Detected
        </div>
        <div style="font-size:12px;color:var(--text-muted);margin-top:2px;" id="inspector-sub">
          Click "Auto-Rewrite Compliant Campaign" to replace demographic descriptors with objective property &amp; loan terms.
        </div>
      </div>

      <div id="violations-list" style="display:flex;flex-direction:column;gap:10px;"></div>

      <div class="ai-compliance-memo" id="vertex-ai-output">
        <strong>Legal &amp; Fair-Lending Counsel Ready:</strong> Click <em>"Run Full Legal Memo"</em> or <em>"Re-Synthesize with Selected Model"</em> to generate a formal CFPB/HUD compliance sign-off memo with <span id="live-model-pill">gemini-4-argon</span>.
      </div>
    </aside>
  </div>

  <script>
    const PROHIBITED_RULES = [
      {{
        phrase: "perfect for young couples",
        replacement: "featuring 4 bedrooms and a flexible home office layout",
        law: "Fair Housing Act 42 U.S.C. § 3604(c) & ECOA Age/Familial Status",
        reason: "Expresses preference based on age and marital/familial status; describe physical house features instead."
      }},
      {{
        phrase: "empty nesters",
        replacement: "buyers seeking single-level main-floor living",
        law: "ECOA Reg B (12 CFR § 1002.4) & FHA Familial Status",
        reason: "Age and familial status proxy; replace with architectural layout description."
      }},
      {{
        phrase: "exclusive neighborhood",
        replacement: "walkable Vinsetta Park historic district near public transit",
        law: "HUD Fair Housing Advertising Guidelines (24 CFR § 100.75)",
        reason: "Implies exclusionary steering; describe objective neighborhood amenities and transit access."
      }},
      {{
        phrase: "stable W-2 earners",
        replacement: "qualified applicants (including self-employed, 1099, retirement, or public assistance income)",
        law: "ECOA Reg B 12 CFR § 1002.6(b)(5) Protected Income Sources",
        reason: "Discourages applicants receiving public assistance, alimony, retirement, or 1099 income."
      }},
      {{
        phrase: "able-bodied buyers",
        replacement: "all homebuyers, with step-free patio access",
        law: "Fair Housing Act 42 U.S.C. § 3604(f) Disability Protection",
        reason: "Directly discriminates against persons with disabilities; describe objective accessibility features."
      }}
    ];

    const CAMPAIGN_PRESETS = [
      {{
        name: "Royal Oak Starter Home Promo",
        flaggedCopy: "Tour 418 Elmhurst Ave in Royal Oak—an exclusive neighborhood cottage that is perfect for young couples or empty nesters! Fast Rocket Mortgage pre-approval for stable W-2 earners at 6.125% APR.",
        compliantCopy: "Tour 418 Elmhurst Ave in Royal Oak—a walkable Vinsetta Park historic district home featuring 4 bedrooms and a flexible home office layout or buyers seeking single-level main-floor living! Fast Rocket Mortgage pre-approval for qualified applicants (including self-employed, 1099, retirement, or public assistance income) at 6.125% APR (30-Yr Fixed, Equal Housing Lender)."
      }},
      {{
        name: "Downtown Detroit Loft Refi",
        flaggedCopy: "Upgrade to a Corktown brick loft—ideal for able-bodied buyers and young couples looking for an exclusive neighborhood with fast Rocket Mortgage approval for stable W-2 earners.",
        compliantCopy: "Upgrade to a Corktown brick loft—welcoming all homebuyers, with step-free patio access and featuring 4 bedrooms and a flexible home office layout in a walkable historic district with fast Rocket Mortgage approval for qualified applicants (including self-employed, 1099, retirement, or public assistance income) at 6.125% APR."
      }},
      {{
        name: "Suburban Move-Up Co-Brand",
        flaggedCopy: "Downsizing for empty nesters or upsizing in an exclusive neighborhood? Lock in a 6.125% rate with Rocket Mortgage—tailored for stable W-2 earners.",
        compliantCopy: "Exploring homes for buyers seeking single-level main-floor living or spacious 4-bedroom layouts in a walkable Vinsetta Park historic district near public transit? Lock in a 6.125% APR (30-Yr Fixed) with Rocket Mortgage—available for qualified applicants (including self-employed, 1099, retirement, or public assistance income)."
      }}
    ];

    let activePresetIdx = 0;

    window.loadCampaignPreset = function(idx) {{
      activePresetIdx = idx;
      for (let i = 0; i < 3; i++) {{
        const btn = document.getElementById('preset-btn-' + i);
        if (btn) btn.classList.toggle('active', i === idx);
      }}
      const textarea = document.getElementById('master-copy-textarea');
      if (textarea) {{
        textarea.value = CAMPAIGN_PRESETS[idx].flaggedCopy;
      }}
      window.scanMasterCopy();
    }};

    window.resetToFlaggedDraft = function() {{
      window.loadCampaignPreset(activePresetIdx);
    }};

    window.autoRewriteCompliantCampaign = function() {{
      const textarea = document.getElementById('master-copy-textarea');
      if (!textarea) return;
      let text = textarea.value;
      let replacedAny = false;
      PROHIBITED_RULES.forEach(rule => {{
        const regex = new RegExp(rule.phrase, 'gi');
        if (regex.test(text)) {{
          text = text.replace(regex, rule.replacement);
          replacedAny = true;
        }}
      }});
      if (!replacedAny) {{
        text = CAMPAIGN_PRESETS[activePresetIdx].compliantCopy;
      }}
      textarea.value = text;
      window.scanMasterCopy();
    }};

    window.scanMasterCopy = function() {{
      const textarea = document.getElementById('master-copy-textarea');
      const rawText = textarea ? textarea.value : "";

      let highlightedHtml = rawText
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;");

      let detectedViolations = [];

      PROHIBITED_RULES.forEach(rule => {{
        const regex = new RegExp('(' + rule.phrase + ')', 'gi');
        if (regex.test(rawText)) {{
          detectedViolations.push(rule);
          highlightedHtml = highlightedHtml.replace(regex, '<span class="flagged-span">$1</span>');
        }} else if (rawText.toLowerCase().includes(rule.replacement.toLowerCase())) {{
          const repRegex = new RegExp('(' + rule.replacement.replace(/[.*+?^${{}}()|[\\]\\\\]/g, '\\\\$&') + ')', 'gi');
          highlightedHtml = highlightedHtml.replace(repRegex, '<span class="approved-span">$1</span>');
        }}
      }});

      // Render into the 3 multi-channel cards
      document.getElementById('ch1-copy').innerHTML = highlightedHtml;
      document.getElementById('ch2-copy').innerHTML = highlightedHtml;
      document.getElementById('ch3-copy').innerHTML = highlightedHtml;

      const isClean = detectedViolations.length === 0;
      ['ch1-badge', 'ch2-badge', 'ch3-badge'].forEach(id => {{
        const el = document.getElementById(id);
        if (el) {{
          el.textContent = isClean ? "✓ ECOA & FHA Approved" : ("⚠ " + detectedViolations.length + " Redline Flag(s)");
          el.style.color = isClean ? "var(--ecoa-green)" : "var(--flag-red)";
        }}
      }});

      const topBadge = document.getElementById('top-compliance-badge');
      if (topBadge) {{
        topBadge.className = 'status-compliance-pill ' + (isClean ? 'approved' : 'flagged');
        topBadge.innerHTML = isClean
          ? '&#10003; 100% ECOA Reg B &amp; Fair Housing Compliant'
          : ('&#9888; ' + detectedViolations.length + ' ECOA / FHA Phrase(s) Flagged');
      }}

      const scorePill = document.getElementById('inspector-score-pill');
      const headline = document.getElementById('inspector-headline');
      const sub = document.getElementById('inspector-sub');
      if (isClean) {{
        scorePill.textContent = "APPROVED FOR LAUNCH";
        scorePill.style.color = "var(--ecoa-green)";
        headline.textContent = "0 Violations · Ready to Publish";
        headline.style.color = "var(--ecoa-green)";
        sub.textContent = "All multi-channel ad variations describe objective property features and inclusive ECOA income criteria.";
      }} else {{
        scorePill.textContent = "HOLD FOR REVISION";
        scorePill.style.color = "var(--flag-red)";
        headline.textContent = detectedViolations.length + " Prohibited Phrase(s) Detected";
        headline.style.color = "var(--text-main)";
        sub.textContent = "Click 'Auto-Rewrite Compliant Campaign' to replace demographic descriptors with objective property & loan terms.";
      }}

      const listEl = document.getElementById('violations-list');
      if (listEl) {{
        if (isClean) {{
          listEl.innerHTML = PROHIBITED_RULES.slice(0, 3).map(r =>
            '<div class="violation-card resolved">' +
              '<div class="violation-phrase">&#10003; Compliant: "' + r.replacement + '"</div>' +
              '<div class="violation-law">' + r.law + '</div>' +
              '<div class="violation-fix">Verified neutral property &amp; credit underwriting language.</div>' +
            '</div>'
          ).join('');
        }} else {{
          listEl.innerHTML = detectedViolations.map(r =>
            '<div class="violation-card">' +
              '<div class="violation-phrase">&#9888; Flagged: "' + r.phrase + '"</div>' +
              '<div class="violation-law">' + r.law + '</div>' +
              '<div class="violation-fix">' + r.reason + ' &rarr; Replace with: <strong>"' + r.replacement + '"</strong></div>' +
            '</div>'
          ).join('');
        }}
      }}
    }};

    window.hearCompliantAdReadout = function(btnEl) {{
      // Ensure compliant rewrite is spoken aloud
      const compliantText = CAMPAIGN_PRESETS[activePresetIdx].compliantCopy;
      window.playLiveCallClip(
        compliantText,
        "Aoede",
        "Rocket & Redfin Fair-Lending Approved Campaign Voice",
        btnEl
      );
    }};

    window.runLiveVertexAI = async function() {{
      const model = window.getSelectedModel ? window.getSelectedModel() : "gemini-4-argon";
      const outEl = document.getElementById('vertex-ai-output');
      const currentCopy = document.getElementById('master-copy-textarea').value;
      const drawerInput = document.getElementById('scenario-input');
      const scenarioText = (drawerInput && drawerInput.value.trim())
        ? drawerInput.value.trim() + "\\nAd Copy Under Review: " + currentCopy
        : "Audit this Redfin + Rocket Mortgage multi-channel ad copy under ECOA Regulation B (12 CFR § 1002.4) and the Fair Housing Act (42 U.S.C. § 3604), and provide a compliant rewrite: " + currentCopy;

      if (outEl) {{
        outEl.innerHTML = "<strong>⏳ Running ECOA &amp; Fair Housing Act Legal Redline Audit via Vertex AI (" + model + ")...</strong>";
      }}
      try {{
        const res = await fetch('/api/run-demo', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{
            square: "4.4",
            model: model,
            scenario: scenarioText
          }})
        }});
        const data = await res.json();
        if (outEl) {{
          outEl.textContent = data.output || data.text || "Fair-lending audit complete.";
        }}
      }} catch (err) {{
        if (outEl) {{
          outEl.textContent = "Unable to reach Vertex AI endpoint: " + err.message;
        }}
      }}
    }};

    document.addEventListener('DOMContentLoaded', () => {{
      window.loadCampaignPreset(0);
    }});
  </script>

  {floating_drawer}
</body>
</html>"""
