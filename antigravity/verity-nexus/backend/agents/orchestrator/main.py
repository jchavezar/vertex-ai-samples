import os
import json
import asyncio
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from google.adk.agents import LlmAgent
from google.adk.sessions import InMemorySessionService
from google.adk import Runner
from google.genai import types
import uuid

# Import agents
from agents.audit_agent.main import audit_agent, ScoredTransaction
from agents.tax_agent.main import tax_agent

# 1. Define Orchestration Output
class ProcessStep(BaseModel):
    step_id: int
    step_name: str
    status: str
    summary: str

class WorkflowExecution(BaseModel):
    workflow_id: str
    steps: List[ProcessStep]
    final_disposition: str
    needs_partner_signoff: bool
    findings: Optional[List[ScoredTransaction]] = Field(default=None, description="Consolidated audit findings from the swarm")

# 2. Configure the Orchestrator
orchestrator = LlmAgent(
    name="verity_orchestrator",
    model="gemini-2.5-pro", # Use Pro for complex reasoning
    instruction="""
    You are the 'Verity Nexus' Multi-Agent Orchestrator. Your goal is to guide the user through the KPMG Smart Audit Workflow.
    
    ### WORKFLOW DATA:
    You have access to data/smart_audit_workflow.json which defines the phases.
    
    ### PROTOCOL:
    1. **Ingestion**: Assume data is in data/ folder.
    2. **Transaction_Scoring**: Delegate to 'audit_agent'.
    3. **A2A_Validation**: Coordinate 'audit_agent' and 'tax_agent'.
       - Send audit findings to the tax agent.
       - Synthesize individual findings into a consensus.
    4. **Final_Review**: Prepare the summary for human sign-off.
    
    ### A2A HANDOVER:
    When the Audit Agent finds an anomaly, you MUST pass that context to the Tax Agent to verify regulatory compliance.
    
    ### OUTPUT:
    1. ALWAYS provide a structured 'WorkflowExecution'. 
    2. In your natural language response (text stream), provide a concise executive summary. 
    3. DO NOT output raw JSON blobs or lists of findings in the text stream; the platform will render the 'WorkflowExecution' findings automatically.
    4. If you delegated to the Audit Agent, you MUST include its findings in the 'findings' field of your structured output.
    """,
    # Orchestrator doesn't need external tools, it uses sub-agents
    sub_agents=[audit_agent, tax_agent],
    output_schema=WorkflowExecution,
    output_key="workflow_status"
)
