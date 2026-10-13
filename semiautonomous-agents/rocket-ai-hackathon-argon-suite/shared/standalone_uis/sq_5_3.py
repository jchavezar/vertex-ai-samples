# -*- coding: utf-8 -*-
"""Square 5.3: Vendor Contract & SOC2 Risk Scorer — Gemini 4 Argon (1M Context)
Design Style: Vanta / Drata Trust & Vendor Security Portal
(#F9FAFB light enterprise gray, #4338CA Vanta indigo, #15803D passing control green,
#B91C1C critical gap red, Plus Jakarta Sans).
"""

from shared.standalone_uis.base_helpers import render_floating_control_bar_and_drawer


def render_sq_5_3(auth_token: str) -> str:
    code = "5.3"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Vendor Contract & SOC2 Risk Scorer | Rocket Trust & TPRM Portal</title>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=IBM+Plex+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  <style>
    :root {{
      --bg: #F9FAFB;
      --card: #FFFFFF;
      --indigo: #4338CA;
      --indigo-dark: #312E81;
      --indigo-light: #EEF2FF;
      --pass-green: #15803D;
      --pass-bg: #F0FDF4;
      --pass-border: #BBF7D0;
      --gap-red: #B91C1C;
      --gap-bg: #FEF2F2;
      --gap-border: #FECACA;
      --warn-amber: #B45309;
      --warn-bg: #FFFBEB;
      --ink: #111827;
      --ink-muted: #4B5563;
      --border: #E5E7EB;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      background-color: var(--bg);
      color: var(--ink);
      font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
      min-height: 100vh;
      padding-bottom: 88px;
    }}
    .mono {{ font-family: 'IBM Plex Mono', monospace; }}

    /* Vanta / Drata Trust Portal Top Bar */
    .trust-nav {{
      background: var(--card);
      border-bottom: 1px solid var(--border);
      padding: 16px 32px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 16px;
    }}
    .trust-brand {{
      display: flex;
      align-items: center;
      gap: 14px;
    }}
    .vanta-shield {{
      width: 40px;
      height: 40px;
      border-radius: 10px;
      background: var(--indigo);
      color: #FFFFFF;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 800;
      font-size: 16px;
      box-shadow: 0 4px 12px rgba(67, 56, 202, 0.25);
    }}
    .trust-title {{
      font-size: 20px;
      font-weight: 800;
      color: var(--ink);
      letter-spacing: -0.02em;
    }}
    .trust-sub {{
      font-size: 13px;
      color: var(--ink-muted);
    }}
    .nav-right {{
      display: flex;
      align-items: center;
      gap: 10px;
      flex-wrap: wrap;
    }}
    .model-pill {{
      background: var(--indigo-light);
      border: 1px solid #C7D2FE;
      padding: 6px 12px;
      border-radius: 8px;
      font-size: 12px;
      font-weight: 600;
      color: var(--indigo);
      display: flex;
      align-items: center;
      gap: 6px;
    }}
    .model-pill select {{
      background: transparent;
      border: none;
      color: var(--indigo-dark);
      font-family: inherit;
      font-weight: 700;
      font-size: 12px;
      outline: none;
      cursor: pointer;
    }}
    .ciso-audio-btn {{
      background: var(--indigo);
      color: #FFFFFF;
      border: none;
      padding: 9px 16px;
      border-radius: 8px;
      font-family: inherit;
      font-size: 13px;
      font-weight: 600;
      cursor: pointer;
      transition: 0.15s;
      box-shadow: 0 2px 6px rgba(67, 56, 202, 0.2);
    }}
    .ciso-audio-btn:hover {{ background: var(--indigo-dark); }}

    /* Vendor Scorecard Hero Banner */
    .scorecard-banner {{
      max-width: 1420px;
      margin: 22px auto 0;
      padding: 0 32px;
    }}
    .scorecard-inner {{
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 20px 26px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 20px;
      box-shadow: 0 2px 8px rgba(17, 24, 39, 0.04);
    }}
    .vendor-meta {{
      display: flex;
      flex-direction: column;
      gap: 4px;
    }}
    .vendor-tag {{
      font-size: 11px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      color: var(--indigo);
    }}
    .vendor-name {{
      font-size: 22px;
      font-weight: 800;
      color: var(--ink);
    }}
    .vendor-docs {{
      font-size: 13px;
      color: var(--ink-muted);
    }}
    .score-ring-box {{
      display: flex;
      align-items: center;
      gap: 20px;
      flex-wrap: wrap;
    }}
    .score-pill {{
      padding: 12px 20px;
      border-radius: 10px;
      background: var(--warn-bg);
      border: 1px solid #FDE68A;
      text-align: right;
    }}
    .score-pill.approved {{
      background: var(--pass-bg);
      border-color: var(--pass-border);
    }}
    .score-num {{
      font-size: 28px;
      font-weight: 800;
      color: var(--warn-amber);
    }}
    .score-pill.approved .score-num {{
      color: var(--pass-green);
    }}
    .score-status {{
      font-size: 12px;
      font-weight: 700;
      color: var(--ink-muted);
    }}

    /* Main Two-Column Vanta Layout */
    .portal-grid {{
      max-width: 1420px;
      margin: 22px auto;
      padding: 0 32px;
      display: grid;
      grid-template-columns: 1fr 1.25fr;
      gap: 24px;
    }}
    @media (max-width: 1060px) {{
      .portal-grid {{ grid-template-columns: 1fr; }}
    }}

    .portal-card {{
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 12px;
      box-shadow: 0 2px 8px rgba(17, 24, 39, 0.03);
      overflow: hidden;
      display: flex;
      flex-direction: column;
    }}
    .portal-card-head {{
      padding: 16px 22px;
      border-bottom: 1px solid var(--border);
      display: flex;
      align-items: center;
      justify-content: space-between;
      background: #FCFDFE;
    }}
    .portal-card-title {{
      font-size: 15px;
      font-weight: 700;
      color: var(--ink);
    }}
    .portal-card-body {{
      padding: 20px 22px;
      display: flex;
      flex-direction: column;
      gap: 14px;
    }}

    /* SOC2 Control Rows */
    .control-row {{
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 13px 16px;
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      gap: 12px;
    }}
    .control-id {{
      font-family: 'IBM Plex Mono', monospace;
      font-size: 11.5px;
      font-weight: 700;
      color: var(--indigo);
    }}
    .control-name {{
      font-size: 13.5px;
      font-weight: 700;
      color: var(--ink);
      margin-top: 2px;
    }}
    .control-detail {{
      font-size: 12.5px;
      color: var(--ink-muted);
      margin-top: 3px;
    }}
    .badge {{
      padding: 4px 10px;
      border-radius: 999px;
      font-size: 11px;
      font-weight: 700;
      white-space: nowrap;
    }}
    .badge.pass {{ background: var(--pass-bg); color: var(--pass-green); border: 1px solid var(--pass-border); }}
    .badge.gap {{ background: var(--gap-bg); color: var(--gap-red); border: 1px solid var(--gap-border); }}

    /* Side-by-Side MSA Clause Reviewer */
    .clause-card {{
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 16px 18px;
      background: #FFFFFF;
      transition: 0.15s;
    }}
    .clause-card.remediated {{
      border-color: var(--pass-border);
      background: #F9FEFB;
    }}
    .clause-header {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
      margin-bottom: 10px;
      flex-wrap: wrap;
    }}
    .clause-title {{
      font-size: 14.5px;
      font-weight: 700;
      color: var(--ink);
    }}
    .side-by-side-diff {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 12px;
      margin-bottom: 12px;
    }}
    @media (max-width: 720px) {{
      .side-by-side-diff {{ grid-template-columns: 1fr; }}
    }}
    .diff-pane {{
      padding: 12px 14px;
      border-radius: 8px;
      font-size: 12.5px;
      line-height: 1.55;
    }}
    .diff-pane.vendor-draft {{
      background: var(--gap-bg);
      border: 1px solid var(--gap-border);
      color: #7F1D1D;
    }}
    .diff-pane.rocket-redline {{
      background: var(--pass-bg);
      border: 1px solid var(--pass-border);
      color: #14532D;
    }}
    .pane-label {{
      font-size: 10.5px;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      margin-bottom: 5px;
    }}
    .redline-toggle-btn {{
      background: var(--indigo);
      color: #FFFFFF;
      border: none;
      padding: 7px 14px;
      border-radius: 6px;
      font-family: inherit;
      font-size: 12px;
      font-weight: 600;
      cursor: pointer;
    }}
    .redline-toggle-btn.accepted {{
      background: var(--pass-green);
    }}
    .ai-output {{
      background: #F8FAFC;
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 14px;
      font-size: 13px;
      line-height: 1.6;
      display: none;
      white-space: pre-wrap;
    }}
  </style>
</head>
<body>

  <!-- Vanta / Drata Trust Portal Header -->
  <header class="trust-nav">
    <div class="trust-brand">
      <div class="vanta-shield">V</div>
      <div>
        <h1 class="trust-title">Vendor Contract &amp; SOC2 Type II Risk Scorer</h1>
        <p class="trust-sub">Rocket Third-Party Risk Management (TPRM) · GLBA &amp; NYDFS 23 NYCRR 500 Continuous Assurance</p>
      </div>
    </div>
    <div class="nav-right">
      <div class="model-pill">
        <span>Model:</span>
        <select id="app-model-select" onchange="window.syncSelectedModel(this.value)">
          <option value="gemini-4-argon">gemini-4-argon (1M Context)</option>
          <option value="gemini-3.8-flash">gemini-3.8-flash</option>
        </select>
      </div>
      <button class="ciso-audio-btn" onclick="window.playCISOSummary(this)">
        🔊 Play CISO Vendor Risk Summary
      </button>
    </div>
  </header>

  <!-- Vendor Security Scorecard Hero -->
  <section class="scorecard-banner">
    <div class="scorecard-inner">
      <div class="vendor-meta">
        <span class="vendor-tag">ACTIVE TPRM REVIEW · VENDOR ID #VND-2026-884</span>
        <div class="vendor-name">ClearTitle AI Settlement Services, Inc.</div>
        <div class="vendor-docs">
          Ingested Corpus: <strong>SOC2 Type II Report (184 pages)</strong> + <strong>Master Services Agreement v2.4 (62 pages)</strong> · Tier-1 NPI Processor
        </div>
      </div>
      <div class="score-ring-box">
        <div class="score-pill" id="vendor-score-pill">
          <div class="score-num" id="vendor-score-num">71/100 · Conditional</div>
          <div class="score-status" id="vendor-score-sub">3 Mandatory MSA Redlines Pending</div>
        </div>
        <button class="ciso-audio-btn" style="background:#111827;" onclick="window.acceptAllClauses()">
          ✓ Enforce All 3 Rocket Security Addenda (→ 96/100 Approved)
        </button>
      </div>
    </div>
  </section>

  <!-- Main Two-Column Vanta Trust & MSA Reviewer -->
  <main class="portal-grid">
    <!-- Left Column: SOC2 Type II Trust Services Criteria Audit -->
    <section class="portal-card">
      <div class="portal-card-head">
        <span class="portal-card-title">AICPA SOC2 Type II Controls Matrix (184-Page Audit Extraction)</span>
        <span class="badge pass" id="controls-summary-badge">142 Passing · 3 Exceptions</span>
      </div>
      <div class="portal-card-body">
        <div class="control-row">
          <div>
            <div class="control-id">CC6.1 · Logical Access &amp; SSO Federation</div>
            <div class="control-name">Okta SAML 2.0 + Hardware WebAuthn MFA Enforced</div>
            <div class="control-detail">Zero exceptions noted across 12-month audit period (p. 64).</div>
          </div>
          <span class="badge pass">PASSING</span>
        </div>

        <div class="control-row">
          <div>
            <div class="control-id">CC6.7 · Encryption in Transit &amp; At Rest</div>
            <div class="control-name">TLS 1.3 &amp; AES-256 Cloud KMS Customer-Managed Keys (CMEK)</div>
            <div class="control-detail">Verified HSM key rotation every 90 days (p. 89).</div>
          </div>
          <span class="badge pass">PASSING</span>
        </div>

        <div class="control-row">
          <div>
            <div class="control-id">CC7.3 · Security Incident Notification SLA</div>
            <div class="control-name">Vendor MSA Draft Allows 72-Hour Notification Window</div>
            <div class="control-detail">Conflicts with Rocket NYDFS 23 NYCRR 500.17 24-hour TPRM mandate.</div>
          </div>
          <span class="badge gap" id="ctrl-badge-1">GAP · § 8.2</span>
        </div>

        <div class="control-row">
          <div>
            <div class="control-id">CC8.1 · Sub-Processor &amp; LLM Data Retention</div>
            <div class="control-name">Third-Party Foundation Model Training Opt-Out Missing</div>
            <div class="control-detail">MSA § 11.4 permits anonymized telemetry retention unless amended.</div>
          </div>
          <span class="badge gap" id="ctrl-badge-2">GAP · § 11.4</span>
        </div>

        <div class="control-row">
          <div>
            <div class="control-id">A1.2 · Multi-Region Disaster Recovery RTO</div>
            <div class="control-name">SOC2 Table 4.9 Notes 24-Hour RTO on Single-Region Failover</div>
            <div class="control-detail">Rocket Tier-1 Closing Criticality requires ≤ 4-Hour Active-Active RTO.</div>
          </div>
          <span class="badge gap" id="ctrl-badge-3">GAP · § 14.1</span>
        </div>

        <div style="padding-top:6px;display:flex;justify-content:space-between;align-items:center;gap:10px;flex-wrap:wrap;">
          <button class="redline-toggle-btn" onclick="window.runLiveVertexAI()">
            ⚡ Generate Live Vertex AI TPRM Risk Memo
          </button>
          <span class="mono" style="font-size:11.5px;color:var(--ink-muted);">Context Window Used: 214,890 / 1,000,000 tokens</span>
        </div>

        <div id="ai-tprm-output" class="ai-output"></div>
      </div>
    </section>

    <!-- Right Column: Side-by-Side MSA Contract Clause Reviewer -->
    <section class="portal-card">
      <div class="portal-card-head">
        <span class="portal-card-title">Side-by-Side MSA Contract Clause Reviewer &amp; Redline Enforcer</span>
        <span style="font-size:12px;color:var(--ink-muted);font-weight:600;">Click each clause to enforce Rocket Addendum</span>
      </div>
      <div class="portal-card-body">

        <!-- Clause 1: § 8.2 Breach Notification -->
        <div class="clause-card" id="clause-card-1">
          <div class="clause-header">
            <span class="clause-title">§ 8.2 Security Incident &amp; Breach Notification Window (+9 pts)</span>
            <button class="redline-toggle-btn" id="clause-btn-1" onclick="window.toggleClause(1)">
              Enforce 24h Notification Redline
            </button>
          </div>
          <div class="side-by-side-diff">
            <div class="diff-pane vendor-draft">
              <div class="pane-label">✗ VENDOR MSA DRAFT (§ 8.2)</div>
              “Vendor shall notify Rocket Companies within <strong>seventy-two (72) hours</strong> after confirming a security breach impacting Non-Public Personal Information (NPI).”
            </div>
            <div class="diff-pane rocket-redline">
              <div class="pane-label">✓ ROCKET TPRM MANDATORY REDLINE</div>
              “Vendor shall notify Rocket SOC within <strong>twenty-four (24) hours</strong> of detecting any suspected or confirmed unauthorized access to Borrower NPI per NYDFS 23 NYCRR 500.17.”
            </div>
          </div>
        </div>

        <!-- Clause 2: § 11.4 Zero-Retention Vertex AI BAA -->
        <div class="clause-card" id="clause-card-2">
          <div class="clause-header">
            <span class="clause-title">§ 11.4 Zero-Retention Vertex AI BAA &amp; Model Training Ban (+9 pts)</span>
            <button class="redline-toggle-btn" id="clause-btn-2" onclick="window.toggleClause(2)">
              Enforce Zero-Retention Addendum
            </button>
          </div>
          <div class="side-by-side-diff">
            <div class="diff-pane vendor-draft">
              <div class="pane-label">✗ VENDOR MSA DRAFT (§ 11.4)</div>
              “Vendor may utilize de-identified closing settlement documents to fine-tune and improve proprietary machine learning models.”
            </div>
            <div class="diff-pane rocket-redline">
              <div class="pane-label">✓ ROCKET TPRM MANDATORY REDLINE</div>
              “Vendor shall process all Rocket data exclusively via <strong>Zero-Data-Retention Vertex AI enterprise endpoints</strong>. Training, fine-tuning, or caching of Borrower NPI is strictly prohibited.”
            </div>
          </div>
        </div>

        <!-- Clause 3: § 14.1 Multi-Region DR RTO <= 4h -->
        <div class="clause-card" id="clause-card-3">
          <div class="clause-header">
            <span class="clause-title">§ 14.1 Multi-Region Disaster Recovery RTO ≤ 4 Hours (+7 pts)</span>
            <button class="redline-toggle-btn" id="clause-btn-3" onclick="window.toggleClause(3)">
              Enforce ≤ 4h Multi-Region DR SLA
            </button>
          </div>
          <div class="side-by-side-diff">
            <div class="diff-pane vendor-draft">
              <div class="pane-label">✗ VENDOR MSA DRAFT (§ 14.1)</div>
              “Vendor targets a commercially reasonable Recovery Time Objective (RTO) of <strong>twenty-four (24) hours</strong> in the event of a regional cloud outage.”
            </div>
            <div class="diff-pane rocket-redline">
              <div class="pane-label">✓ ROCKET TPRM MANDATORY REDLINE</div>
              “Vendor guarantees an active-active multi-region <strong>RTO ≤ 4 hours and RPO ≤ 15 minutes</strong> backed by semi-annual failover attestation.”
            </div>
          </div>
        </div>

      </div>
    </section>
  </main>

  <script>
    const clauses = {{ 1: false, 2: false, 3: false }};
    const weights = {{ 1: 9, 2: 9, 3: 7 }};

    function updateScorecard() {{
      let score = 71;
      let resolvedCount = 0;
      [1, 2, 3].forEach(id => {{
        if (clauses[id]) {{
          score += weights[id];
          resolvedCount++;
        }}
      }});

      const pill = document.getElementById('vendor-score-pill');
      const num = document.getElementById('vendor-score-num');
      const sub = document.getElementById('vendor-score-sub');
      const ctrlBadge = document.getElementById('controls-summary-badge');

      if (resolvedCount === 3) {{
        pill.classList.add('approved');
        num.innerText = `${{score}}/100 · Approved`;
        sub.innerText = "All 3 Mandatory MSA Security Addenda Executed";
        ctrlBadge.innerText = "145 Passing · 0 Exceptions";
      }} else {{
        pill.classList.remove('approved');
        num.innerText = `${{score}}/100 · Conditional`;
        sub.innerText = `${{3 - resolvedCount}} Mandatory MSA Redline(s) Pending`;
        ctrlBadge.innerText = `${{142 + resolvedCount}} Passing · ${{3 - resolvedCount}} Exceptions`;
      }}
    }}

    window.toggleClause = function(id) {{
      clauses[id] = !clauses[id];
      const card = document.getElementById('clause-card-' + id);
      const btn = document.getElementById('clause-btn-' + id);
      const badge = document.getElementById('ctrl-badge-' + id);

      card.classList.toggle('remediated', clauses[id]);
      btn.classList.toggle('accepted', clauses[id]);

      if (clauses[id]) {{
        btn.innerText = "✓ Redline Adopted into MSA";
        badge.className = "badge pass";
        badge.innerText = "REMEDIATED";
      }} else {{
        const labels = {{
          1: "Enforce 24h Notification Redline",
          2: "Enforce Zero-Retention Addendum",
          3: "Enforce ≤ 4h Multi-Region DR SLA"
        }};
        const gaps = {{ 1: "GAP · § 8.2", 2: "GAP · § 11.4", 3: "GAP · § 14.1" }};
        btn.innerText = labels[id];
        badge.className = "badge gap";
        badge.innerText = gaps[id];
      }}
      updateScorecard();
    }};

    window.acceptAllClauses = function() {{
      [1, 2, 3].forEach(id => {{
        if (!clauses[id]) window.toggleClause(id);
      }});
    }};

    window.playCISOSummary = function(btnEl) {{
      const msg = "CISO Third-Party Risk Summary for ClearTitle AI Settlement Services. Gemini 4 Argon ingested the full 184-page SOC2 Type 2 audit and 62-page Master Services Agreement in a single prompt. The vendor initially scored 71 out of 100 Conditional due to three gaps: a 72-hour breach notice clause in Section 8.2, permissive AI model training language in Section 11.4, and a 24-hour disaster recovery RTO in Section 14.1. Enforcing our three standard Rocket security redlines raises the vendor score to 96 out of 100 Approved.";
      window.playLiveCallClip(msg, "Charon", "Rocket Chief Information Security Officer", btnEl);
    }};

    window.runLiveVertexAI = async function() {{
      const out = document.getElementById('ai-tprm-output');
      out.style.display = 'block';
      const model = window.getSelectedModel ? window.getSelectedModel() : 'gemini-4-argon';
      out.textContent = `Running 1M-Context SOC2 + MSA Cross-Audit via Vertex AI (${{model}})...`;
      try {{
        const res = await fetch('/api/run-demo', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{
            code: '5.3',
            model: model,
            scenario: "Audit ClearTitle AI SOC2 Type II + MSA (§ 8.2 72h->24h breach notice, § 11.4 Zero-Retention Vertex AI BAA, § 14.1 Multi-Region DR RTO <= 4h)."
          }})
        }});
        const data = await res.json();
        out.textContent = data.output || data.text || "TPRM risk assessment complete.";
      }} catch (e) {{
        out.textContent = "Error: " + e.message;
      }}
    }};
  </script>

  {render_floating_control_bar_and_drawer(code, auth_token)}
</body>
</html>
"""
