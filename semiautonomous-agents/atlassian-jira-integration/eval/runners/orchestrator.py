"""Run pipelines (A, B, C, D, E, F) over a question set in parallel.

Per-pipeline asyncio.Semaphore (default 6). Resumable: skips IDs already
present in responses_{a,b,c,d,e}.jsonl. --smoke N runs only the first N questions.

Usage:
  python -m runners.orchestrator --questions questions/main.json --out runs/<ts>
  python -m runners.orchestrator --questions questions/_smoke.json --smoke 5 --out runs/_smoke
  python -m runners.orchestrator --questions runs/_smoke_latency/questions.json --only d --out runs/_smoke_d
  python -m runners.orchestrator --questions runs/_smoke_latency/questions.json --only e --out runs/_smoke_e
"""
from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Sequence

import httpx

# Allow running both as a module (-m runners.orchestrator) and as a script.
if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from runners import _common as C
# Lazy imports per pipeline to avoid dependency bloat
run_a_one = None
run_b_one = None
run_c_one = None
run_d_one = None
run_e_one = None
run_f_one = None


async def _run_pipeline(
    name: str,
    runner,
    questions: Sequence[dict[str, Any]],
    out_jsonl: Path,
    raw_dir: Path,
    sem: asyncio.Semaphore,
    client: httpx.AsyncClient,
) -> None:
    done = C.already_done_ids(out_jsonl)
    todo = [q for q in questions if q["id"] not in done]
    print(f"[{name}] {len(done)} already done, {len(todo)} to run.", flush=True)

    async def _wrapped(q: dict[str, Any]) -> None:
        async with sem:
            t0 = time.time()
            try:
                result = await runner(q, client, raw_dir)
            except Exception as exc:  # belt + suspenders
                result = C.RunnerResult(id=q["id"], pipeline=name, ok=False, answer="", error=f"runner crash: {exc}")
            C.append_jsonl(out_jsonl, result.to_jsonl_line())
            tag = "OK" if result.ok else "ERR"
            print(f"[{name}] {tag} {q['id']:>6}  {result.elapsed_s:5.1f}s  {(result.error or result.answer[:60])}", flush=True)

    await asyncio.gather(*[_wrapped(q) for q in todo])


async def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--questions", required=True, help="path to questions/main.json")
    ap.add_argument("--out", required=True, help="run output dir, e.g. runs/_smoke")
    ap.add_argument("--smoke", type=int, default=0, help="run only first N questions")
    ap.add_argument("--only", choices=["a", "b", "c", "d", "e", "f", "g", "both"], default="both")
    ap.add_argument("--concurrency", type=int, default=int(os.environ.get("EVAL_CONCURRENCY", "6")))
    args = ap.parse_args()

    qs: list[dict[str, Any]] = json.loads(Path(args.questions).read_text())
    if args.smoke:
        qs = qs[: args.smoke]
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    raw = out / "raw"

    sem_a = asyncio.Semaphore(args.concurrency)
    sem_b = asyncio.Semaphore(args.concurrency)
    sem_c = asyncio.Semaphore(args.concurrency)
    sem_d = asyncio.Semaphore(args.concurrency)
    sem_e = asyncio.Semaphore(args.concurrency)
    timeout = httpx.Timeout(connect=20.0, read=300.0, write=60.0, pool=60.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        tasks = []
        if args.only in ("a", "both"):
            from runners.run_option_a import run_one as run_a_one
            tasks.append(_run_pipeline("a", run_a_one, qs, out / "responses_a.jsonl", raw, sem_a, client))
        if args.only in ("b", "both"):
            from runners.run_option_b import run_one as run_b_one
            tasks.append(_run_pipeline("b", run_b_one, qs, out / "responses_b.jsonl", raw, sem_b, client))
        if args.only == "c":
            from runners.run_option_c import run_one as run_c_one
            tasks.append(_run_pipeline("c", run_c_one, qs, out / "responses_c.jsonl", raw, sem_c, client))
        if args.only == "d":
            from runners.run_option_d import run_one as run_d_one
            tasks.append(_run_pipeline("d", run_d_one, qs, out / "responses_d.jsonl", raw, sem_d, client))
        if args.only == "e":
            from runners.run_option_e import run_one as run_e_one
            tasks.append(_run_pipeline("e", run_e_one, qs, out / "responses_e.jsonl", raw, sem_e, client))
        if args.only == "f":
            from runners.run_option_f import run_one as run_f_one
            sem_f = asyncio.Semaphore(args.concurrency)
            tasks.append(_run_pipeline("f", run_f_one, qs, out / "responses_f.jsonl", raw, sem_f, client))
        if args.only == "g":
            from runners.run_option_g import run_one as run_g_one
            sem_g = asyncio.Semaphore(args.concurrency)
            tasks.append(_run_pipeline("g", run_g_one, qs, out / "responses_g.jsonl", raw, sem_g, client))
        await asyncio.gather(*tasks)

    print(f"\nDone. Outputs in {out}.", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
