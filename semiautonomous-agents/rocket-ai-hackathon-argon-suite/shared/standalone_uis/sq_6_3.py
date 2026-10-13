# -*- coding: utf-8 -*-
"""Square 6.3: Multi-System Integration Test Generator — Vertex AI + Pytest Contract Suite
Design Style: Postman / Swagger OpenAPI Light Explorer
(#FAFAFA clean light background, #FF6C37 Postman orange CTA, #059669 POST 200 OK badge,
Plus Jakarta Sans + IBM Plex Mono).
"""

from shared.standalone_uis.base_helpers import render_floating_control_bar_and_drawer


def render_sq_6_3(auth_token: str) -> str:
    code = "6.3"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Multi-System Integration Test Generator | Postman & OpenAPI Contract Explorer</title>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=IBM+Plex+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    :root {{
      --bg: #FAFAFA;
      --card: #FFFFFF;
      --pm-orange: #FF6C37;
      --pm-orange-dark: #E05320;
      --ok-green: #059669;
      --ok-bg: #ECFDF5;
      --err-red: #DC2626;
      --err-bg: #FEF2F2;
      --ink: #1E293B;
      --ink-muted: #64748B;
      --border: #E2E8F0;
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

    /* Postman Light Top Workspace Bar */
    .pm-header {{
      background: var(--card);
      border-bottom: 1px solid var(--border);
      border-top: 3px solid var(--pm-orange);
      padding: 14px 32px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 14px;
    }}
    .pm-brand {{
      display: flex;
      align-items: center;
      gap: 12px;
    }}
    .pm-badge {{
      background: var(--pm-orange);
      color: #FFFFFF;
      font-weight: 800;
      font-size: 12px;
      padding: 6px 10px;
      border-radius: 6px;
      letter-spacing: 0.03em;
    }}
    .pm-title {{
      font-size: 19px;
      font-weight: 800;
      color: var(--ink);
    }}
    .pm-sub {{
      font-size: 12.5px;
      color: var(--ink-muted);
    }}
    .pm-controls {{
      display: flex;
      align-items: center;
      gap: 10px;
      flex-wrap: wrap;
    }}
    .model-select {{
      background: #F8FAFC;
      border: 1px solid var(--border);
      padding: 6px 12px;
      border-radius: 6px;
      font-size: 12px;
      font-weight: 600;
      display: flex;
      align-items: center;
      gap: 6px;
    }}
    .model-select select {{
      background: transparent;
      border: none;
      font-family: 'IBM Plex Mono', monospace;
      font-weight: 700;
      font-size: 12px;
      color: var(--pm-orange-dark);
      outline: none;
      cursor: pointer;
    }}
    .btn-pm {{
      background: var(--pm-orange);
      color: #FFFFFF;
      border: none;
      padding: 9px 16px;
      border-radius: 6px;
      font-family: inherit;
      font-size: 13px;
      font-weight: 700;
      cursor: pointer;
      transition: 0.15s;
    }}
    .btn-pm:hover {{ background: var(--pm-orange-dark); }}

    /* OpenAPI Endpoint Request Bar */
    .endpoint-bar-wrap {{
      max-width: 1420px;
      margin: 20px auto 0;
      padding: 0 32px;
    }}
    .endpoint-bar {{
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 10px 14px;
      display: flex;
      align-items: center;
      gap: 12px;
      flex-wrap: wrap;
      box-shadow: 0 1px 4px rgba(15, 23, 42, 0.04);
    }}
    .method-post {{
      background: var(--ok-green);
      color: #FFFFFF;
      font-family: 'IBM Plex Mono', monospace;
      font-weight: 700;
      font-size: 12px;
      padding: 6px 12px;
      border-radius: 5px;
    }}
    .endpoint-url {{
      font-family: 'IBM Plex Mono', monospace;
      font-size: 13px;
      color: var(--ink);
      background: #F8FAFC;
      border: 1px solid var(--border);
      padding: 6px 14px;
      border-radius: 5px;
      flex: 1;
      min-width: 260px;
    }}
    .status-pill {{
      font-family: 'IBM Plex Mono', monospace;
      font-size: 12px;
      font-weight: 700;
      padding: 6px 12px;
      border-radius: 5px;
      background: var(--ok-bg);
      color: var(--ok-green);
      border: 1px solid #A7F3D0;
    }}
    .status-pill.fail {{
      background: var(--err-bg);
      color: var(--err-red);
      border-color: #FECACA;
    }}

    /* Main Workspace Grid */
    .explorer-grid {{
      max-width: 1420px;
      margin: 18px auto;
      padding: 0 32px;
      display: grid;
      grid-template-columns: 1fr 1.15fr;
      gap: 22px;
    }}
    @media (max-width: 1020px) {{
      .explorer-grid {{ grid-template-columns: 1fr; }}
    }}
    .pm-card {{
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 8px;
      overflow: hidden;
      display: flex;
      flex-direction: column;
    }}
    .pm-card-head {{
      padding: 13px 18px;
      border-bottom: 1px solid var(--border);
      background: #FCFDFE;
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 13.5px;
      font-weight: 700;
    }}
    .pm-card-body {{
      padding: 18px;
      display: flex;
      flex-direction: column;
      gap: 14px;
    }}
    .drift-toggle-row {{
      border: 1px solid var(--border);
      border-radius: 6px;
      padding: 11px 14px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 12px;
      background: #F8FAFC;
    }}
    .json-box {{
      background: #F8FAFC;
      border: 1px solid var(--border);
      border-radius: 6px;
      padding: 14px;
      font-family: 'IBM Plex Mono', monospace;
      font-size: 12px;
      line-height: 1.6;
      white-space: pre;
      overflow-x: auto;
    }}
    .ai-test-out {{
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

  <!-- Postman / Swagger OpenAPI Light Header -->
  <header class="pm-header">
    <div class="pm-brand">
      <span class="pm-badge">POSTMAN · OPENAPI 3.1</span>
      <div>
        <h1 class="pm-title">Multi-System Integration Test Generator (`Rocket Logic` → `Mr. Cooper Boarding API`)</h1>
        <p class="pm-sub">Automated Schema Contract Validator &amp; Synthetic Pytest Suite Generator across 14M Serviced Loans</p>
      </div>
    </div>
    <div class="pm-controls">
      <div class="model-select">
        <span>Model:</span>
        <select id="app-model-select" onchange="window.syncSelectedModel(this.value)">
          <option value="gemini-4-argon">gemini-4-argon</option>
          <option value="gemini-3.8-flash">gemini-3.8-flash</option>
        </select>
      </div>
      <button class="btn-pm" onclick="window.playQAAudio(this)">
        🔊 Play QA Contract Test Summary
      </button>
    </div>
  </header>

  <!-- OpenAPI Endpoint Bar -->
  <section class="endpoint-bar-wrap">
    <div class="endpoint-bar">
      <span class="method-post">POST 200 OK</span>
      <span class="endpoint-url">https://boarding.mrcooper-servicing.internal/v2/loans/board</span>
      <span class="status-pill" id="schema-status-pill">✓ OpenAPI 3.1 Contract Valid (42/42 Assertions Passed)</span>
      <button class="btn-pm" onclick="window.runCollectionTests()">▶ Run Collection (42 Tests)</button>
    </div>
  </section>

  <!-- Main Two-Column Postman Explorer -->
  <main class="explorer-grid">
    <!-- Left Column: Contract Drift Simulator & Live JSON Payload vs Schema Validator -->
    <section class="pm-card">
      <div class="pm-card-head">
        <span>1. Contract Drift Simulator &amp; Live JSON Payload Validator</span>
        <span class="mono" style="font-size:11.5px;color:var(--pm-orange);">MISMO v3.4 → Boarding v2</span>
      </div>
      <div class="pm-card-body">
        <div class="drift-toggle-row">
          <div>
            <div style="font-size:13px;font-weight:700;">Inject Drift #1: Enum Case Mismatch (<code>FloodZoneCode: "AE" → "ae_high"</code>)</div>
            <div style="font-size:12px;color:var(--ink-muted);">Tests strict FEMA flood zone enum validation before loan boarding.</div>
          </div>
          <input type="checkbox" id="drift-1" onchange="window.updatePayloadView()" style="width:18px;height:18px;accent-color:var(--pm-orange);cursor:pointer;">
        </div>

        <div class="drift-toggle-row">
          <div>
            <div style="font-size:13px;font-weight:700;">Inject Drift #2: Nullable Escrow Cushion Field (<code>escrowCushionCents: null</code>)</div>
            <div style="font-size:12px;color:var(--ink-muted);">Simulates missing integer cents on tax-exempt VA loans.</div>
          </div>
          <input type="checkbox" id="drift-2" onchange="window.updatePayloadView()" style="width:18px;height:18px;accent-color:var(--pm-orange);cursor:pointer;">
        </div>

        <div class="json-box" id="json-payload-box">{{
  "loanBoardingId": "RKT-COOP-2026-884120",
  "originationSystem": "RocketLogic_Encompass_v24",
  "targetServicer": "MrCooper_MSP_Core",
  "principalBalanceCents": 38450000,
  "noteRateBps": 6125,
  "femaFloodZoneCode": "AE",
  "escrowCushionCents": 158122,
  "mersMinNumber": "100039030498112094"
}}</div>
      </div>
    </section>

    <!-- Right Column: Synthesized Pytest Contract Test Suite -->
    <section class="pm-card">
      <div class="pm-card-head">
        <span>2. Auto-Generated Pytest &amp; Pact Contract Suite (`test_mrcooper_boarding_v2.py`)</span>
        <span class="mono" style="font-size:11.5px;color:var(--ok-green);">100% Edge-Case Coverage</span>
      </div>
      <div class="pm-card-body">
        <div class="json-box" id="pytest-code-box">import pytest
from pydantic import ValidationError
from schemas.mrcooper_v2 import LoanBoardingPayloadV2

@pytest.mark.parametrize("fema_zone", ["X", "AE", "VE", "AH"])
def test_boarding_contract_valid_flood_zones(sample_rocket_loan, fema_zone):
    payload = {{**sample_rocket_loan, "femaFloodZoneCode": fema_zone}}
    validated = LoanBoardingPayloadV2.model_validate(payload)
    assert validated.escrowCushionCents &gt;= 0
    assert len(validated.mersMinNumber) == 18

def test_rejects_lowercase_flood_enum_drift(sample_rocket_loan):
    with pytest.raises(ValidationError, match="femaFloodZoneCode"):
        LoanBoardingPayloadV2.model_validate({{**sample_rocket_loan, "femaFloodZoneCode": "ae_high"}})</div>

        <div style="display:flex;gap:10px;flex-wrap:wrap;justify-content:space-between;align-items:center;">
          <button class="btn-pm" onclick="window.runLiveVertexAI()">
            ⚡ Synthesize Additional Pytest Edge Cases via Vertex AI
          </button>
          <span class="mono" style="font-size:11.5px;color:var(--ink-muted);">CI Gate: Blocks PR on Schema Drift</span>
        </div>

        <div id="ai-qa-output" class="ai-test-out"></div>
      </div>
    </section>
  </main>

  <script>
    window.updatePayloadView = function() {{
      const d1 = document.getElementById('drift-1').checked;
      const d2 = document.getElementById('drift-2').checked;
      const flood = d1 ? '"ae_high"  // <-- SCHEMA DRIFT: Invalid Enum' : '"AE"';
      const cushion = d2 ? 'null       // <-- SCHEMA DRIFT: Non-nullable int64' : '158122';

      document.getElementById('json-payload-box').textContent = `{{\n  "loanBoardingId": "RKT-COOP-2026-884120",\n  "originationSystem": "RocketLogic_Encompass_v24",\n  "targetServicer": "MrCooper_MSP_Core",\n  "principalBalanceCents": 38450000,\n  "noteRateBps": 6125,\n  "femaFloodZoneCode": ${{flood}},\n  "escrowCushionCents": ${{cushion}},\n  "mersMinNumber": "100039030498112094"\n}}`;

      const pill = document.getElementById('schema-status-pill');
      if (d1 || d2) {{
        pill.className = "status-pill fail";
        pill.innerText = "✗ HTTP 422 Unprocessable Entity — Contract Drift Caught by Pytest Gate";
      }} else {{
        pill.className = "status-pill";
        pill.innerText = "✓ OpenAPI 3.1 Contract Valid (42/42 Assertions Passed)";
      }}
    }};

    window.runCollectionTests = function() {{
      document.getElementById('drift-1').checked = false;
      document.getElementById('drift-2').checked = false;
      window.updatePayloadView();
    }};

    window.playQAAudio = function(btnEl) {{
      const msg = "QA Contract Test Summary for the Rocket Logic to Mr. Cooper Servicing Boarding API. Vertex AI analyzed both OpenAPI 3.1 specifications and generated 42 parameterized Pytest contract tests. During pre-release validation, the suite caught two breaking schema drifts: a lowercase FEMA flood zone enum mismatch and a nullable escrow cushion integer field on VA loans, preventing failed boarding across 14 million serviced loans.";
      window.playLiveCallClip(msg, "Aoede", "Rocket Principal QA Automation Architect", btnEl);
    }};

    window.runLiveVertexAI = async function() {{
      const out = document.getElementById('ai-qa-output');
      out.style.display = 'block';
      const model = window.getSelectedModel ? window.getSelectedModel() : 'gemini-4-argon';
      out.textContent = `Generating Pytest OpenAPI 3.1 Contract Tests via Vertex AI (${{model}})...`;
      try {{
        const res = await fetch('/api/run-demo', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{
            code: '6.3',
            model: model,
            scenario: "Generate Pytest contract test assertions for Rocket Logic -> Mr. Cooper Servicing Boarding API (/v2/loans/board)."
          }})
        }});
        const data = await res.json();
        out.textContent = data.output || data.text || "Contract tests synthesized.";
      }} catch (e) {{
        out.textContent = "Error: " + e.message;
      }}
    }};
  </script>

  {render_floating_control_bar_and_drawer(code, auth_token)}
</body>
</html>
"""
