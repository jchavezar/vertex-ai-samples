"""Run the 216-question eval against Gemini Enterprise streamAssist with GA model.

Usage:
    uv run --with google-cloud-discoveryengine python run_streamassist_ga.py <app_id> <model> <label>

    e.g.
    uv run --with google-cloud-discoveryengine python run_streamassist_ga.py \\
        acc \\
        gemini-2.5-flash \\
        ge_ga_flash

Writes runs/<label>.json. Uses ADC for auth.
"""
from __future__ import annotations

import asyncio
import json
import os
import sys
import time
from pathlib import Path

from google.cloud import discoveryengine_v1alpha as discoveryengine

HERE = Path(__file__).resolve().parent

GE_PROJECT = os.environ.get("GE_PROJECT", "sharepoint-wif")
GE_PROJECT_NUMBER = os.environ.get("GE_PROJECT_NUMBER", "984359513632")
CONCURRENCY = int(os.environ.get("EVAL_CONCURRENCY", "6"))

if len(sys.argv) < 4:
    sys.exit("usage: run_streamassist_ga.py <app_id> <model> <label>")

APP_ID = sys.argv[1]
MODEL = sys.argv[2]
OUT_LABEL = sys.argv[3]
OUT_PATH = HERE / "runs" / f"{OUT_LABEL}.json"
OUT_PATH.parent.mkdir(exist_ok=True)

ASSISTANT_PATH = (
    f"projects/{GE_PROJECT_NUMBER}/locations/global/"
    f"collections/default_collection/engines/{APP_ID}/"
    f"assistants/default_assistant"
)

print(f"assistant: {ASSISTANT_PATH}", file=sys.stderr)
print(f"model:     {MODEL}", file=sys.stderr)
print(f"out:       {OUT_PATH}", file=sys.stderr)


async def ask_one(client, q, sem):
    async with sem:
        t0 = time.time()
        try:
            # Build the streamAssist request with GA model
            request = discoveryengine.StreamAssistRequest(
                assistant=ASSISTANT_PATH,
                query=discoveryengine.Query(
                    parts=[discoveryengine.Query.Part(text=q["q"])]
                ),
                tools_spec=discoveryengine.ToolsSpec(
                    answer_model_spec=discoveryengine.ToolsSpec.AnswerModelSpec(
                        model=f"publishers/google/models/{MODEL}"
                    )
                ),
                assist_skipping_mode=discoveryengine.StreamAssistRequest.AssistSkippingMode.ASSIST_SKIPPING_MODE_UNSPECIFIED,
            )

            # Call streamAssist
            response = await asyncio.to_thread(client.stream_assist, request=request)

            # Collect chunks
            answer_parts = []
            chunks_used = 0

            for chunk in response:
                if chunk.answer_chunk and chunk.answer_chunk.text:
                    answer_parts.append(chunk.answer_chunk.text)
                if chunk.grounding_chunks:
                    chunks_used += len(chunk.grounding_chunks)

            answer = "".join(answer_parts).strip()
            elapsed = time.time() - t0

            return {
                "id": q["id"],
                "ok": True,
                "answer": answer,
                "chunks_used": chunks_used,
                "elapsed_s": round(elapsed, 1)
            }
        except Exception as e:
            return {
                "id": q["id"],
                "ok": False,
                "error": f"{type(e).__name__}: {str(e)[:300]}",
                "elapsed_s": round(time.time() - t0, 1)
            }


async def main():
    client = discoveryengine.AssistServiceAsyncClient()
    questions = json.loads((HERE / "questions.json").read_text())
    print(f"[{OUT_LABEL}] starting {len(questions)} questions", file=sys.stderr)

    sem = asyncio.Semaphore(CONCURRENCY)
    results = await asyncio.gather(*[ask_one(client, q, sem) for q in questions])
    results.sort(key=lambda x: x["id"])

    OUT_PATH.write_text(json.dumps(results, indent=2, ensure_ascii=False))
    n_ok = sum(1 for r in results if r.get("ok"))
    print(f"[{OUT_LABEL}] done. ok={n_ok}/{len(results)}  out={OUT_PATH}", file=sys.stderr)


if __name__ == "__main__":
    asyncio.run(main())
