# AI bot upgrade — plan

## Goals
- Convert `ai` bot from "ELO+odds favorite picker" into an aggressive, Gemini-reasoned competitor.
- Expose per-fixture H/D/A probabilities and per-team championship probabilities to all players.
- Persist daily snapshots so we can chart evolution (task #43).
- Anti-cheat: bot reads only pre-kickoff data. Server lock in `predictions-server.ts:mergeWithServerLocks` already enforces this.

## Pieces touched
- New: `src/lib/probability-engine.ts` — pure blender (ELO + odds + recent form + host bonus).
- New: `src/lib/bracket-simulator.ts` — Monte Carlo 10k sims using per-fixture probs.
- New: `src/lib/ai-reasoner.ts` — Gemini call wrapper.
- New: `src/lib/probability-snapshots.ts` — Firestore writes for daily snapshots.
- New: `src/app/api/probabilities/route.ts` — GET, returns map of fixture probs + caches.
- New: `src/app/api/probabilities/bracket/route.ts` — GET, returns per-team round %s + caches.
- New: `src/app/api/probabilities/history/route.ts` — GET ?teamId | ?fixtureId.
- New: `src/app/api/cron/ai-refresh/route.ts` — cron entry, gated by `x-cron-secret`.
- Modified: `src/app/api/ai/sync/route.ts` — calls reasoner per non-locked fixture, persists `reasoning` + `confidence`.
- Modified: `src/lib/predictions.ts` — extend `GroupPrediction` with optional `reasoning?: string; confidence?: number`.
- Modified: `src/app/partidos/page.tsx` — add 3-bar probability strip on upcoming match cards.
- Modified: `src/app/bracket/page.tsx` and `src/app/ranking/page.tsx` — show % campeón under each team.

## Blender weights (v1)
`blend = 0.55 * implied_odds + 0.30 * elo_current + 0.15 * form_recent` (renormalized if odds missing).
Host bonus only applied when host nation plays at home in its own country (using `venues.ts` city → country map).

## Aggressive Gemini prompt
- Inputs: home/away (name+code+tier+strength), kickoff, current ELO delta, model-blend H/D/A, market H/D/A, recent form (W/D/L last 5), context (matchday, group standings if MD2/MD3).
- Output JSON: `{ pick: "H"|"D"|"A", confidence: 0-1, reasoning: string }`.
- Style: explicitly biased toward value — when a non-favorite has implied prob within 5pp of favorite, prefer upset/draw when reasoning supports it.

## Monte Carlo bracket
- 10k full simulations of group stage using fixture probs + simulated GD/GF.
- Top 2 + 8 best 3rd → R32. Sim each knockout via "no-draw" probs.
- Aggregate: P(top2), P(R32 win), P(R16), P(QF), P(SF), P(FINAL), P(CHAMP).

## Snapshots
- Document id pattern: `{YYYY-MM-DD}` (UTC) in collections `fixture_probabilities_history` and `bracket_probabilities_history`.
- Latest cached: `fixture_probabilities/current` + `bracket_probabilities/current`.

## UI exposure (subtle)
- Match card (pre-kickoff only): 3-segment bar with `--accent-mint`/`--ink-muted`/`--accent-coral`.
- Bracket card: small "% campeón" beside team name.

## Cron
- `gcloud scheduler jobs create http q26-ai-refresh --schedule "0 */6 * * *" --time-zone="America/New_York" --uri="https://q26.sonrobots.net/api/cron/ai-refresh" --http-method=POST --headers="x-cron-secret=$CRON_SECRET" --project=vtxdemos --location=us-central1`
- Cron handler: 1) refresh fixture probs (snapshot), 2) refresh bracket probs (snapshot), 3) re-run AI sync.

## Out of scope (v2)
- Injury / suspension scraping.
- Per-player-prop probabilities.
- Live in-match probability updates (we honor the kickoff lock).
