"""Quantitative Risk and What-If Shock Simulation Engine (50ms execution)."""

import math
import time
from typing import Any, Dict, List
from .models import ShockImpactData, ShockParameters


def compute_shock_impact(params: ShockParameters) -> ShockImpactData:
    """
    Computes portfolio sensitivity, Value at Risk (VaR), liquidity stress,
    and supply chain vulnerabilities in < 5ms.
    """
    start_time = time.perf_counter()

    base_portfolio_m = 3450.0  # $3.45 Billion enterprise notional
    base_var_m = 84.5  # $84.5M baseline 99% 10-day VaR
    base_ebitda_m = 480.0  # $480M annual baseline EBITDA
    base_liquidity_reserve_m = 750.0  # $750M liquidity buffer

    # 1. Interest Rate Shock Sensitivity (Duration ~ 3.4 years)
    rate_factor = (params.interest_rate_bps / 100.0) * 0.034
    rate_impact_m = base_portfolio_m * rate_factor

    # 2. Inflation & Tariff Cost Squeeze
    inflation_delta = max(0.0, params.inflation_rate_pct - 2.0)
    cogs_inflation_drag_m = (inflation_delta * 0.045 * base_ebitda_m) + (params.tariff_volatility_pct * 0.032 * base_ebitda_m)

    # 3. Supply Chain Disruption Impact
    sc_factor = params.supply_chain_stress_index / 100.0
    supply_chain_drag_m = sc_factor * 95.0 + (sc_factor ** 1.5) * 45.0

    # 4. Counterparty & Supplier Default Stress
    default_factor = params.supplier_default_risk_pct / 100.0
    counterparty_loss_m = base_portfolio_m * default_factor * 0.18

    # Aggregate Shock Impacts
    total_ebitda_hit_m = round(cogs_inflation_drag_m + supply_chain_drag_m * 0.45 + rate_impact_m * 0.35, 2)
    shocked_var_m = round(base_var_m * (1.0 + (params.interest_rate_bps / 150.0) * 0.4 + sc_factor * 0.65 + (params.tariff_volatility_pct / 20.0) * 0.35), 2)
    var_delta_pct = round(((shocked_var_m - base_var_m) / base_var_m) * 100.0, 1)

    effective_liquidity_m = round(base_liquidity_reserve_m - total_ebitda_hit_m * 0.85 - counterparty_loss_m, 2)
    shortfall_m = round(max(0.0, 350.0 - effective_liquidity_m), 2)

    if effective_liquidity_m >= 550.0:
        buffer_status = "STABLE"
    elif effective_liquidity_m >= 350.0:
        buffer_status = "VULNERABLE"
    else:
        buffer_status = "CRITICAL"

    # Composite Risk Index (0-100)
    risk_index = round(min(100.0, 22.0 + (params.interest_rate_bps / 300.0) * 20.0 + (sc_factor * 35.0) + (params.tariff_volatility_pct / 30.0) * 15.0 + (params.supplier_default_risk_pct / 15.0) * 18.0), 1)

    # Regional Exposure Dynamics
    regional_exposure: List[Dict[str, Any]] = [
        {
            "region": "North America",
            "notional_m": 1420.0,
            "var_m": round(shocked_var_m * 0.41, 1),
            "stress_multiplier": round(1.0 + (params.interest_rate_bps / 200.0) * 0.3, 2),
            "status": "MODERATE" if params.interest_rate_bps < 150 else "ELEVATED",
        },
        {
            "region": "EMEA",
            "notional_m": 980.0,
            "var_m": round(shocked_var_m * 0.29, 1),
            "stress_multiplier": round(1.0 + (params.tariff_volatility_pct / 20.0) * 0.5, 2),
            "status": "ELEVATED" if params.tariff_volatility_pct > 10 else "STABLE",
        },
        {
            "region": "APAC",
            "notional_m": 790.0,
            "var_m": round(shocked_var_m * 0.22, 1),
            "stress_multiplier": round(1.0 + sc_factor * 0.8, 2),
            "status": "CRITICAL" if sc_factor > 0.6 else "MODERATE",
        },
        {
            "region": "LATAM",
            "notional_m": 260.0,
            "var_m": round(shocked_var_m * 0.08, 1),
            "stress_multiplier": round(1.0 + (params.supplier_default_risk_pct / 10.0) * 0.6, 2),
            "status": "WATCH",
        },
    ]

    # Cash Flow Forecast Timeline (Q1 - Q4)
    base_quarterly = [135.0, 142.0, 150.0, 168.0]
    cash_flow_timeline = []
    for q_idx, base_val in enumerate(base_quarterly, 1):
        q_hit = (total_ebitda_hit_m / 4.0) * (0.8 + q_idx * 0.15)
        shocked_val = round(base_val - q_hit, 1)
        cash_flow_timeline.append({
            "quarter": f"2026-Q{q_idx}",
            "baseline_m": base_val,
            "shocked_m": shocked_val,
            "delta_m": round(shocked_val - base_val, 1),
            "delta_pct": round(((shocked_val - base_val) / base_val) * 100.0, 1),
        })

    # Supplier Fragility Matrix
    suppliers = [
        ("NXP / TSMC Substrates", "Semiconductors & Telemetry", "APAC (Taiwan)", 0.35 + sc_factor * 0.55, 320.0),
        ("Rotterdam Maritime Logistics", "Bilateral Freight Line", "EMEA (Netherlands)", 0.20 + (params.tariff_volatility_pct / 50.0), 210.0),
        ("Houston Olefins & Energy", "Feedstocks & Refining", "US Gulf Coast", 0.15 + (params.inflation_rate_pct / 40.0), 450.0),
        ("DBS Singapore FX Clearing", "APAC Liquidity Hub", "APAC (Singapore)", 0.10 + (params.supplier_default_risk_pct / 30.0), 610.0),
    ]

    supplier_fragility_matrix = []
    for name, cat, loc, fragility, exp_m in suppliers:
        fragility_score = round(min(1.0, fragility) * 100.0, 1)
        loss_exp = round(exp_m * (fragility_score / 100.0) * 0.22, 1)
        supplier_fragility_matrix.append({
            "name": name,
            "category": cat,
            "location": loc,
            "fragility_score": fragility_score,
            "exposure_m": exp_m,
            "potential_loss_m": loss_exp,
            "tier": "CRITICAL" if fragility_score > 60 else "WATCH" if fragility_score > 35 else "NORMAL",
        })

    # Dynamic Hedging Recommendations
    hedges = []
    if params.interest_rate_bps > 50:
        hedges.append({
            "action": "Execute $450M SOFR Receiver Swaption Collar",
            "hedged_risk": "Interest Rate Upward Drift",
            "cost_basis_k": 320,
            "projected_savings_m": round((params.interest_rate_bps / 100.0) * 14.5, 2),
            "urgency": "IMMEDIATE",
        })
    if sc_factor > 0.35:
        hedges.append({
            "action": "Activate Secondary APAC Inventory Line & Dual-Sourcing Buffer",
            "hedged_risk": "Supply Chain Bottleneck Shock",
            "cost_basis_k": 850,
            "projected_savings_m": round(sc_factor * 38.0, 2),
            "urgency": "HIGH",
        })
    if params.tariff_volatility_pct > 8.0:
        hedges.append({
            "action": "Hedge EUR/USD & CNY Bilateral FX Exposure via Forward Contracts",
            "hedged_risk": "Tariff & FX Volatility Spillover",
            "cost_basis_k": 180,
            "projected_savings_m": round((params.tariff_volatility_pct / 10.0) * 11.2, 2),
            "urgency": "MEDIUM",
        })
    if not hedges:
        hedges.append({
            "action": "Maintain Dynamic Liquidity Buffer with Continuous A2A Sentinel Polling",
            "hedged_risk": "Baseline Systemic Stability",
            "cost_basis_k": 0,
            "projected_savings_m": 0.0,
            "urgency": "MONITORING",
        })

    calc_latency = (time.perf_counter() - start_time) * 1000.0

    return ShockImpactData(
        calculation_latency_ms=round(calc_latency, 2),
        total_portfolio_value_m=base_portfolio_m,
        value_at_risk_99_m=shocked_var_m,
        var_delta_pct=var_delta_pct,
        ebitda_impact_m=total_ebitda_hit_m,
        liquidity_buffer_status=buffer_status,
        liquidity_shortfall_m=shortfall_m,
        risk_score_index=risk_index,
        regional_exposure=regional_exposure,
        cash_flow_timeline=cash_flow_timeline,
        supplier_fragility_matrix=supplier_fragility_matrix,
        suggested_hedging_actions=hedges,
    )
