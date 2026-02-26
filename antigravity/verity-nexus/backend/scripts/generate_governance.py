#!/usr/bin/env python3
"""
Verity Nexus Platform - Governance Data Generator
==================================================
Role: Senior Forensic Data Engineer
Purpose: Generate high-stakes grounding files for audit and compliance workflows.

Generates:
- data/materiality_policy.yaml - Audit materiality thresholds and risk triggers
- data/smart_audit_workflow.json - 4-step sequential audit workflow
- data/erp_mapping_schema.json - ERP field mappings (SAP/Oracle)
- data/ledger_2026.csv - 500 rows with embedded K-Consulting LLC signals
"""

import os
import csv
import json
import yaml
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any


# --------------------------------------------------------------------------------
# Configuration
# --------------------------------------------------------------------------------
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
TOTAL_LEDGER_ROWS = 500
K_CONSULTING_SIGNALS = 5  # High-risk transactions to inject


# --------------------------------------------------------------------------------
# 1. Materiality Policy Generator (YAML)
# --------------------------------------------------------------------------------
def generate_materiality_policy() -> dict[str, Any]:
    """
    Creates a nested YAML structure for audit materiality thresholds.
    """
    policy = {
        "materiality_policy": {
            "version": "2026.1",
            "effective_date": "2026-01-01",
            "last_reviewed": datetime.now().strftime("%Y-%m-%d"),
            "prepared_by": "Forensic Data Engineering Team",

            "thresholds": {
                "overall_materiality": 1_500_000,
                "performance_materiality": 1_125_000,  # 75% of overall
                "de_minimis": 75_000,
                "trivial_threshold": 7_500,  # 0.5% of overall
                "currency": "USD"
            },

            "quantitative_benchmarks": {
                "revenue_percentage": 0.5,
                "total_assets_percentage": 0.25,
                "net_income_percentage": 5.0,
                "equity_percentage": 1.0
            },

            "risk_triggers": {
                "unapproved_vendors": {
                    "description": "Transactions with vendors not on the approved vendor master list",
                    "risk_level": "HIGH",
                    "threshold_amount": 50_000,
                    "escalation_required": True,
                    "review_timeframe_hours": 24,
                    "actions": [
                        "Flag transaction for immediate review",
                        "Verify vendor legitimacy through external sources",
                        "Cross-reference with historical payment patterns",
                        "Notify Internal Audit if cumulative exposure exceeds $100,000"
                    ],
                    "responsible_party": "AuditAgent",
                    "compliance_references": [
                        "SOX Section 404",
                        "COSO Framework - Control Activities"
                    ]
                },

                "non_treaty_jurisdiction_transfers": {
                    "description": "Cross-border payments to jurisdictions without tax treaty protection",
                    "risk_level": "CRITICAL",
                    "threshold_amount": 100_000,
                    "escalation_required": True,
                    "review_timeframe_hours": 4,
                    "mandatory_forensic_review": True,
                    "actions": [
                        "CRITICAL FLAG: Any unverified service fees exceeding $100,000 to non-treaty jurisdictions must be flagged for manual forensic review to prevent Top-up Tax evasion",
                        "Verify substance of services rendered",
                        "Request transfer pricing documentation",
                        "Assess OECD Pillar Two QDMTT implications",
                        "Escalate to Tax Director within 4 hours"
                    ],
                    "responsible_party": "TaxAgent",
                    "compliance_references": [
                        "OECD Pillar Two GloBE Rules",
                        "FATCA/CRS Reporting Requirements",
                        "Anti-Money Laundering Regulations"
                    ],
                    "non_treaty_jurisdictions": [
                        "British Virgin Islands",
                        "Cayman Islands",
                        "Panama",
                        "Bermuda",
                        "Jersey",
                        "Guernsey",
                        "Isle of Man",
                        "Mauritius",
                        "Seychelles",
                        "Vanuatu"
                    ]
                },

                "unusual_timing_patterns": {
                    "description": "Transactions processed outside normal business hours",
                    "risk_level": "MEDIUM",
                    "threshold_hours": {
                        "after": "21:00",
                        "before": "06:00"
                    },
                    "weekend_flag": True,
                    "actions": [
                        "Log for pattern analysis",
                        "Cross-reference with employee access logs",
                        "Escalate if combined with other risk factors"
                    ],
                    "responsible_party": "AuditAgent"
                },

                "round_number_transactions": {
                    "description": "Transactions with suspiciously round amounts",
                    "risk_level": "LOW",
                    "pattern": "Amounts divisible by $10,000 with no cents",
                    "threshold_amount": 50_000,
                    "actions": [
                        "Flag for review if combined with other indicators",
                        "Compare to historical transaction patterns"
                    ],
                    "responsible_party": "AuditAgent"
                },

                "approval_bypass": {
                    "description": "Transactions marked as AUTO-APPROVE or bypassing standard workflow",
                    "risk_level": "HIGH",
                    "escalation_required": True,
                    "actions": [
                        "Immediate review by Senior Auditor",
                        "Verify authorization chain",
                        "Document business justification"
                    ],
                    "responsible_party": "AuditAgent"
                }
            },

            "aggregation_rules": {
                "vendor_cumulative_threshold": 250_000,
                "category_cumulative_threshold": 500_000,
                "period": "fiscal_quarter",
                "lookback_periods": 4
            },

            "governance": {
                "review_frequency": "quarterly",
                "approval_authority": "Audit Committee",
                "next_review_date": "2026-04-01"
            }
        }
    }

    return policy


def save_materiality_policy():
    """Saves the materiality policy to YAML file."""
    policy = generate_materiality_policy()
    output_path = DATA_DIR / "materiality_policy.yaml"

    with open(output_path, "w", encoding="utf-8") as f:
        yaml.dump(policy, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

    print(f"  ✓ Generated: {output_path}")
    return output_path


# --------------------------------------------------------------------------------
# 2. Smart Audit Workflow Generator (JSON)
# --------------------------------------------------------------------------------
def generate_audit_workflow() -> list[dict[str, Any]]:
    """
    Creates a 4-step sequential audit workflow based on enterprise audit methodology.
    """
    workflow = [
        {
            "step_id": 1,
            "step_name": "Ingestion",
            "phase": "Data Acquisition",
            "description": "Automated ingestion of financial data from multiple ERP sources with validation and normalization",
            "metadata": {
                "agent_role": "DataIngestionAgent",
                "agent_capabilities": [
                    "ERP_CONNECTOR",
                    "SCHEMA_VALIDATION",
                    "DATA_NORMALIZATION",
                    "DUPLICATE_DETECTION"
                ],
                "model": "gemini-2.5-flash",
                "timeout_seconds": 300
            },
            "inputs": [
                {
                    "source": "SAP_S4HANA",
                    "tables": ["BSEG", "BKPF", "LFA1", "KNA1"],
                    "format": "CSV/JSON"
                },
                {
                    "source": "Oracle_Financials",
                    "tables": ["GL_JE_LINES", "AP_INVOICES", "AP_SUPPLIERS"],
                    "format": "CSV/JSON"
                },
                {
                    "source": "Legacy_Systems",
                    "tables": ["LEDGER_EXPORT"],
                    "format": "CSV"
                }
            ],
            "outputs": [
                {
                    "artifact": "normalized_ledger.parquet",
                    "schema_version": "2026.1"
                },
                {
                    "artifact": "ingestion_report.json",
                    "includes": ["row_counts", "validation_errors", "data_quality_scores"]
                }
            ],
            "validation_rules": [
                "Schema conformance check",
                "Referential integrity validation",
                "Date range verification (fiscal year 2026)",
                "Currency code standardization"
            ],
            "success_criteria": {
                "min_data_quality_score": 0.95,
                "max_validation_errors": 100,
                "required_fields_complete": True
            },
            "next_step": "Transaction_Scoring",
            "rollback_on_failure": True
        },

        {
            "step_id": 2,
            "step_name": "Transaction_Scoring",
            "phase": "Risk Assessment",
            "description": "AI-powered risk scoring of individual transactions using materiality thresholds and anomaly detection",
            "metadata": {
                "agent_role": "AuditAgent",
                "agent_capabilities": [
                    "ANOMALY_DETECTION",
                    "RISK_SCORING",
                    "PATTERN_RECOGNITION",
                    "BENFORD_ANALYSIS"
                ],
                "model": "gemini-2.5-flash",
                "timeout_seconds": 600
            },
            "inputs": [
                {
                    "artifact": "normalized_ledger.parquet",
                    "from_step": "Ingestion"
                },
                {
                    "reference": "materiality_policy.yaml",
                    "type": "configuration"
                },
                {
                    "reference": "approved_vendors.json",
                    "type": "master_data"
                }
            ],
            "outputs": [
                {
                    "artifact": "scored_transactions.parquet",
                    "includes": ["risk_score", "risk_factors", "materiality_flag"]
                },
                {
                    "artifact": "high_risk_queue.json",
                    "description": "Transactions requiring manual review"
                },
                {
                    "artifact": "scoring_analytics.json",
                    "includes": ["distribution_stats", "benford_deviation", "cluster_analysis"]
                }
            ],
            "scoring_factors": [
                {
                    "factor": "amount_materiality",
                    "weight": 0.25,
                    "description": "Transaction amount relative to materiality threshold"
                },
                {
                    "factor": "vendor_risk",
                    "weight": 0.30,
                    "description": "Vendor approval status and historical patterns"
                },
                {
                    "factor": "timing_anomaly",
                    "weight": 0.15,
                    "description": "Unusual processing times or patterns"
                },
                {
                    "factor": "description_analysis",
                    "weight": 0.15,
                    "description": "NLP analysis of transaction descriptions"
                },
                {
                    "factor": "approval_workflow",
                    "weight": 0.15,
                    "description": "Adherence to standard approval processes"
                }
            ],
            "thresholds": {
                "high_risk": 0.75,
                "medium_risk": 0.50,
                "low_risk": 0.25
            },
            "success_criteria": {
                "scoring_complete": True,
                "high_risk_reviewed": False
            },
            "next_step": "A2A_Validation",
            "parallel_execution": False
        },

        {
            "step_id": 3,
            "step_name": "A2A_Validation",
            "phase": "Cross-Agent Verification",
            "description": "Agent-to-Agent validation protocol for high-risk transactions requiring multi-domain expertise",
            "metadata": {
                "agent_role": "TaxAgent",
                "collaborating_agents": ["AuditAgent", "ComplianceAgent"],
                "agent_capabilities": [
                    "TAX_COMPLIANCE_CHECK",
                    "TRANSFER_PRICING_ANALYSIS",
                    "PILLAR_TWO_ASSESSMENT",
                    "TREATY_VERIFICATION"
                ],
                "model": "gemini-2.5-flash",
                "timeout_seconds": 900
            },
            "inputs": [
                {
                    "artifact": "high_risk_queue.json",
                    "from_step": "Transaction_Scoring"
                },
                {
                    "reference": "regulatory_kb_2026.md",
                    "type": "knowledge_base"
                },
                {
                    "reference": "erp_mapping_schema.json",
                    "type": "configuration"
                }
            ],
            "outputs": [
                {
                    "artifact": "a2a_validation_results.json",
                    "includes": ["validation_status", "agent_consensus", "findings"]
                },
                {
                    "artifact": "escalation_queue.json",
                    "description": "Items requiring human expert review"
                },
                {
                    "artifact": "tax_exposure_report.json",
                    "includes": ["pillar_two_impact", "withholding_tax_risks", "transfer_pricing_flags"]
                }
            ],
            "validation_protocols": [
                {
                    "protocol": "VENDOR_VERIFICATION",
                    "agents": ["AuditAgent"],
                    "checks": ["approved_vendor_list", "historical_patterns", "external_verification"]
                },
                {
                    "protocol": "TAX_TREATY_CHECK",
                    "agents": ["TaxAgent"],
                    "checks": ["jurisdiction_classification", "treaty_benefits", "substance_requirements"]
                },
                {
                    "protocol": "PILLAR_TWO_ASSESSMENT",
                    "agents": ["TaxAgent"],
                    "checks": ["QDMTT_exposure", "SBIE_carveout", "top_up_tax_risk"]
                },
                {
                    "protocol": "CONSENSUS_VOTING",
                    "agents": ["AuditAgent", "TaxAgent", "ComplianceAgent"],
                    "quorum_required": 2,
                    "escalate_on_disagreement": True
                }
            ],
            "success_criteria": {
                "all_high_risk_validated": True,
                "consensus_reached": True,
                "escalations_documented": True
            },
            "next_step": "Final_Review",
            "human_in_loop": True
        },

        {
            "step_id": 4,
            "step_name": "Final_Review",
            "phase": "Human Oversight & Reporting",
            "description": "Senior auditor review of AI findings with final sign-off and regulatory report generation",
            "metadata": {
                "agent_role": "ReportingAgent",
                "human_roles": ["Senior_Auditor", "Tax_Director", "Audit_Partner"],
                "agent_capabilities": [
                    "REPORT_GENERATION",
                    "FINDING_SUMMARIZATION",
                    "REGULATORY_FORMATTING",
                    "AUDIT_TRAIL_COMPILATION"
                ],
                "model": "gemini-2.5-flash",
                "timeout_seconds": 1200
            },
            "inputs": [
                {
                    "artifact": "a2a_validation_results.json",
                    "from_step": "A2A_Validation"
                },
                {
                    "artifact": "escalation_queue.json",
                    "from_step": "A2A_Validation"
                },
                {
                    "artifact": "scoring_analytics.json",
                    "from_step": "Transaction_Scoring"
                }
            ],
            "outputs": [
                {
                    "artifact": "audit_findings_report.pdf",
                    "format": "Enterprise_CLARA_TEMPLATE",
                    "sections": ["Executive_Summary", "High_Risk_Findings", "Recommendations", "Management_Response"]
                },
                {
                    "artifact": "regulatory_submission.xml",
                    "format": "XBRL",
                    "applicable_to": ["SOX_404", "PCAOB_AS_2201"]
                },
                {
                    "artifact": "audit_trail.json",
                    "includes": ["all_agent_actions", "human_decisions", "timestamps", "evidence_links"]
                },
                {
                    "artifact": "pillar_two_disclosure.json",
                    "format": "GloBE_INFORMATION_RETURN"
                }
            ],
            "review_workflow": {
                "stages": [
                    {
                        "stage": "AI_SUMMARY_REVIEW",
                        "reviewer": "Senior_Auditor",
                        "sla_hours": 24
                    },
                    {
                        "stage": "TAX_FINDING_VALIDATION",
                        "reviewer": "Tax_Director",
                        "sla_hours": 48
                    },
                    {
                        "stage": "FINAL_SIGNOFF",
                        "reviewer": "Audit_Partner",
                        "sla_hours": 72
                    }
                ],
                "requires_all_approvals": True
            },
            "success_criteria": {
                "all_findings_addressed": True,
                "sign_offs_complete": True,
                "reports_generated": True
            },
            "next_step": None,
            "workflow_complete": True
        }
    ]

    return workflow


def save_audit_workflow():
    """Saves the Smart Audit workflow to JSON file."""
    workflow = generate_audit_workflow()
    output_path = DATA_DIR / "smart_audit_workflow.json"

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(workflow, f, indent=2)

    print(f"  ✓ Generated: {output_path}")
    return output_path


# --------------------------------------------------------------------------------
# 3. ERP Mapping Schema Generator (JSON)
# --------------------------------------------------------------------------------
def generate_erp_mapping_schema() -> dict[str, Any]:
    """
    Creates field mappings from ledger_2026.csv to SAP and Oracle ERP systems.
    """
    schema = {
        "schema_version": "2026.1",
        "last_updated": datetime.now().strftime("%Y-%m-%d"),
        "description": "Field mapping schema for Verity Nexus ledger to enterprise ERP systems",

        "source_system": {
            "name": "Verity Nexus Ledger",
            "file": "ledger_2026.csv",
            "encoding": "UTF-8",
            "delimiter": ","
        },

        "field_mappings": {
            "Trans_ID": {
                "description": "Unique transaction identifier",
                "data_type": "VARCHAR(20)",
                "nullable": False,
                "primary_key": True,
                "sap": {
                    "table": "BSEG",
                    "field": "BELNR",
                    "full_path": "SAP_BSEG_BELNR",
                    "description": "Accounting Document Number"
                },
                "oracle": {
                    "table": "GL_JE_LINES",
                    "field": "JE_LINE_NUM",
                    "full_path": "ORA_GL_JE_LINE_NUM",
                    "description": "Journal Entry Line Number"
                }
            },

            "Date": {
                "description": "Transaction date and time",
                "data_type": "TIMESTAMP",
                "nullable": False,
                "format": "YYYY-MM-DD HH:MM:SS",
                "sap": {
                    "table": "BKPF",
                    "field": "BUDAT",
                    "full_path": "SAP_BKPF_BUDAT",
                    "description": "Posting Date",
                    "time_field": {
                        "table": "BKPF",
                        "field": "CPUTM",
                        "full_path": "SAP_BKPF_CPUTM",
                        "description": "Entry Time"
                    }
                },
                "oracle": {
                    "table": "GL_JE_HEADERS",
                    "field": "DEFAULT_EFFECTIVE_DATE",
                    "full_path": "ORA_GL_EFFECTIVE_DATE",
                    "description": "Effective Date"
                }
            },

            "Account_Code": {
                "description": "General ledger account code",
                "data_type": "VARCHAR(20)",
                "nullable": False,
                "sap": {
                    "table": "BSEG",
                    "field": "HKONT",
                    "full_path": "SAP_BSEG_HKONT",
                    "description": "General Ledger Account"
                },
                "oracle": {
                    "table": "GL_CODE_COMBINATIONS",
                    "field": "CODE_COMBINATION_ID",
                    "full_path": "ORA_GL_CODE_COMB_ID",
                    "description": "Account Code Combination"
                }
            },

            "Entity": {
                "description": "Legal entity or company code",
                "data_type": "VARCHAR(50)",
                "nullable": False,
                "sap": {
                    "table": "BKPF",
                    "field": "BUKRS",
                    "full_path": "SAP_BKPF_BUKRS",
                    "description": "Company Code"
                },
                "oracle": {
                    "table": "GL_JE_HEADERS",
                    "field": "LEDGER_ID",
                    "full_path": "ORA_GL_LEDGER_ID",
                    "description": "Ledger Identifier",
                    "lookup_table": "GL_LEDGERS"
                }
            },

            "Vendor_Name": {
                "description": "Vendor or supplier name",
                "data_type": "VARCHAR(100)",
                "nullable": False,
                "sap": {
                    "table": "LFA1",
                    "field": "NAME1",
                    "full_path": "SAP_LFA1_NAME1",
                    "description": "Vendor Name",
                    "join_key": {
                        "from_table": "BSEG",
                        "from_field": "LIFNR",
                        "to_table": "LFA1",
                        "to_field": "LIFNR"
                    }
                },
                "oracle": {
                    "table": "AP_SUPPLIERS",
                    "field": "VENDOR_NAME",
                    "full_path": "ORA_AP_VENDOR_NAME",
                    "description": "Supplier Name",
                    "join_key": {
                        "from_table": "AP_INVOICES_ALL",
                        "from_field": "VENDOR_ID",
                        "to_table": "AP_SUPPLIERS",
                        "to_field": "VENDOR_ID"
                    }
                }
            },

            "Amount_USD": {
                "description": "Transaction amount in USD",
                "data_type": "DECIMAL(18,2)",
                "nullable": False,
                "currency": "USD",
                "sap": {
                    "table": "BSEG",
                    "field": "DMBTR",
                    "full_path": "SAP_BSEG_DMBTR",
                    "description": "Amount in Local Currency",
                    "currency_field": {
                        "table": "BKPF",
                        "field": "WAERS",
                        "full_path": "SAP_BKPF_WAERS"
                    }
                },
                "oracle": {
                    "table": "GL_JE_LINES",
                    "field": "ENTERED_DR",
                    "full_path": "ORA_GL_ENTERED_DR",
                    "description": "Entered Debit Amount",
                    "credit_field": "ENTERED_CR",
                    "currency_field": "CURRENCY_CODE"
                }
            },

            "Approval_Status": {
                "description": "Transaction approval status",
                "data_type": "VARCHAR(20)",
                "nullable": False,
                "valid_values": ["APPROVED", "PENDING", "REJECTED", "AUTO-APPROVE"],
                "sap": {
                    "table": "BKPF",
                    "field": "BSTAT",
                    "full_path": "SAP_BKPF_BSTAT",
                    "description": "Document Status",
                    "value_mapping": {
                        "APPROVED": "",
                        "PENDING": "V",
                        "REJECTED": "S",
                        "AUTO-APPROVE": "D"
                    }
                },
                "oracle": {
                    "table": "GL_JE_HEADERS",
                    "field": "STATUS",
                    "full_path": "ORA_GL_STATUS",
                    "description": "Journal Status",
                    "value_mapping": {
                        "APPROVED": "P",
                        "PENDING": "U",
                        "REJECTED": "R",
                        "AUTO-APPROVE": "P"
                    }
                }
            },

            "Description": {
                "description": "Transaction description or narrative",
                "data_type": "VARCHAR(500)",
                "nullable": True,
                "sap": {
                    "table": "BSEG",
                    "field": "SGTXT",
                    "full_path": "SAP_BSEG_SGTXT",
                    "description": "Item Text"
                },
                "oracle": {
                    "table": "GL_JE_LINES",
                    "field": "DESCRIPTION",
                    "full_path": "ORA_GL_LINE_DESC",
                    "description": "Line Description"
                }
            }
        },

        "derived_fields": {
            "risk_score": {
                "description": "Calculated risk score (0.0 - 1.0)",
                "data_type": "DECIMAL(3,2)",
                "calculation": "AI_MODEL_OUTPUT",
                "storage": "AUDIT_WORKPAPER"
            },
            "materiality_flag": {
                "description": "Boolean flag if amount exceeds materiality threshold",
                "data_type": "BOOLEAN",
                "calculation": "Amount_USD > materiality_policy.thresholds.de_minimis"
            }
        },

        "extraction_queries": {
            "sap": """
                SELECT
                    BSEG.BELNR AS Trans_ID,
                    CONCAT(BKPF.BUDAT, ' ', BKPF.CPUTM) AS Date,
                    BSEG.HKONT AS Account_Code,
                    BKPF.BUKRS AS Entity,
                    LFA1.NAME1 AS Vendor_Name,
                    BSEG.DMBTR AS Amount_USD,
                    BKPF.BSTAT AS Approval_Status,
                    BSEG.SGTXT AS Description
                FROM BSEG
                INNER JOIN BKPF ON BSEG.BUKRS = BKPF.BUKRS
                    AND BSEG.BELNR = BKPF.BELNR
                    AND BSEG.GJAHR = BKPF.GJAHR
                LEFT JOIN LFA1 ON BSEG.LIFNR = LFA1.LIFNR
                WHERE BKPF.GJAHR = '2026'
            """,
            "oracle": """
                SELECT
                    JL.JE_LINE_NUM AS Trans_ID,
                    JH.DEFAULT_EFFECTIVE_DATE AS Date,
                    CC.CODE_COMBINATION_ID AS Account_Code,
                    L.NAME AS Entity,
                    S.VENDOR_NAME AS Vendor_Name,
                    NVL(JL.ENTERED_DR, 0) - NVL(JL.ENTERED_CR, 0) AS Amount_USD,
                    JH.STATUS AS Approval_Status,
                    JL.DESCRIPTION AS Description
                FROM GL_JE_LINES JL
                INNER JOIN GL_JE_HEADERS JH ON JL.JE_HEADER_ID = JH.JE_HEADER_ID
                INNER JOIN GL_LEDGERS L ON JH.LEDGER_ID = L.LEDGER_ID
                INNER JOIN GL_CODE_COMBINATIONS CC ON JL.CODE_COMBINATION_ID = CC.CODE_COMBINATION_ID
                LEFT JOIN AP_INVOICES_ALL AI ON JL.REFERENCE_5 = AI.INVOICE_NUM
                LEFT JOIN AP_SUPPLIERS S ON AI.VENDOR_ID = S.VENDOR_ID
                WHERE EXTRACT(YEAR FROM JH.DEFAULT_EFFECTIVE_DATE) = 2026
            """
        }
    }

    return schema


def save_erp_mapping_schema():
    """Saves the ERP mapping schema to JSON file."""
    schema = generate_erp_mapping_schema()
    output_path = DATA_DIR / "erp_mapping_schema.json"

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(schema, f, indent=2)

    print(f"  ✓ Generated: {output_path}")
    return output_path


# --------------------------------------------------------------------------------
# 4. High-Density Ledger Generator (500 rows + K-Consulting signals)
# --------------------------------------------------------------------------------

# Realistic vendor data by category
VENDOR_DATA = {
    "Software": [
        ("Salesforce Inc.", (5000, 75000)),
        ("Amazon Web Services", (2000, 150000)),
        ("Microsoft Corporation", (3000, 100000)),
        ("Slack Technologies", (1000, 25000)),
        ("Atlassian Pty Ltd", (2000, 40000)),
        ("Oracle Corporation", (10000, 200000)),
        ("ServiceNow Inc.", (5000, 80000)),
        ("Snowflake Inc.", (8000, 120000)),
        ("Datadog Inc.", (3000, 50000)),
        ("Zoom Video Communications", (1000, 15000))
    ],
    "Consulting": [
        ("McKinsey & Company", (25000, 500000)),
        ("Boston Consulting Group", (20000, 400000)),
        ("Deloitte LLP", (15000, 350000)),
        ("Accenture LLP", (10000, 300000)),
        ("Bain & Company", (20000, 450000)),
        ("Enterprise LLP", (12000, 280000)),
        ("PricewaterhouseCoopers", (15000, 320000)),
        ("Ernst & Young LLP", (12000, 290000))
    ],
    "Travel": [
        ("Delta Air Lines", (500, 15000)),
        ("Marriott International", (300, 8000)),
        ("Uber Business", (100, 3000)),
        ("American Express Travel", (1000, 25000)),
        ("Hertz Corporation", (200, 5000)),
        ("United Airlines", (500, 12000)),
        ("Hilton Hotels", (250, 6000))
    ],
    "Office": [
        ("Staples Business Advantage", (500, 15000)),
        ("W.B. Mason Company", (300, 8000)),
        ("Uline Inc.", (200, 5000)),
        ("Pitney Bowes Inc.", (1000, 10000)),
        ("Xerox Corporation", (2000, 20000)),
        ("Canon Solutions America", (1500, 12000))
    ],
    "Legal": [
        ("Baker McKenzie", (15000, 250000)),
        ("Latham & Watkins LLP", (20000, 350000)),
        ("Kirkland & Ellis LLP", (25000, 400000)),
        ("Skadden Arps", (18000, 300000)),
        ("Jones Day", (12000, 200000)),
        ("Sullivan & Cromwell", (20000, 320000))
    ],
    "Utilities": [
        ("Consolidated Edison", (5000, 50000)),
        ("Verizon Business", (3000, 40000)),
        ("Waste Management Inc.", (2000, 25000)),
        ("Pacific Gas & Electric", (4000, 45000)),
        ("AT&T Corporation", (2500, 35000))
    ],
    "Insurance": [
        ("Marsh McLennan", (10000, 150000)),
        ("Aon plc", (8000, 120000)),
        ("Willis Towers Watson", (7000, 100000)),
        ("AIG Insurance", (5000, 80000))
    ],
    "Marketing": [
        ("WPP plc", (5000, 100000)),
        ("Omnicom Group", (4000, 80000)),
        ("Publicis Groupe", (3500, 70000)),
        ("Interpublic Group", (3000, 60000))
    ]
}

# Account codes by category
ACCOUNT_CODES = {
    "Software": "500-SOFTWARE",
    "Consulting": "500-CONSULTING",
    "Travel": "500-TRAVEL",
    "Office": "500-OFFICE",
    "Legal": "500-LEGAL",
    "Utilities": "500-UTILITIES",
    "Insurance": "500-INSURANCE",
    "Marketing": "500-MARKETING"
}


def generate_regular_transaction(trans_id: int, year: int = 2026) -> dict:
    """Generates a single regular transaction with realistic attributes."""
    # Pick random category and vendor
    category = random.choice(list(VENDOR_DATA.keys()))
    vendor_name, amount_range = random.choice(VENDOR_DATA[category])

    # Generate realistic date (business hours, weekdays)
    rand_day = random.randint(1, 360)
    base_date = datetime(year, 1, 1) + timedelta(days=rand_day)

    # Avoid weekends
    while base_date.weekday() >= 5:
        base_date += timedelta(days=1)

    # Business hours (8 AM - 6 PM)
    hour = random.randint(8, 18)
    minute = random.randint(0, 59)
    second = random.randint(0, 59)
    final_date = base_date.replace(hour=hour, minute=minute, second=second)

    # Generate amount with some realistic patterns
    amount = round(random.uniform(amount_range[0], amount_range[1]), 2)

    # Occasionally make round numbers (10% chance)
    if random.random() < 0.10:
        amount = round(amount / 1000) * 1000

    # Generate description
    descriptions = [
        f"Standard {category} Expense",
        f"{category} Services - Q{(final_date.month - 1) // 3 + 1}",
        f"Monthly {category} Invoice",
        f"{category} - Project Alpha",
        f"Annual {category} Renewal",
        f"{category} Support Services"
    ]

    return {
        "Trans_ID": f"TXN-{year}-{str(trans_id).zfill(4)}",
        "Date": final_date.strftime("%Y-%m-%d %H:%M:%S"),
        "Account_Code": ACCOUNT_CODES[category],
        "Entity": "Verity Nexus HQ",
        "Vendor_Name": vendor_name,
        "Amount_USD": amount,
        "Approval_Status": "APPROVED",
        "Description": random.choice(descriptions)
    }


def generate_k_consulting_signal(trans_id: int, signal_num: int, year: int = 2026) -> dict:
    """
    Generates a high-risk K-Consulting LLC transaction with embedded signals:
    - Amount over $100k
    - Timestamp after 11:00 PM
    - "Urgent" in description
    """
    # Find a weekday for the transaction
    rand_day = random.randint(1, 360)
    base_date = datetime(year, 1, 1) + timedelta(days=rand_day)

    # Can be any day (signals often happen on weekends too - suspicious)
    # 50% chance of weekend
    if random.random() < 0.5:
        # Make it a weekend
        days_to_weekend = (5 - base_date.weekday()) % 7
        if days_to_weekend == 0:
            days_to_weekend = random.choice([0, 1])  # Saturday or Sunday
        base_date += timedelta(days=days_to_weekend)

    # After 11:00 PM (23:00-23:59)
    hour = random.randint(23, 23)
    minute = random.randint(0, 59)
    second = random.randint(0, 59)
    final_date = base_date.replace(hour=hour, minute=minute, second=second)

    # Amount over $100k (between $105k and $145k for variety)
    amounts = [105000.00, 112500.00, 127000.00, 138000.00, 142500.00]
    amount = amounts[signal_num % len(amounts)]

    # Urgent descriptions
    descriptions = [
        "URGENT: Strategic Advisory Retainer - Immediate Processing Required",
        "Urgent Consulting Engagement - Executive Authorization",
        "PRIORITY: Advisory Services - Urgent Settlement",
        "Urgent: Special Project Consulting - Expedited Payment",
        "CRITICAL: Strategic Initiative Support - Urgent Processing"
    ]

    return {
        "Trans_ID": f"TXN-{year}-{9000 + signal_num}",
        "Date": final_date.strftime("%Y-%m-%d %H:%M:%S"),
        "Account_Code": "700-CONSULT-EXT",
        "Entity": "Verity Nexus HQ",
        "Vendor_Name": "K-Consulting LLC",
        "Amount_USD": amount,
        "Approval_Status": "AUTO-APPROVE",
        "Description": descriptions[signal_num % len(descriptions)]
    }


def generate_expanded_ledger():
    """
    Generates expanded ledger with 500 rows:
    - 495 regular transactions (financial noise)
    - 5 K-Consulting LLC signals (high-risk)
    """
    transactions = []

    # Generate regular transactions
    regular_count = TOTAL_LEDGER_ROWS - K_CONSULTING_SIGNALS
    print(f"  → Generating {regular_count} regular transactions...")

    for i in range(regular_count):
        txn = generate_regular_transaction(i + 1)
        transactions.append(txn)

    # Generate K-Consulting LLC signals
    print(f"  → Injecting {K_CONSULTING_SIGNALS} K-Consulting LLC signals...")

    for i in range(K_CONSULTING_SIGNALS):
        signal = generate_k_consulting_signal(9000 + i, i)
        transactions.append(signal)
        print(f"    • Signal {i+1}: ${signal['Amount_USD']:,.2f} at {signal['Date'][-8:]}")

    # Shuffle to hide signals
    random.shuffle(transactions)

    return transactions


def save_expanded_ledger():
    """Saves the expanded ledger to CSV file."""
    transactions = generate_expanded_ledger()
    output_path = DATA_DIR / "ledger_2026.csv"

    headers = ["Trans_ID", "Date", "Account_Code", "Entity", "Vendor_Name",
               "Amount_USD", "Approval_Status", "Description"]

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(transactions)

    # Calculate totals for verification
    total_amount = sum(t["Amount_USD"] for t in transactions)
    k_consulting_txns = [t for t in transactions if t["Vendor_Name"] == "K-Consulting LLC"]
    k_consulting_total = sum(t["Amount_USD"] for t in k_consulting_txns)

    print(f"  ✓ Generated: {output_path}")
    print(f"    • Total rows: {len(transactions)}")
    print(f"    • Total amount: ${total_amount:,.2f}")
    print(f"    • K-Consulting LLC transactions: {len(k_consulting_txns)}")
    print(f"    • K-Consulting LLC total: ${k_consulting_total:,.2f}")

    return output_path


# --------------------------------------------------------------------------------
# 5. Main Execution
# --------------------------------------------------------------------------------
def main():
    """Main execution function - generates all governance files."""
    print("=" * 70)
    print("VERITY NEXUS - GOVERNANCE DATA GENERATOR")
    print("Role: Senior Forensic Data Engineer")
    print("=" * 70)
    print()

    # Ensure data directory exists
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Output directory: {DATA_DIR}")
    print()

    # Generate all files
    print("Phase 1: Generating Materiality Policy (YAML)...")
    save_materiality_policy()
    print()

    print("Phase 2: Generating Enterprise Smart Audit Workflow (JSON)...")
    save_audit_workflow()
    print()

    print("Phase 3: Generating ERP Mapping Schema (JSON)...")
    save_erp_mapping_schema()
    print()

    print("Phase 4: Generating Expanded Ledger (CSV)...")
    save_expanded_ledger()
    print()

    print("=" * 70)
    print("SUCCESS: All governance files generated successfully!")
    print("=" * 70)

    # Summary
    print("\nGenerated Files:")
    for f in DATA_DIR.glob("*"):
        if f.is_file():
            size = f.stat().st_size
            print(f"  • {f.name} ({size:,} bytes)")


if __name__ == "__main__":
    main()
