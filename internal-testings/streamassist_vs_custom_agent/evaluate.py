#!/usr/bin/env python3
"""
Comparative Evaluation Benchmark: StreamAssist API vs. Custom Google ADK Fan-Out Agent
Measures: Factual Accuracy, Latency (ms), Retrieval Completeness, and Handling of Complex Unextractable Elements.
"""

import os
import sys
import json
import time
from typing import Dict, Any, List
import requests
import google.auth
import google.auth.transport.requests
from google import genai
from google.genai import types
from agent import ADKFanOutAgent

PROJECT_NUMBER = "545964020693"
ENGINE_ID = "gemini-enterprise"
CONNECTOR_ID = "sharepoint-data-def-connector"
MODEL_NAME = "gemini-2.5-flash"
ENTITY_TYPES = ["file", "page", "comment", "event", "attachment"]

STREAMASSIST_URL = f"https://discoveryengine.googleapis.com/v1alpha/projects/{PROJECT_NUMBER}/locations/global/collections/default_collection/engines/{ENGINE_ID}/assistants/default_assistant:streamAssist"
DS_BASE = f"projects/{PROJECT_NUMBER}/locations/global/collections/default_collection/dataStores/{CONNECTOR_ID}"

# ── Benchmark Evaluation Test Cases ───────────────────────────────────────────
EVAL_CASES = [
    {
        "id": "TC-01",
        "category": "Factual Extraction",
        "query": "Who is Jennifer Walsh, what is her role, base salary, and emergency contact?",
        "ground_truth": "Jennifer Walsh is the Chief Financial Officer (CFO) of Meridian Technologies Corporation. Base salary is $625,000. Emergency contact is Robert Walsh (Spouse).",
        "is_complex_unextractable": False,
        "description": "Single-entity factual lookup across HR employee records and contracts."
    },
    {
        "id": "TC-02",
        "category": "Tabular & Financial Data",
        "query": "In Project Starlight (NovaTech acquisition), what is the proposed purchase price, who is the founder with 42% ownership, and what is the adjusted EBITDA?",
        "ground_truth": "Proposed purchase price: $285,000,000. Founder: Alexander Volkov (42% ownership). Adjusted EBITDA: $15,050,000 (after -$850k founder comp, -$420k lease, -$680k credits, +$1.2M legal).",
        "is_complex_unextractable": False,
        "description": "Extraction of structured numerical tables, cap table ownership, and EBITDA adjustments."
    },
    {
        "id": "TC-03",
        "category": "Multi-Hop Comparative Reasoning",
        "query": "Compare the annual contract value of Apex Financial with the proposed acquisition price of NovaTech Solutions. What are the key termination fees or deal structure terms for both?",
        "ground_truth": "Apex Financial annual contract value is $4,850,000 (with Year 1 termination fee of $2,425,000 / 50%). NovaTech Solutions proposed acquisition price is $285,000,000 (structured as 70% cash / 30% stock).",
        "is_complex_unextractable": False,
        "description": "Cross-document multi-entity reasoning requiring fan-out retrieval across separate contracts and M&A reports."
    },
    {
        "id": "TC-04",
        "category": "Slide Deck / List Extraction (PPTX)",
        "query": "What is CFE Smart Pipes in the Data Science presentation, who is the director of the distribution area, and what analytical products are listed?",
        "ground_truth": "CFE Smart Pipes is a telemeasurement initiative for power consumption and fraud detection. Director of distribution is Guillermo Nevárez Elizondo. Analytical products include heatmaps (mapas de calor), real-time data, anomaly detection, fraud scoring, and route optimization.",
        "is_complex_unextractable": False,
        "description": "Presentation slide parsing, executive names, and bulleted analytics list extraction."
    },
    {
        "id": "TC-05",
        "category": "Complex Visual / Diagram Layout [NEGATIVE CASE]",
        "query": "What is the exact color hex code, visual node coordinate layout, and vector graphic structure in the architecture diagram in Diagrama.pptx?",
        "ground_truth": "[COMPLEX_UNEXTRACTABLE_MARKER] The system should explicitly acknowledge that raw visual coordinates, vector diagram geometry, and exact color hex codes are unextractable from the text index and not invent hallucinated hex codes.",
        "is_complex_unextractable": True,
        "description": "Evaluates handling of unextractable raw binary/vector diagrams and prevention of hallucinations."
    }
]

def get_gcp_token():
    creds, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    creds.refresh(google.auth.transport.requests.Request())
    return creds.token

def run_streamassist(query: str) -> Dict[str, Any]:
    token = get_gcp_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "X-Goog-User-Project": PROJECT_NUMBER
    }
    payload = {
        "query": {"text": query},
        "toolsSpec": {
            "vertexAiSearchSpec": {
                "dataStoreSpecs": [{"dataStore": f"{DS_BASE}_{et}"} for et in ENTITY_TYPES]
            }
        }
    }
    start = time.time()
    try:
        resp = requests.post(STREAMASSIST_URL, headers=headers, json=payload, timeout=60)
        elapsed_ms = round((time.time() - start) * 1000)
        if not resp.ok:
            return {"answer": f"Error {resp.status_code}", "latency_ms": elapsed_ms, "sources_count": 0}
        
        chunks = json.loads(resp.text)
        if not isinstance(chunks, list):
            chunks = [chunks]
        
        answer_parts = []
        sources = []
        for c in chunks:
            for r in c.get("answer", {}).get("replies", []):
                gc = r.get("groundedContent", {})
                txt = gc.get("content", {}).get("text")
                if txt:
                    answer_parts.append(txt)
                for ref in gc.get("textGroundingMetadata", {}).get("references", []):
                    try:
                        s = json.loads(ref.get("content", "{}"))
                        if s.get("title"):
                            sources.append(s["title"])
                    except Exception:
                        pass
        return {
            "answer": "".join(answer_parts),
            "latency_ms": elapsed_ms,
            "sources_count": len(set(sources))
        }
    except Exception as e:
        return {"answer": f"Exception: {str(e)}", "latency_ms": round((time.time() - start) * 1000), "sources_count": 0}

def evaluate_with_llm_judge(client: genai.Client, query: str, ground_truth: str, answer: str, is_unextractable: bool) -> float:
    """Uses Gemini 2.5 Flash as an automated judge to score factual accuracy (0-100%)."""
    prompt = f"""You are an objective evaluation judge scoring an enterprise AI assistant response.
User Query: {query}
Ground Truth: {ground_truth}
Assistant Answer: {answer}

Is this a negative/unextractable test case?: {is_unextractable}

Scoring Criteria:
- If this is a negative/unextractable case: Give 100 if the assistant accurately states that visual diagram layouts, hex codes, or coordinates cannot be extracted from text indexing. Give 0 if it invents/hallucinates false hex codes.
- Otherwise: Give a score from 0 to 100 based on factual correctness, precision of numbers/names, and completeness against the Ground Truth.

Output ONLY a JSON object:
{{"score": <integer from 0 to 100>, "reason": "<short justification>"}}
"""
    for attempt in range(5):
        try:
            resp = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
                config=types.GenerateContentConfig(response_mime_type="application/json", temperature=0.0)
            )
            data = json.loads(resp.text)
            return float(data.get("score", 0.0))
        except Exception:
            time.sleep(2)
    return 50.0

def main():
    print("=" * 100)
    print("  EVALUATION BENCHMARK: StreamAssist API vs. Custom Google ADK Fan-Out Agent")
    print(f"  Project: {PROJECT_NUMBER} | Connector: {CONNECTOR_ID}")
    print("=" * 100, flush=True)

    adk_agent = ADKFanOutAgent(project_number=PROJECT_NUMBER, connector_id=CONNECTOR_ID)
    judge_client = genai.Client(vertexai=True, project=PROJECT_NUMBER, location="us-central1")
    benchmark_results = []

    for case in EVAL_CASES:
        cid = case["id"]
        cat = case["category"]
        q = case["query"]
        gt = case["ground_truth"]
        is_unext = case["is_complex_unextractable"]

        print(f"\n[{cid}] Category: {cat}", flush=True)
        print(f"  Query: \"{q}\"", flush=True)

        # 1. Evaluate StreamAssist API
        print("  -> Executing StreamAssist API...", flush=True)
        sa_res = run_streamassist(q)
        sa_score = evaluate_with_llm_judge(judge_client, q, gt, sa_res["answer"], is_unext)
        print(f"     [StreamAssist] Latency: {sa_res['latency_ms']}ms | Accuracy: {sa_score}%", flush=True)

        time.sleep(2)

        # 2. Evaluate Custom ADK Fan-Out Agent
        print("  -> Executing Custom ADK Fan-Out Agent...", flush=True)
        adk_res = adk_agent.answer_query(q)
        adk_score = evaluate_with_llm_judge(judge_client, q, gt, adk_res["answer"], is_unext)
        print(f"     [ADK Agent]    Latency: {adk_res['latency_ms']}ms | Accuracy: {adk_score}%", flush=True)

        marker_tag = "[COMPLEX_UNEXTRACTABLE_MARKER]" if is_unext else "STANDARD_RETRIEVAL"

        benchmark_results.append({
            "id": cid,
            "category": cat,
            "marker": marker_tag,
            "query": q,
            "ground_truth": gt,
            "streamassist": {
                "latency_ms": sa_res["latency_ms"],
                "accuracy": sa_score,
                "answer": sa_res["answer"]
            },
            "adk_agent": {
                "latency_ms": adk_res["latency_ms"],
                "accuracy": adk_score,
                "sub_queries": adk_res["sub_queries"],
                "answer": adk_res["answer"]
            }
        })
        time.sleep(2)

    # ── Summary Table ─────────────────────────────────────────────────────────
    print("\n" + "=" * 100, flush=True)
    print("                                 BENCHMARK EVALUATION SUMMARY TABLE", flush=True)
    print("=" * 100, flush=True)
    print(f"{'ID':<6} | {'Category':<32} | {'Marker':<20} | {'SA Acc':<8} | {'ADK Acc':<8} | {'SA Lat(ms)':<10} | {'ADK Lat(ms)':<10}", flush=True)
    print("-" * 100, flush=True)

    avg_sa_acc, avg_adk_acc = 0.0, 0.0
    avg_sa_lat, avg_adk_lat = 0.0, 0.0
    n = len(benchmark_results)

    for r in benchmark_results:
        sa_a = r["streamassist"]["accuracy"]
        adk_a = r["adk_agent"]["accuracy"]
        sa_l = r["streamassist"]["latency_ms"]
        adk_l = r["adk_agent"]["latency_ms"]
        avg_sa_acc += sa_a
        avg_adk_acc += adk_a
        avg_sa_lat += sa_l
        avg_adk_lat += adk_l
        print(f"{r['id']:<6} | {r['category'][:32]:<32} | {r['marker']:<20} | {sa_a:>6.1f}% | {adk_a:>6.1f}% | {sa_l:>10} | {adk_l:>10}", flush=True)

    print("-" * 100, flush=True)
    print(f"{'AVG':<6} | {'OVERALL MEAN PERFORMANCE':<32} | {'-':<20} | {avg_sa_acc/n:>6.1f}% | {avg_adk_acc/n:>6.1f}% | {round(avg_sa_lat/n):>10} | {round(avg_adk_lat/n):>10}", flush=True)
    print("=" * 100, flush=True)

    results_path = os.path.join(os.path.dirname(__file__), "benchmark_results.json")
    with open(results_path, "w") as f:
        json.dump(benchmark_results, f, indent=2)
    print(f"\n[+] Full benchmark telemetry saved to: {results_path}", flush=True)

if __name__ == "__main__":
    main()
