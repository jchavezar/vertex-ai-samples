# Demo Use Cases (15, ranked)

For each use case: what it does, which model + task type, and the WOW moment.

### 1. Vibe Search — Natural-language semantic search
Type *"a feeling of nostalgia in a coffee shop"*, get a ranked grid mixing photos,
video stills, and 3D scenes — none of which contain "nostalgia" in their tags.
Model: `gemini-embedding-2-preview` (corpus) + `gemini-embedding-001`
`RETRIEVAL_QUERY` (or aligned multimodal query) for the search side.
**WOW:** Side-by-side with shutterstock.com keyword search.

### 2. Mood-Board Generator from a Creative Brief
Paste a multi-paragraph brief, get 4–6 themed boards (Hero, Lifestyle,
Texture/Background, Talent close-ups).
Model: `gemini-embedding-001` `CLUSTERING` task on retrieved assets.
**WOW:** Replaces a half-day agency exercise.

### 3. Cross-Modal "Match My Brand" Upload
Drop a logo / brand guide / hero photo → similar stock content across photos,
video, 3D *and* music.
Model: multimodal embeddings on both query and corpus.
**WOW:** Photo in → music track out.

### 4. Multilingual Brief → Assets
Brief in Spanish, German, Japanese, Arabic — same quality results, no
translation pipeline.
Model: `gemini-embedding-001` (100+ languages).
**WOW:** Solves a known revenue blocker for international enterprise.

### 5. Editorial Moment Finder — Article → Image
Paste a news article URL or text; get the best matching editorial photos and
video clips, ranked by semantic + recency.
Model: `gemini-embedding-001` for the article, multimodal for assets.
**WOW:** Run with a live breaking-news article during the meeting.

### 6. Music ↔ Video Matching
Pick a video clip, get Pond5 / PremiumBeat tracks whose embeddings are
closest. Or pick a track, get matching B-roll.
Model: `gemini-embedding-2-preview` audio + video in one space.
**WOW:** First-of-its-kind cross-asset bundling.

### 7. Style-Consistency Check for Campaigns
Drop the 12 assets in a campaign, tool flags the outlier and suggests on-style
replacements.
Model: multimodal embeddings + `SEMANTIC_SIMILARITY` framing.
**WOW:** Useful to every brand designer in the room.

### 8. Brand-Safe Content Filter (per-customer policy)
Each customer defines forbidden concepts in plain text — implemented as
classification embeddings, no retraining.
Model: `gemini-embedding-001` `CLASSIFICATION` with concept anchors.
**WOW:** Zero-shot policy customization. Sales can repeat for any vertical.

### 9. Auto-Categorization & Auto-Tagging at Upload
New contributor uploads → auto-embed → assign to existing cluster centroids →
suggested keywords + category.
Model: `gemini-embedding-2-preview` + `CLUSTERING`.
**WOW:** Direct revenue + cost story for contributor ops team.

### 10. Near-Duplicate / Redundancy Detection
Catalog cleanup. Flag near-dup video stills, near-dup photos, lower-resolution
copies.
Model: multimodal embeddings, cosine ≥ 0.95 on 3072-dim.
**WOW:** Storage + curation savings, CFO-friendly.

### 11. Personalized "For You" Feed
Embed user's last 50 downloads → mean vector → nearest neighbors with
diversity penalty.
Model: any task type; `SEMANTIC_SIMILARITY` works well.
**WOW:** Drives repeat-purchase and subscription stickiness.

### 12. Creative-Brief Decomposition (Agentic)
Brief → LLM expands into 8–12 sub-queries → each embedded → diverse asset
pack.
Model: Gemini for decomposition + `gemini-embedding-2-preview` for retrieval.
**WOW:** One click yields a *full* deliverable.

### 13. "Complete the Look" Cart Bundles
At checkout, suggest the 5 missing pieces (matching music if user only has
video; matching 3D mockup if user has flat photos).
Model: multimodal embeddings + cross-category nearest neighbors.
**WOW:** Revenue lift mechanic — Shutterstock loves AOV stories.

### 14. Embedding Playground — Matryoshka Trade-off Live Demo
Slider for dimension 128 → 3072; show latency, recall@10, and cost change in
real time.
Model: `gemini-embedding-2-preview` (or 001), all four recommended dims.
**WOW:** Engineers and execs both get it. Justifies cost story at billion-asset scale.

### 15. Contributor-Trend Insights Dashboard
Cluster all uploads from the last 30 days; surface emerging themes.
Model: `gemini-embedding-2-preview` + `CLUSTERING` + Gemini for cluster naming.
**WOW:** A net-new product surface.

## Suggested meeting walkthrough

1. **#1 Vibe Search** — wow in 30 seconds vs shutterstock.com keyword search
2. **#4 Multilingual** — international growth angle
3. **#3 Cross-Modal Match-My-Brand** — multimodality
4. **#6 Music ↔ Video** — cross-catalog (Pond5 + PremiumBeat) value
5. **#12 Creative-Brief Decomposition** — agentic, strategic upside
6. **#14 Matryoshka Playground** — engineering cost story for 600 M+ assets
