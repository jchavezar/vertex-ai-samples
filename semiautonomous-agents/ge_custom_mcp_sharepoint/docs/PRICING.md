## Pricing — cost per 1K SharePoint queries

> All numbers are forecasts pending the eval run. Update this doc once the runners produce real latency + token-count distributions.

### Option 1 — Custom MCP on Cloud Run

Per-query cost components:

| Component | Source | Estimate / 1K queries |
|---|---|---|
| Cloud Run CPU + memory | 2 vCPU, 1 GiB, avg ~3 s wall per call | $ TBD |
| Cloud Run requests | $0.40 / million | ~$0.0004 |
| Egress to Graph | Cloud → Microsoft, small | negligible (<$0.01) |
| Gemini Flash vision callback (per image in `read_file`) | gemini-2.5-flash per-image rate | $ TBD (sensitive to image-heavy corpora) |
| MarkItDown OCR (per scanned-PDF page) | local tesseract → CPU only | rolled up in Cloud Run CPU |
| GE chat LLM | GE bundled per app — not per-query | $0 marginal |
| **Total (estimate)** | | **TBD per 1K queries** |

Assumptions:
- Cold-start ratio assumed low (min-instances=1 in production).
- No GPU.
- 1 KB request, 8 KB response avg.

Optimizations available:
- Set `min-instances=1` to amortize startup; if cold-start budget is tight, use Cloud Run gen2 + always-on CPU.
- Cache `list_sites` / `list_libraries` per user for 5 min (Microsoft Graph rarely changes those mid-session).
- Skip the vision callback for image-light corpora — wire a `VISION_DISABLED=1` env var.

### Option 2 — Hosted Work IQ SharePoint MCP

Microsoft Agent 365 is licensed per user; the SharePoint MCP is bundled. There is **no per-call charge on the Google side** beyond the GE chat LLM (already paid for as part of the GE app).

| Component | Cost / 1K queries |
|---|---|
| Microsoft Agent 365 license | flat per-user / month (not per query) |
| GE chat LLM | $0 marginal (bundled) |
| Cloud Run | not used |
| **Total (variable)** | **~$0 per 1K queries** |

Caveat: the **5 MB read ceiling** means questions that need a large file simply fail — which moves cost into "questions you can't answer" rather than "questions that cost money." The eval will quantify how often that happens.

### Side-by-side (TBD numbers)

| Metric | Option 1 (Custom MCP) | Option 2 (Hosted IQ) |
|---|---:|---:|
| Cloud Run cost / 1K queries | $ TBD | $0 |
| Marginal Google cost / 1K queries | $ TBD | $0 |
| Microsoft license / user / month | $0 (uses standard SP delegated perms) | $ Agent 365 list price |
| Cost of "questions you can't answer" (5 MB cap) | $0 | high — depends on corpus |
| Latency p50 (estimate) | ~3 s | TBD |
| Latency p90 (estimate) | ~10 s (read_file + vision) | TBD |

> Replace TBD rows after the first full eval pass.
