# -*- coding: utf-8 -*-
"""Square 6.2: AI Software Factory: Autonomous PRD-to-Pull-Request Swarm — Standalone UI Design File.
Visual Archetype: Authentic GitHub Dark Dimmed Pull Request & 4-Agent Swarm Kanban Board
(#0D1117 GitHub canvas, #161B22 panels, #238636 Merge PR button, #8957E5 Open/Merged purple badge)."""

from shared.standalone_uis.base_helpers import render_floating_control_bar_and_drawer


def render_sq_6_2(auth_token: str) -> str:
    controls = render_floating_control_bar_and_drawer("6.2", auth_token)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Pull Request #1408 • Antigravity 2.0 4-Agent Swarm | GitHub Enterprise</title>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600;700&display=swap" rel="stylesheet">
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, 'Inter', sans-serif;
      background: #0D1117;
      color: #C9D1D9;
      min-height: 100vh;
      padding-bottom: 80px;
    }}
    .mono {{ font-family: 'JetBrains Mono', monospace; }}

    .gh-header {{
      background: #161B22;
      border-bottom: 1px solid #30363D;
      padding: 14px 28px;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }}
    .gh-btn-merge {{
      background: #238636;
      color: #FFFFFF;
      border: 1px solid rgba(240,246,252,0.1);
      padding: 8px 16px;
      border-radius: 6px;
      font-weight: 600;
      font-size: 13px;
      cursor: pointer;
    }}
    .gh-btn-merge:hover {{ background: #2EA043; }}

    .gh-container {{
      max-width: 1240px;
      margin: 24px auto;
      padding: 0 24px;
    }}
    .pr-badge {{
      background: #238636;
      color: #FFFFFF;
      padding: 5px 14px;
      border-radius: 999px;
      font-size: 13px;
      font-weight: 600;
      display: inline-flex;
      align-items: center;
      gap: 6px;
    }}
    .pr-badge.merged {{ background: #8957E5; }}

    /* 4-Agent Swarm Kanban Strip */
    .swarm-lanes {{
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 14px;
      margin: 22px 0;
    }}
    @media (max-width: 980px) {{
      .swarm-lanes {{ grid-template-columns: repeat(2, 1fr); }}
    }}
    .agent-lane {{
      background: #161B22;
      border: 1px solid #30363D;
      border-radius: 8px;
      padding: 16px;
      cursor: pointer;
      transition: 0.2s;
    }}
    .agent-lane:hover, .agent-lane.active {{
      border-color: #58A6FF;
      box-shadow: 0 0 0 2px rgba(88,166,255,0.2);
    }}

    .gh-box {{
      background: #161B22;
      border: 1px solid #30363D;
      border-radius: 8px;
      overflow: hidden;
      margin-bottom: 20px;
    }}
    .gh-box-header {{
      background: #21262D;
      padding: 10px 16px;
      border-bottom: 1px solid #30363D;
      font-size: 12.5px;
      font-weight: 600;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}
  </style>
</head>
<body>

  <header class="gh-header">
    <div style="display:flex;align-items:center;gap:12px;">
      <svg height="28" viewBox="0 0 16 16" width="28" fill="#F0F6FC"><path d="M8 0c4.42 0 8 3.58 8 8a8.013 8.013 0 0 1-5.45 7.59c-.4.08-.55-.17-.55-.38 0-.27.01-1.13.01-2.2 0-.75-.25-1.23-.54-1.48 1.78-.2 3.65-.88 3.65-3.95 0-.88-.31-1.59-.82-2.15.08-.2.36-1.02-.08-2.12 0 0-.67-.22-2.2.82-.64-.18-1.32-.27-2-.27-.68 0-1.36.09-2 .27-1.53-1.03-2.2-.82-2.2-.82-.44 1.1-.16 1.92-.08 2.12-.51.56-.82 1.28-.82 2.15 0 3.06 1.86 3.75 3.64 3.95-.23.2-.44.55-.51 1.07-.46.21-1.61.55-2.33-.66-.15-.24-.6-.83-1.23-.82-.67.01-.27.38.01.53.34.19.73.9.82 1.13.16.45.68 1.31 2.69.94 0 .67.01 1.3.01 1.49 0 .21-.15.45-.55.38A7.995 7.995 0 0 1 0 8c0-4.42 3.58-8 8-8Z"></path></svg>
      <div>
        <div style="font-size:14px;font-weight:600;color:#58A6FF;">rocket-companies / <strong style="color:#F0F6FC;">closing-microservice-hub</strong></div>
        <div class="mono" style="font-size:11px;color:#8B949E;">Antigravity 2.0 Multi-Agent Swarm (`workspace="share"` Jujutsu VCS)</div>
      </div>
    </div>

    <div style="display:flex;align-items:center;gap:10px;">
      <div class="mono" style="background:#0D1117;border:1px solid #30363D;padding:5px 10px;border-radius:6px;font-size:11px;">
        Model:
        <select id="app-model-select" onchange="window.syncSelectedModel(this.value)" class="mono" style="background:transparent;color:#58A6FF;font-weight:700;border:none;outline:none;font-size:11px;cursor:pointer;">
          <option value="gemini-4-argon" style="background:#0D1117;">gemini-4-argon</option>
          <option value="gemini-3.8-flash" style="background:#0D1117;">gemini-3.8-flash</option>
        </select>
      </div>
      <button class="gh-btn-merge" onclick="window.runLiveVertexAI()" id="swarm-btn">⚡ Re-Run 4-Agent Swarm Synthesis</button>
    </div>
  </header>

  <main class="gh-container">
    <!-- PR Title & Status -->
    <div style="border-bottom:1px solid #30363D;padding-bottom:16px;">
      <div style="display:flex;align-items:center;gap:12px;flex-wrap:wrap;">
        <h1 style="font-size:24px;font-weight:600;color:#F0F6FC;">feat(escrow): Autonomous FHA/VA Escrow Cushion Calculator API & OpenAPI 3.1 Spec <span style="color:#8B949E;font-weight:400;">#1408</span></h1>
      </div>
      <div style="margin-top:10px;display:flex;align-items:center;gap:12px;flex-wrap:wrap;">
        <span class="pr-badge" id="pr-state-badge">🟣 Open • Ready to Merge</span>
        <span class="mono" style="font-size:12px;color:#8B949E;">
          <strong style="color:#F0F6FC;">antigravity-swarm[bot]</strong> wants to merge 4 commits into <code style="background:#161B22;padding:2px 6px;border-radius:4px;">main</code> from <code style="background:#161B22;padding:2px 6px;border-radius:4px;">feat/jira-rkt-4910-escrow-api</code>
        </span>
      </div>
    </div>

    <!-- 4-AGENT SWARM KANBAN LANES -->
    <section class="swarm-lanes">
      <div class="agent-lane active" onclick="inspectAgent(1, this)">
        <div class="mono" style="font-size:11px;color:#58A6FF;font-weight:700;">AGENT 1 • ARCHITECT</div>
        <div style="font-weight:700;font-size:14px;color:#F0F6FC;margin:4px 0;">OpenAPI 3.1 & RESPA Schema</div>
        <div class="mono" style="font-size:11px;color:#3FB950;">✓ Completed in 4.2s</div>
      </div>
      <div class="agent-lane" onclick="inspectAgent(2, this)">
        <div class="mono" style="font-size:11px;color:#D2A8FF;font-weight:700;">AGENT 2 • CODER</div>
        <div style="font-weight:700;font-size:14px;color:#F0F6FC;margin:4px 0;">FastAPI + Pydantic v2 Service</div>
        <div class="mono" style="font-size:11px;color:#3FB950;">✓ Completed in 6.8s</div>
      </div>
      <div class="agent-lane" onclick="inspectAgent(3, this)">
        <div class="mono" style="font-size:11px;color:#F2CC60;font-weight:700;">AGENT 3 • QA ENGINEER</div>
        <div style="font-weight:700;font-size:14px;color:#F0F6FC;margin:4px 0;" id="qa-lane-title">96.4% Pytest Coverage</div>
        <div class="mono" style="font-size:11px;color:#3FB950;">✓ 28 Edge-Case Tests Pass</div>
      </div>
      <div class="agent-lane" onclick="inspectAgent(4, this)">
        <div class="mono" style="font-size:11px;color:#FF7B72;font-weight:700;">AGENT 4 • SECOPS</div>
        <div style="font-weight:700;font-size:14px;color:#F0F6FC;margin:4px 0;">OWASP & SBOM Gate</div>
        <div class="mono" style="font-size:11px;color:#3FB950;">✓ 0 High/Critical CVEs</div>
      </div>
    </section>

    <div style="display:grid;grid-template-columns:1fr 360px;gap:20px;">
      <!-- Left: PR Diff & Conversation -->
      <div>
        <div class="gh-box">
          <div class="gh-box-header">
            <span id="diff-file-title" class="mono">📄 services/escrow_cushion/router.py (+184 -0)</span>
            <span class="mono" style="color:#3FB950;" id="pr-model-tag">Synthesized via gemini-4-argon</span>
          </div>
          <pre id="pr-code-body" class="mono" style="padding:16px;font-size:12px;line-height:1.6;color:#E6EDF3;overflow-x:auto;background:#0D1117;">+ from fastapi import APIRouter, Depends
+ from pydantic import BaseModel, Field
+ 
+ router = APIRouter(prefix="/v1/escrow-cushion", tags=["RESPA § 1024.17"])
+ 
+ class EscrowCushionRequest(BaseModel):
+     annual_tax: float = Field(..., gt=0)
+     annual_hazard_ins: float = Field(..., gt=0)
+     state_code: str = Field(..., min_length=2, max_length=2)
+ 
+ @router.post("/calculate")
+ def calculate_respa_cushion(req: EscrowCushionRequest):
+     # Enforces 12 CFR § 1024.17 1/6th (2-month) statutory cushion cap
+     monthly_base = round((req.annual_tax + req.annual_hazard_ins) / 12.0, 2)
+     max_ statutory_cushion = round(monthly_base * 2.0, 2)
+     return {{"monthly_escrow": monthly_base, "max_respa_cushion": max_statutory_cushion}}</pre>
        </div>

        <!-- Merge Box -->
        <div class="gh-box" style="padding:16px;display:flex;justify-content:space-between;align-items:center;">
          <div>
            <div style="font-weight:700;color:#3FB950;font-size:14px;">✓ All 4 Antigravity Swarm Checks Have Passed</div>
            <div style="font-size:12px;color:#8B949E;margin-top:2px;" id="swarm-summary-text">100% OpenAPI schema compliance • 96.4% pytest coverage • 0 SAST findings</div>
          </div>
          <button class="gh-btn-merge" onclick="mergePullRequest()">🔀 Squash and Merge PR #1408</button>
        </div>
      </div>

      <!-- Right: Swarm Telemetry & Sliders -->
      <aside class="gh-box" style="padding:18px;height:fit-content;">
        <div style="font-weight:700;font-size:13px;color:#F0F6FC;margin-bottom:12px;">🎛️ Swarm Complexity & QA Calibration</div>
        <div style="margin-bottom:14px;">
          <div class="mono" style="display:flex;justify-content:space-between;font-size:11.5px;margin-bottom:4px;">
            <span>Story Points (Jira PRD):</span>
            <strong id="lbl-pts" style="color:#58A6FF;">8 pts</strong>
          </div>
          <input type="range" id="sl-pts" min="3" max="21" step="1" value="8" style="width:100%;accent-color:#58A6FF;" oninput="recalcSwarm()">
        </div>
        <div style="margin-bottom:14px;">
          <div class="mono" style="display:flex;justify-content:space-between;font-size:11.5px;margin-bottom:4px;">
            <span>Target Pytest Coverage (%):</span>
            <strong id="lbl-cov" style="color:#3FB950;">96.4%</strong>
          </div>
          <input type="range" id="sl-cov" min="80" max="100" step="0.5" value="96.4" style="width:100%;accent-color:#238636;" oninput="recalcSwarm()">
        </div>
        <div class="mono" style="font-size:11px;color:#8B949E;line-height:1.6;padding-top:10px;border-top:1px solid #30363D;" id="sbx-metrics-box">
          • Cycle Time: 4.5 Days -> 6m 12s<br>
          • Parallel Agents: 4 Jujutsu Worktrees
        </div>
      </aside>
    </div>
  </main>

  {controls}

  <script>
    function mergePullRequest() {{
      const b = document.getElementById('pr-state-badge');
      b.className = 'pr-badge merged';
      b.innerText = '🟣 Merged into main (commit 9f4a21c)';
    }}

    function inspectAgent(id, el) {{
      document.querySelectorAll('.agent-lane').forEach(l => l.classList.remove('active'));
      el.classList.add('active');
      const title = document.getElementById('diff-file-title');
      const body = document.getElementById('pr-code-body');
      if (id === 1) {{
        title.innerText = '📄 openapi/escrow_cushion_v1.yaml (+92 -0)';
        body.textContent = `openapi: 3.1.0\ninfo:\n  title: Rocket RESPA Escrow Cushion API\n  version: 1.0.0\npaths:\n  /v1/escrow-cushion/calculate:\n    post:\n      summary: Compute 12 CFR 1024.17 2-Month Cushion Cap`;
      }} else if (id === 2) {{
        title.innerText = '📄 services/escrow_cushion/router.py (+184 -0)';
      }} else if (id === 3) {{
        title.innerText = '🧪 tests/test_escrow_respa_limits.py (+140 -0)';
        body.textContent = `def test_respa_two_month_cushion_cap():\n    res = calculate_respa_cushion(EscrowCushionRequest(annual_tax=4800, annual_hazard_ins=1200, state_code="MI"))\n    assert res["monthly_escrow"] == 500.00\n    assert res["max_respa_cushion"] == 1000.00  # Strictly <= 1/6th annual disbursements`;
      }} else {{
        title.innerText = '🛡️ secops/sbom_attestation.json (+48 -0)';
        body.textContent = `{{"scanner": "Google Cloud Artifact Analysis + Model Armor", "critical_vulnerabilities": 0, "high_vulnerabilities": 0, "slsa_level": "SLSA Build L3 Verified"}}`;
      }}
    }}

    async function recalcSwarm() {{
      const pts = parseInt(document.getElementById('sl-pts').value);
      const cov = parseFloat(document.getElementById('sl-cov').value);
      document.getElementById('lbl-pts').innerText = pts + ' pts';
      document.getElementById('lbl-cov').innerText = cov.toFixed(1) + '%';
      document.getElementById('qa-lane-title').innerText = cov.toFixed(1) + '% Pytest Coverage';

      const res = await fetch('/api/sandbox', {{
        method: 'POST',
        headers: {{'Content-Type': 'application/json'}},
        body: JSON.stringify({{code: '6.2', action: 'simulate_software_factory', params: {{story_points: pts, coverage_pct: cov}}}})
      }});
      const data = await res.json();
      if (data.ok && data.metrics) {{
        document.getElementById('sbx-metrics-box').innerHTML =
          Object.values(data.metrics).map(v => '• ' + v).join('<br>');
      }}
    }}

    window.runLiveVertexAI = async function() {{
      const btn = document.getElementById('swarm-btn');
      const model = window.getSelectedModel();
      btn.innerText = '⏳ Running Swarm on ' + model + '...';
      const pts = parseInt(document.getElementById('sl-pts').value);
      const cov = parseFloat(document.getElementById('sl-cov').value);
      try {{
        const res = await fetch('/api/run-demo', {{
          method: 'POST',
          headers: {{'Content-Type': 'application/json'}},
          body: JSON.stringify({{code: '6.2', model: model, params: {{story_points: pts, coverage_pct: cov}}}})
        }});
        const data = await res.json();
        document.getElementById('pr-model-tag').innerText = 'Synthesized via ' + (data.model_used || model);
        if (data.structured_data && (data.structured_data.pr_summary || data.structured_data.executive_summary)) {{
          document.getElementById('swarm-summary-text').innerHTML = data.structured_data.pr_summary || data.structured_data.executive_summary;
        }} else if (data.output) {{
          document.getElementById('swarm-summary-text').innerText = data.output;
        }}
      }} catch (e) {{}}
      finally {{
        btn.innerText = '⚡ Re-Run 4-Agent Swarm Synthesis';
      }}
    }};
  </script>
</body>
</html>"""
