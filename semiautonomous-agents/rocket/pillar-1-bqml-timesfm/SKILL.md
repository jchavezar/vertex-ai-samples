---
name: pillar-1-bqml-timesfm
description: Step-by-step LLM replication skill to build and deploy Pillar 1 (BigQuery ML AI.FORECAST with TimesFM 2.0) from scratch for Rocket Companies & Mr. Cooper.
---

# SKILL: Replicating Pillar 1 (`BQML TimesFM` Portfolio Forecaster) From Scratch

Any frontier coding assistant (**Claude Code, Gemini CLI, Cursor, Windsurf, Antigravity/Jetski**) can rebuild Pillar 1 from zero by executing the following 4 engineering steps:

## Step 1: Provision the BigQuery Dataset & Multi-Cohort Table

Run this BigQuery Standard SQL DDL in project `vtxdemos` (or your target `GCP_PROJECT_ID`):

```sql
CREATE SCHEMA IF NOT EXISTS `vtxdemos.rocket_nextgen_timesfm`;

CREATE OR REPLACE TABLE `vtxdemos.rocket_nextgen_timesfm.portfolio_metrics` AS
WITH weeks AS (
  SELECT n, DATE_ADD(DATE "2025-04-02", INTERVAL n WEEK) AS week_dt
  FROM UNNEST(GENERATE_ARRAY(0, 79)) AS n
)
SELECT
  week_dt,
  "mrcooper_refi_locks" AS metric_id,
  "Mr. Cooper + Rocket Weekly Refi Locks (9.5M Servicing Cohort)" AS metric_label,
  ROUND(11200 + 85 * n + 1650 * SIN(n / 4.2) + 620 * COS(n / 2.1), 1) AS metric_value,
  ROUND(6.85 - (n * 0.014) + 0.12 * COS(n / 4.2), 3) AS avg_30yr_rate
FROM weeks
UNION ALL
SELECT
  week_dt,
  "redfin_tour_demand" AS metric_id,
  "Redfin Weekly Buyer Tour & Offer Intent Volume" AS metric_label,
  ROUND(28400 + 140 * n + 4800 * SIN((n - 8) / 8.2) + 950 * COS(n / 3.0), 1) AS metric_value,
  ROUND(6.85 - (n * 0.014) + 0.12 * COS(n / 4.2), 3) AS avg_30yr_rate
FROM weeks
UNION ALL
SELECT
  week_dt,
  "escrow_liquidity_outflow_m" AS metric_id,
  "Mr. Cooper Servicing Escrow Tax & Insurance Outflow ($M/Wk)" AS metric_label,
  ROUND(410 + 1.8 * n + 145 * SIN(n / 2.6) + 55 * COS(n / 1.7), 2) AS metric_value,
  ROUND(6.85 - (n * 0.014) + 0.12 * COS(n / 4.2), 3) AS avg_30yr_rate
FROM weeks
UNION ALL
SELECT
  week_dt,
  "warehouse_funding_b" AS metric_id,
  "Rocket Capital Markets Warehouse Line Draw ($B/Wk)" AS metric_label,
  ROUND(3.85 + 0.028 * n + 0.68 * SIN(n / 4.0) + 0.24 * COS(n / 2.2), 3) AS metric_value,
  ROUND(6.85 - (n * 0.014) + 0.12 * COS(n / 4.2), 3) AS avg_30yr_rate
FROM weeks;
```

## Step 2: Implement the Zero-Shot `AI.FORECAST` (TimesFM) Engine in Python

Implement `engine.py` using `google-cloud-bigquery`. Avoid legacy ARIMA_PLUS training loops; execute Google Research's foundation model directly via `AI.FORECAST`:

```python
"""Pillar 1: BigQuery ML AI.FORECAST (TimesFM) Engine."""
import os
import time
from typing import Any, Dict, List
from google.cloud import bigquery

PROJECT_ID = os.environ.get("GCP_PROJECT_ID", "vtxdemos")
TABLE_FQN = f"{PROJECT_ID}.rocket_nextgen_timesfm.portfolio_metrics"

METRIC_CATALOG = {
    "mrcooper_refi_locks": {
        "title": "Mr. Cooper + Rocket Servicing Refi-Wave Locks",
        "rate_elasticity": -0.0042,
        "dollar_per_unit": 4850,
    },
    "redfin_tour_demand": {
        "title": "Redfin Instant Home-Tour & Buyer Offer Velocity",
        "rate_elasticity": -0.0024,
        "dollar_per_unit": 1920,
    },
    "escrow_liquidity_outflow_m": {
        "title": "Mr. Cooper Tax & Hazard Insurance Escrow Outflow",
        "rate_elasticity": 0.0005,
        "dollar_per_unit": 1000000,
    },
    "warehouse_funding_b": {
        "title": "Rocket Capital Markets Warehouse Line Liquidity Draw",
        "rate_elasticity": -0.0031,
        "dollar_per_unit": 12000000,
    },
}

def run_timesfm_forecast(
    metric_id: str = "mrcooper_refi_locks",
    horizon: int = 12,
    confidence_level: float = 0.90,
    rate_shock_bps: int = -50,
) -> Dict[str, Any]:
    meta = METRIC_CATALOG.get(metric_id, METRIC_CATALOG["mrcooper_refi_locks"])
    shock_mult = 1.0 + (rate_shock_bps * meta["rate_elasticity"])

    sql = f"""
    WITH hist AS (
      SELECT CAST(week_dt AS STRING) AS ts, ROUND(metric_value * {shock_mult:.4f}, 2) AS shocked_val, avg_30yr_rate
      FROM `{TABLE_FQN}` WHERE metric_id = '{metric_id}'
    ),
    fc AS (
      SELECT
        CAST(DATE(forecast_timestamp) AS STRING) AS ts,
        ROUND(forecast_value, 2) AS f_val,
        ROUND(prediction_interval_lower_bound, 2) AS f_low,
        ROUND(prediction_interval_upper_bound, 2) AS f_high
      FROM AI.FORECAST(
        (SELECT PARSE_DATE('%Y-%m-%d', ts) AS week_dt, shocked_val FROM hist),
        data_col => 'shocked_val',
        timestamp_col => 'week_dt',
        horizon => {horizon},
        confidence_level => {confidence_level:.2f}
      )
    )
    SELECT 'H' AS row_type, ts, shocked_val AS val, 0.0 AS low_b, 0.0 AS high_b, avg_30yr_rate
    FROM (SELECT * FROM hist ORDER BY ts DESC LIMIT 28)
    UNION ALL
    SELECT 'F' AS row_type, ts, f_val AS val, f_low AS low_b, f_high AS high_b, 0.0 AS avg_30yr_rate
    FROM fc
    ORDER BY row_type ASC, ts ASC;
    """
    client = bigquery.Client(project=PROJECT_ID)
    rows = list(client.query(sql).result())
    # Process rows into historical and forecast series...
```

## Step 3: Wire the FastAPI Endpoint & Gemini Live Ghost Cursor Tool

Expose the endpoint in `app.py`:

```python
@app.post("/api/pillar1/forecast")
async def api_pillar1_forecast(payload: Dict[str, Any]):
    return run_timesfm_forecast(
        metric_id=payload.get("metric_id", "mrcooper_refi_locks"),
        horizon=int(payload.get("horizon", 12)),
        confidence_level=float(payload.get("confidence_level", 0.90)),
        rate_shock_bps=int(payload.get("rate_shock_bps", -50)),
    )
```

In `pillar-4-live-api-avatar/engine.py`, bind the `control_bqml_timesfm` tool declaration so Gemini Live (Kira/Marcus) can adjust sliders and trigger live SQL execution directly from spoken borrower questions.

## Step 4: Verification Command

```bash
python3 -c "import engine; print(engine.run_timesfm_forecast('mrcooper_refi_locks', 12, 0.90, -50)['kpi_summary'])"
```
