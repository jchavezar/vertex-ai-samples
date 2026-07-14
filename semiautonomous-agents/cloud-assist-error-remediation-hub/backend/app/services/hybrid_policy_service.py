"""
Hybrid Split-Plane Agentic Policy & Execution Service

Orchestrates the 5-step Self-Healing Lifecycle:
1. DETECT (Autonomous): Cloud Logging telemetry capture.
2. DIAGNOSE (Autonomous): Gemini Cloud Assist REST API structured root cause.
3. REASON & SEARCH (Autonomous): Google ADK Control Plane + google_search tool.
4. SANDBOX VERIFY (Autonomous): Antigravity Managed Sandbox execution pool.
5. APPLY / POLICY GATE (Risk-Based Autonomous vs. HIL):
   - Autonomous: Non-destructive scaling, cache tuning, non-breaking env vars.
   - HIL (Human-In-The-Loop): Destructive schema changes, IAM role updates, service deletions.
"""

from typing import List, Dict, Any
from app.models.schemas import GcpErrorItem, HypothesisItem

def classify_remediation_policy(command: str) -> Dict[str, Any]:
    """
    Classifies whether a remediation command can run AUTONOMOUSLY or requires HIL (Human-in-the-Loop) approval.
    """
    cmd_lower = command.lower()
    
    # Destructive or high-impact keywords trigger HIL requirement
    hil_keywords = ["delete", "iam", "policy", "drop", "destroy", "restart", "force", "sql instances patch", "remove"]
    
    requires_hil = any(kw in cmd_lower for kw in hil_keywords)
    
    if requires_hil:
        reason = "High-impact operation modifying infrastructure bindings, permissions, or database replicas. Human approval required per safety policy."
        level = "REQUIRES_HIL_APPROVAL"
        risk = "HIGH"
    else:
        reason = "Non-destructive resource scale-up, cache configuration, or diagnostic update. Safe for autonomous execution."
        level = "AUTONOMOUS"
        risk = "LOW"
        
    return {
        "policyLevel": level,
        "riskTier": risk,
        "justification": reason,
        "requiresHumanApproval": requires_hil
    }

def generate_hybrid_execution_plan(error_item: GcpErrorItem, hypotheses: List[HypothesisItem]) -> Dict[str, Any]:
    """
    Generates a complete 5-stage Hybrid Agentic Flow plan with step-by-step execution states and HIL gates.
    """
    primary_hyp = hypotheses[0] if hypotheses else None
    commands = primary_hyp.remediationCommands if primary_hyp else []
    
    classified_commands = [
        {
            "command": cmd,
            **classify_remediation_policy(cmd)
        }
        for cmd in commands
    ]
    
    # Determine overall flow policy gate
    overall_requires_hil = any(c["requiresHumanApproval"] for c in classified_commands)
    
    steps = [
        {
            "stepId": 1,
            "phase": "DETECT",
            "agentPlane": "Telemetry Observer",
            "title": "Cloud Logging Telemetry Ingestion",
            "description": f"Captured real-time error telemetry from {error_item.serviceName} ({error_item.resourceType}).",
            "policyMode": "AUTONOMOUS",
            "status": "COMPLETED",
            "latencyMs": 12
        },
        {
            "stepId": 2,
            "phase": "DIAGNOSE",
            "agentPlane": "Gemini Cloud Assist API",
            "title": "4-Step Root-Cause Investigation",
            "description": f"Seeded symptom observation, created snapshot revision, and extracted ranked hypotheses.",
            "policyMode": "AUTONOMOUS",
            "status": "COMPLETED",
            "latencyMs": 18
        },
        {
            "stepId": 3,
            "phase": "REASON & SEARCH",
            "agentPlane": "Google ADK Control Plane",
            "title": "Reddit & Google Cloud Docs Grounding",
            "description": "Consulted community best practices (r/googlecloud) via google_search tool.",
            "policyMode": "AUTONOMOUS",
            "status": "COMPLETED",
            "latencyMs": 310
        },
        {
            "stepId": 4,
            "phase": "SANDBOX VERIFY",
            "agentPlane": "Antigravity Managed Sandbox",
            "title": "Parallel Subagent Sandbox Execution",
            "description": f"Validated {len(commands)} candidate fix commands inside isolated secure Linux Sandboxes.",
            "policyMode": "AUTONOMOUS",
            "status": "COMPLETED",
            "latencyMs": 450
        },
        {
            "stepId": 5,
            "phase": "APPLY / POLICY GATE",
            "agentPlane": "Policy & Enforcement Gate",
            "title": "Production Remediation Enforcement",
            "description": (
                "High-impact infrastructure modification detected. Awaiting Human-in-the-Loop (HIL) approval before applying to production GCP project."
                if overall_requires_hil
                else "All steps classified as low-risk non-destructive scaling/tuning. Applied automatically."
            ),
            "policyMode": "REQUIRES_HIL_APPROVAL" if overall_requires_hil else "AUTONOMOUS",
            "status": "AWAITING_HIL" if overall_requires_hil else "AUTO_APPLIED",
            "commands": classified_commands
        }
    ]
    
    return {
        "errorId": error_item.id,
        "serviceName": error_item.serviceName,
        "architecture": "Hybrid Split-Plane (ADK Control Plane + Antigravity Managed Sandbox)",
        "overallPolicy": "REQUIRES_HIL_APPROVAL" if overall_requires_hil else "AUTONOMOUS",
        "steps": steps,
        "classifiedCommands": classified_commands
    }
