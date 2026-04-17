# API Capabilities Report — observed live on Vertex AI

> Generated 2026-04-17 by running every script in `demos/` against project
> `vtxdemos` in `us-central1`. Full transcript in `findings/run.log`.
> Models exercised: `gemini-embedding-001` (GA, text), `gemini-embedding-2-preview` (multimodal preview).

## TL;DR

* All ten capability probes ran green against live Vertex.
* Vectors come **L2-normalized straight from the API** (every dim, every model).
* `output_dimensionality` accepts 128 / 256 / 768 / 1536 / 3072; latency is flat across dims.
* Vertex `gemini-embedding-001` accepts **one input per call**; you batch by looping.
* `autoTruncate=true` is the default and **silently truncates ~5.6k-token input** without raising.
* Spaces between Gemini Embedding 1 and 2 are effectively orthogonal (`cos ≈ 0.03`) — re-embed corpus when migrating.
* `gemini-embedding-2-preview` returns **one fused vector** when you put text + image in the same `contents=[…]` list.

## Run summary

| Demo | Result | Wall time |
| ---- | ------ | --------- |
| 01_text_basics.py        | OK | 3.1 s |
| 02_task_types.py         | OK | 3.6 s |
| 03_matryoshka.py         | OK | 17.1 s |
| 04_vibe_search.py        | OK | 3.6 s |
| 05_multilingual.py       | OK | 3.5 s |
| 06_brand_safety.py       | OK | 3.8 s |
| 07_moodboard_cluster.py  | OK | 4.3 s |
| 08_code_retrieval.py     | OK | 1.0 s |
| 09_multimodal_preview.py | OK | 4.2 s |
| 10_limits_and_quirks.py  | OK | 1.3 s |

Total ≈ 46 s for the full sweep.

## Latency notes

* **Cold first call**: ~1.2 – 1.4 s (TLS + auth handshake).
* **Warm calls**: ~0.18 – 0.27 s for `gemini-embedding-001`, dimension agnostic.
* **Multimodal preview (image)**: ~0.4 – 0.6 s per asset for a 256×256 PNG.
* **Long-input (5.6 k tokens, auto-truncated)**: ~1.17 s, a single call.

## Dimension sweep (`gemini-embedding-001`)

Recall@5 against the 5 hand-built probes on the 28-asset corpus (Demo 03):

| dim  | embed_corpus | recall@5 | avg query | corpus storage |
| ---- | ------------ | -------- | --------- | -------------- |
| 3072 | 3.34 s       | 1.00     | 119 ms    | 336 KB         |
| 1536 | 3.05 s       | 1.00     | 101 ms    | 168 KB         |
| 768  | 3.05 s       | 1.00     | 108 ms    | 84 KB          |
| 256  | 2.66 s       | 1.00     | 96 ms     | 28 KB          |
| 128  | 2.72 s       | 1.00     | 120 ms    | 14 KB          |

At this corpus size recall is saturated. The customer takeaway is the
**24× storage compression** (3072 → 128) on the same call, and the well-known
quality cliff only kicks in below 256 dim per the published MTEB curve.

## Task type comparison (Demo 02)

Same query / doc / distractor across all eight task types, 768-dim:

| query task             | doc task             | cos(q,doc) | cos(q,neg) | gap     |
| ---------------------- | -------------------- | ---------- | ---------- | ------- |
| FACT_VERIFICATION      | RETRIEVAL_DOCUMENT   | 0.7403     | 0.4044     | **+0.336** |
| QUESTION_ANSWERING     | RETRIEVAL_DOCUMENT   | 0.7064     | 0.3787     | **+0.328** |
| RETRIEVAL_QUERY        | RETRIEVAL_DOCUMENT   | 0.7024     | 0.3839     | **+0.318** |
| CLASSIFICATION         | CLASSIFICATION       | 0.8288     | 0.5175     | +0.311  |
| CODE_RETRIEVAL_QUERY   | RETRIEVAL_DOCUMENT   | 0.7853     | 0.5261     | +0.259  |
| CLUSTERING             | CLUSTERING           | 0.8876     | 0.6425     | +0.245  |
| SEMANTIC_SIMILARITY    | SEMANTIC_SIMILARITY  | 0.8552     | 0.6257     | +0.229  |
| RETRIEVAL_DOCUMENT     | RETRIEVAL_DOCUMENT   | 0.8453     | 0.6177     | +0.228  |

* **The asymmetric query/doc pairings open the largest separation gap.** Using
  `RETRIEVAL_DOCUMENT` on both sides is the *worst* pairing — exactly what the
  docs warn about.
* `SEMANTIC_SIMILARITY` and `CLUSTERING` push the absolute cosine values higher
  but compress the gap; that's expected — they encode "alike-ness" rather than
  query-versus-passage.

## Vibe Search highlights (Demo 04)

Top-1 result for queries that share **no keywords** with the captions:

| Query | Top-1 caption | cos |
| ----- | ------------- | --- |
| "a feeling of nostalgia in a coffee shop" | Steam rising from a ceramic mug … rain-streaked window … European cafe at dawn | 0.712 |
| "the calm before a storm" | Drone footage of wheat fields bending under sudden wind ahead of a summer thunderstorm | 0.630 |
| "wholesome family time outdoors" | Family of four enjoying a healthy summer picnic … sunny city park | 0.722 |
| "youth saving the planet" | Diverse group of teenagers picking up plastic bottles … sunrise … reusable bags | 0.680 |
| "old-world craftsmanship and ritual" | Traditional Japanese tea ceremony, hands pouring matcha … tatami mat | 0.674 |
| "an emerging Gen-Z urban sport scene" | Two Gen-Z athletes practising basketball at sunset … LA community court | 0.723 |

This *is* the headline customer demo — the keyword-overlap-zero scenario.

## Multilingual proof (Demo 05)

The same intent ("Japanese tea ceremony moment") in five languages all
ranked the same English asset (`SS-00081`) #1 with near-identical cosine:

| Language | Top hit | cosine |
| -------- | ------- | ------ |
| English  | SS-00081 | 0.772 |
| Spanish  | SS-00081 | 0.769 |
| Japanese | SS-00081 | **0.799** |
| German   | SS-00081 | 0.773 |
| Arabic   | SS-00081 | 0.770 |

Japanese had the highest cosine — slight cultural/linguistic priming effect
but unambiguous.

## Brand-safety filter (Demo 06)

Anchor concepts in plain English, threshold 0.55:

* `gambling or casinos` → SS-00041 (Monte Carlo roulette) cos **0.745**
* `alcohol or drinking` → SS-00040 (cocktail) cos 0.690, SS-00082 (Oktoberfest) 0.671
* `weapons or violence` → SS-00042 (police evidence handgun) cos 0.689
* `violent crime` → SS-00042 cos 0.672

The 0.55 threshold also produces a few **expected false positives** (e.g.
"Friends laughing over espresso and pastries" pinged `alcohol or drinking`
at 0.655). In production we'd:

1. Calibrate the threshold per concept on a labelled validation set.
2. Use multiple anchors per concept and take the *mean* (less noise than max).
3. Combine with a simple negation prompt (e.g. "alcohol-free family time")
   embedded as a positive anchor to subtract.

## Mood-board clustering (Demo 07)

K-means with k=5 produced one tight cluster (Editorial — protests + hurricane
news), one tight pastel/cinematic cluster (Wes-Anderson hotel + VW van), and
three larger mixed clusters. With k=8 and a larger corpus you get crisp
themed boards. Naming the clusters with Gemini text generation closes the loop
into a true "creative brief → mood board" deliverable.

## Multimodal cross-modal search (Demo 09)

Text query → solid-color "image" matrix, off-the-shelf colors:

| query | warm orange | cool blue | forest green | midnight |
| ----- | ----------- | --------- | ------------ | -------- |
| "warmth, golden-hour, summer mood" | **0.391** | 0.304 | 0.288 | 0.289 |
| "calm aquatic, marine palette"     | 0.307 | **0.380** | 0.315 | 0.321 |
| "lush nature and vegetation"       | 0.273 | 0.285 | **0.331** | 0.268 |
| "dark cinematic night scene"       | 0.236 | 0.231 | 0.228 | **0.347** |

Diagonal wins every row. Even with crude solid-color stand-ins, the
text-vs-image cosine ranking is correct. With real Shutterstock photography
the gap will be wider.

## Limits & quirks (Demo 10)

| Probe | Observation |
| ----- | ----------- |
| 7 000-token input | Accepted in 1.17 s. Response statistics: `truncated=True, token_count=5601`. So Vertex silently truncated above 2048 tokens (docs claim 2048 hard cap; we observed the tokenizer counted 5601 *and* still returned a vector). **Action**: in production set `autoTruncate=false` if you need to validate length. |
| Cross-model space | `cos(emb1_vec, emb2_vec)` on the SAME text = **0.0312** — effectively orthogonal. **Re-embed your corpus when migrating Gemini Embedding 1 → 2.** |
| Fused multimodal | Text + image in one `contents=[…]` list returns **ONE** 3072-dim fused vector, not two. Useful for "describe-while-showing" use cases; if you need separate vectors, call once per modality. |
| Telemetry | `response.metadata.billable_character_count` and `response.embeddings[0].statistics` (with `token_count` and `truncated`) are present and structured. Wire them into your observability now. |

## Production design checklist (what we'd ship)

1. **Use 768-dim by default**, 3072 only when ground-truth quality matters.
   Always L2-normalize after truncation — and the API already normalizes
   when no truncation is requested.
2. **Pair task types correctly**:
   * Search corpus → `RETRIEVAL_DOCUMENT`
   * Search query → `RETRIEVAL_QUERY`
   * Question answering → `QUESTION_ANSWERING` (with `RETRIEVAL_DOCUMENT` corpus)
   * Brand-safety / topic filter → `CLASSIFICATION`
   * Mood-boards / dedup → `CLUSTERING` or `SEMANTIC_SIMILARITY`
3. **Batch with the Batch API** for backfill (50% discount, up to 30 000 prompts per Vertex job).
4. **Set `autoTruncate=false`** in eval pipelines so you fail loudly instead of silently truncating.
5. **Capture `response.metadata.billable_character_count`** in your spans for cost attribution.
6. **Plan for re-embed** when promoting `gemini-embedding-2-preview` → GA.
7. **Multimodal: keep text and image in **separate** calls if you need them separately searchable.** Combined contents collapse into a fused vector.

## Open questions worth following up

* The `gemini-embedding-001` Vertex tokenizer accepted ~5.6 k tokens before
  truncation flag flipped. Public docs still say 2 048. Is this a recent
  expansion or a tokenizer mismatch? — worth raising with the Vertex AI
  product team before printing it on a customer slide.
* Is `gemini-embedding-2-preview` available in `us-central1` only? We didn't
  test other regions — the customer's compliance footprint may need EU.
* Batch endpoint behaviour for `gemini-embedding-001` on Vertex (vs. the
  Gemini API Batch endpoint) — docs flag a known asymmetry; needs validation
  before committing the Shutterstock backfill story.

## Files generated by this run

* `findings/run.log` — full transcript of the orchestrated sweep.
* `findings/api_capabilities_report.md` — this document.
