# -*- coding: utf-8 -*-
"""Square 5.4: Automated Vendor Contract Risk & GLBA SLA Redliner — Google ADK Runtime
Visual Design: Microsoft Word Legal Track-Changes Editor (#185ABD Word Navy ribbon,
#E5E7EB gray desk background, centered #FFFFFF A4 contract page with #DC2626 red strikethroughs
and #15803D green insertions, Google Fonts Newsreader + Inter).
"""

from shared.standalone_uis.base_helpers import render_floating_control_bar_and_drawer


def render_sq_5_4(auth_token: str) -> str:
    code = "5.4"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>[5.4] Automated Vendor Contract Risk & GLBA SLA Redliner | Rocket Legal Word Track-Changes</title>
  <link href="https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,600;0,6..72,700;1,6..72,400&family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    :root {{
      --word-navy: #185ABD;
      --word-navy-dark: #103F86;
      --ribbon-bg: #F3F4F6;
      --desk-gray: #E5E7EB;
      --page-white: #FFFFFF;
      --del-red: #DC2626;
      --del-bg: #FEE2E2;
      --ins-green: #15803D;
      --ins-bg: #DCFCE7;
      --ink: #111827;
      --muted: #4B5563;
      --border: #D1D5DB;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      background-color: var(--desk-gray);
      color: var(--ink);
      font-family: 'Inter', -apple-system, sans-serif;
      min-height: 100vh;
      padding-bottom: 96px;
    }}
    .serif-contract {{ font-family: 'Newsreader', Georgia, serif; }}
    .mono {{ font-family: 'JetBrains Mono', monospace; }}

    /* Microsoft Word Navy Title Bar */
    .word-titlebar {{
      background: var(--word-navy);
      color: #FFFFFF;
      padding: 10px 24px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 12px;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
    }}
    .doc-filename {{
      display: flex;
      align-items: center;
      gap: 10px;
      font-size: 13.5px;
      font-weight: 700;
    }}
    .autosave-pill {{
      background: rgba(255, 255, 255, 0.16);
      padding: 3px 10px;
      border-radius: 999px;
      font-size: 11px;
      font-weight: 600;
    }}
    .word-model-selector {{
      display: flex;
      align-items: center;
      gap: 8px;
      background: var(--word-navy-dark);
      border: 1px solid rgba(255, 255, 255, 0.3);
      padding: 5px 12px;
      border-radius: 6px;
      font-family: 'JetBrains Mono', monospace;
      font-size: 11px;
    }}
    .word-model-selector select {{
      background: transparent;
      color: #FFFFFF;
      border: none;
      font-family: 'JetBrains Mono', monospace;
      font-size: 11px;
      font-weight: 700;
      outline: none;
      cursor: pointer;
    }}
    .word-model-selector select option {{ background: #0F172A; color: #FFFFFF; }}

    /* Word Review Ribbon Toolbar */
    .word-ribbon {{
      background: var(--ribbon-bg);
      border-bottom: 1px solid var(--border);
      padding: 10px 24px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 14px;
      box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
    }}
    .ribbon-group {{
      display: flex;
      align-items: center;
      gap: 8px;
      padding-right: 14px;
      border-right: 1px solid var(--border);
    }}
    .ribbon-btn {{
      background: #FFFFFF;
      color: var(--ink);
      border: 1px solid var(--border);
      padding: 7px 12px;
      border-radius: 5px;
      font-size: 12px;
      font-weight: 600;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      transition: 0.15s;
    }}
    .ribbon-btn:hover {{ background: #EFF6FF; border-color: var(--word-navy); color: var(--word-navy); }}
    .ribbon-btn.primary {{
      background: var(--word-navy);
      color: #FFFFFF;
      border-color: var(--word-navy-dark);
    }}
    .ribbon-btn.primary:hover {{ background: var(--word-navy-dark); }}

    /* Desk Canvas: Centered A4 Paper + Right Margin Comment Track */
    .desk-canvas {{
      max-width: 1460px;
      margin: 26px auto;
      padding: 0 24px;
      display: grid;
      grid-template-columns: 1fr 410px;
      gap: 24px;
      align-items: start;
    }}
    @media (max-width: 1120px) {{
      .desk-canvas {{ grid-template-columns: 1fr; }}
    }}

    /* A4 Legal Contract Page */
    .a4-page {{
      background: var(--page-white);
      border: 1px solid #CBD5E1;
      box-shadow: 0 12px 32px rgba(15, 23, 42, 0.12);
      padding: 52px 60px;
      min-height: 820px;
      position: relative;
    }}
    @media (max-width: 720px) {{
      .a4-page {{ padding: 28px 22px; }}
    }}
    /* Left red track-changes revision bar */
    .clause-block {{
      position: relative;
      padding: 16px 18px;
      margin: 18px 0;
      border-left: 4px solid var(--del-red);
      background: #FAFAFA;
      border-radius: 0 6px 6px 0;
      cursor: pointer;
      transition: 0.15s;
    }}
    .clause-block:hover {{ background: #F8FAFC; box-shadow: 0 2px 10px rgba(24, 90, 189, 0.08); }}
    .clause-block.accepted {{
      border-left-color: var(--ins-green);
      background: #F0FDF4;
    }}
    .clause-block.rejected {{
      border-left-color: #9CA3AF;
      background: #FEF2F2;
    }}

    .track-del {{
      color: var(--del-red);
      background: var(--del-bg);
      text-decoration: line-through;
      padding: 1px 4px;
      border-radius: 3px;
    }}
    .track-ins {{
      color: var(--ins-green);
      background: var(--ins-bg);
      font-weight: 700;
      text-decoration: underline;
      text-decoration-style: double;
      padding: 1px 5px;
      border-radius: 3px;
    }}

    /* Right Margin Track-Changes Comment Balloons */
    .margin-comments {{
      display: flex;
      flex-direction: column;
      gap: 14px;
    }}
    .comment-balloon {{
      background: #FFFFFF;
      border: 1px solid #CBD5E1;
      border-left: 5px solid var(--word-navy);
      border-radius: 8px;
      padding: 16px;
      box-shadow: 0 4px 14px rgba(15, 23, 42, 0.08);
      transition: 0.15s;
    }}
    .comment-balloon.resolved {{
      border-left-color: var(--ins-green);
      background: #F0FDF4;
    }}
    .balloon-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 8px;
      font-size: 11.5px;
    }}
    .balloon-actions {{
      display: flex;
      gap: 8px;
      margin-top: 12px;
    }}
    .btn-accept {{
      flex: 1;
      background: var(--ins-green);
      color: #FFF;
      border: none;
      padding: 7px 10px;
      border-radius: 5px;
      font-size: 11.5px;
      font-weight: 700;
      cursor: pointer;
    }}
    .btn-accept:hover {{ background: #166534; }}
    .btn-reject {{
      flex: 1;
      background: #FEE2E2;
      color: var(--del-red);
      border: 1px solid #FCA5A5;
      padding: 7px 10px;
      border-radius: 5px;
      font-size: 11.5px;
      font-weight: 700;
      cursor: pointer;
    }}
    .btn-reject:hover {{ background: #FECACA; }}
  </style>
</head>
<body>

  <!-- MICROSOFT WORD NAVY TOP BAR -->
  <header class="word-titlebar">
    <div class="doc-filename">
      <span style="background:#FFF;color:var(--word-navy);font-weight:900;padding:3px 8px;border-radius:4px;font-size:12px;">W</span>
      <span>Master_SaaS_AI_Vendor_Agreement_v4_REDLINED.docx</span>
      <span class="autosave-pill">● Track Changes: ON (Google ADK Legal Runtime • Square [5.4])</span>
    </div>
    <div style="display:flex;align-items:center;gap:12px;flex-wrap:wrap;">
      <div class="word-model-selector">
        <span>ADK MODEL:</span>
        <select id="app-model-select" onchange="window.syncSelectedModel(this.value)">
          <option value="gemini-4-argon">gemini-4-argon (Frontier Global)</option>
          <option value="gemini-3.8-flash" selected>gemini-3.8-flash (Fast / ADK Runtime)</option>
        </select>
      </div>
    </div>
  </header>

  <!-- WORD TRACK-CHANGES RIBBON TOOLBAR -->
  <div class="word-ribbon">
    <div style="display:flex;align-items:center;gap:12px;flex-wrap:wrap;">
      <div class="ribbon-group">
        <button class="ribbon-btn primary" onclick="acceptAllRedlines()">✓ Accept All Rocket Redlines (3)</button>
        <button class="ribbon-btn" onclick="resetRedlines()">↺ Reset Track Changes</button>
      </div>
      <div class="ribbon-group">
        <button class="ribbon-btn" onclick="runMsaSandboxAudit()">🛡️ Score TPRM Risk (/api/sandbox)</button>
        <button class="ribbon-btn primary" style="background:#0F172A;border-color:#0F172A;" onclick="window.runLiveVertexAI()">
          ⚡ Synthesize Rider via Google ADK (/api/run-demo)
        </button>
      </div>
    </div>
    <div class="mono" style="font-size:11.5px;display:flex;align-items:center;gap:14px;">
      <span>TPRM RISK SCORE: <strong id="tprm-score-badge" style="color:var(--del-red);">92 / 100 (CRITICAL BLOCKER)</strong></span>
      <span id="redline-counter-badge" style="background:#DBEAFE;color:var(--word-navy);padding:4px 10px;border-radius:4px;font-weight:700;">0 / 3 Redlines Accepted</span>
    </div>
  </div>

  <!-- DESK CANVAS: CENTERED A4 CONTRACT PAGE + RIGHT MARGIN BALLOONS -->
  <main class="desk-canvas">

    <!-- CENTERED A4 CONTRACT PAPER -->
    <article class="a4-page serif-contract">
      <div style="text-align:center;border-bottom:2px solid #111827;padding-bottom:18px;margin-bottom:24px;">
        <div class="mono" style="font-size:10.5px;color:var(--muted);letter-spacing:0.08em;">ROCKET COMPANIES, INC. • THIRD-PARTY RISK MANAGEMENT (TPRM) & GLBA ADDENDUM</div>
        <h1 style="font-size:24px;font-weight:700;margin-top:6px;">MASTER ENTERPRISE CLOUD & AI SERVICES AGREEMENT</h1>
        <p style="font-size:13.5px;color:var(--muted);margin-top:4px;font-style:italic;">
          Between Rocket Mortgage, LLC ("Customer") and DocuCloud AI Analytics, Inc. ("Vendor")
        </p>
      </div>

      <p style="font-size:14.5px;line-height:1.8;margin-bottom:16px;">
        <strong>WHEREAS,</strong> Customer is a federally regulated financial institution subject to the Gramm-Leach-Bliley Act (GLBA) Safeguards Rule (16 CFR Part 314), CFPB supervisory examination, and NYDFS 23 NYCRR Part 500; and Vendor processes Nonpublic Personal Information ("NPI") including Form 1003 loan applications, Social Security numbers, and tax transcripts.
      </p>

      <!-- CLAUSE 1: GLBA BREACH NOTICE 72h -> 24h -->
      <div class="clause-block" id="clause-box-1" onclick="focusBalloon(1)">
        <div class="mono" style="font-size:11px;font-weight:700;color:var(--word-navy);margin-bottom:6px;font-family:'JetBrains Mono',monospace;">
          SECTION 11.4 — CYBERSECURITY INCIDENT & GLBA BREACH NOTIFICATION SLA
        </div>
        <p style="font-size:15px;line-height:1.85;" id="clause-text-1">
          11.4 <u>Security Incident Notice</u>. In the event Vendor discovers any unauthorized access, acquisition, or exfiltration of Customer Nonpublic Personal Information (NPI), Vendor shall notify the Rocket CISO and Legal Incident Response Desk within <span class="track-del">seventy-two (72) hours of confirming a material breach</span> <span class="track-ins">twenty-four (24) hours of initial detection of any suspected or confirmed Security Incident per NYDFS 23 NYCRR § 500.17 and FTC GLBA Safeguards Rule</span>, and shall provide continuous root-cause forensic logs every 6 hours thereafter.
        </p>
      </div>

      <!-- CLAUSE 2: ZERO DATA RETENTION & AI MODEL TRAINING PROHIBITION -->
      <div class="clause-block" id="clause-box-2" onclick="focusBalloon(2)">
        <div class="mono" style="font-size:11px;font-weight:700;color:var(--word-navy);margin-bottom:6px;font-family:'JetBrains Mono',monospace;">
          SECTION 14.1 — FOUNDATION MODEL TRAINING & ZERO DATA RETENTION COVENANT
        </div>
        <p style="font-size:15px;line-height:1.85;" id="clause-text-2">
          14.1 <u>AI Data Sovereignty</u>. Vendor <span class="track-del">is granted a perpetual, royalty-free license to utilize de-identified and aggregated Customer mortgage documents and borrower prompts to train, fine-tune, and improve Vendor's commercial foundation models</span> <span class="track-ins">strictly covenants that Customer Data, prompts, embeddings, and borrower NPI shall NEVER be used to train, fine-tune, or distill any shared or third-party AI model. Vendor shall enforce ephemeral Zero Data Retention (ZDR) in US-only regions (us-central1 / us-east4)</span>.
        </p>
      </div>

      <!-- CLAUSE 3: SOC2 RIGHT-TO-AUDIT & $5M GLBA SUPER-CAP -->
      <div class="clause-block" id="clause-box-3" onclick="focusBalloon(3)">
        <div class="mono" style="font-size:11px;font-weight:700;color:var(--word-navy);margin-bottom:6px;font-family:'JetBrains Mono',monospace;">
          SECTION 8.2 — LIMITATION OF LIABILITY SUPER-CAP & REGULATORY RIGHT-TO-AUDIT
        </div>
        <p style="font-size:15px;line-height:1.85;" id="clause-text-3">
          8.2 <u>Data Breach Super-Cap & SOC2 Audit</u>. Each party's aggregate liability under this Agreement <span class="track-del">shall in no event exceed the total fees paid by Customer during the three (3) months preceding the claim ($45,000)</span> <span class="track-ins">shall be subject to a $5,000,000.00 GLBA NPI Data Breach Super-Cap plus 100% of CFPB/state regulatory fines and borrower credit-monitoring remediation costs. Customer and federal regulators (CFPB/OCC) retain an unconditional annual SOC2 Type II Right-to-Audit</span>.
        </p>
      </div>

      <!-- GENERATED EXECUTIVE CONTRACT RIDER -->
      <div style="margin-top:28px;border-top:2px solid #E5E7EB;padding-top:18px;font-family:'Inter',sans-serif;">
        <div class="mono" style="font-size:11px;font-weight:700;color:var(--word-navy);margin-bottom:8px;">
          🤖 GOOGLE ADK LEGAL RUNTIME — GENERATED GLBA RIDER & EXECUTION MEMO
        </div>
        <div id="adk-rider-output" style="background:#F8FAFC;border:1px solid #CBD5E1;border-radius:6px;padding:14px;font-size:12.5px;line-height:1.65;color:var(--ink);">
          Click <strong>[✓ Accept Redline]</strong> on the comment balloons on the right or click <strong>⚡ Synthesize Rider via Google ADK</strong> above to generate the final execution-ready addendum.
        </div>
      </div>
    </article>

    <!-- RIGHT MARGIN COMMENT BALLOONS -->
    <aside class="margin-comments">
      <div class="mono" style="font-size:11px;font-weight:700;color:#374151;text-transform:uppercase;padding:0 4px;">
        💬 ADK Counsel Track-Changes Comments (3)
      </div>

      <!-- Balloon 1 -->
      <div class="comment-balloon" id="balloon-1">
        <div class="balloon-header">
          <strong style="color:var(--word-navy);">🤖 Google ADK Legal Agent</strong>
          <span class="mono" id="status-1" style="font-size:10px;background:#FEE2E2;color:#991B1B;padding:2px 7px;border-radius:4px;font-weight:700;">PENDING REVIEW</span>
        </div>
        <div style="font-size:12px;line-height:1.55;color:var(--ink);">
          <strong>§ 11.4 GLBA Breach Notice (72h → 24h):</strong> Vendor's 72-hour post-confirmation clock violates Rocket's mandatory 24-hour notification window required to meet NYDFS 23 NYCRR 500.17 and FTC GLBA Safeguards timelines.
        </div>
        <div class="balloon-actions">
          <button class="btn-accept" onclick="resolveClause(1, true)">✓ Accept Redline</button>
          <button class="btn-reject" onclick="resolveClause(1, false)">✗ Reject</button>
        </div>
      </div>

      <!-- Balloon 2 -->
      <div class="comment-balloon" id="balloon-2">
        <div class="balloon-header">
          <strong style="color:var(--word-navy);">🤖 Google ADK Legal Agent</strong>
          <span class="mono" id="status-2" style="font-size:10px;background:#FEE2E2;color:#991B1B;padding:2px 7px;border-radius:4px;font-weight:700;">PENDING REVIEW</span>
        </div>
        <div style="font-size:12px;line-height:1.55;color:var(--ink);">
          <strong>§ 14.1 Zero Data Retention & Model Training:</strong> Strikes Vendor's foundation model training license over borrower 1003/tax docs and enforces strict US-only (`us-central1`) Zero Data Retention.
        </div>
        <div class="balloon-actions">
          <button class="btn-accept" onclick="resolveClause(2, true)">✓ Accept Redline</button>
          <button class="btn-reject" onclick="resolveClause(2, false)">✗ Reject</button>
        </div>
      </div>

      <!-- Balloon 3 -->
      <div class="comment-balloon" id="balloon-3">
        <div class="balloon-header">
          <strong style="color:var(--word-navy);">🤖 Google ADK Legal Agent</strong>
          <span class="mono" id="status-3" style="font-size:10px;background:#FEE2E2;color:#991B1B;padding:2px 7px;border-radius:4px;font-weight:700;">PENDING REVIEW</span>
        </div>
        <div style="font-size:12px;line-height:1.55;color:var(--ink);">
          <strong>§ 8.2 $5M GLBA Super-Cap & SOC2 Audit:</strong> Replaces the 3-month fee cap ($45k) with Rocket's mandatory $5,000,000 NPI Data Breach Super-Cap and unconditional CFPB/OCC SOC2 Type II Right-to-Audit.
        </div>
        <div class="balloon-actions">
          <button class="btn-accept" onclick="resolveClause(3, true)">✓ Accept Redline</button>
          <button class="btn-reject" onclick="resolveClause(3, false)">✗ Reject</button>
        </div>
      </div>
    </aside>

  </main>

  <script>
    const clauseState = {{ 1: null, 2: null, 3: null }};

    function focusBalloon(idx) {{
      const el = document.getElementById('balloon-' + idx);
      if (el) {{
        el.style.transform = 'scale(1.02)';
        setTimeout(() => {{ el.style.transform = 'scale(1)'; }}, 200);
      }}
    }}

    function resolveClause(idx, accept) {{
      clauseState[idx] = accept ? 'accepted' : 'rejected';
      const box = document.getElementById('clause-box-' + idx);
      const balloon = document.getElementById('balloon-' + idx);
      const status = document.getElementById('status-' + idx);

      box.classList.remove('accepted', 'rejected');
      balloon.classList.remove('resolved');

      if (accept) {{
        box.classList.add('accepted');
        balloon.classList.add('resolved');
        status.innerText = '✓ ACCEPTED';
        status.style.background = '#DCFCE7';
        status.style.color = '#166534';
      }} else {{
        box.classList.add('rejected');
        status.innerText = '✗ REJECTED (RISK REMAINS)';
        status.style.background = '#FEE2E2';
        status.style.color = '#991B1B';
      }}
      updateRibbonScore();
    }}

    function acceptAllRedlines() {{
      resolveClause(1, true);
      resolveClause(2, true);
      resolveClause(3, true);
      runMsaSandboxAudit();
    }}

    function resetRedlines() {{
      [1, 2, 3].forEach(i => {{
        clauseState[i] = null;
        document.getElementById('clause-box-' + i).classList.remove('accepted', 'rejected');
        document.getElementById('balloon-' + i).classList.remove('resolved');
        const st = document.getElementById('status-' + i);
        st.innerText = 'PENDING REVIEW';
        st.style.background = '#FEE2E2';
        st.style.color = '#991B1B';
      }});
      updateRibbonScore();
    }}

    function updateRibbonScore() {{
      const acceptedCount = Object.values(clauseState).filter(v => v === 'accepted').length;
      document.getElementById('redline-counter-badge').innerText = `${'{'}acceptedCount{'}'} / 3 Redlines Accepted`;
      const scoreBadge = document.getElementById('tprm-score-badge');
      if (acceptedCount === 3) {{
        scoreBadge.innerText = '12 / 100 (LOW RISK — APPROVED TO SIGN)';
        scoreBadge.style.color = '#15803D';
      }} else if (acceptedCount > 0) {{
        scoreBadge.innerText = `${'{'}92 - acceptedCount * 26{'}'} / 100 (PARTIAL REMEDIATION)`;
        scoreBadge.style.color = '#D97706';
      }} else {{
        scoreBadge.innerText = '92 / 100 (CRITICAL BLOCKER)';
        scoreBadge.style.color = '#DC2626';
      }}
    }}

    async function runMsaSandboxAudit() {{
      const riderEl = document.getElementById('adk-rider-output');
      riderEl.innerHTML = `Executing TPRM Contract Audit in Cloud Run gVisor Sandbox (<code>redline_vendor_msa</code> / <code>score_vendor_contract</code>)...`;
      try {{
        const res = await fetch('/api/sandbox', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{
            code: '5.4',
            action: 'score_vendor_contract',
            params: {{ secondary_action: 'redline_vendor_msa', accepted_clauses: clauseState }}
          }})
        }});
        const data = await res.json();
        const m = data.metrics || {{}};
        riderEl.innerHTML = `
          <div class="mono" style="font-size:11px;color:var(--word-navy);margin-bottom:6px;">
            ✅ SANDBOX VERIFIED (${'{'}data.execution_ms || 1.1{'}'}ms) • GOOGLE ADK TPRM ENGINE:
          </div>
          <ul style="padding-left:18px;line-height:1.7;">
            <li><strong>Liability Cap Check:</strong> ${'{'}m.violation_1_sec_8_2_liability || ''{'}'}</li>
            <li><strong>Breach SLA Check:</strong> ${'{'}m.violation_2_sec_11_4_breach_sla || ''{'}'}</li>
            <li><strong>AI Training Sovereignty Check:</strong> ${'{'}m.violation_3_sec_14_1_ai_training || ''{'}'}</li>
          </ul>
        `;
      }} catch (e) {{
        riderEl.innerText = "Sandbox Error: " + e.message;
      }}
    }}

    window.runLiveVertexAI = async function() {{
      const model = window.getSelectedModel ? window.getSelectedModel() : 'gemini-3.8-flash';
      const riderEl = document.getElementById('adk-rider-output');
      riderEl.innerHTML = `Synthesizing Binding GLBA Contract Rider via Google ADK + <strong>${'{'}model{'}'}</strong>...`;
      try {{
        const res = await fetch('/api/run-demo', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{
            code: '5.4',
            model: model,
            user_input: "Generate the binding Rocket Mortgage GLBA Safeguards Rule & Zero-Training Contract Rider for Sections 8.2, 11.4, and 14.1."
          }})
        }});
        const data = await res.json();
        const summary = data.output || "Vendor MSA redlines synthesized.";
        const actions = (data.structured_data && data.structured_data.action_items) || [];
        riderEl.innerHTML = `
          <div class="mono" style="font-size:11px;color:#15803D;font-weight:700;margin-bottom:6px;">
            [${'{'}data.model_used || model{'}'} • ${'{'}data.runtime_badge || 'Google ADK Runtime'{'}'}]:
          </div>
          <div style="white-space:pre-wrap;margin-bottom:8px;">${'{'}summary{'}'}</div>
          ${'{'}actions.length ? '<div class="mono" style="font-size:11px;background:#EFF6FF;padding:10px;border-radius:4px;"><strong>EXECUTION CHECKLIST:</strong><ul style="margin-top:4px;padding-left:18px;">' + actions.map(a => `<li>${'{'}a{'}'}</li>`).join('') + '</ul></div>' : ''{'}'}
        `;
      }} catch (e) {{
        riderEl.innerText = "ADK Error: " + e.message;
      }}
    }};
  </script>

  {render_floating_control_bar_and_drawer(code, auth_token)}
</body>
</html>"""
