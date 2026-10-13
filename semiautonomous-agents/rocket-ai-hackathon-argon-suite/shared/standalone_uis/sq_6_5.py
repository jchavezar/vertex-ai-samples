# -*- coding: utf-8 -*-
"""Square 6.5: BigQuery Cost & Query Optimizer —INFORMATION_SCHEMA + Gemini 3.8 Flash
Design Style: Google Cloud Console BigQuery Studio (Material Design 3 Light Mode)
(#FFFFFF Google Cloud white, #F8F9FA Material surface gray, #1A73E8 Google Blue primary buttons,
#1E8E3E savings green, Plus Jakarta Sans + IBM Plex Mono).
"""

from shared.standalone_uis.base_helpers import render_floating_control_bar_and_drawer


def render_sq_6_5(auth_token: str) -> str:
    code = "6.5"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>BigQuery Cost & Query Optimizer | Google Cloud BigQuery Studio</title>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=IBM+Plex+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    :root {{
      --gcp-white: #FFFFFF;
      --gcp-surface: #F8F9FA;
      --gcp-blue: #1A73E8;
      --gcp-blue-dark: #1557B0;
      --gcp-blue-light: #E8F0FE;
      --gcp-green: #1E8E3E;
      --gcp-green-bg: #E6F4EA;
      --gcp-red: #D93025;
      --gcp-red-bg: #FCE8E6;
      --gcp-ink: #202124;
      --gcp-muted: #5F6368;
      --gcp-border: #DADCE0;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      background-color: var(--gcp-surface);
      color: var(--gcp-ink);
      font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
      min-height: 100vh;
      padding-bottom: 92px;
    }}
    .mono {{ font-family: 'IBM Plex Mono', monospace; }}

    /* Google Cloud Console Top App Bar (Material Design 3 Light Mode) */
    .gcp-appbar {{
      background: var(--gcp-white);
      border-bottom: 1px solid var(--gcp-border);
      padding: 12px 28px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 14px;
    }}
    .gcp-brand {{
      display: flex;
      align-items: center;
      gap: 12px;
    }}
    .bq-logo {{
      background: var(--gcp-blue-light);
      color: var(--gcp-blue);
      font-weight: 800;
      font-size: 13px;
      padding: 7px 11px;
      border-radius: 8px;
      border: 1px solid #AECBFA;
    }}
    .gcp-title {{
      font-size: 18px;
      font-weight: 700;
      color: var(--gcp-ink);
    }}
    .gcp-project-chip {{
      font-family: 'IBM Plex Mono', monospace;
      font-size: 11.5px;
      background: var(--gcp-surface);
      border: 1px solid var(--gcp-border);
      padding: 3px 9px;
      border-radius: 6px;
      color: var(--gcp-muted);
    }}
    .gcp-actions {{
      display: flex;
      align-items: center;
      gap: 10px;
      flex-wrap: wrap;
    }}
    .gcp-model-select {{
      background: var(--gcp-surface);
      border: 1px solid var(--gcp-border);
      padding: 6px 12px;
      border-radius: 8px;
      font-size: 12px;
      font-weight: 600;
      display: flex;
      align-items: center;
      gap: 6px;
    }}
    .gcp-model-select select {{
      background: transparent;
      border: none;
      font-family: 'IBM Plex Mono', monospace;
      font-weight: 700;
      font-size: 12px;
      color: var(--gcp-blue);
      outline: none;
      cursor: pointer;
    }}
    .btn-gcp-blue {{
      background: var(--gcp-blue);
      color: #FFFFFF;
      border: none;
      padding: 9px 16px;
      border-radius: 20px;
      font-family: inherit;
      font-size: 13px;
      font-weight: 600;
      cursor: pointer;
      transition: 0.15s;
    }}
    .btn-gcp-blue:hover {{ background: var(--gcp-blue-dark); }}

    /* BigQuery Dry-Run Validator Strip */
    .bq-validator-strip {{
      max-width: 1420px;
      margin: 20px auto 0;
      padding: 0 28px;
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 16px;
    }}
    @media (max-width: 960px) {{
      .bq-validator-strip {{ grid-template-columns: repeat(2, 1fr); }}
    }}
    .md3-metric-card {{
      background: var(--gcp-white);
      border: 1px solid var(--gcp-border);
      border-radius: 12px;
      padding: 16px 18px;
    }}
    .metric-lbl {{
      font-size: 11.5px;
      font-weight: 600;
      color: var(--gcp-muted);
    }}
    .metric-val {{
      font-family: 'IBM Plex Mono', monospace;
      font-size: 22px;
      font-weight: 700;
      margin-top: 4px;
    }}

    /* Side-by-Side SQL Comparison Grid */
    .bq-studio-grid {{
      max-width: 1420px;
      margin: 20px auto;
      padding: 0 28px;
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 20px;
    }}
    @media (max-width: 1020px) {{
      .bq-studio-grid {{ grid-template-columns: 1fr; }}
    }}
    .sql-editor-card {{
      background: var(--gcp-white);
      border: 1px solid var(--gcp-border);
      border-radius: 12px;
      overflow: hidden;
      display: flex;
      flex-direction: column;
    }}
    .sql-toolbar {{
      background: var(--gcp-surface);
      border-bottom: 1px solid var(--gcp-border);
      padding: 12px 18px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 8px;
    }}
    .dry-run-badge {{
      font-family: 'IBM Plex Mono', monospace;
      font-size: 11.5px;
      font-weight: 700;
      padding: 4px 10px;
      border-radius: 999px;
    }}
    .dry-run-badge.bad {{
      background: var(--gcp-red-bg);
      color: var(--gcp-red);
    }}
    .dry-run-badge.good {{
      background: var(--gcp-green-bg);
      color: var(--gcp-green);
    }}
    .sql-code {{
      padding: 18px;
      font-family: 'IBM Plex Mono', monospace;
      font-size: 12.5px;
      line-height: 1.65;
      white-space: pre;
      overflow-x: auto;
      background: #FFFFFF;
      flex: 1;
    }}

    /* FinOps Savings Calculator Panel */
    .finops-panel {{
      max-width: 1420px;
      margin: 0 auto 24px;
      padding: 0 28px;
    }}
    .finops-card {{
      background: var(--gcp-white);
      border: 1px solid var(--gcp-border);
      border-radius: 12px;
      padding: 20px 24px;
      display: grid;
      grid-template-columns: 1.2fr 1fr;
      gap: 24px;
      align-items: center;
    }}
    @media (max-width: 960px) {{
      .finops-card {{ grid-template-columns: 1fr; }}
    }}
    .ai-bq-out {{
      margin-top: 14px;
      background: var(--gcp-surface);
      border: 1px solid var(--gcp-border);
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

  <!-- Google Cloud Console BigQuery Studio Top App Bar -->
  <header class="gcp-appbar">
    <div class="gcp-brand">
      <span class="bq-logo">BigQuery Studio</span>
      <h1 class="gcp-title">BigQuery Cost &amp; Query Optimizer</h1>
      <span class="gcp-project-chip">Project: rocket-edw-prod · region-us</span>
    </div>
    <div class="gcp-actions">
      <div class="gcp-model-select">
        <span>Model:</span>
        <select id="app-model-select" onchange="window.syncSelectedModel(this.value)">
          <option value="gemini-3.8-flash">gemini-3.8-flash (SQL Optimizer)</option>
          <option value="gemini-4-argon">gemini-4-argon</option>
        </select>
      </div>
      <button class="btn-gcp-blue" onclick="window.playFinOpsAudio(this)">
        🔊 Play FinOps Architect Audio Summary
      </button>
    </div>
  </header>

  <!-- BigQuery Dry-Run Metrics Strip -->
  <section class="bq-validator-strip">
    <div class="md3-metric-card">
      <div class="metric-lbl">Unoptimized Bytes Billed / Run</div>
      <div class="metric-val" style="color:var(--gcp-red);">4.82 TB ($24.10)</div>
    </div>
    <div class="md3-metric-card">
      <div class="metric-lbl">Partitioned + Clustered Bytes / Run</div>
      <div class="metric-val" style="color:var(--gcp-green);">42.0 GB ($0.21)</div>
    </div>
    <div class="md3-metric-card">
      <div class="metric-lbl">Bytes &amp; Slot Reduction</div>
      <div class="metric-val" style="color:var(--gcp-blue);">99.1% Saved</div>
    </div>
    <div class="md3-metric-card">
      <div class="metric-lbl">Annualized GCP Savings</div>
      <div class="metric-val" style="color:var(--gcp-green);" id="annual-savings-kpi">$87,198 / yr</div>
    </div>
  </section>

  <!-- Side-by-Side SQL Workspace -->
  <main class="bq-studio-grid">
    <!-- Left: Unoptimized SELECT * Cross-Join -->
    <section class="sql-editor-card">
      <div class="sql-toolbar">
        <span style="font-size:13px;font-weight:700;color:var(--gcp-red);">✗ Legacy Unoptimized Query (`INFORMATION_SCHEMA.JOBS` #1 Offender)</span>
        <span class="dry-run-badge bad">⚠ This query will process 4.82 TB ($24.10/run)</span>
      </div>
      <div class="sql-code">-- ANTI-PATTERN: Full Table Scan (SELECT *) + Unpartitioned Join
SELECT
  *
FROM
  `rocket-edw-prod.servicing.loan_daily_snapshots` AS a
CROSS JOIN
  `rocket-edw-prod.origination.rate_lock_events` AS b
WHERE
  a.loan_number = b.loan_number
  AND CAST(a.snapshot_timestamp AS STRING) LIKE '2026-10%'
ORDER BY
  a.unpaid_principal_balance DESC;</div>
    </section>

    <!-- Right: Partitioned + Clustered DDL & Rewritten Query -->
    <section class="sql-editor-card">
      <div class="sql-toolbar">
        <span style="font-size:13px;font-weight:700;color:var(--gcp-green);">✓ Gemini Rewritten Query (Partition Pruning + Cluster Pushdown)</span>
        <span class="dry-run-badge good">✓ This query will process 42.0 GB ($0.21/run · 99.1% Reduction)</span>
      </div>
      <div class="sql-code">-- STEP 1: Partition by DATE(snapshot_ts) &amp; Cluster by loan_number, state
CREATE OR REPLACE TABLE `rocket-edw-prod.servicing.loan_snapshots_opt`
PARTITION BY DATE(snapshot_timestamp)
CLUSTER BY loan_number, property_state AS ...;

-- STEP 2: Pruned Column Projection + Inner Equi-Join on Clustered Key
SELECT
  a.loan_number,
  a.property_state,
  a.unpaid_principal_balance,
  b.locked_rate_bps
FROM
  `rocket-edw-prod.servicing.loan_snapshots_opt` AS a
INNER JOIN
  `rocket-edw-prod.origination.rate_lock_events_opt` AS b
  USING (loan_number)
WHERE
  DATE(a.snapshot_timestamp) BETWEEN '2026-10-01' AND '2026-10-31'
  AND b.event_date BETWEEN '2026-10-01' AND '2026-10-31';</div>
    </section>
  </main>

  <!-- Interactive Daily Query Frequency Slider & Annual GCP Savings Calculator -->
  <section class="finops-panel">
    <div class="finops-card">
      <div>
        <div style="font-size:11.5px;font-weight:700;color:var(--gcp-blue);text-transform:uppercase;letter-spacing:0.05em;">
          INTERACTIVE FINOPS ROI SIMULATOR
        </div>
        <h2 style="font-size:18px;font-weight:700;margin-top:3px;">
          Scheduled Looker / Airflow Daily Execution Frequency
        </h2>
        <p style="font-size:13px;color:var(--gcp-muted);margin-top:4px;">
          Slide to adjust how many times per day this pipeline executes across Rocket Data Engineering &amp; BI dashboards.
        </p>

        <div style="margin-top:14px;">
          <div style="display:flex;justify-content:space-between;font-size:13px;font-weight:700;margin-bottom:6px;">
            <span>Scheduled Runs per Day</span>
            <span class="mono" id="runs-per-day-lbl" style="color:var(--gcp-blue);">10 runs / day (3,650 runs / yr)</span>
          </div>
          <input type="range" id="slider-freq" min="1" max="50" step="1" value="10" style="width:100%;accent-color:var(--gcp-blue);cursor:pointer;" oninput="window.updateBqSavings()">
        </div>
      </div>

      <div style="background:var(--gcp-green-bg);border:1px solid #A8DAB5;border-radius:10px;padding:18px 20px;">
        <div style="font-size:12px;font-weight:700;color:var(--gcp-green);text-transform:uppercase;">
          NET ANNUAL BIGQUERY FINOPS SAVINGS
        </div>
        <div class="mono" id="net-savings-box" style="font-size:28px;font-weight:800;color:var(--gcp-green);margin-top:4px;">
          $87,198 / yr
        </div>
        <div style="font-size:12.5px;color:#137333;margin-top:4px;" id="savings-breakdown-lbl">
          Before: $87,965/yr → After: $767/yr (Saves 17,439 TB scanned/yr)
        </div>
        <button class="btn-gcp-blue" style="margin-top:12px;width:100%;" onclick="window.runLiveVertexAI()">
          ⚡ Generate Live Vertex AI BigQuery Migration Plan
        </button>
      </div>
    </div>

    <div id="ai-bq-output" class="ai-bq-out"></div>
  </section>

  <script>
    window.updateBqSavings = function() {{
      const runsPerDay = parseInt(document.getElementById('slider-freq').value, 10);
      const runsPerYear = runsPerDay * 365;
      const oldCost = runsPerYear * 24.10;
      const newCost = runsPerYear * 0.21;
      const saved = Math.round(oldCost - newCost);
      const tbSaved = Math.round(runsPerYear * (4.82 - 0.042));

      document.getElementById('runs-per-day-lbl').innerText = `${{runsPerDay}} runs / day (${{runsPerYear.toLocaleString()}} runs / yr)`;
      const fmtSaved = "$" + saved.toLocaleString('en-US') + " / yr";
      document.getElementById('annual-savings-kpi').innerText = fmtSaved;
      document.getElementById('net-savings-box').innerText = fmtSaved;
      document.getElementById('savings-breakdown-lbl').innerText =
        `Before: $${{Math.round(oldCost).toLocaleString()}}/yr → After: $${{Math.round(newCost).toLocaleString()}}/yr (Saves ${{tbSaved.toLocaleString()}} TB scanned/yr)`;
    }};

    window.playFinOpsAudio = function(btnEl) {{
      const msg = "Google Cloud FinOps Architect Summary for Rocket Enterprise Data Warehouse. By auditing INFORMATION_SCHEMA.JOBS_BY_PROJECT, we identified an unpartitioned cross-join in the servicing daily snapshot pipeline that scanned 4.82 terabytes per execution at a cost of 24 dollars and 10 cents per run. Rewriting the table with date partitioning on snapshot_timestamp and clustering on loan_number reduces bytes scanned to 42 gigabytes—a 99.1 percent reduction saving 87,198 dollars annually at 10 runs per day.";
      window.playLiveCallClip(msg, "Puck", "Rocket Principal Cloud FinOps Architect", btnEl);
    }};

    window.runLiveVertexAI = async function() {{
      const out = document.getElementById('ai-bq-output');
      out.style.display = 'block';
      const model = window.getSelectedModel ? window.getSelectedModel() : 'gemini-3.8-flash';
      out.textContent = `Synthesizing BigQuery Partition & Cluster Optimization Plan via Vertex AI (${{model}})...`;
      try {{
        const res = await fetch('/api/run-demo', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{
            code: '6.5',
            model: model,
            scenario: "Optimize BigQuery query scanning 4.82 TB ($24.10/run) down to 42.0 GB ($0.21/run) using PARTITION BY DATE and CLUSTER BY loan_number."
          }})
        }});
        const data = await res.json();
        out.textContent = data.output || data.text || "Optimization plan generated.";
      }} catch (e) {{
        out.textContent = "Error: " + e.message;
      }}
    }};
  </script>

  {render_floating_control_bar_and_drawer(code, auth_token)}
</body>
</html>
"""
