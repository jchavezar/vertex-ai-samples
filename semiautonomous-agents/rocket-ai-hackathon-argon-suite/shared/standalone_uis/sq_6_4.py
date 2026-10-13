# -*- coding: utf-8 -*-
"""Square 6.4: Incident Root-Cause & Runbook Agent — Cloud Trace + Gemini 3.8 Flash
Design Style: Datadog / PagerDuty Light Service Health & Postmortem Report
(#F9FAFB light canvas, #632CA6 Datadog purple header bar, #DC2626 P1 alert red,
#059669 mitigated green, Plus Jakarta Sans + IBM Plex Mono).
"""

from shared.standalone_uis.base_helpers import render_floating_control_bar_and_drawer


def render_sq_6_4(auth_token: str) -> str:
    code = "6.4"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Incident Root-Cause & Runbook Agent | Datadog & PagerDuty Light Postmortem</title>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=IBM+Plex+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    :root {{
      --bg: #F9FAFB;
      --card: #FFFFFF;
      --dd-purple: #632CA6;
      --dd-purple-dark: #4B1E82;
      --p1-red: #DC2626;
      --p1-bg: #FEF2F2;
      --ok-green: #059669;
      --ok-bg: #ECFDF5;
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
      padding-bottom: 92px;
    }}
    .mono {{ font-family: 'IBM Plex Mono', monospace; }}

    /* Datadog Purple Header Bar */
    .dd-header {{
      background: var(--dd-purple);
      color: #FFFFFF;
      padding: 14px 32px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 14px;
    }}
    .dd-brand {{
      display: flex;
      align-items: center;
      gap: 12px;
    }}
    .dd-tag {{
      background: rgba(255, 255, 255, 0.18);
      border: 1px solid rgba(255, 255, 255, 0.35);
      padding: 4px 10px;
      border-radius: 5px;
      font-family: 'IBM Plex Mono', monospace;
      font-size: 11.5px;
      font-weight: 700;
    }}
    .dd-title {{
      font-size: 19px;
      font-weight: 800;
    }}
    .dd-right {{
      display: flex;
      align-items: center;
      gap: 10px;
      flex-wrap: wrap;
    }}
    .dd-model-pill {{
      background: rgba(255, 255, 255, 0.15);
      border: 1px solid rgba(255, 255, 255, 0.3);
      padding: 5px 10px;
      border-radius: 6px;
      font-size: 12px;
      font-weight: 600;
      display: flex;
      align-items: center;
      gap: 6px;
    }}
    .dd-model-pill select {{
      background: transparent;
      border: none;
      color: #FFFFFF;
      font-family: 'IBM Plex Mono', monospace;
      font-weight: 700;
      font-size: 12px;
      outline: none;
      cursor: pointer;
    }}
    .dd-model-pill select option {{ color: #111827; background: #FFFFFF; }}
    .btn-ic-audio {{
      background: #FFFFFF;
      color: var(--dd-purple-dark);
      border: none;
      padding: 8px 15px;
      border-radius: 6px;
      font-family: inherit;
      font-size: 13px;
      font-weight: 700;
      cursor: pointer;
    }}

    /* Incident Status Banner */
    .inc-banner {{
      max-width: 1420px;
      margin: 20px auto 0;
      padding: 0 32px;
    }}
    .inc-bar {{
      background: var(--card);
      border: 1px solid var(--border);
      border-left: 5px solid var(--p1-red);
      border-radius: 8px;
      padding: 16px 22px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 16px;
      box-shadow: 0 1px 4px rgba(0,0,0,0.04);
    }}
    .inc-bar.mitigated {{
      border-left-color: var(--ok-green);
    }}
    .p1-pill {{
      background: var(--p1-bg);
      color: var(--p1-red);
      border: 1px solid #FECACA;
      padding: 4px 10px;
      border-radius: 5px;
      font-family: 'IBM Plex Mono', monospace;
      font-size: 12px;
      font-weight: 700;
    }}
    .p1-pill.mitigated {{
      background: var(--ok-bg);
      color: var(--ok-green);
      border-color: #A7F3D0;
    }}

    /* Main Grid */
    .sre-grid {{
      max-width: 1420px;
      margin: 20px auto;
      padding: 0 32px;
      display: grid;
      grid-template-columns: 1.2fr 1fr;
      gap: 22px;
    }}
    @media (max-width: 1040px) {{
      .sre-grid {{ grid-template-columns: 1fr; }}
    }}
    .sre-card {{
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 8px;
      overflow: hidden;
      display: flex;
      flex-direction: column;
    }}
    .sre-card-head {{
      padding: 14px 18px;
      border-bottom: 1px solid var(--border);
      background: #FCFDFE;
      font-size: 14px;
      font-weight: 700;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}
    .sre-card-body {{
      padding: 18px;
      display: flex;
      flex-direction: column;
      gap: 14px;
    }}

    /* Distributed Trace Waterfall Chart */
    .waterfall-row {{
      display: grid;
      grid-template-columns: 210px 1fr 80px;
      align-items: center;
      gap: 10px;
      font-family: 'IBM Plex Mono', monospace;
      font-size: 11.5px;
      padding: 7px 0;
      border-bottom: 1px solid #F3F4F6;
    }}
    .wf-track {{
      height: 18px;
      background: #F3F4F6;
      border-radius: 3px;
      position: relative;
      overflow: hidden;
    }}
    .wf-bar {{
      height: 100%;
      border-radius: 3px;
      position: absolute;
    }}

    /* Runbook Checklist */
    .runbook-step {{
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 12px 14px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      cursor: pointer;
      background: #FFFFFF;
      transition: 0.15s;
    }}
    .runbook-step.done {{
      background: var(--ok-bg);
      border-color: #A7F3D0;
    }}
    .step-btn {{
      background: var(--dd-purple);
      color: #FFFFFF;
      border: none;
      padding: 6px 12px;
      border-radius: 5px;
      font-family: inherit;
      font-size: 12px;
      font-weight: 700;
      cursor: pointer;
      white-space: nowrap;
    }}
    .runbook-step.done .step-btn {{
      background: var(--ok-green);
    }}
    .ai-sre-out {{
      background: #F8FAFC;
      border: 1px solid var(--border);
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

  <!-- Datadog Purple Header -->
  <header class="dd-header">
    <div class="dd-brand">
      <span class="dd-tag">DATADOG APM · PAGERDUTY INC-4912</span>
      <h1 class="dd-title">Incident Root-Cause &amp; Runbook Agent</h1>
    </div>
    <div class="dd-right">
      <div class="dd-model-pill">
        <span>Model:</span>
        <select id="app-model-select" onchange="window.syncSelectedModel(this.value)">
          <option value="gemini-3.8-flash">gemini-3.8-flash (Low-Latency SRE)</option>
          <option value="gemini-4-argon">gemini-4-argon (Deep Postmortem)</option>
        </select>
      </div>
      <button class="btn-ic-audio" onclick="window.playIncidentBriefing(this)">
        🔊 Listen to Incident Commander Briefing
      </button>
    </div>
  </header>

  <!-- Incident Status Banner -->
  <section class="inc-banner">
    <div class="inc-bar" id="inc-status-bar">
      <div>
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:4px;">
          <span class="p1-pill" id="inc-state-pill">P1 TRIGGERED · 14:02 UTC</span>
          <span class="mono" style="font-size:12px;color:var(--ink-muted);">Service: <code>pricing-lock-engine-us-central1</code></span>
        </div>
        <div style="font-size:17px;font-weight:800;" id="inc-headline">
          Cloud Run → AlloyDB Connection Pool Exhaustion at 14:02 UTC (p99 Latency: 4,820ms)
        </div>
      </div>
      <div class="mono" style="text-align:right;">
        <div style="font-size:11px;color:var(--ink-muted);">CURRENT P99 LATENCY</div>
        <div style="font-size:22px;font-weight:800;color:var(--p1-red);" id="live-p99-val">4,820 ms</div>
      </div>
    </div>
  </section>

  <!-- Main Two-Column Datadog Waterfall & Runbook Executor -->
  <main class="sre-grid">
    <!-- Left Column: Distributed Trace Waterfall Chart + Pool Sliders -->
    <section class="sre-card">
      <div class="sre-card-head">
        <span>Distributed Trace Waterfall (`trace_id: 7f92a01c4b88e102` · 14:02:11 UTC)</span>
        <span class="mono" style="font-size:11.5px;color:var(--dd-purple);">Cloud Trace + AlloyDB Insights</span>
      </div>
      <div class="sre-card-body">
        <div>
          <div class="waterfall-row">
            <span>1. Cloud Armor Edge Ingress</span>
            <div class="wf-track"><div class="wf-bar" style="left:0%;width:4%;background:var(--dd-purple);"></div></div>
            <span style="text-align:right;">12 ms</span>
          </div>
          <div class="waterfall-row">
            <span>2. Cloud Run `rate-lock-v84`</span>
            <div class="wf-track"><div class="wf-bar" style="left:4%;width:94%;background:var(--dd-purple);"></div></div>
            <span style="text-align:right;" id="wf-cr-ms">4,808 ms</span>
          </div>
          <div class="waterfall-row">
            <span>3. PgBouncer Pool Wait</span>
            <div class="wf-track"><div class="wf-bar" id="wf-pool-bar" style="left:6%;width:86%;background:var(--p1-red);"></div></div>
            <span style="text-align:right;font-weight:700;color:var(--p1-red);" id="wf-pool-ms">4,640 ms</span>
          </div>
          <div class="waterfall-row">
            <span>4. AlloyDB SQL Execution</span>
            <div class="wf-track"><div class="wf-bar" style="left:92%;width:6%;background:var(--ok-green);"></div></div>
            <span style="text-align:right;">18 ms</span>
          </div>
        </div>

        <!-- Interactive Connection Pool Size & Traffic Spike Sliders -->
        <div style="background:#F8FAFC;border:1px solid var(--border);border-radius:8px;padding:14px;">
          <div style="display:flex;justify-content:space-between;font-size:12.5px;font-weight:700;margin-bottom:4px;">
            <span>PgBouncer Max Connection Pool Size (`max_client_conn`)</span>
            <span class="mono" id="pool-size-lbl">100 conns (Exhausted)</span>
          </div>
          <input type="range" id="slider-pool" min="100" max="500" step="50" value="100" style="width:100%;accent-color:var(--dd-purple);cursor:pointer;" oninput="window.updatePoolSimulator()">

          <div style="display:flex;justify-content:space-between;font-size:12.5px;font-weight:700;margin-top:12px;margin-bottom:4px;">
            <span>Concurrent Rate-Lock Traffic Spike (RPS)</span>
            <span class="mono" id="rps-val-lbl">1,850 req/s</span>
          </div>
          <input type="range" id="slider-rps" min="600" max="2400" step="50" value="1850" style="width:100%;accent-color:var(--dd-purple);cursor:pointer;" oninput="window.updatePoolSimulator()">
        </div>
      </div>
    </section>

    <!-- Right Column: Clickable SRE Remediation Runbook Checklist -->
    <section class="sre-card">
      <div class="sre-card-head">
        <span>Clickable SRE Remediation Runbook Checklist</span>
        <span class="mono" style="font-size:11.5px;color:var(--ok-green);" id="runbook-progress-lbl">0 / 3 Executed</span>
      </div>
      <div class="sre-card-body">

        <div class="runbook-step" id="rb-step-1" onclick="window.toggleRunbookStep(1)">
          <div>
            <div style="font-size:13.5px;font-weight:700;">1. Drain canary revision (`rate-lock-v84-canary` → `v83-stable`)</div>
            <div style="font-size:12px;color:var(--ink-muted);">Shifts 100% traffic back to revision `v83` which closes leaked cursors.</div>
          </div>
          <button class="step-btn" id="rb-btn-1">Execute Step 1</button>
        </div>

        <div class="runbook-step" id="rb-step-2" onclick="window.toggleRunbookStep(2)">
          <div>
            <div style="font-size:13.5px;font-weight:700;">2. Increase PgBouncer pool (`100 → 400 transaction-mode conns`)</div>
            <div style="font-size:12px;color:var(--ink-muted);">Eliminates AlloyDB connection queue wait under 1,850 RPS lock surge.</div>
          </div>
          <button class="step-btn" id="rb-btn-2">Execute Step 2</button>
        </div>

        <div class="runbook-step" id="rb-step-3" onclick="window.toggleRunbookStep(3)">
          <div>
            <div style="font-size:13.5px;font-weight:700;">3. Verify p99 &lt; 180ms &amp; Resolve PagerDuty Incident #4912</div>
            <div style="font-size:12px;color:var(--ink-muted);">Confirms synthetic rate-lock probes pass at 112ms p99 across 3 regions.</div>
          </div>
          <button class="step-btn" id="rb-btn-3">Execute Step 3</button>
        </div>

        <button class="step-btn" style="padding:10px;width:100%;" onclick="window.runLiveVertexAI()">
          ⚡ Generate Blameless Google SRE Postmortem via Vertex AI
        </button>

        <div id="ai-sre-output" class="ai-sre-out"></div>
      </div>
    </section>
  </main>

  <script>
    const rbDone = {{ 1: false, 2: false, 3: false }};

    window.updatePoolSimulator = function() {{
      const pool = parseInt(document.getElementById('slider-pool').value, 10);
      const rps = parseInt(document.getElementById('slider-rps').value, 10);
      document.getElementById('pool-size-lbl').innerText = `${{pool}} conns (${{pool >= 350 ? 'Healthy Headroom' : 'Contended'}})`;
      document.getElementById('rps-val-lbl').innerText = `${{rps.toLocaleString()}} req/s`;

      const ratio = rps / (pool * 6);
      const waitMs = ratio > 1 ? Math.round((ratio - 0.8) * 2100) : Math.round(ratio * 65);
      const totalP99 = waitMs + 30;

      document.getElementById('live-p99-val').innerText = `${{totalP99.toLocaleString()}} ms`;
      document.getElementById('live-p99-val').style.color = totalP99 < 180 ? "var(--ok-green)" : "var(--p1-red)";
      document.getElementById('wf-cr-ms').innerText = `${{(waitMs + 18).toLocaleString()}} ms`;
      document.getElementById('wf-pool-ms').innerText = `${{waitMs.toLocaleString()}} ms`;
      document.getElementById('wf-pool-ms').style.color = totalP99 < 180 ? "var(--ok-green)" : "var(--p1-red)";
      const bar = document.getElementById('wf-pool-bar');
      bar.style.width = Math.min(86, Math.max(8, Math.round(waitMs / 55))) + "%";
      bar.style.background = totalP99 < 180 ? "var(--ok-green)" : "var(--p1-red)";
    }};

    window.toggleRunbookStep = function(id) {{
      rbDone[id] = !rbDone[id];
      document.getElementById('rb-step-' + id).classList.toggle('done', rbDone[id]);
      document.getElementById('rb-btn-' + id).innerText = rbDone[id] ? "✓ Completed" : `Execute Step ${{id}}`;

      if (id === 2 && rbDone[2]) {{
        document.getElementById('slider-pool').value = 400;
        window.updatePoolSimulator();
      }}
      const count = [1,2,3].filter(k => rbDone[k]).length;
      document.getElementById('runbook-progress-lbl').innerText = `${{count}} / 3 Executed`;

      const bar = document.getElementById('inc-status-bar');
      const pill = document.getElementById('inc-state-pill');
      if (count === 3) {{
        bar.classList.add('mitigated');
        pill.className = "p1-pill mitigated";
        pill.innerText = "✓ RESOLVED · MTTR 4m 12s";
        document.getElementById('inc-headline').innerText = "Incident Mitigated — PgBouncer Scaled to 400 & Canary Drained (p99: 112ms)";
        document.getElementById('live-p99-val').innerText = "112 ms";
        document.getElementById('live-p99-val').style.color = "var(--ok-green)";
      }} else {{
        bar.classList.remove('mitigated');
        pill.className = "p1-pill";
        pill.innerText = "P1 TRIGGERED · 14:02 UTC";
      }}
    }};

    window.playIncidentBriefing = function(btnEl) {{
      const msg = "Incident Commander Briefing for PagerDuty Alert 4912. At 14:02 UTC, p99 latency on the Rocket Pricing Lock Engine spiked to 4,820 milliseconds. Cloud Trace waterfall analysis isolated 4,640 milliseconds of wait time inside PgBouncer due to an unclosed cursor leak introduced in canary revision v84 combined with a 100-connection pool cap. Draining canary revision v84 and scaling PgBouncer to 400 connections restores p99 latency to 112 milliseconds in under four minutes.";
      window.playLiveCallClip(msg, "Charon", "Rocket Principal SRE Incident Commander", btnEl);
    }};

    window.runLiveVertexAI = async function() {{
      const out = document.getElementById('ai-sre-output');
      out.style.display = 'block';
      const model = window.getSelectedModel ? window.getSelectedModel() : 'gemini-3.8-flash';
      out.textContent = `Synthesizing Blameless SRE Postmortem via Vertex AI (${{model}})...`;
      try {{
        const res = await fetch('/api/run-demo', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{
            code: '6.4',
            model: model,
            scenario: "Draft blameless SRE postmortem for Cloud Run -> AlloyDB connection pool exhaustion at 14:02 UTC and 3-step remediation."
          }})
        }});
        const data = await res.json();
        out.textContent = data.output || data.text || "Postmortem generated.";
      }} catch (e) {{
        out.textContent = "Error: " + e.message;
      }}
    }};
  </script>

  {render_floating_control_bar_and_drawer(code, auth_token)}
</body>
</html>
"""
