"""Run the 216-question eval using RAG Engine directly with a GA model.

This bypasses Agent Engine and just uses RAG Engine + genai.Client, which is
simpler and matches the baseline rag_md_v2 approach.

Usage:
    uv run --with google-genai python run_agent_engine.py <corpus_resource> <model> <label>

    e.g.
    uv run --with google-genai python run_agent_engine.py \\
        projects/254356041555/locations/us-central1/ragCorpora/8818611020344852480 \\
        gemini-2.5-flash \\
        agent_ga_flash

Writes runs/<label>.json. Uses ADC for auth.
"""
from __future__ import annotations

import asyncio
import json
import os
import sys
import time
from pathlib import Path

from google import genai
from google.genai import types

HERE = Path(__file__).resolve().parent

PROJECT = os.environ.get("EVAL_PROJECT", "vtxdemos")
LOCATION = os.environ.get("EVAL_LOCATION", "global")  # GA models in global
CONCURRENCY = int(os.environ.get("EVAL_CONCURRENCY", "6"))

if len(sys.argv) < 4:
    sys.exit("usage: run_agent_engine.py <rag_corpus_resource> <model> <label>")

RAG_CORPUS = sys.argv[1]
MODEL = sys.argv[2]
OUT_LABEL = sys.argv[3]
OUT_PATH = HERE / "runs" / f"{OUT_LABEL}.json"
OUT_PATH.parent.mkdir(exist_ok=True)

print(f"corpus: {RAG_CORPUS}", file=sys.stderr)
print(f"model:  {MODEL}", file=sys.stderr)
print(f"out:    {OUT_PATH}", file=sys.stderr)

client = genai.Client(vertexai=True, project=PROJECT, location=LOCATION)

tools = [types.Tool(retrieval=types.Retrieval(vertex_rag_store=types.VertexRagStore(
    rag_resources=[types.VertexRagStoreRagResource(rag_corpus=RAG_CORPUS)],
)))]

cfg = types.GenerateContentConfig(
    temperature=1,
    top_p=0.95,
    max_output_tokens=8192,
    safety_settings=[
        types.SafetySetting(category="HARM_CATEGORY_HATE_SPEECH",        threshold="OFF"),
        types.SafetySetting(category="HARM_CATEGORY_DANGEROUS_CONTENT",  threshold="OFF"),
        types.SafetySetting(category="HARM_CATEGORY_SEXUALLY_EXPLICIT",  threshold="OFF"),
        types.SafetySetting(category="HARM_CATEGORY_HARASSMENT",         threshold="OFF"),
    ],
    tools=tools,
    # Note: thinking_config not supported by GA 2.5 models
)


async def ask_one(q, sem):
    async with sem:
        contents = [types.Content(role="user", parts=[types.Part.from_text(text=q["q"])])]
        t0 = time.time()
        try:
            resp = await client.aio.models.generate_content(model=MODEL, contents=contents, config=cfg)
            elapsed = time.time() - t0
            answer = (resp.text or "").strip()
            chunks_used = 0
            try:
                gm = resp.candidates[0].grounding_metadata
                if gm and gm.grounding_chunks:
                    chunks_used = len(gm.grounding_chunks)
            except Exception:
                pass
            return {"id": q["id"], "ok": True, "answer": answer,
                    "chunks_used": chunks_used, "elapsed_s": round(elapsed, 1)}
        except Exception as e:
            return {"id": q["id"], "ok": False,
                    "error": f"{type(e).__name__}: {str(e)[:300]}",
                    "elapsed_s": round(time.time() - t0, 1)}


async def main():
    questions = json.loads((HERE / "questions.json").read_text())
    print(f"[{OUT_LABEL}] starting {len(questions)} questions", file=sys.stderr)
    sem = asyncio.Semaphore(CONCURRENCY)
    results = await asyncio.gather(*[ask_one(q, sem) for q in questions])
    results.sort(key=lambda x: x["id"])
    OUT_PATH.write_text(json.dumps(results, indent=2, ensure_ascii=False))
    n_ok = sum(1 for r in results if r.get("ok"))
    print(f"[{OUT_LABEL}] done. ok={n_ok}/{len(results)}  out={OUT_PATH}", file=sys.stderr)


if __name__ == "__main__":
    asyncio.run(main())
