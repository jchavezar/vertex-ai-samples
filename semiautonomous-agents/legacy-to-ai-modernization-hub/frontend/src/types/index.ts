export interface LegacyRecord {
  transaction_id: string;
  gl_code: string;
  counterparty_bic: string;
  counterparty_name: string;
  settlement_date: string;
  currency: string;
  notional_amount: number;
  fx_spread_bps: number;
  clearing_house: string;
  margin_tier: string;
  risk_rating: string;
  liquidity_bucket: string;
  tax_jurisdiction: string;
  dodd_frank_tag: string;
  basel_risk_weight_pct: number;
  sla_status: string;
  audit_timestamp: string;
  batch_id: string;
  reconciliation_flag: string;
  override_notes: string;
}

export interface LegacyQueryResponse {
  total_records: number;
  page: number;
  page_size: number;
  total_pages: number;
  query_latency_ms: number;
  data: LegacyRecord[];
  server_timestamp: string;
  db_engine: string;
}

export interface RefactorStep {
  stage_id: number;
  stage_name: string;
  title: string;
  status: 'pending' | 'in_progress' | 'completed';
  duration_ms: number;
  details: string;
  code_artifact?: string;
  metrics: Record<string, any>;
}

export interface RefactorEvent {
  event: 'pipeline_started' | 'stage_progress' | 'stage_completed' | 'pipeline_finished';
  pipeline_id: string;
  current_stage: number;
  total_stages: number;
  progress_percentage: number;
  step?: RefactorStep;
  summary?: {
    status: string;
    legacy_system: string;
    modernized_system: string;
    performance_gain: string;
    dev_time_saved: string;
    steps: RefactorStep[];
  };
}

export interface ShockParameters {
  interest_rate_bps: number;
  inflation_rate_pct: number;
  supply_chain_stress_index: number;
  tariff_volatility_pct: number;
  supplier_default_risk_pct: number;
}

export interface RegionalExposure {
  region: string;
  notional_m: number;
  var_m: number;
  stress_multiplier: number;
  status: string;
}

export interface CashFlowQuarter {
  quarter: string;
  baseline_m: number;
  shocked_m: number;
  delta_m: number;
  delta_pct: number;
}

export interface SupplierFragility {
  name: string;
  category: string;
  location: string;
  fragility_score: number;
  exposure_m: number;
  potential_loss_m: number;
  tier: string;
}

export interface HedgingAction {
  action: string;
  hedged_risk: string;
  cost_basis_k: number;
  projected_savings_m: number;
  urgency: string;
}

export interface ShockImpactData {
  calculation_latency_ms: number;
  total_portfolio_value_m: number;
  value_at_risk_99_m: number;
  var_delta_pct: number;
  ebitda_impact_m: number;
  liquidity_buffer_status: 'STABLE' | 'VULNERABLE' | 'CRITICAL';
  liquidity_shortfall_m: number;
  risk_score_index: number;
  regional_exposure: RegionalExposure[];
  cash_flow_timeline: CashFlowQuarter[];
  supplier_fragility_matrix: SupplierFragility[];
  suggested_hedging_actions: HedgingAction[];
}

export interface AgentQueryResponse {
  query: string;
  intent_detected: string;
  synthesis_markdown: string;
  confidence_score: number;
  reasoning_trace: string[];
  suggested_actions: HedgingAction[];
  shock_impact: ShockImpactData;
  latency_ms: number;
  model_used: string;
}

export interface BoardMemoResponse {
  memo_id: string;
  title: string;
  timestamp: string;
  author: string;
  target_audience: string;
  executive_summary: string;
  full_markdown: string;
  key_metrics_table: Array<{ metric: string; value: string; status: string }>;
  recommended_board_actions: string[];
  governance_signoffs: Array<{ role: string; status: string; timestamp: string }>;
  generation_time_ms: number;
}
