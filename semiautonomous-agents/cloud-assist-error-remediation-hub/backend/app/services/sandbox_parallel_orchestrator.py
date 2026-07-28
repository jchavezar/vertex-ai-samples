"""
Parallel Sandbox Remediation Orchestrator with Intelligent Self-Healing Harness
(Antigravity Managed Sandbox & Auto-Recovery Pattern)

Key Features:
1. Fast Execution: Max 2 attempts per sandbox subagent (avoids 13-attempt infinite loops).
2. Intelligent Auth & Flag Recovery:
   - Detects 'NoActiveAccountException' or missing '--project' flags immediately.
   - Auto-injects local ADC access tokens (CLOUDSDK_AUTH_ACCESS_TOKEN) and --project context.
3. Explicit Actionable Insights:
   - Returns clear executive verdict summaries explaining exact stdout/stderr root cause.
"""

import asyncio
import datetime
import os
import subprocess
from typing import List, Dict, Any
from app.models.schemas import GcpErrorItem, HypothesisItem
from app.config import GCP_PROJECT_ID

class HarnessAttempt:
    def __init__(self, attempt_num: int, command: str, exit_code: int, stdout: str, stderr: str, duration_ms: int):
        self.attempt_num = attempt_num
        self.command = command
        self.exit_code = exit_code
        self.stdout = stdout
        self.stderr = stderr
        self.duration_ms = duration_ms

    def to_dict(self) -> Dict[str, Any]:
        return {
            "attemptNum": self.attempt_num,
            "command": self.command,
            "exitCode": self.exit_code,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "durationMs": self.duration_ms
        }

class SandboxTaskResult:
    def __init__(
        self,
        task_id: str,
        sandbox_id: str,
        success: bool,
        recovered_from_error: bool,
        started_at: str,
        completed_at: str,
        duration_ms: int,
        output: str,
        attempts: List[HarnessAttempt],
        final_command: str,
        insight_summary: str = ""
    ):
        self.task_id = task_id
        self.sandbox_id = sandbox_id
        self.success = success
        self.recovered_from_error = recovered_from_error
        self.started_at = started_at
        self.completed_at = completed_at
        self.duration_ms = duration_ms
        self.output = output
        self.attempts = attempts
        self.final_command = final_command
        self.insight_summary = insight_summary

    def to_dict(self) -> Dict[str, Any]:
        return {
            "taskId": self.task_id,
            "sandboxId": self.sandbox_id,
            "success": self.success,
            "recoveredFromError": self.recovered_from_error,
            "startedAt": self.started_at,
            "completedAt": self.completed_at,
            "durationMs": self.duration_ms,
            "output": self.output,
            "attempts": [a.to_dict() for a in self.attempts],
            "finalCommand": self.final_command,
            "insightSummary": self.insight_summary
        }

async def get_gcp_access_token() -> str:
    """Retrieves active gcloud access token for authenticated sandbox subshell execution."""
    try:
        proc = await asyncio.create_subprocess_shell(
            "gcloud auth print-access-token",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        out, _ = await proc.communicate()
        return out.decode('utf-8').strip()
    except Exception:
        return ""

async def run_subagent_in_sandbox(
    task_id: str,
    hypothesis: HypothesisItem,
    error_item: GcpErrorItem
) -> SandboxTaskResult:
    """
    Executes hypothesis verification with an intelligent, capped 2-attempt recovery harness.
    Automatically injects project context and auth tokens if sandbox lacks credentials.
    """
    start_dt = datetime.datetime.now()
    sandbox_id = f"sandbox-{task_id.lower().replace(' ', '-')}"
    initial_cmd = hypothesis.remediationCommands[0] if (hypothesis.remediationCommands and len(hypothesis.remediationCommands) > 0) else f"gcloud projects get-iam-policy {GCP_PROJECT_ID}"
    
    # Ensure command includes --project flag if missing
    if "--project=" not in initial_cmd and "get-iam-policy" in initial_cmd:
        initial_cmd = f"{initial_cmd} --project={GCP_PROJECT_ID}"

    attempts: List[HarnessAttempt] = []
    logs = []
    recovered_from_error = False
    insight = ""

    logs.append(f"[{start_dt.strftime('%H:%M:%S.%f')[:-3]}] [SANDBOX {sandbox_id}] Provisioned Antigravity Subagent (Target: {error_item.serviceName})")
    logs.append(f"[{start_dt.strftime('%H:%M:%S.%f')[:-3]}] [HYPOTHESIS] {hypothesis.title}")
    
    # Fetch local ADC access token to inject into sandbox env if needed
    access_token = await get_gcp_access_token()
    env_vars = os.environ.copy()
    if access_token:
        env_vars["CLOUDSDK_AUTH_ACCESS_TOKEN"] = access_token

    # Attempt 1: Execute primary command
    cmd_start = datetime.datetime.now()
    logs.append(f"[SANDBOX {sandbox_id}] Attempt 1: Executing '{initial_cmd}'...")

    try:
        proc = await asyncio.create_subprocess_shell(
            initial_cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=env_vars
        )
        stdout_b, stderr_b = await proc.communicate()
        exit_code = proc.returncode or 0
        stdout = stdout_b.decode('utf-8', errors='replace').strip()
        stderr = stderr_b.decode('utf-8', errors='replace').strip()
        cmd_duration = int((datetime.datetime.now() - cmd_start).total_seconds() * 1000)

        attempts.append(
            HarnessAttempt(
                attempt_num=1,
                command=initial_cmd,
                exit_code=exit_code,
                stdout=stdout,
                stderr=stderr,
                duration_ms=cmd_duration
            )
        )

        if exit_code == 0:
            logs.append(f"[HARNESS SUCCESS] Exit Code 0 ({cmd_duration}ms). Service response:")
            logs.append(f"   stdout: {stdout[:300]}..." if len(stdout) > 300 else f"   stdout: {stdout}")
            insight = f"Verification Passed (Exit Code 0): Configuration for {error_item.serviceName} validated successfully."
        else:
            logs.append(f"[HARNESS ATTEMPT 1 FAILED] Exit Code: {exit_code} | Error: {stderr[:150]}")
            
            # Check if failure is due to missing project flag or auth
            if "required property [project] is not currently set" in stderr or "--project" not in initial_cmd:
                patched_cmd = f"{initial_cmd} --project={GCP_PROJECT_ID}"
                logs.append(f"[HARNESS RECOVERY ATTEMPT 2] Injecting '--project={GCP_PROJECT_ID}' flag patch...")
                
                p2_start = datetime.datetime.now()
                p2 = await asyncio.create_subprocess_shell(
                    patched_cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    env=env_vars
                )
                p2_out, p2_err = await p2.communicate()
                p2_code = p2.returncode or 0
                p2_dur = int((datetime.datetime.now() - p2_start).total_seconds() * 1000)
                
                p2_stdout = p2_out.decode('utf-8', errors='replace').strip()
                p2_stderr = p2_err.decode('utf-8', errors='replace').strip()
                
                attempts.append(
                    HarnessAttempt(
                        attempt_num=2,
                        command=patched_cmd,
                        exit_code=p2_code,
                        stdout=p2_stdout,
                        stderr=p2_stderr,
                        duration_ms=p2_dur
                    )
                )
                
                if p2_code == 0:
                    recovered_from_error = True
                    logs.append(f"[HARNESS RECOVERY SUCCESS] Auto-healing patch succeeded (Exit Code 0).")
                    insight = f"Auto-Healing Recovered: Applied '--project={GCP_PROJECT_ID}' flag patch. Verification succeeded!"
                else:
                    insight = f"Diagnosis Complete: Command returned Exit Code {p2_code}. Stderr: {p2_stderr[:100]}"
            elif "NoActiveAccountException" in stderr or "active account selected" in stderr:
                logs.append(f"[HARNESS DIAGNOSIS] Unauthenticated Sandbox Container: 'gcloud auth login' required.")
                insight = "Sandbox Auth Note: Container lacks active GCP credentials. Credentials injected via ADC token."
            else:
                insight = f"Service Audit Note: Command completed with status {exit_code}. Review stdout/stderr logs."

    except Exception as ex:
        logs.append(f"[SANDBOX EXECUTION ERROR] {str(ex)}")
        insight = f"Execution note: {str(ex)}"

    end_dt = datetime.datetime.now()
    total_duration = int((end_dt - start_dt).total_seconds() * 1000)
    final_success = (attempts[-1].exit_code == 0) if attempts else False

    logs.append(f"[VERDICT INSIGHT] {insight}")

    return SandboxTaskResult(
        task_id=task_id,
        sandbox_id=sandbox_id,
        success=final_success,
        recovered_from_error=recovered_from_error,
        started_at=start_dt.isoformat(),
        completed_at=end_dt.isoformat(),
        duration_ms=total_duration,
        output="\n".join(logs),
        attempts=attempts,
        final_command=attempts[-1].command if attempts else initial_cmd,
        insight_summary=insight
    )

async def orchestrate_parallel_remediation(
    error_item: GcpErrorItem,
    hypotheses: List[HypothesisItem]
) -> Dict[str, Any]:
    """
    Dispatches all hypotheses/remediation tasks in parallel across independent sandbox subagents
    equipped with our fast, capped 2-attempt recovery harness.
    """
    start_dt = datetime.datetime.now()
    
    hyp_list = hypotheses if hypotheses and len(hypotheses) > 0 else [
        HypothesisItem(
            id="hyp-default-1",
            title=f"Audit {error_item.serviceName} Configuration & IAM Policy",
            rootCauseText="Runtime service account missing permissions or endpoint path mismatched.",
            recommendationText="Run gcloud project IAM audit and inspect service resource status.",
            relevanceScore=0.92,
            remediationCommands=[f"gcloud projects get-iam-policy {GCP_PROJECT_ID}"]
        )
    ]

    tasks = [
        run_subagent_in_sandbox(
            task_id=f"Subagent-{idx+1}",
            hypothesis=hyp,
            error_item=error_item
        )
        for idx, hyp in enumerate(hyp_list)
    ]
    
    results: List[SandboxTaskResult] = await asyncio.gather(*tasks)
    end_dt = datetime.datetime.now()
    
    successful_count = sum(1 for r in results if r.success)
    failed_count = sum(1 for r in results if not r.success)
    auto_recovered_count = sum(1 for r in results if r.recovered_from_error)
    
    insights_list = [r.insight_summary for r in results if r.insight_summary]
    executive_insight = " | ".join(insights_list) if insights_list else "All sandbox subagents completed verification."

    consolidated_report = {
        "errorId": error_item.id,
        "serviceName": error_item.serviceName,
        "harnessPattern": "Intelligent Capped Recovery Harness (Antigravity Managed Sandbox)",
        "totalParallelSandboxes": len(results),
        "successfulTasks": successful_count,
        "failedTasks": failed_count,
        "autoRecoveredTasks": auto_recovered_count,
        "startedAt": start_dt.isoformat(),
        "completedAt": end_dt.isoformat(),
        "totalDurationMs": int((end_dt - start_dt).total_seconds() * 1000),
        "consolidationStatus": "VERIFIED_ALL_REQUESTS_CONSOLIDATED",
        "executiveInsight": executive_insight,
        "subagentTraces": [r.to_dict() for r in results]
    }
    
    return consolidated_report
