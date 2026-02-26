import os
import json
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
class TaxComplianceFinding(BaseModel):
    category: str = Field(description="Regulatory category (e.g. Pillar Two, withholding tax)")
    risk_level: str = Field(description="LOW, MEDIUM, HIGH, CRITICAL")
    citation: str = Field(description="Reference from regulatory_kb_2026.md")
    impact_assessment: str = Field(description="Detailed impact of this finding")

class TaxComplianceReport(BaseModel):
    findings: List[TaxComplianceFinding] = Field(description="Compliance findings")
    is_compliant: bool = Field(description="Overall compliance status")
    total_tax_exposure: float = Field(description="Estimated tax exposure in USD")

# 2. Define Regulatory Tools
def ComplianceSearch(query: str) -> str:
    """
    Searches the regulatory_kb_2026.md for tax laws, Pillar Two rules, and compliance triggers.
    Use this to ground tax assessments.
    """
    kb_path = os.path.join(os.path.dirname(__file__), "../../data/regulatory_kb_2026.md")
    if not os.path.exists(kb_path):
        return "Regulatory Knowledge Base not found."
    
    with open(kb_path, 'r') as f:
        content = f.read()
    
    # Simple keyword search for RAG simulation
    lines = content.split('\n')
    relevant_lines = []
    keywords = query.lower().split()
    for line in lines:
        if any(kw in line.lower() for kw in keywords):
            relevant_lines.append(line)
    
    if not relevant_lines:
        return content[:2000] # Return header if no match
    
    return "\n".join(relevant_lines[:50])

# 3. Configure the Tax Agent
tax_agent = LlmAgent(
    name="tax_agent",
    model="gemini-2.5-flash",
    instruction="""
    You are a KPMG Senior Tax Compliance Consultant. Your goal is to ensure Verity Nexus clients follow international tax laws.
    
    ### GROUNDING:
    - Prioritize rules found in data/materiality_policy.yaml regarding non-treaty jurisdiction transfers.
    - Use 'ComplianceSearch' to retrieve specific clauses from the Regulatory Knowledge Base.
    
    ### TASK:
    - Assess transactions flagged by the Audit Agent for tax implications.
    - Specifically look for Pillar Two (GloBE Rules), QDMTT, and withholding tax risks.
    - If a payment exceeds $100,000 to a non-treaty jurisdiction, flag it as CRITICAL.
    
    ### NON-TREATY JURISDICTIONS (Grounding):
    British Virgin Islands, Cayman Islands, Panama, Bermuda, Jersey, Guernsey, Isle of Man, Mauritius, Seychelles, Vanuatu.
    """,
    tools=[FunctionTool(ComplianceSearch)],
    output_schema=TaxComplianceReport,
    output_key="tax_results"
)
