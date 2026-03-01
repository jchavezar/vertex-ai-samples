import os
import json
import csv
import yaml
import asyncio
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, SseConnectionParams
from google.adk import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
import uuid

# 1. Define Structured Output Schema
class ScoredTransaction(BaseModel):
    trans_id: str = Field(description="Transaction ID")
    amount: float = Field(description="Transaction amount in USD")
    vendor: str = Field(description="Vendor name")
    risk_score: float = Field(description="Risk score from 0.0 to 1.0 (estimated manually based on anomalies)")
    risk_factors: List[str] = Field(description="Reasons for the risk score (e.g., Unapproved vendor, auto-approved)")
    is_material: bool = Field(description="True if the transaction exceeds thresholds")
    recommendation: str = Field(description="Actionable recommendation")

class AuditReport(BaseModel):
    findings: List[ScoredTransaction] = Field(description="List of scored transactions")
    overall_risk_assessment: str = Field(description="Summary of the audit findings")
    materiality_impact: str = Field(description="Impact on overall financial materiality")

# 2. Configure the Audit Agent
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
    Use the available database tools to query the postgres ledger securely via MCP.
    Identify transactions with anomalous characteristics: large amounts, unapproved vendors, round numbers, or risky jurisdictions.
    When you find anomalies, score the risk manually based on the severity of the flagged factors.
    If an anomaly is found, provide a detailed report.
    IMPORTANT: You MUST return ALL suspicious transactions you find (at least 3-10). Do not just return 1 finding. Keep searching and returning all relevant anomalies.
    
    ### A2A PROTOCOLS:
    If you find transactions involving cross-border payments or non-treaty jurisdictions, highlight them for Tax review.
    
    ### OUTPUT PROTOCOL:
    When finishing, provide a structured 'AuditReport'. 
    In your text response, summarize your findings in plain English. NEVER output raw JSON in the text stream.
    """,
    tools=[
        MCPToolset(
            connection_params=SseConnectionParams(
                url="https://mcp-ledger-toolbox-254356041555.us-central1.run.app/mcp/sse"
            )
        )
    ],
    output_schema=AuditReport,
    output_key="audit_results"
)
