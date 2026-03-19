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
    You are the 'Audit Specialist' for Verity Nexus.
    GOAL: Identify anomalous transactions with EXTREME speed.
    
    ### PROTOCOL:
    1. Call 'get_all_transactions' with limit=100. Do NOT fetch more.
    2. Analyze the 'amount_usd' and 'approval_status'. 
    3. FLAG: Materiality > $1,500k, De Minimis > $75k, or 'AUTO-APPROVE' status on high-value items.
    
    ### LIMITS:
    - **CAP: Return the top 3 most critical findings only.** 
    - NEVER fetch the entire ledger. 
    
    ### OUTPUT:
    - Return a JSON object mapped to 'audit_results' state key.
    - Provide a 1-sentence text summary ONLY. No lists in text.
    """,

    tools=[
        MCPToolset(
            connection_params=SseConnectionParams(
                url="https://mcp-ledger-toolbox-REDACTED_PROJECT_NUMBER.us-central1.run.app/mcp/sse"
            )
        )
    ],
    output_schema=AuditReport,
    output_key="audit_results"
)
