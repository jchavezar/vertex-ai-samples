#!/usr/bin/env python3
"""
Synthetic Topology & Enterprise Commercial Spine Seed Generator.

Generates:
1. `data/commercial_spine_mock.db` (SQLite database representing the federated
   BigQuery Gold Spine, Unstructured Vault metadata, External Market Signals,
   and Data Source Governance registry).
2. `data/taxonomy_questions_catalog.json` (24 representative Enterprise B2B
   Commercial Intelligence Benchmark Questions across all 4 Architectural Tiers,
   annotated with topology, DAX formulas, architectural blockers, SQL, and MCP
   Toolbox configurations).
"""

from __future__ import annotations

import json
import os
import sqlite3
from pathlib import Path
from typing import Any, Dict, List

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "commercial_spine_mock.db"
CATALOG_PATH = BASE_DIR / "taxonomy_questions_catalog.json"


GOVERNANCE_SOURCES: List[Dict[str, Any]] = [
    {
        "source_id": "SRC-001",
        "source_name": "CRM_Opportunity_Spine",
        "category": "Internal Structured (BQ)",
        "storage_engine": "BigQuery Cluster (1.8 TB)",
        "refresh_cadence": "Real-time CDC (15 min)",
        "genai_usage_rights": 1,
        "pii_classification": "Confidential - Customer Commercial",
        "dataplex_aspect_uri": "projects/enterprise-mesh/locations/us/aspectTypes/commercial-spine-crm",
        "steward_team": "Global Sales Operations Engineering",
        "notes": "Primary pipeline spine tracking Stage 1-5 opportunities, TCV, ACV, and deal team assignments.",
    },
    {
        "source_id": "SRC-002",
        "source_name": "Revenue_ODS_15TB",
        "category": "Internal Structured (BQ)",
        "storage_engine": "BigQuery Partitioned ODS (15.4 TB)",
        "refresh_cadence": "Hourly Incremental",
        "genai_usage_rights": 1,
        "pii_classification": "Restricted Financial",
        "dataplex_aspect_uri": "projects/enterprise-mesh/locations/us/aspectTypes/revenue-ods-core",
        "steward_team": "Enterprise Data Warehouse Platform",
        "notes": "36-month historical snapshot ledger across 420+ wide tables; requires Gold Views to avoid join hallucinations.",
    },
    {
        "source_id": "SRC-003",
        "source_name": "Deal_Pricing_Engine",
        "category": "Internal Structured (BQ)",
        "storage_engine": "BigQuery + Cloud SQL Replica",
        "refresh_cadence": "Sub-hour Event Stream",
        "genai_usage_rights": 1,
        "pii_classification": "Highly Confidential - Margin & Rate Cards",
        "dataplex_aspect_uri": "projects/enterprise-mesh/locations/us/aspectTypes/pricing-scenario-engine",
        "steward_team": "Commercial Pricing & Margin Analytics",
        "notes": "Stores scenario versions, rate cards, gross/adjusted yield, pass-through hardware/cloud costs, and discount approvals.",
    },
    {
        "source_id": "SRC-004",
        "source_name": "ERP_Financials_Ledger",
        "category": "Internal Structured (BQ)",
        "storage_engine": "BigQuery Federated SAP/Oracle Replication",
        "refresh_cadence": "Nightly Batch + Period Close",
        "genai_usage_rights": 1,
        "pii_classification": "SOX Regulated Financial",
        "dataplex_aspect_uri": "projects/enterprise-mesh/locations/us/aspectTypes/erp-actuals-ledger",
        "steward_team": "Corporate Controllership & FP&A",
        "notes": "Booked revenue, recognized actuals, billable utilization, and EAC (Estimate at Completion) margin variance.",
    },
    {
        "source_id": "SRC-005",
        "source_name": "Delivery_Governance_Hub",
        "category": "Internal Hybrid (BQ + Text)",
        "storage_engine": "BigQuery + Unstructured Commentary Blobs",
        "refresh_cadence": "Weekly Delivery Pulse",
        "genai_usage_rights": 1,
        "pii_classification": "Internal Operational",
        "dataplex_aspect_uri": "projects/enterprise-mesh/locations/us/aspectTypes/delivery-governance-rag",
        "steward_team": "Global Delivery Excellence PMO",
        "notes": "Tracks milestone SLA slippage, red/amber/green status, change orders, and unstructured delivery director logs.",
    },
    {
        "source_id": "SRC-006",
        "source_name": "CLM_Contract_Vault",
        "category": "Internal Unstructured (RAG)",
        "storage_engine": "Vertex AI Search + Cloud Storage PDF Corpus",
        "refresh_cadence": "Continuous Document Ingestion",
        "genai_usage_rights": 1,
        "pii_classification": "Privileged Legal & Commercial",
        "dataplex_aspect_uri": "projects/enterprise-mesh/locations/us/aspectTypes/clm-contract-clauses",
        "steward_team": "Commercial Legal Operations",
        "notes": "Executed MSAs, SOWs, COLA inflation caps, termination-for-convenience clauses, and volume rebate tiers.",
    },
    {
        "source_id": "SRC-007",
        "source_name": "Customer_Visit_Logs",
        "category": "Internal Unstructured (RAG)",
        "storage_engine": "BigQuery Text + Vertex Embeddings",
        "refresh_cadence": "Daily Sync",
        "genai_usage_rights": 1,
        "pii_classification": "Confidential Executive Notes",
        "dataplex_aspect_uri": "projects/enterprise-mesh/locations/us/aspectTypes/executive-visit-briefings",
        "steward_team": "Executive Client Programs",
        "notes": "Executive sponsor visit debriefs, C-suite sentiment notes, competitor mentions, and stakeholder alignment scores.",
    },
    {
        "source_id": "SRC-008",
        "source_name": "Workforce_Skills_Graph",
        "category": "Internal Structured (BQ)",
        "storage_engine": "BigQuery Graph Projection",
        "refresh_cadence": "Daily",
        "genai_usage_rights": 1,
        "pii_classification": "Internal HR Anonymized",
        "dataplex_aspect_uri": "projects/enterprise-mesh/locations/us/aspectTypes/workforce-bench-skills",
        "steward_team": "Talent Supply Chain Analytics",
        "notes": " tracks certified AI/Cloud architects, bench availability, regional Pyramid ratios, and mobilization lead times.",
    },
    {
        "source_id": "SRC-009",
        "source_name": "Market_Financials_API",
        "category": "External 3P Market API",
        "storage_engine": "REST Gateway + BigQuery Cache",
        "refresh_cadence": "Daily Market Close",
        "genai_usage_rights": 1,
        "pii_classification": "Public / Licensed Commercial",
        "dataplex_aspect_uri": "projects/enterprise-mesh/locations/us/aspectTypes/external-market-financials",
        "steward_team": "Market Intelligence CoE",
        "notes": "Enterprise 10-K/10-Q fundamentals, R&D capex ratios, SG&A compression trends, and peer solvency metrics.",
    },
    {
        "source_id": "SRC-010",
        "source_name": "Tech_Stack_Telemetry_Feed",
        "category": "External 3P Market API",
        "storage_engine": "External API + Weekly Iceberg Sync",
        "refresh_cadence": "Weekly",
        "genai_usage_rights": 1,
        "pii_classification": "Licensed 3P Telemetry",
        "dataplex_aspect_uri": "projects/enterprise-mesh/locations/us/aspectTypes/tech-stack-telemetry",
        "steward_team": "Market Intelligence CoE",
        "notes": "Detects installed cloud footprint, LLM framework adoption, GPU cluster hiring, and DIY AI self-sufficiency signals.",
    },
    {
        "source_id": "SRC-011",
        "source_name": "Buyer_Intent_Signal_Stream",
        "category": "External 3P Market API",
        "storage_engine": "Streaming Webhook + BigQuery Landing",
        "refresh_cadence": "Daily Surge Scores",
        "genai_usage_rights": 1,
        "pii_classification": "Licensed 3P Intent",
        "dataplex_aspect_uri": "projects/enterprise-mesh/locations/us/aspectTypes/buyer-intent-stream",
        "steward_team": "Growth & ABM Analytics",
        "notes": "B2B topic surge scores across Cloud FinOps, Agentic AI, ERP Modernization, and Managed SOC.",
    },
    {
        "source_id": "SRC-012",
        "source_name": "AI_Web_Synthesis_Engine",
        "category": "External Grounded Search",
        "storage_engine": "Vertex AI Grounded Search API",
        "refresh_cadence": "On-Demand Live",
        "genai_usage_rights": 1,
        "pii_classification": "Public Web",
        "dataplex_aspect_uri": "projects/enterprise-mesh/locations/us/aspectTypes/live-web-synthesis",
        "steward_team": "AI Platform Engineering",
        "notes": "Real-time earnings call transcripts, M&A press releases, executive leadership changes, and regulatory news.",
    },
    {
        "source_id": "SRC-013",
        "source_name": "SEC_Regulatory_Filings",
        "category": "External Structured/Text",
        "storage_engine": "EDGAR Filing Index + Vector Store",
        "refresh_cadence": "Quarterly / 8-K Event Driven",
        "genai_usage_rights": 1,
        "pii_classification": "Public Regulatory",
        "dataplex_aspect_uri": "projects/enterprise-mesh/locations/us/aspectTypes/sec-edgar-filings",
        "steward_team": "Market Intelligence CoE",
        "notes": "Risk factor disclosures, IT transformation budget commitments, and cybersecurity incident disclosures.",
    },
    {
        "source_id": "SRC-014",
        "source_name": "Analyst_Benchmark_Feed_Unlicensed",
        "category": "External Restricted Feed",
        "storage_engine": "Quarantined CSV Drop (No LLM Egress)",
        "refresh_cadence": "Quarterly",
        "genai_usage_rights": 0,
        "pii_classification": "RESTRICTED - ZERO GENAI RIGHTS",
        "dataplex_aspect_uri": "projects/enterprise-mesh/locations/us/aspectTypes/quarantined-analyst-feed",
        "steward_team": "Enterprise Procurement & Legal Compliance",
        "notes": "Syndicated rate-card and peer market-share tables. Contract explicitly forbids LLM prompt injection, RAG indexing, or derivative GenAI synthesis.",
    },
]


OPPORTUNITIES_SEED = [
    ("OPP-9011", "ACC-101", "Apex Global Banking Corp", "North America", "Financial Services", "Cloud Core & Agentic Operations", "Stage 3 - Solutioning", 142000000.0, 47300000.0, 118, 0.41, "2026-06-15", "2026-09-18", "2026-10-10", "Marcus Vance", "Regime_2_Margin_Compression", 0.342, 0.289, 18400000.0, 0.78),
    ("OPP-9012", "ACC-102", "Vanguard Sovereign Energy", "EMEA", "Energy & Utilities", "ERP Clean-Core & Grid AI", "Stage 3 - Solutioning", 96500000.0, 32100000.0, 104, 0.38, "2026-06-28", "2026-09-12", "2026-09-21", "Elena Rostova", "Regime_1_High_Velocity_Expansion", 0.365, 0.331, 9200000.0, 0.84),
    ("OPP-9013", "ACC-103", "Meridian BioPharma Holdings", "North America", "Life Sciences", "R&D Clinical Data Mesh", "Stage 4 - Commercial Negotiation", 215000000.0, 53750000.0, 64, 0.68, "2026-08-05", "2026-10-12", "2026-10-12", "David Thorne", "Regime_1_High_Velocity_Expansion", 0.412, 0.378, 14500000.0, 0.91),
    ("OPP-9014", "ACC-104", "Stratos Aerospace & Defense", "North America", "Industrial Manufacturing", "Digital Twin Supply Chain", "Stage 3 - Solutioning", 178000000.0, 44500000.0, 136, 0.29, "2026-05-19", "2026-08-29", "2026-09-14", "Marcus Vance", "Regime_3_Stalled_Procurement", 0.295, 0.214, 29800000.0, 0.62),
    ("OPP-9015", "ACC-105", "Pacifica Omni-Retail Group", "APAC", "Consumer & Retail", "Autonomous Supply & FinOps", "Stage 2 - Qualification", 64000000.0, 21300000.0, 49, 0.52, "2026-08-22", "2026-09-19", "2026-09-20", "Kenji Takahashi", "Regime_2_Margin_Compression", 0.278, 0.162, 11400000.0, 0.69),
    ("OPP-9016", "ACC-106", "Nordic Telecom Infrastructure", "EMEA", "Telecommunications", "Zero-Touch NOC Automation", "Stage 4 - Commercial Negotiation", 128500000.0, 42800000.0, 95, 0.61, "2026-07-02", "2026-10-11", "2026-10-11", "Elena Rostova", "Regime_2_Margin_Compression", 0.334, 0.271, 16200000.0, 0.81),
    ("OPP-9017", "ACC-107", "Helios Semiconductor Foundry", "APAC", "High Tech", "Yield AI & Fab MES Spine", "Stage 5 - Contracting", 310000000.0, 77500000.0, 41, 0.84, "2026-09-01", "2026-10-13", "2026-10-13", "Kenji Takahashi", "Regime_1_High_Velocity_Expansion", 0.438, 0.399, 22000000.0, 0.94),
    ("OPP-9018", "ACC-108", "Continental Logistics Network", "Latin America", "Transportation", "Fleet Route Optimization", "Stage 3 - Solutioning", 54000000.0, 18000000.0, 112, 0.33, "2026-06-18", "2026-09-10", "2026-09-15", "Sofia Mendoza", "Regime_3_Stalled_Procurement", 0.241, 0.148, 8900000.0, 0.58),
    ("OPP-9019", "ACC-109", "Orion Sovereign Wealth Partners", "EMEA", "Financial Services", "Private Markets Risk Mesh", "Stage 2 - Qualification", 88000000.0, 29300000.0, 32, 0.47, "2026-09-08", "2026-09-22", "2026-09-23", "Elena Rostova", "Regime_1_High_Velocity_Expansion", 0.389, 0.352, 6100000.0, 0.87),
    ("OPP-9020", "ACC-110", "Titan Heavy Industrials", "North America", "Industrial Manufacturing", "Legacy Mainframe Offload", "Stage 3 - Solutioning", 510000000.0, 102000000.0, 129, 0.35, "2026-05-28", "2026-09-25", "2026-09-26", "David Thorne", "Regime_3_Stalled_Procurement", 0.264, 0.179, 84000000.0, 0.64),
    ("OPP-9021", "ACC-111", "Aether Cloud Media Group", "North America", "Media & Entertainment", "AdTech Real-Time Bidding AI", "Stage 1 - Discovery", 42000000.0, 14000000.0, 27, 0.25, "2026-09-14", "2026-09-18", "2026-09-18", "Marcus Vance", "Regime_2_Margin_Compression", 0.225, 0.139, 5400000.0, 0.55),
    ("OPP-9022", "ACC-112", "Borealis National Healthcare", "North America", "Healthcare Payer", "Claims Adjudication Copilot", "Stage 4 - Commercial Negotiation", 164000000.0, 54600000.0, 77, 0.72, "2026-07-24", "2026-10-12", "2026-10-12", "David Thorne", "Regime_1_High_Velocity_Expansion", 0.395, 0.358, 12900000.0, 0.89),
]


PRICING_SCENARIOS_SEED = [
    ("PRC-301", "OPP-9011", "v4_Final_BAFO", 142000000.0, 18400000.0, 123600000.0, 0.342, 0.289, 0.274, 0.145, 245.0, 198.0, 1.38, 0.82),
    ("PRC-302", "OPP-9012", "v3_Target_Margin", 96500000.0, 9200000.0, 87300000.0, 0.365, 0.331, 0.324, 0.085, 260.0, 232.0, 0.92, 0.88),
    ("PRC-303", "OPP-9013", "v4_Executive_Approved", 215000000.0, 14500000.0, 200500000.0, 0.412, 0.378, 0.371, 0.062, 295.0, 274.0, 0.74, 0.93),
    ("PRC-304", "OPP-9014", "v2_Aggressive_Share", 178000000.0, 29800000.0, 148200000.0, 0.295, 0.214, 0.192, 0.210, 240.0, 179.0, 2.15, 0.61),
    ("PRC-305", "OPP-9015", "v1_Initial_Bid", 64000000.0, 11400000.0, 52600000.0, 0.278, 0.162, 0.149, 0.245, 210.0, 154.0, 2.42, 0.59),
    ("PRC-306", "OPP-9016", "v3_Cola_Adjusted", 128500000.0, 16200000.0, 112300000.0, 0.334, 0.271, 0.262, 0.130, 250.0, 208.0, 1.29, 0.81),
    ("PRC-307", "OPP-9017", "v4_Value_Based_Gain", 310000000.0, 22000000.0, 288000000.0, 0.438, 0.399, 0.392, 0.055, 315.0, 296.0, 0.68, 0.95),
    ("PRC-308", "OPP-9018", "v2_Floor_Exception", 54000000.0, 8900000.0, 45100000.0, 0.241, 0.148, 0.131, 0.265, 195.0, 138.0, 2.68, 0.52),
    ("PRC-309", "OPP-9019", "v1_Standard_Card", 88000000.0, 6100000.0, 81900000.0, 0.389, 0.352, 0.346, 0.070, 275.0, 251.0, 0.81, 0.90),
    ("PRC-310", "OPP-9020", "v3_Mega_Deal_Cap", 510000000.0, 84000000.0, 426000000.0, 0.264, 0.179, 0.158, 0.230, 235.0, 172.0, 2.31, 0.63),
    ("PRC-311", "OPP-9021", "v1_Discovery_Card", 42000000.0, 5400000.0, 36600000.0, 0.225, 0.139, 0.122, 0.280, 190.0, 132.0, 2.79, 0.49),
    ("PRC-312", "OPP-9022", "v4_Outcome_Capped", 164000000.0, 12900000.0, 151100000.0, 0.395, 0.358, 0.351, 0.075, 280.0, 258.0, 0.79, 0.91),
]


DELIVERY_HEALTH_SEED = [
    ("DLV-501", "ACC-101", "Apex Global Banking Corp", "AMBER", 2, -0.024, 0.91, 14, "Client security review delayed vector DB egress approval by 3 weeks; rate card holding firm."),
    ("DLV-502", "ACC-102", "Vanguard Sovereign Energy", "GREEN", 0, 0.012, 0.96, 4, "All clean-core milestones ahead of schedule; client CFO requested Phase 2 expansion proposal."),
    ("DLV-503", "ACC-103", "Meridian BioPharma Holdings", "GREEN", 0, 0.008, 0.97, 2, "GxP validation pipeline passed audit with zero findings; strong pull-through for clinical AI."),
    ("DLV-504", "ACC-104", "Stratos Aerospace & Defense", "RED", 5, -0.068, 0.82, 31, "Severe shortage of cleared digital-twin architects; unbilled change request backlog of $4.2M."),
    ("DLV-505", "ACC-105", "Pacifica Omni-Retail Group", "AMBER", 3, -0.041, 0.86, 19, "Subcontractor cloud consumption overrun; margin leakage concentrated in non-billable POCs."),
    ("DLV-506", "ACC-106", "Nordic Telecom Infrastructure", "AMBER", 1, -0.015, 0.92, 9, "COLA inflation cap of 3.0% in legacy MSA is compressing onshore engineering margin by 280 bps."),
    ("DLV-507", "ACC-107", "Helios Semiconductor Foundry", "GREEN", 0, 0.019, 0.98, 1, "Fab telemetry model delivered 4.1% wafer yield uplift in pilot; executive sponsor highly aligned."),
    ("DLV-508", "ACC-108", "Continental Logistics Network", "RED", 4, -0.059, 0.79, 27, "Scope creep on legacy telemetry adapters; fixed-price milestone #3 delayed 45 days."),
    ("DLV-509", "ACC-109", "Orion Sovereign Wealth Partners", "GREEN", 0, 0.005, 0.95, 5, "Advisory discovery phase on track; strong executive sponsor engagement."),
    ("DLV-510", "ACC-110", "Titan Heavy Industrials", "RED", 6, -0.074, 0.80, 38, "Procurement demanding 18% rate reduction and uncapped liability on mainframe cutover."),
    ("DLV-511", "ACC-111", "Aether Cloud Media Group", "AMBER", 2, -0.038, 0.84, 22, "Low delivery margin due to ad-hoc discounting without executive giveaway governance."),
    ("DLV-512", "ACC-112", "Borealis National Healthcare", "GREEN", 0, 0.011, 0.96, 3, "Prior-authorization copilot pilot achieved 99.2% clinical accuracy; zero SLA breaches."),
]


UNSTRUCTURED_NOTES_SEED = [
    ("DOC-701", "OPP-9011", "ACC-101", "CLM_Contract_Vault", "2026-09-28", "MSA Section 14.2: Annual COLA rate adjustment capped at 2.5% despite 6.1% regional wage inflation. Volume tier rebate of 4% triggers at $150M cumulative bookings.", "Rate Compression & COLA Cap"),
    ("DOC-702", "OPP-9011", "ACC-101", "Customer_Visit_Logs", "2026-10-04", "CTO stated internal AI platform team has hired 45 ML engineers and wants to transition from full turnkey managed services to co-engineering within 12 months.", "AI Self-Sufficiency Risk"),
    ("DOC-703", "OPP-9014", "ACC-104", "CLM_Contract_Vault", "2026-08-19", "SOW Amendment 4 contains unilateral termination-for-convenience with 15-day notice and zero wind-down fee recovery, plus most-favored-nation (MFN) rate clause.", "Toxic Commercial Clause"),
    ("DOC-704", "OPP-9016", "ACC-106", "Customer_Visit_Logs", "2026-10-06", "Group CIO emphasized that while competitor bid 14% lower on unit rates, they lack sovereign European NOC compliance. Willing to settle at 6% discount if SLA penalty cap is raised.", "Schelling Negotiation Focal Point"),
    ("DOC-705", "OPP-9020", "ACC-110", "CLM_Contract_Vault", "2026-09-15", "Draft Master Agreement demands fixed-price conversion of all T&M squads after Month 6 without baseline productivity re-estimation.", "Fixed-Price Conversion Risk"),
    ("DOC-706", "OPP-9020", "ACC-110", "Customer_Visit_Logs", "2026-09-29", "Procurement VP stalled Stage 3 sign-off awaiting Q4 board capex committee review; competitor offering $12M upfront transformation credit.", "Stalled Stage 3 Bottleneck"),
    ("DOC-707", "OPP-9013", "ACC-103", "Customer_Visit_Logs", "2026-10-09", "Chief Scientific Officer confirmed budget ring-fenced from R&D reallocation; requested accelerated Q1 onboarding of 30 bio-informatics data engineers.", "Expansion Pull-Through"),
    ("DOC-708", "OPP-9017", "ACC-107", "CLM_Contract_Vault", "2026-10-08", "Value-sharing addendum awards 15% performance bonus on verified fab yield gains above 2.5% baseline, offsetting initial 4% rate card concession.", "Outcome-Based Upside"),
]


EXTERNAL_MARKET_SIGNALS_SEED = [
    ("MKT-801", "ACC-101", "Apex Global Banking Corp", "Tech_Stack_Telemetry_Feed", "2026-10-09", 0.82, 88, 0.164, "Detected 62 new job postings for internal LangGraph/Vertex AI platform engineers and enterprise GPU cluster orchestration; high DIY AI self-sufficiency trajectory."),
    ("MKT-802", "ACC-102", "Vanguard Sovereign Energy", "Buyer_Intent_Signal_Stream", "2026-10-10", 0.24, 94, 0.112, "Massive intent spike (+310% 30-day surge) on 'SAP S/4HANA Clean Core', 'Substation Predictive Maintenance', and 'EU AI Act Grid Compliance'."),
    ("MKT-803", "ACC-103", "Meridian BioPharma Holdings", "Market_Financials_API", "2026-10-11", 0.35, 91, 0.228, "Q3 10-Q filing shows $1.4B increase in clinical trial digitization capex and 240 bps gross margin expansion."),
    ("MKT-804", "ACC-104", "Stratos Aerospace & Defense", "SEC_Regulatory_Filings", "2026-10-02", 0.48, 67, 0.094, "8-K filing discloses supply-chain restructuring charge of $180M and freeze on non-critical IT consulting spend through Q1."),
    ("MKT-805", "ACC-105", "Pacifica Omni-Retail Group", "Tech_Stack_Telemetry_Feed", "2026-10-07", 0.76, 72, 0.068, "Rapid internal adoption of open-source FinOps tooling; moderate risk of insourcing Level-1/2 cloud managed services."),
    ("MKT-806", "ACC-106", "Nordic Telecom Infrastructure", "Buyer_Intent_Signal_Stream", "2026-10-11", 0.31, 89, 0.141, "High buyer intent on 'Autonomous Telco NOC', 'Sovereign Cloud Compliance', and '5G Core Slicing Automation'."),
    ("MKT-807", "ACC-107", "Helios Semiconductor Foundry", "Market_Financials_API", "2026-10-12", 0.29, 96, 0.265, "Record $8.2B quarterly free cash flow; CEO earnings call highlighted strategic partnership reliance for fab data mesh."),
    ("MKT-808", "ACC-110", "Titan Heavy Industrials", "SEC_Regulatory_Filings", "2026-10-05", 0.69, 61, 0.072, "10-Q notes activist investor pressure to cut external SG&A and vendor contractor spend by 15% over 18 months."),
]


QUESTIONS_CATALOG: List[Dict[str, Any]] = [
    # -------------------------------------------------------------------------
    # TIER 1 (18%): Deterministic Parameterized SQL via MCP Toolbox (Questions 1-5)
    # -------------------------------------------------------------------------
    {
        "id": "Q-001",
        "priority": "P1-Now",
        "tier_code": "Tier 1",
        "tier_name": "Tier 1 (18%): Deterministic Parameterized SQL via MCP Toolbox",
        "persona": "Global Pipeline Operations Director",
        "domain_group": "Pipeline Velocity & Stage Bottlenecks",
        "question": "Which active opportunities are stalled in Stage 3 (Solutioning) for more than 90 days, ordered by Total Contract Value (TCV) and showing days since last stage progression?",
        "topology": "Internal Structured (BQ)",
        "sources": ["CRM_Opportunity_Spine", "Revenue_ODS_15TB"],
        "kpis": [
            "Stage_3_Age_Days = DATE_DIFF(CURRENT_DATE(), stage_entry_date, DAY)",
            "Stalled_TCV_At_Risk = SUM(IF(stage_name = 'Stage 3 - Solutioning' AND stage_age_days > 90, tcv_usd, 0))",
        ],
        "flags": [],
        "db_only_verdict": "PASS - Direct Parameterized SQL",
        "diagnosis": "100% deterministic filter, projection, and sort over canonical pipeline columns. Ideal for MCP Toolbox parameterized SQL (`get_stalled_stage_opportunities`) with zero LLM SQL hallucination risk.",
        "recommended_architecture": "Route directly through Google MCP Toolbox (`genai-toolbox`) bound to `v_gold_opportunity_spine` in BigQuery.",
        "sample_sql": """SELECT opp_id, account_name, region, industry, tcv_usd, acv_usd, stage_age_days, win_prob, deal_owner, markov_regime
FROM opportunities
WHERE stage_name LIKE 'Stage 3%' AND stage_age_days >= :min_days
ORDER BY tcv_usd DESC;""",
        "sample_tools_yaml": """  get_stalled_stage_opportunities:
    kind: bigquery-sql
    source: enterprise-commercial-bq
    description: Fetch opportunities stalled in a pipeline stage beyond a threshold of days.
    parameters:
      - name: min_days
        type: integer
        description: Minimum days stalled in stage (default 90).""",
    },
    {
        "id": "Q-002",
        "priority": "P1-Now",
        "tier_code": "Tier 1",
        "tier_name": "Tier 1 (18%): Deterministic Parameterized SQL via MCP Toolbox",
        "persona": "Regional Commercial Lead",
        "domain_group": "Regional Win Rate & Booking Velocity",
        "question": "Show our regional pipeline TCV, average win probability, and weighted bookings across North America, EMEA, APAC, and Latin America.",
        "topology": "Internal Structured (BQ)",
        "sources": ["CRM_Opportunity_Spine", "ERP_Financials_Ledger"],
        "kpis": [
            "Weighted_Pipeline_USD = SUM(tcv_usd * win_prob)",
            "Regional_Avg_Adjusted_Yield = AVG(adjusted_yield_v4)",
        ],
        "flags": [],
        "db_only_verdict": "PASS - Direct Parameterized SQL",
        "diagnosis": "Deterministic regional aggregation over verified Gold Spine measures. Requires no external APIs or stochastic simulation.",
        "recommended_architecture": "Execute parameterized MCP Toolbox tool `get_regional_win_rate_trends` against `v_gold_opportunity_spine`.",
        "sample_sql": """SELECT region,
       COUNT(*) AS deal_count,
       ROUND(SUM(tcv_usd) / 1e6, 2) AS total_tcv_millions,
       ROUND(AVG(win_prob) * 100, 1) AS avg_win_prob_pct,
       ROUND(SUM(tcv_usd * win_prob) / 1e6, 2) AS weighted_tcv_millions,
       ROUND(AVG(adjusted_yield_v4) * 100, 1) AS avg_adj_yield_pct
FROM opportunities
GROUP BY region
ORDER BY total_tcv_millions DESC;""",
        "sample_tools_yaml": """  get_regional_win_rate_trends:
    kind: bigquery-sql
    source: enterprise-commercial-bq
    description: Aggregate TCV, weighted bookings, and win rates by geographic region.""",
    },
    {
        "id": "Q-003",
        "priority": "P1-Now",
        "tier_code": "Tier 1",
        "tier_name": "Tier 1 (18%): Deterministic Parameterized SQL via MCP Toolbox",
        "persona": "Chief Revenue Officer (CRO)",
        "domain_group": "Mega-Deal Concentration & Top Deals",
        "question": "List the top 10 active deals by TCV across all regions along with their current stage, gross margin, and assigned deal owner.",
        "topology": "Internal Structured (BQ)",
        "sources": ["CRM_Opportunity_Spine", "Deal_Pricing_Engine"],
        "kpis": [
            "Top_N_Concentration_Share = SUM(Top_10_TCV) / SUM(Total_Pipeline_TCV)",
        ],
        "flags": [],
        "db_only_verdict": "PASS - Direct Parameterized SQL",
        "diagnosis": "Standard top-N ranking query on primary opportunity spine.",
        "recommended_architecture": "Execute MCP Toolbox tool `get_top_tcv_deals_by_region` with optional region parameter.",
        "sample_sql": """SELECT opp_id, account_name, region, stage_name,
       ROUND(tcv_usd / 1e6, 2) AS tcv_millions,
       ROUND(gross_margin_pct * 100, 1) AS gross_margin_pct,
       ROUND(adjusted_yield_v4 * 100, 1) AS adjusted_yield_pct,
       deal_owner
FROM opportunities
ORDER BY tcv_usd DESC
LIMIT 10;""",
        "sample_tools_yaml": """  get_top_tcv_deals_by_region:
    kind: bigquery-sql
    source: enterprise-commercial-bq
    description: Return top N opportunities ordered by TCV.""",
    },
    {
        "id": "Q-004",
        "priority": "P1-Now",
        "tier_code": "Tier 1",
        "tier_name": "Tier 1 (18%): Deterministic Parameterized SQL via MCP Toolbox",
        "persona": "Sales Governance Manager",
        "domain_group": "Pipeline Hygiene & Stale Ownership",
        "question": "Which opportunities have had zero deal owner activity or CRM update for more than 14 days prior to the current snapshot?",
        "topology": "Internal Structured (BQ)",
        "sources": ["CRM_Opportunity_Spine"],
        "kpis": [
            "Owner_Inactivity_Days = DATE_DIFF(DATE('2026-10-13'), DATE(last_owner_activity_date), DAY)",
        ],
        "flags": [],
        "db_only_verdict": "PASS - Direct Parameterized SQL",
        "diagnosis": "Deterministic date-diff hygiene check on opportunity audit timestamps.",
        "recommended_architecture": "Invoke MCP Toolbox `get_stale_owner_opportunities` and surface hygiene alerts.",
        "sample_sql": """SELECT opp_id, account_name, stage_name, deal_owner,
       last_owner_activity_date,
       CAST(julianday('2026-10-13') - julianday(last_owner_activity_date) AS INTEGER) AS inactive_days,
       ROUND(tcv_usd / 1e6, 2) AS tcv_millions
FROM opportunities
WHERE julianday('2026-10-13') - julianday(last_owner_activity_date) >= 14
ORDER BY inactive_days DESC;""",
        "sample_tools_yaml": """  get_stale_owner_opportunities:
    kind: bigquery-sql
    source: enterprise-commercial-bq
    description: Identify pipeline opportunities with no owner activity for >= N days.""",
    },
    {
        "id": "Q-005",
        "priority": "P2-Next",
        "tier_code": "Tier 1",
        "tier_name": "Tier 1 (18%): Deterministic Parameterized SQL via MCP Toolbox",
        "persona": "Service Line Managing Director",
        "domain_group": "Service Line Mix & ACV Breakdown",
        "question": "Break down active Annual Contract Value (ACV) and Total Contract Value (TCV) by industry vertical and service line.",
        "topology": "Internal Structured (BQ)",
        "sources": ["CRM_Opportunity_Spine", "Revenue_ODS_15TB"],
        "kpis": [
            "ACV_to_TCV_Velocity_Ratio = SAFE_DIVIDE(SUM(acv_usd), SUM(tcv_usd))",
        ],
        "flags": [],
        "db_only_verdict": "PASS - Direct Parameterized SQL",
        "diagnosis": "Clean dimensional group-by on curated Gold View columns.",
        "recommended_architecture": "Serve via MCP Toolbox parameterized dimensional aggregation over `v_gold_opportunity_spine`.",
        "sample_sql": """SELECT industry, service_line,
       COUNT(*) AS opps,
       ROUND(SUM(acv_usd) / 1e6, 2) AS total_acv_m,
       ROUND(SUM(tcv_usd) / 1e6, 2) AS total_tcv_m
FROM opportunities
GROUP BY industry, service_line
ORDER BY total_tcv_m DESC;""",
        "sample_tools_yaml": """  get_service_line_acv_mix:
    kind: bigquery-sql
    source: enterprise-commercial-bq
    description: Group ACV and TCV by industry vertical and service line.""",
    },

    # -------------------------------------------------------------------------
    # TIER 2 (30%): Semantic Layer (Dataplex KC DAX) + Gold Views + Simulator (Questions 6-13)
    # -------------------------------------------------------------------------
    {
        "id": "Q-006",
        "priority": "P1-Now",
        "tier_code": "Tier 2",
        "tier_name": "Tier 2 (30%): Semantic Layer (Dataplex KC DAX Formulas) + Pre-Computed Gold Views + Counterfactual Simulator",
        "persona": "Global Pricing & Margin VP",
        "domain_group": "Adjusted Yield DAX & Outlier Trimming",
        "question": "Calculate Adjusted Yield v1, v3, and v4 across our deal portfolio after stripping pass-through cloud/hardware costs, trimming top/bottom 5% outliers, and capping standard deviation sensitivity at 1.5 sigma.",
        "topology": "Internal Structured (BQ)",
        "sources": ["Deal_Pricing_Engine", "CRM_Opportunity_Spine", "ERP_Financials_Ledger"],
        "kpis": [
            "Adjusted_Yield_v1 = SAFE_DIVIDE(Gross_Margin_USD - PassThrough_Cost_USD, Net_Service_Revenue_USD)",
            "Adjusted_Yield_v3_Trimmed = PERCENTILE_CONT(Adjusted_Yield_v1, 0.05..0.95) OVER (PARTITION BY industry)",
            "Adjusted_Yield_v4_SigmaCapped = LEAST(GREATEST(Adjusted_Yield_v1, Mean_Yield - 1.5*StdDev_Yield), Mean_Yield + 1.5*StdDev_Yield)",
        ],
        "flags": ["Incomplete Schema Mapping"],
        "db_only_verdict": "PARTIAL - Requires Semantic DAX + Gold View",
        "diagnosis": "Raw LLM Text-to-SQL fails because 'Adjusted Yield v4' is a multi-stage proprietary DAX formula with pass-through deduction and 1.5-sigma clipping that does not exist as a raw column in the 15TB ODS.",
        "recommended_architecture": "Materialize the v1/v3/v4 DAX formulas inside BigQuery Gold View `v_gold_adjusted_yield_dax` and register business glossary lineage in Dataplex Knowledge Catalog.",
        "sample_sql": """SELECT p.opp_id, o.account_name, o.industry,
       ROUND(p.tcv_usd / 1e6, 2) AS tcv_m,
       ROUND(p.passthrough_cost_usd / 1e6, 2) AS passthrough_m,
       ROUND(p.gross_yield_v1 * 100, 1) AS gross_yield_v1_pct,
       ROUND(p.adjusted_yield_v3_trimmed * 100, 1) AS adj_yield_v3_trimmed_pct,
       ROUND(p.adjusted_yield_v4_sigma_capped * 100, 1) AS adj_yield_v4_sigma_pct,
       p.sigma_zscore
FROM pricing_scenarios p
JOIN opportunities o ON p.opp_id = o.opp_id
ORDER BY p.adjusted_yield_v4_sigma_capped ASC;""",
        "sample_tools_yaml": """  get_adjusted_yield_dax_metrics:
    kind: bigquery-sql
    source: enterprise-commercial-bq
    description: Query materialized Adjusted Yield v1/v3/v4 DAX metrics from Gold View.""",
    },
    {
        "id": "Q-007",
        "priority": "P1-Now",
        "tier_code": "Tier 2",
        "tier_name": "Tier 2 (30%): Semantic Layer (Dataplex KC DAX Formulas) + Pre-Computed Gold Views + Counterfactual Simulator",
        "persona": "Portfolio Strategy CFO",
        "domain_group": "Counterfactual Portfolio Pruning Simulator",
        "question": "If we systematically exit or re-price the bottom 20% lowest-yielding deals in our pipeline, what is the counterfactual impact on blended portfolio margin, total revenue retained, and freed-up delivery capacity?",
        "topology": "Internal Structured (BQ)",
        "sources": ["Deal_Pricing_Engine", "CRM_Opportunity_Spine", "Workforce_Skills_Graph"],
        "kpis": [
            "Baseline_Blended_Yield = SUM(Net_Margin_USD) / SUM(Net_Service_Rev_USD)",
            "Post_Cull_Blended_Yield = SUM(Net_Margin_USD WHERE Yield_Percentile > 0.20) / SUM(Net_Service_Rev_USD WHERE Yield_Percentile > 0.20)",
            "Margin_Bps_Uplift = (Post_Cull_Blended_Yield - Baseline_Blended_Yield) * 10000",
        ],
        "flags": ["Counterfactual / What-If Simulator Required"],
        "db_only_verdict": "PARTIAL - Requires Counterfactual Simulator",
        "diagnosis": "Static SQL only reports historical state. Answering 'what if we exit the bottom X% or reprice to floor Y%' requires a parameterized percentile-cull and elasticity simulator.",
        "recommended_architecture": "Combine MCP Toolbox Gold View query (`simulate_portfolio_margin_cull`) with the Python Counterfactual Monte Carlo Engine.",
        "sample_sql": """WITH ranked AS (
  SELECT o.opp_id, o.account_name, p.tcv_usd, p.net_service_rev_usd,
         p.adjusted_yield_v4_sigma_capped AS adj_yield,
         PERCENT_RANK() OVER (ORDER BY p.adjusted_yield_v4_sigma_capped ASC) AS yield_pct_rank
  FROM pricing_scenarios p
  JOIN opportunities o ON p.opp_id = o.opp_id
)
SELECT
  ROUND(AVG(adj_yield) * 100, 2) AS baseline_avg_yield_pct,
  ROUND(AVG(CASE WHEN yield_pct_rank >= 0.20 THEN adj_yield END) * 100, 2) AS post_exit_avg_yield_pct,
  ROUND(SUM(CASE WHEN yield_pct_rank < 0.20 THEN tcv_usd ELSE 0 END) / 1e6, 2) AS exited_tcv_millions,
  ROUND(SUM(CASE WHEN yield_pct_rank >= 0.20 THEN tcv_usd ELSE 0 END) / 1e6, 2) AS retained_tcv_millions
FROM ranked;""",
        "sample_tools_yaml": """  simulate_portfolio_margin_cull:
    kind: bigquery-sql
    source: enterprise-commercial-bq
    description: Simulate blended margin uplift when pruning bottom N% yield deals.""",
    },
    {
        "id": "Q-008",
        "priority": "P1-Now",
        "tier_code": "Tier 2",
        "tier_name": "Tier 2 (30%): Semantic Layer (Dataplex KC DAX Formulas) + Pre-Computed Gold Views + Counterfactual Simulator",
        "persona": "Commercial Data Science Lead",
        "domain_group": "Econometric & Markov Regime Modeling",
        "question": "Classify all active accounts into Hidden Markov Pricing Regimes (High-Velocity Expansion, Margin Compression, or Stalled Procurement) and show transition probabilities when discount concessions exceed 15%.",
        "topology": "Internal Structured (BQ)",
        "sources": ["Deal_Pricing_Engine", "CRM_Opportunity_Spine", "Revenue_ODS_15TB"],
        "kpis": [
            "Markov_Regime_State = ARGMAX_s P(S_t = s | Yield_Delta, Stage_Velocity, Giveaway_Pct)",
            "Compression_Transition_Prob = P(S_{t+1} = Margin_Compression | Discount_Pct > 0.15)",
        ],
        "flags": ["Missing ML / Econometric Model in DB", "Counterfactual / What-If Simulator Required"],
        "db_only_verdict": "PARTIAL - Requires Semantic DAX + Gold View",
        "diagnosis": "A relational database does not natively run Hidden Markov Baum-Welch / Viterbi state estimation at query time unless pre-materialized by BQML or a Python econometric pipeline.",
        "recommended_architecture": "Pre-compute Markov state probabilities in BigQuery ML / Python job into `v_gold_markov_regime_states` and expose transition shocks in the Tier-2 Simulator.",
        "sample_sql": """SELECT o.markov_regime,
       COUNT(*) AS deal_count,
       ROUND(SUM(o.tcv_usd) / 1e6, 2) AS regime_tcv_millions,
       ROUND(AVG(p.discount_giveaway_pct) * 100, 1) AS avg_giveaway_pct,
       ROUND(AVG(p.adjusted_yield_v4_sigma_capped) * 100, 1) AS avg_adj_yield_pct
FROM opportunities o
JOIN pricing_scenarios p ON o.opp_id = p.opp_id
GROUP BY o.markov_regime
ORDER BY regime_tcv_millions DESC;""",
        "sample_tools_yaml": """  get_markov_regime_distribution:
    kind: bigquery-sql
    source: enterprise-commercial-bq
    description: Retrieve Hidden Markov commercial regime states and giveaway averages.""",
    },
    {
        "id": "Q-009",
        "priority": "P1-Now",
        "tier_code": "Tier 2",
        "tier_name": "Tier 2 (30%): Semantic Layer (Dataplex KC DAX Formulas) + Pre-Computed Gold Views + Counterfactual Simulator",
        "persona": "Enterprise Deal Desk Lead",
        "domain_group": "6-Lever Win Probability Elasticity",
        "question": "Decompose deal win probability across the 6 commercial levers (Price Competitiveness, Executive Sponsor Alignment, Technical Differentiation, Delivery Track Record, Contracting Speed, and Partner Co-Sell) and simulate a +10% improvement in Price Competitiveness.",
        "topology": "Internal Structured (BQ)",
        "sources": ["CRM_Opportunity_Spine", "Deal_Pricing_Engine", "Delivery_Governance_Hub"],
        "kpis": [
            "Logit_Win_Prob = 1 / (1 + EXP(-(b0 + b1*Price_Score + b2*Sponsor_Alignment + b3*Delivery_SLA + b4*Stage_Velocity)))",
            "Elasticity_dWin_dPrice = b1 * Win_Prob * (1 - Win_Prob)",
        ],
        "flags": ["Missing ML / Econometric Model in DB", "Counterfactual / What-If Simulator Required"],
        "db_only_verdict": "PARTIAL - Requires Counterfactual Simulator",
        "diagnosis": "Calculating marginal win-rate elasticity across 6 interacting levers requires logistic regression coefficients stored in the Gold View plus an interactive perturbation engine.",
        "recommended_architecture": "Query baseline lever scores via MCP Toolbox `get_deal_win_lever_elasticity` and run the 6-Lever Logit Perturbation Simulator in the agent tier.",
        "sample_sql": """SELECT o.opp_id, o.account_name,
       ROUND(o.tcv_usd / 1e6, 2) AS tcv_m,
       ROUND(o.win_prob * 100, 1) AS baseline_win_prob_pct,
       ROUND(o.client_Temp_score * 100, 1) AS sponsor_alignment_score,
       ROUND(p.price_competitiveness_score * 100, 1) AS price_competitiveness_score,
       ROUND(MIN(0.96, o.win_prob + 0.085 * (1 - o.win_prob)) * 100, 1) AS simulated_win_prob_plus10_price_pct
FROM opportunities o
JOIN pricing_scenarios p ON o.opp_id = p.opp_id
ORDER BY o.tcv_usd DESC;""",
        "sample_tools_yaml": """  get_deal_win_lever_elasticity:
    kind: bigquery-sql
    source: enterprise-commercial-bq
    description: Fetch 6-lever deal win probability drivers and elasticity uplift.""",
    },
    {
        "id": "Q-010",
        "priority": "P2-Next",
        "tier_code": "Tier 2",
        "tier_name": "Tier 2 (30%): Semantic Layer (Dataplex KC DAX Formulas) + Pre-Computed Gold Views + Counterfactual Simulator",
        "persona": "Corporate FP&A Stress-Test Director",
        "domain_group": "Mega-Deal Loss & Concentration Stress Test",
        "question": "Run a downside stress test: if our single largest $510M mega-deal (OPP-9020) is lost or slips by two quarters, what happens to North America bookings coverage and blended delivery utilization?",
        "topology": "Internal Structured (BQ)",
        "sources": ["CRM_Opportunity_Spine", "ERP_Financials_Ledger", "Workforce_Skills_Graph"],
        "kpis": [
            "Stress_Coverage_Ratio = (Weighted_Pipeline_USD - MegaDeal_Weighted_USD) / Quarterly_Target_USD",
            "Bench_Utilization_Shock_Bps = -1 * (MegaDeal_FTE_Demand / Regional_Billable_Headcount) * 10000",
        ],
        "flags": ["Counterfactual / What-If Simulator Required"],
        "db_only_verdict": "PARTIAL - Requires Counterfactual Simulator",
        "diagnosis": "Requires counterfactual removal of specific mega-deal IDs and recomputation of regional target coverage and bench absorption.",
        "recommended_architecture": "Execute stress-test simulation over `v_gold_opportunity_spine` comparing baseline vs. ex-OPP-9020 scenarios.",
        "sample_sql": """SELECT
  ROUND(SUM(tcv_usd * win_prob) / 1e6, 2) AS baseline_weighted_pipeline_m,
  ROUND(SUM(CASE WHEN opp_id != 'OPP-9020' THEN tcv_usd * win_prob ELSE 0 END) / 1e6, 2) AS stressed_weighted_pipeline_m,
  ROUND(SUM(CASE WHEN opp_id = 'OPP-9020' THEN tcv_usd * win_prob ELSE 0 END) / 1e6, 2) AS mega_deal_exposure_m
FROM opportunities
WHERE region = 'North America';""",
        "sample_tools_yaml": """  simulate_megadeal_slippage_shock:
    kind: bigquery-sql
    source: enterprise-commercial-bq
    description: Compute weighted pipeline shock if a specified mega-deal slips or is lost.""",
    },
    {
        "id": "Q-011",
        "priority": "P2-Next",
        "tier_code": "Tier 2",
        "tier_name": "Tier 2 (30%): Semantic Layer (Dataplex KC DAX Formulas) + Pre-Computed Gold Views + Counterfactual Simulator",
        "persona": "Commercial Pricing Operations Lead",
        "domain_group": "Unapproved Giveaway & Margin Leakage",
        "question": "Quantify total commercial giveaway (rate card ceiling vs. negotiated bill rate excluding pass-through expenses) across deals where discount exceeds 15%.",
        "topology": "Internal Structured (BQ)",
        "sources": ["Deal_Pricing_Engine", "CRM_Opportunity_Spine"],
        "kpis": [
            "Rate_Card_Giveaway_USD = (standard_rate_usd - negotiated_rate_usd) / standard_rate_usd * net_service_rev_usd",
            "Net_Margin_Erosion_Bps = (gross_yield_v1 - adjusted_yield_v4_sigma_capped) * 10000",
        ],
        "flags": ["Incomplete Schema Mapping"],
        "db_only_verdict": "PARTIAL - Requires Semantic DAX + Gold View",
        "diagnosis": "Requires joining rate card baselines to final pricing scenarios while excluding hardware/cloud pass-through revenue.",
        "recommended_architecture": "Expose via `v_gold_adjusted_yield_dax` in Dataplex Knowledge Catalog with strict semantic definition of Net Service Revenue.",
        "sample_sql": """SELECT p.opp_id, o.account_name,
       p.standard_rate_usd, p.negotiated_rate_usd,
       ROUND(p.discount_giveaway_pct * 100, 1) AS giveaway_pct,
       ROUND((p.net_service_rev_usd * p.discount_giveaway_pct) / 1e6, 2) AS giveaway_leakage_millions
FROM pricing_scenarios p
JOIN opportunities o ON p.opp_id = o.opp_id
WHERE p.discount_giveaway_pct >= 0.15
ORDER BY giveaway_leakage_millions DESC;""",
        "sample_tools_yaml": """  get_commercial_giveaway_leakage:
    kind: bigquery-sql
    source: enterprise-commercial-bq
    description: Calculate dollar margin leakage from rate card giveaways > threshold.""",
    },
    {
        "id": "Q-012",
        "priority": "P2-Next",
        "tier_code": "Tier 2",
        "tier_name": "Tier 2 (30%): Semantic Layer (Dataplex KC DAX Formulas) + Pre-Computed Gold Views + Counterfactual Simulator",
        "persona": "Global Delivery Commercial Controller",
        "domain_group": "Sold Margin vs. Delivered EAC Variance",
        "question": "Which accounts exhibit the largest negative gap between Sold Margin in Deal_Pricing_Engine and actual Delivered EAC Margin in Delivery_Governance_Hub?",
        "topology": "Internal Structured (BQ)",
        "sources": ["Deal_Pricing_Engine", "Delivery_Governance_Hub", "ERP_Financials_Ledger"],
        "kpis": [
            "Sold_vs_Delivered_Variance_Bps = d.eac_margin_variance_pct * 10000",
            "Unbilled_Overrun_Exposure_USD = ABS(d.eac_margin_variance_pct) * p.net_service_rev_usd",
        ],
        "flags": ["Incomplete Schema Mapping"],
        "db_only_verdict": "PARTIAL - Requires Semantic DAX + Gold View",
        "diagnosis": "Pre-sales opportunity IDs and post-sales ERP project codes use disparate composite keys across systems; requires pre-joined entity resolution in `v_gold_account_360_health`.",
        "recommended_architecture": "Query `v_gold_account_360_health` via MCP Toolbox `get_account_360_composite_health`.",
        "sample_sql": """SELECT o.account_id, o.account_name, d.rag_status,
       ROUND(p.adjusted_yield_v4_sigma_capped * 100, 1) AS sold_adj_yield_pct,
       ROUND(d.eac_margin_variance_pct * 100, 1) AS eac_variance_pct,
       d.sla_slippage_days,
       ROUND(ABS(d.eac_margin_variance_pct) * p.net_service_rev_usd / 1e6, 2) AS margin_erosion_millions
FROM opportunities o
JOIN pricing_scenarios p ON o.opp_id = p.opp_id
JOIN delivery_health d ON o.account_id = d.account_id
WHERE d.eac_margin_variance_pct < 0
ORDER BY d.eac_margin_variance_pct ASC;""",
        "sample_tools_yaml": """  get_account_360_composite_health:
    kind: bigquery-sql
    source: enterprise-commercial-bq
    description: Join pre-sales pricing yield with post-sales delivery EAC margin variance.""",
    },
    {
        "id": "Q-013",
        "priority": "P3-Next",
        "tier_code": "Tier 2",
        "tier_name": "Tier 2 (30%): Semantic Layer (Dataplex KC DAX Formulas) + Pre-Computed Gold Views + Counterfactual Simulator",
        "persona": "Talent & Pyramid Optimization VP",
        "domain_group": "Pyramid Leverage & Rate Realization",
        "question": "Simulate the margin impact of shifting 15% of onshore principal hours to nearshore AI-augmented delivery pods across all Stage 3 and Stage 4 opportunities.",
        "topology": "Internal Structured (BQ)",
        "sources": ["Deal_Pricing_Engine", "Workforce_Skills_Graph"],
        "kpis": [
            "Pyramid_Mix_Savings_USD = Net_Service_Rev_USD * 0.15 * (1 - Nearshore_Cost_Ratio)",
            "Simulated_Yield_Post_Pyramid = Adjusted_Yield_v4 + 0.032",
        ],
        "flags": ["Counterfactual / What-If Simulator Required"],
        "db_only_verdict": "PARTIAL - Requires Counterfactual Simulator",
        "diagnosis": "Requires dynamic cost-rate substitution in the pricing model rather than static table retrieval.",
        "recommended_architecture": "Invoke the Tier-2 Python Counterfactual Simulator over `pricing_scenarios`.",
        "sample_sql": """SELECT o.opp_id, o.account_name, o.stage_name,
       ROUND(p.adjusted_yield_v4_sigma_capped * 100, 1) AS current_yield_pct,
       ROUND((p.adjusted_yield_v4_sigma_capped + 0.032) * 100, 1) AS pyramid_shifted_yield_pct,
       ROUND(p.net_service_rev_usd * 0.032 / 1e6, 2) AS incremental_margin_millions
FROM opportunities o
JOIN pricing_scenarios p ON o.opp_id = p.opp_id
WHERE o.stage_name LIKE 'Stage 3%' OR o.stage_name LIKE 'Stage 4%'
ORDER BY incremental_margin_millions DESC;""",
        "sample_tools_yaml": """  simulate_pyramid_mix_shift:
    kind: bigquery-sql
    source: enterprise-commercial-bq
    description: Estimate margin expansion from nearshore pyramid mix optimization.""",
    },

    # -------------------------------------------------------------------------
    # TIER 3 (49%): Federated Multi-Tool Agent (SQL + Unstructured RAG + 3P Market APIs) (Questions 14-22)
    # -------------------------------------------------------------------------
    {
        "id": "Q-014",
        "priority": "P1-Now",
        "tier_code": "Tier 3",
        "tier_name": "Tier 3 (49%): Federated Multi-Tool Agent (Structured SQL + Unstructured CLM/Visit RAG + External Market Intelligence APIs)",
        "persona": "Strategic Account Executive",
        "domain_group": "Client AI Self-Sufficiency & Insourcing Risk",
        "question": "Which top accounts show high 'AI Self-Sufficiency / Insourcing Risk' based on external ML engineering hiring telemetry (`Tech_Stack_Telemetry_Feed`) combined with executive visit debrief notes (`Customer_Visit_Logs`), and how much active TCV is exposed?",
        "topology": "Hybrid (BQ + External/Unstructured)",
        "sources": ["CRM_Opportunity_Spine", "Tech_Stack_Telemetry_Feed", "Customer_Visit_Logs"],
        "kpis": [
            "AI_Insourcing_Exposure_USD = SUM(tcv_usd WHERE ai_self_sufficiency_index > 0.65)",
            "Composite_Insourcing_Risk_Score = 0.6 * ai_self_sufficiency_index + 0.4 * Unstructured_Sentiment_Risk",
        ],
        "flags": ["External 3P Market API Required", "Hidden Unstructured Notes in Tabular Source"],
        "db_only_verdict": "FAIL - Requires Unstructured RAG + 3P API",
        "diagnosis": "Internal CRM tables have zero visibility into a client's external ML job postings (`Tech_Stack_Telemetry_Feed`) or qualitative CTO statements in `Customer_Visit_Logs`.",
        "recommended_architecture": "Federated ADK Agent: (1) Query `CRM_Opportunity_Spine` via MCP Toolbox, (2) Fetch external hiring telemetry from `Tech_Stack_Telemetry_Feed`, (3) Run semantic search over `Customer_Visit_Logs`.",
        "sample_sql": """SELECT o.opp_id, o.account_name, ROUND(o.tcv_usd / 1e6, 2) AS tcv_m,
       m.ai_self_sufficiency_index, m.signal_summary,
       u.extracted_risk_tag, u.note_snippet
FROM opportunities o
JOIN external_market_signals m ON o.account_id = m.account_id
LEFT JOIN unstructured_deal_notes u ON o.opp_id = u.opp_id
WHERE m.ai_self_sufficiency_index >= 0.60
ORDER BY m.ai_self_sufficiency_index DESC;""",
        "sample_tools_yaml": """  get_ai_insourcing_risk_signals:
    kind: bigquery-sql
    source: enterprise-commercial-bq
    description: Federate internal opportunity TCV with external tech-stack telemetry and visit notes.""",
    },
    {
        "id": "Q-015",
        "priority": "P1-Now",
        "tier_code": "Tier 3",
        "tier_name": "Tier 3 (49%): Federated Multi-Tool Agent (Structured SQL + Unstructured CLM/Visit RAG + External Market Intelligence APIs)",
        "persona": "Commercial Legal & Pricing Counsel",
        "domain_group": "Contractual COLA Caps & Toxic Clauses",
        "question": "Cross-reference our active Stage 3-4 deals against executed MSAs in `CLM_Contract_Vault` to identify accounts where COLA inflation caps (<3%) or termination-for-convenience clauses threaten Adjusted Yield v4.",
        "topology": "Hybrid (BQ + External/Unstructured)",
        "sources": ["Deal_Pricing_Engine", "CLM_Contract_Vault", "CRM_Opportunity_Spine"],
        "kpis": [
            "Inflation_Unrecovered_Bps = MAX(0, Regional_Wage_Inflation_Pct - MSA_COLA_Cap_Pct) * 10000",
        ],
        "flags": ["Hidden Unstructured Notes in Tabular Source"],
        "db_only_verdict": "FAIL - Requires Unstructured RAG + 3P API",
        "diagnosis": "COLA caps, MFN clauses, and termination-for-convenience penalties live inside unstructured PDF contract clauses in `CLM_Contract_Vault`, not in structured ERP columns.",
        "recommended_architecture": "Hybrid Retrieval: MCP Toolbox fetches deal margins from `Deal_Pricing_Engine` while Vertex AI RAG extracts legal clauses from `CLM_Contract_Vault`.",
        "sample_sql": """SELECT o.opp_id, o.account_name, o.stage_name,
       ROUND(o.tcv_usd / 1e6, 2) AS tcv_m,
       ROUND(p.adjusted_yield_v4_sigma_capped * 100, 1) AS adj_yield_pct,
       u.extracted_risk_tag, u.note_snippet
FROM opportunities o
JOIN pricing_scenarios p ON o.opp_id = p.opp_id
JOIN unstructured_deal_notes u ON o.opp_id = u.opp_id
WHERE u.source_system = 'CLM_Contract_Vault';""",
        "sample_tools_yaml": """  search_clm_contract_clauses:
    kind: bigquery-sql
    source: enterprise-commercial-bq
    description: Retrieve extracted MSA/SOW risk clauses joined with deal pricing scenarios.""",
    },
    {
        "id": "Q-016",
        "priority": "P1-Now",
        "tier_code": "Tier 3",
        "tier_name": "Tier 3 (49%): Federated Multi-Tool Agent (Structured SQL + Unstructured CLM/Visit RAG + External Market Intelligence APIs)",
        "persona": "Competitive Intelligence & Pricing Lead",
        "domain_group": "Competitor Rate Benchmarking (Compliance Guard)",
        "question": "Synthesize competitor hourly rate cards and market-share tables from `Analyst_Benchmark_Feed_Unlicensed` to recommend unit-rate cuts on our top 5 deals.",
        "topology": "External / Market Only",
        "sources": ["Analyst_Benchmark_Feed_Unlicensed", "Deal_Pricing_Engine"],
        "kpis": [
            "Governance_Compliance_Check = MIN(genai_usage_rights) OVER (Selected_Sources)",
        ],
        "flags": ["License Compliance Blocker (GenAI Rights: No)", "External 3P Market API Required"],
        "db_only_verdict": "BLOCKED - GenAI License Compliance Guard",
        "diagnosis": "CRITICAL COMPLIANCE VIOLATION: `Analyst_Benchmark_Feed_Unlicensed` carries `genai_usage_rights = False` in Dataplex Knowledge Catalog. Passing its rows into an LLM prompt violates 3P syndication licensing.",
        "recommended_architecture": "Pre-flight Dataplex Governance Guard (`check_source_genai_compliance`) intercepts the query, blocks LLM ingestion of `Analyst_Benchmark_Feed_Unlicensed`, and substitutes clean internal `Deal_Pricing_Engine` historical win/loss elasticity.",
        "sample_sql": """SELECT source_id, source_name, category, genai_usage_rights, pii_classification, steward_team, notes
FROM data_source_governance
WHERE source_name = 'Analyst_Benchmark_Feed_Unlicensed';""",
        "sample_tools_yaml": """  check_source_genai_compliance:
    kind: bigquery-sql
    source: enterprise-commercial-bq
    description: Verify Dataplex GenAI usage rights before routing data to Vertex AI LLM prompts.""",
    },
    {
        "id": "Q-017",
        "priority": "P1-Now",
        "tier_code": "Tier 3",
        "tier_name": "Tier 3 (49%): Federated Multi-Tool Agent (Structured SQL + Unstructured CLM/Visit RAG + External Market Intelligence APIs)",
        "persona": "Mega-Deal Negotiation Strategist",
        "domain_group": "Game-Theoretic Schelling Focal Point Synthesis",
        "question": "For our €128.5M Nordic Telecom deal (OPP-9016), combine our internal floor margin (`Deal_Pricing_Engine`), sovereign NOC differentiation notes (`Customer_Visit_Logs`), and external buyer intent (`Buyer_Intent_Signal_Stream`) to compute the Schelling negotiation focal point.",
        "topology": "Hybrid (BQ + External/Unstructured)",
        "sources": ["Deal_Pricing_Engine", "Customer_Visit_Logs", "Buyer_Intent_Signal_Stream"],
        "kpis": [
            "Schelling_Focal_Discount_Pct = (Client_Target_Discount + Provider_Walkaway_Floor) / 2 * Differentiation_Weight",
            "Expected_Value_At_Focal_Point = TCV_Focal * P(Win | Focal_Discount) * Yield_Focal",
        ],
        "flags": [
            "Missing ML / Econometric Model in DB",
            "Hidden Unstructured Notes in Tabular Source",
            "External 3P Market API Required",
        ],
        "db_only_verdict": "FAIL - Requires Unstructured RAG + 3P API",
        "diagnosis": "Computing a bargaining focal point requires synthesizing structured floor margins, unstructured CIO sentiment from visit notes, and external buyer urgency scores.",
        "recommended_architecture": "Federated Multi-Tool Agent orchestrates SQL pricing lookup + RAG visit note extraction + Game-Theoretic Nash/Schelling solver in Python.",
        "sample_sql": """SELECT o.opp_id, o.account_name, o.tcv_usd,
       p.standard_rate_usd, p.negotiated_rate_usd, p.adjusted_yield_v4_sigma_capped,
       u.note_snippet AS cio_visit_intelligence,
       m.intent_surge_score, m.signal_summary
FROM opportunities o
JOIN pricing_scenarios p ON o.opp_id = p.opp_id
LEFT JOIN unstructured_deal_notes u ON o.opp_id = u.opp_id
LEFT JOIN external_market_signals m ON o.account_id = m.account_id
WHERE o.opp_id = 'OPP-9016';""",
        "sample_tools_yaml": """  get_schelling_negotiation_context:
    kind: bigquery-sql
    source: enterprise-commercial-bq
    description: Assemble pricing floor, CIO visit notes, and intent surge for negotiation modeling.""",
    },
    {
        "id": "Q-018",
        "priority": "P2-Next",
        "tier_code": "Tier 3",
        "tier_name": "Tier 3 (49%): Federated Multi-Tool Agent (Structured SQL + Unstructured CLM/Visit RAG + External Market Intelligence APIs)",
        "persona": "Account Growth Director",
        "domain_group": "White-Space ABM & Intent Surge Matching",
        "question": "Which accounts have an external `Buyer_Intent_Signal_Stream` surge score above 85 or strong R&D capex expansion in `Market_Financials_API`, and how does that compare to our current pipeline stage and delivery health?",
        "topology": "Hybrid (BQ + External/Unstructured)",
        "sources": ["Buyer_Intent_Signal_Stream", "Market_Financials_API", "CRM_Opportunity_Spine", "Delivery_Governance_Hub"],
        "kpis": [
            "Account_Expansion_Propensity = 0.5 * (intent_surge_score / 100) + 0.3 * client_rd_intensity_pct + 0.2 * csat_index",
        ],
        "flags": ["External 3P Market API Required"],
        "db_only_verdict": "FAIL - Requires Unstructured RAG + 3P API",
        "diagnosis": "Requires joining external B2B intent streams and quarterly 10-Q R&D ratios with internal CRM and delivery CSAT scores.",
        "recommended_architecture": "Federated Agent queries `external_market_signals` and joins with `v_gold_account_360_health`.",
        "sample_sql": """SELECT o.account_name, o.stage_name, ROUND(o.tcv_usd / 1e6, 2) AS tcv_m,
       d.rag_status, d.csat_score,
       m.signal_source, m.intent_surge_score,
       ROUND(m.client_rd_intensity_pct * 100, 1) AS rd_intensity_pct,
       m.signal_summary
FROM opportunities o
JOIN delivery_health d ON o.account_id = d.account_id
JOIN external_market_signals m ON o.account_id = m.account_id
WHERE m.intent_surge_score >= 85
ORDER BY m.intent_surge_score DESC;""",
        "sample_tools_yaml": """  get_intent_surge_whitespace_accounts:
    kind: bigquery-sql
    source: enterprise-commercial-bq
    description: Match external buyer intent surge and 10-Q R&D signals with internal delivery health.""",
    },
    {
        "id": "Q-019",
        "priority": "P2-Next",
        "tier_code": "Tier 3",
        "tier_name": "Tier 3 (49%): Federated Multi-Tool Agent (Structured SQL + Unstructured CLM/Visit RAG + External Market Intelligence APIs)",
        "persona": "Enterprise Risk & Portfolio Officer",
        "domain_group": "SEC 8-K Restructuring & Pipeline Freeze Contagion",
        "question": "Scan `SEC_Regulatory_Filings` for 8-K/10-Q restructuring charges or vendor spend freezes among our clients and quantify the immediate pipeline TCV and red-account delivery exposure.",
        "topology": "Hybrid (BQ + External/Unstructured)",
        "sources": ["SEC_Regulatory_Filings", "CRM_Opportunity_Spine", "Delivery_Governance_Hub"],
        "kpis": [
            "Macro_Contagion_TCV_USD = SUM(tcv_usd WHERE SEC_Filing_Sentiment = 'Spend_Freeze')",
        ],
        "flags": ["External 3P Market API Required", "Hidden Unstructured Notes in Tabular Source"],
        "db_only_verdict": "FAIL - Requires Unstructured RAG + 3P API",
        "diagnosis": "Client 8-K restructuring disclosures and activist investor demands occur in external SEC filings long before sales reps downgrade CRM win probabilities.",
        "recommended_architecture": "Early-Warning Federated Agent joins `SEC_Regulatory_Filings` alerts with `CRM_Opportunity_Spine` and `Delivery_Governance_Hub`.",
        "sample_sql": """SELECT o.opp_id, o.account_name, o.stage_name,
       ROUND(o.tcv_usd / 1e6, 2) AS tcv_m,
       o.win_prob AS crm_win_prob,
       d.rag_status,
       m.signal_summary AS sec_filing_alert
FROM opportunities o
JOIN delivery_health d ON o.account_id = d.account_id
JOIN external_market_signals m ON o.account_id = m.account_id
WHERE m.signal_source = 'SEC_Regulatory_Filings';""",
        "sample_tools_yaml": """  get_sec_filing_pipeline_exposure:
    kind: bigquery-sql
    source: enterprise-commercial-bq
    description: Cross-reference SEC 8-K/10-Q restructuring alerts with active pipeline TCV.""",
    },
    {
        "id": "Q-020",
        "priority": "P2-Next",
        "tier_code": "Tier 3",
        "tier_name": "Tier 3 (49%): Federated Multi-Tool Agent (Structured SQL + Unstructured CLM/Visit RAG + External Market Intelligence APIs)",
        "persona": "Global Delivery Excellence Lead",
        "domain_group": "Unstructured Delivery Logs & Change-Order Recovery",
        "question": "Analyze unstructured delivery director commentary in `Delivery_Governance_Hub` alongside contract terms in `CLM_Contract_Vault` to diagnose why RED accounts are experiencing negative EAC margin variance.",
        "topology": "Hybrid (BQ + External/Unstructured)",
        "sources": ["Delivery_Governance_Hub", "CLM_Contract_Vault", "Deal_Pricing_Engine"],
        "kpis": [
            "Recoverable_Change_Order_USD = Unbilled_Backlog_USD * Clause_Enforceability_Score",
        ],
        "flags": ["Hidden Unstructured Notes in Tabular Source"],
        "db_only_verdict": "FAIL - Requires Unstructured RAG + 3P API",
        "diagnosis": "The root cause of RED delivery status (e.g., cleared architect shortages, unbilled change orders, fixed-price conversion traps) is embedded in free-text commentary and SOW clauses.",
        "recommended_architecture": "Combine SQL filter on `rag_status = 'RED'` with semantic synthesis over `delivery_commentary` and `CLM_Contract_Vault` notes.",
        "sample_sql": """SELECT d.account_name, d.rag_status, d.milestone_delays,
       ROUND(d.eac_margin_variance_pct * 100, 1) AS eac_var_pct,
       d.sla_slippage_days, d.delivery_commentary,
       u.extracted_risk_tag, u.note_snippet AS contract_clause_note
FROM delivery_health d
LEFT JOIN unstructured_deal_notes u ON d.account_id = u.account_id
WHERE d.rag_status = 'RED';""",
        "sample_tools_yaml": """  diagnose_red_delivery_accounts:
    kind: bigquery-sql
    source: enterprise-commercial-bq
    description: Fetch RED delivery accounts with free-text director logs and contract risk clauses.""",
    },
    {
        "id": "Q-021",
        "priority": "P3-Next",
        "tier_code": "Tier 3",
        "tier_name": "Tier 3 (49%): Federated Multi-Tool Agent (Structured SQL + Unstructured CLM/Visit RAG + External Market Intelligence APIs)",
        "persona": "Outcome-Based Pricing Architect",
        "domain_group": "Value-Sharing & Gain-Share Structuring",
        "question": "Identify accounts where high client R&D intensity (`Market_Financials_API`) and strong delivery CSAT (`Delivery_Governance_Hub`) support converting standard T&M rate cards into outcome-based gain-share contracts (`CLM_Contract_Vault`).",
        "topology": "Hybrid (BQ + External/Unstructured)",
        "sources": ["Market_Financials_API", "Delivery_Governance_Hub", "CLM_Contract_Vault", "Deal_Pricing_Engine"],
        "kpis": [
            "Gain_Share_Upside_Yield = Adjusted_Yield_v4 + (Verified_KPI_Uplift * Bonus_Pool_Share)",
        ],
        "flags": ["External 3P Market API Required", "Hidden Unstructured Notes in Tabular Source"],
        "db_only_verdict": "FAIL - Requires Unstructured RAG + 3P API",
        "diagnosis": "Requires combining external client cash-flow/R&D posture with internal delivery reliability and precedent gain-share language in CLM.",
        "recommended_architecture": "Federated Agent queries `Market_Financials_API` + `Delivery_Governance_Hub` + `CLM_Contract_Vault` exemplars.",
        "sample_sql": """SELECT o.opp_id, o.account_name, o.service_line,
       ROUND(o.tcv_usd / 1e6, 2) AS tcv_m,
       ROUND(p.adjusted_yield_v4_sigma_capped * 100, 1) AS adj_yield_pct,
       d.csat_score, d.delivery_commentary,
       m.client_rd_intensity_pct, m.signal_summary
FROM opportunities o
JOIN pricing_scenarios p ON o.opp_id = p.opp_id
JOIN delivery_health d ON o.account_id = d.account_id
JOIN external_market_signals m ON o.account_id = m.account_id
WHERE d.csat_score >= 0.90
ORDER BY m.client_rd_intensity_pct DESC;""",
        "sample_tools_yaml": """  find_outcome_based_pricing_candidates:
    kind: bigquery-sql
    source: enterprise-commercial-bq
    description: Identify high-CSAT, high-R&D accounts suited for gain-share commercial models.""",
    },
    {
        "id": "Q-022",
        "priority": "P4-Next",
        "tier_code": "Tier 3",
        "tier_name": "Tier 3 (49%): Federated Multi-Tool Agent (Structured SQL + Unstructured CLM/Visit RAG + External Market Intelligence APIs)",
        "persona": "Corporate M&A & Ecosystem Strategy Lead",
        "domain_group": "Unmapped Ecosystem Partner Influence",
        "question": "Quantify how co-sell hyperscaler commit drawdown speed correlates with competitor displacement across unmapped regional partner registries.",
        "topology": "Unmapped Spec",
        "sources": ["CRM_Opportunity_Spine", "AI_Web_Synthesis_Engine"],
        "kpis": [
            "Partner_Commit_Burn_Multiplier = CoSell_Win_Rate / Solo_Win_Rate",
        ],
        "flags": ["Incomplete Schema Mapping", "External 3P Market API Required"],
        "db_only_verdict": "FAIL - Requires Unstructured RAG + 3P API",
        "diagnosis": "Hyperscaler private-offer drawdown telemetry is currently unmapped in the internal ODS schema; requires schema onboarding into Dataplex plus external web synthesis.",
        "recommended_architecture": "Flag as P4 Schema Onboarding gap in Dataplex Knowledge Catalog; provide proxy pipeline correlation from `CRM_Opportunity_Spine`.",
        "sample_sql": """SELECT service_line, COUNT(*) AS deals,
       ROUND(AVG(win_prob) * 100, 1) AS avg_win_prob_pct,
       ROUND(SUM(tcv_usd) / 1e6, 2) AS total_tcv_m
FROM opportunities
GROUP BY service_line;""",
        "sample_tools_yaml": """  get_partner_cosell_proxy_metrics:
    kind: bigquery-sql
    source: enterprise-commercial-bq
    description: Proxy service-line win rates while Partner Drawdown schema is onboarded.""",
    },

    # -------------------------------------------------------------------------
    # TIER 4 (3%): Multi-System Action & Executive Briefing Automation (Questions 23-24)
    # -------------------------------------------------------------------------
    {
        "id": "Q-023",
        "priority": "P3-Next",
        "tier_code": "Tier 4",
        "tier_name": "Tier 4 (3%): Multi-System Action & Executive Briefing Automation",
        "persona": "Executive Client Sponsor (MD)",
        "domain_group": "Automated Executive QBR Briefing Generation",
        "question": "Generate an executive-ready Quarterly Business Review (QBR) briefing packet for Apex Global Banking Corp (ACC-101) combining pipeline TCV, Adjusted Yield v4, delivery SLA health, contract COLA risks, and external AI hiring signals.",
        "topology": "Hybrid (BQ + External/Unstructured)",
        "sources": [
            "CRM_Opportunity_Spine",
            "Deal_Pricing_Engine",
            "Delivery_Governance_Hub",
            "CLM_Contract_Vault",
            "Customer_Visit_Logs",
            "Tech_Stack_Telemetry_Feed",
        ],
        "kpis": [
            "Account_360_Composite_Health = 0.35*Yield_Index + 0.35*Delivery_CSAT + 0.30*(1 - AI_Insourcing_Risk)",
        ],
        "flags": ["Hidden Unstructured Notes in Tabular Source", "External 3P Market API Required"],
        "db_only_verdict": "FAIL - Requires Multi-System Action Orchestration",
        "diagnosis": "Requires multi-source synthesis across 6 structured, unstructured, and 3P systems followed by structured artifact formatting for executive consumption.",
        "recommended_architecture": "Tier-4 Action Orchestrator: Invoke Account 360 Federated Toolset + synthesize executive briefing markdown/slides packet.",
        "sample_sql": """SELECT o.opp_id, o.account_name, o.stage_name, o.tcv_usd,
       p.adjusted_yield_v4_sigma_capped, p.discount_giveaway_pct,
       d.rag_status, d.csat_score, d.delivery_commentary,
       m.ai_self_sufficiency_index, m.signal_summary
FROM opportunities o
JOIN pricing_scenarios p ON o.opp_id = p.opp_id
JOIN delivery_health d ON o.account_id = d.account_id
LEFT JOIN external_market_signals m ON o.account_id = m.account_id
WHERE o.account_id = 'ACC-101';""",
        "sample_tools_yaml": """  assemble_executive_qbr_dossier:
    kind: bigquery-sql
    source: enterprise-commercial-bq
    description: Aggregate full Account 360 telemetry for executive QBR generation.""",
    },
    {
        "id": "Q-024",
        "priority": "P3-Next",
        "tier_code": "Tier 4",
        "tier_name": "Tier 4 (3%): Multi-System Action & Executive Briefing Automation",
        "persona": "Global Deal Pursuit Director",
        "domain_group": "Pre-Call SME Mobilization & Action Dispatch",
        "question": "For all RED delivery accounts with active Stage 3 opportunities > $150M, match required architectural skills from `Workforce_Skills_Graph` and generate a pre-call intervention action plan.",
        "topology": "Hybrid (BQ + External/Unstructured)",
        "sources": [
            "CRM_Opportunity_Spine",
            "Delivery_Governance_Hub",
            "Workforce_Skills_Graph",
            "CLM_Contract_Vault",
        ],
        "kpis": [
            "At_Risk_MegaDeal_TCV_USD = SUM(tcv_usd WHERE rag_status = 'RED' AND tcv_usd > 150000000)",
        ],
        "flags": ["Hidden Unstructured Notes in Tabular Source"],
        "db_only_verdict": "FAIL - Requires Multi-System Action Orchestration",
        "diagnosis": "Combines structured deal/delivery filtering with unstructured bottleneck diagnosis and downstream mobilization workflow generation.",
        "recommended_architecture": "Tier-4 Multi-System Agent: Query at-risk mega-deals, extract delivery/contract bottlenecks, and trigger SME mobilization workflow.",
        "sample_sql": """SELECT o.opp_id, o.account_name, o.service_line,
       ROUND(o.tcv_usd / 1e6, 2) AS tcv_millions,
       d.rag_status, d.sla_slippage_days, d.delivery_commentary
FROM opportunities o
JOIN delivery_health d ON o.account_id = d.account_id
WHERE d.rag_status = 'RED' AND o.tcv_usd >= 150000000
ORDER BY o.tcv_usd DESC;""",
        "sample_tools_yaml": """  mobilize_red_account_pursuit_squad:
    kind: bigquery-sql
    source: enterprise-commercial-bq
    description: Identify >$150M opportunities on RED delivery accounts for SME intervention.""",
    },
]


def build_sqlite_db() -> None:
    if DB_PATH.exists():
        DB_PATH.unlink()

    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE opportunities (
            opp_id TEXT PRIMARY KEY,
            account_id TEXT NOT NULL,
            account_name TEXT NOT NULL,
            region TEXT NOT NULL,
            industry TEXT NOT NULL,
            service_line TEXT NOT NULL,
            stage_name TEXT NOT NULL,
            tcv_usd REAL NOT NULL,
            acv_usd REAL NOT NULL,
            stage_age_days INTEGER NOT NULL,
            win_prob REAL NOT NULL,
            stage_entry_date TEXT NOT NULL,
            last_updated_date TEXT NOT NULL,
            last_owner_activity_date TEXT NOT NULL,
            deal_owner TEXT NOT NULL,
            markov_regime TEXT NOT NULL,
            gross_margin_pct REAL NOT NULL,
            adjusted_yield_v4 REAL NOT NULL,
            passthrough_cost_usd REAL NOT NULL,
            client_Temp_score REAL NOT NULL
        );
        """
    )

    cur.execute(
        """
        CREATE TABLE pricing_scenarios (
            scenario_id TEXT PRIMARY KEY,
            opp_id TEXT NOT NULL,
            version_tag TEXT NOT NULL,
            tcv_usd REAL NOT NULL,
            passthrough_cost_usd REAL NOT NULL,
            net_service_rev_usd REAL NOT NULL,
            gross_yield_v1 REAL NOT NULL,
            adjusted_yield_v3_trimmed REAL NOT NULL,
            adjusted_yield_v4_sigma_capped REAL NOT NULL,
            discount_giveaway_pct REAL NOT NULL,
            standard_rate_usd REAL NOT NULL,
            negotiated_rate_usd REAL NOT NULL,
            sigma_zscore REAL NOT NULL,
            price_competitiveness_score REAL NOT NULL
        );
        """
    )

    cur.execute(
        """
        CREATE TABLE delivery_health (
            delivery_id TEXT PRIMARY KEY,
            account_id TEXT NOT NULL,
            account_name TEXT NOT NULL,
            rag_status TEXT NOT NULL,
            milestone_delays INTEGER NOT NULL,
            eac_margin_variance_pct REAL NOT NULL,
            csat_score REAL NOT NULL,
            sla_slippage_days INTEGER NOT NULL,
            delivery_commentary TEXT NOT NULL
        );
        """
    )

    cur.execute(
        """
        CREATE TABLE unstructured_deal_notes (
            doc_id TEXT PRIMARY KEY,
            opp_id TEXT NOT NULL,
            account_id TEXT NOT NULL,
            source_system TEXT NOT NULL,
            note_date TEXT NOT NULL,
            note_snippet TEXT NOT NULL,
            extracted_risk_tag TEXT NOT NULL
        );
        """
    )

    cur.execute(
        """
        CREATE TABLE external_market_signals (
            signal_id TEXT PRIMARY KEY,
            account_id TEXT NOT NULL,
            account_name TEXT NOT NULL,
            signal_source TEXT NOT NULL,
            captured_date TEXT NOT NULL,
            ai_self_sufficiency_index REAL NOT NULL,
            intent_surge_score INTEGER NOT NULL,
            client_rd_intensity_pct REAL NOT NULL,
            signal_summary TEXT NOT NULL
        );
        """
    )

    cur.execute(
        """
        CREATE TABLE data_source_governance (
            source_id TEXT PRIMARY KEY,
            source_name TEXT NOT NULL UNIQUE,
            category TEXT NOT NULL,
            storage_engine TEXT NOT NULL,
            refresh_cadence TEXT NOT NULL,
            genai_usage_rights INTEGER NOT NULL,
            pii_classification TEXT NOT NULL,
            dataplex_aspect_uri TEXT NOT NULL,
            steward_team TEXT NOT NULL,
            notes TEXT NOT NULL
        );
        """
    )

    cur.executemany(
        "INSERT INTO opportunities VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        OPPORTUNITIES_SEED,
    )
    cur.executemany(
        "INSERT INTO pricing_scenarios VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        PRICING_SCENARIOS_SEED,
    )
    cur.executemany(
        "INSERT INTO delivery_health VALUES (?,?,?,?,?,?,?,?,?)",
        DELIVERY_HEALTH_SEED,
    )
    cur.executemany(
        "INSERT INTO unstructured_deal_notes VALUES (?,?,?,?,?,?,?)",
        UNSTRUCTURED_NOTES_SEED,
    )
    cur.executemany(
        "INSERT INTO external_market_signals VALUES (?,?,?,?,?,?,?,?,?)",
        EXTERNAL_MARKET_SIGNALS_SEED,
    )
    cur.executemany(
        """INSERT INTO data_source_governance VALUES (
            :source_id, :source_name, :category, :storage_engine,
            :refresh_cadence, :genai_usage_rights, :pii_classification,
            :dataplex_aspect_uri, :steward_team, :notes
        )""",
        GOVERNANCE_SOURCES,
    )

    conn.commit()
    conn.close()


CONTEXT_CONFIDENCE_ENRICHMENTS: Dict[str, Dict[str, Any]] = {
    "Q-001": {
        "confidence_pct": 92,
        "missing_artifacts": [
            "Physical BigQuery DDL for CRM_Opportunity_Spine stage history audit table (to verify whether Stage 3 re-entry resets stage_entry_date).",
        ],
    },
    "Q-002": {
        "confidence_pct": 91,
        "missing_artifacts": [
            "Corporate FX currency conversion rate table DDL in ERP_Financials_Ledger (constant-dollar vs. spot USD normalization).",
        ],
    },
    "Q-003": {
        "confidence_pct": 92,
        "missing_artifacts": [
            "Primary scenario flag convention in Deal_Pricing_Engine (confirming is_primary_scenario = TRUE vs. max(version_tag) join key).",
        ],
    },
    "Q-004": {
        "confidence_pct": 89,
        "missing_artifacts": [
            "Activity event taxonomy in CRM_Opportunity_Spine (confirming whether automated marketing touches update last_owner_activity_date).",
        ],
    },
    "Q-005": {
        "confidence_pct": 90,
        "missing_artifacts": [
            "Multi-service-line split allocation table in Revenue_ODS_15TB for bundled multi-tower contracts.",
        ],
    },
    "Q-006": {
        "confidence_pct": 74,
        "missing_artifacts": [
            "Exact semantic DAX formula sheet for Adjusted Yield v1/v3/v4 (specifically pass-through cloud/hardware cost GL account codes).",
            "Confirm whether 1.5-sigma clipping is partitioned by Industry Vertical or Global Region.",
        ],
    },
    "Q-007": {
        "confidence_pct": 68,
        "missing_artifacts": [
            "Counterfactual customer churn elasticity curve when repricing bottom-decile deals by +300 bps.",
            "Stranded bench cost absorption parameters in Workforce_Skills_Graph.",
        ],
    },
    "Q-008": {
        "confidence_pct": 52,
        "missing_artifacts": [
            "Trained Hidden Markov Model (Baum-Welch transition matrix & emission probability weights) not currently persisted in BigQuery.",
            "Historical 8-quarter pricing version sequence log in Deal_Pricing_Engine.",
        ],
    },
    "Q-009": {
        "confidence_pct": 58,
        "missing_artifacts": [
            "Fitted 6-lever logistic regression feature weights (b0..b6) across won/lost deals in CRM_Opportunity_Spine.",
            "Competitor bid spread proxy variable in Deal_Pricing_Engine.",
        ],
    },
    "Q-010": {
        "confidence_pct": 76,
        "missing_artifacts": [
            "Quarterly regional bookings target table in ERP_Financials_Ledger.",
            "Role-level ramp schedule linking OPP-9020 to Workforce_Skills_Graph bench headcount.",
        ],
    },
    "Q-011": {
        "confidence_pct": 79,
        "missing_artifacts": [
            "Master regional rate-card ceiling table DDL in Deal_Pricing_Engine mapped by labor grade and shore tier.",
        ],
    },
    "Q-012": {
        "confidence_pct": 72,
        "missing_artifacts": [
            "Cross-system entity resolution bridge table mapping pre-sales CRM opp_id to post-sales ERP_Financials_Ledger project WBS codes.",
        ],
    },
    "Q-013": {
        "confidence_pct": 66,
        "missing_artifacts": [
            "Loaded hourly cost rate card by onshore/nearshore/offshore tier in Workforce_Skills_Graph.",
            "Client MSA offshoring restriction flags in CLM_Contract_Vault.",
        ],
    },
    "Q-014": {
        "confidence_pct": 48,
        "missing_artifacts": [
            "Live API schema and entity-matching D-U-N-S bridge for Tech_Stack_Telemetry_Feed.",
            "Vector embedding index over unstructured executive debriefs in Customer_Visit_Logs.",
        ],
    },
    "Q-015": {
        "confidence_pct": 54,
        "missing_artifacts": [
            "Document AI / Vertex RAG chunking pipeline over executed PDF MSAs and SOW amendments in CLM_Contract_Vault.",
            "Structured metadata extraction schema for COLA cap % and termination notice days.",
        ],
    },
    "Q-016": {
        "confidence_pct": 15,
        "missing_artifacts": [
            "LEGAL BLOCKER: Analyst_Benchmark_Feed_Unlicensed has GenAI_Usage_Rights = False (zero LLM ingestion permitted).",
            "Requires clean-room aggregated benchmark substitution or commercial contract amendment with 3P vendor.",
        ],
    },
    "Q-017": {
        "confidence_pct": 44,
        "missing_artifacts": [
            "Game-theoretic Nash/Schelling bargaining utility function parameters (client walk-away reservation price vs. switching cost).",
            "Real-time feed integration for Buyer_Intent_Signal_Stream and Customer_Visit_Logs.",
        ],
    },
    "Q-018": {
        "confidence_pct": 56,
        "missing_artifacts": [
            "3P topic taxonomy mapping between Buyer_Intent_Signal_Stream surge topics and internal service_line catalog.",
            "SEC CIK / ticker to CRM account_id cross-walk for Market_Financials_API.",
        ],
    },
    "Q-019": {
        "confidence_pct": 49,
        "missing_artifacts": [
            "Automated EDGAR 8-K/10-Q ingestion webhook and restructuring sentiment classifier for SEC_Regulatory_Filings.",
            "Subsidiary-to-parent corporate hierarchy tree in CRM_Opportunity_Spine.",
        ],
    },
    "Q-020": {
        "confidence_pct": 61,
        "missing_artifacts": [
            "Unstructured text indexing of weekly delivery director commentary blobs in Delivery_Governance_Hub.",
            "Change-request (CR) status ledger in ERP_Financials_Ledger.",
        ],
    },
    "Q-021": {
        "confidence_pct": 51,
        "missing_artifacts": [
            "Historical outcome-based gain-share KPI realization ledger in ERP_Financials_Ledger.",
            "Approved value-sharing addendum templates in CLM_Contract_Vault.",
        ],
    },
    "Q-022": {
        "confidence_pct": 24,
        "missing_artifacts": [
            "UNMAPPED SCHEMA: Hyperscaler co-sell private-offer drawdown registry is not yet ingested into Revenue_ODS_15TB.",
            "Partner influence attribution model in CRM_Opportunity_Spine.",
        ],
    },
    "Q-023": {
        "confidence_pct": 46,
        "missing_artifacts": [
            "Cross-system Account 360 orchestration workflow binding 6 structured, RAG, and 3P telemetry sources.",
            "Executive QBR slide template schema and automated write-back service account permissions.",
        ],
    },
    "Q-024": {
        "confidence_pct": 42,
        "missing_artifacts": [
            "Real-time skill availability and clearance verification API in Workforce_Skills_Graph.",
            "Downstream calendar/dispatch webhook for automated pursuit squad mobilization.",
        ],
    },
}


def write_catalog_json() -> None:
    for q in QUESTIONS_CATALOG:
        enrichment = CONTEXT_CONFIDENCE_ENRICHMENTS.get(
            q["id"],
            {
                "confidence_pct": 65,
                "missing_artifacts": ["Physical BigQuery DDL and join key verification required."],
            },
        )
        q["confidence_pct"] = enrichment["confidence_pct"]
        q["missing_artifacts"] = enrichment["missing_artifacts"]

    tier_summary = [
        {
            "tier_code": "Tier 1",
            "title": "Tier 1: Deterministic Parameterized SQL via MCP Toolbox",
            "share_pct": 18,
            "benchmark_count": 5,
            "production_equivalent_count": 37,
            "avg_confidence_pct": 91,
            "latency_target": "350ms - 800ms",
            "description": "Direct single/multi-table SQL lookups over canonical BigQuery Gold Views with zero LLM SQL hallucination risk.",
        },
        {
            "tier_code": "Tier 2",
            "title": "Tier 2: Semantic Layer (Dataplex KC DAX) + Gold Views + Simulator",
            "share_pct": 30,
            "benchmark_count": 8,
            "production_equivalent_count": 61,
            "avg_confidence_pct": 68,
            "latency_target": "800ms - 1.8s",
            "description": "Materializes proprietary DAX formulas (Adjusted Yield v1/v3/v4, Markov Regimes) in BigQuery Gold Views and executes Python counterfactual What-If simulations.",
        },
        {
            "tier_code": "Tier 3",
            "title": "Tier 3: Federated Multi-Tool Agent (SQL + Unstructured RAG + 3P Market APIs)",
            "share_pct": 49,
            "benchmark_count": 9,
            "production_equivalent_count": 100,
            "avg_confidence_pct": 45,
            "latency_target": "1.8s - 4.2s",
            "description": "Combines structured BigQuery telemetry with unstructured CLM/Visit RAG and licensed external market/intent feeds behind a Dataplex GenAI Compliance Guard.",
        },
        {
            "tier_code": "Tier 4",
            "title": "Tier 4: Multi-System Action & Executive Briefing Automation",
            "share_pct": 3,
            "benchmark_count": 2,
            "production_equivalent_count": 5,
            "avg_confidence_pct": 44,
            "latency_target": "3.5s - 7.0s",
            "description": "Synthesizes cross-domain Account 360 intelligence into executive QBR packets and triggers pursuit squad mobilization workflows.",
        },
    ]

    blocker_summary: Dict[str, int] = {}
    for q in QUESTIONS_CATALOG:
        for flag in q["flags"]:
            blocker_summary[flag] = blocker_summary.get(flag, 0) + 1

    avg_conf = round(
        sum(q["confidence_pct"] for q in QUESTIONS_CATALOG) / len(QUESTIONS_CATALOG), 1
    )

    payload = {
        "metadata": {
            "title": "Dataplex Knowledge Catalog & Federated Commercial Mesh Benchmark",
            "version": "2026.10.1",
            "total_benchmark_questions": len(QUESTIONS_CATALOG),
            "production_corpus_equivalent": 203,
            "database_only_pass_rate_pct": 18.2,
            "hybrid_mesh_coverage_pct": 100.0,
            "average_readiness_confidence_pct": avg_conf,
        },
        "tier_summary": tier_summary,
        "blocker_summary": blocker_summary,
        "governance_sources": GOVERNANCE_SOURCES,
        "questions": QUESTIONS_CATALOG,
    }

    with open(CATALOG_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)


if __name__ == "__main__":
    build_sqlite_db()
    write_catalog_json()
    print(f"[OK] Seeded SQLite DB -> {DB_PATH}")
    print(f"[OK] Generated Catalog JSON ({len(QUESTIONS_CATALOG)} questions) -> {CATALOG_PATH}")
