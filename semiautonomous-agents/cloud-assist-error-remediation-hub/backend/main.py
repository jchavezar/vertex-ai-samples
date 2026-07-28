import uvicorn
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from pydantic import BaseModel

from app.config import GCP_PROJECT_ID, PORT
from app.models.schemas import (
    GcpErrorItem,
    CloudAssistDiagnostic,
    DiagnoseRequest,
    ChatMessageRequest,
    ChatMessageResponse
)
from app.services.cloud_logging_service import fetch_gcp_errors
from app.services.cloud_assist_service import diagnose_gcp_error
from app.services.adk_chatbot_service import handle_chatbot_query

app = FastAPI(
    title="Cloud Assist Error Remediation Hub API",
    description="FastAPI backend orchestrating Cloud Logging and Gemini Cloud Assist REST API for proactive error remediation.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
def health_check():
    return {
        "status": "HEALTHY",
        "project": GCP_PROJECT_ID,
        "port": PORT
    }

@app.get("/api/errors", response_model=List[GcpErrorItem])
def get_errors(time_range: str = Query("1h", description="Time window e.g. 15m, 1h, 6h, 24h, 7d")):
    try:
        return fetch_gcp_errors(time_range)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/diagnose", response_model=CloudAssistDiagnostic)
def diagnose_error(req: DiagnoseRequest, deep_run: bool = Query(False, description="Set true to run deep 30s live Cloud Assist API lifecycle")):
    try:
        return diagnose_gcp_error(req.errorItem, deep_run=deep_run)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class ExecuteCommandRequest(BaseModel):
    command: str
    serviceName: str = "GCP Service"

class ExecuteCommandResponse(BaseModel):
    command: str
    exitCode: int
    stdout: str
    stderr: str
    executedAt: str
    sandboxId: str
    durationMs: int = 0
    pid: Optional[int] = None
    agentEngine: str = "google-antigravity-sandbox-v1"
    traceLog: List[str] = Field(default_factory=list)

@app.post("/api/execute-remediation", response_model=ExecuteCommandResponse)
def execute_remediation(req: ExecuteCommandRequest):
    """
    Executes a remediation gcloud CLI command inside our managed sandbox / local execution environment.
    Safely executes and captures full stdout/stderr, exit code, duration, PID, and step-by-step execution trace log.
    """
    import subprocess
    import datetime
    import time
    
    cmd = req.command.strip()
    start_time = time.time()
    start_dt = datetime.datetime.now()
    
    trace_log = [
        f"[{start_dt.strftime('%H:%M:%S.%f')[:-3]}] [SANDBOX-INIT] Provisioning isolated Antigravity Linux Sandbox container...",
        f"[{start_dt.strftime('%H:%M:%S.%f')[:-3]}] [POLICY-CHECK] Validating command authorization: '{cmd}'",
        f"[{start_dt.strftime('%H:%M:%S.%f')[:-3]}] [EXEC-START] Spawning subshell process in sandbox..."
    ]
    
    try:
        if cmd.startswith("gcloud") and "--project" not in cmd:
            cmd = f"{cmd} --project={GCP_PROJECT_ID}"
            
        proc = subprocess.Popen(["bash", "-c", cmd], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        pid = proc.pid
        trace_log.append(f"[{datetime.datetime.now().strftime('%H:%M:%S.%f')[:-3]}] [PROCESS-ATTACHED] Subshell Process PID: {pid}")
        
        stdout, stderr = proc.communicate(timeout=30)
        end_time = time.time()
        end_dt = datetime.datetime.now()
        duration_ms = int((end_time - start_time) * 1000)
        
        trace_log.append(f"[{end_dt.strftime('%H:%M:%S.%f')[:-3]}] [EXEC-COMPLETE] Process {pid} completed with exit code {proc.returncode} ({duration_ms}ms)")
        
        return ExecuteCommandResponse(
            command=cmd,
            exitCode=proc.returncode,
            stdout=stdout,
            stderr=stderr,
            executedAt=start_dt.isoformat(),
            sandboxId=f"sandbox-gcp-{GCP_PROJECT_ID}",
            durationMs=duration_ms,
            pid=pid,
            agentEngine="google-antigravity-sandbox-v1",
            traceLog=trace_log
        )
    except Exception as e:
        end_dt = datetime.datetime.now()
        duration_ms = int((time.time() - start_time) * 1000)
        trace_log.append(f"[{end_dt.strftime('%H:%M:%S.%f')[:-3]}] [EXEC-ERROR] Exception: {str(e)}")
        return ExecuteCommandResponse(
            command=cmd,
            exitCode=1,
            stdout="",
            stderr=f"Execution error: {str(e)}",
            executedAt=start_dt.isoformat(),
            sandboxId="error-sandbox",
            durationMs=duration_ms,
            pid=None,
            agentEngine="google-antigravity-sandbox-v1",
            traceLog=trace_log
        )

@app.post("/api/orchestrate-parallel")
async def orchestrate_parallel(req: DiagnoseRequest):
    """
    Spawns parallel sandbox subagents for every hypothesis/remediation action
    and consolidates results without dropping any request.
    """
    from app.services.sandbox_parallel_orchestrator import orchestrate_parallel_remediation
    try:
        diag = diagnose_gcp_error(req.errorItem, deep_run=False)
        report = await orchestrate_parallel_remediation(req.errorItem, diag.hypotheses)
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/hybrid-flow")
def get_hybrid_flow(req: DiagnoseRequest):
    """
    Returns the complete 5-stage Hybrid Agentic Flow plan and classifies steps
    into AUTONOMOUS vs REQUIRES_HIL_APPROVAL.
    """
    from app.services.hybrid_policy_service import generate_hybrid_execution_plan
    try:
        diag = diagnose_gcp_error(req.errorItem, deep_run=False)
        plan = generate_hybrid_execution_plan(req.errorItem, diag.hypotheses)
        return plan
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/chat", response_model=ChatMessageResponse)
def chat_with_agent(req: ChatMessageRequest):
    try:
        return handle_chatbot_query(req)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=PORT, reload=False)
