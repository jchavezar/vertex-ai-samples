"""Backfill `started_at_iso` / `finished_at_iso` into pre-existing JSONL.

Past runs were written before the orchestrator captured wall-clock timestamps
per question. We have:
  - the run start time (encoded in the run dir name `v2-YYYYMMDD-HHMMSS-<letter>`)
  - the per-record `elapsed_s` (duration of the API call only)

We don't have per-question start times. The orchestrator runs questions in
parallel (concurrency 4-6), so a strictly serial reconstruction won't be
accurate for any individual row. What we do here is a "best-effort"
estimate that preserves the aggregate distribution: walk the file in
write order and assign

    started_at_iso  = run_start + cumulative_elapsed_so_far
    finished_at_iso = started_at_iso + elapsed_s

Every backfilled row is tagged `evaluated_at_estimated: true` so the UI can
mark it as approximate. Future runs go through the orchestrator wrapper
and get true wall-clock stamps with `evaluated_at_estimated: false`.

Idempotent: if a record already has both `started_at_iso` and
`finished_at_iso` set, it's left alone (so re-running this script after a
mixed run won't double-shift).

Skip rules:
  - The v2fix re-eval directory (#58 MCP fix coordinator) is being written
    natively as we run — skip it.
  - Any run dir whose name doesn't match the `v2-YYYYMMDD-HHMMSS-...`
    pattern (we can't derive a start time).

Usage:
    python -m runners.backfill_timestamps
    python -m runners.backfill_timestamps --runs-dir /path/to/runs
    python -m runners.backfill_timestamps --dry-run
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Run dirs look like: v2-YYYYMMDD-HHMMSS-<suffix>
_RUN_DIR_RE = re.compile(r"^v2-(\d{8})-(\d{6})-")
_SKIP_PREFIXES = ("v2fix-",)


def _iso(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%S.") + f"{dt.microsecond // 1000:03d}Z"


def _parse_start(dir_name: str) -> datetime | None:
    m = _RUN_DIR_RE.match(dir_name)
    if not m:
        return None
    return datetime.strptime(m.group(1) + m.group(2), "%Y%m%d%H%M%S").replace(
        tzinfo=timezone.utc
    )


def backfill_file(jsonl_path: Path, run_start: datetime, dry_run: bool = False) -> tuple[int, int]:
    """Return (records_stamped, records_skipped_already_set)."""
    if not jsonl_path.exists() or jsonl_path.stat().st_size == 0:
        return (0, 0)

    cumulative = 0.0
    stamped = 0
    skipped = 0
    out_lines: list[str] = []

    with jsonl_path.open() as f:
        for raw in f:
            raw = raw.rstrip("\n")
            if not raw.strip():
                out_lines.append(raw)
                continue
            try:
                rec = json.loads(raw)
            except Exception:
                out_lines.append(raw)
                continue

            elapsed = float(rec.get("elapsed_s") or 0.0)

            if rec.get("started_at_iso") and rec.get("finished_at_iso"):
                # Already set — preserve, just advance the cumulative cursor
                # so any later un-stamped rows estimate roughly correctly.
                skipped += 1
                cumulative += elapsed
                out_lines.append(json.dumps(rec, ensure_ascii=False))
                continue

            started = run_start + timedelta(seconds=cumulative)
            finished = started + timedelta(seconds=elapsed)
            rec["started_at_iso"] = _iso(started)
            rec["finished_at_iso"] = _iso(finished)
            rec["evaluated_at_estimated"] = True
            cumulative += elapsed
            stamped += 1
            out_lines.append(json.dumps(rec, ensure_ascii=False))

    if dry_run or stamped == 0:
        return (stamped, skipped)

    # Atomic write: tmp file in same dir, then rename.
    tmp = tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        dir=str(jsonl_path.parent),
        prefix=jsonl_path.name + ".",
        suffix=".tmp",
        delete=False,
    )
    try:
        with tmp:
            tmp.write("\n".join(out_lines) + "\n")
        os.replace(tmp.name, jsonl_path)
    except Exception:
        # Best effort cleanup
        try:
            os.unlink(tmp.name)
        except OSError:
            pass
        raise

    return (stamped, skipped)


def main() -> int:
    ap = argparse.ArgumentParser()
    here = Path(__file__).resolve().parent.parent  # .../eval
    ap.add_argument("--runs-dir", default=str(here / "runs"))
    ap.add_argument(
        "--dry-run",
        action="store_true",
        help="Walk and report counts without writing.",
    )
    args = ap.parse_args()

    runs_root = Path(args.runs_dir)
    if not runs_root.is_dir():
        print(f"No such dir: {runs_root}", file=sys.stderr)
        return 2

    total_stamped = 0
    total_skipped = 0
    runs_touched = 0
    runs_skipped: list[str] = []

    for run_dir in sorted(runs_root.iterdir()):
        if not run_dir.is_dir():
            continue
        name = run_dir.name
        if any(name.startswith(pfx) for pfx in _SKIP_PREFIXES):
            runs_skipped.append(f"{name} (active re-eval prefix)")
            continue
        start = _parse_start(name)
        if start is None:
            # Not a v2-* run we can date — silently skip
            continue

        run_stamped = 0
        run_skipped = 0
        jsonls = sorted(run_dir.glob("responses_*.jsonl"))
        for j in jsonls:
            s, sk = backfill_file(j, start, dry_run=args.dry_run)
            run_stamped += s
            run_skipped += sk

        if run_stamped or run_skipped:
            runs_touched += 1
            total_stamped += run_stamped
            total_skipped += run_skipped
            print(
                f"  {name}: stamped={run_stamped} already={run_skipped} files={len(jsonls)}"
            )

    print()
    print(f"Runs touched: {runs_touched}")
    print(f"Records stamped: {total_stamped}")
    print(f"Records already had timestamps: {total_skipped}")
    if runs_skipped:
        print("Runs skipped:")
        for s in runs_skipped:
            print(f"  - {s}")
    if args.dry_run:
        print("(dry-run — no files written)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
