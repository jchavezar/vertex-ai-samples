"""Standalone FastAPI Microservice for Pillar 1: BigQuery ML TimesFM 2.0 (AI.FORECAST).

Exposes:
  - GET  /                     Interactive Studio HTML or JSON Health
  - GET  /api/pillar1/catalog  Returns METRIC_CATALOG
  - POST /api/pillar1/forecast Calls engine.run_timesfm_forecast
  - GET  /healthz              Kubernetes / Cloud Run liveness probe
"""

import os
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from engine import METRIC_CATALOG, run_timesfm_forecast

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(
    title="Rocket × Pillar 1: BigQuery ML TimesFM 2.0 Microservice",
    description="Standalone zero-shot time-series forecasting microservice powered by Google Research TimesFM on BigQuery ML",
    version="2.0.0",
)

FRONTEND_DIR = BASE_DIR / "frontend"
FRONTEND_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/frontend", StaticFiles(directory=str(FRONTEND_DIR)), name="frontend")

ASSETS_DIR = BASE_DIR / "assets"
if ASSETS_DIR.exists():
    app.mount("/assets", StaticFiles(directory=str(ASSETS_DIR)), name="assets")

INDEX_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Pillar 1 · BigQuery ML TimesFM 2.0 (AI.FORECAST) Studio</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg: #090D16;
      --card-bg: #111827;
      --border: #1E293B;
      --accent: #D81E28;
      --blue: #1A73E8;
      --emerald: #059669;
      --text: #F8FAFC;
      --text-muted: #94A3B8;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      background: var(--bg);
      color: var(--text);
      font-family: 'Plus Jakarta Sans', sans-serif;
      padding: 24px;
    }
    .container { max-width: 1100px; margin: 0 auto; }
    .header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 20px;
      padding-bottom: 16px;
      border-bottom: 1px solid var(--border);
    }
    .badge {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 6px 12px;
      border-radius: 9999px;
      font-size: 12px;
      font-weight: 700;
      background: rgba(26, 115, 232, 0.15);
      color: #60A5FA;
      border: 1px solid rgba(26, 115, 232, 0.3);
    }
    .dot-pulse {
      width: 8px; height: 8px; border-radius: 50%; background: #60A5FA;
      box-shadow: 0 0 8px #60A5FA;
    }
    .cohort-strip {
      display: flex;
      gap: 8px;
      overflow-x: auto;
      margin-bottom: 20px;
      padding-bottom: 4px;
    }
    .cohort-btn {
      padding: 10px 16px;
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 12px;
      color: var(--text);
      font-size: 13px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.15s ease;
      white-space: nowrap;
    }
    .cohort-btn.active {
      background: rgba(216, 30, 40, 0.15);
      border-color: var(--accent);
      color: #FFF;
    }
    .grid { display: grid; grid-template-columns: 280px 1fr; gap: 20px; }
    @media (max-width: 860px) { .grid { grid-template-columns: 1fr; } }
    .card {
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 16px;
      padding: 20px;
    }
    .form-group { margin-bottom: 16px; }
    label {
      display: flex;
      justify-content: space-between;
      font-size: 12.5px;
      color: var(--text-muted);
      font-weight: 600;
      margin-bottom: 6px;
    }
    .val-display { font-family: 'JetBrains Mono', monospace; color: #FFF; }
    input[type=range] {
      width: 100%;
      accent-color: var(--accent);
      background: #1E293B;
    }
    .btn-run {
      width: 100%;
      padding: 12px;
      background: var(--accent);
      border: none;
      border-radius: 10px;
      color: #FFF;
      font-weight: 700;
      cursor: pointer;
      font-size: 14px;
    }
    .kpi-row {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
      gap: 12px;
      margin-bottom: 16px;
    }
    .kpi-tile {
      background: #0D1321;
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 12px 14px;
    }
    .kpi-title { font-size: 11px; color: var(--text-muted); text-transform: uppercase; font-weight: 700; }
    .kpi-value { font-size: 18px; font-weight: 800; font-family: 'JetBrains Mono', monospace; margin-top: 4px; }
    .svg-container {
      background: #0D1321;
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 12px;
      overflow-x: auto;
    }
    svg { width: 100%; height: auto; display: block; }
    .sql-box {
      margin-top: 16px;
      background: #05080F;
      border: 1px solid #1E293B;
      border-radius: 10px;
      padding: 14px;
      font-family: 'JetBrains Mono', monospace;
      font-size: 11.5px;
      color: #93C5FD;
      overflow-x: auto;
      max-height: 220px;
    }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <div>
        <h1 style="margin:0; font-size:22px; font-weight:800;">Pillar 1 · BigQuery ML TimesFM 2.0 Studio</h1>
        <p style="margin:4px 0 0; font-size:13px; color:var(--text-muted);">
          Zero-Shot Foundation Forecasting across 9.5M Loans &amp; Redfin Demand
        </p>
      </div>
      <div id="p1-status" class="badge">
        <span class="dot-pulse"></span>
        <span id="p1-badge-text">Port 8081 · Standalone</span>
      </div>
    </div>

    <div class="cohort-strip" id="cohort-strip">
      <button class="cohort-btn active" data-metric="mrcooper_refi_locks">Mr. Cooper Refi Locks</button>
      <button class="cohort-btn" data-metric="redfin_tour_demand">Redfin Tour Demand</button>
      <button class="cohort-btn" data-metric="escrow_liquidity_outflow_m">Escrow Outflow ($M)</button>
      <button class="cohort-btn" data-metric="warehouse_funding_b">Warehouse Funding ($B)</button>
    </div>

    <div class="grid">
      <div class="card">
        <h3 style="margin-top:0; font-size:15px;">Forecast Controls</h3>
        <div class="form-group">
          <label>Rate Shock (Fed Cut/Hike) <span class="val-display" id="disp-shock">-50 bps</span></label>
          <input type="range" id="p1-shock" min="-150" max="100" step="5" value="-50">
        </div>
        <div class="form-group">
          <label>Horizon (Weeks) <span class="val-display" id="disp-horizon">12 w</span></label>
          <input type="range" id="p1-horizon" min="4" max="24" step="1" value="12">
        </div>
        <div class="form-group">
          <label>Confidence Level (CI) <span class="val-display" id="disp-ci">90%</span></label>
          <input type="range" id="p1-ci" min="80" max="95" step="5" value="90">
        </div>
        <button class="btn-run" id="btn-run">Execute AI.FORECAST</button>
      </div>

      <div>
        <div class="kpi-row" id="kpi-row">
          <div class="kpi-tile">
            <div class="kpi-title">Last Historical</div>
            <div class="kpi-value" id="kpi-last">--</div>
          </div>
          <div class="kpi-tile">
            <div class="kpi-title">Peak Forecast</div>
            <div class="kpi-value" id="kpi-peak" style="color:var(--accent);">--</div>
          </div>
          <div class="kpi-tile">
            <div class="kpi-title">Delta vs Baseline</div>
            <div class="kpi-value" id="kpi-delta" style="color:#60A5FA;">--</div>
          </div>
          <div class="kpi-tile">
            <div class="kpi-title">Cumulative Horizon</div>
            <div class="kpi-value" id="kpi-cum">--</div>
          </div>
          <div class="kpi-tile">
            <div class="kpi-title">Est Value Impact</div>
            <div class="kpi-value" id="kpi-usd" style="color:#34D399;">--</div>
          </div>
        </div>

        <div class="svg-container">
          <svg id="p1-chart" viewBox="0 0 860 300"></svg>
        </div>

        <details style="margin-top:14px; font-size:12px; color:var(--text-muted);">
          <summary style="cursor:pointer; font-weight:700;">View Parameterized BigQuery ML SQL</summary>
          <pre class="sql-box" id="p1-sql">-- Click 'Execute AI.FORECAST' to generate live SQL</pre>
        </details>
      </div>
    </div>
  </div>

  <script src="/frontend/p1_chart.js"></script>
  <script>
    let activeMetric = 'mrcooper_refi_locks';

    document.querySelectorAll('.cohort-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('.cohort-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        activeMetric = btn.dataset.metric;
        runForecast();
      });
    });

    const shockEl = document.getElementById('p1-shock');
    const horizonEl = document.getElementById('p1-horizon');
    const ciEl = document.getElementById('p1-ci');

    shockEl.addEventListener('input', () => {
      const v = parseInt(shockEl.value, 10);
      document.getElementById('disp-shock').innerText = (v > 0 ? '+' : '') + v + ' bps';
    });
    horizonEl.addEventListener('input', () => {
      document.getElementById('disp-horizon').innerText = horizonEl.value + ' w';
    });
    ciEl.addEventListener('input', () => {
      document.getElementById('disp-ci').innerText = ciEl.value + '%';
    });

    document.getElementById('btn-run').addEventListener('click', runForecast);

    async function runForecast() {
      const badge = document.getElementById('p1-badge-text');
      badge.innerText = 'Running TimesFM 2.0...';
      try {
        const data = await window.P1ChartModule.fetchForecast({
          metric_id: activeMetric,
          rate_shock_bps: parseInt(shockEl.value, 10),
          horizon: parseInt(horizonEl.value, 10),
          confidence_level: parseInt(ciEl.value, 10) / 100.0
        });

        badge.innerText = `TimesFM · ${data.latency_ms}ms`;
        document.getElementById('kpi-last').innerText = data.kpis.last_historical.toLocaleString();
        document.getElementById('kpi-peak').innerText = data.kpis.peak_forecast.toLocaleString();
        document.getElementById('kpi-delta').innerText = (data.kpis.delta_pct >= 0 ? '+' : '') + data.kpis.delta_pct + '%';
        document.getElementById('kpi-cum').innerText = Math.round(data.kpis.cumulative_horizon).toLocaleString();
        document.getElementById('kpi-usd').innerText = '$' + (data.kpis.est_value_usd / 1e6).toFixed(1) + 'M';
        document.getElementById('p1-sql').innerText = data.sql;

        window.P1ChartModule.renderTimesFmSvg('#p1-chart', data.historical, data.forecast);
      } catch (err) {
        badge.innerText = 'Error: ' + err.message;
      }
    }

    // Auto-run on mount
    window.addEventListener('DOMContentLoaded', runForecast);
  </script>
</body>
</html>"""


@app.get("/", response_class=HTMLResponse)
async def get_index(request: Request):
    """Renders standalone interactive studio HTML, or returns JSON health if requested."""
    accept = request.headers.get("accept", "")
    if "application/json" in accept or request.query_params.get("format") == "json":
        return JSONResponse({
            "ok": True,
            "service": "pillar-1-bqml-timesfm",
            "port": 8081,
            "engine": "BigQuery ML TimesFM 2.0 (AI.FORECAST)",
            "metrics": list(METRIC_CATALOG.keys()),
        })
    return HTMLResponse(INDEX_HTML)


@app.get("/api/pillar1/catalog")
async def api_p1_catalog():
    """Returns the multi-cohort financial and demand metric catalog."""
    return JSONResponse({"ok": True, "count": len(METRIC_CATALOG), "catalog": METRIC_CATALOG})


@app.post("/api/pillar1/forecast")
async def api_p1_forecast(request: Request):
    """Runs zero-shot TimesFM 2.0 foundation forecasting via BigQuery ML AI.FORECAST."""
    try:
        body = await request.json()
    except Exception:
        body = {}
    res = run_timesfm_forecast(
        metric_id=body.get("metric_id", "mrcooper_refi_locks"),
        horizon=int(body.get("horizon", 12)),
        confidence_level=float(body.get("confidence_level", 0.90)),
        rate_shock_bps=int(body.get("rate_shock_bps", -50)),
    )
    return JSONResponse(res)


@app.get("/healthz")
async def healthz():
    return JSONResponse({"status": "ok", "service": "pillar-1-bqml-timesfm", "port": 8081})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8081, reload=True)
