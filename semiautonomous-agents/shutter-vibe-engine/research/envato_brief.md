# Envato — Customer Brief (April 2026)

## The ask (verbatim)

> Envato is a creative-asset company owned by Shutterstock. They are seeking
> more information about Gemini Embeddings 2 and Vector Search 2.0 in the
> context of improving their current search capabilities for their multi-modal
> assets (images, videos, graphics, etc.). They see the most downloads of
> their assets today via the Search tool so it is an important funnel for
> their business. They want to understand its capabilities for improving
> their current search and **guiding users when their search turns up with
> no results**.

## Who Envato is

* Acquired by Shutterstock on **22 July 2024 for ~$245M cash**.
* Brought 650K subs → Shutterstock now ~1.15M subs total.
* Headquartered in Melbourne; global creator base.
* Already a Google Cloud GenAI customer — **Envato Labs `VideoGen` runs on Google Veo 2 via Vertex AI**. Embeddings 2 + Vector Search 2.0 is an *expansion*, not a new-vendor decision.

## Catalog

| Property | What | Volume |
| -------- | ---- | ------ |
| **Envato Elements** | Subscription, unlimited downloads | 22 M+ assets (10 M images, 6 M videos, 1 M audio, 0.5 M templates, 0.2 M graphics/fonts) |
| **VideoHive** | Stock footage + AE/Premiere/DaVinci/Motion templates | 10 849 545 items |
| **AudioJungle** | Music, SFX, kits, idents, logos | 2 411 967 tracks |
| **GraphicRiver** | Graphics, fonts, presentations, infographics | 833 398 items |
| **ThemeForest** | WP, Shopify, HTML, Figma, etc. themes | "Largest in world"; bestseller Avada has 1 M+ sales |
| **CodeCanyon** | PHP/JS/.NET/mobile apps + plugins | Large |
| **3DOcean** | 3D models, textures, HDRI | 55 472 items |
| **Placeit** | Mockups, logo maker, design templates | Acquired 2018 |
| **Envato Tuts+** | Tutorials | — |
| **Envato Labs** | AI suite (ImageGen, VideoGen on Veo 2, VoiceGen, MusicGen, ImageEdit, InspoGen) | Free with sub |

Cross-marketplace lifetime: **78.6 M items sold, $1.246 B paid to community**.

## How search works today

* Heavy reliance on contributor tags + title + description.
* **Token-OR matching** — search "lawn care icon set" returns dental-care, beauty-care, car-care results.
* Filters: orientation, colour, resolution, aspect ratio, duration, file type, software, genre/mood, contributor.
* Sort: Relevance, Popularity, Newest, Trending, Featured.
* Cross-marketplace blindness — Elements query never surfaces a Market asset.
* Long-tail / multi-word descriptive queries fail often (this is where the rescue use case lives).
* AI-assisted search and "vector search" appear in product copy but execution is greenfield.

## What happens today on a zero-result search

1. Generic empty state: "Try different keywords."
2. A few category fall-back recommendations.
3. **No semantic rescue** — user retypes manually, or leaves.
4. Failed-search → tab close → competitor (Adobe Stock, Storyblocks, Canva) → churn risk.

## Personas

* Solo designer / freelancer (primary Elements buyer)
* SMB / mid-market marketing team (multi-seat Team plans)
* Video editor / motion designer (heavy VideoHive + AudioJungle)
* Content creator / YouTuber / TikToker
* Web developer / agency (ThemeForest + CodeCanyon)
* Hobbyist / micro-business (Placeit-style)
* **Enterprise creative ops** — newer, courted post-Shutterstock acquisition

## Competitive snapshot

| Player | Pricing | Library | Notes |
| ------ | ------- | ------- | ----- |
| Adobe Stock | $30–$200 / mo | 300 M+ images, 25 M+ video | Creative Cloud + Firefly + $10 K indemnification |
| Canva | $0–$15 / mo | Templates-first | All-in-one editor |
| Creative Market | per-item | Curated indie | Premium but small |
| Storyblocks | sub | Strong video + audio | Narrower modalities |
| Freepik / Flaticon | freemium | Massive vectors | AI generation, lower brand premium |

**Envato's structural moat**: only major player covering templates, themes,
code, AND stock. A unified semantic search across all of it is a
defensible feature competitors cannot easily copy.

## The 10 demo use cases

| # | Use case | Stack | WOW |
| - | -------- | ----- | --- |
| UC1 | Unified multimodal search across all marketplaces | Gemini Emb 2 + Vector Search 2.0 (hybrid, marketplace filters) | One query → six asset types, one aesthetic |
| UC2 | **Zero-result rescue** | Gemini Emb 2 + Vector Search 2.0 ANN + confidence threshold | Customer's verbatim ask — type something weird, watch it recover |
| UC3 | Conceptual type-ahead (suggest concepts, not prefixes) | Embedding-clustered query log | Suggests concepts the user didn't know to ask for |
| UC4 | Visual similarity from a sketch / wireframe upload | Image embedding → image-image search across templates | "Know it when I see it" gap closed |
| UC5 | Cross-format project bundle ("complete the project") | Multimodal embeddings + cross-modality NN | ARPU lift via cross-sell |
| UC6 | Brand-kit compliance search | Multi-aspect embeddings (colour, type, mood) + weighted query | Moves Envato up-market into Enterprise |
| UC7 | Trend-cluster discovery for contributors | Cluster query+asset embeddings; gap analysis | Two-sided flywheel |
| UC8 | Multilingual semantic search | Gemini Emb 2 native cross-lingual | Lifts non-English conversion |
| UC9 | Style-transfer search (image + text modifier) | Composed multimodal query | "Search for style" — never possible before |
| UC10 | Personalised re-ranking & session-aware rescue | User embedding × asset embedding | Same query, different rescue per persona |

## Suggested meeting flow

1. **UC2 zero-result rescue** — verbatim customer ask; biggest visual wow
2. **UC1 unified search** — only Envato can do this at this scale
3. **UC4 visual upload** — concrete designer workflow
4. **UC8 multilingual** — global ARPU
5. **UC6 brand-kit** — enterprise expansion
6. **UC7 contributor trend insights** — flywheel / strategic close

## Sources

* https://investor.shutterstock.com/news-releases/news-release-details/shutterstock-completes-acquisition-envato
* https://themeforest.net , https://videohive.net , https://audiojungle.net , https://graphicriver.net , https://codecanyon.net , https://3docean.net
* https://labs.envato.com
* https://weandthecolor.com/envato-elements-vs-adobe-stock-which-is-better-for-graphic-designers-in-2026/
* https://photutorial.com/adobe-stock-vs-envato-elements/
