import json
import os
import sys
import time
import asyncio
import subprocess
import httpx
from typing import List
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

# Structured schema for judge output
class Judgment(BaseModel):
    precision_score: float = Field(description="Precision score from 0.0 to 100.0 representing percentage of criteria matched factually")
    factual_correctness: bool = Field(description="True if the answer is factually correct, False otherwise")
    failure_reason: str = Field(description="Failure reason category. Allowed values: 'none', 'rigid_matching_false_negative', 'factual_error', 'data_missing', 'ambiguity_mismatch', 'logic_error'")
    analysis: str = Field(description="Short 1-2 sentence explanation of the judgment and score")

# Structured schema for auto-fix output
class PromptFix(BaseModel):
    revised_instructions: str = Field(description="The complete, updated system instructions text block incorporating the fix")
    explanation: str = Field(description="Detailed explanation of the changes made and why they resolve the failure")

# Initialize ONE global Vertex AI GenAI Client
CLIENT = genai.Client(vertexai=True, project="254356041555", location="us-central1")

async def run_single_eval(query: str) -> dict:
    url = "http://localhost:8001/api/search"
    payload = {"query": query, "timezone": "America/New_York"}
    t0 = time.time()
    response_text = ""
    tools_called = []
    
    try:
        async with httpx.AsyncClient(timeout=180.0) as http_client:
            async with http_client.stream("POST", url, json=payload, headers={"X-Entra-Id-Token": "session-active-token"}) as response:
                if response.status_code != 200:
                    err_content = await response.aread()
                    return {"answer": f"Error {response.status_code}: {err_content.decode('utf-8')}", "tools_called": [], "latency_s": round(time.time() - t0, 2)}
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:].strip()
                        if not data_str: continue
                        try:
                            evt = json.loads(data_str)
                            if evt.get("type") == "text":
                                response_text += evt.get("text", "")
                            elif evt.get("type") == "tool_call":
                                t_name = evt.get("tool", {}).get("name")
                                if t_name: tools_called.append(t_name)
                        except Exception:
                            pass
        return {"answer": response_text.strip(), "tools_called": tools_called, "latency_s": round(time.time() - t0, 2)}
    except Exception as e:
        return {"answer": f"Exception: {e}", "tools_called": [], "latency_s": round(time.time() - t0, 2)}

async def judge_answer(query: str, ground_truth: str, criteria: List[str], candidate: str) -> Judgment:
    prompt = f"""You are an expert AI system evaluation judge.
Analyze the Candidate Answer against the Ground Truth Answer and Truth Criteria.
Determine if the Candidate Answer is factually correct, complete, and contains the critical information requested, even if formatting or wording styling differs.

Query: {query}
Ground Truth Answer: {ground_truth}
Truth Criteria: {criteria}
Candidate Answer: {candidate}
"""
    try:
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: CLIENT.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=Judgment,
                    temperature=0.0
                )
            )
        )
        return Judgment(**json.loads(response.text))
    except Exception as e:
        return Judgment(precision_score=0.0, factual_correctness=False, failure_reason="logic_error", analysis=str(e))

async def suggest_prompt_fix(query: str, expected_tool: str, ground_truth: str, candidate: str, tools_called: List[str], judgment: Judgment, current_instructions: str) -> PromptFix:
    prompt = f"""You are an expert Prompt Engineer and ADK Agent optimization system.
Your task is to revise the system instructions for the ADK agent to fix a specific failure in its evaluation benchmark.

Test Case Details:
- Query: {query}
- Expected Tool: {expected_tool}
- Ground Truth Answer: {ground_truth}
- Actual Agent Answer: {candidate}
- Tools Called: {tools_called}
- Judge Score: {judgment.precision_score}
- Failure Reason: {judgment.failure_reason}
- Judge Analysis: {judgment.analysis}

Current System Instructions:
{current_instructions}

Based on the failure details and analysis, suggest a precise modification to the system instructions to fix this error. Keep the instructions professional, low-latency, and safe.
Return only the complete updated instructions text block.
"""
    try:
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: CLIENT.models.generate_content(
                model="gemini-2.5-pro", # Use Pro for sophisticated prompt engineering tasks
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=PromptFix,
                    temperature=0.2
                )
            )
        )
        return PromptFix(**json.loads(response.text))
    except Exception as e:
        # Fallback to flash if pro is unavailable / throttled
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: CLIENT.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=PromptFix,
                    temperature=0.2
                )
            )
        )
        return PromptFix(**json.loads(response.text))

def redeploy_agent():
    print("Redeploying updated agent engine to Vertex AI...")
    cwd = "/Users/jesusarguelles/IdeaProjects/vertex-ai-samples/semiautonomous-agents/custom_ui_mcp_outlook/remote-agentruntime-mcp/adk-agent"
    res = subprocess.run(["python3", "deploy.py"], cwd=cwd, capture_output=True, text=True)
    if res.returncode == 0:
        print("Agent deployment successful.")
        return True
    else:
        print(f"Agent deployment failed: {res.stderr}")
        return False

async def run_autofix_for_cases(case_ids: List[str]):
    suite_file = "golden_100_suite.json" if os.path.exists("golden_100_suite.json") else "evaluations/golden_100_suite.json"
    instructions_file = "remote-agentruntime-mcp/adk-agent/system_instructions.txt" if os.path.exists("remote-agentruntime-mcp/adk-agent/system_instructions.txt") else "../remote-agentruntime-mcp/adk-agent/system_instructions.txt"
    
    with open(suite_file, "r") as f:
        suite = json.load(f)
    cases = [c for c in suite if c["id"] in case_ids]
    
    if not cases:
        print("No test cases found matching specified IDs.")
        return

    for case in cases:
        print(f"\n==================================================")
        print(f"Starting Auto-Fix Cycle for {case['id']}: {case['query'][:50]}...")
        print(f"==================================================")
        
        # Read current instructions
        with open(instructions_file, "r") as f:
            current_instr = f.read()

        # Step 1: Run Evaluation
        print("Executing test query on agent...")
        res = await run_single_eval(case["query"])
        print(f"Agent Response: {res['answer'][:150]}...")
        print(f"Tools Called: {res['tools_called']}")

        # Step 2: Judge Output
        print("Judging answer...")
        judgment = await judge_answer(case["query"], case["ground_truth_answer"], case.get("truth_criteria", []), res["answer"])
        print(f"Judge Score: {judgment.precision_score}% | Factual: {judgment.factual_correctness} | Reason: {judgment.failure_reason}")
        print(f"Judge Analysis: {judgment.analysis}")

        if judgment.precision_score >= 90.0 or judgment.failure_reason == "rigid_matching_false_negative":
            print(f"Test case {case['id']} passed or is a rigid matching false negative. No fix needed.")
            continue

        # Step 3: Suggest Fix
        print("Invoking Auto-Fixer Prompt Optimizer...")
        fix = await suggest_prompt_fix(
            case["query"], case.get("expected_tool", ""), case["ground_truth_answer"],
            res["answer"], res["tools_called"], judgment, current_instr
        )
        print(f"Auto-Fixer Explanation: {fix.explanation}")

        # Step 4: Write & Deploy
        print("Applying instruction fixes to system_instructions.txt...")
        with open(instructions_file, "w") as f:
            f.write(fix.revised_instructions.strip())

        # Redeploy
        if redeploy_agent():
            print("Verifying fix by re-running query...")
            re_res = await run_single_eval(case["query"])
            re_judgment = await judge_answer(case["query"], case["ground_truth_answer"], case.get("truth_criteria", []), re_res["answer"])
            print(f"Re-test Judge Score: {re_judgment.precision_score}% | Factual: {re_judgment.factual_correctness}")
            print(f"Re-test Analysis: {re_judgment.analysis}")
            if re_judgment.precision_score >= 90.0:
                print(f"FIX SUCCESSFUL! Test case {case['id']} is now passing.")
            else:
                print(f"Fix applied, but score is still {re_judgment.precision_score}%. Reverting instructions to prevent side effects.")
                with open(instructions_file, "w") as f:
                    f.write(current_instr)
                redeploy_agent()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 autofix_pipeline.py <case_id1> <case_id2> ...")
        sys.exit(1)
    target_cases = sys.argv[1:]
    asyncio.run(run_autofix_for_cases(target_cases))
