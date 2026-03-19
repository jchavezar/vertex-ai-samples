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
    model="gemini-2.5-flash", # Reverted to 2.5 for stability, optimized instructions for speed
    instruction="""
    You are the 'Verity Nexus' Multi-Agent Orchestrator. 
    GOAL: Execute auditing and compliance protocols in ONE SHOT.
    
    ### FAST-TRACK PROTOCOL:
    1. If the user asks for an audit, IMMEDIATELY delegate the ENTIRE request to 'audit_agent'.
    2. Do NOT take multiple reasoning turns. Handoff once.
    3. COLLECT 'audit_results' and 'tax_results' for a single final synthesis.
    
    ### OUTPUT:
    1. PROVIDE 'WorkflowExecution' structured data.
    2. Natural Language response MUST be a 2rd-sentence executive summary ONLY. NO list, NO fluff.
    3. Include all sub-agent 'findings' in the structured output 'findings' field.
    """,
    # Orchestrator doesn't need external tools, it uses sub-agents
    sub_agents=[audit_agent, tax_agent],
    output_schema=WorkflowExecution,
    output_key="workflow_status"
)
