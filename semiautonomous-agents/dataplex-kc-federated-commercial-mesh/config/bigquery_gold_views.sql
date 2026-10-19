-- ============================================================================
-- Enterprise Commercial Intelligence Mesh - BigQuery Gold Semantic Views
-- Dataset: `vtxdemos.commercial_mesh_gold` (Location: US)
-- Governed by Dataplex Knowledge Catalog Business Glossary & Aspect Types
-- ============================================================================

CREATE SCHEMA IF NOT EXISTS `vtxdemos.commercial_mesh_gold`
OPTIONS (
  description = 'Curated Gold Semantic Layer governed by Dataplex Knowledge Catalog for MCP Toolbox and Vertex AI ADK Agents',
  location = 'US'
);

-- ----------------------------------------------------------------------------
-- 1. v_gold_stage2b_stalled_deals
-- Canonical pipeline velocity view isolating Stage 2B - Solutioning bottlenecks,
-- owner inactivity hygiene, and deal pricing margin telemetry.
-- ----------------------------------------------------------------------------
CREATE OR REPLACE VIEW `vtxdemos.commercial_mesh_gold.v_gold_stage2b_stalled_deals`
OPTIONS (
  description = 'Dataplex Gold View: Stage 2B Solutioning opportunities with stage residence duration, inactivity days, and pricing yield.'
) AS
SELECT
  o.opp_id,
  o.account_id,
  o.account_name,
  o.region,
  o.industry,
  o.service_line,
  o.stage_code,
  o.days_at_current_stage,
  o.days_since_last_activity,
  ROUND(o.tcv_usd / 1e6, 2) AS tcv_millions,
  ROUND(o.acv_usd / 1e6, 2) AS acv_millions,
  o.win_probability,
  ROUND(o.tcv_usd * o.win_probability / 1e6, 2) AS weighted_tcv_millions,
  o.markov_regime,
  o.primary_competitor,
  o.has_key_buyer,
  o.client_temperature_score,
  p.pricing_construct,
  p.cci_excluding_be_pct,
  p.adjusted_yield_v4_sigma_capped,
  p.rate_card_discount_pct,
  o.fiscal_quarter,
  o.close_date
FROM `vtxdemos.commercial_mesh_gold.crm_opportunities` o
JOIN `vtxdemos.commercial_mesh_gold.deal_pricing_scenarios` p
  ON o.opp_id = p.opp_id
WHERE o.stage_code = 'Stage 2B - Solutioning';

-- ----------------------------------------------------------------------------
-- 2. v_gold_pricing_yield_dax
-- Materializes multi-stage BI DAX measures into deterministic BigQuery SQL:
--   * CCI Excluding Billable Expenses: Canonical net service margin excluding 0%-margin passthrough
--   * Adjusted Yield v1: Gross Margin on Net Service Revenue
--   * Adjusted Yield v3: Winsorized / trimmed at 5th and 95th industry percentiles
--   * Adjusted Yield v4: Capped at +/- 1.5 standard deviations (sigma)
-- ----------------------------------------------------------------------------
CREATE OR REPLACE VIEW `vtxdemos.commercial_mesh_gold.v_gold_pricing_yield_dax`
OPTIONS (
  description = 'Dataplex Gold View: Materialized DAX pricing formulas (CCI Excl BE, Adjusted Yield v1, v3 outlier-trimmed, v4 1.5-sigma capped, and AI task substitutability).'
) AS
SELECT
  o.opp_id,
  o.account_id,
  o.account_name,
  o.region,
  o.industry,
  o.service_line,
  o.stage_code,
  o.tcv_usd,
  o.win_probability,
  p.pricing_construct,
  p.gross_revenue_usd,
  p.billable_expense_passthrough_usd,
  p.net_service_revenue_usd,
  p.delivery_cost_usd,
  p.cci_including_be_pct,
  p.cci_excluding_be_pct,
  ROUND(p.cci_excluding_be_pct - p.cci_including_be_pct, 4) AS be_passthrough_distortion_pct,
  p.adr_usd,
  p.rate_card_discount_pct,
  p.gross_yield_v1,
  p.adjusted_yield_v3_trimmed,
  p.adjusted_yield_v4_sigma_capped,
  p.ams_ai_task_substitutable_pct,
  o.markov_regime,
  o.fiscal_quarter
FROM `vtxdemos.commercial_mesh_gold.crm_opportunities` o
JOIN `vtxdemos.commercial_mesh_gold.deal_pricing_scenarios` p
  ON o.opp_id = p.opp_id;

-- ----------------------------------------------------------------------------
-- 3. v_gold_markov_regime_analytics
-- Aggregates pipeline health, win probability levers, and margin compression
-- dynamics across Econometric Hidden Markov Regimes.
-- ----------------------------------------------------------------------------
CREATE OR REPLACE VIEW `vtxdemos.commercial_mesh_gold.v_gold_markov_regime_analytics`
OPTIONS (
  description = 'Dataplex Gold View: Econometric Hidden Markov Regime distribution, transition risk, and 6-lever PWin drivers.'
) AS
SELECT
  o.opp_id,
  o.account_id,
  o.account_name,
  o.region,
  o.industry,
  o.service_line,
  o.stage_code,
  o.markov_regime,
  o.regime_duration_days,
  o.days_at_current_stage,
  o.tcv_usd,
  o.win_probability,
  o.primary_competitor,
  o.is_competitive,
  o.has_key_buyer,
  o.client_temperature_score,
  o.pwin_lever_pricing_score,
  o.pwin_lever_exec_sponsor_score,
  o.pwin_lever_tech_diff_score,
  p.rate_card_discount_pct,
  p.cci_excluding_be_pct,
  p.adjusted_yield_v4_sigma_capped,
  CASE
    WHEN o.markov_regime = 'Stalled_Procurement' AND p.rate_card_discount_pct > 0.16 THEN 0.72
    WHEN o.markov_regime = 'Pressured_Margin' AND p.rate_card_discount_pct > 0.12 THEN 0.48
    ELSE 0.15
  END AS regime_erosion_risk_prob
FROM `vtxdemos.commercial_mesh_gold.crm_opportunities` o
JOIN `vtxdemos.commercial_mesh_gold.deal_pricing_scenarios` p
  ON o.opp_id = p.opp_id;

-- ----------------------------------------------------------------------------
-- 4. v_gold_account_360_health
-- Entity-resolved composite view joining Pre-Sales Opportunity & Pricing Spine
-- with Post-Sales Delivery Governance Hub and External Market Signals.
-- ----------------------------------------------------------------------------
CREATE OR REPLACE VIEW `vtxdemos.commercial_mesh_gold.v_gold_account_360_health`
OPTIONS (
  description = 'Dataplex Gold View: Unified Account 360 combining pre-sales Adjusted Yield v4 with post-sales Delivery RAG status, EAC margin variance (bps), and external AI self-sufficiency signals.'
) AS
SELECT
  d.account_id,
  d.account_name,
  d.region,
  d.industry,
  d.rag_status,
  d.csat_score,
  d.nps_score,
  d.sla_slippage_days,
  d.eac_margin_variance_bps,
  d.open_staffing_roles,
  d.unstructured_director_review_notes,
  COUNT(o.opp_id) AS active_opp_count,
  ROUND(SUM(o.tcv_usd) / 1e6, 2) AS total_pipeline_tcv_millions,
  ROUND(AVG(p.cci_excluding_be_pct) * 100, 2) AS avg_cci_excl_be_pct,
  ROUND(AVG(p.adjusted_yield_v4_sigma_capped) * 100, 2) AS avg_adjusted_yield_v4_pct,
  MAX(e.ai_self_sufficiency_index) AS ai_self_sufficiency_index,
  MAX(e.buyer_intent_surge_score) AS buyer_intent_surge_score,
  MAX(e.c_suite_change_detected) AS c_suite_change_detected
FROM `vtxdemos.commercial_mesh_gold.delivery_governance_hub` d
LEFT JOIN `vtxdemos.commercial_mesh_gold.crm_opportunities` o
  ON d.account_id = o.account_id
LEFT JOIN `vtxdemos.commercial_mesh_gold.deal_pricing_scenarios` p
  ON o.opp_id = p.opp_id
LEFT JOIN `vtxdemos.commercial_mesh_gold.external_market_signals` e
  ON d.account_id = e.account_id
GROUP BY
  d.account_id,
  d.account_name,
  d.region,
  d.industry,
  d.rag_status,
  d.csat_score,
  d.nps_score,
  d.sla_slippage_days,
  d.eac_margin_variance_bps,
  d.open_staffing_roles,
  d.unstructured_director_review_notes;
