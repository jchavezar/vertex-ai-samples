import os
import json
import csv
import yaml
import asyncio
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
from google.adk import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
import uuid

# 1. Define Structured Output Schema
class ScoredTransaction(BaseModel):
    trans_id: str = Field(description="Transaction ID")
    amount: float = Field(description="Transaction amount in USD")
    vendor: str = Field(description="Vendor name")
    risk_score: float = Field(description="Risk score from 0.0 to 1.0")
    risk_factors: List[str] = Field(description="Reasons for the risk score")
    is_material: bool = Field(description="True if the transaction exceeds thresholds")
    recommendation: str = Field(description="Actionable recommendation")

class AuditReport(BaseModel):
    findings: List[ScoredTransaction] = Field(description="List of scored transactions")
    overall_risk_assessment: str = Field(description="Summary of the audit findings")
    materiality_impact: str = Field(description="Impact on overall financial materiality")

# 2. Define Forensic Tools
def TransactionScorer(count: int = 100) -> str:
    """
    Analyzes the ledger_2026.csv and scores transactions using approved_vendors.json and materiality_policy.yaml.
    Returns a summary of high-risk transactions.
    """
    data_dir = os.path.join(os.path.dirname(__file__), "../../data")
    ledger_path = os.path.join(data_dir, "ledger_2026.csv")
    vendors_path = os.path.join(data_dir, "approved_vendors.json")
    policy_path = os.path.join(data_dir, "materiality_policy.yaml")

    # Load data
    with open(vendors_path, 'r') as f:
        approved_vendors = set(json.load(f)["approved_vendors"])
    
    with open(policy_path, 'r') as f:
        policy = yaml.safe_load(f)["materiality_policy"]
    
    de_minimis = policy["thresholds"]["de_minimis"]
    unapproved_vendor_threshold = policy["risk_triggers"]["unapproved_vendors"]["threshold_amount"]

    results = []
    with open(ledger_path, 'r') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if i >= count: break
            
            score = 0.0
            factors = []
            amount = float(row["Amount_USD"])
            vendor = row["Vendor_Name"]
            
            # Check 1: Approved Vendor
            if vendor not in approved_vendors:
                score += 0.4
                factors.append(f"Unapproved Vendor: {vendor}")
                if amount > unapproved_vendor_threshold:
                    score += 0.2
                    factors.append(f"High-value Unapproved Transaction")
            
            # Check 2: Materiality
            if amount > de_minimis:
                score += 0.3
                factors.append(f"Materiality Threshold Exceeded: ${amount}")
            
            # Check 3: Round Numbers
            if amount % 1000 == 0:
                score += 0.1
                factors.append("Round number transaction")
            
            # Check 4: Approval Status
            if row["Approval_Status"] == "AUTO-APPROVE":
                score += 0.4
                factors.append("Bypassed standard approval (AUTO-APPROVE)")

            if score > 0.5:
                results.append({
                    "trans_id": row["Trans_ID"],
                    "amount": amount,
                    "vendor": vendor,
                    "risk_score": min(1.0, score),
                    "risk_factors": factors,
                    "is_material": amount > de_minimis
                })

    return json.dumps(results[:20], indent=2)

# 3. Configure the Audit Agent
audit_agent = LlmAgent(
    name="audit_agent",
    model="gemini-2.5-flash",
    instruction="""
    You are a KPMG Senior Forensic Auditor. Your goal is to identify financial anomalies and risks in the Verity Nexus platform.
    
    ### GROUNDING:
    You must prioritize rules found in data/materiality_policy.yaml.
    Overall Materiality: $1,500,000
    De Minimis: $75,000
    
    ### TASK:
    Use the 'TransactionScorer' tool to analyze the ledger.
    Identify transactions with high risk scores (> 0.7) or those exceeding the de_minimis threshold.
    If an anomaly is found, provide a detailed report.
    
    ### A2A PROTOCOLS:
    If you find transactions involving cross-border payments or non-treaty jurisdictions, highlight them for Tax review.
    
    ### OUTPUT PROTOCOL:
    When finishing, provide a structured 'AuditReport'. 
    In your text response, summarize your findings in plain English. NEVER output raw JSON in the text stream.
    """,
    tools=[FunctionTool(TransactionScorer)],
    output_schema=AuditReport,
    output_key="audit_results"
)
