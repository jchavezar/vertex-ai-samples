import json
import time
import os
import asyncio
from typing import List, Optional
from pydantic import BaseModel, Field
from google import genai
from google.genai import types

# Define structured output schema for the judge
class Judgment(BaseModel):
    precision_score: float = Field(description="Precision score from 0.0 to 100.0 representing percentage of criteria matched factually")
    factual_correctness: bool = Field(description="True if the answer is factually correct and answers the prompt, False otherwise")
    failure_reason: str = Field(description="Failure reason category. Allowed values: 'none', 'rigid_matching_false_negative', 'factual_error', 'data_missing', 'ambiguity_mismatch', 'logic_error'")
    analysis: str = Field(description="Detailed 1-2 sentence explanation of the judgment and score")

async def judge_answer(sem, query: str, ground_truth: str, criteria: List[str], candidate: str) -> Judgment:
    async with sem:
        prompt = f"""You are an expert AI system evaluation judge.
Analyze the Candidate Answer against the Ground Truth Answer and Truth Criteria.
Determine if the Candidate Answer is factually correct, complete, and contains the critical information requested, even if formatting, wording, or minor date styling (e.g. July 23rd vs July 23) differs.

Query: {query}
Ground Truth Answer: {ground_truth}
Truth Criteria: {criteria}
Candidate Answer: {candidate}

Scoring criteria rules:
1. If the Candidate Answer contains all core factual information requested by the query and specified in the criteria, it should get a precision_score close to or equal to 100.0, even if the phrasing differs.
2. If the only difference is date suffix styling (e.g., July 23rd vs July 23) or minor omitted grammatical words ("the", "a"), classify as 'rigid_matching_false_negative' and give 100.0 score.
3. If there is a genuine factual contradiction or missing critical data point, mark factual_correctness as false and score appropriately.
"""
        try:
            # Initialize a fresh client inside each call to prevent shared connection context mutations
            client = genai.Client(vertexai=True, project="254356041555", location="us-central1")
            
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=Judgment,
                        temperature=0.0
                    )
                )
            )
            data = json.loads(response.text)
            return Judgment(**data)
        except Exception as e:
            return Judgment(
                precision_score=0.0,
                factual_correctness=False,
                failure_reason="logic_error",
                analysis=f"Exception during judging: {str(e)}"
            )

async def run_judge_pipeline():
    in_file = "multi_model_evaluated_suite.json"
    out_file = "multi_model_llm_judged_suite.json"
    
    if not os.path.exists(in_file):
        print(f"Error: {in_file} does not exist. Run benchmark first.")
        return

    with open(in_file, "r") as f:
        data = json.load(f)

    results = data.get("results", [])
    print(f"Loaded {len(results)} evaluated test cases. Starting LLM judgment...")

    # Use semaphore of 1 to ensure sequential API processing and prevent Vertex AI token context conflicts
    sem = asyncio.Semaphore(1)
    
    for idx, r in enumerate(results):
        query = r["query"]
        ground_truth = r["ground_truth_answer"]
        criteria = r.get("truth_criteria", [])
        
        print(f"[{idx+1}/100] Judging query: {query[:50]}...")
        
        app_j = await judge_answer(sem, query, ground_truth, criteria, r["app_answer"])
        sa_j = await judge_answer(sem, query, ground_truth, criteria, r["streamassist_answer"])
        
        r["app_judgment"] = app_j.model_dump()
        r["streamassist_judgment"] = sa_j.model_dump()
        
        r["llm_precision_score_36"] = app_j.precision_score
        r["llm_streamassist_precision"] = sa_j.precision_score

    # Re-calculate overall statistics
    num_cases = len(results)
    avg_app_rigid = round(sum(r["precision_score_36"] for r in results) / num_cases, 1)
    avg_app_llm = round(sum(r["llm_precision_score_36"] for r in results) / num_cases, 1)
    
    avg_sa_rigid = round(sum(r["streamassist_precision"] for r in results) / num_cases, 1)
    avg_sa_llm = round(sum(r["llm_streamassist_precision"] for r in results) / num_cases, 1)

    app_failures = [r for r in results if r["app_judgment"]["failure_reason"] != "none"]
    sa_failures = [r for r in results if r["streamassist_judgment"]["failure_reason"] != "none"]

    summary = data.get("summary", {})
    summary["gemini_36_flash"]["llm_precision"] = avg_app_llm
    summary["streamassist_federated"]["llm_precision"] = avg_sa_llm
    summary["llm_judge_timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())

    # Write output file
    with open(out_file, "w") as f:
        json.dump(data, f, indent=2)

    print("\n==============================================")
    print("           LLM JUDGE EVALUATION COMPLETED      ")
    print("==============================================")
    print(f"Gemini 3.6 Flash (MCP):")
    print(f"  - Rigid Substring Precision: {avg_app_rigid}%")
    print(f"  - LLM Unbiased Precision:    {avg_app_llm}%")
    print(f"  - Classified Failures:       {len(app_failures)} cases")
    print(f"StreamAssist (Federated):")
    print(f"  - Rigid Substring Precision: {avg_sa_rigid}%")
    print(f"  - LLM Unbiased Precision:    {avg_sa_llm}%")
    print(f"  - Classified Failures:       {len(sa_failures)} cases")
    print("==============================================")
    print(f"Results saved to: {out_file}")

if __name__ == "__main__":
    # Inject criteria map from golden_100_suite.json
    golden_suite_file = "evaluations/golden_100_suite.json"
    if os.path.exists(golden_suite_file):
        with open(golden_suite_file, "r") as f:
            suite = json.load(f)
        criteria_map = {tc["id"]: tc.get("truth_criteria", []) for tc in suite}
        
        # Load multi model results
        in_file = "multi_model_evaluated_suite.json"
        if os.path.exists(in_file):
            with open(in_file, "r") as f:
                data = json.load(f)
            for r in data.get("results", []):
                r["truth_criteria"] = criteria_map.get(r["id"], [])
            with open(in_file, "w") as f:
                json.dump(data, f, indent=2)
                
    asyncio.run(run_judge_pipeline())
