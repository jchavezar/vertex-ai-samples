"""Storm test for Pattern C: send 100 duplicate enqueue calls for the same
(bucket, object, generation) and verify Cloud Tasks dedup keeps it to 1 task.

If this passes, Pub/Sub redelivering the same OBJECT_FINALIZE 100 times can
NEVER trigger more than 1 extraction.

Run from the extractor/ folder:
    uv run python ../_archive/storm_test.py
"""
import asyncio
import os
import sys

# Make the docparse package importable from this script's location
sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "extractor", "src")),
)

# Configure env vars BEFORE importing tasks (its module-level reads them)
os.environ.setdefault("GOOGLE_CLOUD_PROJECT", os.environ.get("PROJECT", "your-gcp-project"))
os.environ.setdefault("TASKS_LOCATION", "us-central1")
os.environ.setdefault("TASKS_QUEUE", "docparse-extract")
# Replace these with your real test deployment URL + SA before running:
os.environ.setdefault(
    "WORKER_URL",
    f"https://docparse-{os.environ.get('GOOGLE_CLOUD_PROJECT')}.us-central1.run.app/work",
)
os.environ.setdefault(
    "WORKER_SA",
    f"docparse-runner@{os.environ.get('GOOGLE_CLOUD_PROJECT')}.iam.gserviceaccount.com",
)

from docparse.tasks import enqueue_extract  # noqa: E402

BUCKET = "docparse-storm-test-in"
OBJECT = "Accenture-Metaverse.pdf"
GENERATION = 1745520000000001  # any fixed value; same value = dedup target


async def burst(n: int) -> None:
    print(f"Sending {n} duplicate enqueue calls for gs://{BUCKET}/{OBJECT} gen={GENERATION}")
    print()

    results = await asyncio.gather(
        *[enqueue_extract(BUCKET, OBJECT, GENERATION) for _ in range(n)],
        return_exceptions=True,
    )

    created = sum(1 for r in results if isinstance(r, dict) and r.get("created"))
    suppressed = sum(1 for r in results if isinstance(r, dict) and not r.get("created"))
    errors = [r for r in results if isinstance(r, Exception)]

    print(f"  created (new task)         : {created}")
    print(f"  suppressed (ALREADY_EXISTS): {suppressed}")
    print(f"  errors                     : {len(errors)}")
    if errors:
        print(f"  first error: {type(errors[0]).__name__}: {str(errors[0])[:200]}")
    print()
    print("PASS ✓" if created == 1 and suppressed == n - 1 and not errors else "FAIL ✗")
    print()
    if results:
        first_ok = next((r for r in results if isinstance(r, dict)), None)
        if first_ok:
            print(f"task name: {first_ok['task_name']}")


asyncio.run(burst(100))
