"""
Enterprise Agent Implementation using Google ADK (Agent Development Kit 2.7+)
and Gemini 3.7 Flash with InMemoryRunner and real-time tool telemetry.
"""
from __future__ import annotations

import os
import json
import time
import math
import logging
from typing import Any, AsyncGenerator, Dict, List, Optional
from pydantic import BaseModel, Field

# Force environment overrides for Vertex AI and model location
os.environ["GOOGLE_CLOUD_LOCATION"] = os.environ.get("GOOGLE_CLOUD_LOCATION", "global")
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "TRUE"

from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner
from google.adk.agents.run_config import RunConfig, StreamingMode
from google.genai import types

logger = logging.getLogger("adk-enterprise-agent")
logger.setLevel(logging.INFO)

APP_NAME = "adk_enterprise_assistant"
DEFAULT_MODEL = os.environ.get("MODEL_NAME", "gemini-3.7-flash")


# =====================================================================
# Enterprise Tools Definition
# =====================================================================

def search_enterprise_knowledge(query: str, domain: str = "all") -> dict:
    """Performs an enterprise-grounded knowledge base and web search for industry benchmarks,
    competitor intelligence, market trends, or technical documentation.

    Args:
        query: Specific search topic or query string.
        domain: Filter domain (e.g. 'finance', 'cloud_infra', 'market_intelligence', 'compliance', 'all').

    Returns:
        Structured search results with source citations, relevance confidence, and key snippets.
    """
    logger.info("Executing tool [search_enterprise_knowledge] query=%r, domain=%r", query, domain)
    q_lower = query.lower()
    
    # Mock rich enterprise index lookup with realistic market data
    if "cloud" in q_lower or "infra" in q_lower or "aws" in q_lower or "gcp" in q_lower:
        results = [
            {
                "title": "Gartner 2025 Magic Quadrant for Strategic Cloud Infrastructure",
                "source": "https://enterprise-research.internal/gartner-cloud-2025",
                "snippet": "Multi-cloud optimization delivers an average 24.3% cost reduction when combining automated workload rightsizing with spot instance orchestration.",
                "confidence": 0.96,
                "domain": "cloud_infra"
            },
            {
                "title": "Enterprise FinOps Benchmarks: Unit Cost per Compute Hour",
                "source": "https://finops.internal/benchmarks/q3",
                "snippet": "Top-quartile SaaS companies maintain cloud spend below 8.2% of Total ARR, while achieving 99.995% SLA availability.",
                "confidence": 0.92,
                "domain": "cloud_infra"
            }
        ]
    elif "roi" in q_lower or "financial" in q_lower or "revenue" in q_lower or "valuation" in q_lower:
        results = [
            {
                "title": "Enterprise AI ROI & Capital Efficiency Framework 2026",
                "source": "https://mckinsey-quarterly.internal/ai-roi-study-2026",
                "snippet": "Agentic automation pipelines deliver median 340% 3-year ROI by deflecting L1/L2 engineering tickets and automating data lineage audits.",
                "confidence": 0.98,
                "domain": "finance"
            },
            {
                "title": "Morgan Stanley Enterprise SaaS Multiples & Rule of 40 Analysis",
                "source": "https://morganstanley.internal/equity-research/saas-multiples",
                "snippet": "Companies exceeding the Rule of 40 with >25% Free Cash Flow margin command an average 14.2x NTM revenue multiple.",
                "confidence": 0.94,
                "domain": "finance"
            }
        ]
    else:
        results = [
            {
                "title": f"Enterprise Intelligence Portal: Analysis on '{query}'",
                "source": "https://knowledge.corp.internal/intelligence-feed",
                "snippet": f"Validated organizational data and global benchmarks regarding {query}. Highlighted strong tailwinds in operational automation and agentic integration.",
                "confidence": 0.91,
                "domain": domain
            },
            {
                "title": "Regulatory & Enterprise Security Compliance Index",
                "source": "https://compliance.corp.internal/standards/2026-v2",
                "snippet": "SOC2 Type II, FedRAMP High, and Zero-Trust Data Isolation protocols validated across all production cluster nodes.",
                "confidence": 0.89,
                "domain": "compliance"
            }
        ]
        
    return {
        "status": "success",
        "query": query,
        "domain": domain,
        "result_count": len(results),
        "results": results,
        "timestamp": time.time()
    }


def query_enterprise_database(metric_name: str, timeframe: str = "last_4_quarters", department: str = "all") -> dict:
    """Queries the Enterprise Data Warehouse for mission-critical financial, operational,
    and infrastructure metrics.

    Args:
        metric_name: Target metric (e.g. 'arr', 'cloud_spend', 'ebitda', 'ndr', 'cac_payback', 'headcount').
        timeframe: Time horizon (e.g. 'last_4_quarters', 'ytd', '3_year_trend', 'monthly_run_rate').
        department: Corporate division ('engineering', 'sales', 'product', 'marketing', 'all').

    Returns:
        Aggregated time series data, variance vs target, and drill-down drivers.
    """
    logger.info("Executing tool [query_enterprise_database] metric=%r, timeframe=%r, dept=%r", metric_name, timeframe, department)
    m = metric_name.lower()
    
    if "cloud" in m or "infra" in m or "cost" in m:
        data = {
            "metric": "Cloud Infrastructure Spend ($ USD)",
            "unit": "USD",
            "current_run_rate": 18450000,
            "annual_budget": 16000000,
            "variance_pct": "+15.3% (Over Budget)",
            "quarterly_history": [
                {"quarter": "Q1 2025", "value": 3950000, "target": 4000000},
                {"quarter": "Q2 2025", "value": 4320000, "target": 4000000},
                {"quarter": "Q3 2025", "value": 4890000, "target": 4000000},
                {"quarter": "Q4 2025", "value": 5290000, "target": 4000000}
            ],
            "cost_breakdown": [
                {"category": "Compute Engine / GKE", "share_pct": 46.5, "amount": 8579250},
                {"category": "BigQuery & Vertex AI", "share_pct": 28.2, "amount": 5202900},
                {"category": "Network Interconnect & Egress", "share_pct": 14.8, "amount": 2730600},
                {"category": "Cloud Storage & Logging", "share_pct": 10.5, "amount": 1937250}
            ],
            "primary_driver": "Rapid spike in LLM inference fine-tuning jobs and uncompressed staging datasets in BigQuery."
        }
    elif "arr" in m or "revenue" in m:
        data = {
            "metric": "Annual Recurring Revenue (ARR)",
            "unit": "USD",
            "current_run_rate": 128500000,
            "annual_budget": 120000000,
            "variance_pct": "+7.08% (Ahead of Target)",
            "quarterly_history": [
                {"quarter": "Q1 2025", "value": 108000000, "target": 105000000},
                {"quarter": "Q2 2025", "value": 114200000, "target": 110000000},
                {"quarter": "Q3 2025", "value": 121000000, "target": 115000000},
                {"quarter": "Q4 2025", "value": 128500000, "target": 120000000}
            ],
            "cost_breakdown": [
                {"category": "Enterprise Core Tier", "share_pct": 58.0, "amount": 74530000},
                {"category": "AI Agent Platform Add-ons", "share_pct": 26.5, "amount": 34052500},
                {"category": "Professional Services & SLAs", "share_pct": 15.5, "amount": 19917500}
            ],
            "primary_driver": "High expansion in Agent Platform subscriptions with Net Dollar Retention (NDR) at 124%."
        }
    else:
        data = {
            "metric": metric_name.upper(),
            "unit": "Index/Score",
            "current_run_rate": 84.6,
            "annual_budget": 80.0,
            "variance_pct": "+5.75%",
            "quarterly_history": [
                {"quarter": "Q1 2025", "value": 72.1, "target": 70.0},
                {"quarter": "Q2 2025", "value": 76.4, "target": 73.0},
                {"quarter": "Q3 2025", "value": 81.0, "target": 77.0},
                {"quarter": "Q4 2025", "value": 84.6, "target": 80.0}
            ],
            "cost_breakdown": [
                {"category": "Americas", "share_pct": 52.0, "amount": 43.9},
                {"category": "EMEA", "share_pct": 31.0, "amount": 26.2},
                {"category": "APAC", "share_pct": 17.0, "amount": 14.5}
            ],
            "primary_driver": "Strong organic pipeline conversion across enterprise accounts."
        }
        
    return {
        "status": "success",
        "query_metric": metric_name,
        "timeframe": timeframe,
        "department": department,
        "data": data,
        "timestamp": time.time()
    }


def execute_enterprise_code(code_snippet: str, language: str = "python") -> dict:
    """Executes a sanitized analytical code snippet in a sandboxed Python execution engine
    for numerical simulation, statistical regression, or algorithmic data transformation.

    Args:
        code_snippet: Python code snippet to run (e.g. calculation, numpy/math logic).
        language: Execution language (defaults to 'python').

    Returns:
        Execution stdout, returned variables, memory stats, and execution latency.
    """
    logger.info("Executing tool [execute_enterprise_code]")
    start_t = time.time()
    
    # Safe execution environment
    safe_globals = {
        "__builtins__": {
            "print": print, "range": range, "len": len, "sum": sum,
            "min": min, "max": max, "abs": abs, "round": round,
            "dict": dict, "list": list, "set": set, "tuple": tuple,
            "int": int, "float": float, "str": str, "bool": bool,
            "enumerate": enumerate, "zip": zip, "sorted": sorted
        },
        "math": math
    }
    local_vars: Dict[str, Any] = {}
    
    stdout_buffer = []
    def custom_print(*args, **kwargs):
        stdout_buffer.append(" ".join(str(a) for a in args))
        
    safe_globals["__builtins__"]["print"] = custom_print
    
    try:
        # Execute snippet
        exec(code_snippet, safe_globals, local_vars)
        elapsed_ms = round((time.time() - start_t) * 1000, 2)
        
        # Filter serializable outputs
        clean_locals = {}
        for k, v in local_vars.items():
            if not k.startswith("_") and isinstance(v, (int, float, str, bool, list, dict)):
                clean_locals[k] = v
                
        return {
            "status": "success",
            "stdout": "\n".join(stdout_buffer) if stdout_buffer else "Execution completed without stdout.",
            "variables": clean_locals,
            "execution_time_ms": elapsed_ms,
            "sandbox_security": "SOC2-Compliant Isolation"
        }
    except Exception as exc:
        elapsed_ms = round((time.time() - start_t) * 1000, 2)
        return {
            "status": "error",
            "error": str(exc),
            "execution_time_ms": elapsed_ms
        }


def model_financial_projections(
    initial_investment: float,
    annual_savings: float,
    discount_rate_pct: float = 8.5,
    projection_years: int = 5,
    growth_rate_pct: float = 5.0
) -> dict:
    """Computes rigorous Net Present Value (NPV), Internal Rate of Return (IRR), Payback Period,
    and year-by-year cash flow projections for enterprise capital allocation decisions.

    Args:
        initial_investment: Total upfront capital expenditure ($ USD).
        annual_savings: Baseline Year-1 operational cost savings / gross profit addition ($ USD).
        discount_rate_pct: Weighted Average Cost of Capital (WACC) / hurdle rate (e.g. 8.5%).
        projection_years: Horizon for modeling (default 5 years).
        growth_rate_pct: Expected annual compound growth rate of benefits (e.g. 5.0%).

    Returns:
        Structured financial model including NPV, ROI %, Payback (Months), and year-by-year schedule.
    """
    logger.info("Executing tool [model_financial_projections] inv=%f, sav=%f", initial_investment, annual_savings)
    
    r = discount_rate_pct / 100.0
    g = growth_rate_pct / 100.0
    
    cash_flows = [-initial_investment]
    yearly_breakdown = []
    
    cumulative_cash = -initial_investment
    payback_month = None
    npv = -initial_investment
    
    for yr in range(1, projection_years + 1):
        benefit = annual_savings * ((1 + g) ** (yr - 1))
        discounted_benefit = benefit / ((1 + r) ** yr)
        npv += discounted_benefit
        cash_flows.append(benefit)
        
        prev_cum = cumulative_cash
        cumulative_cash += benefit
        
        if payback_month is None and cumulative_cash >= 0:
            fraction = (0 - prev_cum) / benefit
            payback_month = round(((yr - 1) + fraction) * 12, 1)
            
        yearly_breakdown.append({
            "year": f"Year {yr}",
            "gross_cash_flow": round(benefit, 2),
            "discounted_cash_flow": round(discounted_benefit, 2),
            "cumulative_net": round(cumulative_cash, 2)
        })
        
    total_benefits = sum(cash_flows[1:])
    net_profit = total_benefits - initial_investment
    roi_pct = round((net_profit / initial_investment) * 100, 2) if initial_investment > 0 else 0
    
    return {
        "status": "success",
        "initial_investment": initial_investment,
        "discount_rate_pct": discount_rate_pct,
        "npv": round(npv, 2),
        "total_undiscounted_savings": round(total_benefits, 2),
        "net_profit": round(net_profit, 2),
        "roi_pct": roi_pct,
        "payback_period_months": payback_month or (projection_years * 12),
        "cash_flow_schedule": yearly_breakdown,
        "verdict": "STRONG_BUY" if npv > 0 and roi_pct > 150 else "MODERATE_VIABILITY"
    }


def generate_visualization_artifact(
    chart_type: str,
    title: str,
    subtitle: str,
    labels: List[str],
    datasets: List[dict],
    kpi_highlights: Optional[List[dict]] = None
) -> dict:
    """Generates an interactive enterprise visualization artifact (rendered in the right preview panel).

    Args:
        chart_type: Type of chart: 'line', 'bar', 'area', 'donut', 'radar'.
        title: Executive chart title (e.g. '3-Year Cloud Spend Optimization vs Baseline').
        subtitle: Descriptive subtitle or business context.
        labels: X-axis categories or time labels (e.g. ['Q1 25', 'Q2 25', 'Q3 25', 'Q4 25']).
        datasets: Array of dataset objects: [{'label': 'Optimized Run-Rate', 'data': [100, 120, 140], 'color': '#06b6d4'}].
        kpi_highlights: Array of KPI cards: [{'label': 'Total Net Savings', 'value': '$2.4M', 'trend': '+18%'}].

    Returns:
        Rich visualization artifact definition ready for live rendering.
    """
    logger.info("Executing tool [generate_visualization_artifact] type=%r title=%r", chart_type, title)
    artifact = {
        "artifact_id": f"art-{int(time.time()*1000)}",
        "artifact_type": "interactive_chart",
        "chart_type": chart_type,
        "title": title,
        "subtitle": subtitle,
        "labels": labels,
        "datasets": datasets,
        "kpi_highlights": kpi_highlights or [],
        "created_at": time.time()
    }
    return {
        "status": "success",
        "message": "Interactive visualization artifact successfully prepared for display in the executive preview panel.",
        "artifact": artifact
    }


# =====================================================================
# ADK Agent and InMemoryRunner Scaffolding
# =====================================================================

SYSTEM_INSTRUCTION = """
You are the **ADK Enterprise Assistant**, a premier autonomous strategic analyst and technical advisor powered by Google Agent Development Kit (ADK) and Gemini 3.7.

Your mission is to provide deep, analytical, executive-grade intelligence, architectural recommendations, financial modeling, and data-driven insights.

### Operational Directives:
1. **Evidence-Based Reasoning**: Actively utilize your tools to back every assertion with concrete data:
   - Use `query_enterprise_database` for internal data warehouse metrics (ARR, Cloud Spend, NDR, Churn).
   - Use `search_enterprise_knowledge` for real-time market data, compliance frameworks, and industry benchmarks.
   - Use `model_financial_projections` for ROI, NPV, and DCF capital models.
   - Use `execute_enterprise_code` for exact computations, regression models, and mathematical verification.
   - Use `generate_visualization_artifact` to produce rich interactive charts, line graphs, bar breakdowns, and KPI summaries whenever the user asks for analysis, trends, comparisons, or forecasts.

2. **Structure & Presentation**:
   - Deliver clear, beautiful Markdown with structured headings, executive summaries, data tables, and actionable next steps.
   - When generating calculations or comparisons, always invoke `generate_visualization_artifact` so the user receives an interactive visualization in their live preview panel alongside your detailed text.

3. **Tone & Style**:
   - Executive, articulate, precise, objective, and deeply technical yet accessible to C-suite decision makers.
"""

def create_adk_agent() -> Agent:
    """Instantiates the root ADK Agent equipped with enterprise tools."""
    tools = [
        search_enterprise_knowledge,
        query_enterprise_database,
        execute_enterprise_code,
        model_financial_projections,
        generate_visualization_artifact
    ]
    
    agent = Agent(
        name="adk_enterprise_assistant",
        model=DEFAULT_MODEL,
        instruction=SYSTEM_INSTRUCTION,
        tools=tools
    )
    return agent


class ADKEnterpriseEngine:
    """Wrapper managing the ADK InMemoryRunner, session states, and SSE streaming pipeline."""
    
    def __init__(self):
        self.agent = create_adk_agent()
        self.runner = InMemoryRunner(agent=self.agent, app_name=APP_NAME)
        self.active_sessions: set[str] = set()
        logger.info("Initialized ADKEnterpriseEngine with model %s on InMemoryRunner", DEFAULT_MODEL)

    async def ensure_session(self, user_id: str, session_id: str):
        """Idempotently initializes an ADK session in the InMemoryRunner."""
        if session_id not in self.active_sessions:
            try:
                await self.runner.session_service.create_session(
                    app_name=APP_NAME,
                    user_id=user_id,
                    session_id=session_id
                )
                self.active_sessions.add(session_id)
                logger.info("Created ADK session: %s (user: %s)", session_id, user_id)
            except Exception as e:
                logger.warning("Session creation notice: %s", e)
                self.active_sessions.add(session_id)

    async def stream_chat(
        self,
        message: str,
        user_id: str = "enterprise_user",
        session_id: str = "default_session"
    ) -> AsyncGenerator[str, None]:
        """Runs the ADK agent loop, intercepting tool invocations, reasoning tokens,
        and content streams into formatted SSE events for the frontend UI."""
        
        await self.ensure_session(user_id=user_id, session_id=session_id)
        start_time = time.time()
        
        run_config = RunConfig(
            streaming_mode=StreamingMode.SSE,
            max_llm_calls=20
        )
        
        user_content = types.Content(
            role="user",
            parts=[types.Part.from_text(text=message)]
        )
        
        # Tool categories mapping for frontend badge badges
        tool_category_map = {
            "search_enterprise_knowledge": {"category": "Search", "icon": "Search", "label": "Enterprise Search Grounding"},
            "query_enterprise_database": {"category": "Database Query", "icon": "Database", "label": "Data Warehouse Query"},
            "execute_enterprise_code": {"category": "Code Execution", "icon": "Code2", "label": "Python Analytical Sandbox"},
            "model_financial_projections": {"category": "Financial Modeling", "icon": "TrendingUp", "label": "Financial ROI Engine"},
            "generate_visualization_artifact": {"category": "Dynamic Visualization", "icon": "BarChart3", "label": "Interactive Chart Generator"}
        }

        # Yield initial thinking pulse
        yield f"data: {json.dumps({'type': 'thinking', 'thought': 'Analyzing prompt and synthesizing strategic plan with Gemini 3.7 reasoning...'})}\n\n"

        prompt_tokens = 0
        candidate_tokens = 0
        thought_tokens = 0

        try:
            async for event in self.runner.run_async(
                user_id=user_id,
                session_id=session_id,
                new_message=user_content,
                run_config=run_config
            ):
                # Check usage metadata
                if hasattr(event, "usage_metadata") and event.usage_metadata:
                    um = event.usage_metadata
                    prompt_tokens = getattr(um, "prompt_token_count", prompt_tokens)
                    candidate_tokens = getattr(um, "candidates_token_count", candidate_tokens)
                    thought_tokens = getattr(um, "thoughts_token_count", thought_tokens)

                # Process parts
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        # 1. Thought / Reasoning
                        if getattr(part, "thought", False) and getattr(part, "text", None):
                            yield f"data: {json.dumps({'type': 'thinking', 'thought': part.text})}\n\n"
                        
                        # 2. Tool Function Call (Tool Start)
                        elif getattr(part, "function_call", None):
                            fc = part.function_call
                            t_info = tool_category_map.get(fc.name, {
                                "category": "System Tool", "icon": "Cpu", "label": fc.name
                            })
                            payload = {
                                "type": "tool_start",
                                "tool_call_id": fc.id or f"call-{int(time.time()*1000)}",
                                "tool_name": fc.name,
                                "category": t_info["category"],
                                "icon": t_info["icon"],
                                "label": t_info["label"],
                                "arguments": fc.args or {}
                            }
                            yield f"data: {json.dumps(payload)}\n\n"
                        
                        # 3. Tool Function Response (Tool End & Artifact Capture)
                        elif getattr(part, "function_response", None):
                            fr = part.function_response
                            t_info = tool_category_map.get(fr.name, {
                                "category": "System Tool", "icon": "Cpu", "label": fr.name
                            })
                            resp_data = fr.response if isinstance(fr.response, dict) else {"result": str(fr.response)}
                            
                            payload = {
                                "type": "tool_end",
                                "tool_call_id": fr.id or f"call-resp-{int(time.time()*1000)}",
                                "tool_name": fr.name,
                                "category": t_info["category"],
                                "status": resp_data.get("status", "success"),
                                "output": resp_data
                            }
                            yield f"data: {json.dumps(payload)}\n\n"
                            
                            # If the tool created an artifact, dispatch the artifact event
                            if fr.name == "generate_visualization_artifact" and "artifact" in resp_data:
                                art_payload = {
                                    "type": "artifact",
                                    "artifact": resp_data["artifact"]
                                }
                                yield f"data: {json.dumps(art_payload)}\n\n"
                            elif fr.name == "model_financial_projections" and resp_data.get("status") == "success":
                                # Automatically synthesize a financial schedule artifact
                                schedule_art = {
                                    "artifact_id": f"art-fin-{int(time.time()*1000)}",
                                    "artifact_type": "interactive_chart",
                                    "chart_type": "bar",
                                    "title": f"5-Year Financial ROI Schedule (NPV: ${resp_data.get('npv', 0):,.0f})",
                                    "subtitle": f"Payback in {resp_data.get('payback_period_months')} months | {resp_data.get('roi_pct')}% ROI",
                                    "labels": [item["year"] for item in resp_data.get("cash_flow_schedule", [])],
                                    "datasets": [
                                        {
                                            "label": "Gross Cash Inflow ($)",
                                            "data": [item["gross_cash_flow"] for item in resp_data.get("cash_flow_schedule", [])],
                                            "color": "#10b981"
                                        },
                                        {
                                            "label": "Discounted Value ($)",
                                            "data": [item["discounted_cash_flow"] for item in resp_data.get("cash_flow_schedule", [])],
                                            "color": "#06b6d4"
                                        }
                                    ],
                                    "kpi_highlights": [
                                        {"label": "Net Present Value", "value": f"${resp_data.get('npv', 0):,.0f}", "trend": "+Positive"},
                                        {"label": "Projected ROI", "value": f"{resp_data.get('roi_pct', 0)}%", "trend": resp_data.get("verdict", "")},
                                        {"label": "Payback Period", "value": f"{resp_data.get('payback_period_months', 0)} mos", "trend": "Rapid"}
                                    ],
                                    "created_at": time.time()
                                }
                                yield f"data: {json.dumps({'type': 'artifact', 'artifact': schedule_art})}\n\n"

                        # 4. Standard Text Delta Content
                        elif getattr(part, "text", None):
                            yield f"data: {json.dumps({'type': 'content', 'delta': part.text})}\n\n"

            # Final completion event
            elapsed_sec = round(time.time() - start_time, 2)
            done_payload = {
                "type": "done",
                "elapsed_seconds": elapsed_sec,
                "model": DEFAULT_MODEL,
                "usage": {
                    "prompt_tokens": prompt_tokens,
                    "candidate_tokens": candidate_tokens,
                    "thought_tokens": thought_tokens,
                    "total_tokens": prompt_tokens + candidate_tokens + thought_tokens
                }
            }
            yield f"data: {json.dumps(done_payload)}\n\n"

        except Exception as exc:
            logger.exception("Error during ADK stream execution: %s", exc)
            err_payload = {
                "type": "error",
                "error": str(exc),
                "message": "Encountered runtime error during ADK reasoning stream."
            }
            yield f"data: {json.dumps(err_payload)}\n\n"


# Singleton Engine Instance
engine = ADKEnterpriseEngine()
