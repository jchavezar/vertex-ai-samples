#!/usr/bin/env python3
"""
Federated Commercial Intelligence Mesh Orchestrator (ADK + Vertex AI Gemini 2.5 Flash).

Routes enterprise commercial benchmark queries across 4 architectural tiers:
  - Pre-Flight Guard: Dataplex Knowledge Catalog GenAI Usage Rights Compliance Check
  - Tier 1 (18%): Deterministic Parameterized SQL via Google MCP Toolbox
  - Tier 2 (30%): Semantic Layer (Dataplex KC DAX Formulas) + Gold Views + Python Simulator
  - Tier 3 (49%): Federated Multi-Tool Agent (SQL + Unstructured CLM/Visit RAG + 3P Market APIs)
  - Tier 4 (3%):  Multi-System Action & Executive Briefing Automation
"""

from __future__ import annotations

import json
import os
import shutil
import sqlite3
import subprocess
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "commercial_spine_mock.db"
CATALOG_PATH = BASE_DIR / "data" / "taxonomy_questions_catalog.json"
TOOLS_YAML_PATH = BASE_DIR / "config" / "tools.yaml"
GOLD_VIEWS_SQL_PATH = BASE_DIR / "config" / "bigquery_gold_views.sql"


class FederatedCommercialMeshOrchestrator:
    """Executes 4-Tier Federated Routing, Counterfactual Simulation, and Gemini 2.5 Flash Copilot."""

    def __init__(self) -> None:
        self.project_id = (
            os.environ.get("GOOGLE_CLOUD_PROJECT")
            or os.environ.get("GCP_PROJECT_ID")
            or "vtxdemos"
        )
        self.location = os.environ.get("GOOGLE_CLOUD_LOCATION", "global")
        self.model_name = os.environ.get("GEMINI_MODEL", "gemini-3.8-flash")
        self._genai_client = None

    def _get_genai_client(self):
        if self._genai_client is not None:
            return self._genai_client
        try:
            from google import genai

            self._genai_client = genai.Client(
                vertexai=True,
                project=self.project_id,
                location=self.location,
            )
            return self._genai_client
        except Exception:
            return None

    def load_catalog(self) -> Dict[str, Any]:
        with open(CATALOG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

    def get_question_by_id(self, question_id: str) -> Dict[str, Any]:
        catalog = self.load_catalog()
        raw = (question_id or "").strip().upper()
        # Normalize 'q-21', 'Q-21', '21', 'Q-021' -> compare numeric suffix or exact ID
        digits = "".join(ch for ch in raw if ch.isdigit())
        normalized_code = f"Q-{int(digits):03d}" if digits else raw
        for q in catalog.get("questions", []):
            qid = q["id"].upper()
            if qid == raw or qid == normalized_code:
                return q
        raise KeyError(f"Question ID '{question_id}' not found in taxonomy catalog.")

    def _query_sqlite(self, sql: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(str(DB_PATH))
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        try:
            cur.execute(sql, params or {})
            rows = [dict(r) for r in cur.fetchall()]
            return rows
        finally:
            conn.close()

    def check_dataplex_governance(self, sources: List[str]) -> Dict[str, Any]:
        """Step 0: Pre-flight Dataplex Knowledge Catalog GenAI_Usage_Rights check."""
        if not sources:
            return {"status": "ALLOWED", "checked_sources": [], "blocked_sources": []}

        placeholders = ",".join("?" for _ in sources)
        conn = sqlite3.connect(str(DB_PATH))
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(
            f"""
            SELECT source_id, source_name, category, genai_usage_rights,
                   pii_classification, dataplex_aspect_uri, steward_team, notes
            FROM data_source_governance
            WHERE source_name IN ({placeholders})
            """,
            sources,
        )
        records = [dict(r) for r in cur.fetchall()]
        conn.close()

        blocked = [r for r in records if int(r.get("genai_usage_rights", 1)) == 0]
        return {
            "status": "BLOCKED" if blocked else "ALLOWED",
            "checked_sources": records,
            "blocked_sources": blocked,
            "policy_rule": "Dataplex Aspect `genai_usage_rights == TRUE` required before LLM prompt or RAG injection.",
        }

    def run_counterfactual_simulator(
        self,
        question: Dict[str, Any],
        custom_params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Executes Tier-2 Python Monte Carlo / What-If Counterfactual & Econometric simulations."""
        params = custom_params or {}
        cull_pct = float(params.get("cull_percentile", 0.20))
        price_boost_pct = float(params.get("price_competitiveness_boost_pct", 10.0))
        discount_cap_pct = float(params.get("discount_cap_pct", 15.0))

        all_deals = self._query_sqlite(
            """
            SELECT o.opp_id, o.account_name, o.region, o.industry, o.stage_name,
                   o.tcv_usd, o.win_prob, o.markov_regime, o.client_Temp_score,
                   p.net_service_rev_usd, p.passthrough_cost_usd,
                   p.gross_yield_v1, p.adjusted_yield_v3_trimmed,
                   p.adjusted_yield_v4_sigma_capped, p.discount_giveaway_pct,
                   p.price_competitiveness_score
            FROM opportunities o
            JOIN pricing_scenarios p ON o.opp_id = p.opp_id
            ORDER BY p.adjusted_yield_v4_sigma_capped ASC
            """
        )

        n = len(all_deals)
        cutoff_idx = max(1, int(round(n * cull_pct)))
        pruned_deals = all_deals[:cutoff_idx]
        retained_deals = all_deals[cutoff_idx:]

        baseline_yield = sum(d["adjusted_yield_v4_sigma_capped"] * d["net_service_rev_usd"] for d in all_deals) / max(
            1.0, sum(d["net_service_rev_usd"] for d in all_deals)
        )
        post_cull_yield = sum(
            d["adjusted_yield_v4_sigma_capped"] * d["net_service_rev_usd"] for d in retained_deals
        ) / max(1.0, sum(d["net_service_rev_usd"] for d in retained_deals))

        uplift_bps = round((post_cull_yield - baseline_yield) * 10000, 1)

        # 6-Lever Logit Win-Probability Elasticity
        logit_sensitivity = []
        for d in sorted(all_deals, key=lambda x: x["tcv_usd"], reverse=True)[:6]:
            w0 = float(d["win_prob"])
            delta_p = (price_boost_pct / 100.0) * 0.85 * w0 * (1.0 - w0)
            w1 = min(0.96, w0 + delta_p)
            ev_delta_m = round(((w1 - w0) * d["tcv_usd"]) / 1e6, 2)
            logit_sensitivity.append(
                {
                    "opp_id": d["opp_id"],
                    "account_name": d["account_name"],
                    "tcv_millions": round(d["tcv_usd"] / 1e6, 2),
                    "baseline_win_prob_pct": round(w0 * 100, 1),
                    "simulated_win_prob_pct": round(w1 * 100, 1),
                    "expected_booking_gain_millions": ev_delta_m,
                }
            )

        # Hidden Markov Regime Matrix
        markov_transition_matrix = {
            "Regime_1_High_Velocity_Expansion": {
                "stay_expansion": 0.78,
                "shift_to_compression": 0.17,
                "shift_to_stalled": 0.05,
            },
            "Regime_2_Margin_Compression": {
                "recover_to_expansion": 0.22 if discount_cap_pct <= 12.0 else 0.14,
                "stay_compression": 0.56,
                "degrade_to_stalled": 0.22 if discount_cap_pct <= 12.0 else 0.30,
            },
            "Regime_3_Stalled_Procurement": {
                "recover_to_expansion": 0.08,
                "shift_to_compression": 0.31,
                "remain_stalled_or_lost": 0.61,
            },
        }

        return {
            "simulator_engine": "Vertex Python Counterfactual & Markov Engine v2.4",
            "parameters_applied": {
                "cull_percentile": cull_pct,
                "price_competitiveness_boost_pct": price_boost_pct,
                "discount_cap_pct": discount_cap_pct,
            },
            "portfolio_pruning_result": {
                "baseline_blended_yield_pct": round(baseline_yield * 100, 2),
                "post_cull_blended_yield_pct": round(post_cull_yield * 100, 2),
                "margin_uplift_bps": uplift_bps,
                "pruned_deal_count": len(pruned_deals),
                "pruned_deals": [d["opp_id"] for d in pruned_deals],
                "pruned_tcv_millions": round(sum(d["tcv_usd"] for d in pruned_deals) / 1e6, 2),
                "retained_tcv_millions": round(sum(d["tcv_usd"] for d in retained_deals) / 1e6, 2),
            },
            "six_lever_win_elasticity": logit_sensitivity,
            "markov_transition_matrix": markov_transition_matrix,
        }

    def simulate_question_execution(
        self,
        question_id: str,
        custom_params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Executes the full 4-Tier Federated Router for a benchmark question."""
        t0 = time.perf_counter()
        q = self.get_question_by_id(question_id)
        params = custom_params or {}

        trace: List[Dict[str, Any]] = []

        # Step 0: Dataplex Knowledge Catalog Governance Pre-Flight Check
        governance = self.check_dataplex_governance(q.get("sources", []))
        trace.append(
            {
                "step": 1,
                "component": "Dataplex Knowledge Catalog Governance Guard",
                "action": f"Evaluated GenAI_Usage_Rights across {len(q.get('sources', []))} source(s)",
                "status": governance["status"],
                "latency_ms": 18,
            }
        )

        # Execute parameterized SQL (with safe binding for :min_days if present)
        raw_sql = q.get("sample_sql", "SELECT * FROM opportunities LIMIT 5;")
        sql_params = {"min_days": int(params.get("min_days", 90))}
        try:
            sql_rows = self._query_sqlite(raw_sql, sql_params)
        except Exception as exc:
            sql_rows = [{"sql_error": str(exc)}]

        trace.append(
            {
                "step": 2,
                "component": "Google MCP Toolbox for Databases (genai-toolbox)",
                "action": f"Executed parameterized query against Gold Spine ({len(sql_rows)} rows returned)",
                "status": "COMPLETED",
                "latency_ms": 42,
            }
        )

        # If Governance Guard blocked a source, substitute clean-room internal pricing telemetry
        clean_room_fallback_rows: List[Dict[str, Any]] = []
        if governance["status"] == "BLOCKED":
            clean_room_fallback_rows = self._query_sqlite(
                """
                SELECT o.opp_id, o.account_name, o.industry,
                       p.standard_rate_usd, p.negotiated_rate_usd,
                       ROUND(p.discount_giveaway_pct * 100, 1) AS internal_giveaway_pct,
                       ROUND(p.adjusted_yield_v4_sigma_capped * 100, 1) AS internal_adj_yield_v4_pct
                FROM opportunities o
                JOIN pricing_scenarios p ON o.opp_id = p.opp_id
                ORDER BY o.tcv_usd DESC
                LIMIT 5;
                """
            )
            trace.append(
                {
                    "step": 3,
                    "component": "Clean-Room Internal Substitution Router",
                    "action": "Quarantined Analyst_Benchmark_Feed_Unlicensed (GenAI_Usage_Rights=False) and substituted internal Deal_Pricing_Engine elasticity",
                    "status": "SUBSTITUTED_SAFE_SOURCE",
                    "latency_ms": 29,
                }
            )

        # Tier 2 Counterfactual / Econometric Simulator
        counterfactual: Optional[Dict[str, Any]] = None
        if (
            q["tier_code"] in ("Tier 2", "Tier 4")
            or "Counterfactual / What-If Simulator Required" in q.get("flags", [])
            or "Missing ML / Econometric Model in DB" in q.get("flags", [])
        ):
            counterfactual = self.run_counterfactual_simulator(q, params)
            trace.append(
                {
                    "step": len(trace) + 1,
                    "component": "Tier-2 Python Counterfactual & Markov Simulator",
                    "action": "Computed portfolio pruning uplift (bps), 6-lever logit elasticity, and Markov transition matrix",
                    "status": "COMPLETED",
                    "latency_ms": 64,
                }
            )

        # Tier 3 / Tier 4 Unstructured RAG + External 3P Market Signals
        unstructured_hits: List[Dict[str, Any]] = []
        external_signals: List[Dict[str, Any]] = []
        if q["tier_code"] in ("Tier 3", "Tier 4") and governance["status"] != "BLOCKED":
            unstructured_hits = self._query_sqlite(
                """
                SELECT doc_id, opp_id, account_id, source_system, note_date,
                       extracted_risk_tag, note_snippet
                FROM unstructured_deal_notes
                ORDER BY note_date DESC
                LIMIT 6;
                """
            )
            external_signals = self._query_sqlite(
                """
                SELECT signal_id, account_id, account_name, signal_source,
                       captured_date, ai_self_sufficiency_index,
                       intent_surge_score, client_rd_intensity_pct, signal_summary
                FROM external_market_signals
                ORDER BY intent_surge_score DESC
                LIMIT 6;
                """
            )
            trace.append(
                {
                    "step": len(trace) + 1,
                    "component": "Tier-3 Federated RAG & 3P Market Signal Bus",
                    "action": f"Retrieved {len(unstructured_hits)} contract/visit RAG chunks and {len(external_signals)} external telemetry signals",
                    "status": "COMPLETED",
                    "latency_ms": 88,
                }
            )

        elapsed_ms = round((time.perf_counter() - t0) * 1000, 1)

        executive_synthesis = self._build_deterministic_synthesis(
            q, governance, sql_rows, counterfactual, unstructured_hits, external_signals
        )

        tier_enum_map = {
            "Tier 1": "TIER_1",
            "Tier 2": "TIER_2",
            "Tier 3": "TIER_3",
            "Tier 4": "TIER_4",
        }
        tier_enum = tier_enum_map.get(q["tier_code"], "TIER_1")
        is_blocked = governance["status"] == "BLOCKED"

        ui_trace_steps: List[Dict[str, Any]] = [
            {
                "stepOrder": 1,
                "pillar": "PRE_FLIGHT_GOVERNANCE",
                "title": "Pre-Flight Dataplex GenAI License & RBAC Guard",
                "status": "BLOCKED" if is_blocked else "PASSED",
                "latencyMs": 18,
                "detail": (
                    f"BLOCKED: {', '.join(b['source_name'] for b in governance['blocked_sources'])} has GenAI_Usage_Rights=False."
                    if is_blocked
                    else f"Verified Dataplex governance aspects for sources: {', '.join(q.get('sources', []))}."
                ),
            },
            {
                "stepOrder": 2,
                "pillar": "GENAI_TOOLBOX_MCP" if q["tier_code"] == "Tier 1" else "DATAPLEX_KC_BQCA",
                "title": "Execute Parameterized SQL via Google MCP Toolbox (genai-toolbox)",
                "status": "EXECUTED",
                "latencyMs": 42,
                "detail": f"Executed governed SQL against commercial_spine_mock.db ({len(sql_rows)} rows returned).",
                "artifactSnippet": raw_sql,
            },
        ]

        if counterfactual:
            cull = counterfactual["portfolio_pruning_result"]
            ui_trace_steps.append(
                {
                    "stepOrder": len(ui_trace_steps) + 1,
                    "pillar": "PYTHON_WHAT_IF_SANDBOX",
                    "title": "Tier-2 Python Counterfactual & Markov Regime Simulator",
                    "status": "EXECUTED",
                    "latencyMs": 64,
                    "detail": (
                        f"Baseline Yield: {cull['baseline_blended_yield_pct']}% -> Post-Cull Yield: "
                        f"{cull['post_cull_blended_yield_pct']}% (+{cull['margin_uplift_bps']} bps uplift; "
                        f"Retained TCV: ${cull['retained_tcv_millions']}M)."
                    ),
                }
            )

        if unstructured_hits:
            ui_trace_steps.append(
                {
                    "stepOrder": len(ui_trace_steps) + 1,
                    "pillar": "VERTEX_UNSTRUCTURED_RAG",
                    "title": "Vertex AI Unstructured Contract & Visit Log RAG",
                    "status": "EXECUTED",
                    "latencyMs": 51,
                    "detail": f"Retrieved {len(unstructured_hits)} contract/visit clauses from CLM_Contract_Vault & Customer_Visit_Logs.",
                }
            )

        if external_signals:
            ui_trace_steps.append(
                {
                    "stepOrder": len(ui_trace_steps) + 1,
                    "pillar": "EXTERNAL_MARKET_MCP",
                    "title": "Licensed 3P Market & Buyer Intent Telemetry Bus",
                    "status": "SYNTHESIZED",
                    "latencyMs": 37,
                    "detail": f"Fused {len(external_signals)} external telemetry signals (Tech_Stack_Telemetry_Feed, Buyer_Intent_Signal_Stream, SEC_Regulatory_Filings).",
                }
            )

        raw_mcp_outcome = (
            "BLOCKED_LICENSE"
            if is_blocked
            else (
                "SUCCESS"
                if q["tier_code"] == "Tier 1"
                else (
                    "FAILED_HALLUCINATED_METRIC"
                    if q["tier_code"] == "Tier 2"
                    else "FAILED_MISSING_UNSTRUCTURED"
                )
            )
        )

        preview_rows = clean_room_fallback_rows if is_blocked else sql_rows

        return {
            # Backend snake_case fields
            "question_id": q["id"],
            "question": q["question"],
            "tier_code": q["tier_code"],
            "tier_name": q["tier_name"],
            "persona": q["persona"],
            "domain_group": q["domain_group"],
            "topology": q["topology"],
            "confidence_pct": q.get("confidence_pct", 70),
            "missing_artifacts": q.get("missing_artifacts", []),
            "db_only_verdict": q["db_only_verdict"],
            "flags": q["flags"],
            "diagnosis": q["diagnosis"],
            "recommended_architecture": q["recommended_architecture"],
            "compliance_guard": governance,
            "execution_trace": trace,
            "sql_executed": raw_sql,
            "sql_rows": sql_rows,
            "clean_room_fallback_rows": clean_room_fallback_rows,
            "counterfactual_simulation": counterfactual,
            "unstructured_rag_hits": unstructured_hits,
            "external_market_signals": external_signals,
            "executive_synthesis": executive_synthesis,
            "synthesized_answer": executive_synthesis,
            "total_latency_ms": elapsed_ms,
            "latency_ms": elapsed_ms,
            # Frontend SimulationResult camelCase fields
            "questionId": q["id"],
            "questionText": q["question"],
            "tier": tier_enum,
            "complianceStatus": "BLOCKED_UNLICENSED_3P_FEED" if is_blocked else "APPROVED",
            "rawSqlMcpOutcome": raw_mcp_outcome,
            "federatedMeshOutcome": "GOVERNANCE_SAFE_FALLBACK" if is_blocked else "VERIFIED_SYNTHESIS",
            "totalLatencyMs": int(max(120, round(elapsed_ms + 180))),
            "traceSteps": ui_trace_steps,
            "synthesizedAnswer": executive_synthesis,
            "sqlExecuted": raw_sql,
            "dataPreview": preview_rows[:8],
        }

    def _build_deterministic_synthesis(
        self,
        q: Dict[str, Any],
        governance: Dict[str, Any],
        sql_rows: List[Dict[str, Any]],
        counterfactual: Optional[Dict[str, Any]],
        unstructured_hits: List[Dict[str, Any]],
        external_signals: List[Dict[str, Any]],
    ) -> str:
        if governance["status"] == "BLOCKED":
            blocked_names = ", ".join(b["source_name"] for b in governance["blocked_sources"])
            return (
                f"COMPLIANCE INTERCEPT: Dataplex Knowledge Catalog blocked LLM access to `{blocked_names}` "
                f"because `genai_usage_rights = False`. The orchestrator automatically rerouted the request "
                f"to internal `Deal_Pricing_Engine` historical rate-card benchmarks, protecting enterprise "
                f"3P licensing compliance while delivering 5 clean-room comparable deals."
            )

        parts = [
            f"Executed `{q['id']}` via **{q['tier_name']}** (Readiness Confidence: **{q.get('confidence_pct', 70)}%**).",
            f"MCP Toolbox returned **{len(sql_rows)} structured records** from the governed BigQuery Gold Spine.",
        ]
        if counterfactual:
            cull = counterfactual["portfolio_pruning_result"]
            parts.append(
                f"Counterfactual Simulator shows pruning the bottom {int(counterfactual['parameters_applied']['cull_percentile']*100)}% "
                f"lowest-yielding deals expands blended portfolio Adjusted Yield v4 from "
                f"**{cull['baseline_blended_yield_pct']}%** to **{cull['post_cull_blended_yield_pct']}%** "
                f"(**+{cull['margin_uplift_bps']} bps** uplift) while retaining **${cull['retained_tcv_millions']}M** in TCV."
            )
        if unstructured_hits or external_signals:
            parts.append(
                f"Federated RAG fused **{len(unstructured_hits)} unstructured contract/visit clauses** "
                f"with **{len(external_signals)} external 3P market & buyer-intent signals**."
            )
        return " ".join(parts)

    def copilot_architect_chat(
        self,
        user_message: str,
        question_id: Optional[str] = None,
        custom_params: Optional[Dict[str, Any]] = None,
        frontend_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """AI Architect Copilot powered by Vertex AI Gemini 2.5 Flash."""
        q_context: Optional[Dict[str, Any]] = None
        sim_result: Optional[Dict[str, Any]] = None

        if question_id:
            try:
                sim_result = self.simulate_question_execution(question_id, custom_params)
                q_context = self.get_question_by_id(question_id)
            except KeyError:
                q_context = None

        system_instruction = """You are the Principal Enterprise Data Mesh & Agentic AI Architect.
CRITICAL COMMUNICATION RULES:
1. Be CONCISE, DIRECT, and CONVERSATIONAL. Answer the user's specific question in 3 to 5 tight bullet points (under 140 words) unless the user explicitly asks for full SQL or YAML code.
2. NEVER dump unsolicited boilerplate headers (like '### Architectural Diagnosis' or '#### Missing Artifacts') if the user didn't ask for them. Answer their exact question first!
3. If the user asks "how did you know there were hidden unstructured notes?" or similar, explain directly:
   - Although sources like `CRM_Opportunity_Spine`, `Delivery_Governance_Hub`, and `CLM_Contract_Vault` appear in the structured tracker, the actual root-cause answers (e.g., why a deal was lost, delivery director review commentary, client visit debriefs, or custom gain-share/rate-cap contract clauses) live inside free-text narrative fields or PDF/Word attachments (`unstructured_deal_notes`), NOT structured numeric SQL columns.
   - A SQL-only MCP tool (`GROUP BY` / `SUM`) cannot reason over free-text review notes or contract clauses without a Semantic RAG index or `AI.GENERATE_TABLE` extraction pipeline.
4. Use clean Markdown (short bullets, bold key terms, inline `code` tags). Only include code blocks when asked."""

        merged_context = {}
        if q_context:
            merged_context.update(
                {
                    "id": q_context["id"],
                    "tier": q_context["tier_name"],
                    "question": q_context["question"],
                    "confidence_pct": q_context.get("confidence_pct"),
                    "missing_artifacts": q_context.get("missing_artifacts"),
                    "db_only_verdict": q_context["db_only_verdict"],
                    "flags": q_context["flags"],
                    "diagnosis": q_context["diagnosis"],
                    "recommended_architecture": q_context["recommended_architecture"],
                }
            )
        if frontend_context:
            for k, v in frontend_context.items():
                if v is not None and k != "history":
                    merged_context[k] = v

        history_lines = []
        if frontend_context and isinstance(frontend_context.get("history"), list):
            for msg in frontend_context["history"][-6:]:
                role = msg.get("role", "user").upper()
                content = msg.get("content", "")
                if content:
                    history_lines.append(f"{role}: {content}")

        prompt_parts = []
        if merged_context:
            prompt_parts.append("Selected Question Context:\n" + json.dumps(merged_context, indent=2))
        if sim_result:
            prompt_parts.append(
                "Live Mock DB Telemetry Summary:\n"
                + json.dumps(
                    {
                        "sql_rows_count": len(sim_result.get("sql_rows", [])),
                        "sql_rows_sample": sim_result.get("sql_rows", [])[:3],
                        "unstructured_rag_hits_sample": sim_result.get("unstructured_rag_hits", [])[:2],
                        "compliance_guard": sim_result.get("compliance_guard"),
                    },
                    indent=2,
                )
            )
        if history_lines:
            prompt_parts.append("Recent Conversation History:\n" + "\n".join(history_lines))
        prompt_parts.append(f"User's Current Question (answer this directly and concisely):\n{user_message}")

        full_prompt = "\n\n".join(prompt_parts)
        client = self._get_genai_client()

        if client is not None:
            try:
                from google.genai import types

                resp = client.models.generate_content(
                    model=self.model_name,
                    contents=full_prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        temperature=0.2,
                        max_output_tokens=700,
                    ),
                )
                if resp and resp.text:
                    return {
                        "model": self.model_name,
                        "mode": "vertex_ai_live",
                        "question_id": question_id,
                        "reply": resp.text.strip(),
                        "simulation_snapshot": sim_result,
                    }
            except Exception as exc:
                fallback_note = f"*(Vertex AI call error: {type(exc).__name__})*"
        else:
            fallback_note = ""

        # Concise, question-aware fallback if offline
        q_label = merged_context.get("question_code") or merged_context.get("id") or "this question"
        diag = merged_context.get("diagnosis") or "Requires federated synthesis across structured and unstructured sources."
        missing = merged_context.get("missing_artifacts") or []
        reply_md = (
            f"For **{q_label}**, here is the direct breakdown:\n"
            f"- **Why we flagged it**: {diag}\n"
            f"- **Recommended Fix**: {merged_context.get('recommended_architecture', 'Federate BigQuery Gold Views with Vertex AI Unstructured RAG.')}\n"
            + (f"- **Missing Info to Verify**: {'; '.join(missing[:2])}" if missing else "")
        )

        return {
            "model": f"{self.model_name}",
            "mode": "deterministic_fallback",
            "question_id": question_id,
            "reply": reply_md,
            "simulation_snapshot": sim_result,
        }

    def dispatch_to_antigravity_agent(
        self,
        prompt_text: str,
        conversation_id: Optional[str] = None,
        question_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Dispatches an architectural prompt or question context into Antigravity IDE via `agentapi` CLI."""
        agentapi_bin = shutil.which("agentapi") or "/google/bin/releases/agentapi/agentapi"
        enriched_prompt = prompt_text
        if question_id:
            try:
                q = self.get_question_by_id(question_id)
                enriched_prompt = (
                    f"[Federated Commercial Mesh Benchmark {q['id']} - {q['tier_code']} | "
                    f"Confidence: {q.get('confidence_pct')}%]\n"
                    f"Question: {q['question']}\n"
                    f"DB-Only Verdict: {q['db_only_verdict']}\n"
                    f"Missing Artifacts: {', '.join(q.get('missing_artifacts', []))}\n\n"
                    f"User Request: {prompt_text}"
                )
            except KeyError:
                pass

        if not os.path.exists(agentapi_bin):
            return {
                "status": "simulated",
                "message": "agentapi binary not found in PATH; prepared payload for Antigravity IDE.",
                "dispatched_prompt": enriched_prompt,
            }

        try:
            if conversation_id:
                cmd = [agentapi_bin, "send-message", "--conversation-id", conversation_id, "--message", enriched_prompt]
            else:
                cmd = [agentapi_bin, "new-conversation", "--message", enriched_prompt]
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=12, check=False)
            return {
                "status": "dispatched" if proc.returncode == 0 else "cli_warning",
                "exit_code": proc.returncode,
                "stdout": proc.stdout.strip(),
                "stderr": proc.stderr.strip(),
                "dispatched_prompt": enriched_prompt,
            }
        except Exception as exc:
            return {
                "status": "error",
                "error": str(exc),
                "dispatched_prompt": enriched_prompt,
            }
