# -*- coding: utf-8 -*-
"""Square M.5: Project Air-Tight: Self-Healing Autonomous Compliance Swarm — Google ADK Runtime
Visual Design: Autonomous Pre-Close Diagnostic Pipeline & Self-Healing PDF Surgery Console
(#0A0F18 clinical slate, #10B981 diagnostic emerald, #F43F5E fault rose, #3B82F6 laser blue,
Google Fonts Chakra Petch + JetBrains Mono).
"""

from shared.standalone_uis.base_helpers import render_floating_control_bar_and_drawer


def render_sq_m_5(auth_token: str) -> str:
    code = "M.5"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>[M.5] Project Air-Tight: Self-Healing Autonomous Compliance Swarm | Google ADK</title>
  <link href="https://fonts.googleapis.com/css2?family=Chakra+Petch:wght@500;600;700&family=JetBrains+Mono:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <style>
    :root {{
      --clinical-bg: #0A0F18;
      --clinical-card: #111827;
      --clinical-panel: #192338;
      --emerald: #10B981;
      --emerald-dim: rgba(16, 185, 129, 0.15);
      --fault-rose: #F43F5E;
      --rose-dim: rgba(244, 63, 94, 0.16);
      --laser-blue: #3B82F6;
      --blue-dim: rgba(59, 130, 246, 0.16);
      --text-main: #F8FAFC;
      --text-muted: #94A3B8;
      --border: #263552;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      background-color: var(--clinical-bg);
      color: var(--text-main);
      font-family: 'Chakra Petch', sans-serif;
      min-height: 100vh;
      background-image:
        linear-gradient(rgba(59, 130, 246, 0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(59, 130, 246, 0.03) 1px, transparent 1px);
      background-size: 36px 36px;
      padding-bottom: 96px;
    }}
    .mono {{ font-family: 'JetBrains Mono', monospace; }}

    /* Top Clinical Surgery Header */
    .airtight-header {{
      background: rgba(17, 24, 39, 0.94);
      border-bottom: 1px solid var(--laser-blue);
      box-shadow: 0 0 28px rgba(59, 130, 246, 0.16);
      padding: 14px 28px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 14px;
    }}
    .laser-badge {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      background: var(--blue-dim);
      border: 1px solid var(--laser-blue);
      color: #93C5FD;
      font-family: 'JetBrains Mono', monospace;
      font-size: 11px;
      font-weight: 700;
      padding: 5px 12px;
      border-radius: 6px;
    }}
    .clinical-model-select {{
      display: flex;
      align-items: center;
      gap: 8px;
      background: var(--clinical-bg);
      border: 1px solid var(--emerald);
      padding: 6px 12px;
      border-radius: 6px;
      font-family: 'JetBrains Mono', monospace;
      font-size: 11px;
    }}
    .clinical-model-select select {{
      background: transparent;
      color: var(--emerald);
      border: none;
      font-family: 'JetBrains Mono', monospace;
      font-size: 11px;
      font-weight: 700;
      outline: none;
      cursor: pointer;
    }}
    .clinical-model-select select option {{ background: #0A0F18; color: #FFFFFF; }}

    /* Main Surgery Workspace */
    .surgery-container {{
      max-width: 1560px;
      margin: 24px auto;
      padding: 0 28px;
      display: flex;
      flex-direction: column;
      gap: 22px;
    }}

    /* 4-Stage Self-Healing Pipeline Stepper */
    .pipeline-stepper {{
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 14px;
    }}
    @media (max-width: 1050px) {{
      .pipeline-stepper {{ grid-template-columns: 1fr 1fr; }}
    }}
    .stage-node {{
      background: var(--clinical-card);
      border: 1px solid var(--border);
      border-top: 3px solid var(--laser-blue);
      border-radius: 10px;
      padding: 16px;
      cursor: pointer;
      transition: all 0.2s;
      position: relative;
    }}
    .stage-node:hover {{ transform: translateY(-2px); border-color: var(--laser-blue); }}
    .stage-node.fault {{ border-top-color: var(--fault-rose); }}
    .stage-node.healed {{
      border-top-color: var(--emerald);
      background: rgba(16, 185, 129, 0.08);
      border-color: rgba(16, 185, 129, 0.45);
    }}
    .stage-step-num {{
      font-family: 'JetBrains Mono', monospace;
      font-size: 10.5px;
      font-weight: 700;
      padding: 3px 8px;
      border-radius: 4px;
      display: inline-block;
      margin-bottom: 8px;
    }}

    /* Side-by-Side Defective vs. Self-Healed Closing Disclosure PDF Diff */
    .pdf-surgery-grid {{
      display: grid;
      grid-template-columns: 1fr 340px 1fr;
      gap: 18px;
      align-items: stretch;
    }}
    @media (max-width: 1200px) {{
      .pdf-surgery-grid {{ grid-template-columns: 1fr; }}
    }}

    .pdf-pane {{
      background: var(--clinical-card);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 20px;
      display: flex;
      flex-direction: column;
      gap: 14px;
    }}
    .pdf-pane.defective {{ border-top: 4px solid var(--fault-rose); }}
    .pdf-pane.certified {{ border-top: 4px solid var(--emerald); }}

    .pdf-paper-mock {{
      background: #06090F;
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 16px;
      font-family: 'JetBrains Mono', monospace;
      font-size: 11.5px;
      line-height: 1.65;
      flex: 1;
    }}
    .defect-row {{
      background: var(--rose-dim);
      border-left: 3px solid var(--fault-rose);
      padding: 8px 10px;
      margin: 8px 0;
      border-radius: 0 4px 4px 0;
    }}
    .healed-row {{
      background: var(--emerald-dim);
      border-left: 3px solid var(--emerald);
      padding: 8px 10px;
      margin: 8px 0;
      border-radius: 0 4px 4px 0;
    }}

    /* Center Surgical Control Spine */
    .surgical-controls {{
      background: var(--clinical-card);
      border: 1px solid var(--laser-blue);
      border-radius: 12px;
      padding: 20px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      gap: 14px;
      box-shadow: 0 0 32px rgba(59, 130, 246, 0.12);
    }}
    .btn-heal {{
      width: 100%;
      padding: 13px 16px;
      background: linear-gradient(135deg, var(--emerald), #059669);
      color: #04130C;
      border: none;
      border-radius: 8px;
      font-family: 'JetBrains Mono', monospace;
      font-size: 12px;
      font-weight: 800;
      cursor: pointer;
      text-transform: uppercase;
      transition: 0.15s;
      box-shadow: 0 8px 24px rgba(16, 185, 129, 0.3);
    }}
    .btn-heal:hover {{ filter: brightness(1.08); transform: translateY(-1px); }}
  </style>
</head>
<body>

  <!-- TOP HEADER -->
  <header class="airtight-header">
    <div style="display:flex;align-items:center;gap:14px;flex-wrap:wrap;">
      <span class="laser-badge">🩺 PROJECT AIR-TIGHT // SELF-HEALING LOS SWARM • SQUARE [M.5]</span>
      <div>
        <h1 style="font-size:20px;font-weight:700;">Autonomous Pre-Close Diagnostic Pipeline & Self-Healing PDF Surgery Console</h1>
        <p class="mono" style="font-size:11px;color:#93C5FD;">Google ADK Runtime + Document AI + Headless Playwright LOS Patcher (72 Hours Prior to Closing)</p>
      </div>
    </div>
    <div style="display:flex;align-items:center;gap:12px;flex-wrap:wrap;">
      <div class="clinical-model-select">
        <span>SWARM MODEL:</span>
        <select id="app-model-select" onchange="window.syncSelectedModel(this.value)">
          <option value="gemini-4-argon">gemini-4-argon (Frontier Global)</option>
          <option value="gemini-3.8-flash" selected>gemini-3.8-flash (Fast / ADK Runtime)</option>
        </select>
      </div>
      <button class="btn-heal" style="width:auto;padding:9px 16px;" onclick="window.runLiveVertexAI()">
        ⚡ Execute Full ADK Self-Heal (/api/run-demo)
      </button>
    </div>
  </header>

  <!-- MAIN SURGERY WORKSPACE -->
  <main class="surgery-container">

    <!-- 4-STAGE INTERACTIVE SELF-HEALING PIPELINE -->
    <section class="pipeline-stepper">
      <div class="stage-node" id="pipe-stage-1" onclick="activatePipelineStage(1)">
        <span class="stage-step-num" style="background:var(--blue-dim);color:#93C5FD;">STAGE 01 // INGEST</span>
        <h3 style="font-size:15px;font-weight:700;">1. Ingest Loan Packet (T-72h)</h3>
        <p class="mono" style="font-size:11px;color:var(--text-muted);margin-top:6px;">
          Document AI parses 148-page Closing Packet: Form 1003, Initial LE, Draft CD v1, Amrock Title Commitment & MI Driver's Licenses.
        </p>
      </div>

      <div class="stage-node fault" id="pipe-stage-2" onclick="activatePipelineStage(2)">
        <span class="stage-step-num" style="background:var(--rose-dim);color:#FDA4AF;">STAGE 02 // DETECT FAULTS</span>
        <h3 style="font-size:15px;font-weight:700;">2. Detect Missing Co-Borrower Sign & TRID Overcharge</h3>
        <p class="mono" style="font-size:11px;color:#FDA4AF;margin-top:6px;" id="stage2-desc">
          3 Blocking Defects Caught: Missing Co-Borrower ('Elena R. Vance') Addendum Sign, Middle Initial Vesting Mismatch, & $485 TRID Overcharge.
        </p>
      </div>

      <div class="stage-node" id="pipe-stage-3" onclick="activatePipelineStage(3)">
        <span class="stage-step-num" style="background:var(--blue-dim);color:#93C5FD;">STAGE 03 // AUTO-CURE</span>
        <h3 style="font-size:15px;font-weight:700;">3. Auto-Compute Lender Cure & Patch LOS</h3>
        <p class="mono" style="font-size:11px;color:var(--text-muted);margin-top:6px;" id="stage3-desc">
          ADK Remediation Agent computes $485.00 Section J Lender Cure, patches vesting to 'Marcus A. Vance', & dispatches e-Sign link.
        </p>
      </div>

      <div class="stage-node healed" id="pipe-stage-4" onclick="activatePipelineStage(4)">
        <span class="stage-step-num" style="background:var(--emerald-dim);color:var(--emerald);">STAGE 04 // RE-RENDER PDF</span>
        <h3 style="font-size:15px;font-weight:700;">4. Re-Render Certified CD v2 PDF</h3>
        <p class="mono" style="font-size:11px;color:var(--emerald);margin-top:6px;" id="stage4-desc">
          0 Violations Remaining — Certified Clear-to-Close Closing Disclosure v2 PDF generated 71 hours prior to signing.
        </p>
      </div>
    </section>

    <!-- SIDE-BY-SIDE DIFF: DEFECTIVE CD v1 VS. SELF-HEALED CERTIFIED CD v2 -->
    <section class="pdf-surgery-grid">

      <!-- LEFT: DEFECTIVE CLOSING DISCLOSURE v1 -->
      <div class="pdf-pane defective">
        <div style="display:flex;justify-content:space-between;align-items:center;">
          <div>
            <div class="mono" style="font-size:10px;color:var(--fault-rose);font-weight:700;">PRE-SURGERY ARTIFACT // CLOSING_DISCLOSURE_V1_DRAFT.PDF</div>
            <h2 style="font-size:16px;font-weight:700;margin-top:2px;">Defective Closing Packet (3 Blocking Faults)</h2>
          </div>
          <span class="mono" style="background:var(--rose-dim);border:1px solid var(--fault-rose);color:#FDA4AF;padding:3px 9px;border-radius:4px;font-size:10.5px;font-weight:700;">
            REJECTED BY AUDIT
          </span>
        </div>

        <div class="pdf-paper-mock">
          <div style="color:var(--text-muted);border-bottom:1px solid var(--border);padding-bottom:6px;margin-bottom:10px;">
            FILE: #RKT-2026-884920 • PROPERTY: 1420 VINSETTA BLVD, ROYAL OAK MI
          </div>

          <div class="defect-row">
            <div style="color:#FDA4AF;font-weight:700;">[FAULT #01 — VESTING & CO-BORROWER SIGNATURE DEFECT]</div>
            <div>CD Page 1 Vesting: <code>"Marcus Vance"</code> (Omits middle initial <code>"A."</code> on MI Driver's License & Warranty Deed)</div>
            <div>Co-Borrower Signature Line (Page 5): <code>[MISSING_SIGNATURE_TOKEN: ELENA R. VANCE]</code></div>
          </div>

          <div class="defect-row">
            <div style="color:#FDA4AF;font-weight:700;">[FAULT #02 — 0% ZERO-TOLERANCE BUCKET OVERCHARGE]</div>
            <div>Section B Appraisal Fee: Initial LE <code>$550.00</code> → Draft CD <code id="def-zero-val">$800.00 (+$250.00 Unapproved Rush Fee)</code></div>
            <div>Violation: 12 CFR § 1026.19(e)(3)(i) Zero-Tolerance Breach (No Valid COC).</div>
          </div>

          <div class="defect-row">
            <div style="color:#FDA4AF;font-weight:700;">[FAULT #03 — 10% CUMULATIVE BUCKET OVERAGE]</div>
            <div>Section C & E Recording/Title: 110% Cap <code>$715.00</code> → Draft CD <code id="def-ten-val">$950.00 (+$235.00 Overage)</code></div>
            <div>Section J Lender Tolerance Credit: <code>$0.00 (MISSING MANDATORY CURE!)</code></div>
          </div>
        </div>
      </div>

      <!-- CENTER: SURGICAL SELF-HEALING PARAMETERS -->
      <div class="surgical-controls">
        <div>
          <div class="mono" style="font-size:11px;color:var(--laser-blue);font-weight:700;text-transform:uppercase;margin-bottom:8px;">
            🔧 Autonomous Surgery Controls
          </div>
          <p style="font-size:12.5px;color:var(--text-muted);line-height:1.55;margin-bottom:14px;">
            Adjust the detected TRID tolerance breaches below and trigger the 4-stage self-healing pipeline (`run_airtight_self_heal` / `run_airtight_healing`).
          </p>

          <div style="margin-bottom:12px;">
            <label class="mono" style="font-size:10.5px;color:var(--text-muted);display:block;margin-bottom:4px;">0% Bucket Appraisal Overcharge ($):</label>
            <input type="number" id="inp-zero-breach" value="250" oninput="runAirTightSandbox()"
              style="width:100%;padding:9px 12px;border-radius:6px;border:1px solid var(--border);background:#06090F;color:#FDA4AF;font-family:'JetBrains Mono',monospace;font-size:13px;font-weight:700;">
          </div>

          <div style="margin-bottom:12px;">
            <label class="mono" style="font-size:10.5px;color:var(--text-muted);display:block;margin-bottom:4px;">10% Bucket Recording Overage ($):</label>
            <input type="number" id="inp-ten-breach" value="235" oninput="runAirTightSandbox()"
              style="width:100%;padding:9px 12px;border-radius:6px;border:1px solid var(--border);background:#06090F;color:#FDA4AF;font-family:'JetBrains Mono',monospace;font-size:13px;font-weight:700;">
          </div>

          <div style="background:#06090F;border:1px solid var(--emerald);border-radius:8px;padding:12px;text-align:center;margin-top:14px;">
            <div class="mono" style="font-size:10px;color:var(--text-muted);">AUTO-COMPUTED SECTION J CURE</div>
            <div class="mono" id="center-cure-total" style="font-size:26px;font-weight:800;color:var(--emerald);margin-top:4px;">$485.00</div>
            <div class="mono" style="font-size:10px;color:var(--emerald);margin-top:2px;">Patched via Playwright LOS Agent</div>
          </div>
        </div>

        <div>
          <div class="mono" id="airtight-latency-lbl" style="font-size:10.5px;color:var(--text-muted);text-align:center;margin-bottom:8px;">
            gVisor Sandbox Ready
          </div>
          <button class="btn-heal" onclick="runAirTightSandbox()">
            🩺 Run Self-Healing PDF Surgery (/api/sandbox)
          </button>
        </div>
      </div>

      <!-- RIGHT: SELF-HEALED CERTIFIED CLOSING DISCLOSURE v2 -->
      <div class="pdf-pane certified">
        <div style="display:flex;justify-content:space-between;align-items:center;">
          <div>
            <div class="mono" style="font-size:10px;color:var(--emerald);font-weight:700;">POST-SURGERY ARTIFACT // CLOSING_DISCLOSURE_V2_CERTIFIED.PDF</div>
            <h2 style="font-size:16px;font-weight:700;margin-top:2px;">Self-Healed Closing Disclosure (Clear to Close)</h2>
          </div>
          <span class="mono" style="background:var(--emerald-dim);border:1px solid var(--emerald);color:var(--emerald);padding:3px 9px;border-radius:4px;font-size:10.5px;font-weight:700;">
            ✅ 0 DEFECTS • CTC
          </span>
        </div>

        <div class="pdf-paper-mock">
          <div style="color:var(--text-muted);border-bottom:1px solid var(--border);padding-bottom:6px;margin-bottom:10px;">
            FILE: #RKT-2026-884920-V2 • SHA-256: 9f84e2a1...c40b • CLEAR TO CLOSE
          </div>

          <div class="healed-row">
            <div style="color:var(--emerald);font-weight:700;">[HEALED #01 — VESTING RECONCILED & CO-BORROWER E-SIGN COMPLETED]</div>
            <div>CD Page 1 Vesting Patched: <code>"Marcus A. Vance and Elena R. Vance, Husband and Wife"</code> (Matches MI Driver's License OCR & Amrock Deed)</div>
            <div>Co-Borrower Signature Line (Page 5): <code>[DOCUSIGN_VERIFIED: ELENA R. VANCE • IP 73.142.88.19]</code></div>
          </div>

          <div class="healed-row">
            <div style="color:var(--emerald);font-weight:700;">[HEALED #02 — 12 CFR § 1026.19(f)(2)(v) LENDER TOLERANCE CURE APPLIED]</div>
            <div>CD Page 2, Section J (Lender Credits): <code id="heal-cure-line">-$485.00 (Includes $250.00 Zero-Bucket + $235.00 10%-Bucket Cure)</code></div>
            <div>Net Cash to Close Reduced by <strong id="heal-cash-delta">$485.00</strong> — No 3-Day Waiting Period Reset Required!</div>
          </div>

          <div class="healed-row">
            <div style="color:var(--emerald);font-weight:700;">[HEALED #03 — AUTOMATED SECONDARY MARKET & FANNIE MAE UCD CHECK]</div>
            <div>Uniform Closing Dataset (UCD) XML Validated: <code>0 Fatal Edits • 100% GSE Deliverable</code></div>
          </div>
        </div>
      </div>

    </section>

    <!-- BOTTOM ADK EXECUTION LOG -->
    <section style="background:var(--clinical-card);border:1px solid var(--border);border-left:4px solid var(--emerald);border-radius:10px;padding:16px 20px;">
      <div class="mono" style="font-size:11px;color:var(--emerald);font-weight:700;margin-bottom:6px;">
        🤖 GOOGLE ADK AUTONOMOUS SELF-HEALING EXECUTION LOG (`run_airtight_self_heal`)
      </div>
      <div id="airtight-ai-log" class="mono" style="font-size:12px;line-height:1.65;color:var(--text-main);">
        [STAGE 1 -> 4 COMPLETE]: Document AI caught 3 pre-closing defects at T-72h. Google ADK Remediation Agent computed the mandatory $485.00 Section J Lender Tolerance Cure, reconciled borrower middle initial vesting against Michigan Driver's License OCR, and re-rendered Closing Disclosure v2 PDF.
      </div>
    </section>

  </main>

  <script>
    function activatePipelineStage(stageNum) {{
      for (let i = 1; i <= 4; i++) {{
        const el = document.getElementById('pipe-stage-' + i);
        if (el) el.style.boxShadow = (i === stageNum) ? '0 0 24px rgba(59, 130, 246, 0.45)' : 'none';
      }}
      runAirTightSandbox();
    }}

    async function runAirTightSandbox() {{
      const zBreach = parseFloat(document.getElementById('inp-zero-breach').value || 250);
      const tBreach = parseFloat(document.getElementById('inp-ten-breach').value || 235);
      const totalCure = zBreach + tBreach;

      document.getElementById('center-cure-total').innerText = '$' + totalCure.toFixed(2);
      document.getElementById('def-zero-val').innerText = `$${'{'} (550 + zBreach).toFixed(2) {'}'} (+$${'{'}zBreach.toFixed(2){'}'} Unapproved Rush Fee)`;
      document.getElementById('def-ten-val').innerText = `$${'{'} (715 + tBreach).toFixed(2) {'}'} (+$${'{'}tBreach.toFixed(2){'}'} Overage)`;
      document.getElementById('heal-cure-line').innerText = `-$${'{'}totalCure.toFixed(2){'}'} (Includes $${'{'}zBreach.toFixed(2){'}'} Zero-Bucket + $${'{'}tBreach.toFixed(2){'}'} 10%-Bucket Cure)`;
      document.getElementById('heal-cash-delta').innerText = '$' + totalCure.toFixed(2);

      try {{
        const res = await fetch('/api/sandbox', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{
            code: 'M.5',
            action: 'run_airtight_healing',
            params: {{
              secondary_action: 'run_airtight_self_heal',
              zero_bucket_breach: zBreach,
              ten_pct_breach: tBreach
            }}
          }})
        }});
        const data = await res.json();
        const m = data.metrics || {{}};
        document.getElementById('airtight-latency-lbl').innerText = `Sandbox Verified (${'{'}data.execution_ms || 1.1{'}'}ms)`;
        document.getElementById('stage2-desc').innerText = m.stage_1_docai_anomalies || '';
        document.getElementById('stage3-desc').innerText = m.stage_2_argon_remediation || '';
        document.getElementById('stage4-desc').innerText = m.stage_4_post_patch_verification || '';
      }} catch (e) {{}}
    }}

    window.runLiveVertexAI = async function() {{
      const model = window.getSelectedModel ? window.getSelectedModel() : 'gemini-3.8-flash';
      const zBreach = parseFloat(document.getElementById('inp-zero-breach').value || 250);
      const tBreach = parseFloat(document.getElementById('inp-ten-breach').value || 235);
      const logEl = document.getElementById('airtight-ai-log');
      logEl.innerText = `Executing 4-Stage Self-Healing Compliance Swarm with ${'{'}model{'}'}...`;

      try {{
        const res = await fetch('/api/run-demo', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{
            code: 'M.5',
            model: model,
            user_input: `Execute the 4-stage self-healing pipeline for Loan #RKT-2026-884920: cure the $${'{'}zBreach{'}'} 0% bucket overcharge and $${'{'}tBreach{'}'} 10% bucket overage, patch middle initial vesting, and certify Closing Disclosure v2.`,
            params: {{ zero_bucket_breach: zBreach, ten_pct_breach: tBreach }}
          }})
        }});
        const data = await res.json();
        logEl.innerHTML = `<span style="color:var(--emerald);font-weight:700;">[${'{'}data.model_used || model{'}'} // SELF-HEALING SWARM]:</span> ${'{'}data.output || 'Closing Disclosure v2 certified.'{'}'}`;
      }} catch (e) {{
        logEl.innerText = "Swarm Error: " + e.message;
      }}
    }};

    document.addEventListener('DOMContentLoaded', () => {{
      runAirTightSandbox();
    }});
  </script>

  {render_floating_control_bar_and_drawer(code, auth_token)}
</body>
</html>"""
