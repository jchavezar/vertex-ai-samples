# -*- coding: utf-8 -*-
"""Square 6.1: Autonomous Vulnerability Trace & Repair (CodeMender) — Standalone UI Design File.
Visual Archetype: Authentic VS Code Dark+ Security IDE & Live gVisor Exploit Terminal
(#1E1E1E editor, #252526 file explorer, #333333 activity bar, #007ACC bottom status bar,
side-by-side vulnerable vs patched AST diff + interactive bottom pytest exploit terminal)."""

from shared.standalone_uis.base_helpers import render_floating_control_bar_and_drawer


def render_sq_6_1(auth_token: str) -> str:
    controls = render_floating_control_bar_and_drawer("6.1", auth_token)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>CodeMender Security IDE — VS Code Dark+ | Rocket AppSec</title>
  <link href="https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500;600;700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: 'Inter', sans-serif;
      background: #1E1E1E;
      color: #CCCCCC;
      height: 100vh;
      overflow: hidden;
      display: flex;
      flex-direction: column;
    }}
    .code {{ font-family: 'Fira Code', monospace; }}

    /* VS Code Title Bar */
    .vscode-titlebar {{
      height: 38px;
      background: #323233;
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 14px;
      font-size: 12px;
      border-bottom: 1px solid #1E1E1E;
    }}
    .window-dots {{ display: flex; gap: 7px; }}
    .dot {{ width: 11px; height: 11px; border-radius: 50%; }}

    /* VS Code Main Workspace */
    .vscode-main {{
      display: grid;
      grid-template-columns: 48px 250px 1fr;
      flex: 1;
      overflow: hidden;
    }}
    .activity-bar {{
      background: #333333;
      display: flex;
      flex-direction: column;
      align-items: center;
      padding-top: 12px;
      gap: 18px;
      font-size: 18px;
    }}
    .explorer-pane {{
      background: #252526;
      border-right: 1px solid #1E1E1E;
      padding: 10px 0;
      font-size: 12.5px;
    }}
    .file-row {{
      padding: 6px 18px;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 8px;
      color: #CCCCCC;
    }}
    .file-row:hover {{ background: #2A2D2E; }}
    .file-row.active {{ background: #37373D; color: #FFFFFF; font-weight: 600; }}

    /* Editor + Bottom Terminal Split */
    .editor-stack {{
      display: grid;
      grid-template-rows: 36px 1fr 230px;
      overflow: hidden;
    }}
    .editor-tabs {{
      background: #252526;
      display: flex;
      align-items: center;
      border-bottom: 1px solid #1E1E1E;
    }}
    .tab-item {{
      height: 36px;
      padding: 0 16px;
      background: #1E1E1E;
      color: #FFFFFF;
      border-top: 2px solid #007ACC;
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 12px;
      font-family: 'Fira Code', monospace;
    }}
    .diff-grid {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      overflow-y: auto;
      background: #1E1E1E;
    }}
    .diff-col {{
      padding: 16px;
      border-right: 1px solid #2D2D2D;
      font-family: 'Fira Code', monospace;
      font-size: 12px;
      line-height: 1.65;
    }}
    .line-del {{
      background: rgba(244, 63, 94, 0.18);
      border-left: 3px solid #F43F5E;
      padding: 2px 8px;
      color: #FDA4AF;
    }}
    .line-add {{
      background: rgba(16, 185, 129, 0.18);
      border-left: 3px solid #10B981;
      padding: 2px 8px;
      color: #6EE7B7;
    }}

    /* Bottom Terminal */
    .terminal-pane {{
      background: #181818;
      border-top: 1px solid #333333;
      padding: 12px 18px 60px 18px;
      font-family: 'Fira Code', monospace;
      font-size: 11.5px;
      overflow-y: auto;
    }}
    .vscode-statusbar {{
      height: 24px;
      background: #007ACC;
      color: #FFFFFF;
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 12px;
      font-size: 11px;
      font-family: 'Fira Code', monospace;
    }}
    .cm-btn {{
      background: #0E639C;
      color: #FFFFFF;
      border: none;
      padding: 5px 12px;
      border-radius: 3px;
      font-family: 'Fira Code', monospace;
      font-size: 11px;
      font-weight: 600;
      cursor: pointer;
    }}
    .cm-btn.green {{ background: #16825D; }}
  </style>
</head>
<body>

  <!-- VS CODE TOP TITLEBAR -->
  <header class="vscode-titlebar">
    <div style="display:flex;align-items:center;gap:12px;">
      <div class="window-dots">
        <div class="dot" style="background:#FF5F56;"></div>
        <div class="dot" style="background:#FFBD2E;"></div>
        <div class="dot" style="background:#27C93F;"></div>
      </div>
      <span class="code" style="color:#E2E8F0;font-weight:600;">escrow_wire_router.py — DeepMind CodeMender IDE (rocket-core-closing)</span>
    </div>

    <div style="display:flex;align-items:center;gap:8px;">
      <span class="code" style="font-size:11px;color:#9CDCFE;">Model:</span>
      <select id="app-model-select" onchange="window.syncSelectedModel(this.value)" class="code" style="background:#252526;color:#4EC9B0;border:1px solid #3C3C3C;padding:3px 8px;border-radius:3px;font-size:11px;cursor:pointer;">
        <option value="gemini-4-argon">gemini-4-argon</option>
        <option value="gemini-3.8-flash">gemini-3.8-flash</option>
      </select>
      <button class="cm-btn" onclick="runExploitTrace()">▶ 1. Run PoC Exploit (`cm verify`)</button>
      <button class="cm-btn green" onclick="window.runLiveVertexAI()" id="patch-btn">🛠️ 2. Synthesize & Verify AST Patch (`cm fix`)</button>
    </div>
  </header>

  <div class="vscode-main">
    <!-- Activity Bar -->
    <div class="activity-bar">
      <div title="Explorer">📁</div>
      <div title="Search">🔍</div>
      <div title="CodeMender Shield" style="color:#4EC9B0;">🛡️</div>
      <div title="Git PR">🌿</div>
    </div>

    <!-- Explorer File Tree -->
    <aside class="explorer-pane">
      <div class="code" style="font-size:10.5px;color:#858585;padding:4px 18px 8px 18px;text-transform:uppercase;">ROCKET-CLOSING-API</div>
      <div class="file-row active" onclick="switchCve('SSRF', this)">🐍 escrow_wire_router.py <span style="color:#F43F5E;margin-left:auto;font-size:10px;">CWE-918</span></div>
      <div class="file-row" onclick="switchCve('SQLI', this)">🐍 lien_payoff_lookup.py <span style="color:#F59E0B;margin-left:auto;font-size:10px;">CWE-89</span></div>
      <div class="file-row" onclick="switchCve('TEST', this)">🧪 test_codemender_poc.py <span style="color:#10B981;margin-left:auto;font-size:10px;">PASS</span></div>
      <div class="file-row">📄 codemender.yaml</div>

      <div style="margin:20px 14px;padding:12px;background:#1E1E1E;border:1px solid #333333;border-radius:4px;">
        <div class="code" style="font-size:10.5px;color:#4EC9B0;margin-bottom:8px;">🎛️ gVisor Regression Suite</div>
        <div class="code" style="display:flex;justify-content:space-between;font-size:11px;margin-bottom:4px;">
          <span>Test Suite Count:</span>
          <strong id="lbl-tests" style="color:#4EC9B0;">142</strong>
        </div>
        <input type="range" id="sl-tests" min="50" max="300" step="10" value="142" style="width:100%;accent-color:#007ACC;" oninput="recalcCodeMender()">
      </div>
    </aside>

    <!-- Editor + Bottom Terminal -->
    <div class="editor-stack">
      <div class="editor-tabs">
        <div class="tab-item">
          <span>🐍 escrow_wire_router.py (Working Tree ↔ CodeMender AST Patch)</span>
        </div>
      </div>

      <!-- Side-by-Side Diff Viewer -->
      <div class="diff-grid">
        <div class="diff-col">
          <div style="color:#F43F5E;font-weight:700;margin-bottom:8px;">❌ BEFORE: Vulnerable Endpoint (CWE-918 SSRF + BOLA)</div>
          <pre id="code-before" style="white-space:pre-wrap;color:#D4D4D4;">14  @app.post("/v1/escrow/webhook-verify")
15  def verify_title_wire_instruction(loan_id: str, callback_url: str):
16      # CRITICAL FLAW 1: No ownership check on loan_id (BOLA)
17      wire = db.execute(f"SELECT * FROM wires WHERE loan_id='{{loan_id}}'")
<div class="line-del">18      # CRITICAL FLAW 2: Unvalidated SSRF fetches internal metadata!</div>
<div class="line-del">19      resp = requests.get(callback_url, timeout=5)</div>
20      return {{"status": resp.status_code, "wire": wire}}</pre>
        </div>

        <div class="diff-col">
          <div style="color:#10B981;font-weight:700;margin-bottom:8px;">✅ AFTER: CodeMender Verified Patch (0 Regressions)</div>
          <pre id="code-after" style="white-space:pre-wrap;color:#D4D4D4;">14  ALLOWED_TITLE_HOSTS = {{"api.amrock.com", "closing.rocketmortgage.com"}}
15  
16  @app.post("/v1/escrow/webhook-verify")
17  def verify_title_wire_instruction(loan_id: str, callback_url: str, user=Depends(auth_borrower)):
<div class="line-add">18      parsed = urllib.parse.urlparse(callback_url)</div>
<div class="line-add">19      if parsed.scheme != "https" or parsed.hostname not in ALLOWED_TITLE_HOSTS:</div>
<div class="line-add">20          raise SecurityError("Blocked SSRF: Untrusted Title Host")</div>
<div class="line-add">21      wire = db.execute("SELECT * FROM wires WHERE loan_id=:id AND borrower_id=:uid", {{"id": loan_id, "uid": user.id}})</div>
22      return {{"status": 200, "wire_verified": bool(wire)}}</pre>
        </div>
      </div>

      <!-- Bottom Interactive gVisor Terminal -->
      <div class="terminal-pane" id="terminal-out">
        <div style="color:#569CD6;margin-bottom:4px;">TERMINAL • gVisor Isolated Sandbox (`runsc` rootless container)</div>
        <div id="term-lines">
          <span style="color:#4EC9B0;">rocket@gvisor-sbx:~/closing-api$</span> cm verify --cve CWE-918 --target escrow_wire_router.py<br>
          <span style="color:#F43F5E;">[EXPLOIT REPRODUCED]</span> SSRF payload `http://169.254.169.254/computeMetadata/v1/` leaked service token (HTTP 200).<br>
          <span style="color:#4EC9B0;">rocket@gvisor-sbx:~/closing-api$</span> cm fix --verify-regression 142<br>
          <span style="color:#10B981;">[PATCH VERIFIED]</span> Exploit blocked (SecurityError raised) • <strong>142 / 142 unit tests PASSED (0.41s)</strong>.
        </div>
      </div>
    </div>
  </div>

  <!-- VS CODE STATUS BAR -->
  <footer class="vscode-statusbar">
    <div>🌿 fix/codemender-cwe-918-ssrf • 🛡️ 0 Critical Vulnerabilities Remaining</div>
    <div id="status-model-tag">Engine: gemini-4-argon • UTF-8 • Python 3.12</div>
  </footer>

  {controls}

  <script>
    function switchCve(mode, el) {{
      document.querySelectorAll('.file-row').forEach(r => r.classList.remove('active'));
      el.classList.add('active');
      runExploitTrace();
    }}

    function runExploitTrace() {{
      const term = document.getElementById('term-lines');
      term.innerHTML += `<br><span style="color:#DCDCAA;">[gVisor Sandbox]</span> Re-running exploit PoC against patched AST... <span style="color:#10B981;">BLOCKED (SecurityError: Untrusted Title Host)</span>`;
    }}

    async function recalcCodeMender() {{
      const tests = parseInt(document.getElementById('sl-tests').value);
      document.getElementById('lbl-tests').innerText = tests;
      const res = await fetch('/api/sandbox', {{
        method: 'POST',
        headers: {{'Content-Type': 'application/json'}},
        body: JSON.stringify({{code: '6.1', action: 'verify_codemender_patch', params: {{regression_tests: tests}}}})
      }});
      const data = await res.json();
      if (data.ok && data.metrics) {{
        document.getElementById('term-lines').innerHTML +=
          `<br><span style="color:#10B981;">[SANDBOX]</span> ${{data.metrics.regression_test_suite || (tests + '/' + tests + ' PASSED')}}`;
      }}
    }}

    window.runLiveVertexAI = async function() {{
      const btn = document.getElementById('patch-btn');
      const model = window.getSelectedModel();
      btn.innerText = '⏳ Synthesizing AST Patch on ' + model + '...';
      document.getElementById('status-model-tag').innerText = 'Engine: ' + model + ' • Running cm fix...';
      const tests = parseInt(document.getElementById('sl-tests').value);
      try {{
        const res = await fetch('/api/run-demo', {{
          method: 'POST',
          headers: {{'Content-Type': 'application/json'}},
          body: JSON.stringify({{code: '6.1', model: model, params: {{regression_tests: tests}}}})
        }});
        const data = await res.json();
        const usedModel = data.model_used || model;
        document.getElementById('status-model-tag').innerText = 'Engine: ' + usedModel + ' • Patch Verified';
        const summary = (data.structured_data && (data.structured_data.root_cause_analysis || data.structured_data.executive_summary)) || data.output || 'AST Patch Verified.';
        document.getElementById('term-lines').innerHTML +=
          `<br><span style="color:#4EC9B0;">[${{usedModel}}]</span> ${{summary}}`;
      }} catch (e) {{}}
      finally {{
        btn.innerText = '🛠️ 2. Synthesize & Verify AST Patch (`cm fix`)';
      }}
    }};
  </script>
</body>
</html>"""
