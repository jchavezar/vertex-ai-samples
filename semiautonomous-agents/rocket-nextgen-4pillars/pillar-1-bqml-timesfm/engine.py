"""Pillar 1: BigQuery ML AI.FORECAST (TimesFM) Engine for Rocket + Mr. Cooper $2.1T Servicing."""

import os
import time
from typing import Any, Dict, List
from google.cloud import bigquery

PROJECT_ID = os.environ.get("GCP_PROJECT_ID", "vtxdemos")
BQ_DATASET_ID = os.environ.get("BQ_DATASET_ID", "rocket_nextgen_timesfm")
BQ_TABLE_ID = os.environ.get("BQ_TABLE_ID", "portfolio_metrics")
TABLE_FQN = os.environ.get("BQ_TABLE_FQN", f"{PROJECT_ID}.{BQ_DATASET_ID}.{BQ_TABLE_ID}")

METRIC_CATALOG: Dict[str, Dict[str, Any]] = {
    "mrcooper_refi_locks": {
        "title": "Mr. Cooper + Rocket Servicing Refi-Wave Locks",
        "unit": "locks/wk",
        "subtitle": "9.5M Serviced Loans · Zero-Shot TimesFM Recapture Forecast",
        "rate_elasticity": -0.0042,  # -100 bps rate drop -> +42% refi lock surge
        "dollar_per_unit": 4850,     # $4,850 net origination margin per recaptured refi lock
        "claude_gap": "Claude has 0 time-series foundation weights and cannot ingest 9.5M servicing rows inside BigQuery.",
    },
    "redfin_tour_demand": {
        "title": "Redfin Instant Home-Tour & Buyer Offer Velocity",
        "unit": "tours/wk",
        "subtitle": "Redfin Top-of-Funnel Search -> Rocket Mortgage Pre-Approval Conversion",
        "rate_elasticity": -0.0024,  # -100 bps rate drop -> +24% buyer tour surge
        "dollar_per_unit": 1920,
        "claude_gap": "Claude cannot run SQL-native multivariate forecasting across 50M monthly Redfin visitors.",
    },
    "escrow_liquidity_outflow_m": {
        "title": "Mr. Cooper Tax & Hazard Insurance Escrow Outflow",
        "unit": "$M/wk",
        "subtitle": "$2.1T Servicing Portfolio · Treasury Float & Municipal Tax Spike Predictor",
        "rate_elasticity": 0.0005,
        "dollar_per_unit": 1000000,
        "claude_gap": "Claude text tokens hallucinate seasonal municipal tax spikes and lack calibrated P10/P90 bounds.",
    },
    "warehouse_funding_b": {
        "title": "Rocket Capital Markets Warehouse Line Liquidity Draw",
        "unit": "$B/wk",
        "subtitle": "Secondary Market MBS Hedging & Warehouse Line Capacity Allocation",
        "rate_elasticity": -0.0031,
        "dollar_per_unit": 12000000,
        "claude_gap": "Claude cannot compute zero-shot probabilistic prediction intervals (80%-95% CI) in SQL.",
    },
}

_bq_client: bigquery.Client | None = None


def get_bq_client() -> bigquery.Client:
    global _bq_client
    if _bq_client is None:
        _bq_client = bigquery.Client(project=PROJECT_ID)
    return _bq_client


def run_timesfm_forecast(
    metric_id: str = "mrcooper_refi_locks",
    horizon: int = 12,
    confidence_level: float = 0.90,
    rate_shock_bps: int = -50,
) -> Dict[str, Any]:
    """Executes a live BigQuery ML `AI.FORECAST` (TimesFM) query against `vtxdemos.rocket_nextgen_timesfm.portfolio_metrics`."""
    t0 = time.perf_counter()
    if metric_id not in METRIC_CATALOG:
        metric_id = "mrcooper_refi_locks"
    meta = METRIC_CATALOG[metric_id]
    horizon = max(4, min(24, int(horizon)))
    confidence_level = max(0.80, min(0.95, float(confidence_level)))
    rate_shock_bps = max(-150, min(100, int(rate_shock_bps)))

    shock_multiplier = 1.0 + (rate_shock_bps * meta["rate_elasticity"])

    display_sql = f"""-- Live BigQuery ML Zero-Shot Foundation Forecast (Google Research TimesFM)
WITH shocked_series AS (
  SELECT
    week_dt,
    ROUND(metric_value * {shock_multiplier:.4f}, 2) AS adjusted_metric_value,
    avg_30yr_rate
  FROM `{TABLE_FQN}`
  WHERE metric_id = '{metric_id}'
)
SELECT
  forecast_timestamp,
  ROUND(forecast_value, 2) AS forecast_value,
  ROUND(prediction_interval_lower_bound, 2) AS lower_bound,
  ROUND(prediction_interval_upper_bound, 2) AS upper_bound,
  confidence_level
FROM AI.FORECAST(
  TABLE shocked_series,
  data_col => 'adjusted_metric_value',
  timestamp_col => 'week_dt',
  horizon => {horizon},
  confidence_level => {confidence_level:.2f}
)
ORDER BY forecast_timestamp ASC;"""

    combined_query = f"""
    WITH hist AS (
      SELECT
        CAST(week_dt AS STRING) AS ts,
        ROUND(metric_value, 2) AS val,
        ROUND(metric_value * {shock_multiplier:.4f}, 2) AS shocked_val,
        avg_30yr_rate
      FROM `{TABLE_FQN}`
      WHERE metric_id = '{metric_id}'
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
    SELECT 'H' AS row_type, ts, val, shocked_val, 0.0 AS low_b, 0.0 AS high_b, avg_30yr_rate
    FROM (SELECT * FROM hist ORDER BY ts DESC LIMIT 28)
    UNION ALL
    SELECT 'F' AS row_type, ts, f_val AS val, f_val AS shocked_val, f_low AS low_b, f_high AS high_b, 0.0 AS avg_30yr_rate
    FROM fc
    ORDER BY row_type ASC, ts ASC
    """

    client = get_bq_client()
    rows = list(client.query(combined_query).result())
    latency_ms = int((time.perf_counter() - t0) * 1000)

    historical: List[Dict[str, Any]] = []
    forecast: List[Dict[str, Any]] = []
    for r in rows:
        if r["row_type"] == "H":
            historical.append({
                "date": r["ts"],
                "baseline": float(r["val"]),
                "value": float(r["shocked_val"]),
                "rate_30yr": float(r["avg_30yr_rate"]),
            })
        else:
            forecast.append({
                "date": r["ts"],
                "forecast": float(r["val"]),
                "lower": float(r["low_b"]),
                "upper": float(r["high_b"]),
            })

    historical.sort(key=lambda x: x["date"])
    forecast.sort(key=lambda x: x["date"])

    last_hist = historical[-1]["value"] if historical else 1.0
    peak_fc = max((f["forecast"] for f in forecast), default=last_hist)
    total_fc = sum(f["forecast"] for f in forecast)
    delta_pct = ((peak_fc - last_hist) / max(last_hist, 1e-6)) * 100.0
    est_revenue_impact = total_fc * meta["dollar_per_unit"] * (abs(rate_shock_bps) / 100.0 + 0.15)

    return {
        "ok": True,
        "pillar": "Pillar 1 · BigQuery ML TimesFM (AI.FORECAST)",
        "engine": "BigQuery ML TimesFM Foundation Model (Zero-Shot SQL)",
        "latency_ms": latency_ms,
        "metric_id": metric_id,
        "meta": meta,
        "params": {
            "horizon": horizon,
            "confidence_level": confidence_level,
            "rate_shock_bps": rate_shock_bps,
            "shock_multiplier": round(shock_multiplier, 4),
        },
        "kpis": {
            "last_historical": round(last_hist, 2),
            "peak_forecast": round(peak_fc, 2),
            "cumulative_horizon": round(total_fc, 2),
            "delta_pct": round(delta_pct, 1),
            "est_value_usd": round(est_revenue_impact, 0),
        },
        "historical": historical,
        "forecast": forecast,
        "sql": display_sql,
    }


if __name__ == "__main__":
    res = run_timesfm_forecast("mrcooper_refi_locks", horizon=8, confidence_level=0.90, rate_shock_bps=-50)
    print(f"Executed in {res['latency_ms']}ms | Forecast rows: {len(res['forecast'])} | Peak: {res['kpis']['peak_forecast']}")
