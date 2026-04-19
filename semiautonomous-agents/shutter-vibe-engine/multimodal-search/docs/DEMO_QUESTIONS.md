# Vibe Search — 50 Demo Queries

A curated bank of 50 search queries designed to **prove the semantic and contextual depth** of the Gemini Embedding 2 + Vertex AI Vector Search 2.0 stack — not just keyword matching, but real understanding of subject, style, mood, composition, and subtle visual cues.

Each entry has:

- **Query** — what to type into the search box (and which modality filter to use)
- **Why it's interesting** — the specific aspect of semantic search it stresses
- **Expected behavior** — what a "good" result set looks like, so you can call out a hit live

The queries are grouped by **what they prove**, not by modality, so you can sequence the demo around a narrative arc.

---

## Section A — Fine-grained detail recall (the model sees the small stuff)

These prove the model attends to tiny visual cues that a keyword search would never surface.

| # | Query | Modality | Why it matters | Expected |
|---|---|---|---|---|
| 1 | `ant crawling on a leaf` | Photo / All | A literal one-pixel-tall subject — proves the embedding picks up the *foreground object*, not just the dominant green leaf. | Top hits show macro-photography of insects on leaves; a nature shot dominated by leaves with **no insect** ranks lower. |
| 2 | `single dewdrop catching the morning light` | Photo / All | Combines a subtle subject (one dewdrop, not many) with a *lighting condition*. | Macro spider-web + single droplet + warm backlight beats a generic wet-leaves shot. |
| 3 | `bee covered in pollen on a yellow flower` | Photo / All | Two-attribute compositional cue ("covered in pollen", colour-aware). | Yellow + bee + visible pollen dust. A bee on a *blue* flower should rank lower. |
| 4 | `single red leaf lying on snow` | Photo / All | Counting + colour contrast in a sea of white. | Red-on-white minimalism, not a forest of red leaves. |
| 5 | `frost crystals forming on a window` | Photo / All | Texture + transformation. | Macro frost geometry, not generic winter scenes. |

---

## Section B — Mood and atmosphere (vibes a tagger can't write)

A human curator types `landscape, sea, lighthouse`. Gemini hears `melancholic, isolated, weather-beaten`.

| # | Query | Modality | Why it matters | Expected |
|---|---|---|---|---|
| 6 | `lonely Sunday afternoon` | All Items | No physical noun — pure mood. | Empty park benches, half-finished coffees, rainy windows; not "weekend brunch crowd". |
| 7 | `the calm before a storm` | All Items | The *absence* of the storm is the point. | Heavy clouds rolling in, still water, empty beach — not actual rain or lightning. |
| 8 | `warm cozy nostalgic` | All Items | Three-attribute mood across modalities. | Polaroid stacks, vintage radios, lo-fi acoustic music, warm-toned graphics. |
| 9 | `the weight of leadership` | Photo | Metaphorical — no literal noun in the catalog. | Solo executive at a window, hands clasped, dim lighting; not a "team meeting". |
| 10 | `quiet pride after a long day` | Photo | Emotion + temporal context. | Tired smile, soft lighting, end-of-day frame. |

---

## Section C — Compositional and relational understanding

The model has to understand *who is doing what to whom*, not just `child + umbrella + woman`.

| # | Query | Modality | Why it matters | Expected |
|---|---|---|---|---|
| 11 | `child sharing an umbrella with their grandmother` | Photo | Three subjects + a verb of relation. | Two-person shots, one tall, one short, with shared umbrella. A photo of just an umbrella should *not* win. |
| 12 | `father teaching his son to ride a bike` | Photo / Video | Action verb + intergenerational pair. | Adult holding the seat, child on the bike, motion blur. |
| 13 | `hands passing a letter across a table` | Photo | POV + object-handover composition. | Two pairs of hands, envelope mid-transfer. |
| 14 | `couple walking away from camera into sunset` | Photo / Video | Camera direction + composition. | Backs to the camera, golden hour. |
| 15 | `surgeon's hands tying a knot during surgery` | Photo | Domain-specific micro-action. | Gloved hands + suture; not "doctor smiling at camera". |

---

## Section D — Style, era, cultural reference

Tests if the embeddings encode *art-historical and cultural shorthand*.

| # | Query | Modality | Why it matters | Expected |
|---|---|---|---|---|
| 16 | `Bauhaus primary-colour poster` | Graphic | Specific design movement. | Red/blue/yellow rectangles, geometric type. |
| 17 | `Art Deco gold geometric pattern` | Graphic | Style-only query, no subject. | Sunburst motifs, gold-on-black, fan shapes. |
| 18 | `Japanese ukiyo-e woodblock print` | Graphic | Cross-cultural style cue. | Wave + Mt Fuji aesthetic, flat colour, line work. |
| 19 | `Memphis design pattern from the 80s` | Graphic | Era-specific. | Squiggles, confetti shapes, neon palette. |
| 20 | `Holi colour festival in India` | Photo | Specific cultural event. | Powder-covered faces, vibrant pigment in air. |

---

## Section E — Lighting, colour, time of day

Pure photographic-attribute queries — no subject given.

| # | Query | Modality | Why it matters | Expected |
|---|---|---|---|---|
| 21 | `blue hour cityscape with reflections` | Photo / Video | Time-of-day + composition + atmosphere. | Twilight skies, deep blue water, lit windows; not noon shots. |
| 22 | `monochrome black-and-white street photography` | Photo | Tonal-only filter; subject can be anything. | Grayscale, candid framing, urban context. |
| 23 | `golden hour in a wheat field` | Photo / Video | Sunset light + specific environment. | Backlit wheat heads, lens flare. |
| 24 | `neon-lit cyberpunk alley at night` | Photo / Video | Multi-attribute style + setting. | Pink/purple neon, wet pavement, narrow alleys. |
| 25 | `harsh midday sun on a desert highway` | Photo | Lighting *quality*, not just time. | Sharp shadows, pale pavement, heat shimmer if possible. |

---

## Section F — Cross-modal: same vibe, different media

These prove the unified embedding space — one query, three categories all in tune.

| # | Query | Modality | Why it matters | Expected |
|---|---|---|---|---|
| 26 | `cinematic epic trailer build-up` | All Items | Same vibe should manifest as orchestral music **and** sweeping drone footage **and** dark gradient graphics. | All four sections populated, all on-vibe. |
| 27 | `lo-fi coffee shop morning` | All Items | Music genre + photo scene + graphic palette. | Lo-fi instrumentals + cozy cafe photos + warm-tone graphics. |
| 28 | `tropical beach getaway` | All Items | Travel pack — proves project-level discovery. | Drone reef video + ukulele/marimba audio + palm-leaf graphics + turquoise photos. |
| 29 | `tense documentary investigation` | All Items | Genre vibe across categories. | Dark cinematic music + serious portrait photos + minimalist serif typography. |
| 30 | `wedding celebration outdoor` | All Items | Emotional + situational. | Joyful crowd photos + romantic instrumental + floral graphics + ceremony video. |

---

## Section G — Paraphrase and synonym robustness

The model must **not** depend on lexical overlap with the caption.

| # | Query | Modality | Why it matters | Expected |
|---|---|---|---|---|
| 31 | `a body of water moving against the shore` | Photo / Video | Wordy paraphrase of "ocean waves". | Should rank ocean/wave assets despite zero token overlap with their captions. |
| 32 | `someone preparing food with raw fish` | Video | Indirect description of "sushi chef". | Sushi-prep videos surface even though "sushi" never appears in the query. |
| 33 | `the place where you go when you feel sad` | All Items | Highly abstract paraphrase. | Rainy windows, empty rooms, slow piano. |
| 34 | `light from the sky after the sun has set` | Photo / Video | Paraphrase of "twilight"/"dusk". | Dusk skies, blue hour, evening landscapes. |
| 35 | `the noise a heavy door makes when it shuts` | SFX | Pure description of an SFX, no SFX vocabulary. | Door-slam SFX clips. |

---

## Section H — Multilingual and code-switching

Same embedding space across ~100 languages.

| # | Query | Modality | Why it matters | Expected |
|---|---|---|---|---|
| 36 | `café au lait morning routine` | Photo / All | English with French phrase. | Coffee + breakfast scenes. |
| 37 | `lluvia sobre la ventana` (Spanish: rain on the window) | Photo / All | Pure Spanish — no English token. | Rainy-window shots; comparable score to the English version. |
| 38 | `桜の木の下で` (Japanese: under the cherry tree) | Photo | Pure Japanese. | Cherry-blossom photos. |
| 39 | `forêt en automne brouillard matinal` (French) | Photo | French descriptive phrase. | Foggy autumn forest. |
| 40 | `música chill para estudiar` (Spanish: chill study music) | Audio | Cross-lingual genre query. | Lo-fi / chill instrumentals. |

---

## Section I — Negation and constraint (hard mode)

These probe the limits — useful for **failure-mode honesty** during the demo.

| # | Query | Modality | Why it matters | Expected |
|---|---|---|---|---|
| 41 | `drone shot of a mountain, no people` | Video | Negation handling. | Honest: pure embedding doesn't enforce hard NOT. Use this to motivate the "negative prompt" feature on the roadmap. |
| 42 | `coffee shop, but empty` | Photo | Constraint inversion. | Mostly empty cafe interiors should rank above bustling ones — partial success. |
| 43 | `formal but friendly headshot` | Photo | Two attributes that pull in opposite directions. | Soft smile + business attire + neutral background. |
| 44 | `minimalist but warm interior` | Photo | Style tension. | Scandi + wood tones + soft lighting (not stark white minimalism). |
| 45 | `cinematic but not dark` | Video | Genre + colour-grade conflict. | High-key cinematic shots; bright epic landscapes. |

---

## Section J — Reverse search & creative bridges

Showcases the upload + cross-modal discovery flow.

| # | Query | Modality | Why it matters | Expected |
|---|---|---|---|---|
| 46 | *(upload a moody Tokyo street photo)* | All Items | Image-as-query → cross-modal retrieval. | Synthwave music + neon graphics + similar street-photography. |
| 47 | *(upload a corporate-friendly graphic)* | All Items | Graphic-as-query → matching kit. | Uplifting corporate music + business-meeting photos + clean B-roll. |
| 48 | *(upload a sunrise drone clip)* | All Items | Video-as-query → mood transfer. | Ambient/cinematic music + matching sunrise photos + nature graphics. |
| 49 | `make a moodboard for "early morning farmers market"` | All Items | Multi-asset narrative query. | Photo block: produce stalls. Video: hands choosing tomatoes. Audio: acoustic morning. Graphic: hand-drawn signage. |
| 50 | `find me three clips that tell the story: rain, regret, recovery` | Video / All | Storyboard intent — temporal narrative. | Three on-arc clips in roughly the right order; demonstrates ranking can be sequenced. |

---

## How to run the demo

1. **Open with Section F #28** (`tropical beach getaway`) — fastest "wow" because all four sections populate cleanly and prove cross-modality.
2. **Drop into Section A #1** (`ant crawling on a leaf`) — tiny-detail flex; explain that this proves the model is **not** running a tag-match on `nature` or `green`.
3. **Switch to Section B #6** (`lonely Sunday afternoon`) — pure-mood query; show that there's no token overlap between the query and any caption.
4. **Go multilingual: Section H #37 or #38** — same embedding space, no translation layer.
5. **Section J #46** — drag in an image, get a kit out. The "More like this" / "Build a kit" features hang off this naturally.
6. **Close on Section I #41** — honest failure mode → segue into the negative-prompt and palette-filter roadmap.

## Why these prove the model is good

- **No keyword overlap required**: Sections G and H force the model to operate on *meaning*, not text matching.
- **Composition over bag-of-objects**: Section C requires understanding the *relation* between objects, not their presence.
- **Subtle attention**: Section A proves the embedding doesn't get hijacked by background dominance.
- **Cross-modal coherence**: Section F is impossible without a true unified vector space.
- **Honest limits**: Section I shows where pure ANN ranking ends and where the roadmap (negative prompts, palette pre-filter, hard restricts) takes over.
