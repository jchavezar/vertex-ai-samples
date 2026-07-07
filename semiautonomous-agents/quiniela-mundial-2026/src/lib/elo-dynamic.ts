// Dynamic strength layer. Operates on the same 0-100 scale as team-strength.ts.
// After each finished fixture, both teams' strengths shift toward what the
// result actually showed. The delta is persisted in Firestore so the next
// sync can pick up where we left off.

import { TEAM_STRENGTH } from "@/data/team-strength";

export type EloDelta = Record<string, number>;

export type EloEvent = {
  fixtureId: string;
  date: string;       // ISO date
  homeCode: string;
  awayCode: string;
  homeGoals: number;
  awayGoals: number;
  homeBefore: number;
  awayBefore: number;
  homeAfter: number;
  awayAfter: number;
  homeDelta: number;
  awayDelta: number;
  ts: number;
};

// K-factor on a 0-100 scale: a clean upset moves the loser ~ -3, the winner ~ +3.
// We multiply by the goal-difference multiplier (1, 1.5, 1.75, 1.875, ...).
const K_BASE = 6;

function expectedWin(diff: number): number {
  // Logistic on a 14-pt scale (mirrors matchProbability's softmax).
  return 1 / (1 + Math.exp(-diff / 14));
}

function gdMultiplier(gd: number): number {
  const n = Math.abs(gd);
  if (n <= 1) return 1;
  if (n === 2) return 1.5;
  return (11 + n) / 8; // 1.75, 1.875, 2.0 ...
}

export function baseStrength(code: string): number {
  return TEAM_STRENGTH[code]?.strength ?? 50;
}

export function effectiveStrength(code: string, delta: EloDelta): number {
  const base = baseStrength(code);
  const d = delta[code] ?? 0;
  // Cap so a meltdown doesn't push a B-tier below F-tier overnight.
  return Math.max(30, Math.min(100, base + d));
}

// Returns the deltas to APPLY (cumulative) and the per-team before/after
// snapshot for the event log. Does not mutate `delta`.
export function applyResult(
  delta: EloDelta,
  homeCode: string,
  awayCode: string,
  homeGoals: number,
  awayGoals: number,
): { newDelta: EloDelta; event: Omit<EloEvent, "fixtureId" | "date" | "ts"> } {
  const hBefore = effectiveStrength(homeCode, delta);
  const aBefore = effectiveStrength(awayCode, delta);
  const expHome = expectedWin(hBefore - aBefore);
  const actualHome = homeGoals > awayGoals ? 1 : homeGoals < awayGoals ? 0 : 0.5;
  const gd = homeGoals - awayGoals;
  const mult = gdMultiplier(gd);
  const shift = K_BASE * mult * (actualHome - expHome);
  // Symmetric: home gains/loses `shift`, away loses/gains the same.
  const newHome = Math.max(30, Math.min(100, hBefore + shift));
  const newAway = Math.max(30, Math.min(100, aBefore - shift));
  const hDelta = newHome - baseStrength(homeCode);
  const aDelta = newAway - baseStrength(awayCode);
  return {
    newDelta: { ...delta, [homeCode]: hDelta, [awayCode]: aDelta },
    event: {
      homeCode,
      awayCode,
      homeGoals,
      awayGoals,
      homeBefore: hBefore,
      awayBefore: aBefore,
      homeAfter: newHome,
      awayAfter: newAway,
      homeDelta: shift,
      awayDelta: -shift,
    },
  };
}

// Probability of {H,D,A} using effective strengths. Mirrors matchProbability
// in team-strength.ts but takes a delta map to render dynamic numbers.
export function dynamicMatchProbability(
  homeCode: string,
  awayCode: string,
  delta: EloDelta,
  HOME_FIELD_BONUS = 4,
): { H: number; D: number; A: number } {
  const sh = effectiveStrength(homeCode, delta) + HOME_FIELD_BONUS;
  const sa = effectiveStrength(awayCode, delta);
  const diff = sh - sa;
  // Same temperature/draw weight as matchProbability — keep both in sync.
  const T = 40;
  const wH = Math.exp(diff / T);
  const wA = Math.exp(-diff / T);
  const wD = Math.exp(-Math.abs(diff) / T) * 1.05;
  const sum = wH + wD + wA;
  return { H: wH / sum, D: wD / sum, A: wA / sum };
}
