# Production-readiness verification

Two tests confirm the v6 extractor is safe to ship to production:

1. **Storm test** — duplicate events can't multiply cost
2. **End-to-end test** — real PDFs flow through the full pipeline and produce eval-quality markdown

Both passed on 2026-04-29.

---

## 1. Storm test (duplicate events → 1 extraction)

### What we're preventing

Pre-v6 docparse was vulnerable to a Pub/Sub redelivery loop. When the worker exceeded its ACK deadline (e.g. on a slow extraction), Pub/Sub would redeliver the same `OBJECT_FINALIZE` event to a fresh worker. That worker would also exceed the deadline, triggering another redelivery. A single PDF upload could amplify into 5-10 extractions; over 36 hours of dev iteration this produced ~1,500 redundant extractions of just 2 PDFs (the Apr 25 incident — **~$3,000** in Vertex AI Gemini calls).

### How v6 prevents it

```
GCS upload → Eventarc → Cloud Run /dispatch
                              │
                              ▼
                  hash = sha256(bucket : object : generation)
                              │
                              ▼
                  CreateTask(name = "extract-<hash>")
                              │
                              ▼
                  Cloud Tasks queue
                              │                  ▲
                              ▼                  │
                  /work endpoint                 duplicate dispatches
                  (extract + write GCS)          hit ALREADY_EXISTS, no-op
```

GCS `generation` is a monotonic per-object counter that bumps on every overwrite. Pub/Sub redelivering the SAME event always carries the same generation → same task name → Cloud Tasks `CreateTask` returns `ALREADY_EXISTS`, and the worker is never invoked twice for the same input.

### Test methodology

```python
# 100 simultaneous duplicate enqueue calls for the same (bucket, object, generation)
results = await asyncio.gather(
    *[enqueue_extract(BUCKET, OBJECT, GENERATION) for _ in range(100)]
)
```

### Result

```
Sending 100 duplicate enqueue calls for gs://...Accenture-Metaverse...pdf gen=1745520000000001

  created (new task)         : 1
  suppressed (ALREADY_EXISTS): 99
  errors                     : 0

PASS ✓
```

100 dispatches → **1 task created, 99 ALREADY_EXISTS no-ops**, zero errors.

---

## 2. End-to-end test (real PDFs through the full pipeline)

### What ran

Both PDFs uploaded to a fresh test bucket. Eventarc → Cloud Tasks → /work → Vertex AI extraction → GCS output bucket. Then the per-page chunks were imported into a fresh RAG corpus and the full 216-question eval ran against it.

### Results

| Step | Outcome |
|---|---|
| Eventarc fired on upload | ✓ |
| Cloud Tasks dedup'd duplicate triggers | ✓ — duplicate Eventarc retries during init were absorbed |
| Both PDFs extracted | Accenture in 3.5 min, SE in 6.7 min |
| Markdown content quality | ✓ — Carrefour quote, Mater/Siemens, MBBs all captured |
| RAG corpus indexed | ✓ — 72 chunks, 0 failures |
| 216-question eval composite | **91.7%** — within v5's noise band (mean 92.2 ± 0.81) |
| No storm | ✓ — request-count peak was 16 / 5 min (storm threshold was 20) |

### Bounded-retry config

The Cloud Tasks queue is provisioned by `deploy.sh` with explicit safety bounds:

```
--max-attempts=3                 # max 3 worker invocations per task
--max-retry-duration=1800s       # absolute time-cap on retry budget
--min-backoff=10s
--max-backoff=600s               # exponential backoff caps at 10min
--max-dispatches-per-second=2    # caps queue throughput → Vertex rate-limit headroom
--max-concurrent-dispatches=5    # caps simultaneous worker invocations
```

Even if Cloud Tasks dedup somehow missed a duplicate (it can't — that's a queue invariant), each unique input would be retried at most 3 times.

---

## Production impact

| Scenario | Without v6 | With v6 |
|---|---|---|
| 1 PDF uploaded normally | 1 extraction | 1 extraction |
| 1 PDF, Pub/Sub redelivers the event 5× | 5 extractions = ~$10 | **1** extraction = ~$2 (4 dedup'd) |
| 1 PDF, dev re-uploads byte-identical content 50× | 50 extractions = ~$100 | 50 extractions (each is a real new generation — intentional) |
| Cloud Run returns 429, Eventarc retries 3× | 3 extractions | **1** extraction (2 dedup'd) |
| Apr 25 historic storm: 2 PDFs, 1,500 redundant fires | **~$3,000** | **~$4** |

---

## Reproducing both tests

```bash
# 1. Provision the queue + service
cd extractor
PROJECT=your-gcp-project ./deploy.sh

# 2. Storm test (proves dedup works at scale) — script lives at _archive/storm_test.py
uv run python ../_archive/storm_test.py
#   expect: created=1, suppressed=99, errors=0

# 3. End-to-end test (real extraction)
gcloud storage cp ~/sample.pdf gs://${PROJECT}-docparse-in/
gcloud storage ls gs://${PROJECT}-docparse-out/   # wait ~5min, expect sample.txt
```

If the storm test fails, do NOT deploy to a production bucket — investigate IAM and queue config first.
