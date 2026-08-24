"""Data models and schemas for Legacy to AI-Native Modernization Hub."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class LegacyRecord(BaseModel):
    """Legacy 2015 Enterprise ERP record with 20 columns."""
    transaction_id: str = Field(..., description="Unique Transaction Reference")
    gl_code: str = Field(..., description="General Ledger Account Code")
    counterparty_bic: str = Field(..., description="Counterparty BIC / SWIFT Code")
    counterparty_name: str = Field(..., description="Entity Name")
    settlement_date: str = Field(..., description="Settlement Date (YYYY-MM-DD)")
    currency: str = Field(..., description="Currency ISO 4217")
    notional_amount: float = Field(..., description="Notional Amount")
    fx_spread_bps: float = Field(..., description="FX Spread in Basis Points")
    clearing_house: str = Field(..., description="Clearing House Facility")
    margin_tier: str = Field(..., description="Collateral Margin Tier (Tier 1-4)")
    risk_rating: str = Field(..., description="Internal Credit Risk Grade (AAA-CCC)")
    liquidity_bucket: str = Field(..., description="Liquidity Horizon Bucket")
    tax_jurisdiction: str = Field(..., description="Tax Jurisdiction Code")
    dodd_frank_tag: str = Field(..., description="Dodd-Frank Clearing Category")
    basel_risk_weight_pct: float = Field(..., description="Basel III Standardized Risk Weight %")
    sla_status: str = Field(..., description="SLA Processing Status")
    audit_timestamp: str = Field(..., description="ISO Audit Log Timestamp")
    batch_id: str = Field(..., description="Overnight Batch Identifier")
    reconciliation_flag: str = Field(..., description="Automated Recon Status")
    override_notes: str = Field(..., description="Manual Operator Override Notes")


class LegacyQueryFilter(BaseModel):
    """Filters for the legacy enterprise ERP table."""
    page: int = Field(1, ge=1)
    page_size: int = Field(15, ge=1, le=100)
    search: Optional[str] = None
    currency: Optional[str] = None
    risk_rating: Optional[str] = None
    margin_tier: Optional[str] = None
    clearing_house: Optional[str] = None
    sla_status: Optional[str] = None
    simulate_slow_query_ms: int = Field(1200, ge=0, le=10000)


class LegacyQueryResponse(BaseModel):
    """Paginated response from legacy 2015 database."""
    total_records: int
    page: int
    page_size: int
    total_pages: int
    query_latency_ms: float
    data: List[LegacyRecord]
    server_timestamp: str
    db_engine: str = "Oracle Exadata 11g R2 (Legacy Connector)"


class RefactorStep(BaseModel):
    """A step in the Antigravity Autonomous Refactor Pipeline."""
    stage_id: int
    stage_name: str
    title: str
    status: str  # "pending", "in_progress", "completed"
    duration_ms: int
    details: str
    code_artifact: Optional[str] = None
    metrics: Dict[str, Any] = Field(default_factory=dict)


class RefactorPipelineStatus(BaseModel):
    """Status of the live Antigravity Autonomous Refactor pipeline."""
    pipeline_id: str
    is_running: bool
    current_stage: int
    total_stages: int
    progress_percentage: int
    steps: List[RefactorStep]
    summary: Optional[Dict[str, Any]] = None


class ShockParameters(BaseModel):
    """Real-time reactive What-If shock parameters."""
    interest_rate_bps: float = Field(0.0, description="Interest rate delta in basis points (-200 to +300)")
    inflation_rate_pct: float = Field(2.5, description="Headline inflation percentage (0.0 to 10.0)")
    supply_chain_stress_index: float = Field(25.0, description="Disruption stress index (0 to 100)")
    tariff_volatility_pct: float = Field(5.0, description="Tariff / FX volatility shock % (0 to 30)")
    supplier_default_risk_pct: float = Field(1.5, description="Counterparty default probability % (0 to 15)")


class ShockImpactData(BaseModel):
    """Calculated dynamic risk and financial shock impacts."""
    calculation_latency_ms: float
    total_portfolio_value_m: float
    value_at_risk_99_m: float
    var_delta_pct: float
    ebitda_impact_m: float
    liquidity_buffer_status: str  # "STABLE", "VULNERABLE", "CRITICAL"
    liquidity_shortfall_m: float
    risk_score_index: float  # 0 to 100
    regional_exposure: List[Dict[str, Any]]
    cash_flow_timeline: List[Dict[str, Any]]
    supplier_fragility_matrix: List[Dict[str, Any]]
    suggested_hedging_actions: List[Dict[str, Any]]


class AgentQueryRequest(BaseModel):
    """Natural language query from executive user."""
    query: str
    shock_params: Optional[ShockParameters] = None
    use_grounding: bool = True


class AgentQueryResponse(BaseModel):
    """Generative UI response with synthesized metrics, insights, and actions."""
    query: str
    intent_detected: str
    synthesis_markdown: str
    confidence_score: float
    reasoning_trace: List[str]
    suggested_actions: List[Dict[str, Any]]
    shock_impact: ShockImpactData
    latency_ms: float
    model_used: str


class BoardMemoRequest(BaseModel):
    """Request to synthesize an Executive Boardroom Decision Memo."""
    query_context: str
    shock_params: ShockParameters
    memo_title: Optional[str] = "Strategic Liquidity & Supply Chain Shock Assessment"
    target_audience: str = "Board of Directors & Audit Committee"


class BoardMemoResponse(BaseModel):
    """Boardroom Decision Memo payload."""
    memo_id: str
    title: str
    timestamp: str
    author: str = "Antigravity Autonomous Enterprise Agent (Gemini 2.5/3 Engine)"
    target_audience: str
    executive_summary: str
    full_markdown: str
    key_metrics_table: List[Dict[str, Any]]
    recommended_board_actions: List[str]
    governance_signoffs: List[Dict[str, str]]
    generation_time_ms: float
