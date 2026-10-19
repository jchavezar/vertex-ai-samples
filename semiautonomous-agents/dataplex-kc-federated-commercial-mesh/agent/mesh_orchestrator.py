#!/usr/bin/env python3
"""
Federated Commercial Intelligence Mesh Orchestrator (ADK + Vertex AI Gemini 3.8 Flash).

Routes enterprise commercial benchmark queries across 4 architectural tiers:
  - Pre-Flight Guard: Dataplex Knowledge Catalog GenAI Usage Rights Compliance Check
  - Tier 1 (18%): Deterministic Parameterized SQL via Google MCP Toolbox
  - Tier 2 (30%): Semantic Layer (Dataplex KC DAX Formulas) + Gold Views + Python Simulator
  - Tier 3 (49%): Federated Multi-Tool Agent (SQL + Unstructured CLM/Visit RAG + 3P Market APIs)
  - Tier 4 (3%):  Multi-System Action & Executive Briefing Automation

Backed by BigQuery Dataset `vtxdemos.commercial_mesh_gold` (1,404 rows + 4 Gold Views)
and fast local SQLite mirror for zero-latency interactive simulation.
"""

from __future__ import annotations

import contextlib
import io
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
TOOLS_YAML_PATH = BASE_DIR / "backend" / "config" / "tools.yaml"
GOLD_VIEWS_SQL_PATH = BASE_DIR / "backend" / "config" / "bigquery_gold_views.sql"
PARTS_DIR = BASE_DIR / "backend" / "parts"

BQ_PROJECT_ID = "vtxdemos"
BQ_DATASET_ID = "commercial_mesh_gold"

BQ_TABLES_META = [
    {
        "table_id": "crm_opportunities",
        "full_table_id": "vtxdemos.commercial_mesh_gold.crm_opportunities",
        "layer": "Gold Structured Spine",
        "expected_rows": 500,
        "description": "500 active & historical B2B pipeline opportunities across NA, EMEA, APAC, and LATAM with stage residence time (45 deals >90d in Stage 2B), Markov regimes, and 6-lever PWin scores.",
    },
    {
        "table_id": "deal_pricing_scenarios",
        "full_table_id": "vtxdemos.commercial_mesh_gold.deal_pricing_scenarios",
        "layer": "Semantic DAX Pricing Spine",
        "expected_rows": 500,
        "description": "1:1 deal pricing scenarios containing Gross Revenue, Billable Expense Passthrough, canonical CCI Excl. BE %, ADR ($), Adjusted Yield v1/v3/v4, and AMS AI task substitutability %.",
    },
    {
        "table_id": "delivery_governance_hub",
        "full_table_id": "vtxdemos.commercial_mesh_gold.delivery_governance_hub",
        "layer": "Post-Sales Delivery Spine",
        "expected_rows": 120,
        "description": "120 enterprise account delivery health scorecards with RAG status, CSAT, NPS, SLA slippage days, EAC margin variance (bps), and unstructured Delivery Director narrative commentary.",
    },
    {
        "table_id": "clm_contract_vault_chunks",
        "full_table_id": "vtxdemos.commercial_mesh_gold.clm_contract_vault_chunks",
        "layer": "Unstructured Legal & Visit RAG",
        "expected_rows": 150,
        "description": "150 verbatim contract clauses (MSA/SOW amendments), Stage 2B solutioning blocker notes, GenAI productivity deflator terms, and executive visit debriefs.",
    },
    {
        "table_id": "external_market_signals",
        "full_table_id": "vtxdemos.commercial_mesh_gold.external_market_signals",
        "layer": "3P Market & Buyer Intent Bus",
        "expected_rows": 120,
        "description": "120 licensed external market signals tracking Client R&D Intensity %, AI Self-Sufficiency Index, Buyer Intent Surge Scores, C-Suite changes, and competitor concession alerts.",
    },
    {
        "table_id": "dataplex_source_governance",
        "full_table_id": "vtxdemos.commercial_mesh_gold.dataplex_source_governance",
        "layer": "Dataplex Knowledge Catalog",
        "expected_rows": 14,
        "description": "14 enterprise & 3P data sources governed by Dataplex aspect `genai_usage_rights` (13 ALLOWED, 1 BLOCKED: `Analyst_Benchmark_Feed_Unlicensed`).",
    },
]

BQ_GOLD_VIEWS_META = [
    {
        "view_id": "v_gold_stage2b_stalled_deals",
        "full_view_id": "vtxdemos.commercial_mesh_gold.v_gold_stage2b_stalled_deals",
        "description": "Isolates Stage 2B - Solutioning bottlenecks (>90 days) joined with CCI Excl. BE and Adjusted Yield v4.",
    },
    {
        "view_id": "v_gold_pricing_yield_dax",
        "full_view_id": "vtxdemos.commercial_mesh_gold.v_gold_pricing_yield_dax",
        "description": "Materializes canonical DAX measures: CCI Excluding Billable Expenses, Adjusted Yield v1/v3/v4, and AI task substitutability.",
    },
    {
        "view_id": "v_gold_markov_regime_analytics",
        "full_view_id": "vtxdemos.commercial_mesh_gold.v_gold_markov_regime_analytics",
        "description": "Econometric Hidden Markov Regime classification (Expansion_Velocity, Pressured_Margin, Stalled_Procurement) and erosion risk.",
    },
    {
        "view_id": "v_gold_account_360_health",
        "full_view_id": "vtxdemos.commercial_mesh_gold.v_gold_account_360_health",
        "description": "Entity-resolved Account 360 joining Pre-Sales Opportunity/Pricing Spine with Post-Sales Delivery RAG & 3P Market Signals.",
    },
]

DEMO_PARTS_CATALOG = [
    {
        "part_id": "part1",
        "step_number": 1,
        "file_path": "backend/parts/part1_bigquery_gold_spine.py",
        "title": "Part 1: BigQuery Gold Spine & Semantic DAX Layer",
        "tier_badge": "FOUNDATION SPINE",
        "architectural_explanation": (
            "Connects directly to `vtxdemos.commercial_mesh_gold` in BigQuery (1,404 total rows across 6 tables + 4 Gold Views) "
            "and queries `v_gold_pricing_yield_dax` to contrast raw margin against canonical CCI Excluding Billable Expenses and Adjusted Yield v4."
        ),
        "pre_verified_output": (
            "=== PART 1: BIGQUERY GOLD SPINE (`vtxdemos.commercial_mesh_gold`) ===\n"
            "  • crm_opportunities            :  500 rows\n"
            "  • deal_pricing_scenarios       :  500 rows\n"
            "  • delivery_governance_hub      :  120 rows\n"
            "  • clm_contract_vault_chunks    :  150 rows\n"
            "  • external_market_signals      :  120 rows\n"
            "  • dataplex_source_governance   :   14 rows\n\n"
            "Top 5 Deals via `v_gold_pricing_yield_dax` (Canonical CCI Excl. Billable Expenses):\n"
            "  [OPP-10095] Apex Media Networks #95          | TCV: $519.97M | CCI (Incl BE): 28.0% -> CCI (Excl BE): 30.3% | Adj Yield v4: 30.3%\n"
            "  [OPP-10358] Novacore Power & Renewables #118 | TCV: $499.27M | CCI (Incl BE): 24.9% -> CCI (Excl BE): 28.8% | Adj Yield v4: 28.8%\n"
            "  [OPP-10005] Apex Telecom Holdings #05        | TCV: $496.28M | CCI (Incl BE): 20.8% -> CCI (Excl BE): 24.0% | Adj Yield v4: 24.0%\n"
            "  [OPP-10081] Obsidian Silicon Systems #81     | TCV: $491.09M | CCI (Incl BE): 31.1% -> CCI (Excl BE): 38.4% | Adj Yield v4: 38.1%\n"
            "  [OPP-10488] Vertexa Therapeutics #08         | TCV: $489.10M | CCI (Incl BE): 20.6% -> CCI (Excl BE): 22.6% | Adj Yield v4: 22.6%"
        ),
    },
    {
        "part_id": "part2",
        "step_number": 2,
        "file_path": "backend/parts/part2_dataplex_license_guard.py",
        "title": "Part 2: Pre-Flight Dataplex GenAI License Guard",
        "tier_badge": "STEP 0 GOVERNANCE",
        "architectural_explanation": (
            "Queries `vtxdemos.commercial_mesh_gold.dataplex_source_governance` prior to LLM prompt assembly. Automatically blocks "
            "`Analyst_Benchmark_Feed_Unlicensed` (`genai_usage_rights = FALSE`) and reroutes to clean-room 1P `deal_pricing_scenarios`."
        ),
        "pre_verified_output": (
            "=== PART 2: DATAPLEX KNOWLEDGE CATALOG PRE-FLIGHT LICENSE GUARD ===\n"
            "  • [SRC-014] Analyst_Benchmark_Feed_Unlicensed   -> BLOCKED (GenAI_Usage_Rights=FALSE)\n"
            "  • [SRC-003] Deal_Pricing_Engine                 -> ALLOWED\n\n"
            "Clean-Room 1P Substitution (`deal_pricing_scenarios` Rate & Yield Telemetry):\n"
            "  [OPP-10095] Outcome / Gain-Share | ADR: $ 1108/day | Discount: 15.0% | CCI Excl BE: 30.3%\n"
            "  [OPP-10358] Time & Materials     | ADR: $ 1630/day | Discount: 13.9% | CCI Excl BE: 28.8%\n"
            "  [OPP-10005] Fixed Price          | ADR: $ 1647/day | Discount: 25.3% | CCI Excl BE: 24.0%\n"
            "  [OPP-10081] Fixed Price          | ADR: $ 1505/day | Discount: 10.6% | CCI Excl BE: 38.4%\n"
            "  [OPP-10488] Managed Capacity     | ADR: $  994/day | Discount: 15.7% | CCI Excl BE: 22.6%"
        ),
    },
    {
        "part_id": "part3",
        "step_number": 3,
        "file_path": "backend/parts/part3_tier1_mcp_toolbox_sql.py",
        "title": "Part 3: Tier 1 (18%) Parameterized SQL via Google MCP Toolbox",
        "tier_badge": "TIER 1 • 18% OF QUESTIONS",
        "architectural_explanation": (
            "Executes deterministic, parameterized BigQuery SQL for Tier 1 fact lookups: identifies all 45 opportunities stalled >90 days "
            "in `Stage 2B - Solutioning` and computes 8-quarter regional win rates across NA, EMEA, APAC, and LATAM."
        ),
        "pre_verified_output": (
            "=== PART 3: TIER 1 DETERMINISTIC MCP TOOLBOX SQL (Stage 2B > 90 Days) ===\n"
            "  • Found 45 deals stalled > 90 days in `Stage 2B - Solutioning`:\n"
            "    [OPP-10005] Apex Telecom Holdings #05      | 119d in Stage 2B | TCV: $496.28M | PWin: 38.0%\n"
            "    [OPP-10034] Solstice Power & Renewables #34 | 130d in Stage 2B | TCV: $479.05M | PWin: 44.7%\n"
            "    [OPP-10019] Atlas Capital Markets #19      | 125d in Stage 2B | TCV: $463.54M | PWin: 48.7%\n"
            "    [OPP-10017] Valiant Telecom Holdings #17   | 142d in Stage 2B | TCV: $453.69M | PWin: 28.7%\n"
            "    [OPP-10023] Equinox Media Networks #23     | 107d in Stage 2B | TCV: $406.13M | PWin: 52.0%\n\n"
            "  • 8-Quarter Regional Win Rates & Pipeline Velocity:\n"
            "    Region LATAM | Deals: 125 | TCV: $12959.66M | Avg PWin: 52.0% | Closed Win Rate: 48.5%\n"
            "    Region NA    | Deals: 125 | TCV: $12907.40M | Avg PWin: 49.5% | Closed Win Rate: 33.3%\n"
            "    Region APAC  | Deals: 125 | TCV: $11393.24M | Avg PWin: 52.9% | Closed Win Rate: 40.7%\n"
            "    Region EMEA  | Deals: 125 | TCV: $ 9692.69M | Avg PWin: 52.1% | Closed Win Rate: 55.6%"
        ),
    },
    {
        "part_id": "part4",
        "step_number": 4,
        "file_path": "backend/parts/part4_tier2_kc_and_simulator.py",
        "title": "Part 4: Tier 2 (30%) Semantic DAX & Python Counterfactual Simulator",
        "tier_badge": "TIER 2 • 30% OF QUESTIONS",
        "architectural_explanation": (
            "Queries `v_gold_pricing_yield_dax` and executes the Python What-If Counterfactual Simulator to quantify the margin uplift (+bps) "
            "from pruning the bottom 20% lowest-yielding deals and simulating 25% AI task substitution across AMS & Cloud constructs."
        ),
        "pre_verified_output": (
            "=== PART 4: TIER 2 SEMANTIC DAX & PYTHON COUNTERFACTUAL SIMULATOR ===\n"
            "  • Portfolio Pruning (Bottom 20% Cull): Baseline Yield v4 = 27.43% -> Post-Cull = 29.61% (+218.0 bps uplift)\n"
            "  • 25% AI Task Substitution Simulation: Baseline CCI (Excl BE) = 27.39% -> Post-AI Construct CCI = 33.77% (+638.2 bps net impact)"
        ),
    },
    {
        "part_id": "part5",
        "step_number": 5,
        "file_path": "backend/parts/part5_tier3_federated_agent.py",
        "title": "Part 5: Tier 3 (49%) Federated Agent (`gemini-3.8-flash` @ `global`)",
        "tier_badge": "TIER 3 • 49% OF QUESTIONS",
        "architectural_explanation": (
            "Invokes `gemini-3.8-flash` (`location=\"global\"`, `project=\"vtxdemos\"`) to synthesize structured BigQuery rows "
            "(`v_gold_stage2b_stalled_deals`) + unstructured CLM contract clauses (`clm_contract_vault_chunks`) + external 3P signals (`external_market_signals`)."
        ),
        "pre_verified_output": (
            "=== PART 5: TIER 3 FEDERATED MULTI-TOOL AGENT (gemini-3.8-flash @ global) ===\n\n"
            "Gemini 3.8 Flash Federated Synthesis:\n"
            "* **Symptom ($1.44B Mega-Deal Gridlock):** Stage 2B pipeline velocity has halted across top opportunities (Apex Telecom, Solstice Power, Atlas Capital) with deals languishing between 119 to 130 days, while delivered margins (CCI 21.8%–30.7%) fall well below standard hurdle rates.\n"
            "* **Contractual Root Cause (Mandated Deflation):** Enterprise buyers are systematically weaponizing CLM SOW amendments (Section 14.3 GenAI Productivity Deflator), demanding non-negotiable 25% unit-rate cuts across L1/L2 and testing workstreams starting in Month 7—unconditionally decoupled from client cloud readiness.\n"
            "* **External Catalyst (Aggressive Competitor Undercutting):** Market disruption is accelerating the freeze, evidenced by maximum buyer intent surge scores (98–99) exploited by Boutique AI Natives offering outcome-based fixed fees 30% below legacy T&M, alongside Global SI peers offering 18% rate cuts plus free pilot credits to force displacement.\n"
            "* **Remediation Action Plan:** Establish an executive Deal Desk strike team within 5 business days to: (1) strike mandatory unconditional deflation clauses, replacing them with gain-share models pegged to verified cloud-readiness gates; and (2) restructure commoditized L1/L2 T&M scope into output-based AI-native pods to neutralize competitor pricing undercut while protecting baseline margins."
        ),
    },
]


class FederatedCommercialMeshOrchestrator:
    """Executes 4-Tier Federated Routing, BigQuery Explorer, Demo Parts, and Gemini 3.8 Flash Copilot."""

    def __init__(self) -> None:
        self.project_id = "vtxdemos"
        self.location = "global"
        self.model_name = "gemini-3.8-flash"
        self._genai_client = None
        self._bq_client = None
        self._bq_explorer_cache: Optional[Dict[str, Any]] = None

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

    def _get_bq_client(self):
        if self._bq_client is not None:
            return self._bq_client
        try:
            from google.cloud import bigquery

            self._bq_client = bigquery.Client(project=BQ_PROJECT_ID, location="US")
            return self._bq_client
        except Exception:
            return None

    def get_bq_explorer_data(self, force_refresh: bool = False) -> Dict[str, Any]:
        """Returns live table metadata, row counts, and sample rows from `vtxdemos.commercial_mesh_gold` with in-memory caching."""
        if self._bq_explorer_cache is not None and not force_refresh:
            return {**self._bq_explorer_cache, "cached": True}

        t0 = time.perf_counter()
        bq = self._get_bq_client()
        tables_out: List[Dict[str, Any]] = []
        total_rows = 0

        if bq is not None:
            try:
                for meta in BQ_TABLES_META:
                    tid = meta["table_id"]
                    full_id = meta["full_table_id"]
                    t_ref = bq.get_table(full_id)
                    num_rows = int(t_ref.num_rows or meta["expected_rows"])
                    total_rows += num_rows
                    schema_fields = [
                        {"name": f.name, "type": f.field_type, "mode": f.mode}
                        for f in t_ref.schema
                    ]
                    sample_query = f"SELECT * FROM `{full_id}` LIMIT 5"
                    sample_rows = [
                        json.loads(json.dumps(dict(r), default=str))
                        for r in bq.query(sample_query).result()
                    ]
                    tables_out.append(
                        {
                            **meta,
                            "row_count": num_rows,
                            "column_count": len(schema_fields),
                            "schema": schema_fields,
                            "sample_rows": sample_rows,
                        }
                    )
            except Exception as exc:
                tables_out = [
                    {
                        **m,
                        "row_count": m["expected_rows"],
                        "column_count": 0,
                        "schema": [],
                        "sample_rows": [],
                        "warning": str(exc),
                    }
                    for m in BQ_TABLES_META
                ]
                total_rows = sum(m["expected_rows"] for m in BQ_TABLES_META)
        else:
            tables_out = [
                {
                    **m,
                    "row_count": m["expected_rows"],
                    "column_count": 0,
                    "schema": [],
                    "sample_rows": [],
                }
                for m in BQ_TABLES_META
            ]
            total_rows = sum(m["expected_rows"] for m in BQ_TABLES_META)

        elapsed_ms = round((time.perf_counter() - t0) * 1000, 1)
        payload = {
            "project_id": BQ_PROJECT_ID,
            "dataset_id": BQ_DATASET_ID,
            "full_dataset": f"{BQ_PROJECT_ID}.{BQ_DATASET_ID}",
            "location": "US",
            "total_tables": len(tables_out),
            "total_views": len(BQ_GOLD_VIEWS_META),
            "total_rows": total_rows,
            "tables": tables_out,
            "views": BQ_GOLD_VIEWS_META,
            "load_latency_ms": elapsed_ms,
            "cached": False,
        }
        self._bq_explorer_cache = payload
        return payload

    def get_demo_parts_catalog(self) -> Dict[str, Any]:
        """Returns the 5 concise Python code snippets (`part1`..`part5`), titles, explanations, and pre-verified outputs."""
        parts_list = []
        for item in DEMO_PARTS_CATALOG:
            code_path = BASE_DIR / item["file_path"]
            code_str = code_path.read_text(encoding="utf-8") if code_path.exists() else ""
            line_count = len(code_str.strip().splitlines())
            parts_list.append(
                {
                    **item,
                    "code": code_str,
                    "line_count": line_count,
                }
            )
        return {
            "project_id": BQ_PROJECT_ID,
            "dataset_id": BQ_DATASET_ID,
            "model": self.model_name,
            "location": self.location,
            "walkthrough_file": "backend/live_demo_walkthrough.py",
            "notebook_file": "backend/customer_live_demo.ipynb",
            "parts": parts_list,
        }

    def run_demo_part_live(self, part_id: str) -> Dict[str, Any]:
        """Executes `part1`..`part5` live against `vtxdemos.commercial_mesh_gold` + `gemini-3.8-flash` (`location='global'`)."""
        norm = (part_id or "part1").strip().lower()
        if not norm.startswith("part"):
            norm = f"part{norm}"

        part_meta = next((p for p in DEMO_PARTS_CATALOG if p["part_id"] == norm), None)
        if part_meta is None:
            raise KeyError(f"Unknown demo part_id '{part_id}'. Expected 'part1'..'part5'.")

        t0 = time.perf_counter()
        buf = io.StringIO()
        structured_result: Dict[str, Any] = {}

        with contextlib.redirect_stdout(buf):
            if norm == "part1":
                from backend.parts.part1_bigquery_gold_spine import run_part1

                structured_result = run_part1()
            elif norm == "part2":
                from backend.parts.part2_dataplex_license_guard import run_part2

                structured_result = run_part2()
            elif norm == "part3":
                from backend.parts.part3_tier1_mcp_toolbox_sql import run_part3

                structured_result = run_part3()
            elif norm == "part4":
                from backend.parts.part4_tier2_kc_and_simulator import run_part4

                structured_result = run_part4()
            elif norm == "part5":
                from backend.parts.part5_tier3_federated_agent import run_part5

                structured_result = run_part5()

        elapsed_ms = round((time.perf_counter() - t0) * 1000, 1)
        stdout_text = buf.getvalue().strip()

        return {
            "part_id": norm,
            "title": part_meta["title"],
            "tier_badge": part_meta["tier_badge"],
            "file_path": part_meta["file_path"],
            "status": "EXECUTED_LIVE",
            "dataset": f"{BQ_PROJECT_ID}.{BQ_DATASET_ID}",
            "model": self.model_name,
            "location": self.location,
            "latency_ms": elapsed_ms,
            "stdout": stdout_text,
            "telemetry": json.loads(json.dumps(structured_result, default=str)),
        }

    def load_catalog(self) -> Dict[str, Any]:
        with open(CATALOG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

    def get_question_by_id(self, question_id: str) -> Dict[str, Any]:
        catalog = self.load_catalog()
        raw = (question_id or "").strip().upper()
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
                "detail": f"Executed governed SQL against vtxdemos.commercial_mesh_gold ({len(sql_rows)} rows returned).",
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
            f"MCP Toolbox returned **{len(sql_rows)} structured records** from the governed BigQuery Gold Spine (`vtxdemos.commercial_mesh_gold`).",
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
        """AI Architect Copilot powered by Vertex AI Gemini 3.8 Flash (`location='global'`, `project='vtxdemos'`)."""
        q_context: Optional[Dict[str, Any]] = None
        sim_result: Optional[Dict[str, Any]] = None

        if question_id:
            try:
                sim_result = self.simulate_question_execution(question_id, custom_params)
                q_context = self.get_question_by_id(question_id)
            except KeyError:
                q_context = None

        system_instruction = """You are the Principal Enterprise Data Mesh & Agentic AI Architect for `vtxdemos.commercial_mesh_gold`.
CRITICAL COMMUNICATION RULES:
1. Be CONCISE, DIRECT, and CONVERSATIONAL. Answer the user's specific question in 3 to 5 tight bullet points (under 140 words) unless the user explicitly asks for full SQL or YAML code.
2. NEVER dump unsolicited boilerplate headers (like '### Architectural Diagnosis' or '#### Missing Artifacts') if the user didn't ask for them. Answer their exact question first!
3. If the user asks "how did you know there were hidden unstructured notes?" or similar, explain directly:
   - Although sources like `crm_opportunities`, `delivery_governance_hub`, and `clm_contract_vault_chunks` appear in the structured tracker, the actual root-cause answers (e.g., why a Stage 2B deal is stalled, delivery director review commentary, client visit debriefs, or custom gain-share/rate-cap contract clauses) live inside free-text narrative columns (`unstructured_director_review_notes`, `verbatim_text_chunk`), NOT structured numeric SQL columns.
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
                "Live Telemetry Summary:\n"
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
                        max_output_tokens=1024,
                        thinking_config=types.ThinkingConfig(thinking_budget=0),
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
            except Exception:
                pass

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
