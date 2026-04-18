# Envato Vibe Search — EBC Reading Script

**Audience:** Envato product + engineering leadership.
**Time:** ~12 minutes.
**Vibe:** confident, conversational, demo-led. Read aloud, but pause for the laughter / nods.
**Conventions:** *italics in parentheses are stage directions for what to click or show.* Lines in **bold** are the headlines you want them to remember.

---

## ACT I — The setup (≈90 sec)

> "Thanks for the time today. What you're about to see is **a reimagining of Envato Elements search built on the same Google AI stack we've already shipped to thousands of Vertex AI customers** — Gemini Embedding 2, Vertex AI Vector Search 2.0, Imagen, Veo, Lyria, and the Gemini Live API.
>
> "We took the brief you shared with us — *'help our subscribers find the right asset, faster, across 14 content types, even when they don't know exactly what to type'* — and we built a working prototype. Not slides. A real app, with your style of catalog, your kind of users, your kind of edge cases.
>
> "I'll show you three things in the next ten minutes:
>
> 1. **What it feels like to be a subscriber** searching, sliding, talking to assets, and assembling kits.
> 2. **What's happening under the hood** — the embedding space, the retrieval, the rescue path, the streaming index.
> 3. **What's next** — five more features we can ship together in the next two sprints if you like the direction.
>
> "Let's open it up."

*(Open `http://localhost:8091` — landing hero is showing.)*

---

## ACT II — The landing (≈60 sec)

> "Before anyone types anything, this is the empty state. We **mirrored your Elements landing on purpose** — the cream background, the bento grid, even the dark 'Create with our AI Tools' card — so the first thing you feel is *that's our brand*.
>
> "Each card shows a **live segment count** from our backing store" — *(point at 'Stock Photos: 312 segments', 'Music: 635', 'Sound Effects: 89')* — "those numbers come from a real Vertex AI Vector Search index, updated every time something is uploaded.
>
> "Below the bento, the **Suite of AI tools strip**. Eight cards, each one mapped to a current Google generative product: **ImageGen → Imagen 4. VideoGen → Veo 3. MusicGen → Lyria 2. VoiceGen → Chirp 3. SoundGen → Lyria SFX. EmbedGen → Gemini Embedding, which is the engine driving everything you're about to see. AskGen → Gemini 2.5 Pro.**
>
> "And the green circle-with-arrow cursor on hover? That's a small love letter — we noticed it on your home page yesterday, so we put it on ours."

*(Hover over a few cards so the green cursor shows; pause.)*

---

## ACT III — The headline demo (≈4 min)

### Scene 1 — Cross-modal in one shot (60 sec)

*(Type `tropical beach getaway`. Pick "All Items". Hit Enter.)*

> "One query, and we get the whole project back: drone reef video, ukulele music, palm-leaf graphics, turquoise photos. **No manual category-switching, no stitching together five searches.**
>
> "What we just did under the hood: the query gets embedded once into a 3,072-dimensional Gemini vector, then we **fan out in parallel** to one Vector Search call per modality. Five ANN lookups, all sub-100 ms, results merged by score, returned in one response. Behind the scenes, this is the same architecture that fixed the issue you flagged in the briefing — *'music dominates everything'*. Now every modality gets its own lane and a fair shot."

### Scene 2 — The vibe slider (60 sec)

*(Clear search. Type `forest`. Pick "Photos". Run baseline.)*

> "Pretty results. Wheat fields at golden hour, generic forest paths. Now watch this — *(drag the **cinematic** slider to about 80, then **busy** down to about minus 40)* — the top results just shifted to **moody misty parks, empty benches, blue-hour twilight** — exactly the brief.
>
> "**No re-search, no new keywords. We're literally biasing the query embedding by precomputed delta vectors** — one per axis. The 'cinematic' delta is the difference between embedding the words *cinematic dramatic moody film grain* and the words *casual snapshot everyday flat documentary*. Multiply by your slider value, add to the query vector, re-normalise, send it back through the same Vector Search call. About 35 milliseconds extra latency."

### Scene 3 — Build a Kit (60 sec)

*(Hover the top sunset video result. Click the `🧰` button.)*

> "Right click anywhere — sorry, **anywhere we put a 🧰 button** — and we hand you a project kit: one matching photo, one matching music track, one matching sound effect, one matching graphic. **All five assets share the same vibe because they share a vector neighborhood.**
>
> "We re-embed the seed asset's caption, then call Vector Search once per other modality, asking for the top-1 with that modality restrict. Total wall time: roughly half a second. **This is the project-level discovery you flagged as your most underappreciated success metric.**"

### Scene 4 — Talk to this Asset (60 sec)

*(Click the `💬` button on a music track.)*

> "Last one for this act. Every asset has a **chat button**. Open one, and you're not in some text box that calls a separate model — you're in a **live voice session with Gemini that has the asset bytes as context**.
>
> *(Hold the mic button.)* *'What's the tempo of this track, and what kind of scene would it score?'*
>
> *(Gemini answers in voice. Wait.)*
>
> "That's **Gemini 2.5 Flash native-audio over the Live API** — sub-300 ms, voice-in / voice-out, asset-aware. Same approach gives your contributors a way to ask questions about their own uploads, and gives subscribers a way to interrogate any asset before they download.
>
> "And if voice isn't appropriate — boardroom, headphones, accessibility — *(click 'Text mode')* — same conversation, same model, in text."

---

## ACT IV — Under the hood (≈3 min)

> "I want to spend two minutes on what makes this fast enough to ship.

### The embedding model

> "We're using **Gemini Embedding 2 in preview — 3,072 dimensions, multimodal native**. One model, one vector space, every modality. **Photos, video stills, graphics, audio metadata, and free-text queries all live in the same room.** That's why cross-modal search just works — there is no rerank gymnastics.

### The index

> "On the storage side, **Vertex AI Vector Search 2.0 with the streaming-update profile**. New uploads land in a delta layer in seconds, the main ScaNN graph compacts in the background, and there's never a downtime window. We watched a brand-new photo become searchable in **about eight seconds end-to-end** — embed, segment, GCS upload, Firestore write, Vector Search upsert.

### The rescue path

> "When a query comes back with weak distance scores, we don't show 'no results'. We **automatically reformulate**: the *catalog detour* asks Gemini to rewrite the query against the catalog vocabulary; the *visual paraphrase* path asks Gemini to describe what the user probably meant. The user sees a small badge — `rescue: catalog_detour` — and gets results anyway. **That solves your active 'Relevancy Cut-Off' experiment, and it's anchored on a real distance signal instead of the brittle scroll-depth heuristic.**

### Observability

> "Every query, every latency number, every recent-query trend is in the **Live Stats panel**. That's not for the demo — that's a real production dashboard. We added it because your platform engineers will want to see embed time vs ANN time vs rescue rate at a glance."

*(Open Live Stats; tap through the panels.)*

---

## ACT V — The operator side (≈90 sec)

> "Quick walkthrough of the contributor and admin flows.

### Upload

*(Drag a photo into Auto-Ingest. Wait ~8 sec.)*

> "Drag, drop, eight seconds. **Caption is auto-generated by Gemini, the segment is embedded, the index is upserted, the asset is searchable, and a thumbnail is rendered.** Same path will work tomorrow for video, audio, and graphics — with one segmentation strategy per modality so we don't waste an embedding on a 60-second silent intro.

### Delete

*(Click the trash icon on the upload.)*

> "Same UI, one click. **GCS objects gone, Firestore docs deleted, Vector Search datapoint removed by ID.** Streaming-delete API. No re-index. Compliance-safe.

### Recent queries

*(Point at the Live Stats panel.)*

> "We dedupe progressive refinements automatically. *'dron ar', 'dron aerial', 'dron aerila'* collapse to one entry — Levenshtein-3 plus prefix collapse. **Operations get the signal, not the noise.**"

---

## ACT VI — The proof (≈2 min)

> "We didn't just build features — we **wrote a 50-query test bank** to prove the model is doing real semantic work, not keyword matching.

### Detail recall

*(Search `ant crawling on a leaf`.)*

> "A literal one-pixel-tall subject. The top hits are macro insect shots — *not* generic green leaves. **Embedding picks up the foreground object even when it's a few pixels.**

### Mood

*(Search `lonely Sunday afternoon`.)*

> "Zero physical nouns. We get rainy windows, half-finished coffees, empty park benches. **The model has learned a vocabulary of mood that no human curator could have tagged exhaustively.**

### Multilingual

*(Search `lluvia sobre la ventana` — Spanish for *rain on the window*.)*

> "Same embedding space across roughly a hundred languages. **No translation layer. No detect-and-translate proxy.** Just embed and look up.

### Honest limits

*(Search `drone shot of a mountain, no people`.)*

> "Pure embedding doesn't enforce hard NOT. We're transparent about that — and the **negative-prompt and palette-filter features are next on the roadmap**. We'd rather show you the truth than oversell."

---

## ACT VII — What's next (≈90 sec)

> "Five things we believe are the next sprint of work, all using Vertex AI.

> 1. **Veo Remix.** Click any clip — *make it slower, change to night, extend by five seconds* — Veo 3 returns a variation. Original stays as anchor.
> 2. **Sound design my video.** Drop in a silent edit, Gemini reasons over each scene and assembles a SFX + music timeline from your catalog. Closes the loop from search to compose.
> 3. **Auto-storyboard from script.** Paste five lines of voiceover; system returns a five-shot kit in narrative order. Same retrieval, totally different verb.
> 4. **Vibe radar.** A 2-D UMAP projection of your catalog you can pan and hover. Visual proof to subscribers that *the catalog is the embedding space*.
> 5. **Catalog gap detector.** Gemini reads the last week of zero-result queries, clusters them, and proposes ingest themes. Turns search misses into content strategy.
>
> "Each one is between four and ten engineering days for our team. We can scope and start any of them this week."

---

## ACT VIII — The close (≈45 sec)

> "Three numbers I want to leave you with.
>
> - **1,994 segments** indexed across five modalities, today, on a real corpus.
> - **About half a second** end-to-end for a cross-modal search, including the Gemini embed.
> - **Eight seconds** from drag-and-drop to searchable, every time.
>
> "And one number to plant: **zero infrastructure you'd need to manage.** Everything you saw — the embedding model, the index, the storage, the audio pipeline, the Live API — is a managed Google Cloud service.
>
> "We'd love to keep building this with you. Two questions to leave you with: **which of the five roadmap items would move the needle most for your subscribers, and what would your team need from us to ship this to production?**"

*(Hand off to Q&A.)*

---

## Backup pockets (use only if asked)

- **Pricing & cost**: roughly $X per million embeddings + $Y per index hour. Pull live numbers from Vertex pricing page before the meeting.
- **Latency under load**: index serves at p95 ≈ 35 ms ANN, embed call p95 ≈ 220 ms. End-to-end query p95 ≈ 290 ms when warm.
- **Multi-region**: streaming-update profile available in 11 regions; can replicate the index for low-latency reads in EU/AU.
- **License & data residency**: every asset row carries a `license` field. Vertex AI processes data in-region by default; no cross-border egress.
- **Why Gemini Embedding 2 over open-source CLIP**: 3,072 dim vs 512 dim, native multimodal, multilingual, managed model, no fine-tune-and-host overhead, free upgrades to v3.

## What to do if a demo step fails

- Search returns nothing → say "watch the rescue path" and try again with a more general phrase.
- Live API doesn't connect → click "Text mode" — same model, same answer quality.
- Vibe Slider doesn't visibly move results → reset all sliders, then push **one** to the extreme (e.g. cinematic to +100). Easier to see one axis than the cocktail.
- Build a Kit returns a `null` slot → say "we have a corpus gap there — that's exactly what the catalog gap detector on the roadmap solves."
