# -*- coding: utf-8 -*-
"""Square 6.1: Legacy .NET-to-Cloud Refactorer — Antigravity Agentic IDE
Design Style: GitHub Light Mode Pull Request & Split Code Review Page
(#FFFFFF GitHub light canvas, #F6F8FA GitHub header gray, #1F883D GitHub merge green button,
#DAFBE1 green diff additions, #FFEBE9 red diff deletions, Plus Jakarta Sans + IBM Plex Mono).
"""

from shared.standalone_uis.base_helpers import render_floating_control_bar_and_drawer


def render_sq_6_1(auth_token: str) -> str:
    code = "6.1"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>PR #1482: Refactor legacy VB.NET Float64 EscrowEngine to Go/Python Decimal128 | GitHub Light</title>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=IBM+Plex+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    :root {{
      --gh-canvas: #FFFFFF;
      --gh-header: #F6F8FA;
      --gh-border: #D0D7DE;
      --gh-border-muted: #D8DEE4;
      --gh-ink: #1F2328;
      --gh-muted: #656D76;
      --gh-green: #1F883D;
      --gh-green-hover: #1A7F37;
      --gh-add-bg: #DAFBE1;
      --gh-add-line: #ACEEBB;
      --gh-del-bg: #FFEBE9;
      --gh-del-line: #FFCECB;
      --gh-blue: #0969DA;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      background-color: var(--gh-canvas);
      color: var(--gh-ink);
      font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
      min-height: 100vh;
      padding-bottom: 92px;
    }}
    .mono {{ font-family: 'IBM Plex Mono', monospace; }}

    /* GitHub Light Repo Header */
    .gh-top-nav {{
      background: var(--gh-header);
      border-bottom: 1px solid var(--gh-border);
      padding: 14px 32px 0;
    }}
    .gh-repo-row {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 12px;
      padding-bottom: 12px;
    }}
    .repo-breadcrumb {{
      font-size: 14px;
      color: var(--gh-blue);
      font-weight: 600;
      display: flex;
      align-items: center;
      gap: 6px;
    }}
    .repo-breadcrumb strong {{ font-weight: 800; }}
    .repo-visibility {{
      font-size: 11px;
      color: var(--gh-muted);
      border: 1px solid var(--gh-border);
      padding: 1px 7px;
      border-radius: 999px;
      background: #FFFFFF;
      font-weight: 600;
    }}
    .top-right-controls {{
      display: flex;
      align-items: center;
      gap: 10px;
      flex-wrap: wrap;
    }}
    .gh-model-select {{
      background: #FFFFFF;
      border: 1px solid var(--gh-border);
      padding: 5px 10px;
      border-radius: 6px;
      font-size: 12px;
      font-weight: 600;
      display: flex;
      align-items: center;
      gap: 6px;
    }}
    .gh-model-select select {{
      background: transparent;
      border: none;
      font-family: 'IBM Plex Mono', monospace;
      font-size: 12px;
      font-weight: 700;
      color: var(--gh-blue);
      outline: none;
      cursor: pointer;
    }}
    .gh-btn-green {{
      background: var(--gh-green);
      color: #FFFFFF;
      border: 1px solid rgba(31, 35, 40, 0.15);
      padding: 7px 14px;
      border-radius: 6px;
      font-family: inherit;
      font-size: 12.5px;
      font-weight: 600;
      cursor: pointer;
      transition: 0.15s;
    }}
    .gh-btn-green:hover {{ background: var(--gh-green-hover); }}

    /* PR Title & Tabs */
    .pr-container {{
      max-width: 1420px;
      margin: 0 auto;
      padding: 20px 32px;
    }}
    .pr-title-row {{
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      gap: 16px;
      flex-wrap: wrap;
      margin-bottom: 10px;
    }}
    .pr-title {{
      font-size: 24px;
      font-weight: 700;
      color: var(--gh-ink);
      line-height: 1.25;
    }}
    .pr-num {{
      color: var(--gh-muted);
      font-weight: 400;
    }}
    .pr-meta-row {{
      display: flex;
      align-items: center;
      gap: 10px;
      flex-wrap: wrap;
      font-size: 13px;
      color: var(--gh-muted);
      padding-bottom: 16px;
      border-bottom: 1px solid var(--gh-border);
    }}
    .pr-state-open {{
      background: var(--gh-green);
      color: #FFFFFF;
      padding: 4px 12px;
      border-radius: 999px;
      font-weight: 700;
      font-size: 12.5px;
      display: inline-flex;
      align-items: center;
      gap: 5px;
    }}
    .branch-pill {{
      background: #DDF4FF;
      color: #0969DA;
      font-family: 'IBM Plex Mono', monospace;
      font-size: 11.5px;
      padding: 2px 8px;
      border-radius: 6px;
      font-weight: 600;
    }}

    /* GitHub PR Sub-Tabs */
    .pr-tabs {{
      display: flex;
      gap: 4px;
      border-bottom: 1px solid var(--gh-border);
      margin-top: 14px;
      margin-bottom: 20px;
      flex-wrap: wrap;
    }}
    .pr-tab {{
      background: transparent;
      border: 1px solid transparent;
      border-bottom: none;
      padding: 9px 16px;
      font-family: inherit;
      font-size: 13px;
      font-weight: 600;
      color: var(--gh-muted);
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      border-radius: 6px 6px 0 0;
    }}
    .pr-tab.active {{
      background: #FFFFFF;
      color: var(--gh-ink);
      border-color: var(--gh-border);
      position: relative;
      top: 1px;
    }}
    .tab-counter {{
      background: rgba(175, 184, 193, 0.25);
      padding: 1px 7px;
      border-radius: 999px;
      font-size: 11px;
      font-weight: 700;
    }}

    /* Split Code Diff File Box */
    .diff-file-card {{
      border: 1px solid var(--gh-border);
      border-radius: 6px;
      overflow: hidden;
      margin-bottom: 22px;
    }}
    .diff-file-header {{
      background: var(--gh-header);
      border-bottom: 1px solid var(--gh-border);
      padding: 10px 16px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      font-family: 'IBM Plex Mono', monospace;
      font-size: 12.5px;
      flex-wrap: wrap;
      gap: 10px;
    }}
    .diff-split-grid {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      font-family: 'IBM Plex Mono', monospace;
      font-size: 12px;
      line-height: 1.65;
    }}
    @media (max-width: 980px) {{
      .diff-split-grid {{ grid-template-columns: 1fr; }}
    }}
    .diff-col {{
      padding: 12px 0;
      overflow-x: auto;
    }}
    .diff-col.left-legacy {{
      border-right: 1px solid var(--gh-border);
      background: #FFFDFD;
    }}
    .diff-col.right-cloud {{
      background: #FCFFFD;
    }}
    .code-line {{
      padding: 1px 14px;
      white-space: pre;
      display: flex;
      gap: 12px;
    }}
    .ln {{
      color: var(--gh-muted);
      width: 28px;
      text-align: right;
      user-select: none;
      flex-shrink: 0;
    }}
    .code-line.del {{
      background: var(--gh-del-bg);
      color: #82071E;
    }}
    .code-line.add {{
      background: var(--gh-add-bg);
      color: #116329;
    }}

    /* Precision Drift Simulator & Merge Box */
    .bottom-grid {{
      display: grid;
      grid-template-columns: 1.15fr 1fr;
      gap: 22px;
    }}
    @media (max-width: 980px) {{
      .bottom-grid {{ grid-template-columns: 1fr; }}
    }}
    .gh-box {{
      border: 1px solid var(--gh-border);
      border-radius: 6px;
      background: #FFFFFF;
      overflow: hidden;
    }}
    .gh-box-head {{
      background: var(--gh-header);
      border-bottom: 1px solid var(--gh-border);
      padding: 12px 16px;
      font-size: 13.5px;
      font-weight: 700;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}
    .gh-box-body {{
      padding: 16px 18px;
      display: flex;
      flex-direction: column;
      gap: 14px;
    }}
    .sim-compare {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 12px;
    }}
    .sim-pill {{
      padding: 12px;
      border-radius: 6px;
      border: 1px solid var(--gh-border);
    }}
    .sim-pill.bad {{ background: var(--gh-del-bg); border-color: var(--gh-del-line); }}
    .sim-pill.good {{ background: var(--gh-add-bg); border-color: var(--gh-add-line); }}
    .ai-review-out {{
      background: var(--gh-header);
      border: 1px solid var(--gh-border);
      border-radius: 6px;
      padding: 14px;
      font-size: 12.5px;
      line-height: 1.6;
      display: none;
      white-space: pre-wrap;
    }}
  </style>
</head>
<body>

  <!-- GitHub Light Header -->
  <header class="gh-top-nav">
    <div class="gh-repo-row">
      <div class="repo-breadcrumb">
        <span>📦 rocket-companies / <strong>servicing-escrow-core</strong></span>
        <span class="repo-visibility">Internal Enterprise</span>
      </div>
      <div class="top-right-controls">
        <div class="gh-model-select">
          <span>Model:</span>
          <select id="app-model-select" onchange="window.syncSelectedModel(this.value)">
            <option value="gemini-4-argon">gemini-4-argon</option>
            <option value="gemini-3.8-flash">gemini-3.8-flash</option>
          </select>
        </div>
        <button class="gh-btn-green" onclick="window.playStaffReviewAudio(this)">
          🔊 Play Staff Engineer Code Review Audio
        </button>
      </div>
    </div>
  </header>

  <main class="pr-container">
    <div class="pr-title-row">
      <h1 class="pr-title">
        Refactor legacy VB.NET Float64 EscrowEngine to Go/Python Decimal128 Cloud Run Service
        <span class="pr-num">#1482</span>
      </h1>
    </div>

    <div class="pr-meta-row">
      <span class="pr-state-open" id="pr-state-badge">● Open</span>
      <span><strong>antigravity-bot</strong> wants to merge 3 commits into <span class="branch-pill">main</span> from <span class="branch-pill">refactor/escrow-decimal128-cloudrun</span></span>
      <span style="margin-left:auto;color:var(--gh-green);font-weight:700;">+148 −112 lines changed</span>
    </div>

    <!-- GitHub PR Navigation Tabs -->
    <div class="pr-tabs" role="tablist">
      <button class="pr-tab" onclick="window.switchPrTab('conv', this)">
        💬 Conversation <span class="tab-counter">4</span>
      </button>
      <button class="pr-tab" onclick="window.switchPrTab('commits', this)">
        🔨 Commits <span class="tab-counter">3</span>
      </button>
      <button class="pr-tab" onclick="window.switchPrTab('checks', this)">
        ✓ Checks <span class="tab-counter" style="background:#DAFBE1;color:#116329;">12 Passed</span>
      </button>
      <button class="pr-tab active" onclick="window.switchPrTab('files', this)">
        📄 Files Changed <span class="tab-counter">2</span>
      </button>
    </div>

    <div id="tab-notice" style="display:none;margin-bottom:16px;padding:12px 16px;background:var(--gh-header);border:1px solid var(--gh-border);border-radius:6px;font-size:13px;"></div>

    <!-- Split Code Diff Viewer -->
    <section class="diff-file-card">
      <div class="diff-file-header">
        <span><strong>src/escrow/EscrowEngine.vb</strong> → <strong>services/escrow_service/calculator.py</strong></span>
        <span style="color:var(--gh-green);font-weight:700;">✓ IEEE-754 Float64 Penny Drift Eliminated (RESPA § 1024.17 Compliant)</span>
      </div>

      <div class="diff-split-grid">
        <!-- Left: Legacy VB.NET COM+ Float64 -->
        <div class="diff-col left-legacy">
          <div class="code-line"><span class="ln">41</span><span>' LEGACY VB.NET (.NET Framework 4.6.1 COM+ Monolith)</span></div>
          <div class="code-line"><span class="ln">42</span><span>Public Class EscrowCushionCalculator</span></div>
          <div class="code-line del"><span class="ln">43</span><span>-   Public Function CalcMonthlyImpound(ByVal tax As Double, _</span></div>
          <div class="code-line del"><span class="ln">44</span><span>-                                      ByVal haz As Double) As Double</span></div>
          <div class="code-line del"><span class="ln">45</span><span>-       ' BUG: IEEE-754 Binary64 causes $0.03-$0.19 RESPA drift</span></div>
          <div class="code-line del"><span class="ln">46</span><span>-       Dim rawMonthly As Double = (tax + haz) / 12.0R</span></div>
          <div class="code-line del"><span class="ln">47</span><span>-       Dim statutoryCushion As Double = rawMonthly * 2.0R</span></div>
          <div class="code-line del"><span class="ln">48</span><span>-       Return Math.Round(rawMonthly + (statutoryCushion / 12.0R), 2)</span></div>
          <div class="code-line del"><span class="ln">49</span><span>-   End Function</span></div>
          <div class="code-line"><span class="ln">50</span><span>End Class</span></div>
        </div>

        <!-- Right: Refactored Cloud Run Python Decimal128 Service -->
        <div class="diff-col right-cloud">
          <div class="code-line"><span class="ln">41</span><span># REFACTORED CLOUD RUN SERVICE (Python 3.12 · Decimal128)</span></div>
          <div class="code-line add"><span class="ln">42</span><span>+ from decimal import Decimal, ROUND_HALF_EVEN</span></div>
          <div class="code-line add"><span class="ln">43</span><span>+ </span></div>
          <div class="code-line add"><span class="ln">44</span><span>+ def calc_monthly_impound(annual_tax: Decimal,</span></div>
          <div class="code-line add"><span class="ln">45</span><span>+                          annual_hazard: Decimal) -> Decimal:</span></div>
          <div class="code-line add"><span class="ln">46</span><span>+     '''RESPA 12 CFR § 1024.17 1/6th aggregate escrow cushion.'''</span></div>
          <div class="code-line add"><span class="ln">47</span><span>+     cent = Decimal("0.01")</span></div>
          <div class="code-line add"><span class="ln">48</span><span>+     monthly_base = ((annual_tax + annual_hazard) / Decimal(12)).quantize(cent, ROUND_HALF_EVEN)</span></div>
          <div class="code-line add"><span class="ln">49</span><span>+     respa_cushion = ((annual_tax + annual_hazard) / Decimal(6)).quantize(cent, ROUND_HALF_EVEN)</span></div>
          <div class="code-line add"><span class="ln">50</span><span>+     return monthly_base, respa_cushion</span></div>
        </div>
      </div>
    </section>

    <!-- Bottom Interactive Precision Test Sliders & GitHub Merge Box -->
    <div class="bottom-grid">
      <div class="gh-box">
        <div class="gh-box-head">
          <span>Interactive RESPA 360-Month Amortization Precision Test</span>
          <span class="mono" style="font-size:11.5px;color:var(--gh-blue);">10,000 Golden Loan Parity Vectors</span>
        </div>
        <div class="gh-box-body">
          <div>
            <div style="display:flex;justify-content:space-between;font-size:13px;font-weight:700;margin-bottom:6px;">
              <span>Annual Property Tax + Hazard Disbursal</span>
              <span class="mono" id="tax-val-lbl">$9,487.33 / yr</span>
            </div>
            <input type="range" id="slider-tax" min="3200" max="24000" step="17.33" value="9487.33" style="width:100%;accent-color:var(--gh-green);cursor:pointer;" oninput="window.updateEscrowSim()">
          </div>

          <div class="sim-compare">
            <div class="sim-pill bad">
              <div style="font-size:11px;font-weight:700;color:#82071E;">LEGACY VB.NET FLOAT64 (360-MO CUMULATIVE)</div>
              <div class="mono" id="legacy-drift-val" style="font-size:18px;font-weight:700;color:#82071E;margin-top:4px;">$790.6108333... (-$0.14 Drift)</div>
              <div style="font-size:11.5px;color:#82071E;margin-top:2px;">Triggers RESPA § 1024.17 Over-Cushion Exception</div>
            </div>
            <div class="sim-pill good">
              <div style="font-size:11px;font-weight:700;color:#116329;">CLOUD RUN DECIMAL128 (EXACT BANKER'S ROUNDING)</div>
              <div class="mono" id="cloud-exact-val" style="font-size:18px;font-weight:700;color:#116329;margin-top:4px;">$790.61 / mo ($0.00 Drift)</div>
              <div style="font-size:11.5px;color:#116329;margin-top:2px;">100.0% Bit-Exact Match vs. CFPB Reference Table</div>
            </div>
          </div>
        </div>
      </div>

      <div class="gh-box">
        <div class="gh-box-head">
          <span>GitHub Pull Request Merge &amp; CI Checks</span>
          <span style="color:var(--gh-green);font-size:12px;">✓ All 12 checks have passed</span>
        </div>
        <div class="gh-box-body">
          <div style="font-size:13px;color:var(--gh-ink);line-height:1.55;">
            <div>✓ <strong>antigravity/golden-master-suite</strong> — 10,000/10,000 loan vectors passed in 4.1s</div>
            <div>✓ <strong>cloud-run/canary-benchmark</strong> — p99 latency reduced from 340ms to 29ms</div>
            <div>✓ <strong>secops/semgrep-sast</strong> — 0 vulnerabilities detected</div>
          </div>
          <div style="display:flex;gap:10px;flex-wrap:wrap;margin-top:4px;">
            <button class="gh-btn-green" id="merge-btn" onclick="window.mergePullRequest()">
              Merge pull request #1482
            </button>
            <button class="gh-btn-green" style="background:#0969DA;" onclick="window.runLiveVertexAI()">
              ⚡ Run Live Vertex AI Code Review
            </button>
          </div>
          <div id="ai-pr-output" class="ai-review-out"></div>
        </div>
      </div>
    </div>
  </main>

  <script>
    window.updateEscrowSim = function() {{
      const val = parseFloat(document.getElementById('slider-tax').value);
      document.getElementById('tax-val-lbl').innerText = "$" + val.toLocaleString('en-US', {{minimumFractionDigits:2, maximumFractionDigits:2}}) + " / yr";
      const monthly = val / 12.0;
      const exact = monthly.toFixed(2);
      const driftCents = (((val * 100) % 12) * 0.02 + 0.04).toFixed(2);
      document.getElementById('legacy-drift-val').innerText = `$${{monthly.toFixed(6)}} (-$${{driftCents}} Drift)`;
      document.getElementById('cloud-exact-val').innerText = `$${{exact}} / mo ($0.00 Drift)`;
    }};

    window.switchPrTab = function(tab, btnEl) {{
      document.querySelectorAll('.pr-tab').forEach(b => b.classList.remove('active'));
      if (btnEl) btnEl.classList.add('active');
      const notice = document.getElementById('tab-notice');
      if (tab === 'files') {{
        notice.style.display = 'none';
      }} else if (tab === 'conv') {{
        notice.style.display = 'block';
        notice.innerHTML = '<strong>@staff-eng-architect:</strong> Approved! Replacing COM+ <code>System.Double</code> with <code>Decimal(ROUND_HALF_EVEN)</code> eliminates the $0.14 RESPA annual escrow statement discrepancy across 2.1M serviced loans.';
      }} else if (tab === 'commits') {{
        notice.style.display = 'block';
        notice.innerHTML = '<code>a91f40c</code> Extract VB.NET EscrowEngine AST · <code>e48b112</code> Implement Python Decimal128 service · <code>7c3029d</code> Add 10,000 golden-master RESPA unit tests.';
      }} else if (tab === 'checks') {{
        notice.style.display = 'block';
        notice.innerHTML = '✓ <strong>12 / 12 GitHub Actions Checks Passed:</strong> Pytest Golden Vector Suite (10,000/10,000), Cloud Run Terraform Plan, Container Structure Test, and RESPA Compliance Verifier.';
      }}
    }};

    window.mergePullRequest = function() {{
      const badge = document.getElementById('pr-state-badge');
      badge.style.background = '#8250DF';
      badge.innerText = '🟣 Merged';
      const btn = document.getElementById('merge-btn');
      btn.style.background = '#8250DF';
      btn.innerText = '✓ Pull Request #1482 Merged into main';
    }};

    window.playStaffReviewAudio = function(btnEl) {{
      const msg = "Staff Engineer Code Review for Pull Request 1482. Antigravity refactored our legacy 2009 VB.NET COM-Plus EscrowEngine into a stateless Cloud Run microservice using strict Decimal128 banker's rounding. Previously, IEEE-754 binary floating-point arithmetic caused up to 14 cents of cumulative drift over 360-month amortization schedules, triggering RESPA Section 1024.17 audit exceptions. All 10,000 golden-master loan vectors now pass with zero drift and p99 latency dropped from 340 milliseconds to 29 milliseconds.";
      window.playLiveCallClip(msg, "Puck", "Rocket Principal Staff Engineer", btnEl);
    }};

    window.runLiveVertexAI = async function() {{
      const out = document.getElementById('ai-pr-output');
      out.style.display = 'block';
      const model = window.getSelectedModel ? window.getSelectedModel() : 'gemini-4-argon';
      out.textContent = `Running Antigravity AST & Decimal128 Verification via Vertex AI (${{model}})...`;
      try {{
        const res = await fetch('/api/run-demo', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{
            code: '6.1',
            model: model,
            scenario: "Review PR #1482 refactoring legacy VB.NET Float64 EscrowEngine to Cloud Run Python Decimal128 with 10,000 RESPA golden tests."
          }})
        }});
        const data = await res.json();
        out.textContent = data.output || data.text || "Code review completed.";
      }} catch (e) {{
        out.textContent = "Error: " + e.message;
      }}
    }};
  </script>

  {render_floating_control_bar_and_drawer(code, auth_token)}
</body>
</html>
"""
