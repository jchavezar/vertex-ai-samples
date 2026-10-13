import { ArchitecturalTier, BlockerFlag, BenchmarkQuestion } from './types';

export const ARCHITECTURAL_TIERS: ArchitecturalTier[] = [
  {
    id: 'TIER_1',
    code: 'TIER 1 // ~18%',
    title: 'Deterministic Parameterized SQL',
    subtitle: 'Google MCP Toolbox for Databases (genai-toolbox)',
    coveragePct: 18,
    cumulativeCeilingPct: 18,
    avgConfidencePct: 91,
    engineStack: ['genai-toolbox', 'Parameterized SQL', 'CRM_Opportunity_Spine'],
    description:
      'Direct single/multi-table SQL lookups over canonical BigQuery Gold Views with zero LLM SQL hallucination risk.',
    whyRawMcpFails:
      'Works for Tier 1 (~18%), but fails when queries require proprietary DAX business ratios, counterfactual simulations, or unstructured contract/visit RAG.',
  },
  {
    id: 'TIER_2',
    code: 'TIER 2 // ~30%',
    title: 'Semantic Layer (Dataplex KC DAX) + Gold Views + Simulator',
    subtitle: 'Dataplex Knowledge Catalog + BQCA + Materialized Gold Views + Python Sandbox',
    coveragePct: 30,
    cumulativeCeilingPct: 48,
    avgConfidencePct: 68,
    engineStack: [
      'Dataplex KC Glossary',
      'BigQuery Gold Views',
      'BQ Conversational Analytics',
      'Python What-If Sandbox',
    ],
    description:
      'Materializes complex DAX formulas (Adjusted Yield v1/v3/v4, Markov Regimes) in BigQuery Gold Views and executes Python counterfactual What-If simulations.',
    whyRawMcpFails:
      'Raw execute_sql hallucinates join paths across 15TB Revenue_ODS_15TB and Deal_Pricing_Engine tables and cannot execute Monte Carlo or margin stress-tests.',
  },
  {
    id: 'TIER_3',
    code: 'TIER 3 // ~49%',
    title: 'Federated Multi-Tool Agent (SQL + Unstructured RAG + 3P Market APIs)',
    subtitle: 'ADK Orchestrator + Pre-Flight License Guard + Vertex AI Search + Licensed Market MCPs',
    coveragePct: 49,
    cumulativeCeilingPct: 97,
    avgConfidencePct: 45,
    engineStack: [
      'ADK Multi-Agent Mesh',
      'Pre-Flight License Guard',
      'Vertex AI Search (CLM & Visits)',
      'Licensed External Market MCP',
    ],
    description:
      'Combines structured BigQuery telemetry with unstructured CLM_Contract_Vault / Customer_Visit_Logs RAG and licensed external market feeds behind a Pre-Flight Compliance Guard.',
    whyRawMcpFails:
      'Qualitative root causes, MSA COLA/termination clauses, and unlicensed 3P analyst feeds (Analyst_Benchmark_Feed_Unlicensed) cannot be queried via raw SQL.',
  },
  {
    id: 'TIER_4',
    code: 'TIER 4 // ~3%',
    title: 'Multi-System Action & Executive Briefing Automation',
    subtitle: 'Workspace Action MCP + Executive QBR Packet & Pursuit Squad Mobilization',
    coveragePct: 3,
    cumulativeCeilingPct: 100,
    avgConfidencePct: 44,
    engineStack: ['Workspace Action MCP', 'Account 360 QBR Generator', 'Pursuit Mobilization Webhook'],
    description:
      'Synthesizes cross-domain Account 360 intelligence into executive QBR packets and triggers pursuit squad mobilization workflows.',
    whyRawMcpFails:
      'Database MCP servers are read-only analytical connectors and cannot orchestrate cross-platform Workspace document synthesis or pursuit mobilization.',
  },
];

export const BLOCKER_FLAGS: BlockerFlag[] = [
  {
    id: 'License Compliance Blocker',
    label: 'License Compliance Blocker',
    shortCode: 'LIC-GUARD',
    severity: 'CRITICAL',
    count: 1,
    description:
      '3P market research feeds (Analyst_Benchmark_Feed_Unlicensed) contractually prohibit LLM context ingestion or vectorization (GenAI_Usage_Rights = 0).',
    remediationPattern:
      'Enforce deterministic Pre-Flight Policy Guard in ADK before tool invocation; block unlicensed feeds and substitute governed 1P telemetry.',
  },
  {
    id: 'Missing ML Model in DB',
    label: 'Missing ML Model in DB',
    shortCode: 'ML-MODEL',
    severity: 'HIGH',
    count: 3,
    description:
      'Requires Hidden Markov regime classification, logistic win-probability regression, or econometric elasticity models not stored in raw transaction tables.',
    remediationPattern:
      'Materialize BigQuery ML (BQML) / Python model inference scores into Gold Views or invoke a Vertex AI Model Endpoint via ADK.',
  },
  {
    id: 'Counterfactual What-If Simulator',
    label: 'Counterfactual What-If Simulator',
    shortCode: 'WHAT-IF',
    severity: 'HIGH',
    count: 5,
    description:
      'Scenario stress-tests (e.g., repricing bottom-decile yield deals by +300 bps or shifting onshore/offshore pyramid mix).',
    remediationPattern:
      'Fetch baseline cohort parameters via genai-toolbox, then execute deterministic Python counterfactual simulation in the ADK sandbox.',
  },
  {
    id: 'Hidden Unstructured Notes',
    label: 'Hidden Unstructured Notes',
    shortCode: 'UNSTRUCT-RAG',
    severity: 'CRITICAL',
    count: 8,
    description:
      'Deal slippage rationale, MSA COLA/termination caps, and executive sentiment live in PDFs (CLM_Contract_Vault) and call notes (Customer_Visit_Logs).',
    remediationPattern:
      'Federate structured BigQuery deal IDs with Vertex AI Search unstructured grounding over indexed CLM contracts and field visit transcripts.',
  },
  {
    id: 'External 3P Market API',
    label: 'External 3P Market API',
    shortCode: 'EXT-API',
    severity: 'MEDIUM',
    count: 8,
    description:
      'Requires live external buyer intent surges (Buyer_Intent_Signal_Stream), tech-stack telemetry, or SEC EDGAR 10-K/8-K filings outside BigQuery.',
    remediationPattern:
      'Orchestrate parallel tool calls to licensed External Market Intelligence MCP servers alongside internal CRM_Opportunity_Spine queries.',
  },
  {
    id: 'Incomplete Spec',
    label: 'Incomplete Spec',
    shortCode: 'SCHEMA-GAP',
    severity: 'MEDIUM',
    count: 4,
    description:
      'Requires unmapped cross-system entity bridges (e.g., hyperscaler co-sell drawdown registry or Adjusted Yield v1/v3/v4 DAX reconciliation).',
    remediationPattern:
      'Bind terms to canonical Dataplex Knowledge Catalog (KC) business glossary definitions and materialize reconciled BigQuery Gold Views.',
  },
];

export const BENCHMARK_QUESTIONS: BenchmarkQuestion[] = [
  {
    "id": "Q-001",
    "code": "Q-001",
    "priority": "P1-Now",
    "persona": "Global Pipeline Operations Director",
    "domain": "Pipeline Velocity & Stage Bottlenecks",
    "question": "Which active opportunities are stalled in Stage 3 (Solutioning) for more than 90 days, ordered by Total Contract Value (TCV) and showing days since last stage progression?",
    "tier": "TIER_1",
    "tierLabel": "Tier 1 (18%): Deterministic Parameterized SQL via MCP Toolbox",
    "systemsInvolved": [
      "CRM_Opportunity_Spine",
      "Revenue_ODS_15TB"
    ],
    "blockerFlags": [],
    "confidence_pct": 92,
    "missing_artifacts": [
      "Physical BigQuery DDL for CRM_Opportunity_Spine stage history audit table (to verify whether Stage 3 re-entry resets stage_entry_date)."
    ],
    "rawDbMcpSufficient": true,
    "dataplexKcCeilingSufficient": true,
    "requiresMultiToolFederation": false,
    "architecturalDiagnosis": "100% deterministic filter, projection, and sort over canonical pipeline columns. Ideal for MCP Toolbox parameterized SQL (`get_stalled_stage_opportunities`) with zero LLM SQL hallucination risk.",
    "recommendedArchitecture": "Route directly through Google MCP Toolbox (`genai-toolbox`) bound to `v_gold_opportunity_spine` in BigQuery.",
    "daxOrMetricFormula": {
      "id": "KPI-Q-001",
      "metricName": "Pipeline Velocity & Stage Bottlenecks",
      "domain": "Internal Structured (BQ)",
      "daxExpression": "Stage_3_Age_Days = DATE_DIFF(CURRENT_DATE(), stage_entry_date, DAY) // Stalled_TCV_At_Risk = SUM(IF(stage_name = 'Stage 3 - Solutioning' AND stage_age_days > 90, tcv_usd, 0))",
      "canonicalSqlExpression": "SELECT opp_id, account_name, region, industry, tcv_usd, acv_usd, stage_age_days, win_prob, deal_owner, markov_regime\nFROM opportunities\nWHERE stage_name LIKE 'Stage 3%' AND stage_age_days >= :min_days\nORDER BY tcv_usd DESC;",
      "dataplexGlossaryTerm": "projects/enterprise-mesh/locations/us/glossaries/commercial-kpi/terms/q_001",
      "sourceSystems": [
        "CRM_Opportunity_Spine",
        "Revenue_ODS_15TB"
      ],
      "grain": "Internal Structured (BQ) // Primary Commercial Entity Grain"
    },
    "genaiToolboxYaml": "  get_stalled_stage_opportunities:\n    kind: bigquery-sql\n    source: enterprise-commercial-bq\n    description: Fetch opportunities stalled in a pipeline stage beyond a threshold of days.\n    parameters:\n      - name: min_days\n        type: integer\n        description: Minimum days stalled in stage (default 90).",
    "bigqueryGoldViewDdl": "-- Canonical BigQuery Gold View for Q-001 (Pipeline Velocity & Stage Bottlenecks)\nCREATE OR REPLACE VIEW `enterprise-commercial-mesh.gold_commercial.v_q_001_spine`\nOPTIONS(\n  description=\"Pipeline Velocity & Stage Bottlenecks governed by Dataplex Knowledge Catalog.\"\n) AS\nSELECT opp_id, account_name, region, industry, tcv_usd, acv_usd, stage_age_days, win_prob, deal_owner, markov_regime\nFROM opportunities\nWHERE stage_name LIKE 'Stage 3%' AND stage_age_days >= :min_days\nORDER BY tcv_usd DESC;",
    "defaultSimulation": {
      "questionId": "Q-001",
      "questionText": "Which active opportunities are stalled in Stage 3 (Solutioning) for more than 90 days, ordered by Total Contract Value (TCV) and showing days since last stage progression?",
      "tier": "TIER_1",
      "complianceStatus": "APPROVED",
      "rawSqlMcpOutcome": "SUCCESS",
      "federatedMeshOutcome": "VERIFIED_SYNTHESIS",
      "totalLatencyMs": 329,
      "traceSteps": [
        {
          "stepOrder": 1,
          "pillar": "PRE_FLIGHT_GOVERNANCE",
          "title": "Pre-Flight Dataplex GenAI License & RBAC Guard",
          "status": "PASSED",
          "latencyMs": 19,
          "detail": "Verified Dataplex governance aspects for sources: CRM_Opportunity_Spine, Revenue_ODS_15TB."
        },
        {
          "stepOrder": 2,
          "pillar": "GENAI_TOOLBOX_MCP",
          "title": "Execute Parameterized SQL via Google MCP Toolbox (genai-toolbox)",
          "status": "SYNTHESIZED",
          "latencyMs": 310,
          "detail": "100% deterministic filter, projection, and sort over canonical pipeline columns. Ideal for MCP Toolbox parameterized SQL (`get_stalled_stage_opportunities`) with zero LLM SQL hallucination risk."
        }
      ],
      "synthesizedAnswer": "### Architectural Synthesis (Q-001 \u2014 Tier 1)\n- **Verdict on Raw Database MCP**: `PASS - Direct Parameterized SQL`\n- **Diagnosis**: 100% deterministic filter, projection, and sort over canonical pipeline columns. Ideal for MCP Toolbox parameterized SQL (`get_stalled_stage_opportunities`) with zero LLM SQL hallucination risk.\n- **Recommended Production Mesh**: Route directly through Google MCP Toolbox (`genai-toolbox`) bound to `v_gold_opportunity_spine` in BigQuery.\n- **Assessment Readiness Confidence**: `92%`",
      "sqlExecuted": "SELECT opp_id, account_name, region, industry, tcv_usd, acv_usd, stage_age_days, win_prob, deal_owner, markov_regime\nFROM opportunities\nWHERE stage_name LIKE 'Stage 3%' AND stage_age_days >= :min_days\nORDER BY tcv_usd DESC;"
    }
  },
  {
    "id": "Q-002",
    "code": "Q-002",
    "priority": "P1-Now",
    "persona": "Regional Commercial Lead",
    "domain": "Regional Win Rate & Booking Velocity",
    "question": "Show our regional pipeline TCV, average win probability, and weighted bookings across North America, EMEA, APAC, and Latin America.",
    "tier": "TIER_1",
    "tierLabel": "Tier 1 (18%): Deterministic Parameterized SQL via MCP Toolbox",
    "systemsInvolved": [
      "CRM_Opportunity_Spine",
      "ERP_Financials_Ledger"
    ],
    "blockerFlags": [],
    "confidence_pct": 91,
    "missing_artifacts": [
      "Corporate FX currency conversion rate table DDL in ERP_Financials_Ledger (constant-dollar vs. spot USD normalization)."
    ],
    "rawDbMcpSufficient": true,
    "dataplexKcCeilingSufficient": true,
    "requiresMultiToolFederation": false,
    "architecturalDiagnosis": "Deterministic regional aggregation over verified Gold Spine measures. Requires no external APIs or stochastic simulation.",
    "recommendedArchitecture": "Execute parameterized MCP Toolbox tool `get_regional_win_rate_trends` against `v_gold_opportunity_spine`.",
    "daxOrMetricFormula": {
      "id": "KPI-Q-002",
      "metricName": "Regional Win Rate & Booking Velocity",
      "domain": "Internal Structured (BQ)",
      "daxExpression": "Weighted_Pipeline_USD = SUM(tcv_usd * win_prob) // Regional_Avg_Adjusted_Yield = AVG(adjusted_yield_v4)",
      "canonicalSqlExpression": "SELECT region,\n       COUNT(*) AS deal_count,\n       ROUND(SUM(tcv_usd) / 1e6, 2) AS total_tcv_millions,\n       ROUND(AVG(win_prob) * 100, 1) AS avg_win_prob_pct,\n       ROUND(SUM(tcv_usd * win_prob) / 1e6, 2) AS weighted_tcv_millions,\n       ROUND(AVG(adjusted_yield_v4) * 100, 1) AS avg_adj_yield_pct\nFROM opportunities\nGROUP BY region\nORDER BY total_tcv_millions DESC;",
      "dataplexGlossaryTerm": "projects/enterprise-mesh/locations/us/glossaries/commercial-kpi/terms/q_002",
      "sourceSystems": [
        "CRM_Opportunity_Spine",
        "ERP_Financials_Ledger"
      ],
      "grain": "Internal Structured (BQ) // Primary Commercial Entity Grain"
    },
    "genaiToolboxYaml": "  get_regional_win_rate_trends:\n    kind: bigquery-sql\n    source: enterprise-commercial-bq\n    description: Aggregate TCV, weighted bookings, and win rates by geographic region.",
    "bigqueryGoldViewDdl": "-- Canonical BigQuery Gold View for Q-002 (Regional Win Rate & Booking Velocity)\nCREATE OR REPLACE VIEW `enterprise-commercial-mesh.gold_commercial.v_q_002_spine`\nOPTIONS(\n  description=\"Regional Win Rate & Booking Velocity governed by Dataplex Knowledge Catalog.\"\n) AS\nSELECT region,\n       COUNT(*) AS deal_count,\n       ROUND(SUM(tcv_usd) / 1e6, 2) AS total_tcv_millions,\n       ROUND(AVG(win_prob) * 100, 1) AS avg_win_prob_pct,\n       ROUND(SUM(tcv_usd * win_prob) / 1e6, 2) AS weighted_tcv_millions,\n       ROUND(AVG(adjusted_yield_v4) * 100, 1) AS avg_adj_yield_pct\nFROM opportunities\nGROUP BY region\nORDER BY total_tcv_millions DESC;",
    "defaultSimulation": {
      "questionId": "Q-002",
      "questionText": "Show our regional pipeline TCV, average win probability, and weighted bookings across North America, EMEA, APAC, and Latin America.",
      "tier": "TIER_1",
      "complianceStatus": "APPROVED",
      "rawSqlMcpOutcome": "SUCCESS",
      "federatedMeshOutcome": "VERIFIED_SYNTHESIS",
      "totalLatencyMs": 329,
      "traceSteps": [
        {
          "stepOrder": 1,
          "pillar": "PRE_FLIGHT_GOVERNANCE",
          "title": "Pre-Flight Dataplex GenAI License & RBAC Guard",
          "status": "PASSED",
          "latencyMs": 19,
          "detail": "Verified Dataplex governance aspects for sources: CRM_Opportunity_Spine, ERP_Financials_Ledger."
        },
        {
          "stepOrder": 2,
          "pillar": "GENAI_TOOLBOX_MCP",
          "title": "Execute Parameterized SQL via Google MCP Toolbox (genai-toolbox)",
          "status": "SYNTHESIZED",
          "latencyMs": 310,
          "detail": "Deterministic regional aggregation over verified Gold Spine measures. Requires no external APIs or stochastic simulation."
        }
      ],
      "synthesizedAnswer": "### Architectural Synthesis (Q-002 \u2014 Tier 1)\n- **Verdict on Raw Database MCP**: `PASS - Direct Parameterized SQL`\n- **Diagnosis**: Deterministic regional aggregation over verified Gold Spine measures. Requires no external APIs or stochastic simulation.\n- **Recommended Production Mesh**: Execute parameterized MCP Toolbox tool `get_regional_win_rate_trends` against `v_gold_opportunity_spine`.\n- **Assessment Readiness Confidence**: `91%`",
      "sqlExecuted": "SELECT region,\n       COUNT(*) AS deal_count,\n       ROUND(SUM(tcv_usd) / 1e6, 2) AS total_tcv_millions,\n       ROUND(AVG(win_prob) * 100, 1) AS avg_win_prob_pct,\n       ROUND(SUM(tcv_usd * win_prob) / 1e6, 2) AS weighted_tcv_millions,\n       ROUND(AVG(adjusted_yield_v4) * 100, 1) AS avg_adj_yield_pct\nFROM opportunities\nGROUP BY region\nORDER BY total_tcv_millions DESC;"
    }
  },
  {
    "id": "Q-003",
    "code": "Q-003",
    "priority": "P1-Now",
    "persona": "Chief Revenue Officer (CRO)",
    "domain": "Mega-Deal Concentration & Top Deals",
    "question": "List the top 10 active deals by TCV across all regions along with their current stage, gross margin, and assigned deal owner.",
    "tier": "TIER_1",
    "tierLabel": "Tier 1 (18%): Deterministic Parameterized SQL via MCP Toolbox",
    "systemsInvolved": [
      "CRM_Opportunity_Spine",
      "Deal_Pricing_Engine"
    ],
    "blockerFlags": [],
    "confidence_pct": 92,
    "missing_artifacts": [
      "Primary scenario flag convention in Deal_Pricing_Engine (confirming is_primary_scenario = TRUE vs. max(version_tag) join key)."
    ],
    "rawDbMcpSufficient": true,
    "dataplexKcCeilingSufficient": true,
    "requiresMultiToolFederation": false,
    "architecturalDiagnosis": "Standard top-N ranking query on primary opportunity spine.",
    "recommendedArchitecture": "Execute MCP Toolbox tool `get_top_tcv_deals_by_region` with optional region parameter.",
    "daxOrMetricFormula": {
      "id": "KPI-Q-003",
      "metricName": "Mega-Deal Concentration & Top Deals",
      "domain": "Internal Structured (BQ)",
      "daxExpression": "Top_N_Concentration_Share = SUM(Top_10_TCV) / SUM(Total_Pipeline_TCV)",
      "canonicalSqlExpression": "SELECT opp_id, account_name, region, stage_name,\n       ROUND(tcv_usd / 1e6, 2) AS tcv_millions,\n       ROUND(gross_margin_pct * 100, 1) AS gross_margin_pct,\n       ROUND(adjusted_yield_v4 * 100, 1) AS adjusted_yield_pct,\n       deal_owner\nFROM opportunities\nORDER BY tcv_usd DESC\nLIMIT 10;",
      "dataplexGlossaryTerm": "projects/enterprise-mesh/locations/us/glossaries/commercial-kpi/terms/q_003",
      "sourceSystems": [
        "CRM_Opportunity_Spine",
        "Deal_Pricing_Engine"
      ],
      "grain": "Internal Structured (BQ) // Primary Commercial Entity Grain"
    },
    "genaiToolboxYaml": "  get_top_tcv_deals_by_region:\n    kind: bigquery-sql\n    source: enterprise-commercial-bq\n    description: Return top N opportunities ordered by TCV.",
    "bigqueryGoldViewDdl": "-- Canonical BigQuery Gold View for Q-003 (Mega-Deal Concentration & Top Deals)\nCREATE OR REPLACE VIEW `enterprise-commercial-mesh.gold_commercial.v_q_003_spine`\nOPTIONS(\n  description=\"Mega-Deal Concentration & Top Deals governed by Dataplex Knowledge Catalog.\"\n) AS\nSELECT opp_id, account_name, region, stage_name,\n       ROUND(tcv_usd / 1e6, 2) AS tcv_millions,\n       ROUND(gross_margin_pct * 100, 1) AS gross_margin_pct,\n       ROUND(adjusted_yield_v4 * 100, 1) AS adjusted_yield_pct,\n       deal_owner\nFROM opportunities\nORDER BY tcv_usd DESC\nLIMIT 10;",
    "defaultSimulation": {
      "questionId": "Q-003",
      "questionText": "List the top 10 active deals by TCV across all regions along with their current stage, gross margin, and assigned deal owner.",
      "tier": "TIER_1",
      "complianceStatus": "APPROVED",
      "rawSqlMcpOutcome": "SUCCESS",
      "federatedMeshOutcome": "VERIFIED_SYNTHESIS",
      "totalLatencyMs": 329,
      "traceSteps": [
        {
          "stepOrder": 1,
          "pillar": "PRE_FLIGHT_GOVERNANCE",
          "title": "Pre-Flight Dataplex GenAI License & RBAC Guard",
          "status": "PASSED",
          "latencyMs": 19,
          "detail": "Verified Dataplex governance aspects for sources: CRM_Opportunity_Spine, Deal_Pricing_Engine."
        },
        {
          "stepOrder": 2,
          "pillar": "GENAI_TOOLBOX_MCP",
          "title": "Execute Parameterized SQL via Google MCP Toolbox (genai-toolbox)",
          "status": "SYNTHESIZED",
          "latencyMs": 310,
          "detail": "Standard top-N ranking query on primary opportunity spine."
        }
      ],
      "synthesizedAnswer": "### Architectural Synthesis (Q-003 \u2014 Tier 1)\n- **Verdict on Raw Database MCP**: `PASS - Direct Parameterized SQL`\n- **Diagnosis**: Standard top-N ranking query on primary opportunity spine.\n- **Recommended Production Mesh**: Execute MCP Toolbox tool `get_top_tcv_deals_by_region` with optional region parameter.\n- **Assessment Readiness Confidence**: `92%`",
      "sqlExecuted": "SELECT opp_id, account_name, region, stage_name,\n       ROUND(tcv_usd / 1e6, 2) AS tcv_millions,\n       ROUND(gross_margin_pct * 100, 1) AS gross_margin_pct,\n       ROUND(adjusted_yield_v4 * 100, 1) AS adjusted_yield_pct,\n       deal_owner\nFROM opportunities\nORDER BY tcv_usd DESC\nLIMIT 10;"
    }
  },
  {
    "id": "Q-004",
    "code": "Q-004",
    "priority": "P1-Now",
    "persona": "Sales Governance Manager",
    "domain": "Pipeline Hygiene & Stale Ownership",
    "question": "Which opportunities have had zero deal owner activity or CRM update for more than 14 days prior to the current snapshot?",
    "tier": "TIER_1",
    "tierLabel": "Tier 1 (18%): Deterministic Parameterized SQL via MCP Toolbox",
    "systemsInvolved": [
      "CRM_Opportunity_Spine"
    ],
    "blockerFlags": [],
    "confidence_pct": 89,
    "missing_artifacts": [
      "Activity event taxonomy in CRM_Opportunity_Spine (confirming whether automated marketing touches update last_owner_activity_date)."
    ],
    "rawDbMcpSufficient": true,
    "dataplexKcCeilingSufficient": true,
    "requiresMultiToolFederation": false,
    "architecturalDiagnosis": "Deterministic date-diff hygiene check on opportunity audit timestamps.",
    "recommendedArchitecture": "Invoke MCP Toolbox `get_stale_owner_opportunities` and surface hygiene alerts.",
    "daxOrMetricFormula": {
      "id": "KPI-Q-004",
      "metricName": "Pipeline Hygiene & Stale Ownership",
      "domain": "Internal Structured (BQ)",
      "daxExpression": "Owner_Inactivity_Days = DATE_DIFF(DATE('2026-10-13'), DATE(last_owner_activity_date), DAY)",
      "canonicalSqlExpression": "SELECT opp_id, account_name, stage_name, deal_owner,\n       last_owner_activity_date,\n       CAST(julianday('2026-10-13') - julianday(last_owner_activity_date) AS INTEGER) AS inactive_days,\n       ROUND(tcv_usd / 1e6, 2) AS tcv_millions\nFROM opportunities\nWHERE julianday('2026-10-13') - julianday(last_owner_activity_date) >= 14\nORDER BY inactive_days DESC;",
      "dataplexGlossaryTerm": "projects/enterprise-mesh/locations/us/glossaries/commercial-kpi/terms/q_004",
      "sourceSystems": [
        "CRM_Opportunity_Spine"
      ],
      "grain": "Internal Structured (BQ) // Primary Commercial Entity Grain"
    },
    "genaiToolboxYaml": "  get_stale_owner_opportunities:\n    kind: bigquery-sql\n    source: enterprise-commercial-bq\n    description: Identify pipeline opportunities with no owner activity for >= N days.",
    "bigqueryGoldViewDdl": "-- Canonical BigQuery Gold View for Q-004 (Pipeline Hygiene & Stale Ownership)\nCREATE OR REPLACE VIEW `enterprise-commercial-mesh.gold_commercial.v_q_004_spine`\nOPTIONS(\n  description=\"Pipeline Hygiene & Stale Ownership governed by Dataplex Knowledge Catalog.\"\n) AS\nSELECT opp_id, account_name, stage_name, deal_owner,\n       last_owner_activity_date,\n       CAST(julianday('2026-10-13') - julianday(last_owner_activity_date) AS INTEGER) AS inactive_days,\n       ROUND(tcv_usd / 1e6, 2) AS tcv_millions\nFROM opportunities\nWHERE julianday('2026-10-13') - julianday(last_owner_activity_date) >= 14\nORDER BY inactive_days DESC;",
    "defaultSimulation": {
      "questionId": "Q-004",
      "questionText": "Which opportunities have had zero deal owner activity or CRM update for more than 14 days prior to the current snapshot?",
      "tier": "TIER_1",
      "complianceStatus": "APPROVED",
      "rawSqlMcpOutcome": "SUCCESS",
      "federatedMeshOutcome": "VERIFIED_SYNTHESIS",
      "totalLatencyMs": 329,
      "traceSteps": [
        {
          "stepOrder": 1,
          "pillar": "PRE_FLIGHT_GOVERNANCE",
          "title": "Pre-Flight Dataplex GenAI License & RBAC Guard",
          "status": "PASSED",
          "latencyMs": 19,
          "detail": "Verified Dataplex governance aspects for sources: CRM_Opportunity_Spine."
        },
        {
          "stepOrder": 2,
          "pillar": "GENAI_TOOLBOX_MCP",
          "title": "Execute Parameterized SQL via Google MCP Toolbox (genai-toolbox)",
          "status": "SYNTHESIZED",
          "latencyMs": 310,
          "detail": "Deterministic date-diff hygiene check on opportunity audit timestamps."
        }
      ],
      "synthesizedAnswer": "### Architectural Synthesis (Q-004 \u2014 Tier 1)\n- **Verdict on Raw Database MCP**: `PASS - Direct Parameterized SQL`\n- **Diagnosis**: Deterministic date-diff hygiene check on opportunity audit timestamps.\n- **Recommended Production Mesh**: Invoke MCP Toolbox `get_stale_owner_opportunities` and surface hygiene alerts.\n- **Assessment Readiness Confidence**: `89%`",
      "sqlExecuted": "SELECT opp_id, account_name, stage_name, deal_owner,\n       last_owner_activity_date,\n       CAST(julianday('2026-10-13') - julianday(last_owner_activity_date) AS INTEGER) AS inactive_days,\n       ROUND(tcv_usd / 1e6, 2) AS tcv_millions\nFROM opportunities\nWHERE julianday('2026-10-13') - julianday(last_owner_activity_date) >= 14\nORDER BY inactive_days DESC;"
    }
  },
  {
    "id": "Q-005",
    "code": "Q-005",
    "priority": "P2-Next",
    "persona": "Service Line Managing Director",
    "domain": "Service Line Mix & ACV Breakdown",
    "question": "Break down active Annual Contract Value (ACV) and Total Contract Value (TCV) by industry vertical and service line.",
    "tier": "TIER_1",
    "tierLabel": "Tier 1 (18%): Deterministic Parameterized SQL via MCP Toolbox",
    "systemsInvolved": [
      "CRM_Opportunity_Spine",
      "Revenue_ODS_15TB"
    ],
    "blockerFlags": [],
    "confidence_pct": 90,
    "missing_artifacts": [
      "Multi-service-line split allocation table in Revenue_ODS_15TB for bundled multi-tower contracts."
    ],
    "rawDbMcpSufficient": true,
    "dataplexKcCeilingSufficient": true,
    "requiresMultiToolFederation": false,
    "architecturalDiagnosis": "Clean dimensional group-by on curated Gold View columns.",
    "recommendedArchitecture": "Serve via MCP Toolbox parameterized dimensional aggregation over `v_gold_opportunity_spine`.",
    "daxOrMetricFormula": {
      "id": "KPI-Q-005",
      "metricName": "Service Line Mix & ACV Breakdown",
      "domain": "Internal Structured (BQ)",
      "daxExpression": "ACV_to_TCV_Velocity_Ratio = SAFE_DIVIDE(SUM(acv_usd), SUM(tcv_usd))",
      "canonicalSqlExpression": "SELECT industry, service_line,\n       COUNT(*) AS opps,\n       ROUND(SUM(acv_usd) / 1e6, 2) AS total_acv_m,\n       ROUND(SUM(tcv_usd) / 1e6, 2) AS total_tcv_m\nFROM opportunities\nGROUP BY industry, service_line\nORDER BY total_tcv_m DESC;",
      "dataplexGlossaryTerm": "projects/enterprise-mesh/locations/us/glossaries/commercial-kpi/terms/q_005",
      "sourceSystems": [
        "CRM_Opportunity_Spine",
        "Revenue_ODS_15TB"
      ],
      "grain": "Internal Structured (BQ) // Primary Commercial Entity Grain"
    },
    "genaiToolboxYaml": "  get_service_line_acv_mix:\n    kind: bigquery-sql\n    source: enterprise-commercial-bq\n    description: Group ACV and TCV by industry vertical and service line.",
    "bigqueryGoldViewDdl": "-- Canonical BigQuery Gold View for Q-005 (Service Line Mix & ACV Breakdown)\nCREATE OR REPLACE VIEW `enterprise-commercial-mesh.gold_commercial.v_q_005_spine`\nOPTIONS(\n  description=\"Service Line Mix & ACV Breakdown governed by Dataplex Knowledge Catalog.\"\n) AS\nSELECT industry, service_line,\n       COUNT(*) AS opps,\n       ROUND(SUM(acv_usd) / 1e6, 2) AS total_acv_m,\n       ROUND(SUM(tcv_usd) / 1e6, 2) AS total_tcv_m\nFROM opportunities\nGROUP BY industry, service_line\nORDER BY total_tcv_m DESC;",
    "defaultSimulation": {
      "questionId": "Q-005",
      "questionText": "Break down active Annual Contract Value (ACV) and Total Contract Value (TCV) by industry vertical and service line.",
      "tier": "TIER_1",
      "complianceStatus": "APPROVED",
      "rawSqlMcpOutcome": "SUCCESS",
      "federatedMeshOutcome": "VERIFIED_SYNTHESIS",
      "totalLatencyMs": 329,
      "traceSteps": [
        {
          "stepOrder": 1,
          "pillar": "PRE_FLIGHT_GOVERNANCE",
          "title": "Pre-Flight Dataplex GenAI License & RBAC Guard",
          "status": "PASSED",
          "latencyMs": 19,
          "detail": "Verified Dataplex governance aspects for sources: CRM_Opportunity_Spine, Revenue_ODS_15TB."
        },
        {
          "stepOrder": 2,
          "pillar": "GENAI_TOOLBOX_MCP",
          "title": "Execute Parameterized SQL via Google MCP Toolbox (genai-toolbox)",
          "status": "SYNTHESIZED",
          "latencyMs": 310,
          "detail": "Clean dimensional group-by on curated Gold View columns."
        }
      ],
      "synthesizedAnswer": "### Architectural Synthesis (Q-005 \u2014 Tier 1)\n- **Verdict on Raw Database MCP**: `PASS - Direct Parameterized SQL`\n- **Diagnosis**: Clean dimensional group-by on curated Gold View columns.\n- **Recommended Production Mesh**: Serve via MCP Toolbox parameterized dimensional aggregation over `v_gold_opportunity_spine`.\n- **Assessment Readiness Confidence**: `90%`",
      "sqlExecuted": "SELECT industry, service_line,\n       COUNT(*) AS opps,\n       ROUND(SUM(acv_usd) / 1e6, 2) AS total_acv_m,\n       ROUND(SUM(tcv_usd) / 1e6, 2) AS total_tcv_m\nFROM opportunities\nGROUP BY industry, service_line\nORDER BY total_tcv_m DESC;"
    }
  },
  {
    "id": "Q-006",
    "code": "Q-006",
    "priority": "P1-Now",
    "persona": "Global Pricing & Margin VP",
    "domain": "Adjusted Yield DAX & Outlier Trimming",
    "question": "Calculate Adjusted Yield v1, v3, and v4 across our deal portfolio after stripping pass-through cloud/hardware costs, trimming top/bottom 5% outliers, and capping standard deviation sensitivity at 1.5 sigma.",
    "tier": "TIER_2",
    "tierLabel": "Tier 2 (30%): Semantic Layer (Dataplex KC DAX Formulas) + Pre-Computed Gold Views + Counterfactual Simulator",
    "systemsInvolved": [
      "Deal_Pricing_Engine",
      "CRM_Opportunity_Spine",
      "ERP_Financials_Ledger"
    ],
    "blockerFlags": [
      "Incomplete Spec"
    ],
    "confidence_pct": 74,
    "missing_artifacts": [
      "Exact semantic DAX formula sheet for Adjusted Yield v1/v3/v4 (specifically pass-through cloud/hardware cost GL account codes).",
      "Confirm whether 1.5-sigma clipping is partitioned by Industry Vertical or Global Region."
    ],
    "rawDbMcpSufficient": false,
    "dataplexKcCeilingSufficient": true,
    "requiresMultiToolFederation": false,
    "architecturalDiagnosis": "Raw LLM Text-to-SQL fails because 'Adjusted Yield v4' is a multi-stage proprietary DAX formula with pass-through deduction and 1.5-sigma clipping that does not exist as a raw column in the 15TB ODS.",
    "recommendedArchitecture": "Materialize the v1/v3/v4 DAX formulas inside BigQuery Gold View `v_gold_adjusted_yield_dax` and register business glossary lineage in Dataplex Knowledge Catalog.",
    "daxOrMetricFormula": {
      "id": "KPI-Q-006",
      "metricName": "Adjusted Yield DAX & Outlier Trimming",
      "domain": "Internal Structured (BQ)",
      "daxExpression": "Adjusted_Yield_v1 = SAFE_DIVIDE(Gross_Margin_USD - PassThrough_Cost_USD, Net_Service_Revenue_USD) // Adjusted_Yield_v3_Trimmed = PERCENTILE_CONT(Adjusted_Yield_v1, 0.05..0.95) OVER (PARTITION BY industry) // Adjusted_Yield_v4_SigmaCapped = LEAST(GREATEST(Adjusted_Yield_v1, Mean_Yield - 1.5*StdDev_Yield), Mean_Yield + 1.5*StdDev_Yield)",
      "canonicalSqlExpression": "SELECT p.opp_id, o.account_name, o.industry,\n       ROUND(p.tcv_usd / 1e6, 2) AS tcv_m,\n       ROUND(p.passthrough_cost_usd / 1e6, 2) AS passthrough_m,\n       ROUND(p.gross_yield_v1 * 100, 1) AS gross_yield_v1_pct,\n       ROUND(p.adjusted_yield_v3_trimmed * 100, 1) AS adj_yield_v3_trimmed_pct,\n       ROUND(p.adjusted_yield_v4_sigma_capped * 100, 1) AS adj_yield_v4_sigma_pct,\n       p.sigma_zscore\nFROM pricing_scenarios p\nJOIN opportunities o ON p.opp_id = o.opp_id\nORDER BY p.adjusted_yield_v4_sigma_capped ASC;",
      "dataplexGlossaryTerm": "projects/enterprise-mesh/locations/us/glossaries/commercial-kpi/terms/q_006",
      "sourceSystems": [
        "Deal_Pricing_Engine",
        "CRM_Opportunity_Spine",
        "ERP_Financials_Ledger"
      ],
      "grain": "Internal Structured (BQ) // Primary Commercial Entity Grain"
    },
    "genaiToolboxYaml": "  get_adjusted_yield_dax_metrics:\n    kind: bigquery-sql\n    source: enterprise-commercial-bq\n    description: Query materialized Adjusted Yield v1/v3/v4 DAX metrics from Gold View.",
    "bigqueryGoldViewDdl": "-- Canonical BigQuery Gold View for Q-006 (Adjusted Yield DAX & Outlier Trimming)\nCREATE OR REPLACE VIEW `enterprise-commercial-mesh.gold_commercial.v_q_006_spine`\nOPTIONS(\n  description=\"Adjusted Yield DAX & Outlier Trimming governed by Dataplex Knowledge Catalog.\"\n) AS\nSELECT p.opp_id, o.account_name, o.industry,\n       ROUND(p.tcv_usd / 1e6, 2) AS tcv_m,\n       ROUND(p.passthrough_cost_usd / 1e6, 2) AS passthrough_m,\n       ROUND(p.gross_yield_v1 * 100, 1) AS gross_yield_v1_pct,\n       ROUND(p.adjusted_yield_v3_trimmed * 100, 1) AS adj_yield_v3_trimmed_pct,\n       ROUND(p.adjusted_yield_v4_sigma_capped * 100, 1) AS adj_yield_v4_sigma_pct,\n       p.sigma_zscore\nFROM pricing_scenarios p\nJOIN opportunities o ON p.opp_id = o.opp_id\nORDER BY p.adjusted_yield_v4_sigma_capped ASC;",
    "defaultSimulation": {
      "questionId": "Q-006",
      "questionText": "Calculate Adjusted Yield v1, v3, and v4 across our deal portfolio after stripping pass-through cloud/hardware costs, trimming top/bottom 5% outliers, and capping standard deviation sensitivity at 1.5 sigma.",
      "tier": "TIER_2",
      "complianceStatus": "APPROVED",
      "rawSqlMcpOutcome": "FAILED_HALLUCINATED_METRIC",
      "federatedMeshOutcome": "VERIFIED_SYNTHESIS",
      "totalLatencyMs": 649,
      "traceSteps": [
        {
          "stepOrder": 1,
          "pillar": "PRE_FLIGHT_GOVERNANCE",
          "title": "Pre-Flight Dataplex GenAI License & RBAC Guard",
          "status": "PASSED",
          "latencyMs": 19,
          "detail": "Verified Dataplex governance aspects for sources: Deal_Pricing_Engine, CRM_Opportunity_Spine, ERP_Financials_Ledger."
        },
        {
          "stepOrder": 2,
          "pillar": "DATAPLEX_KC_BQCA",
          "title": "Resolve DAX Business Formula in Dataplex Knowledge Catalog & Gold Views",
          "status": "EXECUTED",
          "latencyMs": 220,
          "detail": "Bound KPI formula: Adjusted_Yield_v1 = SAFE_DIVIDE(Gross_Margin_USD - PassThrough_Cost_USD, Net_Service_Revenue_USD)"
        },
        {
          "stepOrder": 3,
          "pillar": "PYTHON_WHAT_IF_SANDBOX",
          "title": "Execute Counterfactual What-If / Econometric Regime Simulation",
          "status": "SYNTHESIZED",
          "latencyMs": 410,
          "detail": "Materialize the v1/v3/v4 DAX formulas inside BigQuery Gold View `v_gold_adjusted_yield_dax` and register business glossary lineage in Dataplex Knowledge Catalog."
        }
      ],
      "synthesizedAnswer": "### Architectural Synthesis (Q-006 \u2014 Tier 2)\n- **Verdict on Raw Database MCP**: `PARTIAL - Requires Semantic DAX + Gold View`\n- **Diagnosis**: Raw LLM Text-to-SQL fails because 'Adjusted Yield v4' is a multi-stage proprietary DAX formula with pass-through deduction and 1.5-sigma clipping that does not exist as a raw column in the 15TB ODS.\n- **Recommended Production Mesh**: Materialize the v1/v3/v4 DAX formulas inside BigQuery Gold View `v_gold_adjusted_yield_dax` and register business glossary lineage in Dataplex Knowledge Catalog.\n- **Assessment Readiness Confidence**: `74%`",
      "sqlExecuted": "SELECT p.opp_id, o.account_name, o.industry,\n       ROUND(p.tcv_usd / 1e6, 2) AS tcv_m,\n       ROUND(p.passthrough_cost_usd / 1e6, 2) AS passthrough_m,\n       ROUND(p.gross_yield_v1 * 100, 1) AS gross_yield_v1_pct,\n       ROUND(p.adjusted_yield_v3_trimmed * 100, 1) AS adj_yield_v3_trimmed_pct,\n       ROUND(p.adjusted_yield_v4_sigma_capped * 100, 1) AS adj_yield_v4_sigma_pct,\n       p.sigma_zscore\nFROM pricing_scenarios p\nJOIN opportunities o ON p.opp_id = o.opp_id\nORDER BY p.adjusted_yield_v4_sigma_capped ASC;"
    }
  },
  {
    "id": "Q-007",
    "code": "Q-007",
    "priority": "P1-Now",
    "persona": "Portfolio Strategy CFO",
    "domain": "Counterfactual Portfolio Pruning Simulator",
    "question": "If we systematically exit or re-price the bottom 20% lowest-yielding deals in our pipeline, what is the counterfactual impact on blended portfolio margin, total revenue retained, and freed-up delivery capacity?",
    "tier": "TIER_2",
    "tierLabel": "Tier 2 (30%): Semantic Layer (Dataplex KC DAX Formulas) + Pre-Computed Gold Views + Counterfactual Simulator",
    "systemsInvolved": [
      "Deal_Pricing_Engine",
      "CRM_Opportunity_Spine",
      "Workforce_Skills_Graph"
    ],
    "blockerFlags": [
      "Counterfactual What-If Simulator"
    ],
    "confidence_pct": 68,
    "missing_artifacts": [
      "Counterfactual customer churn elasticity curve when repricing bottom-decile deals by +300 bps.",
      "Stranded bench cost absorption parameters in Workforce_Skills_Graph."
    ],
    "rawDbMcpSufficient": false,
    "dataplexKcCeilingSufficient": true,
    "requiresMultiToolFederation": false,
    "architecturalDiagnosis": "Static SQL only reports historical state. Answering 'what if we exit the bottom X% or reprice to floor Y%' requires a parameterized percentile-cull and elasticity simulator.",
    "recommendedArchitecture": "Combine MCP Toolbox Gold View query (`simulate_portfolio_margin_cull`) with the Python Counterfactual Monte Carlo Engine.",
    "daxOrMetricFormula": {
      "id": "KPI-Q-007",
      "metricName": "Counterfactual Portfolio Pruning Simulator",
      "domain": "Internal Structured (BQ)",
      "daxExpression": "Baseline_Blended_Yield = SUM(Net_Margin_USD) / SUM(Net_Service_Rev_USD) // Post_Cull_Blended_Yield = SUM(Net_Margin_USD WHERE Yield_Percentile > 0.20) / SUM(Net_Service_Rev_USD WHERE Yield_Percentile > 0.20) // Margin_Bps_Uplift = (Post_Cull_Blended_Yield - Baseline_Blended_Yield) * 10000",
      "canonicalSqlExpression": "WITH ranked AS (\n  SELECT o.opp_id, o.account_name, p.tcv_usd, p.net_service_rev_usd,\n         p.adjusted_yield_v4_sigma_capped AS adj_yield,\n         PERCENT_RANK() OVER (ORDER BY p.adjusted_yield_v4_sigma_capped ASC) AS yield_pct_rank\n  FROM pricing_scenarios p\n  JOIN opportunities o ON p.opp_id = o.opp_id\n)\nSELECT\n  ROUND(AVG(adj_yield) * 100, 2) AS baseline_avg_yield_pct,\n  ROUND(AVG(CASE WHEN yield_pct_rank >= 0.20 THEN adj_yield END) * 100, 2) AS post_exit_avg_yield_pct,\n  ROUND(SUM(CASE WHEN yield_pct_rank < 0.20 THEN tcv_usd ELSE 0 END) / 1e6, 2) AS exited_tcv_millions,\n  ROUND(SUM(CASE WHEN yield_pct_rank >= 0.20 THEN tcv_usd ELSE 0 END) / 1e6, 2) AS retained_tcv_millions\nFROM ranked;",
      "dataplexGlossaryTerm": "projects/enterprise-mesh/locations/us/glossaries/commercial-kpi/terms/q_007",
      "sourceSystems": [
        "Deal_Pricing_Engine",
        "CRM_Opportunity_Spine",
        "Workforce_Skills_Graph"
      ],
      "grain": "Internal Structured (BQ) // Primary Commercial Entity Grain"
    },
    "genaiToolboxYaml": "  simulate_portfolio_margin_cull:\n    kind: bigquery-sql\n    source: enterprise-commercial-bq\n    description: Simulate blended margin uplift when pruning bottom N% yield deals.",
    "bigqueryGoldViewDdl": "-- Canonical BigQuery Gold View for Q-007 (Counterfactual Portfolio Pruning Simulator)\nCREATE OR REPLACE VIEW `enterprise-commercial-mesh.gold_commercial.v_q_007_spine`\nOPTIONS(\n  description=\"Counterfactual Portfolio Pruning Simulator governed by Dataplex Knowledge Catalog.\"\n) AS\nWITH ranked AS (\n  SELECT o.opp_id, o.account_name, p.tcv_usd, p.net_service_rev_usd,\n         p.adjusted_yield_v4_sigma_capped AS adj_yield,\n         PERCENT_RANK() OVER (ORDER BY p.adjusted_yield_v4_sigma_capped ASC) AS yield_pct_rank\n  FROM pricing_scenarios p\n  JOIN opportunities o ON p.opp_id = o.opp_id\n)\nSELECT\n  ROUND(AVG(adj_yield) * 100, 2) AS baseline_avg_yield_pct,\n  ROUND(AVG(CASE WHEN yield_pct_rank >= 0.20 THEN adj_yield END) * 100, 2) AS post_exit_avg_yield_pct,\n  ROUND(SUM(CASE WHEN yield_pct_rank < 0.20 THEN tcv_usd ELSE 0 END) / 1e6, 2) AS exited_tcv_millions,\n  ROUND(SUM(CASE WHEN yield_pct_rank >= 0.20 THEN tcv_usd ELSE 0 END) / 1e6, 2) AS retained_tcv_millions\nFROM ranked;",
    "defaultSimulation": {
      "questionId": "Q-007",
      "questionText": "If we systematically exit or re-price the bottom 20% lowest-yielding deals in our pipeline, what is the counterfactual impact on blended portfolio margin, total revenue retained, and freed-up delivery capacity?",
      "tier": "TIER_2",
      "complianceStatus": "APPROVED",
      "rawSqlMcpOutcome": "FAILED_HALLUCINATED_METRIC",
      "federatedMeshOutcome": "VERIFIED_SYNTHESIS",
      "totalLatencyMs": 649,
      "traceSteps": [
        {
          "stepOrder": 1,
          "pillar": "PRE_FLIGHT_GOVERNANCE",
          "title": "Pre-Flight Dataplex GenAI License & RBAC Guard",
          "status": "PASSED",
          "latencyMs": 19,
          "detail": "Verified Dataplex governance aspects for sources: Deal_Pricing_Engine, CRM_Opportunity_Spine, Workforce_Skills_Graph."
        },
        {
          "stepOrder": 2,
          "pillar": "DATAPLEX_KC_BQCA",
          "title": "Resolve DAX Business Formula in Dataplex Knowledge Catalog & Gold Views",
          "status": "EXECUTED",
          "latencyMs": 220,
          "detail": "Bound KPI formula: Baseline_Blended_Yield = SUM(Net_Margin_USD) / SUM(Net_Service_Rev_USD)"
        },
        {
          "stepOrder": 3,
          "pillar": "PYTHON_WHAT_IF_SANDBOX",
          "title": "Execute Counterfactual What-If / Econometric Regime Simulation",
          "status": "SYNTHESIZED",
          "latencyMs": 410,
          "detail": "Combine MCP Toolbox Gold View query (`simulate_portfolio_margin_cull`) with the Python Counterfactual Monte Carlo Engine."
        }
      ],
      "synthesizedAnswer": "### Architectural Synthesis (Q-007 \u2014 Tier 2)\n- **Verdict on Raw Database MCP**: `PARTIAL - Requires Counterfactual Simulator`\n- **Diagnosis**: Static SQL only reports historical state. Answering 'what if we exit the bottom X% or reprice to floor Y%' requires a parameterized percentile-cull and elasticity simulator.\n- **Recommended Production Mesh**: Combine MCP Toolbox Gold View query (`simulate_portfolio_margin_cull`) with the Python Counterfactual Monte Carlo Engine.\n- **Assessment Readiness Confidence**: `68%`",
      "sqlExecuted": "WITH ranked AS (\n  SELECT o.opp_id, o.account_name, p.tcv_usd, p.net_service_rev_usd,\n         p.adjusted_yield_v4_sigma_capped AS adj_yield,\n         PERCENT_RANK() OVER (ORDER BY p.adjusted_yield_v4_sigma_capped ASC) AS yield_pct_rank\n  FROM pricing_scenarios p\n  JOIN opportunities o ON p.opp_id = o.opp_id\n)\nSELECT\n  ROUND(AVG(adj_yield) * 100, 2) AS baseline_avg_yield_pct,\n  ROUND(AVG(CASE WHEN yield_pct_rank >= 0.20 THEN adj_yield END) * 100, 2) AS post_exit_avg_yield_pct,\n  ROUND(SUM(CASE WHEN yield_pct_rank < 0.20 THEN tcv_usd ELSE 0 END) / 1e6, 2) AS exited_tcv_millions,\n  ROUND(SUM(CASE WHEN yield_pct_rank >= 0.20 THEN tcv_usd ELSE 0 END) / 1e6, 2) AS retained_tcv_millions\nFROM ranked;"
    }
  },
  {
    "id": "Q-008",
    "code": "Q-008",
    "priority": "P1-Now",
    "persona": "Commercial Data Science Lead",
    "domain": "Econometric & Markov Regime Modeling",
    "question": "Classify all active accounts into Hidden Markov Pricing Regimes (High-Velocity Expansion, Margin Compression, or Stalled Procurement) and show transition probabilities when discount concessions exceed 15%.",
    "tier": "TIER_2",
    "tierLabel": "Tier 2 (30%): Semantic Layer (Dataplex KC DAX Formulas) + Pre-Computed Gold Views + Counterfactual Simulator",
    "systemsInvolved": [
      "Deal_Pricing_Engine",
      "CRM_Opportunity_Spine",
      "Revenue_ODS_15TB"
    ],
    "blockerFlags": [
      "Missing ML Model in DB",
      "Counterfactual What-If Simulator"
    ],
    "confidence_pct": 52,
    "missing_artifacts": [
      "Trained Hidden Markov Model (Baum-Welch transition matrix & emission probability weights) not currently persisted in BigQuery.",
      "Historical 8-quarter pricing version sequence log in Deal_Pricing_Engine."
    ],
    "rawDbMcpSufficient": false,
    "dataplexKcCeilingSufficient": true,
    "requiresMultiToolFederation": false,
    "architecturalDiagnosis": "A relational database does not natively run Hidden Markov Baum-Welch / Viterbi state estimation at query time unless pre-materialized by BQML or a Python econometric pipeline.",
    "recommendedArchitecture": "Pre-compute Markov state probabilities in BigQuery ML / Python job into `v_gold_markov_regime_states` and expose transition shocks in the Tier-2 Simulator.",
    "daxOrMetricFormula": {
      "id": "KPI-Q-008",
      "metricName": "Econometric & Markov Regime Modeling",
      "domain": "Internal Structured (BQ)",
      "daxExpression": "Markov_Regime_State = ARGMAX_s P(S_t = s | Yield_Delta, Stage_Velocity, Giveaway_Pct) // Compression_Transition_Prob = P(S_{t+1} = Margin_Compression | Discount_Pct > 0.15)",
      "canonicalSqlExpression": "SELECT o.markov_regime,\n       COUNT(*) AS deal_count,\n       ROUND(SUM(o.tcv_usd) / 1e6, 2) AS regime_tcv_millions,\n       ROUND(AVG(p.discount_giveaway_pct) * 100, 1) AS avg_giveaway_pct,\n       ROUND(AVG(p.adjusted_yield_v4_sigma_capped) * 100, 1) AS avg_adj_yield_pct\nFROM opportunities o\nJOIN pricing_scenarios p ON o.opp_id = p.opp_id\nGROUP BY o.markov_regime\nORDER BY regime_tcv_millions DESC;",
      "dataplexGlossaryTerm": "projects/enterprise-mesh/locations/us/glossaries/commercial-kpi/terms/q_008",
      "sourceSystems": [
        "Deal_Pricing_Engine",
        "CRM_Opportunity_Spine",
        "Revenue_ODS_15TB"
      ],
      "grain": "Internal Structured (BQ) // Primary Commercial Entity Grain"
    },
    "genaiToolboxYaml": "  get_markov_regime_distribution:\n    kind: bigquery-sql\n    source: enterprise-commercial-bq\n    description: Retrieve Hidden Markov commercial regime states and giveaway averages.",
    "bigqueryGoldViewDdl": "-- Canonical BigQuery Gold View for Q-008 (Econometric & Markov Regime Modeling)\nCREATE OR REPLACE VIEW `enterprise-commercial-mesh.gold_commercial.v_q_008_spine`\nOPTIONS(\n  description=\"Econometric & Markov Regime Modeling governed by Dataplex Knowledge Catalog.\"\n) AS\nSELECT o.markov_regime,\n       COUNT(*) AS deal_count,\n       ROUND(SUM(o.tcv_usd) / 1e6, 2) AS regime_tcv_millions,\n       ROUND(AVG(p.discount_giveaway_pct) * 100, 1) AS avg_giveaway_pct,\n       ROUND(AVG(p.adjusted_yield_v4_sigma_capped) * 100, 1) AS avg_adj_yield_pct\nFROM opportunities o\nJOIN pricing_scenarios p ON o.opp_id = p.opp_id\nGROUP BY o.markov_regime\nORDER BY regime_tcv_millions DESC;",
    "defaultSimulation": {
      "questionId": "Q-008",
      "questionText": "Classify all active accounts into Hidden Markov Pricing Regimes (High-Velocity Expansion, Margin Compression, or Stalled Procurement) and show transition probabilities when discount concessions exceed 15%.",
      "tier": "TIER_2",
      "complianceStatus": "APPROVED",
      "rawSqlMcpOutcome": "FAILED_HALLUCINATED_METRIC",
      "federatedMeshOutcome": "VERIFIED_SYNTHESIS",
      "totalLatencyMs": 649,
      "traceSteps": [
        {
          "stepOrder": 1,
          "pillar": "PRE_FLIGHT_GOVERNANCE",
          "title": "Pre-Flight Dataplex GenAI License & RBAC Guard",
          "status": "PASSED",
          "latencyMs": 19,
          "detail": "Verified Dataplex governance aspects for sources: Deal_Pricing_Engine, CRM_Opportunity_Spine, Revenue_ODS_15TB."
        },
        {
          "stepOrder": 2,
          "pillar": "DATAPLEX_KC_BQCA",
          "title": "Resolve DAX Business Formula in Dataplex Knowledge Catalog & Gold Views",
          "status": "EXECUTED",
          "latencyMs": 220,
          "detail": "Bound KPI formula: Markov_Regime_State = ARGMAX_s P(S_t = s | Yield_Delta, Stage_Velocity, Giveaway_Pct)"
        },
        {
          "stepOrder": 3,
          "pillar": "PYTHON_WHAT_IF_SANDBOX",
          "title": "Execute Counterfactual What-If / Econometric Regime Simulation",
          "status": "SYNTHESIZED",
          "latencyMs": 410,
          "detail": "Pre-compute Markov state probabilities in BigQuery ML / Python job into `v_gold_markov_regime_states` and expose transition shocks in the Tier-2 Simulator."
        }
      ],
      "synthesizedAnswer": "### Architectural Synthesis (Q-008 \u2014 Tier 2)\n- **Verdict on Raw Database MCP**: `PARTIAL - Requires Semantic DAX + Gold View`\n- **Diagnosis**: A relational database does not natively run Hidden Markov Baum-Welch / Viterbi state estimation at query time unless pre-materialized by BQML or a Python econometric pipeline.\n- **Recommended Production Mesh**: Pre-compute Markov state probabilities in BigQuery ML / Python job into `v_gold_markov_regime_states` and expose transition shocks in the Tier-2 Simulator.\n- **Assessment Readiness Confidence**: `52%`",
      "sqlExecuted": "SELECT o.markov_regime,\n       COUNT(*) AS deal_count,\n       ROUND(SUM(o.tcv_usd) / 1e6, 2) AS regime_tcv_millions,\n       ROUND(AVG(p.discount_giveaway_pct) * 100, 1) AS avg_giveaway_pct,\n       ROUND(AVG(p.adjusted_yield_v4_sigma_capped) * 100, 1) AS avg_adj_yield_pct\nFROM opportunities o\nJOIN pricing_scenarios p ON o.opp_id = p.opp_id\nGROUP BY o.markov_regime\nORDER BY regime_tcv_millions DESC;"
    }
  },
  {
    "id": "Q-009",
    "code": "Q-009",
    "priority": "P1-Now",
    "persona": "Enterprise Deal Desk Lead",
    "domain": "6-Lever Win Probability Elasticity",
    "question": "Decompose deal win probability across the 6 commercial levers (Price Competitiveness, Executive Sponsor Alignment, Technical Differentiation, Delivery Track Record, Contracting Speed, and Partner Co-Sell) and simulate a +10% improvement in Price Competitiveness.",
    "tier": "TIER_2",
    "tierLabel": "Tier 2 (30%): Semantic Layer (Dataplex KC DAX Formulas) + Pre-Computed Gold Views + Counterfactual Simulator",
    "systemsInvolved": [
      "CRM_Opportunity_Spine",
      "Deal_Pricing_Engine",
      "Delivery_Governance_Hub"
    ],
    "blockerFlags": [
      "Missing ML Model in DB",
      "Counterfactual What-If Simulator"
    ],
    "confidence_pct": 58,
    "missing_artifacts": [
      "Fitted 6-lever logistic regression feature weights (b0..b6) across won/lost deals in CRM_Opportunity_Spine.",
      "Competitor bid spread proxy variable in Deal_Pricing_Engine."
    ],
    "rawDbMcpSufficient": false,
    "dataplexKcCeilingSufficient": true,
    "requiresMultiToolFederation": false,
    "architecturalDiagnosis": "Calculating marginal win-rate elasticity across 6 interacting levers requires logistic regression coefficients stored in the Gold View plus an interactive perturbation engine.",
    "recommendedArchitecture": "Query baseline lever scores via MCP Toolbox `get_deal_win_lever_elasticity` and run the 6-Lever Logit Perturbation Simulator in the agent tier.",
    "daxOrMetricFormula": {
      "id": "KPI-Q-009",
      "metricName": "6-Lever Win Probability Elasticity",
      "domain": "Internal Structured (BQ)",
      "daxExpression": "Logit_Win_Prob = 1 / (1 + EXP(-(b0 + b1*Price_Score + b2*Sponsor_Alignment + b3*Delivery_SLA + b4*Stage_Velocity))) // Elasticity_dWin_dPrice = b1 * Win_Prob * (1 - Win_Prob)",
      "canonicalSqlExpression": "SELECT o.opp_id, o.account_name,\n       ROUND(o.tcv_usd / 1e6, 2) AS tcv_m,\n       ROUND(o.win_prob * 100, 1) AS baseline_win_prob_pct,\n       ROUND(o.client_Temp_score * 100, 1) AS sponsor_alignment_score,\n       ROUND(p.price_competitiveness_score * 100, 1) AS price_competitiveness_score,\n       ROUND(MIN(0.96, o.win_prob + 0.085 * (1 - o.win_prob)) * 100, 1) AS simulated_win_prob_plus10_price_pct\nFROM opportunities o\nJOIN pricing_scenarios p ON o.opp_id = p.opp_id\nORDER BY o.tcv_usd DESC;",
      "dataplexGlossaryTerm": "projects/enterprise-mesh/locations/us/glossaries/commercial-kpi/terms/q_009",
      "sourceSystems": [
        "CRM_Opportunity_Spine",
        "Deal_Pricing_Engine",
        "Delivery_Governance_Hub"
      ],
      "grain": "Internal Structured (BQ) // Primary Commercial Entity Grain"
    },
    "genaiToolboxYaml": "  get_deal_win_lever_elasticity:\n    kind: bigquery-sql\n    source: enterprise-commercial-bq\n    description: Fetch 6-lever deal win probability drivers and elasticity uplift.",
    "bigqueryGoldViewDdl": "-- Canonical BigQuery Gold View for Q-009 (6-Lever Win Probability Elasticity)\nCREATE OR REPLACE VIEW `enterprise-commercial-mesh.gold_commercial.v_q_009_spine`\nOPTIONS(\n  description=\"6-Lever Win Probability Elasticity governed by Dataplex Knowledge Catalog.\"\n) AS\nSELECT o.opp_id, o.account_name,\n       ROUND(o.tcv_usd / 1e6, 2) AS tcv_m,\n       ROUND(o.win_prob * 100, 1) AS baseline_win_prob_pct,\n       ROUND(o.client_Temp_score * 100, 1) AS sponsor_alignment_score,\n       ROUND(p.price_competitiveness_score * 100, 1) AS price_competitiveness_score,\n       ROUND(MIN(0.96, o.win_prob + 0.085 * (1 - o.win_prob)) * 100, 1) AS simulated_win_prob_plus10_price_pct\nFROM opportunities o\nJOIN pricing_scenarios p ON o.opp_id = p.opp_id\nORDER BY o.tcv_usd DESC;",
    "defaultSimulation": {
      "questionId": "Q-009",
      "questionText": "Decompose deal win probability across the 6 commercial levers (Price Competitiveness, Executive Sponsor Alignment, Technical Differentiation, Delivery Track Record, Contracting Speed, and Partner Co-Sell) and simulate a +10% improvement in Price Competitiveness.",
      "tier": "TIER_2",
      "complianceStatus": "APPROVED",
      "rawSqlMcpOutcome": "FAILED_HALLUCINATED_METRIC",
      "federatedMeshOutcome": "VERIFIED_SYNTHESIS",
      "totalLatencyMs": 649,
      "traceSteps": [
        {
          "stepOrder": 1,
          "pillar": "PRE_FLIGHT_GOVERNANCE",
          "title": "Pre-Flight Dataplex GenAI License & RBAC Guard",
          "status": "PASSED",
          "latencyMs": 19,
          "detail": "Verified Dataplex governance aspects for sources: CRM_Opportunity_Spine, Deal_Pricing_Engine, Delivery_Governance_Hub."
        },
        {
          "stepOrder": 2,
          "pillar": "DATAPLEX_KC_BQCA",
          "title": "Resolve DAX Business Formula in Dataplex Knowledge Catalog & Gold Views",
          "status": "EXECUTED",
          "latencyMs": 220,
          "detail": "Bound KPI formula: Logit_Win_Prob = 1 / (1 + EXP(-(b0 + b1*Price_Score + b2*Sponsor_Alignment + b3*Delivery_SLA + b4*Stage_Velocity)))"
        },
        {
          "stepOrder": 3,
          "pillar": "PYTHON_WHAT_IF_SANDBOX",
          "title": "Execute Counterfactual What-If / Econometric Regime Simulation",
          "status": "SYNTHESIZED",
          "latencyMs": 410,
          "detail": "Query baseline lever scores via MCP Toolbox `get_deal_win_lever_elasticity` and run the 6-Lever Logit Perturbation Simulator in the agent tier."
        }
      ],
      "synthesizedAnswer": "### Architectural Synthesis (Q-009 \u2014 Tier 2)\n- **Verdict on Raw Database MCP**: `PARTIAL - Requires Counterfactual Simulator`\n- **Diagnosis**: Calculating marginal win-rate elasticity across 6 interacting levers requires logistic regression coefficients stored in the Gold View plus an interactive perturbation engine.\n- **Recommended Production Mesh**: Query baseline lever scores via MCP Toolbox `get_deal_win_lever_elasticity` and run the 6-Lever Logit Perturbation Simulator in the agent tier.\n- **Assessment Readiness Confidence**: `58%`",
      "sqlExecuted": "SELECT o.opp_id, o.account_name,\n       ROUND(o.tcv_usd / 1e6, 2) AS tcv_m,\n       ROUND(o.win_prob * 100, 1) AS baseline_win_prob_pct,\n       ROUND(o.client_Temp_score * 100, 1) AS sponsor_alignment_score,\n       ROUND(p.price_competitiveness_score * 100, 1) AS price_competitiveness_score,\n       ROUND(MIN(0.96, o.win_prob + 0.085 * (1 - o.win_prob)) * 100, 1) AS simulated_win_prob_plus10_price_pct\nFROM opportunities o\nJOIN pricing_scenarios p ON o.opp_id = p.opp_id\nORDER BY o.tcv_usd DESC;"
    }
  },
  {
    "id": "Q-010",
    "code": "Q-010",
    "priority": "P2-Next",
    "persona": "Corporate FP&A Stress-Test Director",
    "domain": "Mega-Deal Loss & Concentration Stress Test",
    "question": "Run a downside stress test: if our single largest $510M mega-deal (OPP-9020) is lost or slips by two quarters, what happens to North America bookings coverage and blended delivery utilization?",
    "tier": "TIER_2",
    "tierLabel": "Tier 2 (30%): Semantic Layer (Dataplex KC DAX Formulas) + Pre-Computed Gold Views + Counterfactual Simulator",
    "systemsInvolved": [
      "CRM_Opportunity_Spine",
      "ERP_Financials_Ledger",
      "Workforce_Skills_Graph"
    ],
    "blockerFlags": [
      "Counterfactual What-If Simulator"
    ],
    "confidence_pct": 76,
    "missing_artifacts": [
      "Quarterly regional bookings target table in ERP_Financials_Ledger.",
      "Role-level ramp schedule linking OPP-9020 to Workforce_Skills_Graph bench headcount."
    ],
    "rawDbMcpSufficient": false,
    "dataplexKcCeilingSufficient": true,
    "requiresMultiToolFederation": false,
    "architecturalDiagnosis": "Requires counterfactual removal of specific mega-deal IDs and recomputation of regional target coverage and bench absorption.",
    "recommendedArchitecture": "Execute stress-test simulation over `v_gold_opportunity_spine` comparing baseline vs. ex-OPP-9020 scenarios.",
    "daxOrMetricFormula": {
      "id": "KPI-Q-010",
      "metricName": "Mega-Deal Loss & Concentration Stress Test",
      "domain": "Internal Structured (BQ)",
      "daxExpression": "Stress_Coverage_Ratio = (Weighted_Pipeline_USD - MegaDeal_Weighted_USD) / Quarterly_Target_USD // Bench_Utilization_Shock_Bps = -1 * (MegaDeal_FTE_Demand / Regional_Billable_Headcount) * 10000",
      "canonicalSqlExpression": "SELECT\n  ROUND(SUM(tcv_usd * win_prob) / 1e6, 2) AS baseline_weighted_pipeline_m,\n  ROUND(SUM(CASE WHEN opp_id != 'OPP-9020' THEN tcv_usd * win_prob ELSE 0 END) / 1e6, 2) AS stressed_weighted_pipeline_m,\n  ROUND(SUM(CASE WHEN opp_id = 'OPP-9020' THEN tcv_usd * win_prob ELSE 0 END) / 1e6, 2) AS mega_deal_exposure_m\nFROM opportunities\nWHERE region = 'North America';",
      "dataplexGlossaryTerm": "projects/enterprise-mesh/locations/us/glossaries/commercial-kpi/terms/q_010",
      "sourceSystems": [
        "CRM_Opportunity_Spine",
        "ERP_Financials_Ledger",
        "Workforce_Skills_Graph"
      ],
      "grain": "Internal Structured (BQ) // Primary Commercial Entity Grain"
    },
    "genaiToolboxYaml": "  simulate_megadeal_slippage_shock:\n    kind: bigquery-sql\n    source: enterprise-commercial-bq\n    description: Compute weighted pipeline shock if a specified mega-deal slips or is lost.",
    "bigqueryGoldViewDdl": "-- Canonical BigQuery Gold View for Q-010 (Mega-Deal Loss & Concentration Stress Test)\nCREATE OR REPLACE VIEW `enterprise-commercial-mesh.gold_commercial.v_q_010_spine`\nOPTIONS(\n  description=\"Mega-Deal Loss & Concentration Stress Test governed by Dataplex Knowledge Catalog.\"\n) AS\nSELECT\n  ROUND(SUM(tcv_usd * win_prob) / 1e6, 2) AS baseline_weighted_pipeline_m,\n  ROUND(SUM(CASE WHEN opp_id != 'OPP-9020' THEN tcv_usd * win_prob ELSE 0 END) / 1e6, 2) AS stressed_weighted_pipeline_m,\n  ROUND(SUM(CASE WHEN opp_id = 'OPP-9020' THEN tcv_usd * win_prob ELSE 0 END) / 1e6, 2) AS mega_deal_exposure_m\nFROM opportunities\nWHERE region = 'North America';",
    "defaultSimulation": {
      "questionId": "Q-010",
      "questionText": "Run a downside stress test: if our single largest $510M mega-deal (OPP-9020) is lost or slips by two quarters, what happens to North America bookings coverage and blended delivery utilization?",
      "tier": "TIER_2",
      "complianceStatus": "APPROVED",
      "rawSqlMcpOutcome": "FAILED_HALLUCINATED_METRIC",
      "federatedMeshOutcome": "VERIFIED_SYNTHESIS",
      "totalLatencyMs": 649,
      "traceSteps": [
        {
          "stepOrder": 1,
          "pillar": "PRE_FLIGHT_GOVERNANCE",
          "title": "Pre-Flight Dataplex GenAI License & RBAC Guard",
          "status": "PASSED",
          "latencyMs": 19,
          "detail": "Verified Dataplex governance aspects for sources: CRM_Opportunity_Spine, ERP_Financials_Ledger, Workforce_Skills_Graph."
        },
        {
          "stepOrder": 2,
          "pillar": "DATAPLEX_KC_BQCA",
          "title": "Resolve DAX Business Formula in Dataplex Knowledge Catalog & Gold Views",
          "status": "EXECUTED",
          "latencyMs": 220,
          "detail": "Bound KPI formula: Stress_Coverage_Ratio = (Weighted_Pipeline_USD - MegaDeal_Weighted_USD) / Quarterly_Target_USD"
        },
        {
          "stepOrder": 3,
          "pillar": "PYTHON_WHAT_IF_SANDBOX",
          "title": "Execute Counterfactual What-If / Econometric Regime Simulation",
          "status": "SYNTHESIZED",
          "latencyMs": 410,
          "detail": "Execute stress-test simulation over `v_gold_opportunity_spine` comparing baseline vs. ex-OPP-9020 scenarios."
        }
      ],
      "synthesizedAnswer": "### Architectural Synthesis (Q-010 \u2014 Tier 2)\n- **Verdict on Raw Database MCP**: `PARTIAL - Requires Counterfactual Simulator`\n- **Diagnosis**: Requires counterfactual removal of specific mega-deal IDs and recomputation of regional target coverage and bench absorption.\n- **Recommended Production Mesh**: Execute stress-test simulation over `v_gold_opportunity_spine` comparing baseline vs. ex-OPP-9020 scenarios.\n- **Assessment Readiness Confidence**: `76%`",
      "sqlExecuted": "SELECT\n  ROUND(SUM(tcv_usd * win_prob) / 1e6, 2) AS baseline_weighted_pipeline_m,\n  ROUND(SUM(CASE WHEN opp_id != 'OPP-9020' THEN tcv_usd * win_prob ELSE 0 END) / 1e6, 2) AS stressed_weighted_pipeline_m,\n  ROUND(SUM(CASE WHEN opp_id = 'OPP-9020' THEN tcv_usd * win_prob ELSE 0 END) / 1e6, 2) AS mega_deal_exposure_m\nFROM opportunities\nWHERE region = 'North America';"
    }
  },
  {
    "id": "Q-011",
    "code": "Q-011",
    "priority": "P2-Next",
    "persona": "Commercial Pricing Operations Lead",
    "domain": "Unapproved Giveaway & Margin Leakage",
    "question": "Quantify total commercial giveaway (rate card ceiling vs. negotiated bill rate excluding pass-through expenses) across deals where discount exceeds 15%.",
    "tier": "TIER_2",
    "tierLabel": "Tier 2 (30%): Semantic Layer (Dataplex KC DAX Formulas) + Pre-Computed Gold Views + Counterfactual Simulator",
    "systemsInvolved": [
      "Deal_Pricing_Engine",
      "CRM_Opportunity_Spine"
    ],
    "blockerFlags": [
      "Incomplete Spec"
    ],
    "confidence_pct": 79,
    "missing_artifacts": [
      "Master regional rate-card ceiling table DDL in Deal_Pricing_Engine mapped by labor grade and shore tier."
    ],
    "rawDbMcpSufficient": false,
    "dataplexKcCeilingSufficient": true,
    "requiresMultiToolFederation": false,
    "architecturalDiagnosis": "Requires joining rate card baselines to final pricing scenarios while excluding hardware/cloud pass-through revenue.",
    "recommendedArchitecture": "Expose via `v_gold_adjusted_yield_dax` in Dataplex Knowledge Catalog with strict semantic definition of Net Service Revenue.",
    "daxOrMetricFormula": {
      "id": "KPI-Q-011",
      "metricName": "Unapproved Giveaway & Margin Leakage",
      "domain": "Internal Structured (BQ)",
      "daxExpression": "Rate_Card_Giveaway_USD = (standard_rate_usd - negotiated_rate_usd) / standard_rate_usd * net_service_rev_usd // Net_Margin_Erosion_Bps = (gross_yield_v1 - adjusted_yield_v4_sigma_capped) * 10000",
      "canonicalSqlExpression": "SELECT p.opp_id, o.account_name,\n       p.standard_rate_usd, p.negotiated_rate_usd,\n       ROUND(p.discount_giveaway_pct * 100, 1) AS giveaway_pct,\n       ROUND((p.net_service_rev_usd * p.discount_giveaway_pct) / 1e6, 2) AS giveaway_leakage_millions\nFROM pricing_scenarios p\nJOIN opportunities o ON p.opp_id = o.opp_id\nWHERE p.discount_giveaway_pct >= 0.15\nORDER BY giveaway_leakage_millions DESC;",
      "dataplexGlossaryTerm": "projects/enterprise-mesh/locations/us/glossaries/commercial-kpi/terms/q_011",
      "sourceSystems": [
        "Deal_Pricing_Engine",
        "CRM_Opportunity_Spine"
      ],
      "grain": "Internal Structured (BQ) // Primary Commercial Entity Grain"
    },
    "genaiToolboxYaml": "  get_commercial_giveaway_leakage:\n    kind: bigquery-sql\n    source: enterprise-commercial-bq\n    description: Calculate dollar margin leakage from rate card giveaways > threshold.",
    "bigqueryGoldViewDdl": "-- Canonical BigQuery Gold View for Q-011 (Unapproved Giveaway & Margin Leakage)\nCREATE OR REPLACE VIEW `enterprise-commercial-mesh.gold_commercial.v_q_011_spine`\nOPTIONS(\n  description=\"Unapproved Giveaway & Margin Leakage governed by Dataplex Knowledge Catalog.\"\n) AS\nSELECT p.opp_id, o.account_name,\n       p.standard_rate_usd, p.negotiated_rate_usd,\n       ROUND(p.discount_giveaway_pct * 100, 1) AS giveaway_pct,\n       ROUND((p.net_service_rev_usd * p.discount_giveaway_pct) / 1e6, 2) AS giveaway_leakage_millions\nFROM pricing_scenarios p\nJOIN opportunities o ON p.opp_id = o.opp_id\nWHERE p.discount_giveaway_pct >= 0.15\nORDER BY giveaway_leakage_millions DESC;",
    "defaultSimulation": {
      "questionId": "Q-011",
      "questionText": "Quantify total commercial giveaway (rate card ceiling vs. negotiated bill rate excluding pass-through expenses) across deals where discount exceeds 15%.",
      "tier": "TIER_2",
      "complianceStatus": "APPROVED",
      "rawSqlMcpOutcome": "FAILED_HALLUCINATED_METRIC",
      "federatedMeshOutcome": "VERIFIED_SYNTHESIS",
      "totalLatencyMs": 649,
      "traceSteps": [
        {
          "stepOrder": 1,
          "pillar": "PRE_FLIGHT_GOVERNANCE",
          "title": "Pre-Flight Dataplex GenAI License & RBAC Guard",
          "status": "PASSED",
          "latencyMs": 19,
          "detail": "Verified Dataplex governance aspects for sources: Deal_Pricing_Engine, CRM_Opportunity_Spine."
        },
        {
          "stepOrder": 2,
          "pillar": "DATAPLEX_KC_BQCA",
          "title": "Resolve DAX Business Formula in Dataplex Knowledge Catalog & Gold Views",
          "status": "EXECUTED",
          "latencyMs": 220,
          "detail": "Bound KPI formula: Rate_Card_Giveaway_USD = (standard_rate_usd - negotiated_rate_usd) / standard_rate_usd * net_service_rev_usd"
        },
        {
          "stepOrder": 3,
          "pillar": "PYTHON_WHAT_IF_SANDBOX",
          "title": "Execute Counterfactual What-If / Econometric Regime Simulation",
          "status": "SYNTHESIZED",
          "latencyMs": 410,
          "detail": "Expose via `v_gold_adjusted_yield_dax` in Dataplex Knowledge Catalog with strict semantic definition of Net Service Revenue."
        }
      ],
      "synthesizedAnswer": "### Architectural Synthesis (Q-011 \u2014 Tier 2)\n- **Verdict on Raw Database MCP**: `PARTIAL - Requires Semantic DAX + Gold View`\n- **Diagnosis**: Requires joining rate card baselines to final pricing scenarios while excluding hardware/cloud pass-through revenue.\n- **Recommended Production Mesh**: Expose via `v_gold_adjusted_yield_dax` in Dataplex Knowledge Catalog with strict semantic definition of Net Service Revenue.\n- **Assessment Readiness Confidence**: `79%`",
      "sqlExecuted": "SELECT p.opp_id, o.account_name,\n       p.standard_rate_usd, p.negotiated_rate_usd,\n       ROUND(p.discount_giveaway_pct * 100, 1) AS giveaway_pct,\n       ROUND((p.net_service_rev_usd * p.discount_giveaway_pct) / 1e6, 2) AS giveaway_leakage_millions\nFROM pricing_scenarios p\nJOIN opportunities o ON p.opp_id = o.opp_id\nWHERE p.discount_giveaway_pct >= 0.15\nORDER BY giveaway_leakage_millions DESC;"
    }
  },
  {
    "id": "Q-012",
    "code": "Q-012",
    "priority": "P2-Next",
    "persona": "Global Delivery Commercial Controller",
    "domain": "Sold Margin vs. Delivered EAC Variance",
    "question": "Which accounts exhibit the largest negative gap between Sold Margin in Deal_Pricing_Engine and actual Delivered EAC Margin in Delivery_Governance_Hub?",
    "tier": "TIER_2",
    "tierLabel": "Tier 2 (30%): Semantic Layer (Dataplex KC DAX Formulas) + Pre-Computed Gold Views + Counterfactual Simulator",
    "systemsInvolved": [
      "Deal_Pricing_Engine",
      "Delivery_Governance_Hub",
      "ERP_Financials_Ledger"
    ],
    "blockerFlags": [
      "Incomplete Spec"
    ],
    "confidence_pct": 72,
    "missing_artifacts": [
      "Cross-system entity resolution bridge table mapping pre-sales CRM opp_id to post-sales ERP_Financials_Ledger project WBS codes."
    ],
    "rawDbMcpSufficient": false,
    "dataplexKcCeilingSufficient": true,
    "requiresMultiToolFederation": false,
    "architecturalDiagnosis": "Pre-sales opportunity IDs and post-sales ERP project codes use disparate composite keys across systems; requires pre-joined entity resolution in `v_gold_account_360_health`.",
    "recommendedArchitecture": "Query `v_gold_account_360_health` via MCP Toolbox `get_account_360_composite_health`.",
    "daxOrMetricFormula": {
      "id": "KPI-Q-012",
      "metricName": "Sold Margin vs. Delivered EAC Variance",
      "domain": "Internal Structured (BQ)",
      "daxExpression": "Sold_vs_Delivered_Variance_Bps = d.eac_margin_variance_pct * 10000 // Unbilled_Overrun_Exposure_USD = ABS(d.eac_margin_variance_pct) * p.net_service_rev_usd",
      "canonicalSqlExpression": "SELECT o.account_id, o.account_name, d.rag_status,\n       ROUND(p.adjusted_yield_v4_sigma_capped * 100, 1) AS sold_adj_yield_pct,\n       ROUND(d.eac_margin_variance_pct * 100, 1) AS eac_variance_pct,\n       d.sla_slippage_days,\n       ROUND(ABS(d.eac_margin_variance_pct) * p.net_service_rev_usd / 1e6, 2) AS margin_erosion_millions\nFROM opportunities o\nJOIN pricing_scenarios p ON o.opp_id = p.opp_id\nJOIN delivery_health d ON o.account_id = d.account_id\nWHERE d.eac_margin_variance_pct < 0\nORDER BY d.eac_margin_variance_pct ASC;",
      "dataplexGlossaryTerm": "projects/enterprise-mesh/locations/us/glossaries/commercial-kpi/terms/q_012",
      "sourceSystems": [
        "Deal_Pricing_Engine",
        "Delivery_Governance_Hub",
        "ERP_Financials_Ledger"
      ],
      "grain": "Internal Structured (BQ) // Primary Commercial Entity Grain"
    },
    "genaiToolboxYaml": "  get_account_360_composite_health:\n    kind: bigquery-sql\n    source: enterprise-commercial-bq\n    description: Join pre-sales pricing yield with post-sales delivery EAC margin variance.",
    "bigqueryGoldViewDdl": "-- Canonical BigQuery Gold View for Q-012 (Sold Margin vs. Delivered EAC Variance)\nCREATE OR REPLACE VIEW `enterprise-commercial-mesh.gold_commercial.v_q_012_spine`\nOPTIONS(\n  description=\"Sold Margin vs. Delivered EAC Variance governed by Dataplex Knowledge Catalog.\"\n) AS\nSELECT o.account_id, o.account_name, d.rag_status,\n       ROUND(p.adjusted_yield_v4_sigma_capped * 100, 1) AS sold_adj_yield_pct,\n       ROUND(d.eac_margin_variance_pct * 100, 1) AS eac_variance_pct,\n       d.sla_slippage_days,\n       ROUND(ABS(d.eac_margin_variance_pct) * p.net_service_rev_usd / 1e6, 2) AS margin_erosion_millions\nFROM opportunities o\nJOIN pricing_scenarios p ON o.opp_id = p.opp_id\nJOIN delivery_health d ON o.account_id = d.account_id\nWHERE d.eac_margin_variance_pct < 0\nORDER BY d.eac_margin_variance_pct ASC;",
    "defaultSimulation": {
      "questionId": "Q-012",
      "questionText": "Which accounts exhibit the largest negative gap between Sold Margin in Deal_Pricing_Engine and actual Delivered EAC Margin in Delivery_Governance_Hub?",
      "tier": "TIER_2",
      "complianceStatus": "APPROVED",
      "rawSqlMcpOutcome": "FAILED_HALLUCINATED_METRIC",
      "federatedMeshOutcome": "VERIFIED_SYNTHESIS",
      "totalLatencyMs": 649,
      "traceSteps": [
        {
          "stepOrder": 1,
          "pillar": "PRE_FLIGHT_GOVERNANCE",
          "title": "Pre-Flight Dataplex GenAI License & RBAC Guard",
          "status": "PASSED",
          "latencyMs": 19,
          "detail": "Verified Dataplex governance aspects for sources: Deal_Pricing_Engine, Delivery_Governance_Hub, ERP_Financials_Ledger."
        },
        {
          "stepOrder": 2,
          "pillar": "DATAPLEX_KC_BQCA",
          "title": "Resolve DAX Business Formula in Dataplex Knowledge Catalog & Gold Views",
          "status": "EXECUTED",
          "latencyMs": 220,
          "detail": "Bound KPI formula: Sold_vs_Delivered_Variance_Bps = d.eac_margin_variance_pct * 10000"
        },
        {
          "stepOrder": 3,
          "pillar": "PYTHON_WHAT_IF_SANDBOX",
          "title": "Execute Counterfactual What-If / Econometric Regime Simulation",
          "status": "SYNTHESIZED",
          "latencyMs": 410,
          "detail": "Query `v_gold_account_360_health` via MCP Toolbox `get_account_360_composite_health`."
        }
      ],
      "synthesizedAnswer": "### Architectural Synthesis (Q-012 \u2014 Tier 2)\n- **Verdict on Raw Database MCP**: `PARTIAL - Requires Semantic DAX + Gold View`\n- **Diagnosis**: Pre-sales opportunity IDs and post-sales ERP project codes use disparate composite keys across systems; requires pre-joined entity resolution in `v_gold_account_360_health`.\n- **Recommended Production Mesh**: Query `v_gold_account_360_health` via MCP Toolbox `get_account_360_composite_health`.\n- **Assessment Readiness Confidence**: `72%`",
      "sqlExecuted": "SELECT o.account_id, o.account_name, d.rag_status,\n       ROUND(p.adjusted_yield_v4_sigma_capped * 100, 1) AS sold_adj_yield_pct,\n       ROUND(d.eac_margin_variance_pct * 100, 1) AS eac_variance_pct,\n       d.sla_slippage_days,\n       ROUND(ABS(d.eac_margin_variance_pct) * p.net_service_rev_usd / 1e6, 2) AS margin_erosion_millions\nFROM opportunities o\nJOIN pricing_scenarios p ON o.opp_id = p.opp_id\nJOIN delivery_health d ON o.account_id = d.account_id\nWHERE d.eac_margin_variance_pct < 0\nORDER BY d.eac_margin_variance_pct ASC;"
    }
  },
  {
    "id": "Q-013",
    "code": "Q-013",
    "priority": "P3-Next",
    "persona": "Talent & Pyramid Optimization VP",
    "domain": "Pyramid Leverage & Rate Realization",
    "question": "Simulate the margin impact of shifting 15% of onshore principal hours to nearshore AI-augmented delivery pods across all Stage 3 and Stage 4 opportunities.",
    "tier": "TIER_2",
    "tierLabel": "Tier 2 (30%): Semantic Layer (Dataplex KC DAX Formulas) + Pre-Computed Gold Views + Counterfactual Simulator",
    "systemsInvolved": [
      "Deal_Pricing_Engine",
      "Workforce_Skills_Graph"
    ],
    "blockerFlags": [
      "Counterfactual What-If Simulator"
    ],
    "confidence_pct": 66,
    "missing_artifacts": [
      "Loaded hourly cost rate card by onshore/nearshore/offshore tier in Workforce_Skills_Graph.",
      "Client MSA offshoring restriction flags in CLM_Contract_Vault."
    ],
    "rawDbMcpSufficient": false,
    "dataplexKcCeilingSufficient": true,
    "requiresMultiToolFederation": false,
    "architecturalDiagnosis": "Requires dynamic cost-rate substitution in the pricing model rather than static table retrieval.",
    "recommendedArchitecture": "Invoke the Tier-2 Python Counterfactual Simulator over `pricing_scenarios`.",
    "daxOrMetricFormula": {
      "id": "KPI-Q-013",
      "metricName": "Pyramid Leverage & Rate Realization",
      "domain": "Internal Structured (BQ)",
      "daxExpression": "Pyramid_Mix_Savings_USD = Net_Service_Rev_USD * 0.15 * (1 - Nearshore_Cost_Ratio) // Simulated_Yield_Post_Pyramid = Adjusted_Yield_v4 + 0.032",
      "canonicalSqlExpression": "SELECT o.opp_id, o.account_name, o.stage_name,\n       ROUND(p.adjusted_yield_v4_sigma_capped * 100, 1) AS current_yield_pct,\n       ROUND((p.adjusted_yield_v4_sigma_capped + 0.032) * 100, 1) AS pyramid_shifted_yield_pct,\n       ROUND(p.net_service_rev_usd * 0.032 / 1e6, 2) AS incremental_margin_millions\nFROM opportunities o\nJOIN pricing_scenarios p ON o.opp_id = p.opp_id\nWHERE o.stage_name LIKE 'Stage 3%' OR o.stage_name LIKE 'Stage 4%'\nORDER BY incremental_margin_millions DESC;",
      "dataplexGlossaryTerm": "projects/enterprise-mesh/locations/us/glossaries/commercial-kpi/terms/q_013",
      "sourceSystems": [
        "Deal_Pricing_Engine",
        "Workforce_Skills_Graph"
      ],
      "grain": "Internal Structured (BQ) // Primary Commercial Entity Grain"
    },
    "genaiToolboxYaml": "  simulate_pyramid_mix_shift:\n    kind: bigquery-sql\n    source: enterprise-commercial-bq\n    description: Estimate margin expansion from nearshore pyramid mix optimization.",
    "bigqueryGoldViewDdl": "-- Canonical BigQuery Gold View for Q-013 (Pyramid Leverage & Rate Realization)\nCREATE OR REPLACE VIEW `enterprise-commercial-mesh.gold_commercial.v_q_013_spine`\nOPTIONS(\n  description=\"Pyramid Leverage & Rate Realization governed by Dataplex Knowledge Catalog.\"\n) AS\nSELECT o.opp_id, o.account_name, o.stage_name,\n       ROUND(p.adjusted_yield_v4_sigma_capped * 100, 1) AS current_yield_pct,\n       ROUND((p.adjusted_yield_v4_sigma_capped + 0.032) * 100, 1) AS pyramid_shifted_yield_pct,\n       ROUND(p.net_service_rev_usd * 0.032 / 1e6, 2) AS incremental_margin_millions\nFROM opportunities o\nJOIN pricing_scenarios p ON o.opp_id = p.opp_id\nWHERE o.stage_name LIKE 'Stage 3%' OR o.stage_name LIKE 'Stage 4%'\nORDER BY incremental_margin_millions DESC;",
    "defaultSimulation": {
      "questionId": "Q-013",
      "questionText": "Simulate the margin impact of shifting 15% of onshore principal hours to nearshore AI-augmented delivery pods across all Stage 3 and Stage 4 opportunities.",
      "tier": "TIER_2",
      "complianceStatus": "APPROVED",
      "rawSqlMcpOutcome": "FAILED_HALLUCINATED_METRIC",
      "federatedMeshOutcome": "VERIFIED_SYNTHESIS",
      "totalLatencyMs": 649,
      "traceSteps": [
        {
          "stepOrder": 1,
          "pillar": "PRE_FLIGHT_GOVERNANCE",
          "title": "Pre-Flight Dataplex GenAI License & RBAC Guard",
          "status": "PASSED",
          "latencyMs": 19,
          "detail": "Verified Dataplex governance aspects for sources: Deal_Pricing_Engine, Workforce_Skills_Graph."
        },
        {
          "stepOrder": 2,
          "pillar": "DATAPLEX_KC_BQCA",
          "title": "Resolve DAX Business Formula in Dataplex Knowledge Catalog & Gold Views",
          "status": "EXECUTED",
          "latencyMs": 220,
          "detail": "Bound KPI formula: Pyramid_Mix_Savings_USD = Net_Service_Rev_USD * 0.15 * (1 - Nearshore_Cost_Ratio)"
        },
        {
          "stepOrder": 3,
          "pillar": "PYTHON_WHAT_IF_SANDBOX",
          "title": "Execute Counterfactual What-If / Econometric Regime Simulation",
          "status": "SYNTHESIZED",
          "latencyMs": 410,
          "detail": "Invoke the Tier-2 Python Counterfactual Simulator over `pricing_scenarios`."
        }
      ],
      "synthesizedAnswer": "### Architectural Synthesis (Q-013 \u2014 Tier 2)\n- **Verdict on Raw Database MCP**: `PARTIAL - Requires Counterfactual Simulator`\n- **Diagnosis**: Requires dynamic cost-rate substitution in the pricing model rather than static table retrieval.\n- **Recommended Production Mesh**: Invoke the Tier-2 Python Counterfactual Simulator over `pricing_scenarios`.\n- **Assessment Readiness Confidence**: `66%`",
      "sqlExecuted": "SELECT o.opp_id, o.account_name, o.stage_name,\n       ROUND(p.adjusted_yield_v4_sigma_capped * 100, 1) AS current_yield_pct,\n       ROUND((p.adjusted_yield_v4_sigma_capped + 0.032) * 100, 1) AS pyramid_shifted_yield_pct,\n       ROUND(p.net_service_rev_usd * 0.032 / 1e6, 2) AS incremental_margin_millions\nFROM opportunities o\nJOIN pricing_scenarios p ON o.opp_id = p.opp_id\nWHERE o.stage_name LIKE 'Stage 3%' OR o.stage_name LIKE 'Stage 4%'\nORDER BY incremental_margin_millions DESC;"
    }
  },
  {
    "id": "Q-014",
    "code": "Q-014",
    "priority": "P1-Now",
    "persona": "Strategic Account Executive",
    "domain": "Client AI Self-Sufficiency & Insourcing Risk",
    "question": "Which top accounts show high 'AI Self-Sufficiency / Insourcing Risk' based on external ML engineering hiring telemetry (`Tech_Stack_Telemetry_Feed`) combined with executive visit debrief notes (`Customer_Visit_Logs`), and how much active TCV is exposed?",
    "tier": "TIER_3",
    "tierLabel": "Tier 3 (49%): Federated Multi-Tool Agent (Structured SQL + Unstructured CLM/Visit RAG + External Market Intelligence APIs)",
    "systemsInvolved": [
      "CRM_Opportunity_Spine",
      "Tech_Stack_Telemetry_Feed",
      "Customer_Visit_Logs"
    ],
    "blockerFlags": [
      "External 3P Market API",
      "Hidden Unstructured Notes"
    ],
    "confidence_pct": 48,
    "missing_artifacts": [
      "Live API schema and entity-matching D-U-N-S bridge for Tech_Stack_Telemetry_Feed.",
      "Vector embedding index over unstructured executive debriefs in Customer_Visit_Logs."
    ],
    "rawDbMcpSufficient": false,
    "dataplexKcCeilingSufficient": false,
    "requiresMultiToolFederation": true,
    "architecturalDiagnosis": "Internal CRM tables have zero visibility into a client's external ML job postings (`Tech_Stack_Telemetry_Feed`) or qualitative CTO statements in `Customer_Visit_Logs`.",
    "recommendedArchitecture": "Federated ADK Agent: (1) Query `CRM_Opportunity_Spine` via MCP Toolbox, (2) Fetch external hiring telemetry from `Tech_Stack_Telemetry_Feed`, (3) Run semantic search over `Customer_Visit_Logs`.",
    "daxOrMetricFormula": {
      "id": "KPI-Q-014",
      "metricName": "Client AI Self-Sufficiency & Insourcing Risk",
      "domain": "Hybrid (BQ + External/Unstructured)",
      "daxExpression": "AI_Insourcing_Exposure_USD = SUM(tcv_usd WHERE ai_self_sufficiency_index > 0.65) // Composite_Insourcing_Risk_Score = 0.6 * ai_self_sufficiency_index + 0.4 * Unstructured_Sentiment_Risk",
      "canonicalSqlExpression": "SELECT o.opp_id, o.account_name, ROUND(o.tcv_usd / 1e6, 2) AS tcv_m,\n       m.ai_self_sufficiency_index, m.signal_summary,\n       u.extracted_risk_tag, u.note_snippet\nFROM opportunities o\nJOIN external_market_signals m ON o.account_id = m.account_id\nLEFT JOIN unstructured_deal_notes u ON o.opp_id = u.opp_id\nWHERE m.ai_self_sufficiency_index >= 0.60\nORDER BY m.ai_self_sufficiency_index DESC;",
      "dataplexGlossaryTerm": "projects/enterprise-mesh/locations/us/glossaries/commercial-kpi/terms/q_014",
      "sourceSystems": [
        "CRM_Opportunity_Spine",
        "Tech_Stack_Telemetry_Feed",
        "Customer_Visit_Logs"
      ],
      "grain": "Hybrid (BQ + External/Unstructured) // Primary Commercial Entity Grain"
    },
    "genaiToolboxYaml": "  get_ai_insourcing_risk_signals:\n    kind: bigquery-sql\n    source: enterprise-commercial-bq\n    description: Federate internal opportunity TCV with external tech-stack telemetry and visit notes.",
    "bigqueryGoldViewDdl": "-- Canonical BigQuery Gold View for Q-014 (Client AI Self-Sufficiency & Insourcing Risk)\nCREATE OR REPLACE VIEW `enterprise-commercial-mesh.gold_commercial.v_q_014_spine`\nOPTIONS(\n  description=\"Client AI Self-Sufficiency & Insourcing Risk governed by Dataplex Knowledge Catalog.\"\n) AS\nSELECT o.opp_id, o.account_name, ROUND(o.tcv_usd / 1e6, 2) AS tcv_m,\n       m.ai_self_sufficiency_index, m.signal_summary,\n       u.extracted_risk_tag, u.note_snippet\nFROM opportunities o\nJOIN external_market_signals m ON o.account_id = m.account_id\nLEFT JOIN unstructured_deal_notes u ON o.opp_id = u.opp_id\nWHERE m.ai_self_sufficiency_index >= 0.60\nORDER BY m.ai_self_sufficiency_index DESC;",
    "defaultSimulation": {
      "questionId": "Q-014",
      "questionText": "Which top accounts show high 'AI Self-Sufficiency / Insourcing Risk' based on external ML engineering hiring telemetry (`Tech_Stack_Telemetry_Feed`) combined with executive visit debrief notes (`Customer_Visit_Logs`), and how much active TCV is exposed?",
      "tier": "TIER_3",
      "complianceStatus": "APPROVED",
      "rawSqlMcpOutcome": "FAILED_HALLUCINATED_METRIC",
      "federatedMeshOutcome": "VERIFIED_SYNTHESIS",
      "totalLatencyMs": 949,
      "traceSteps": [
        {
          "stepOrder": 1,
          "pillar": "PRE_FLIGHT_GOVERNANCE",
          "title": "Pre-Flight Dataplex GenAI License & RBAC Guard",
          "status": "PASSED",
          "latencyMs": 19,
          "detail": "Verified Dataplex governance aspects for sources: CRM_Opportunity_Spine, Tech_Stack_Telemetry_Feed, Customer_Visit_Logs."
        },
        {
          "stepOrder": 2,
          "pillar": "GENAI_TOOLBOX_MCP",
          "title": "Fetch Structured Anchor Cohort from BigQuery Gold Spine",
          "status": "EXECUTED",
          "latencyMs": 290,
          "detail": "Queried structured keys from CRM_Opportunity_Spine, Tech_Stack_Telemetry_Feed."
        },
        {
          "stepOrder": 3,
          "pillar": "VERTEX_UNSTRUCTURED_RAG",
          "title": "Federate Unstructured CLM_Contract_Vault / Customer_Visit_Logs & External Market APIs",
          "status": "SYNTHESIZED",
          "latencyMs": 640,
          "detail": "Federated ADK Agent: (1) Query `CRM_Opportunity_Spine` via MCP Toolbox, (2) Fetch external hiring telemetry from `Tech_Stack_Telemetry_Feed`, (3) Run semantic search over `Customer_Visit_Logs`."
        }
      ],
      "synthesizedAnswer": "### Architectural Synthesis (Q-014 \u2014 Tier 3)\n- **Verdict on Raw Database MCP**: `FAIL - Requires Unstructured RAG + 3P API`\n- **Diagnosis**: Internal CRM tables have zero visibility into a client's external ML job postings (`Tech_Stack_Telemetry_Feed`) or qualitative CTO statements in `Customer_Visit_Logs`.\n- **Recommended Production Mesh**: Federated ADK Agent: (1) Query `CRM_Opportunity_Spine` via MCP Toolbox, (2) Fetch external hiring telemetry from `Tech_Stack_Telemetry_Feed`, (3) Run semantic search over `Customer_Visit_Logs`.\n- **Assessment Readiness Confidence**: `48%`",
      "sqlExecuted": "SELECT o.opp_id, o.account_name, ROUND(o.tcv_usd / 1e6, 2) AS tcv_m,\n       m.ai_self_sufficiency_index, m.signal_summary,\n       u.extracted_risk_tag, u.note_snippet\nFROM opportunities o\nJOIN external_market_signals m ON o.account_id = m.account_id\nLEFT JOIN unstructured_deal_notes u ON o.opp_id = u.opp_id\nWHERE m.ai_self_sufficiency_index >= 0.60\nORDER BY m.ai_self_sufficiency_index DESC;"
    }
  },
  {
    "id": "Q-015",
    "code": "Q-015",
    "priority": "P1-Now",
    "persona": "Commercial Legal & Pricing Counsel",
    "domain": "Contractual COLA Caps & Toxic Clauses",
    "question": "Cross-reference our active Stage 3-4 deals against executed MSAs in `CLM_Contract_Vault` to identify accounts where COLA inflation caps (<3%) or termination-for-convenience clauses threaten Adjusted Yield v4.",
    "tier": "TIER_3",
    "tierLabel": "Tier 3 (49%): Federated Multi-Tool Agent (Structured SQL + Unstructured CLM/Visit RAG + External Market Intelligence APIs)",
    "systemsInvolved": [
      "Deal_Pricing_Engine",
      "CLM_Contract_Vault",
      "CRM_Opportunity_Spine"
    ],
    "blockerFlags": [
      "Hidden Unstructured Notes"
    ],
    "confidence_pct": 54,
    "missing_artifacts": [
      "Document AI / Vertex RAG chunking pipeline over executed PDF MSAs and SOW amendments in CLM_Contract_Vault.",
      "Structured metadata extraction schema for COLA cap % and termination notice days."
    ],
    "rawDbMcpSufficient": false,
    "dataplexKcCeilingSufficient": false,
    "requiresMultiToolFederation": true,
    "architecturalDiagnosis": "COLA caps, MFN clauses, and termination-for-convenience penalties live inside unstructured PDF contract clauses in `CLM_Contract_Vault`, not in structured ERP columns.",
    "recommendedArchitecture": "Hybrid Retrieval: MCP Toolbox fetches deal margins from `Deal_Pricing_Engine` while Vertex AI RAG extracts legal clauses from `CLM_Contract_Vault`.",
    "daxOrMetricFormula": {
      "id": "KPI-Q-015",
      "metricName": "Contractual COLA Caps & Toxic Clauses",
      "domain": "Hybrid (BQ + External/Unstructured)",
      "daxExpression": "Inflation_Unrecovered_Bps = MAX(0, Regional_Wage_Inflation_Pct - MSA_COLA_Cap_Pct) * 10000",
      "canonicalSqlExpression": "SELECT o.opp_id, o.account_name, o.stage_name,\n       ROUND(o.tcv_usd / 1e6, 2) AS tcv_m,\n       ROUND(p.adjusted_yield_v4_sigma_capped * 100, 1) AS adj_yield_pct,\n       u.extracted_risk_tag, u.note_snippet\nFROM opportunities o\nJOIN pricing_scenarios p ON o.opp_id = p.opp_id\nJOIN unstructured_deal_notes u ON o.opp_id = u.opp_id\nWHERE u.source_system = 'CLM_Contract_Vault';",
      "dataplexGlossaryTerm": "projects/enterprise-mesh/locations/us/glossaries/commercial-kpi/terms/q_015",
      "sourceSystems": [
        "Deal_Pricing_Engine",
        "CLM_Contract_Vault",
        "CRM_Opportunity_Spine"
      ],
      "grain": "Hybrid (BQ + External/Unstructured) // Primary Commercial Entity Grain"
    },
    "genaiToolboxYaml": "  search_clm_contract_clauses:\n    kind: bigquery-sql\n    source: enterprise-commercial-bq\n    description: Retrieve extracted MSA/SOW risk clauses joined with deal pricing scenarios.",
    "bigqueryGoldViewDdl": "-- Canonical BigQuery Gold View for Q-015 (Contractual COLA Caps & Toxic Clauses)\nCREATE OR REPLACE VIEW `enterprise-commercial-mesh.gold_commercial.v_q_015_spine`\nOPTIONS(\n  description=\"Contractual COLA Caps & Toxic Clauses governed by Dataplex Knowledge Catalog.\"\n) AS\nSELECT o.opp_id, o.account_name, o.stage_name,\n       ROUND(o.tcv_usd / 1e6, 2) AS tcv_m,\n       ROUND(p.adjusted_yield_v4_sigma_capped * 100, 1) AS adj_yield_pct,\n       u.extracted_risk_tag, u.note_snippet\nFROM opportunities o\nJOIN pricing_scenarios p ON o.opp_id = p.opp_id\nJOIN unstructured_deal_notes u ON o.opp_id = u.opp_id\nWHERE u.source_system = 'CLM_Contract_Vault';",
    "defaultSimulation": {
      "questionId": "Q-015",
      "questionText": "Cross-reference our active Stage 3-4 deals against executed MSAs in `CLM_Contract_Vault` to identify accounts where COLA inflation caps (<3%) or termination-for-convenience clauses threaten Adjusted Yield v4.",
      "tier": "TIER_3",
      "complianceStatus": "APPROVED",
      "rawSqlMcpOutcome": "FAILED_HALLUCINATED_METRIC",
      "federatedMeshOutcome": "VERIFIED_SYNTHESIS",
      "totalLatencyMs": 949,
      "traceSteps": [
        {
          "stepOrder": 1,
          "pillar": "PRE_FLIGHT_GOVERNANCE",
          "title": "Pre-Flight Dataplex GenAI License & RBAC Guard",
          "status": "PASSED",
          "latencyMs": 19,
          "detail": "Verified Dataplex governance aspects for sources: Deal_Pricing_Engine, CLM_Contract_Vault, CRM_Opportunity_Spine."
        },
        {
          "stepOrder": 2,
          "pillar": "GENAI_TOOLBOX_MCP",
          "title": "Fetch Structured Anchor Cohort from BigQuery Gold Spine",
          "status": "EXECUTED",
          "latencyMs": 290,
          "detail": "Queried structured keys from Deal_Pricing_Engine, CLM_Contract_Vault."
        },
        {
          "stepOrder": 3,
          "pillar": "VERTEX_UNSTRUCTURED_RAG",
          "title": "Federate Unstructured CLM_Contract_Vault / Customer_Visit_Logs & External Market APIs",
          "status": "SYNTHESIZED",
          "latencyMs": 640,
          "detail": "Hybrid Retrieval: MCP Toolbox fetches deal margins from `Deal_Pricing_Engine` while Vertex AI RAG extracts legal clauses from `CLM_Contract_Vault`."
        }
      ],
      "synthesizedAnswer": "### Architectural Synthesis (Q-015 \u2014 Tier 3)\n- **Verdict on Raw Database MCP**: `FAIL - Requires Unstructured RAG + 3P API`\n- **Diagnosis**: COLA caps, MFN clauses, and termination-for-convenience penalties live inside unstructured PDF contract clauses in `CLM_Contract_Vault`, not in structured ERP columns.\n- **Recommended Production Mesh**: Hybrid Retrieval: MCP Toolbox fetches deal margins from `Deal_Pricing_Engine` while Vertex AI RAG extracts legal clauses from `CLM_Contract_Vault`.\n- **Assessment Readiness Confidence**: `54%`",
      "sqlExecuted": "SELECT o.opp_id, o.account_name, o.stage_name,\n       ROUND(o.tcv_usd / 1e6, 2) AS tcv_m,\n       ROUND(p.adjusted_yield_v4_sigma_capped * 100, 1) AS adj_yield_pct,\n       u.extracted_risk_tag, u.note_snippet\nFROM opportunities o\nJOIN pricing_scenarios p ON o.opp_id = p.opp_id\nJOIN unstructured_deal_notes u ON o.opp_id = u.opp_id\nWHERE u.source_system = 'CLM_Contract_Vault';"
    }
  },
  {
    "id": "Q-016",
    "code": "Q-016",
    "priority": "P1-Now",
    "persona": "Competitive Intelligence & Pricing Lead",
    "domain": "Competitor Rate Benchmarking (Compliance Guard)",
    "question": "Synthesize competitor hourly rate cards and market-share tables from `Analyst_Benchmark_Feed_Unlicensed` to recommend unit-rate cuts on our top 5 deals.",
    "tier": "TIER_3",
    "tierLabel": "Tier 3 (49%): Federated Multi-Tool Agent (Structured SQL + Unstructured CLM/Visit RAG + External Market Intelligence APIs)",
    "systemsInvolved": [
      "Analyst_Benchmark_Feed_Unlicensed",
      "Deal_Pricing_Engine"
    ],
    "blockerFlags": [
      "License Compliance Blocker",
      "External 3P Market API"
    ],
    "confidence_pct": 15,
    "missing_artifacts": [
      "LEGAL BLOCKER: Analyst_Benchmark_Feed_Unlicensed has GenAI_Usage_Rights = False (zero LLM ingestion permitted).",
      "Requires clean-room aggregated benchmark substitution or commercial contract amendment with 3P vendor."
    ],
    "rawDbMcpSufficient": false,
    "dataplexKcCeilingSufficient": false,
    "requiresMultiToolFederation": true,
    "architecturalDiagnosis": "CRITICAL COMPLIANCE VIOLATION: `Analyst_Benchmark_Feed_Unlicensed` carries `genai_usage_rights = False` in Dataplex Knowledge Catalog. Passing its rows into an LLM prompt violates 3P syndication licensing.",
    "recommendedArchitecture": "Pre-flight Dataplex Governance Guard (`check_source_genai_compliance`) intercepts the query, blocks LLM ingestion of `Analyst_Benchmark_Feed_Unlicensed`, and substitutes clean internal `Deal_Pricing_Engine` historical win/loss elasticity.",
    "daxOrMetricFormula": {
      "id": "KPI-Q-016",
      "metricName": "Competitor Rate Benchmarking (Compliance Guard)",
      "domain": "External / Market Only",
      "daxExpression": "Governance_Compliance_Check = MIN(genai_usage_rights) OVER (Selected_Sources)",
      "canonicalSqlExpression": "SELECT source_id, source_name, category, genai_usage_rights, pii_classification, steward_team, notes\nFROM data_source_governance\nWHERE source_name = 'Analyst_Benchmark_Feed_Unlicensed';",
      "dataplexGlossaryTerm": "projects/enterprise-mesh/locations/us/glossaries/commercial-kpi/terms/q_016",
      "sourceSystems": [
        "Analyst_Benchmark_Feed_Unlicensed",
        "Deal_Pricing_Engine"
      ],
      "grain": "External / Market Only // Primary Commercial Entity Grain"
    },
    "genaiToolboxYaml": "  check_source_genai_compliance:\n    kind: bigquery-sql\n    source: enterprise-commercial-bq\n    description: Verify Dataplex GenAI usage rights before routing data to Vertex AI LLM prompts.",
    "bigqueryGoldViewDdl": "-- Canonical BigQuery Gold View for Q-016 (Competitor Rate Benchmarking (Compliance Guard))\nCREATE OR REPLACE VIEW `enterprise-commercial-mesh.gold_commercial.v_q_016_spine`\nOPTIONS(\n  description=\"Competitor Rate Benchmarking (Compliance Guard) governed by Dataplex Knowledge Catalog.\"\n) AS\nSELECT source_id, source_name, category, genai_usage_rights, pii_classification, steward_team, notes\nFROM data_source_governance\nWHERE source_name = 'Analyst_Benchmark_Feed_Unlicensed';",
    "defaultSimulation": {
      "questionId": "Q-016",
      "questionText": "Synthesize competitor hourly rate cards and market-share tables from `Analyst_Benchmark_Feed_Unlicensed` to recommend unit-rate cuts on our top 5 deals.",
      "tier": "TIER_3",
      "complianceStatus": "BLOCKED_UNLICENSED_3P_FEED",
      "rawSqlMcpOutcome": "BLOCKED_LICENSE",
      "federatedMeshOutcome": "GOVERNANCE_SAFE_FALLBACK",
      "totalLatencyMs": 949,
      "traceSteps": [
        {
          "stepOrder": 1,
          "pillar": "PRE_FLIGHT_GOVERNANCE",
          "title": "Pre-Flight Dataplex GenAI License & RBAC Guard",
          "status": "BLOCKED",
          "latencyMs": 19,
          "detail": "INTERCEPTED: Source Analyst_Benchmark_Feed_Unlicensed has genai_usage_rights=0. Blocked raw table egress and substituted governed 1P telemetry."
        },
        {
          "stepOrder": 2,
          "pillar": "GENAI_TOOLBOX_MCP",
          "title": "Fetch Structured Anchor Cohort from BigQuery Gold Spine",
          "status": "EXECUTED",
          "latencyMs": 290,
          "detail": "Queried structured keys from Analyst_Benchmark_Feed_Unlicensed, Deal_Pricing_Engine."
        },
        {
          "stepOrder": 3,
          "pillar": "VERTEX_UNSTRUCTURED_RAG",
          "title": "Federate Unstructured CLM_Contract_Vault / Customer_Visit_Logs & External Market APIs",
          "status": "SYNTHESIZED",
          "latencyMs": 640,
          "detail": "Pre-flight Dataplex Governance Guard (`check_source_genai_compliance`) intercepts the query, blocks LLM ingestion of `Analyst_Benchmark_Feed_Unlicensed`, and substitutes clean internal `Deal_Pricing_Engine` historical win/loss elasticity."
        }
      ],
      "synthesizedAnswer": "### Architectural Synthesis (Q-016 \u2014 Tier 3)\n- **Verdict on Raw Database MCP**: `BLOCKED - GenAI License Compliance Guard`\n- **Diagnosis**: CRITICAL COMPLIANCE VIOLATION: `Analyst_Benchmark_Feed_Unlicensed` carries `genai_usage_rights = False` in Dataplex Knowledge Catalog. Passing its rows into an LLM prompt violates 3P syndication licensing.\n- **Recommended Production Mesh**: Pre-flight Dataplex Governance Guard (`check_source_genai_compliance`) intercepts the query, blocks LLM ingestion of `Analyst_Benchmark_Feed_Unlicensed`, and substitutes clean internal `Deal_Pricing_Engine` historical win/loss elasticity.\n- **Assessment Readiness Confidence**: `15%`",
      "sqlExecuted": "SELECT source_id, source_name, category, genai_usage_rights, pii_classification, steward_team, notes\nFROM data_source_governance\nWHERE source_name = 'Analyst_Benchmark_Feed_Unlicensed';"
    }
  },
  {
    "id": "Q-017",
    "code": "Q-017",
    "priority": "P1-Now",
    "persona": "Mega-Deal Negotiation Strategist",
    "domain": "Game-Theoretic Schelling Focal Point Synthesis",
    "question": "For our \u20ac128.5M Nordic Telecom deal (OPP-9016), combine our internal floor margin (`Deal_Pricing_Engine`), sovereign NOC differentiation notes (`Customer_Visit_Logs`), and external buyer intent (`Buyer_Intent_Signal_Stream`) to compute the Schelling negotiation focal point.",
    "tier": "TIER_3",
    "tierLabel": "Tier 3 (49%): Federated Multi-Tool Agent (Structured SQL + Unstructured CLM/Visit RAG + External Market Intelligence APIs)",
    "systemsInvolved": [
      "Deal_Pricing_Engine",
      "Customer_Visit_Logs",
      "Buyer_Intent_Signal_Stream"
    ],
    "blockerFlags": [
      "Missing ML Model in DB",
      "Hidden Unstructured Notes",
      "External 3P Market API"
    ],
    "confidence_pct": 44,
    "missing_artifacts": [
      "Game-theoretic Nash/Schelling bargaining utility function parameters (client walk-away reservation price vs. switching cost).",
      "Real-time feed integration for Buyer_Intent_Signal_Stream and Customer_Visit_Logs."
    ],
    "rawDbMcpSufficient": false,
    "dataplexKcCeilingSufficient": false,
    "requiresMultiToolFederation": true,
    "architecturalDiagnosis": "Computing a bargaining focal point requires synthesizing structured floor margins, unstructured CIO sentiment from visit notes, and external buyer urgency scores.",
    "recommendedArchitecture": "Federated Multi-Tool Agent orchestrates SQL pricing lookup + RAG visit note extraction + Game-Theoretic Nash/Schelling solver in Python.",
    "daxOrMetricFormula": {
      "id": "KPI-Q-017",
      "metricName": "Game-Theoretic Schelling Focal Point Synthesis",
      "domain": "Hybrid (BQ + External/Unstructured)",
      "daxExpression": "Schelling_Focal_Discount_Pct = (Client_Target_Discount + Provider_Walkaway_Floor) / 2 * Differentiation_Weight // Expected_Value_At_Focal_Point = TCV_Focal * P(Win | Focal_Discount) * Yield_Focal",
      "canonicalSqlExpression": "SELECT o.opp_id, o.account_name, o.tcv_usd,\n       p.standard_rate_usd, p.negotiated_rate_usd, p.adjusted_yield_v4_sigma_capped,\n       u.note_snippet AS cio_visit_intelligence,\n       m.intent_surge_score, m.signal_summary\nFROM opportunities o\nJOIN pricing_scenarios p ON o.opp_id = p.opp_id\nLEFT JOIN unstructured_deal_notes u ON o.opp_id = u.opp_id\nLEFT JOIN external_market_signals m ON o.account_id = m.account_id\nWHERE o.opp_id = 'OPP-9016';",
      "dataplexGlossaryTerm": "projects/enterprise-mesh/locations/us/glossaries/commercial-kpi/terms/q_017",
      "sourceSystems": [
        "Deal_Pricing_Engine",
        "Customer_Visit_Logs",
        "Buyer_Intent_Signal_Stream"
      ],
      "grain": "Hybrid (BQ + External/Unstructured) // Primary Commercial Entity Grain"
    },
    "genaiToolboxYaml": "  get_schelling_negotiation_context:\n    kind: bigquery-sql\n    source: enterprise-commercial-bq\n    description: Assemble pricing floor, CIO visit notes, and intent surge for negotiation modeling.",
    "bigqueryGoldViewDdl": "-- Canonical BigQuery Gold View for Q-017 (Game-Theoretic Schelling Focal Point Synthesis)\nCREATE OR REPLACE VIEW `enterprise-commercial-mesh.gold_commercial.v_q_017_spine`\nOPTIONS(\n  description=\"Game-Theoretic Schelling Focal Point Synthesis governed by Dataplex Knowledge Catalog.\"\n) AS\nSELECT o.opp_id, o.account_name, o.tcv_usd,\n       p.standard_rate_usd, p.negotiated_rate_usd, p.adjusted_yield_v4_sigma_capped,\n       u.note_snippet AS cio_visit_intelligence,\n       m.intent_surge_score, m.signal_summary\nFROM opportunities o\nJOIN pricing_scenarios p ON o.opp_id = p.opp_id\nLEFT JOIN unstructured_deal_notes u ON o.opp_id = u.opp_id\nLEFT JOIN external_market_signals m ON o.account_id = m.account_id\nWHERE o.opp_id = 'OPP-9016';",
    "defaultSimulation": {
      "questionId": "Q-017",
      "questionText": "For our \u20ac128.5M Nordic Telecom deal (OPP-9016), combine our internal floor margin (`Deal_Pricing_Engine`), sovereign NOC differentiation notes (`Customer_Visit_Logs`), and external buyer intent (`Buyer_Intent_Signal_Stream`) to compute the Schelling negotiation focal point.",
      "tier": "TIER_3",
      "complianceStatus": "APPROVED",
      "rawSqlMcpOutcome": "FAILED_HALLUCINATED_METRIC",
      "federatedMeshOutcome": "VERIFIED_SYNTHESIS",
      "totalLatencyMs": 949,
      "traceSteps": [
        {
          "stepOrder": 1,
          "pillar": "PRE_FLIGHT_GOVERNANCE",
          "title": "Pre-Flight Dataplex GenAI License & RBAC Guard",
          "status": "PASSED",
          "latencyMs": 19,
          "detail": "Verified Dataplex governance aspects for sources: Deal_Pricing_Engine, Customer_Visit_Logs, Buyer_Intent_Signal_Stream."
        },
        {
          "stepOrder": 2,
          "pillar": "GENAI_TOOLBOX_MCP",
          "title": "Fetch Structured Anchor Cohort from BigQuery Gold Spine",
          "status": "EXECUTED",
          "latencyMs": 290,
          "detail": "Queried structured keys from Deal_Pricing_Engine, Customer_Visit_Logs."
        },
        {
          "stepOrder": 3,
          "pillar": "VERTEX_UNSTRUCTURED_RAG",
          "title": "Federate Unstructured CLM_Contract_Vault / Customer_Visit_Logs & External Market APIs",
          "status": "SYNTHESIZED",
          "latencyMs": 640,
          "detail": "Federated Multi-Tool Agent orchestrates SQL pricing lookup + RAG visit note extraction + Game-Theoretic Nash/Schelling solver in Python."
        }
      ],
      "synthesizedAnswer": "### Architectural Synthesis (Q-017 \u2014 Tier 3)\n- **Verdict on Raw Database MCP**: `FAIL - Requires Unstructured RAG + 3P API`\n- **Diagnosis**: Computing a bargaining focal point requires synthesizing structured floor margins, unstructured CIO sentiment from visit notes, and external buyer urgency scores.\n- **Recommended Production Mesh**: Federated Multi-Tool Agent orchestrates SQL pricing lookup + RAG visit note extraction + Game-Theoretic Nash/Schelling solver in Python.\n- **Assessment Readiness Confidence**: `44%`",
      "sqlExecuted": "SELECT o.opp_id, o.account_name, o.tcv_usd,\n       p.standard_rate_usd, p.negotiated_rate_usd, p.adjusted_yield_v4_sigma_capped,\n       u.note_snippet AS cio_visit_intelligence,\n       m.intent_surge_score, m.signal_summary\nFROM opportunities o\nJOIN pricing_scenarios p ON o.opp_id = p.opp_id\nLEFT JOIN unstructured_deal_notes u ON o.opp_id = u.opp_id\nLEFT JOIN external_market_signals m ON o.account_id = m.account_id\nWHERE o.opp_id = 'OPP-9016';"
    }
  },
  {
    "id": "Q-018",
    "code": "Q-018",
    "priority": "P2-Next",
    "persona": "Account Growth Director",
    "domain": "White-Space ABM & Intent Surge Matching",
    "question": "Which accounts have an external `Buyer_Intent_Signal_Stream` surge score above 85 or strong R&D capex expansion in `Market_Financials_API`, and how does that compare to our current pipeline stage and delivery health?",
    "tier": "TIER_3",
    "tierLabel": "Tier 3 (49%): Federated Multi-Tool Agent (Structured SQL + Unstructured CLM/Visit RAG + External Market Intelligence APIs)",
    "systemsInvolved": [
      "Buyer_Intent_Signal_Stream",
      "Market_Financials_API",
      "CRM_Opportunity_Spine",
      "Delivery_Governance_Hub"
    ],
    "blockerFlags": [
      "External 3P Market API"
    ],
    "confidence_pct": 56,
    "missing_artifacts": [
      "3P topic taxonomy mapping between Buyer_Intent_Signal_Stream surge topics and internal service_line catalog.",
      "SEC CIK / ticker to CRM account_id cross-walk for Market_Financials_API."
    ],
    "rawDbMcpSufficient": false,
    "dataplexKcCeilingSufficient": false,
    "requiresMultiToolFederation": true,
    "architecturalDiagnosis": "Requires joining external B2B intent streams and quarterly 10-Q R&D ratios with internal CRM and delivery CSAT scores.",
    "recommendedArchitecture": "Federated Agent queries `external_market_signals` and joins with `v_gold_account_360_health`.",
    "daxOrMetricFormula": {
      "id": "KPI-Q-018",
      "metricName": "White-Space ABM & Intent Surge Matching",
      "domain": "Hybrid (BQ + External/Unstructured)",
      "daxExpression": "Account_Expansion_Propensity = 0.5 * (intent_surge_score / 100) + 0.3 * client_rd_intensity_pct + 0.2 * csat_index",
      "canonicalSqlExpression": "SELECT o.account_name, o.stage_name, ROUND(o.tcv_usd / 1e6, 2) AS tcv_m,\n       d.rag_status, d.csat_score,\n       m.signal_source, m.intent_surge_score,\n       ROUND(m.client_rd_intensity_pct * 100, 1) AS rd_intensity_pct,\n       m.signal_summary\nFROM opportunities o\nJOIN delivery_health d ON o.account_id = d.account_id\nJOIN external_market_signals m ON o.account_id = m.account_id\nWHERE m.intent_surge_score >= 85\nORDER BY m.intent_surge_score DESC;",
      "dataplexGlossaryTerm": "projects/enterprise-mesh/locations/us/glossaries/commercial-kpi/terms/q_018",
      "sourceSystems": [
        "Buyer_Intent_Signal_Stream",
        "Market_Financials_API",
        "CRM_Opportunity_Spine",
        "Delivery_Governance_Hub"
      ],
      "grain": "Hybrid (BQ + External/Unstructured) // Primary Commercial Entity Grain"
    },
    "genaiToolboxYaml": "  get_intent_surge_whitespace_accounts:\n    kind: bigquery-sql\n    source: enterprise-commercial-bq\n    description: Match external buyer intent surge and 10-Q R&D signals with internal delivery health.",
    "bigqueryGoldViewDdl": "-- Canonical BigQuery Gold View for Q-018 (White-Space ABM & Intent Surge Matching)\nCREATE OR REPLACE VIEW `enterprise-commercial-mesh.gold_commercial.v_q_018_spine`\nOPTIONS(\n  description=\"White-Space ABM & Intent Surge Matching governed by Dataplex Knowledge Catalog.\"\n) AS\nSELECT o.account_name, o.stage_name, ROUND(o.tcv_usd / 1e6, 2) AS tcv_m,\n       d.rag_status, d.csat_score,\n       m.signal_source, m.intent_surge_score,\n       ROUND(m.client_rd_intensity_pct * 100, 1) AS rd_intensity_pct,\n       m.signal_summary\nFROM opportunities o\nJOIN delivery_health d ON o.account_id = d.account_id\nJOIN external_market_signals m ON o.account_id = m.account_id\nWHERE m.intent_surge_score >= 85\nORDER BY m.intent_surge_score DESC;",
    "defaultSimulation": {
      "questionId": "Q-018",
      "questionText": "Which accounts have an external `Buyer_Intent_Signal_Stream` surge score above 85 or strong R&D capex expansion in `Market_Financials_API`, and how does that compare to our current pipeline stage and delivery health?",
      "tier": "TIER_3",
      "complianceStatus": "APPROVED",
      "rawSqlMcpOutcome": "FAILED_HALLUCINATED_METRIC",
      "federatedMeshOutcome": "VERIFIED_SYNTHESIS",
      "totalLatencyMs": 949,
      "traceSteps": [
        {
          "stepOrder": 1,
          "pillar": "PRE_FLIGHT_GOVERNANCE",
          "title": "Pre-Flight Dataplex GenAI License & RBAC Guard",
          "status": "PASSED",
          "latencyMs": 19,
          "detail": "Verified Dataplex governance aspects for sources: Buyer_Intent_Signal_Stream, Market_Financials_API, CRM_Opportunity_Spine, Delivery_Governance_Hub."
        },
        {
          "stepOrder": 2,
          "pillar": "GENAI_TOOLBOX_MCP",
          "title": "Fetch Structured Anchor Cohort from BigQuery Gold Spine",
          "status": "EXECUTED",
          "latencyMs": 290,
          "detail": "Queried structured keys from Buyer_Intent_Signal_Stream, Market_Financials_API."
        },
        {
          "stepOrder": 3,
          "pillar": "VERTEX_UNSTRUCTURED_RAG",
          "title": "Federate Unstructured CLM_Contract_Vault / Customer_Visit_Logs & External Market APIs",
          "status": "SYNTHESIZED",
          "latencyMs": 640,
          "detail": "Federated Agent queries `external_market_signals` and joins with `v_gold_account_360_health`."
        }
      ],
      "synthesizedAnswer": "### Architectural Synthesis (Q-018 \u2014 Tier 3)\n- **Verdict on Raw Database MCP**: `FAIL - Requires Unstructured RAG + 3P API`\n- **Diagnosis**: Requires joining external B2B intent streams and quarterly 10-Q R&D ratios with internal CRM and delivery CSAT scores.\n- **Recommended Production Mesh**: Federated Agent queries `external_market_signals` and joins with `v_gold_account_360_health`.\n- **Assessment Readiness Confidence**: `56%`",
      "sqlExecuted": "SELECT o.account_name, o.stage_name, ROUND(o.tcv_usd / 1e6, 2) AS tcv_m,\n       d.rag_status, d.csat_score,\n       m.signal_source, m.intent_surge_score,\n       ROUND(m.client_rd_intensity_pct * 100, 1) AS rd_intensity_pct,\n       m.signal_summary\nFROM opportunities o\nJOIN delivery_health d ON o.account_id = d.account_id\nJOIN external_market_signals m ON o.account_id = m.account_id\nWHERE m.intent_surge_score >= 85\nORDER BY m.intent_surge_score DESC;"
    }
  },
  {
    "id": "Q-019",
    "code": "Q-019",
    "priority": "P2-Next",
    "persona": "Enterprise Risk & Portfolio Officer",
    "domain": "SEC 8-K Restructuring & Pipeline Freeze Contagion",
    "question": "Scan `SEC_Regulatory_Filings` for 8-K/10-Q restructuring charges or vendor spend freezes among our clients and quantify the immediate pipeline TCV and red-account delivery exposure.",
    "tier": "TIER_3",
    "tierLabel": "Tier 3 (49%): Federated Multi-Tool Agent (Structured SQL + Unstructured CLM/Visit RAG + External Market Intelligence APIs)",
    "systemsInvolved": [
      "SEC_Regulatory_Filings",
      "CRM_Opportunity_Spine",
      "Delivery_Governance_Hub"
    ],
    "blockerFlags": [
      "External 3P Market API",
      "Hidden Unstructured Notes"
    ],
    "confidence_pct": 49,
    "missing_artifacts": [
      "Automated EDGAR 8-K/10-Q ingestion webhook and restructuring sentiment classifier for SEC_Regulatory_Filings.",
      "Subsidiary-to-parent corporate hierarchy tree in CRM_Opportunity_Spine."
    ],
    "rawDbMcpSufficient": false,
    "dataplexKcCeilingSufficient": false,
    "requiresMultiToolFederation": true,
    "architecturalDiagnosis": "Client 8-K restructuring disclosures and activist investor demands occur in external SEC filings long before sales reps downgrade CRM win probabilities.",
    "recommendedArchitecture": "Early-Warning Federated Agent joins `SEC_Regulatory_Filings` alerts with `CRM_Opportunity_Spine` and `Delivery_Governance_Hub`.",
    "daxOrMetricFormula": {
      "id": "KPI-Q-019",
      "metricName": "SEC 8-K Restructuring & Pipeline Freeze Contagion",
      "domain": "Hybrid (BQ + External/Unstructured)",
      "daxExpression": "Macro_Contagion_TCV_USD = SUM(tcv_usd WHERE SEC_Filing_Sentiment = 'Spend_Freeze')",
      "canonicalSqlExpression": "SELECT o.opp_id, o.account_name, o.stage_name,\n       ROUND(o.tcv_usd / 1e6, 2) AS tcv_m,\n       o.win_prob AS crm_win_prob,\n       d.rag_status,\n       m.signal_summary AS sec_filing_alert\nFROM opportunities o\nJOIN delivery_health d ON o.account_id = d.account_id\nJOIN external_market_signals m ON o.account_id = m.account_id\nWHERE m.signal_source = 'SEC_Regulatory_Filings';",
      "dataplexGlossaryTerm": "projects/enterprise-mesh/locations/us/glossaries/commercial-kpi/terms/q_019",
      "sourceSystems": [
        "SEC_Regulatory_Filings",
        "CRM_Opportunity_Spine",
        "Delivery_Governance_Hub"
      ],
      "grain": "Hybrid (BQ + External/Unstructured) // Primary Commercial Entity Grain"
    },
    "genaiToolboxYaml": "  get_sec_filing_pipeline_exposure:\n    kind: bigquery-sql\n    source: enterprise-commercial-bq\n    description: Cross-reference SEC 8-K/10-Q restructuring alerts with active pipeline TCV.",
    "bigqueryGoldViewDdl": "-- Canonical BigQuery Gold View for Q-019 (SEC 8-K Restructuring & Pipeline Freeze Contagion)\nCREATE OR REPLACE VIEW `enterprise-commercial-mesh.gold_commercial.v_q_019_spine`\nOPTIONS(\n  description=\"SEC 8-K Restructuring & Pipeline Freeze Contagion governed by Dataplex Knowledge Catalog.\"\n) AS\nSELECT o.opp_id, o.account_name, o.stage_name,\n       ROUND(o.tcv_usd / 1e6, 2) AS tcv_m,\n       o.win_prob AS crm_win_prob,\n       d.rag_status,\n       m.signal_summary AS sec_filing_alert\nFROM opportunities o\nJOIN delivery_health d ON o.account_id = d.account_id\nJOIN external_market_signals m ON o.account_id = m.account_id\nWHERE m.signal_source = 'SEC_Regulatory_Filings';",
    "defaultSimulation": {
      "questionId": "Q-019",
      "questionText": "Scan `SEC_Regulatory_Filings` for 8-K/10-Q restructuring charges or vendor spend freezes among our clients and quantify the immediate pipeline TCV and red-account delivery exposure.",
      "tier": "TIER_3",
      "complianceStatus": "APPROVED",
      "rawSqlMcpOutcome": "FAILED_HALLUCINATED_METRIC",
      "federatedMeshOutcome": "VERIFIED_SYNTHESIS",
      "totalLatencyMs": 949,
      "traceSteps": [
        {
          "stepOrder": 1,
          "pillar": "PRE_FLIGHT_GOVERNANCE",
          "title": "Pre-Flight Dataplex GenAI License & RBAC Guard",
          "status": "PASSED",
          "latencyMs": 19,
          "detail": "Verified Dataplex governance aspects for sources: SEC_Regulatory_Filings, CRM_Opportunity_Spine, Delivery_Governance_Hub."
        },
        {
          "stepOrder": 2,
          "pillar": "GENAI_TOOLBOX_MCP",
          "title": "Fetch Structured Anchor Cohort from BigQuery Gold Spine",
          "status": "EXECUTED",
          "latencyMs": 290,
          "detail": "Queried structured keys from SEC_Regulatory_Filings, CRM_Opportunity_Spine."
        },
        {
          "stepOrder": 3,
          "pillar": "VERTEX_UNSTRUCTURED_RAG",
          "title": "Federate Unstructured CLM_Contract_Vault / Customer_Visit_Logs & External Market APIs",
          "status": "SYNTHESIZED",
          "latencyMs": 640,
          "detail": "Early-Warning Federated Agent joins `SEC_Regulatory_Filings` alerts with `CRM_Opportunity_Spine` and `Delivery_Governance_Hub`."
        }
      ],
      "synthesizedAnswer": "### Architectural Synthesis (Q-019 \u2014 Tier 3)\n- **Verdict on Raw Database MCP**: `FAIL - Requires Unstructured RAG + 3P API`\n- **Diagnosis**: Client 8-K restructuring disclosures and activist investor demands occur in external SEC filings long before sales reps downgrade CRM win probabilities.\n- **Recommended Production Mesh**: Early-Warning Federated Agent joins `SEC_Regulatory_Filings` alerts with `CRM_Opportunity_Spine` and `Delivery_Governance_Hub`.\n- **Assessment Readiness Confidence**: `49%`",
      "sqlExecuted": "SELECT o.opp_id, o.account_name, o.stage_name,\n       ROUND(o.tcv_usd / 1e6, 2) AS tcv_m,\n       o.win_prob AS crm_win_prob,\n       d.rag_status,\n       m.signal_summary AS sec_filing_alert\nFROM opportunities o\nJOIN delivery_health d ON o.account_id = d.account_id\nJOIN external_market_signals m ON o.account_id = m.account_id\nWHERE m.signal_source = 'SEC_Regulatory_Filings';"
    }
  },
  {
    "id": "Q-020",
    "code": "Q-020",
    "priority": "P2-Next",
    "persona": "Global Delivery Excellence Lead",
    "domain": "Unstructured Delivery Logs & Change-Order Recovery",
    "question": "Analyze unstructured delivery director commentary in `Delivery_Governance_Hub` alongside contract terms in `CLM_Contract_Vault` to diagnose why RED accounts are experiencing negative EAC margin variance.",
    "tier": "TIER_3",
    "tierLabel": "Tier 3 (49%): Federated Multi-Tool Agent (Structured SQL + Unstructured CLM/Visit RAG + External Market Intelligence APIs)",
    "systemsInvolved": [
      "Delivery_Governance_Hub",
      "CLM_Contract_Vault",
      "Deal_Pricing_Engine"
    ],
    "blockerFlags": [
      "Hidden Unstructured Notes"
    ],
    "confidence_pct": 61,
    "missing_artifacts": [
      "Unstructured text indexing of weekly delivery director commentary blobs in Delivery_Governance_Hub.",
      "Change-request (CR) status ledger in ERP_Financials_Ledger."
    ],
    "rawDbMcpSufficient": false,
    "dataplexKcCeilingSufficient": false,
    "requiresMultiToolFederation": true,
    "architecturalDiagnosis": "The root cause of RED delivery status (e.g., cleared architect shortages, unbilled change orders, fixed-price conversion traps) is embedded in free-text commentary and SOW clauses.",
    "recommendedArchitecture": "Combine SQL filter on `rag_status = 'RED'` with semantic synthesis over `delivery_commentary` and `CLM_Contract_Vault` notes.",
    "daxOrMetricFormula": {
      "id": "KPI-Q-020",
      "metricName": "Unstructured Delivery Logs & Change-Order Recovery",
      "domain": "Hybrid (BQ + External/Unstructured)",
      "daxExpression": "Recoverable_Change_Order_USD = Unbilled_Backlog_USD * Clause_Enforceability_Score",
      "canonicalSqlExpression": "SELECT d.account_name, d.rag_status, d.milestone_delays,\n       ROUND(d.eac_margin_variance_pct * 100, 1) AS eac_var_pct,\n       d.sla_slippage_days, d.delivery_commentary,\n       u.extracted_risk_tag, u.note_snippet AS contract_clause_note\nFROM delivery_health d\nLEFT JOIN unstructured_deal_notes u ON d.account_id = u.account_id\nWHERE d.rag_status = 'RED';",
      "dataplexGlossaryTerm": "projects/enterprise-mesh/locations/us/glossaries/commercial-kpi/terms/q_020",
      "sourceSystems": [
        "Delivery_Governance_Hub",
        "CLM_Contract_Vault",
        "Deal_Pricing_Engine"
      ],
      "grain": "Hybrid (BQ + External/Unstructured) // Primary Commercial Entity Grain"
    },
    "genaiToolboxYaml": "  diagnose_red_delivery_accounts:\n    kind: bigquery-sql\n    source: enterprise-commercial-bq\n    description: Fetch RED delivery accounts with free-text director logs and contract risk clauses.",
    "bigqueryGoldViewDdl": "-- Canonical BigQuery Gold View for Q-020 (Unstructured Delivery Logs & Change-Order Recovery)\nCREATE OR REPLACE VIEW `enterprise-commercial-mesh.gold_commercial.v_q_020_spine`\nOPTIONS(\n  description=\"Unstructured Delivery Logs & Change-Order Recovery governed by Dataplex Knowledge Catalog.\"\n) AS\nSELECT d.account_name, d.rag_status, d.milestone_delays,\n       ROUND(d.eac_margin_variance_pct * 100, 1) AS eac_var_pct,\n       d.sla_slippage_days, d.delivery_commentary,\n       u.extracted_risk_tag, u.note_snippet AS contract_clause_note\nFROM delivery_health d\nLEFT JOIN unstructured_deal_notes u ON d.account_id = u.account_id\nWHERE d.rag_status = 'RED';",
    "defaultSimulation": {
      "questionId": "Q-020",
      "questionText": "Analyze unstructured delivery director commentary in `Delivery_Governance_Hub` alongside contract terms in `CLM_Contract_Vault` to diagnose why RED accounts are experiencing negative EAC margin variance.",
      "tier": "TIER_3",
      "complianceStatus": "APPROVED",
      "rawSqlMcpOutcome": "FAILED_HALLUCINATED_METRIC",
      "federatedMeshOutcome": "VERIFIED_SYNTHESIS",
      "totalLatencyMs": 949,
      "traceSteps": [
        {
          "stepOrder": 1,
          "pillar": "PRE_FLIGHT_GOVERNANCE",
          "title": "Pre-Flight Dataplex GenAI License & RBAC Guard",
          "status": "PASSED",
          "latencyMs": 19,
          "detail": "Verified Dataplex governance aspects for sources: Delivery_Governance_Hub, CLM_Contract_Vault, Deal_Pricing_Engine."
        },
        {
          "stepOrder": 2,
          "pillar": "GENAI_TOOLBOX_MCP",
          "title": "Fetch Structured Anchor Cohort from BigQuery Gold Spine",
          "status": "EXECUTED",
          "latencyMs": 290,
          "detail": "Queried structured keys from Delivery_Governance_Hub, CLM_Contract_Vault."
        },
        {
          "stepOrder": 3,
          "pillar": "VERTEX_UNSTRUCTURED_RAG",
          "title": "Federate Unstructured CLM_Contract_Vault / Customer_Visit_Logs & External Market APIs",
          "status": "SYNTHESIZED",
          "latencyMs": 640,
          "detail": "Combine SQL filter on `rag_status = 'RED'` with semantic synthesis over `delivery_commentary` and `CLM_Contract_Vault` notes."
        }
      ],
      "synthesizedAnswer": "### Architectural Synthesis (Q-020 \u2014 Tier 3)\n- **Verdict on Raw Database MCP**: `FAIL - Requires Unstructured RAG + 3P API`\n- **Diagnosis**: The root cause of RED delivery status (e.g., cleared architect shortages, unbilled change orders, fixed-price conversion traps) is embedded in free-text commentary and SOW clauses.\n- **Recommended Production Mesh**: Combine SQL filter on `rag_status = 'RED'` with semantic synthesis over `delivery_commentary` and `CLM_Contract_Vault` notes.\n- **Assessment Readiness Confidence**: `61%`",
      "sqlExecuted": "SELECT d.account_name, d.rag_status, d.milestone_delays,\n       ROUND(d.eac_margin_variance_pct * 100, 1) AS eac_var_pct,\n       d.sla_slippage_days, d.delivery_commentary,\n       u.extracted_risk_tag, u.note_snippet AS contract_clause_note\nFROM delivery_health d\nLEFT JOIN unstructured_deal_notes u ON d.account_id = u.account_id\nWHERE d.rag_status = 'RED';"
    }
  },
  {
    "id": "Q-021",
    "code": "Q-021",
    "priority": "P3-Next",
    "persona": "Outcome-Based Pricing Architect",
    "domain": "Value-Sharing & Gain-Share Structuring",
    "question": "Identify accounts where high client R&D intensity (`Market_Financials_API`) and strong delivery CSAT (`Delivery_Governance_Hub`) support converting standard T&M rate cards into outcome-based gain-share contracts (`CLM_Contract_Vault`).",
    "tier": "TIER_3",
    "tierLabel": "Tier 3 (49%): Federated Multi-Tool Agent (Structured SQL + Unstructured CLM/Visit RAG + External Market Intelligence APIs)",
    "systemsInvolved": [
      "Market_Financials_API",
      "Delivery_Governance_Hub",
      "CLM_Contract_Vault",
      "Deal_Pricing_Engine"
    ],
    "blockerFlags": [
      "External 3P Market API",
      "Hidden Unstructured Notes"
    ],
    "confidence_pct": 51,
    "missing_artifacts": [
      "Historical outcome-based gain-share KPI realization ledger in ERP_Financials_Ledger.",
      "Approved value-sharing addendum templates in CLM_Contract_Vault."
    ],
    "rawDbMcpSufficient": false,
    "dataplexKcCeilingSufficient": false,
    "requiresMultiToolFederation": true,
    "architecturalDiagnosis": "Requires combining external client cash-flow/R&D posture with internal delivery reliability and precedent gain-share language in CLM.",
    "recommendedArchitecture": "Federated Agent queries `Market_Financials_API` + `Delivery_Governance_Hub` + `CLM_Contract_Vault` exemplars.",
    "daxOrMetricFormula": {
      "id": "KPI-Q-021",
      "metricName": "Value-Sharing & Gain-Share Structuring",
      "domain": "Hybrid (BQ + External/Unstructured)",
      "daxExpression": "Gain_Share_Upside_Yield = Adjusted_Yield_v4 + (Verified_KPI_Uplift * Bonus_Pool_Share)",
      "canonicalSqlExpression": "SELECT o.opp_id, o.account_name, o.service_line,\n       ROUND(o.tcv_usd / 1e6, 2) AS tcv_m,\n       ROUND(p.adjusted_yield_v4_sigma_capped * 100, 1) AS adj_yield_pct,\n       d.csat_score, d.delivery_commentary,\n       m.client_rd_intensity_pct, m.signal_summary\nFROM opportunities o\nJOIN pricing_scenarios p ON o.opp_id = p.opp_id\nJOIN delivery_health d ON o.account_id = d.account_id\nJOIN external_market_signals m ON o.account_id = m.account_id\nWHERE d.csat_score >= 0.90\nORDER BY m.client_rd_intensity_pct DESC;",
      "dataplexGlossaryTerm": "projects/enterprise-mesh/locations/us/glossaries/commercial-kpi/terms/q_021",
      "sourceSystems": [
        "Market_Financials_API",
        "Delivery_Governance_Hub",
        "CLM_Contract_Vault",
        "Deal_Pricing_Engine"
      ],
      "grain": "Hybrid (BQ + External/Unstructured) // Primary Commercial Entity Grain"
    },
    "genaiToolboxYaml": "  find_outcome_based_pricing_candidates:\n    kind: bigquery-sql\n    source: enterprise-commercial-bq\n    description: Identify high-CSAT, high-R&D accounts suited for gain-share commercial models.",
    "bigqueryGoldViewDdl": "-- Canonical BigQuery Gold View for Q-021 (Value-Sharing & Gain-Share Structuring)\nCREATE OR REPLACE VIEW `enterprise-commercial-mesh.gold_commercial.v_q_021_spine`\nOPTIONS(\n  description=\"Value-Sharing & Gain-Share Structuring governed by Dataplex Knowledge Catalog.\"\n) AS\nSELECT o.opp_id, o.account_name, o.service_line,\n       ROUND(o.tcv_usd / 1e6, 2) AS tcv_m,\n       ROUND(p.adjusted_yield_v4_sigma_capped * 100, 1) AS adj_yield_pct,\n       d.csat_score, d.delivery_commentary,\n       m.client_rd_intensity_pct, m.signal_summary\nFROM opportunities o\nJOIN pricing_scenarios p ON o.opp_id = p.opp_id\nJOIN delivery_health d ON o.account_id = d.account_id\nJOIN external_market_signals m ON o.account_id = m.account_id\nWHERE d.csat_score >= 0.90\nORDER BY m.client_rd_intensity_pct DESC;",
    "defaultSimulation": {
      "questionId": "Q-021",
      "questionText": "Identify accounts where high client R&D intensity (`Market_Financials_API`) and strong delivery CSAT (`Delivery_Governance_Hub`) support converting standard T&M rate cards into outcome-based gain-share contracts (`CLM_Contract_Vault`).",
      "tier": "TIER_3",
      "complianceStatus": "APPROVED",
      "rawSqlMcpOutcome": "FAILED_HALLUCINATED_METRIC",
      "federatedMeshOutcome": "VERIFIED_SYNTHESIS",
      "totalLatencyMs": 949,
      "traceSteps": [
        {
          "stepOrder": 1,
          "pillar": "PRE_FLIGHT_GOVERNANCE",
          "title": "Pre-Flight Dataplex GenAI License & RBAC Guard",
          "status": "PASSED",
          "latencyMs": 19,
          "detail": "Verified Dataplex governance aspects for sources: Market_Financials_API, Delivery_Governance_Hub, CLM_Contract_Vault, Deal_Pricing_Engine."
        },
        {
          "stepOrder": 2,
          "pillar": "GENAI_TOOLBOX_MCP",
          "title": "Fetch Structured Anchor Cohort from BigQuery Gold Spine",
          "status": "EXECUTED",
          "latencyMs": 290,
          "detail": "Queried structured keys from Market_Financials_API, Delivery_Governance_Hub."
        },
        {
          "stepOrder": 3,
          "pillar": "VERTEX_UNSTRUCTURED_RAG",
          "title": "Federate Unstructured CLM_Contract_Vault / Customer_Visit_Logs & External Market APIs",
          "status": "SYNTHESIZED",
          "latencyMs": 640,
          "detail": "Federated Agent queries `Market_Financials_API` + `Delivery_Governance_Hub` + `CLM_Contract_Vault` exemplars."
        }
      ],
      "synthesizedAnswer": "### Architectural Synthesis (Q-021 \u2014 Tier 3)\n- **Verdict on Raw Database MCP**: `FAIL - Requires Unstructured RAG + 3P API`\n- **Diagnosis**: Requires combining external client cash-flow/R&D posture with internal delivery reliability and precedent gain-share language in CLM.\n- **Recommended Production Mesh**: Federated Agent queries `Market_Financials_API` + `Delivery_Governance_Hub` + `CLM_Contract_Vault` exemplars.\n- **Assessment Readiness Confidence**: `51%`",
      "sqlExecuted": "SELECT o.opp_id, o.account_name, o.service_line,\n       ROUND(o.tcv_usd / 1e6, 2) AS tcv_m,\n       ROUND(p.adjusted_yield_v4_sigma_capped * 100, 1) AS adj_yield_pct,\n       d.csat_score, d.delivery_commentary,\n       m.client_rd_intensity_pct, m.signal_summary\nFROM opportunities o\nJOIN pricing_scenarios p ON o.opp_id = p.opp_id\nJOIN delivery_health d ON o.account_id = d.account_id\nJOIN external_market_signals m ON o.account_id = m.account_id\nWHERE d.csat_score >= 0.90\nORDER BY m.client_rd_intensity_pct DESC;"
    }
  },
  {
    "id": "Q-022",
    "code": "Q-022",
    "priority": "P4-Next",
    "persona": "Corporate M&A & Ecosystem Strategy Lead",
    "domain": "Unmapped Ecosystem Partner Influence",
    "question": "Quantify how co-sell hyperscaler commit drawdown speed correlates with competitor displacement across unmapped regional partner registries.",
    "tier": "TIER_3",
    "tierLabel": "Tier 3 (49%): Federated Multi-Tool Agent (Structured SQL + Unstructured CLM/Visit RAG + External Market Intelligence APIs)",
    "systemsInvolved": [
      "CRM_Opportunity_Spine",
      "AI_Web_Synthesis_Engine"
    ],
    "blockerFlags": [
      "Incomplete Spec",
      "External 3P Market API"
    ],
    "confidence_pct": 24,
    "missing_artifacts": [
      "UNMAPPED SCHEMA: Hyperscaler co-sell private-offer drawdown registry is not yet ingested into Revenue_ODS_15TB.",
      "Partner influence attribution model in CRM_Opportunity_Spine."
    ],
    "rawDbMcpSufficient": false,
    "dataplexKcCeilingSufficient": false,
    "requiresMultiToolFederation": true,
    "architecturalDiagnosis": "Hyperscaler private-offer drawdown telemetry is currently unmapped in the internal ODS schema; requires schema onboarding into Dataplex plus external web synthesis.",
    "recommendedArchitecture": "Flag as P4 Schema Onboarding gap in Dataplex Knowledge Catalog; provide proxy pipeline correlation from `CRM_Opportunity_Spine`.",
    "daxOrMetricFormula": {
      "id": "KPI-Q-022",
      "metricName": "Unmapped Ecosystem Partner Influence",
      "domain": "Unmapped Spec",
      "daxExpression": "Partner_Commit_Burn_Multiplier = CoSell_Win_Rate / Solo_Win_Rate",
      "canonicalSqlExpression": "SELECT service_line, COUNT(*) AS deals,\n       ROUND(AVG(win_prob) * 100, 1) AS avg_win_prob_pct,\n       ROUND(SUM(tcv_usd) / 1e6, 2) AS total_tcv_m\nFROM opportunities\nGROUP BY service_line;",
      "dataplexGlossaryTerm": "projects/enterprise-mesh/locations/us/glossaries/commercial-kpi/terms/q_022",
      "sourceSystems": [
        "CRM_Opportunity_Spine",
        "AI_Web_Synthesis_Engine"
      ],
      "grain": "Unmapped Spec // Primary Commercial Entity Grain"
    },
    "genaiToolboxYaml": "  get_partner_cosell_proxy_metrics:\n    kind: bigquery-sql\n    source: enterprise-commercial-bq\n    description: Proxy service-line win rates while Partner Drawdown schema is onboarded.",
    "bigqueryGoldViewDdl": "-- Canonical BigQuery Gold View for Q-022 (Unmapped Ecosystem Partner Influence)\nCREATE OR REPLACE VIEW `enterprise-commercial-mesh.gold_commercial.v_q_022_spine`\nOPTIONS(\n  description=\"Unmapped Ecosystem Partner Influence governed by Dataplex Knowledge Catalog.\"\n) AS\nSELECT service_line, COUNT(*) AS deals,\n       ROUND(AVG(win_prob) * 100, 1) AS avg_win_prob_pct,\n       ROUND(SUM(tcv_usd) / 1e6, 2) AS total_tcv_m\nFROM opportunities\nGROUP BY service_line;",
    "defaultSimulation": {
      "questionId": "Q-022",
      "questionText": "Quantify how co-sell hyperscaler commit drawdown speed correlates with competitor displacement across unmapped regional partner registries.",
      "tier": "TIER_3",
      "complianceStatus": "APPROVED",
      "rawSqlMcpOutcome": "FAILED_HALLUCINATED_METRIC",
      "federatedMeshOutcome": "VERIFIED_SYNTHESIS",
      "totalLatencyMs": 949,
      "traceSteps": [
        {
          "stepOrder": 1,
          "pillar": "PRE_FLIGHT_GOVERNANCE",
          "title": "Pre-Flight Dataplex GenAI License & RBAC Guard",
          "status": "PASSED",
          "latencyMs": 19,
          "detail": "Verified Dataplex governance aspects for sources: CRM_Opportunity_Spine, AI_Web_Synthesis_Engine."
        },
        {
          "stepOrder": 2,
          "pillar": "GENAI_TOOLBOX_MCP",
          "title": "Fetch Structured Anchor Cohort from BigQuery Gold Spine",
          "status": "EXECUTED",
          "latencyMs": 290,
          "detail": "Queried structured keys from CRM_Opportunity_Spine, AI_Web_Synthesis_Engine."
        },
        {
          "stepOrder": 3,
          "pillar": "VERTEX_UNSTRUCTURED_RAG",
          "title": "Federate Unstructured CLM_Contract_Vault / Customer_Visit_Logs & External Market APIs",
          "status": "SYNTHESIZED",
          "latencyMs": 640,
          "detail": "Flag as P4 Schema Onboarding gap in Dataplex Knowledge Catalog; provide proxy pipeline correlation from `CRM_Opportunity_Spine`."
        }
      ],
      "synthesizedAnswer": "### Architectural Synthesis (Q-022 \u2014 Tier 3)\n- **Verdict on Raw Database MCP**: `FAIL - Requires Unstructured RAG + 3P API`\n- **Diagnosis**: Hyperscaler private-offer drawdown telemetry is currently unmapped in the internal ODS schema; requires schema onboarding into Dataplex plus external web synthesis.\n- **Recommended Production Mesh**: Flag as P4 Schema Onboarding gap in Dataplex Knowledge Catalog; provide proxy pipeline correlation from `CRM_Opportunity_Spine`.\n- **Assessment Readiness Confidence**: `24%`",
      "sqlExecuted": "SELECT service_line, COUNT(*) AS deals,\n       ROUND(AVG(win_prob) * 100, 1) AS avg_win_prob_pct,\n       ROUND(SUM(tcv_usd) / 1e6, 2) AS total_tcv_m\nFROM opportunities\nGROUP BY service_line;"
    }
  },
  {
    "id": "Q-023",
    "code": "Q-023",
    "priority": "P3-Next",
    "persona": "Executive Client Sponsor (MD)",
    "domain": "Automated Executive QBR Briefing Generation",
    "question": "Generate an executive-ready Quarterly Business Review (QBR) briefing packet for Apex Global Banking Corp (ACC-101) combining pipeline TCV, Adjusted Yield v4, delivery SLA health, contract COLA risks, and external AI hiring signals.",
    "tier": "TIER_4",
    "tierLabel": "Tier 4 (3%): Multi-System Action & Executive Briefing Automation",
    "systemsInvolved": [
      "CRM_Opportunity_Spine",
      "Deal_Pricing_Engine",
      "Delivery_Governance_Hub",
      "CLM_Contract_Vault",
      "Customer_Visit_Logs",
      "Tech_Stack_Telemetry_Feed"
    ],
    "blockerFlags": [
      "Hidden Unstructured Notes",
      "External 3P Market API"
    ],
    "confidence_pct": 46,
    "missing_artifacts": [
      "Cross-system Account 360 orchestration workflow binding 6 structured, RAG, and 3P telemetry sources.",
      "Executive QBR slide template schema and automated write-back service account permissions."
    ],
    "rawDbMcpSufficient": false,
    "dataplexKcCeilingSufficient": false,
    "requiresMultiToolFederation": true,
    "architecturalDiagnosis": "Requires multi-source synthesis across 6 structured, unstructured, and 3P systems followed by structured artifact formatting for executive consumption.",
    "recommendedArchitecture": "Tier-4 Action Orchestrator: Invoke Account 360 Federated Toolset + synthesize executive briefing markdown/slides packet.",
    "daxOrMetricFormula": {
      "id": "KPI-Q-023",
      "metricName": "Automated Executive QBR Briefing Generation",
      "domain": "Hybrid (BQ + External/Unstructured)",
      "daxExpression": "Account_360_Composite_Health = 0.35*Yield_Index + 0.35*Delivery_CSAT + 0.30*(1 - AI_Insourcing_Risk)",
      "canonicalSqlExpression": "SELECT o.opp_id, o.account_name, o.stage_name, o.tcv_usd,\n       p.adjusted_yield_v4_sigma_capped, p.discount_giveaway_pct,\n       d.rag_status, d.csat_score, d.delivery_commentary,\n       m.ai_self_sufficiency_index, m.signal_summary\nFROM opportunities o\nJOIN pricing_scenarios p ON o.opp_id = p.opp_id\nJOIN delivery_health d ON o.account_id = d.account_id\nLEFT JOIN external_market_signals m ON o.account_id = m.account_id\nWHERE o.account_id = 'ACC-101';",
      "dataplexGlossaryTerm": "projects/enterprise-mesh/locations/us/glossaries/commercial-kpi/terms/q_023",
      "sourceSystems": [
        "CRM_Opportunity_Spine",
        "Deal_Pricing_Engine",
        "Delivery_Governance_Hub",
        "CLM_Contract_Vault",
        "Customer_Visit_Logs",
        "Tech_Stack_Telemetry_Feed"
      ],
      "grain": "Hybrid (BQ + External/Unstructured) // Primary Commercial Entity Grain"
    },
    "genaiToolboxYaml": "  assemble_executive_qbr_dossier:\n    kind: bigquery-sql\n    source: enterprise-commercial-bq\n    description: Aggregate full Account 360 telemetry for executive QBR generation.",
    "bigqueryGoldViewDdl": "-- Canonical BigQuery Gold View for Q-023 (Automated Executive QBR Briefing Generation)\nCREATE OR REPLACE VIEW `enterprise-commercial-mesh.gold_commercial.v_q_023_spine`\nOPTIONS(\n  description=\"Automated Executive QBR Briefing Generation governed by Dataplex Knowledge Catalog.\"\n) AS\nSELECT o.opp_id, o.account_name, o.stage_name, o.tcv_usd,\n       p.adjusted_yield_v4_sigma_capped, p.discount_giveaway_pct,\n       d.rag_status, d.csat_score, d.delivery_commentary,\n       m.ai_self_sufficiency_index, m.signal_summary\nFROM opportunities o\nJOIN pricing_scenarios p ON o.opp_id = p.opp_id\nJOIN delivery_health d ON o.account_id = d.account_id\nLEFT JOIN external_market_signals m ON o.account_id = m.account_id\nWHERE o.account_id = 'ACC-101';",
    "defaultSimulation": {
      "questionId": "Q-023",
      "questionText": "Generate an executive-ready Quarterly Business Review (QBR) briefing packet for Apex Global Banking Corp (ACC-101) combining pipeline TCV, Adjusted Yield v4, delivery SLA health, contract COLA risks, and external AI hiring signals.",
      "tier": "TIER_4",
      "complianceStatus": "APPROVED",
      "rawSqlMcpOutcome": "FAILED_HALLUCINATED_METRIC",
      "federatedMeshOutcome": "VERIFIED_SYNTHESIS",
      "totalLatencyMs": 1089,
      "traceSteps": [
        {
          "stepOrder": 1,
          "pillar": "PRE_FLIGHT_GOVERNANCE",
          "title": "Pre-Flight Dataplex GenAI License & RBAC Guard",
          "status": "PASSED",
          "latencyMs": 19,
          "detail": "Verified Dataplex governance aspects for sources: CRM_Opportunity_Spine, Deal_Pricing_Engine, Delivery_Governance_Hub, CLM_Contract_Vault, Customer_Visit_Logs, Tech_Stack_Telemetry_Feed."
        },
        {
          "stepOrder": 2,
          "pillar": "VERTEX_UNSTRUCTURED_RAG",
          "title": "Cross-Domain Account 360 & Unstructured Synthesis",
          "status": "EXECUTED",
          "latencyMs": 580,
          "detail": "Requires multi-source synthesis across 6 structured, unstructured, and 3P systems followed by structured artifact formatting for executive consumption."
        },
        {
          "stepOrder": 3,
          "pillar": "WORKSPACE_ACTION_MESH",
          "title": "Generate Executive QBR Pack & Trigger Pursuit Mobilization Workflow",
          "status": "SYNTHESIZED",
          "latencyMs": 490,
          "detail": "Tier-4 Action Orchestrator: Invoke Account 360 Federated Toolset + synthesize executive briefing markdown/slides packet."
        }
      ],
      "synthesizedAnswer": "### Architectural Synthesis (Q-023 \u2014 Tier 4)\n- **Verdict on Raw Database MCP**: `FAIL - Requires Multi-System Action Orchestration`\n- **Diagnosis**: Requires multi-source synthesis across 6 structured, unstructured, and 3P systems followed by structured artifact formatting for executive consumption.\n- **Recommended Production Mesh**: Tier-4 Action Orchestrator: Invoke Account 360 Federated Toolset + synthesize executive briefing markdown/slides packet.\n- **Assessment Readiness Confidence**: `46%`",
      "sqlExecuted": "SELECT o.opp_id, o.account_name, o.stage_name, o.tcv_usd,\n       p.adjusted_yield_v4_sigma_capped, p.discount_giveaway_pct,\n       d.rag_status, d.csat_score, d.delivery_commentary,\n       m.ai_self_sufficiency_index, m.signal_summary\nFROM opportunities o\nJOIN pricing_scenarios p ON o.opp_id = p.opp_id\nJOIN delivery_health d ON o.account_id = d.account_id\nLEFT JOIN external_market_signals m ON o.account_id = m.account_id\nWHERE o.account_id = 'ACC-101';"
    }
  },
  {
    "id": "Q-024",
    "code": "Q-024",
    "priority": "P3-Next",
    "persona": "Global Deal Pursuit Director",
    "domain": "Pre-Call SME Mobilization & Action Dispatch",
    "question": "For all RED delivery accounts with active Stage 3 opportunities > $150M, match required architectural skills from `Workforce_Skills_Graph` and generate a pre-call intervention action plan.",
    "tier": "TIER_4",
    "tierLabel": "Tier 4 (3%): Multi-System Action & Executive Briefing Automation",
    "systemsInvolved": [
      "CRM_Opportunity_Spine",
      "Delivery_Governance_Hub",
      "Workforce_Skills_Graph",
      "CLM_Contract_Vault"
    ],
    "blockerFlags": [
      "Hidden Unstructured Notes"
    ],
    "confidence_pct": 42,
    "missing_artifacts": [
      "Real-time skill availability and clearance verification API in Workforce_Skills_Graph.",
      "Downstream calendar/dispatch webhook for automated pursuit squad mobilization."
    ],
    "rawDbMcpSufficient": false,
    "dataplexKcCeilingSufficient": false,
    "requiresMultiToolFederation": true,
    "architecturalDiagnosis": "Combines structured deal/delivery filtering with unstructured bottleneck diagnosis and downstream mobilization workflow generation.",
    "recommendedArchitecture": "Tier-4 Multi-System Agent: Query at-risk mega-deals, extract delivery/contract bottlenecks, and trigger SME mobilization workflow.",
    "daxOrMetricFormula": {
      "id": "KPI-Q-024",
      "metricName": "Pre-Call SME Mobilization & Action Dispatch",
      "domain": "Hybrid (BQ + External/Unstructured)",
      "daxExpression": "At_Risk_MegaDeal_TCV_USD = SUM(tcv_usd WHERE rag_status = 'RED' AND tcv_usd > 150000000)",
      "canonicalSqlExpression": "SELECT o.opp_id, o.account_name, o.service_line,\n       ROUND(o.tcv_usd / 1e6, 2) AS tcv_millions,\n       d.rag_status, d.sla_slippage_days, d.delivery_commentary\nFROM opportunities o\nJOIN delivery_health d ON o.account_id = d.account_id\nWHERE d.rag_status = 'RED' AND o.tcv_usd >= 150000000\nORDER BY o.tcv_usd DESC;",
      "dataplexGlossaryTerm": "projects/enterprise-mesh/locations/us/glossaries/commercial-kpi/terms/q_024",
      "sourceSystems": [
        "CRM_Opportunity_Spine",
        "Delivery_Governance_Hub",
        "Workforce_Skills_Graph",
        "CLM_Contract_Vault"
      ],
      "grain": "Hybrid (BQ + External/Unstructured) // Primary Commercial Entity Grain"
    },
    "genaiToolboxYaml": "  mobilize_red_account_pursuit_squad:\n    kind: bigquery-sql\n    source: enterprise-commercial-bq\n    description: Identify >$150M opportunities on RED delivery accounts for SME intervention.",
    "bigqueryGoldViewDdl": "-- Canonical BigQuery Gold View for Q-024 (Pre-Call SME Mobilization & Action Dispatch)\nCREATE OR REPLACE VIEW `enterprise-commercial-mesh.gold_commercial.v_q_024_spine`\nOPTIONS(\n  description=\"Pre-Call SME Mobilization & Action Dispatch governed by Dataplex Knowledge Catalog.\"\n) AS\nSELECT o.opp_id, o.account_name, o.service_line,\n       ROUND(o.tcv_usd / 1e6, 2) AS tcv_millions,\n       d.rag_status, d.sla_slippage_days, d.delivery_commentary\nFROM opportunities o\nJOIN delivery_health d ON o.account_id = d.account_id\nWHERE d.rag_status = 'RED' AND o.tcv_usd >= 150000000\nORDER BY o.tcv_usd DESC;",
    "defaultSimulation": {
      "questionId": "Q-024",
      "questionText": "For all RED delivery accounts with active Stage 3 opportunities > $150M, match required architectural skills from `Workforce_Skills_Graph` and generate a pre-call intervention action plan.",
      "tier": "TIER_4",
      "complianceStatus": "APPROVED",
      "rawSqlMcpOutcome": "FAILED_HALLUCINATED_METRIC",
      "federatedMeshOutcome": "VERIFIED_SYNTHESIS",
      "totalLatencyMs": 1089,
      "traceSteps": [
        {
          "stepOrder": 1,
          "pillar": "PRE_FLIGHT_GOVERNANCE",
          "title": "Pre-Flight Dataplex GenAI License & RBAC Guard",
          "status": "PASSED",
          "latencyMs": 19,
          "detail": "Verified Dataplex governance aspects for sources: CRM_Opportunity_Spine, Delivery_Governance_Hub, Workforce_Skills_Graph, CLM_Contract_Vault."
        },
        {
          "stepOrder": 2,
          "pillar": "VERTEX_UNSTRUCTURED_RAG",
          "title": "Cross-Domain Account 360 & Unstructured Synthesis",
          "status": "EXECUTED",
          "latencyMs": 580,
          "detail": "Combines structured deal/delivery filtering with unstructured bottleneck diagnosis and downstream mobilization workflow generation."
        },
        {
          "stepOrder": 3,
          "pillar": "WORKSPACE_ACTION_MESH",
          "title": "Generate Executive QBR Pack & Trigger Pursuit Mobilization Workflow",
          "status": "SYNTHESIZED",
          "latencyMs": 490,
          "detail": "Tier-4 Multi-System Agent: Query at-risk mega-deals, extract delivery/contract bottlenecks, and trigger SME mobilization workflow."
        }
      ],
      "synthesizedAnswer": "### Architectural Synthesis (Q-024 \u2014 Tier 4)\n- **Verdict on Raw Database MCP**: `FAIL - Requires Multi-System Action Orchestration`\n- **Diagnosis**: Combines structured deal/delivery filtering with unstructured bottleneck diagnosis and downstream mobilization workflow generation.\n- **Recommended Production Mesh**: Tier-4 Multi-System Agent: Query at-risk mega-deals, extract delivery/contract bottlenecks, and trigger SME mobilization workflow.\n- **Assessment Readiness Confidence**: `42%`",
      "sqlExecuted": "SELECT o.opp_id, o.account_name, o.service_line,\n       ROUND(o.tcv_usd / 1e6, 2) AS tcv_millions,\n       d.rag_status, d.sla_slippage_days, d.delivery_commentary\nFROM opportunities o\nJOIN delivery_health d ON o.account_id = d.account_id\nWHERE d.rag_status = 'RED' AND o.tcv_usd >= 150000000\nORDER BY o.tcv_usd DESC;"
    }
  }
];
