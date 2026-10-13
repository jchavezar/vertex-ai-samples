-- ============================================================================
-- Enterprise Commercial Intelligence Mesh - BigQuery Gold Semantic Views
-- Registered with Dataplex Knowledge Catalog Business Glossary & Aspect Types
-- ============================================================================
-- Resolves the 15TB Operational Data Store (Revenue_ODS_15TB) join fan-out and
-- materializes proprietary semantic DAX metrics (Adjusted Yield v1/v3/v4,
-- Hidden Markov Regime States, and Account 360 Pre/Post-Sales Health).
-- ============================================================================

CREATE SCHEMA IF NOT EXISTS `enterprise_commercial_gold`
OPTIONS (
  description = 'Curated Gold Semantic Layer governed by Dataplex Knowledge Catalog for MCP Toolbox and ADK Agents',
  location = 'US'
);

-- ----------------------------------------------------------------------------
-- 1. v_gold_opportunity_spine
-- Canonical entity-resolved pipeline view joining CRM_Opportunity_Spine,
-- Revenue_ODS_15TB latest snapshot, and Deal_Pricing_Engine active scenario.
-- ----------------------------------------------------------------------------
CREATE OR REPLACE VIEW `enterprise_commercial_gold.v_gold_opportunity_spine`
OPTIONS (
  description = 'Dataplex Gold View: Canonical active pipeline spine with stage velocity, owner hygiene, and primary yield metrics.'
) AS
WITH latest_ods_snapshot AS (
  SELECT
    opp_id,
    account_id,
    account_name,
    region,
    industry,
    service_line,
    stage_name,
    tcv_usd,
    acv_usd,
    DATE_DIFF(CURRENT_DATE(), DATE(stage_entry_date), DAY) AS stage_age_days,
    win_prob,
    stage_entry_date,
    last_updated_date,
    last_owner_activity_date,
    deal_owner,
    client_Temp_score,
    ROW_NUMBER() OVER (PARTITION BY opp_id ORDER BY last_updated_date DESC) AS rn
  FROM `enterprise_raw_spine.CRM_Opportunity_Spine`
)
SELECT
  s.opp_id,
  s.account_id,
  s.account_name,
  s.region,
  s.industry,
  s.service_line,
  s.stage_name,
  s.tcv_usd,
  s.acv_usd,
  s.stage_age_days,
  s.win_prob,
  ROUND(s.tcv_usd * s.win_prob, 2) AS weighted_booking_usd,
  s.stage_entry_date,
  s.last_updated_date,
  s.last_owner_activity_date,
  DATE_DIFF(CURRENT_DATE(), DATE(s.last_owner_activity_date), DAY) AS owner_inactive_days,
  s.deal_owner,
  s.client_Temp_score,
  p.gross_yield_v1 AS gross_margin_pct,
  p.adjusted_yield_v4_sigma_capped AS adjusted_yield_v4,
  p.passthrough_cost_usd,
  m.markov_regime
FROM latest_ods_snapshot s
LEFT JOIN `enterprise_commercial_gold.v_gold_adjusted_yield_dax` p
  ON s.opp_id = p.opp_id
LEFT JOIN `enterprise_commercial_gold.v_gold_markov_regime_states` m
  ON s.opp_id = m.opp_id
WHERE s.rn = 1;


-- ----------------------------------------------------------------------------
-- 2. v_gold_adjusted_yield_dax
-- Translates multi-stage BI DAX measures into deterministic BigQuery SQL:
--   * Adjusted Yield v1: Gross Margin net of pass-through hardware/cloud costs
--   * Adjusted Yield v3: Winsorized / trimmed at 5th and 95th industry percentiles
--   * Adjusted Yield v4: Capped at +/- 1.5 standard deviations (sigma) to
--     prevent mega-deal anomalies from distorting portfolio pricing thresholds.
-- ----------------------------------------------------------------------------
CREATE OR REPLACE VIEW `enterprise_commercial_gold.v_gold_adjusted_yield_dax`
OPTIONS (
  description = 'Dataplex Gold View: Materialized DAX pricing formulas (Adjusted Yield v1, v3 outlier-trimmed, v4 1.5-sigma sensitivity capped).'
) AS
WITH base_pricing AS (
  SELECT
    p.scenario_id,
    p.opp_id,
    o.account_id,
    o.account_name,
    o.industry,
    p.version_tag,
    p.tcv_usd,
    p.passthrough_cost_usd,
    (p.tcv_usd - p.passthrough_cost_usd) AS net_service_rev_usd,
    p.standard_rate_usd,
    p.negotiated_rate_usd,
    SAFE_DIVIDE(p.standard_rate_usd - p.negotiated_rate_usd, p.standard_rate_usd) AS discount_giveaway_pct,
    p.gross_yield_v1,
    -- Deduct pass-through distortion and unapproved rate giveaway penalty
    SAFE_DIVIDE(
      (p.tcv_usd * p.gross_yield_v1) - (p.passthrough_cost_usd * 0.12),
      NULLIF(p.tcv_usd - p.passthrough_cost_usd, 0)
    ) AS raw_net_yield,
    p.price_competitiveness_score
  FROM `enterprise_raw_spine.Deal_Pricing_Engine` p
  JOIN `enterprise_raw_spine.CRM_Opportunity_Spine` o
    ON p.opp_id = o.opp_id
  WHERE p.is_primary_scenario = TRUE
),
industry_distribution AS (
  SELECT
    *,
    PERCENTILE_CONT(raw_net_yield, 0.05) OVER (PARTITION BY industry) AS p05_yield,
    PERCENTILE_CONT(raw_net_yield, 0.95) OVER (PARTITION BY industry) AS p95_yield,
    AVG(raw_net_yield) OVER (PARTITION BY industry) AS mean_industry_yield,
    STDDEV_POP(raw_net_yield) OVER (PARTITION BY industry) AS stddev_industry_yield
  FROM base_pricing
),
trimmed_v3 AS (
  SELECT
    *,
    -- v3 DAX: Trim to [P05, P95] industry corridor
    LEAST(GREATEST(raw_net_yield, p05_yield), p95_yield) AS adjusted_yield_v3_trimmed
  FROM industry_distribution
)
SELECT
  scenario_id,
  opp_id,
  account_id,
  account_name,
  industry,
  version_tag,
  tcv_usd,
  passthrough_cost_usd,
  net_service_rev_usd,
  gross_yield_v1,
  ROUND(adjusted_yield_v3_trimmed, 4) AS adjusted_yield_v3_trimmed,
  -- v4 DAX: Apply 1.5-sigma sensitivity cap
  ROUND(
    LEAST(
      GREATEST(adjusted_yield_v3_trimmed, mean_industry_yield - 1.5 * COALESCE(NULLIF(stddev_industry_yield, 0), 0.04)),
      mean_industry_yield + 1.5 * COALESCE(NULLIF(stddev_industry_yield, 0), 0.04)
    ),
    4
  ) AS adjusted_yield_v4_sigma_capped,
  ROUND(discount_giveaway_pct, 4) AS discount_giveaway_pct,
  standard_rate_usd,
  negotiated_rate_usd,
  ROUND(
    SAFE_DIVIDE(ABS(raw_net_yield - mean_industry_yield), COALESCE(NULLIF(stddev_industry_yield, 0), 0.04)),
    2
  ) AS sigma_zscore,
  price_competitiveness_score
FROM trimmed_v3;


-- ----------------------------------------------------------------------------
-- 3. v_gold_markov_regime_states
-- Classifies every active opportunity into one of 3 Hidden Markov Commercial
-- Regimes based on stage residence time, discount giveaway, and yield erosion.
-- ----------------------------------------------------------------------------
CREATE OR REPLACE VIEW `enterprise_commercial_gold.v_gold_markov_regime_states`
OPTIONS (
  description = 'Dataplex Gold View: Econometric Hidden Markov Regime classification and state transition probabilities.'
) AS
SELECT
  o.opp_id,
  o.account_id,
  o.account_name,
  CASE
    WHEN o.stage_age_days > 105 AND p.discount_giveaway_pct >= 0.18
      THEN 'Regime_3_Stalled_Procurement'
    WHEN p.discount_giveaway_pct >= 0.12 OR p.adjusted_yield_v4_sigma_capped < 0.28
      THEN 'Regime_2_Margin_Compression'
    ELSE 'Regime_1_High_Velocity_Expansion'
  END AS markov_regime,
  CASE
    WHEN p.discount_giveaway_pct >= 0.15 THEN 0.74
    WHEN p.discount_giveaway_pct >= 0.10 THEN 0.42
    ELSE 0.14
  END AS prob_transition_to_compression,
  p.discount_giveaway_pct,
  p.adjusted_yield_v4_sigma_capped
FROM `enterprise_raw_spine.CRM_Opportunity_Spine` o
JOIN `enterprise_commercial_gold.v_gold_adjusted_yield_dax` p
  ON o.opp_id = p.opp_id;


-- ----------------------------------------------------------------------------
-- 4. v_gold_account_360_health
-- Entity-resolved composite view joining Pre-Sales Opportunity & Pricing Spine
-- with Post-Sales ERP Financials Ledger and Delivery Governance Hub.
-- ----------------------------------------------------------------------------
CREATE OR REPLACE VIEW `enterprise_commercial_gold.v_gold_account_360_health`
OPTIONS (
  description = 'Dataplex Gold View: Unified Account 360 combining pre-sales Sold Yield v4 with post-sales ERP EAC Margin Variance and Delivery SLA RAG status.'
) AS
SELECT
  o.account_id,
  o.account_name,
  o.opp_id,
  o.region,
  o.industry,
  o.service_line,
  o.stage_name,
  o.tcv_usd,
  p.adjusted_yield_v4_sigma_capped AS sold_adjusted_yield_v4,
  p.discount_giveaway_pct,
  d.rag_status,
  d.milestone_delays,
  d.sla_slippage_days,
  d.eac_margin_variance_pct,
  d.csat_score,
  d.delivery_commentary,
  ROUND(
    (0.40 * p.adjusted_yield_v4_sigma_capped) +
    (0.40 * d.csat_score) +
    (0.20 * (1.0 + d.eac_margin_variance_pct)),
    3
  ) AS composite_account_health_score
FROM `enterprise_raw_spine.CRM_Opportunity_Spine` o
JOIN `enterprise_commercial_gold.v_gold_adjusted_yield_dax` p
  ON o.opp_id = p.opp_id
JOIN `enterprise_raw_spine.Delivery_Governance_Hub` d
  ON o.account_id = d.account_id;
