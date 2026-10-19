-- =============================================================================
-- Rocket Companies × BigQuery ML TimesFM 2.0 (AI.FORECAST)
-- Production SQL DDL and Parameterized Forecasting Query
-- Table: vtxdemos.rocket_nextgen_timesfm.portfolio_metrics
-- =============================================================================

-- -----------------------------------------------------------------------------
-- 1. Table DDL: Historical Multi-Cohort Servicing & Demand Metrics
-- -----------------------------------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `vtxdemos.rocket_nextgen_timesfm`
OPTIONS (
  location = 'us-central1',
  description = 'Rocket Companies Next-Gen Servicing ($2.1T Portfolio) and Redfin Demand Time Series'
);

CREATE OR REPLACE TABLE `vtxdemos.rocket_nextgen_timesfm.portfolio_metrics` (
  metric_id STRING OPTIONS(description = 'Cohort ID: mrcooper_refi_locks, redfin_tour_demand, escrow_liquidity_outflow_m, warehouse_funding_b'),
  week_dt DATE OPTIONS(description = 'Weekly observation timestamp (Monday weekly interval)'),
  metric_value FLOAT64 OPTIONS(description = 'Weekly volume, tour velocity, or dollar volume'),
  avg_30yr_rate FLOAT64 OPTIONS(description = 'Prevailing 30-year fixed conforming mortgage rate (percentage)'),
  created_at TIMESTAMP OPTIONS(description = 'Ingestion timestamp into BigQuery')
)
PARTITION BY week_dt
CLUSTER BY metric_id
OPTIONS(
  description = 'Partitioned weekly time-series storage supporting zero-shot TimesFM 2.0 inference'
);

-- -----------------------------------------------------------------------------
-- 2. Parameterized Zero-Shot TimesFM 2.0 Foundation Model Forecast Query
--    Executed by engine.py::run_timesfm_forecast
--    Parameters:
--      @metric_id: e.g. 'mrcooper_refi_locks'
--      @shock_multiplier: 1.0 + (rate_shock_bps * elasticity) e.g. 1.2100 for -50 bps shock
--      @horizon: Forecast horizon in weeks (e.g. 12)
--      @confidence_level: Calibrated prediction interval coverage (e.g. 0.90 for P10-P90)
-- -----------------------------------------------------------------------------

-- Parameterized AI.FORECAST Query:
WITH shocked_series AS (
  SELECT
    week_dt,
    ROUND(metric_value * @shock_multiplier, 2) AS adjusted_metric_value,
    avg_30yr_rate
  FROM `vtxdemos.rocket_nextgen_timesfm.portfolio_metrics`
  WHERE metric_id = @metric_id
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
  horizon => @horizon,
  confidence_level => @confidence_level
)
ORDER BY forecast_timestamp ASC;

-- -----------------------------------------------------------------------------
-- 3. Unified Historical + Forecast Evaluation Query (Union for Dual-Zone SVG)
-- -----------------------------------------------------------------------------
WITH hist AS (
  SELECT
    CAST(week_dt AS STRING) AS ts,
    ROUND(metric_value, 2) AS val,
    ROUND(metric_value * @shock_multiplier, 2) AS shocked_val,
    avg_30yr_rate
  FROM `vtxdemos.rocket_nextgen_timesfm.portfolio_metrics`
  WHERE metric_id = @metric_id
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
    horizon => @horizon,
    confidence_level => @confidence_level
  )
)
SELECT 'H' AS row_type, ts, val, shocked_val, 0.0 AS low_b, 0.0 AS high_b, avg_30yr_rate
FROM (SELECT * FROM hist ORDER BY ts DESC LIMIT 28)
UNION ALL
SELECT 'F' AS row_type, ts, f_val AS val, f_val AS shocked_val, f_low AS low_b, f_high AS high_b, 0.0 AS avg_30yr_rate
FROM fc
ORDER BY row_type ASC, ts ASC;
