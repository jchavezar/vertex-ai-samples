# -*- coding: utf-8 -*-
"""Square 6.2: CodeMender Vulnerability Auto-Patcher — DeepMind CodeMender + Gemini 4 Argon
Design Style: Snyk / GitHub Dependabot Security Advisory Report (Light Mode)
(#F8FAFC clean security advisory page, #B91C1C CVE high-severity badge,
#15803D verified patch green, Outfit + IBM Plex Mono).
"""

from shared.standalone_uis.base_helpers import render_floating_control_bar_and_drawer


def render_sq_6_2(auth_token: str) -> str:
    code = "6.2"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>CVE-2026-RKT01 Advisory & CodeMender Auto-Patcher | Rocket AppSec</title>
  <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800&family=IBM+Plex+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    :root {{
      --bg: #F8FAFC;
      --card: #FFFFFF;
      --cve-red: #B91C1C;
      --cve-bg: #FEF2F2;
      --cve-border: #FECACA;
      --patch-green: #15803D;
      --patch-bg: #F0FDF4;
      --patch-border: #BBF7D0;
      --ink: #0F172A;
      --ink-muted: #475569;
      --border: #E2E8F0;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      background-color: var(--bg);
      color: var(--ink);
      font-family: 'Outfit', -apple-system, BlinkMacSystemFont, sans-serif;
      min-height: 100vh;
      padding-bottom: 92px;
    }}
    .mono {{ font-family: 'IBM Plex Mono', monospace; }}

    /* Snyk / Dependabot Security Advisory Header */
    .advisory-header {{
      background: var(--card);
      border-bottom: 1px solid var(--border);
      padding: 18px 32px;
    }}
    .adv-top-row {{
      max-width: 1420px;
      margin: 0 auto;
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 14px;
    }}
    .cve-pill-row {{
      display: flex;
      align-items: center;
      gap: 10px;
      flex-wrap: wrap;
      margin-bottom: 6px;
    }}
    .cve-badge {{
      background: var(--cve-red);
      color: #FFFFFF;
      font-family: 'IBM Plex Mono', monospace;
      font-size: 11.5px;
      font-weight: 700;
      padding: 4px 10px;
      border-radius: 5px;
      letter-spacing: 0.03em;
    }}
    .cve-badge.patched {{
      background: var(--patch-green);
    }}
    .cvss-chip {{
      background: var(--cve-bg);
      color: var(--cve-red);
      border: 1px solid var(--cve-border);
      font-family: 'IBM Plex Mono', monospace;
      font-size: 11.5px;
      font-weight: 700;
      padding: 3px 9px;
      border-radius: 5px;
    }}
    .adv-title {{
      font-size: 24px;
      font-weight: 800;
      color: var(--ink);
    }}
    .header-actions {{
      display: flex;
      align-items: center;
      gap: 10px;
      flex-wrap: wrap;
    }}
    .model-select-wrap {{
      background: #F1F5F9;
      border: 1px solid var(--border);
      padding: 6px 12px;
      border-radius: 6px;
      font-size: 12px;
      font-weight: 600;
      display: flex;
      align-items: center;
      gap: 6px;
    }}
    .model-select-wrap select {{
      background: transparent;
      border: none;
      font-family: 'IBM Plex Mono', monospace;
      font-weight: 700;
      font-size: 12px;
      color: #1E3A8A;
      outline: none;
      cursor: pointer;
    }}
    .btn-audio {{
      background: #0F172A;
      color: #FFFFFF;
      border: none;
      padding: 9px 16px;
      border-radius: 6px;
      font-family: inherit;
      font-size: 13px;
      font-weight: 600;
      cursor: pointer;
    }}

    /* Vulnerability Selector Bar */
    .vuln-selector-bar {{
      max-width: 1420px;
      margin: 20px auto 0;
      padding: 0 32px;
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
    }}
    .vuln-tab {{
      background: var(--card);
      border: 1px solid var(--border);
      padding: 10px 16px;
      border-radius: 8px;
      font-family: inherit;
      font-size: 13px;
      font-weight: 700;
      color: var(--ink);
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 8px;
      transition: 0.15s;
    }}
    .vuln-tab.active {{
      border-color: var(--cve-red);
      background: var(--cve-bg);
      color: var(--cve-red);
    }}

    /* Main Advisory Body */
    .advisory-main {{
      max-width: 1420px;
      margin: 18px auto;
      padding: 0 32px;
      display: flex;
      flex-direction: column;
      gap: 20px;
    }}
    .diff-comparison-grid {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 20px;
    }}
    @media (max-width: 980px) {{
      .diff-comparison-grid {{ grid-template-columns: 1fr; }}
    }}
    .code-card {{
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 10px;
      overflow: hidden;
      box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04);
    }}
    .code-card.vuln-card {{ border-top: 4px solid var(--cve-red); }}
    .code-card.patch-card {{ border-top: 4px solid var(--patch-green); }}
    .code-card-head {{
      padding: 12px 18px;
      border-bottom: 1px solid var(--border);
      display: flex;
      justify-content: space-between;
      align-items: center;
      background: #FCFDFE;
      font-size: 13px;
      font-weight: 700;
    }}
    .code-pre {{
      padding: 16px 18px;
      font-family: 'IBM Plex Mono', monospace;
      font-size: 12px;
      line-height: 1.65;
      overflow-x: auto;
      white-space: pre;
    }}
    .hl-bad {{
      background: var(--cve-bg);
      color: var(--cve-red);
      display: block;
      margin: 0 -18px;
      padding: 0 18px;
      border-left: 3px solid var(--cve-red);
    }}
    .hl-good {{
      background: var(--patch-bg);
      color: var(--patch-green);
      display: block;
      margin: 0 -18px;
      padding: 0 18px;
      border-left: 3px solid var(--patch-green);
    }}

    /* Verification & Action Panel */
    .verify-bar {{
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 18px 22px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 16px;
    }}
    .btn-patch {{
      background: var(--patch-green);
      color: #FFFFFF;
      border: none;
      padding: 10px 18px;
      border-radius: 7px;
      font-family: inherit;
      font-size: 13.5px;
      font-weight: 700;
      cursor: pointer;
    }}
    .ai-sec-out {{
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 16px;
      font-size: 13px;
      line-height: 1.6;
      display: none;
      white-space: pre-wrap;
    }}
  </style>
</head>
<body>

  <!-- Snyk / Dependabot Light Security Advisory Header -->
  <header class="advisory-header">
    <div class="adv-top-row">
      <div>
        <div class="cve-pill-row">
          <span class="cve-badge" id="cve-status-badge">CVE-2026-RKT01 · HIGH SEVERITY</span>
          <span class="cvss-chip" id="cvss-score-chip">CVSS 8.8 · CWE-89 / CWE-918</span>
          <span class="mono" style="font-size:12px;color:var(--ink-muted);">Target: <code>LoanLookupController.py</code></span>
        </div>
        <h1 class="adv-title">CodeMender Vulnerability Auto-Patcher (CVE-2026-RKT01 · SQLi &amp; SSRF in LoanLookupController.py)</h1>
      </div>
      <div class="header-actions">
        <div class="model-select-wrap">
          <span>Model:</span>
          <select id="app-model-select" onchange="window.syncSelectedModel(this.value)">
            <option value="gemini-4-argon">gemini-4-argon (CodeMender)</option>
            <option value="gemini-3.8-flash">gemini-3.8-flash</option>
          </select>
        </div>
        <button class="btn-audio" onclick="window.playAppSecAudio(this)">
          🔊 Play AppSec Patch Briefing
        </button>
      </div>
    </div>
  </header>

  <!-- Interactive Vulnerability Selector -->
  <nav class="vuln-selector-bar">
    <button class="vuln-tab active" onclick="window.selectVuln('sqli', this)">
      <span>1. SQL Injection (CWE-89 · LoanLookupController.py)</span>
    </button>
    <button class="vuln-tab" onclick="window.selectVuln('ssrf', this)">
      <span>2. SSRF Webhook Bypass (CWE-918 · AppraisalWebhook.py)</span>
    </button>
    <button class="vuln-tab" onclick="window.selectVuln('idor', this)">
      <span>3. IDOR Closing Doc (CWE-639 · ClosingVaultHandler.py)</span>
    </button>
  </nav>

  <!-- Side-by-Side Vulnerable vs Parameterized Patch Viewer -->
  <main class="advisory-main">
    <div class="diff-comparison-grid">
      <!-- Left: Vulnerable Source -->
      <section class="code-card vuln-card">
        <div class="code-card-head">
          <span style="color:var(--cve-red);">✗ VULNERABLE SOURCE DETECTED BY SAST</span>
          <span class="mono" id="vuln-file-lbl" style="font-size:11.5px;color:var(--ink-muted);">controllers/LoanLookupController.py:74</span>
        </div>
        <div class="code-pre" id="vuln-code-pane">@app.get("/api/v1/loans/search")
def search_borrower_loan(loan_num: str, ssn_last4: str):
    cursor = db.cursor()
    # CRITICAL CWE-89: Raw f-string SQL interpolation
<span class="hl-bad">-   query = f"SELECT * FROM loans WHERE loan_id = '{{loan_num}}' AND ssn4 = '{{ssn_last4}}'"</span>
<span class="hl-bad">-   cursor.execute(query)</span>
    return jsonify(cursor.fetchall())</div>
      </section>

      <!-- Right: CodeMender Verified Parameterized Patch -->
      <section class="code-card patch-card">
        <div class="code-card-head">
          <span style="color:var(--patch-green);">✓ CODEMENDER PARAMETERIZED AUTO-PATCH</span>
          <span class="mono" style="font-size:11.5px;color:var(--patch-green);"> Semgrep + Exploit Replay: 0 Findings</span>
        </div>
        <div class="code-pre" id="patch-code-pane">@app.get("/api/v1/loans/search")
def search_borrower_loan(loan_num: str, ssn_last4: str):
    cursor = db.cursor()
    # FIXED: Strict bind parameters + regex loan_id validation
<span class="hl-good">+   if not LOAN_ID_PATTERN.fullmatch(loan_num): raise ValueError("Invalid Loan ID")</span>
<span class="hl-good">+   query = "SELECT loan_id, status, rate FROM loans WHERE loan_id = %s AND ssn4 = %s"</span>
<span class="hl-good">+   cursor.execute(query, (loan_num, ssn_last4))</span>
    return jsonify(cursor.fetchall())</div>
      </section>
    </div>

    <!-- One-Click Apply & Verify CodeMender Patch Bar -->
    <section class="verify-bar">
      <div>
        <div style="font-size:15px;font-weight:700;color:var(--ink);" id="patch-verify-headline">
          Automated Exploit Replay &amp; Regression Suite Ready (`sqlmap` + 48 Pytest Cases)
        </div>
        <div style="font-size:13px;color:var(--ink-muted);margin-top:2px;" id="patch-verify-sub">
          Click "Apply &amp; Verify CodeMender Patch" to run AST transform and block payload <code>' OR 1=1 --</code>.
        </div>
      </div>
      <div style="display:flex;gap:10px;flex-wrap:wrap;">
        <button class="btn-patch" id="apply-patch-btn" onclick="window.applyCodeMenderPatch()">
          Apply &amp; Verify CodeMender Patch
        </button>
        <button class="btn-audio" style="background:#1E3A8A;" onclick="window.runLiveVertexAI()">
          ⚡ Generate Live Vertex AI Security Advisory
        </button>
      </div>
    </section>

    <div id="ai-sec-output" class="ai-sec-out"></div>
  </main>

  <script>
    const VULNS = {{
      sqli: {{
        file: "controllers/LoanLookupController.py:74",
        cvss: "CVSS 8.8 · CWE-89 SQL Injection",
        vulnCode: `@app.get("/api/v1/loans/search")\\ndef search_borrower_loan(loan_num: str, ssn_last4: str):\\n    cursor = db.cursor()\\n    # CRITICAL CWE-89: Raw f-string SQL interpolation\\n<span class="hl-bad">-   query = f"SELECT * FROM loans WHERE loan_id = '{{loan_num}}' AND ssn4 = '{{ssn_last4}}'"</span>\\n<span class="hl-bad">-   cursor.execute(query)</span>\\n    return jsonify(cursor.fetchall())`,
        patchCode: `@app.get("/api/v1/loans/search")\\ndef search_borrower_loan(loan_num: str, ssn_last4: str):\\n    cursor = db.cursor()\\n    # FIXED: Strict bind parameters + regex loan_id validation\\n<span class="hl-good">+   if not LOAN_ID_PATTERN.fullmatch(loan_num): raise ValueError("Invalid Loan ID")</span>\\n<span class="hl-good">+   query = "SELECT loan_id, status, rate FROM loans WHERE loan_id = %s AND ssn4 = %s"</span>\\n<span class="hl-good">+   cursor.execute(query, (loan_num, ssn_last4))</span>\\n    return jsonify(cursor.fetchall())`
      }},
      ssrf: {{
        file: "webhooks/AppraisalWebhook.py:118",
        cvss: "CVSS 8.6 · CWE-918 SSRF Metadata Access",
        vulnCode: `@app.post("/api/v1/appraisal/callback")\\ndef fetch_amc_pdf(callback_url: str):\\n    # CRITICAL CWE-918: Unvalidated URL allows 169.254.169.254 metadata fetch\\n<span class="hl-bad">-   resp = requests.get(callback_url, timeout=5)</span>\\n    return store_appraisal_doc(resp.content)`,
        patchCode: `@app.post("/api/v1/appraisal/callback")\\ndef fetch_amc_pdf(callback_url: str):\\n    # FIXED: Hostname allowlist + private CIDR blocklist enforcement\\n<span class="hl-good">+   parsed = verify_allowed_amc_host(callback_url, ALLOWED_AMC_DOMAINS)</span>\\n<span class="hl-good">+   resp = requests.get(parsed.geturl(), timeout=5, allow_redirects=False)</span>\\n    return store_appraisal_doc(resp.content)`
      }},
      idor: {{
        file: "handlers/ClosingVaultHandler.py:52",
        cvss: "CVSS 8.1 · CWE-639 Broken Object Level Auth",
        vulnCode: `@app.get("/api/v1/closing-disclosure/<doc_id>")\\ndef download_closing_pdf(doc_id: str, current_user: User):\\n    # CRITICAL CWE-639: Fetches CD PDF without verifying borrower ownership\\n<span class="hl-bad">-   return gcs_bucket.blob(f"cd_pdfs/{{doc_id}}.pdf").download_as_bytes()</span>`,
        patchCode: `@app.get("/api/v1/closing-disclosure/<doc_id>")\\ndef download_closing_pdf(doc_id: str, current_user: User):\\n    # FIXED: Enforce row-level borrower ownership check before GCS signed read\\n<span class="hl-good">+   assert_borrower_owns_document(current_user.uid, doc_id)</span>\\n<span class="hl-good">+   return gcs_bucket.blob(f"cd_pdfs/{{doc_id}}.pdf").download_as_bytes()</span>`
      }}
    }};

    window.selectVuln = function(key, btnEl) {{
      document.querySelectorAll('.vuln-tab').forEach(b => b.classList.remove('active'));
      if (btnEl) btnEl.classList.add('active');
      const v = VULNS[key];
      document.getElementById('vuln-file-lbl').innerText = v.file;
      document.getElementById('cvss-score-chip').innerText = v.cvss;
      document.getElementById('vuln-code-pane').innerHTML = v.vulnCode;
      document.getElementById('patch-code-pane').innerHTML = v.patchCode;
    }};

    window.applyCodeMenderPatch = function() {{
      const badge = document.getElementById('cve-status-badge');
      badge.className = "cve-badge patched";
      badge.innerText = "✓ CVE-2026-RKT01 PATCHED & VERIFIED";
      document.getElementById('patch-verify-headline').innerText = "✓ CodeMender Patch Applied · 0 SAST Findings · All 48 Regression Tests Passed";
      document.getElementById('patch-verify-sub').innerText = "Exploit replay payloads (' OR 1=1 --, 169.254.169.254, unauthorized doc_id) blocked with HTTP 400/403.";
      const btn = document.getElementById('apply-patch-btn');
      btn.innerText = "✓ Patch Merged & Attested";
    }};

    window.playAppSecAudio = function(btnEl) {{
      const msg = "AppSec Security Briefing for Advisory CVE-2026-RKT01. DeepMind CodeMender detected three critical vulnerabilities in the Loan Lookup and Closing Vault controllers: a SQL Injection in LoanLookupController, a Server-Side Request Forgery in AppraisalWebhook, and an Insecure Direct Object Reference in ClosingVaultHandler. CodeMender synthesized parameterized bind queries, strict AMC domain allowlists, and borrower ownership assertions, verified against live exploit replay in 3.8 seconds.";
      window.playLiveCallClip(msg, "Fenrir", "Rocket Principal AppSec Architect", btnEl);
    }};

    window.runLiveVertexAI = async function() {{
      const out = document.getElementById('ai-sec-output');
      out.style.display = 'block';
      const model = window.getSelectedModel ? window.getSelectedModel() : 'gemini-4-argon';
      out.textContent = `Synthesizing CodeMender SAST Patch & Exploit Verification Report via Vertex AI (${{model}})...`;
      try {{
        const res = await fetch('/api/run-demo', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{
            code: '6.2',
            model: model,
            scenario: "Generate CodeMender patch verification report for CVE-2026-RKT01 (SQLi, SSRF, and IDOR in LoanLookupController.py)."
          }})
        }});
        const data = await res.json();
        out.textContent = data.output || data.text || "Security patch verified.";
      }} catch (e) {{
        out.textContent = "Error: " + e.message;
      }}
    }};
  </script>

  {render_floating_control_bar_and_drawer(code, auth_token)}
</body>
</html>
"""
