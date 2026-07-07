// Monte Carlo simulator for the Mundial 2026 bracket.
//
// Inputs:
//   - Per-fixture {H, D, A} probabilities for all 72 group-stage matches.
//   - Optional already-known final results (locked in stone, not re-simulated).
//
// Outputs aggregated probabilities for every team:
//   - P(top-2 in group), P(best-3rd advance), P(reach R32 / R16 / QF / SF / Final),
//   - P(champion), expected group points, expected goal differential.
//
// Implementation notes:
//   - Each group match is a Bernoulli draw across {H, D, A}.
//   - Scorelines are synthesized so we can compute GD/GF/GA tiebreakers
//     (drawn from a small Poisson-ish lookup biased by predicted outcome).
//   - The 8 best 3rd-placed teams advance per FIFA 2026 rules (12 groups,
//     top 2 + 8 best 3rds = 32 teams into R32).
//   - Knockout matches re-normalize {H, A} after dropping draws (penalties
//     resolve to one side via prob ratio).
//   - Bracket pairing for R32 → R16 → ... follows the FIFA 2026 published
//     bracket structure (see PAIRINGS below).

import { allGroupFixtures, GROUPS, type GroupLetter } from "@/data/groups";
import type { Probs } from "@/lib/probability-engine";
import type { BracketTeamProbs } from "@/lib/probability-snapshots";

export type FixtureProbsMap = Record<string, Probs>;
export type KnownResults = Record<string, { homeGoals: number; awayGoals: number }>;

// ---------- helpers ----------

function sample3(p: Probs, rng: () => number): "H" | "D" | "A" {
  const r = rng();
  if (r < p.H) return "H";
  if (r < p.H + p.D) return "D";
  return "A";
}

// Tiny PRNG (mulberry32) so runs are reproducible in tests / debugging.
export function mulberry32(seed: number): () => number {
  let a = seed >>> 0;
  return function () {
    a |= 0; a = (a + 0x6D2B79F5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

// Synthesize a scoreline based on the realized outcome and the favorite's edge.
// Goals here are only used for tiebreakers — they don't need to be realistic
// per-match, just statistically reasonable in aggregate.
function synthScore(outcome: "H" | "D" | "A", p: Probs, rng: () => number): { hg: number; ag: number } {
  // edge = how confident the favorite was. The larger, the larger the GD.
  const edge = outcome === "H" ? p.H - p.A : outcome === "A" ? p.A - p.H : Math.min(p.H, p.A);
  // Base GD distribution: 1 with 0.55, 2 with 0.30, 3+ with 0.15, scaled by edge.
  const r = rng();
  let gd: number;
  if (outcome === "D") {
    // Draw scores: 1-1 (0.55), 0-0 (0.30), 2-2 (0.15)
    if (r < 0.55) return { hg: 1, ag: 1 };
    if (r < 0.85) return { hg: 0, ag: 0 };
    return { hg: 2, ag: 2 };
  }
  if (r < 0.50) gd = 1;
  else if (r < 0.80) gd = 2;
  else if (r < 0.93) gd = 3;
  else gd = 4;
  if (edge > 0.4) gd = Math.min(5, gd + 1); // blowout for huge favorites
  // Losing side scores 0-2.
  const lo = rng() < 0.45 ? 0 : rng() < 0.7 ? 1 : 2;
  const hi = lo + gd;
  return outcome === "H" ? { hg: hi, ag: lo } : { hg: lo, ag: hi };
}

// FIFA 2026 R32 pairings. Source: the official R32 pairing tree.
// Each entry is a pair of "slot specs". A slot spec is either:
//   "1A" (winner of group A), "2C" (runner-up C), or "3X/Y/Z/W" (best-3rd from X|Y|Z|W).
// We codify the 16 R32 matches in order so the R16 → QF → SF brackets follow.
//
// Reference: https://en.wikipedia.org/wiki/2026_FIFA_World_Cup_knockout_stage
type SlotSpec =
  | { kind: "WIN"; group: GroupLetter }
  | { kind: "RU"; group: GroupLetter }
  | { kind: "BEST3"; pool: GroupLetter[] };

type R32Pair = [SlotSpec, SlotSpec];

// The "best-3rd pool" depends on which 8 of 12 groups have their 3rd placed
// team in the top 8. FIFA publishes a lookup keyed by which groups qualified,
// but for the simulator we assign best-3rds to bracket slots in their order
// of qualification (top of standings first). This is a simplification — the
// official table is more nuanced — but it's stable enough to give per-team
// "reach R16" probabilities consistent with the broader bracket structure.
const R32_PAIRS: R32Pair[] = [
  // Slot indices 0..15 in order. Each slot will become R16 winner, then QF, etc.
  [{ kind: "WIN", group: "A" }, { kind: "BEST3", pool: ["C","D","E","F","I","J","K","L"] }],
  [{ kind: "RU", group: "B" },  { kind: "RU", group: "F" }],
  [{ kind: "WIN", group: "C" }, { kind: "BEST3", pool: ["A","B","E","F","G","H","I","J"] }],
  [{ kind: "RU", group: "D" },  { kind: "RU", group: "H" }],
  [{ kind: "WIN", group: "E" }, { kind: "BEST3", pool: ["B","C","G","H","I","J","K","L"] }],
  [{ kind: "RU", group: "A" },  { kind: "RU", group: "E" }],
  [{ kind: "WIN", group: "G" }, { kind: "BEST3", pool: ["A","B","C","D","F","H","K","L"] }],
  [{ kind: "RU", group: "C" },  { kind: "RU", group: "G" }],
  [{ kind: "WIN", group: "I" }, { kind: "BEST3", pool: ["A","B","C","D","F","G","H","K"] }],
  [{ kind: "RU", group: "J" },  { kind: "RU", group: "L" }],
  [{ kind: "WIN", group: "K" }, { kind: "BEST3", pool: ["A","B","D","E","F","G","H","I"] }],
  [{ kind: "WIN", group: "F" }, { kind: "WIN", group: "H" }],
  [{ kind: "WIN", group: "B" }, { kind: "BEST3", pool: ["E","F","G","H","I","J","K","L"] }],
  [{ kind: "RU", group: "I" },  { kind: "RU", group: "K" }],
  [{ kind: "WIN", group: "L" }, { kind: "BEST3", pool: ["A","B","C","D","E","F","G","H"] }],
  [{ kind: "WIN", group: "D" }, { kind: "WIN", group: "J" }],
];

// R16 pairings: pairs of R32 winner slots.
const R16_PAIRS: Array<[number, number]> = [
  [0, 1], [2, 3], [4, 5], [6, 7], [8, 9], [10, 11], [12, 13], [14, 15],
];
const QF_PAIRS: Array<[number, number]> = [
  [0, 1], [2, 3], [4, 5], [6, 7],
];
const SF_PAIRS: Array<[number, number]> = [[0, 1], [2, 3]];

// ---------- per-group standings (single sim) ----------

type Standing = {
  code: string;
  pts: number;
  gf: number;
  ga: number;
  gd: number;     // gf - ga
};

function freshStanding(code: string): Standing {
  return { code, pts: 0, gf: 0, ga: 0, gd: 0 };
}

function compareStandings(a: Standing, b: Standing): number {
  // FIFA tiebreakers: pts → gd → gf → (then h2h / fair play, ignored for sim).
  if (b.pts !== a.pts) return b.pts - a.pts;
  if (b.gd !== a.gd) return b.gd - a.gd;
  return b.gf - a.gf;
}

// ---------- main simulator ----------

export type SimulationResult = {
  teams: Record<string, BracketTeamProbs>;
  simulations: number;
};

export type SimulateOptions = {
  probs: FixtureProbsMap;
  known?: KnownResults;
  iterations?: number;
  seed?: number;
};

export function simulateBracket(opts: SimulateOptions): SimulationResult {
  const iters = opts.iterations ?? 10_000;
  const rng = mulberry32(opts.seed ?? 0xCAFEBABE);
  const fixtures = allGroupFixtures();

  // Pre-index fixtures by group for fast standings rebuild.
  const fixturesByGroup: Record<GroupLetter, typeof fixtures> = {} as Record<GroupLetter, typeof fixtures>;
  for (const g of Object.keys(GROUPS) as GroupLetter[]) fixturesByGroup[g] = [];
  for (const fx of fixtures) fixturesByGroup[fx.group].push(fx);

  const allCodes = Object.values(GROUPS).flat();
  const counts: Record<string, BracketTeamProbs> = {};
  for (const code of allCodes) {
    counts[code] = {
      code,
      pTop2: 0, pBest3rd: 0, pR32: 0, pR16: 0, pQF: 0, pSF: 0, pFinal: 0, pChampion: 0,
      expectedPoints: 0, expectedGoalDiff: 0,
    };
  }

  const sumPoints: Record<string, number> = {};
  const sumGD: Record<string, number> = {};
  for (const code of allCodes) { sumPoints[code] = 0; sumGD[code] = 0; }

  for (let it = 0; it < iters; it++) {
    // 1) Sim every group-stage fixture (or use known result).
    const standings: Record<string, Standing> = {};
    for (const code of allCodes) standings[code] = freshStanding(code);

    for (const fx of fixtures) {
      const p = opts.probs[fx.id];
      let hg: number, ag: number;
      const known = opts.known?.[fx.id];
      if (known) {
        hg = known.homeGoals; ag = known.awayGoals;
      } else if (!p) {
        // No prob for this fixture — assume tossup so a missing fixture
        // doesn't deterministically reward one side.
        const o = sample3({ H: 1 / 3, D: 1 / 3, A: 1 / 3 }, rng);
        const s = synthScore(o, { H: 1 / 3, D: 1 / 3, A: 1 / 3 }, rng);
        hg = s.hg; ag = s.ag;
      } else {
        const o = sample3(p, rng);
        const s = synthScore(o, p, rng);
        hg = s.hg; ag = s.ag;
      }
      const h = standings[fx.home];
      const a = standings[fx.away];
      h.gf += hg; h.ga += ag; h.gd = h.gf - h.ga;
      a.gf += ag; a.ga += hg; a.gd = a.gf - a.ga;
      if (hg > ag) h.pts += 3;
      else if (hg < ag) a.pts += 3;
      else { h.pts += 1; a.pts += 1; }
    }

    // 2) Per-group rank: collect top-2 and 3rd-placed.
    const winners: Record<GroupLetter, string> = {} as Record<GroupLetter, string>;
    const runnersUp: Record<GroupLetter, string> = {} as Record<GroupLetter, string>;
    const thirds: Array<{ group: GroupLetter; standing: Standing }> = [];
    for (const g of Object.keys(GROUPS) as GroupLetter[]) {
      const ranked = GROUPS[g].map(c => standings[c]).sort(compareStandings);
      winners[g] = ranked[0].code;
      runnersUp[g] = ranked[1].code;
      thirds.push({ group: g, standing: ranked[2] });
      counts[ranked[0].code].pTop2 += 1;
      counts[ranked[1].code].pTop2 += 1;
    }

    // 3) 8 best 3rd-placed teams advance.
    const sortedThirds = thirds.sort((a, b) => compareStandings(a.standing, b.standing));
    const best3 = sortedThirds.slice(0, 8);
    const best3Codes = new Set(best3.map(t => t.standing.code));
    for (const t of best3) counts[t.standing.code].pBest3rd += 1;

    // 4) Build R32 slot teams. For best-3 slots, pick the next-best-3 from
    //    the pool that still has an unassigned advancing team.
    const usedBest3 = new Set<string>();
    const slotTeam: string[] = new Array(16).fill("");
    for (let i = 0; i < R32_PAIRS.length; i++) {
      const [a, b] = R32_PAIRS[i];
      const resolve = (spec: SlotSpec): string => {
        if (spec.kind === "WIN") return winners[spec.group];
        if (spec.kind === "RU") return runnersUp[spec.group];
        // BEST3: pick best advancing 3rd from spec.pool that we haven't used yet.
        for (const t of best3) {
          if (spec.pool.includes(t.group) && !usedBest3.has(t.standing.code)) {
            usedBest3.add(t.standing.code);
            return t.standing.code;
          }
        }
        // Fallback: any unused best-3rd.
        for (const t of best3) {
          if (!usedBest3.has(t.standing.code)) {
            usedBest3.add(t.standing.code);
            return t.standing.code;
          }
        }
        return "";
      };
      // We need a stable evaluation order: alternate WIN/RU first, BEST3 second.
      // Build the slot in two passes so BEST3 picks see all WIN/RU first.
      slotTeam[i * 2] = a.kind === "BEST3" ? "__DEFER__" : resolve(a);
      slotTeam[i * 2 + 1] = b.kind === "BEST3" ? "__DEFER__" : resolve(b);
    }
    // Second pass: fill BEST3 deferrals in pair-order.
    for (let i = 0; i < R32_PAIRS.length; i++) {
      const [a, b] = R32_PAIRS[i];
      if (a.kind === "BEST3" && slotTeam[i * 2] === "__DEFER__") slotTeam[i * 2] = (a.kind === "BEST3" ? (() => {
        for (const t of best3) {
          if (a.pool.includes(t.group) && !usedBest3.has(t.standing.code)) {
            usedBest3.add(t.standing.code);
            return t.standing.code;
          }
        }
        for (const t of best3) {
          if (!usedBest3.has(t.standing.code)) {
            usedBest3.add(t.standing.code);
            return t.standing.code;
          }
        }
        return "";
      })() : "");
      if (b.kind === "BEST3" && slotTeam[i * 2 + 1] === "__DEFER__") slotTeam[i * 2 + 1] = (b.kind === "BEST3" ? (() => {
        for (const t of best3) {
          if (b.pool.includes(t.group) && !usedBest3.has(t.standing.code)) {
            usedBest3.add(t.standing.code);
            return t.standing.code;
          }
        }
        for (const t of best3) {
          if (!usedBest3.has(t.standing.code)) {
            usedBest3.add(t.standing.code);
            return t.standing.code;
          }
        }
        return "";
      })() : "");
    }

    // R32 reached counts (top-2 + best-3 advancing).
    for (let i = 0; i < 32; i++) {
      const code = slotTeam[i];
      if (!code) continue;
      counts[code].pR32 += 1;
    }

    // 5) Knockouts. Use the per-fixture probs only for group stage; for
    //    knockouts we don't have per-pair probs, so derive a simple H vs A
    //    win prob from the *current* ELO-based model probability of those
    //    teams meeting at a neutral venue. We approximate: P(team X beats Y)
    //    = avg over all group-stage fixtures where they nominally faced any
    //    similarly-ranked opponent. For simplicity, we use a softmax over
    //    pre-computed "team strength" derived from their expected group points.
    //
    //    Cheaper proxy: use the team's pTop2 share as its strength (running
    //    average is fine over enough iters). But pTop2 is updated across
    //    iters, so we use a per-sim local strength: each team's points this sim.
    const winProb = (a: string, b: string): number => {
      // pseudo-ELO: each team's "strength" this sim = group pts + gd*0.5 + gf*0.2.
      const score = (c: string): number => {
        const s = standings[c];
        return s.pts * 1 + s.gd * 0.5 + s.gf * 0.2;
      };
      const diff = score(a) - score(b);
      // map diff to win prob with sigmoid centred at 0.
      return 1 / (1 + Math.exp(-diff / 3));
    };

    const playPair = (h: string, a: string): string => {
      if (!h) return a;
      if (!a) return h;
      const pH = winProb(h, a);
      return rng() < pH ? h : a;
    };

    // R32 → R16 winners
    const r16Winners: string[] = [];
    for (const [i, j] of R16_PAIRS) {
      // Each R16 pair takes 4 R32 slots: slot i*2, i*2+1, j*2, j*2+1.
      const wA = playPair(slotTeam[i * 2], slotTeam[i * 2 + 1]);
      const wB = playPair(slotTeam[j * 2], slotTeam[j * 2 + 1]);
      if (wA) counts[wA].pR16 += 1;
      if (wB) counts[wB].pR16 += 1;
      r16Winners.push(wA, wB);
    }

    // R16 → QF winners (8 → 4)
    const qfWinners: string[] = [];
    for (let i = 0; i < r16Winners.length; i += 2) {
      const w = playPair(r16Winners[i], r16Winners[i + 1]);
      if (w) counts[w].pQF += 1;
      qfWinners.push(w);
    }

    // QF → SF (4 → 2)
    const sfWinners: string[] = [];
    for (let i = 0; i < qfWinners.length; i += 2) {
      const w = playPair(qfWinners[i], qfWinners[i + 1]);
      if (w) counts[w].pSF += 1;
      sfWinners.push(w);
    }

    // SF → Final (2 → 1)
    const finalists: string[] = [];
    for (let i = 0; i < sfWinners.length; i += 2) {
      const w = playPair(sfWinners[i], sfWinners[i + 1]);
      if (w) counts[w].pFinal += 1;
      finalists.push(w);
      const loser = sfWinners[i] === w ? sfWinners[i + 1] : sfWinners[i];
      if (loser) counts[loser].pFinal += 1; // both finalists count
    }
    // The block above double-counted finalists (winners counted once, then
    // again as loser pair); rebuild cleanly:
    // (Reset the +1 we just added for the loser and only count winner of SF
    // matches as finalist.)
    // Simpler: revert and recompute.
    // To keep code simple, undo: subtract loser back out.
    {
      const setFromLoser: string[] = [];
      for (let i = 0; i < sfWinners.length; i += 2) {
        const w = finalists[Math.floor(i / 2)];
        const loser = sfWinners[i] === w ? sfWinners[i + 1] : sfWinners[i];
        if (loser) setFromLoser.push(loser);
      }
      // (the loser was incremented above by mistake; subtract now)
      for (const l of setFromLoser) counts[l].pFinal -= 1;
    }
    // Now both finalists ARE counted: SF winners reach final.
    // Champion:
    if (finalists.length === 2) {
      const champ = playPair(finalists[0], finalists[1]);
      if (champ) counts[champ].pChampion += 1;
    } else if (finalists.length === 1) {
      counts[finalists[0]].pChampion += 1;
    }

    // 6) Track expected points / GD.
    for (const code of allCodes) {
      sumPoints[code] += standings[code].pts;
      sumGD[code] += standings[code].gd;
    }
  }

  const result: Record<string, BracketTeamProbs> = {};
  for (const code of allCodes) {
    const c = counts[code];
    result[code] = {
      code,
      pTop2: c.pTop2 / iters,
      pBest3rd: c.pBest3rd / iters,
      pR32: c.pR32 / iters,
      pR16: c.pR16 / iters,
      pQF: c.pQF / iters,
      pSF: c.pSF / iters,
      pFinal: c.pFinal / iters,
      pChampion: c.pChampion / iters,
      expectedPoints: sumPoints[code] / iters,
      expectedGoalDiff: sumGD[code] / iters,
    };
  }
  return { teams: result, simulations: iters };
}
