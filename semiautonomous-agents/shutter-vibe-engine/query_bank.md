# Envato Vibe Engine — Curated Query Bank

Hand-picked queries, grouped by what they showcase. Expected hits are inferred from `envato/assets/manifest.json` (300 source assets across 13 photo / 13 video / 8 audio / 2 graphic sub-categories) and confirmed against a sample of segment captions in Firestore (`gemini-embedding-2-preview`, 3072-dim, COSINE).

> **How to use this:** Pick 1–2 from each category to drive Acts 1–3 in `demo_script.md`. The "edge cases that DON'T work" section is for the AE's pre-brief, not the live audience — but ship the truth into the Q&A if asked.

---

## 1. Mood-based audio (showcases cross-asset audio similarity)

| # | Query | Expected top hits (top 3–5) | Why it's a good demo query |
|---|---|---|---|
| 1.1 | `calm cinematic underscore` | `ambient cinematic underscore` segments (multiple), `acoustic folk guitar` segments | Cleanest audio query in the set — exact thematic match in corpus, returns multiple segments of the SAME track at different timestamps, demonstrating per-segment retrieval |
| 1.2 | `upbeat lofi beat for studying` | `lofi hip hop beat` segments, low-tempo `jazz piano improvisation` | Shows mood + use-case combo. Returns segments at chill-beat tempos (~70–85 BPM). |
| 1.3 | `dark synthwave at night` | `electronic synthwave` segments, `experimental electronic sketch` | Genre-specific. Audio embeddings cluster well on synth timbres. |
| 1.4 | `uplifting corporate background music` | `uplifting corporate background` segments (overrepresented in corpus — many high-quality hits) | Safest possible audio query; corpus has ~100+ uplifting corporate segments. Use this if anything else flakes. |
| 1.5 | `acoustic guitar fingerpicking, intimate` | `acoustic folk guitar` segments | Tests instrument + technique specificity. Matches asset-theme well. |
| 1.6 | `world percussion drum circle` | `world percussion ensemble` segments | Genre-specific, well-represented. |

---

## 2. Visual scenes (text → photo + video, often returns a mix)

| # | Query | Expected top hits | Why it's a good demo query |
|---|---|---|---|
| 2.1 | `drone shot of ocean at golden hour` | `tropical beach drone aerial` photos, `ocean waves slow motion` video segments, `sunset clouds time lapse` video | Compound query (subject + camera + lighting). Hits both photos AND video segments — great for showing modality fan-out from one query. |
| 2.2 | `minimalist scandinavian interior` | `minimalist scandinavian interior` photos, `abstract macro texture` (light wood) | Exact thematic match. Use if you need a clean grid of photos for visual impact. |
| 2.3 | `cozy coffee shop morning` | `cozy coffee shop morning` photos, `coffee pour macro` video segments, `acoustic folk guitar` audio | The headline cross-modal query — pulls all 4 modalities cleanly. **Use as the Act 1 opener.** |
| 2.4 | `northern lights aurora borealis dancing` | `northern lights aurora` video segments, `cinematic mountain sunrise` photos | Long-tail subject; tests recall on niche scenes. |
| 2.5 | `neon cyberpunk street at night` | `neon cyberpunk street` photos, `neon sign night` video segments, `electronic synthwave` audio | Cross-modal vibe — synthwave music returns alongside the visuals because both occupy the same "neon, night, urban, electronic" region of the embedding space. |
| 2.6 | `time lapse of city traffic at dusk` | `city traffic time lapse` video segments, `neon sign night` segments | Tests motion descriptors landing in the embedding. |

---

## 3. Cross-modal "vibe" (text returns mixed media — the hero use-case)

These are the queries where the demo *sells itself* — one short phrase pulls coherent multi-modal results.

| # | Query | Expected top hits | What capability it shows |
|---|---|---|---|
| 3.1 | `morning routine` | Coffee photos, coffee-pour videos, acoustic folk audio, podcast studio photos | Open-ended user intent; system returns a complete mood-board. The cross-modal grouping in the UI shines here. |
| 3.2 | `victory moment` | `athlete training golden hour` photos, `uplifting corporate background` audio (high-energy segments at ~128 BPM), `sunset clouds time lapse` | Abstract concept → concrete media. Tests semantic depth. |
| 3.3 | `sad rainy day` | Low-key photos, slow ambient music, `snow falling slow motion` video | "Sad" isn't a tag in the corpus. Pure embedding inference of mood. |
| 3.4 | `meditation and focus` | Ambient cinematic underscore, `japanese tea ceremony` photos, `candle flame close up` video | Vibe alignment across all 4 modalities. |
| 3.5 | `startup pitch energy` | `diverse startup team meeting` photos, `uplifting corporate background` audio, `podcast recording studio` photos | Demonstrates the "find me everything for this campaign" use case. |

---

## 4. Edge cases that work surprisingly well

| # | Query | Expected behavior | Why surprising |
|---|---|---|---|
| 4.1 | `the sound of footsteps on gravel` | Falls back to nearest SFX segments + ambient cinematic / world percussion | We have only 8 SFX datapoints in the corpus, so coverage is thin — but the query embedding lands closer to "footsteps-y" sounds than to music tracks even without an exact match. Good talk-track for "this would be amazing with your full SFX library." |
| 4.2 | `the feeling just before a wave breaks` | `ocean waves slow motion` video segments, ambient underscore | Poetic, non-literal phrasing — system handles it. Demonstrates that the embedding generalizes from concrete training data to abstract user phrasings. |
| 4.3 | `that vintage Wes-Anderson symmetry` | `vintage film grain portrait` photos, `minimalist scandinavian interior` | Stylistic / aesthetic-reference query without naming a literal subject. The model picked up on "symmetry" + "vintage palette" cues from the captions. |

---

## 5. Edge cases that DON'T work yet (be honest in Q&A)

| # | Query | Why it fails | What to say |
|---|---|---|---|
| 5.1 | `Taylor Swift Eras Tour vibe` | No celebrity/brand training in this corpus; model degrades to generic "concert" vibes (which we don't have either). | "Specific celebrity / brand-IP queries are out of scope for a stock catalog by definition. For an Envato production system you'd handle this in a query-rewrite layer that maps brand references to canonical scene descriptors." |
| 5.2 | `Premiere Pro project file template` | Catalog has zero project-file metadata. | "We didn't index project-file metadata in this slice — Vertex Vector Search supports that namespace cleanly, it was a corpus-scope decision." |
| 5.3 | `the song from that 2010 commercial` | No temporal / contextual provenance in the embeddings. | "Embeddings are spatial, not temporal — 'song from 2010' isn't a feature of the audio itself. This is where you'd combine semantic search with structured metadata filters: text → embed for vibe, then filter by `year=2010` from Firestore. We have the namespace, we just don't have the year metadata populated in this corpus." |
| 5.4 (bonus) | A 30-language non-English query | Mixed — `gemini-embedding-2` is multilingual at the query side, but our captions are English-only, so cross-lingual retrieval works for visual content (image embeddings are language-free) but degrades for audio (where the caption text dominates). | "Worth a longer conversation — multilingual indexing is supported, we just need the captioner pass to run in the right language." |

---

## Filters worth showing live

The web UI exposes filters that map to Vector Search namespace restricts and one post-filter. Useful to demo alongside the queries above:

| Filter | UI control | Backend mechanism |
|---|---|---|
| Modality (photo/video/audio/graphic) | Tabs / chips | VS namespace `modality` (special: `audio` allows both `audio` + `sfx`) |
| Tempo (slow/mid/upbeat/fast) | Slider on audio results | VS namespace `tempo_bucket` (music only — populated from `tempo_bpm` in the caption JSON) |
| Length (short <5s / mid <15s / long <60s / epic) | Chips on video/audio | VS namespace `length_bucket` |
| Color | Hex swatch picker | Post-filter on `caption.dominant_colors`, RGB Euclidean ≤140 |

**Suggested combo to demo:** Query `cinematic mountain sunrise`, then click the color swatch for `#d4a574` (warm gold). Watch the result set re-rank to favor warm-toned segments. Narration: "This is happening server-side against the structured caption JSON — no re-embedding, no second VS round-trip."
