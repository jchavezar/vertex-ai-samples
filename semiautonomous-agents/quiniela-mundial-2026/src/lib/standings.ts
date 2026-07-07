// Derives standings + R32 pairings.
// Per-fixture data is the player's 1X2 prediction UNLESS the match has finished
// in real life — in that case the real score takes over, so the bracket reshapes
// to what's actually happening in the tournament.
import { GROUP_LETTERS, GROUPS, groupFixtures, type GroupLetter } from "@/data/groups";
import type { PlayerPredictions, GroupPrediction } from "@/lib/predictions";
import {
  annexeCLookup,
  ANNEXE_C_MATRIX,
  THIRD_SLOT_ANCHORS,
  type ThirdSlotAnchor,
} from "@/data/annexe-c-thirds-matrix";

export type Standing = {
  team: string;
  pts: number;
  gf: number;
  ga: number;
  gd: number;
  played: number;
  w: number;
  d: number;
  l: number;
  realCount: number; // how many of the team's counted matches came from real results
};

export type RealResult = { homeGoals: number; awayGoals: number };
export type RealResults = Record<string, RealResult>; // fixtureId → real final

// Convention: if user provided exact goals use them; else winner pick = 1-0, draw pick = 0-0.
function goalsFor(pred: GroupPrediction): { h: number; a: number } {
  if (Number.isFinite(pred.homeGoals) && Number.isFinite(pred.awayGoals)) {
    return { h: pred.homeGoals as number, a: pred.awayGoals as number };
  }
  if (pred.pick === "H") return { h: 1, a: 0 };
  if (pred.pick === "A") return { h: 0, a: 1 };
  return { h: 0, a: 0 };
}

function blankStanding(team: string): Standing {
  return { team, pts: 0, gf: 0, ga: 0, gd: 0, played: 0, w: 0, d: 0, l: 0, realCount: 0 };
}

function sortStandings(a: Standing, b: Standing): number {
  if (b.pts !== a.pts) return b.pts - a.pts;
  if (b.gd !== a.gd) return b.gd - a.gd;
  if (b.gf !== a.gf) return b.gf - a.gf;
  return a.team.localeCompare(b.team);
}

export function computeGroupStandings(
  letter: GroupLetter,
  predictions: PlayerPredictions,
  real: RealResults = {},
): Standing[] {
  const teams = GROUPS[letter];
  const table: Record<string, Standing> = {};
  for (const t of teams) table[t] = blankStanding(t);

  for (const fx of groupFixtures(letter)) {
    const realFx = real[fx.id];
    const pred = predictions.group[fx.id];
    let h: number;
    let a: number;
    let pick: "H" | "D" | "A";
    let isReal = false;
    if (realFx) {
      h = realFx.homeGoals;
      a = realFx.awayGoals;
      pick = h > a ? "H" : h < a ? "A" : "D";
      isReal = true;
    } else if (pred?.pick) {
      const g = goalsFor(pred);
      h = g.h; a = g.a; pick = pred.pick;
    } else {
      continue;
    }

    const home = table[fx.home];
    const away = table[fx.away];
    if (!home || !away) continue;
    home.played++; away.played++;
    home.gf += h; home.ga += a;
    away.gf += a; away.ga += h;
    home.gd = home.gf - home.ga;
    away.gd = away.gf - away.ga;
    if (pick === "H") { home.pts += 3; home.w++; away.l++; }
    else if (pick === "A") { away.pts += 3; away.w++; home.l++; }
    else { home.pts += 1; away.pts += 1; home.d++; away.d++; }
    if (isReal) { home.realCount++; away.realCount++; }
  }

  return Object.values(table).sort(sortStandings);
}

export function computeAllStandings(
  predictions: PlayerPredictions,
  real: RealResults = {},
): Record<string, Standing[]> {
  const out: Record<string, Standing[]> = {};
  for (const l of GROUP_LETTERS) out[l] = computeGroupStandings(l, predictions, real);
  return out;
}

export function computeThirdPlaceRanking(
  predictions: PlayerPredictions,
  real: RealResults = {},
): Standing[] {
  const all = computeAllStandings(predictions, real);
  const thirds: Standing[] = [];
  for (const l of GROUP_LETTERS) {
    const t = all[l]?.[2];
    if (t) thirds.push(t);
  }
  return thirds.sort(sortStandings);
}

// Returns true once every group has at least one match predicted (so standings exist).
export function hasGroupPicks(predictions: PlayerPredictions): boolean {
  return GROUP_LETTERS.every(l => groupFixtures(l).some(fx => predictions.group[fx.id]?.pick));
}

export type R32Pairing = { slot: string; teams: [string, string] };

// Official FIFA 2026 R32 pairings — matches 73-88 in FIFA's globally-numbered
// schedule, ordered here as R32-1..R32-16.
//
// 12 group winners (1°) + 12 runners-up (2°) + 8 best 3rd-place teams = 32.
// The 8 third-place slots are written as "3rd1".."3rd8" matching their rank
// in `computeThirdPlaceRanking`. FIFA's official assignment matrix maps the
// 3rd of each qualifying group to specific R32 slots based on which 8 of 12
// groups have their 3rd advance (495 possible combinations). We currently
// assign in rank order so the bracket reshapes deterministically; the slot
// row labels will still read "Mejor 3° (#N)" until the qualifying 8 are
// known and FIFA's matrix can be applied verbatim.
//
// Source: FIFA 2026 World Cup match schedule (image-verified 2026-06-23).
export const R32_TEMPLATE: ReadonlyArray<readonly [string, string]> = [
  ["2A", "2B"],     // Match 73
  ["1E", "3rd1"],   // Match 74
  ["1F", "2C"],     // Match 75
  ["1C", "2F"],     // Match 76
  ["1I", "3rd2"],   // Match 77
  ["2E", "2I"],     // Match 78
  ["1A", "3rd3"],   // Match 79
  ["1L", "3rd4"],   // Match 80
  ["1D", "3rd5"],   // Match 81
  ["1G", "3rd6"],   // Match 82
  ["2K", "2L"],     // Match 83
  ["1H", "2J"],     // Match 84
  ["1B", "3rd7"],   // Match 85
  ["1J", "2H"],     // Match 86
  ["1K", "3rd8"],   // Match 87
  ["2D", "2G"],     // Match 88
];

// Maps each "3rdN" placeholder in R32_TEMPLATE to the anchor (1A..1L) it is
// paired against. Anchor order matches the 8 columns of FIFA's Annexe C and
// the slot the corresponding third-place team will occupy.
//   3rd1 (template idx 1)  -> 1E
//   3rd2 (template idx 4)  -> 1I
//   3rd3 (template idx 6)  -> 1A
//   3rd4 (template idx 7)  -> 1L
//   3rd5 (template idx 8)  -> 1D
//   3rd6 (template idx 9)  -> 1G
//   3rd7 (template idx 12) -> 1B
//   3rd8 (template idx 14) -> 1K
export const THIRD_TOKEN_TO_ANCHOR: Record<string, ThirdSlotAnchor> = {
  "3rd1": "1E",
  "3rd2": "1I",
  "3rd3": "1A",
  "3rd4": "1L",
  "3rd5": "1D",
  "3rd6": "1G",
  "3rd7": "1B",
  "3rd8": "1K",
};

export function computeR32Pairings(
  predictions: PlayerPredictions,
  real: RealResults = {},
): R32Pairing[] {
  const all = computeAllStandings(predictions, real);
  const thirdsRanked = computeThirdPlaceRanking(predictions, real).slice(0, 8);

  // Try the official FIFA Annexe C lookup. Requires all 8 qualifying-third
  // groups to be determinable (i.e. every group has a third-place team in
  // the standings, which is always true here, but we additionally need
  // exactly 8 of them to fill the bracket — top 8 by ranking).
  let anchorToTeam: Record<ThirdSlotAnchor, string> | null = null;
  if (thirdsRanked.length === 8) {
    const qualifyingGroups = thirdsRanked.map(t => {
      // Find the group letter whose 3rd-place standing equals this team.
      for (const l of GROUP_LETTERS) {
        if (all[l]?.[2]?.team === t.team) return l;
      }
      return "";
    }).filter(Boolean);
    if (qualifyingGroups.length === 8) {
      const row = annexeCLookup(qualifyingGroups);
      if (row) {
        const m: Partial<Record<ThirdSlotAnchor, string>> = {};
        for (let i = 0; i < THIRD_SLOT_ANCHORS.length; i++) {
          const anchor = THIRD_SLOT_ANCHORS[i];
          const groupLetter = row[i] as GroupLetter;
          const team = all[groupLetter]?.[2]?.team ?? "";
          m[anchor] = team;
        }
        anchorToTeam = m as Record<ThirdSlotAnchor, string>;
      }
    }
  }

  function resolve(token: string): string {
    if (token.startsWith("3rd")) {
      if (anchorToTeam) {
        const anchor = THIRD_TOKEN_TO_ANCHOR[token];
        if (anchor) return anchorToTeam[anchor] ?? "";
      }
      // Fallback: rank-order rendering (used early-tournament before all 8
      // qualifying thirds are known, or if Annexe C matrix is unavailable).
      const idx = parseInt(token.slice(3), 10) - 1;
      return thirdsRanked[idx]?.team ?? "";
    }
    const pos = parseInt(token[0], 10);
    const letter = token.slice(1) as GroupLetter;
    return all[letter]?.[pos - 1]?.team ?? "";
  }

  return R32_TEMPLATE.map((pair, i) => ({
    slot: `R32-${i + 1}`,
    teams: [resolve(pair[0]), resolve(pair[1])] as [string, string],
  }));
}

// Pair winners of round[i] and round[i+1] into next round's matches.
export function pairWinners(winners: string[]): Array<[string, string]> {
  const out: Array<[string, string]> = [];
  for (let i = 0; i < winners.length; i += 2) {
    out.push([winners[i] ?? "", winners[i + 1] ?? ""]);
  }
  return out;
}

// True when all 6 matches in the group have real final results.
export function groupConfirmed(letter: GroupLetter, real: RealResults): boolean {
  const fxs = groupFixtures(letter);
  return fxs.every(fx => !!real[fx.id]);
}

export function groupRealCount(letter: GroupLetter, real: RealResults): { played: number; total: number } {
  const fxs = groupFixtures(letter);
  const played = fxs.filter(fx => !!real[fx.id]).length;
  return { played, total: fxs.length };
}

// For a slot like "1A" or "3rd1" → which group letter(s) feed it.
function slotSourceGroups(token: string): GroupLetter[] {
  if (token.startsWith("3rd")) return [...GROUP_LETTERS] as GroupLetter[];
  return [token.slice(1) as GroupLetter];
}

export function slotConfirmed(pairing: R32Pairing, real: RealResults): boolean {
  const tokenIdx = R32_TEMPLATE.findIndex((_, i) => `R32-${i + 1}` === pairing.slot);
  if (tokenIdx === -1) return false;
  const [a, b] = R32_TEMPLATE[tokenIdx];
  const groups = new Set<GroupLetter>([...slotSourceGroups(a), ...slotSourceGroups(b)]);
  return Array.from(groups).every(l => groupConfirmed(l, real));
}

export type ThirdSlotProb = {
  team: string;
  group: string;
  pct: number; // 0..1
};

function choose<T>(arr: T[], k: number): T[][] {
  if (k === 0) return [[]];
  if (arr.length < k) return [];
  const [head, ...tail] = arr;
  return [
    ...choose(tail, k - 1).map(c => [head, ...c]),
    ...choose(tail, k),
  ];
}

// For each of the 8 third-place slots (anchored by 1A/1B/1D/1E/1G/1I/1K/1L),
// compute probability distribution over which team might fill it.
// Enumerates all C(12,8)=495 Annexe C combos, weights each by combined pts of
// the 8 qualifying thirds, accumulates per-anchor team probabilities.
export function computeThirdSlotProbabilities(
  predictions: PlayerPredictions,
  real: RealResults = {},
): Record<ThirdSlotAnchor, ThirdSlotProb[]> {
  const all = computeAllStandings(predictions, real);

  const thirds = (GROUP_LETTERS as readonly GroupLetter[]).map(l => {
    const t = all[l]?.[2];
    return { group: l, team: t?.team ?? "", pts: t?.pts ?? 0, played: t?.played ?? 0 };
  }).filter(x => x.team);

  const letters = thirds.map(x => x.group);
  const combos = choose(letters, Math.min(8, letters.length));

  const acc: Record<string, Record<string, number>> = {};
  for (const a of THIRD_SLOT_ANCHORS) acc[a] = {};
  let totalW = 0;

  for (const combo of combos) {
    const key = [...combo].sort().join("");
    const row = ANNEXE_C_MATRIX[key];
    if (!row) continue;

    // Product of exp(pts) — exponential separation means 4pts vs 3pts is 2.7x
    // more likely, not just 33% more. Correctly reflects that a team with more
    // points is disproportionately more probable to be in the qualifying top-8.
    const weight = combo.reduce((prod, g) => {
      const info = thirds.find(t => t.group === g);
      return prod * Math.exp(info ? info.pts : 0);
    }, 1);
    totalW += weight;

    for (let i = 0; i < THIRD_SLOT_ANCHORS.length; i++) {
      const anchor = THIRD_SLOT_ANCHORS[i];
      const srcGroup = row[i] as GroupLetter;
      const info = thirds.find(t => t.group === srcGroup);
      if (!info?.team) continue;
      acc[anchor][info.team] = (acc[anchor][info.team] ?? 0) + weight;
    }
  }

  const result = {} as Record<ThirdSlotAnchor, ThirdSlotProb[]>;
  for (const anchor of THIRD_SLOT_ANCHORS) {
    result[anchor] = Object.entries(acc[anchor])
      .map(([team, w]) => ({
        team,
        group: thirds.find(t => t.team === team)?.group ?? "",
        pct: totalW > 0 ? w / totalW : 0,
      }))
      .sort((a, b) => b.pct - a.pct);
  }
  return result;
}
