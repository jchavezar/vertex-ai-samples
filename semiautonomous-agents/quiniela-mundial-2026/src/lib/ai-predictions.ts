// Deterministic engine that proposes 1X2 + scoreline picks for every group-stage fixture.
// Pure function over the curated strength table + user's favorites + already-saved picks.

import { allGroupFixtures, type GroupFixture } from "@/data/groups";
import { getStrength, favoriteBoost, HOME_FIELD_BONUS, DRAW_BAND, TEAM_STRENGTH } from "@/data/team-strength";
import { TEAMS_BY_CODE } from "@/data/teams";
import { effectiveStrength, dynamicMatchProbability, type EloDelta } from "@/lib/elo-dynamic";
import type { GroupPrediction, Pick1X2 } from "@/lib/predictions";

export type MarketProbMap = Record<string, { H: number; D: number; A: number }>;

export type ManualScoreOverride = {
  fixtureId: string;
  homeGoals: number;
  awayGoals: number;
};

export type AiProposal = {
  fixtureId: string;
  group: string;
  home: string;
  away: string;
  pick: Pick1X2;
  homeGoals: number;
  awayGoals: number;
  reason: string;
  source: "ai" | "manual-override";
};

export type GenerateInput = {
  favorites: string[];                       // ordered: index 0 = top
  existing: Record<string, GroupPrediction>; // playerId picks already saved
  fillOnlyEmpty: boolean;
  manualScores?: ManualScoreOverride[];      // user-pinned scorelines (override the model)
};

// Map an effective-strength diff (home_effective - away_effective) to a plausible scoreline.
// Always returns goals from the home perspective; caller swaps for an away win.
function scoreFromDiff(absDiff: number, isDraw: boolean): { hi: number; lo: number } {
  if (isDraw) {
    if (absDiff < 2) return { hi: 1, lo: 1 };
    return { hi: 2, lo: 2 };
  }
  if (absDiff < 4) return { hi: 1, lo: 0 };
  if (absDiff < 9) return { hi: 2, lo: 1 };
  if (absDiff < 15) return { hi: 2, lo: 0 };
  if (absDiff < 22) return { hi: 3, lo: 1 };
  if (absDiff < 30) return { hi: 3, lo: 0 };
  return { hi: 4, lo: 0 };
}

function shortName(code: string): string {
  return TEAMS_BY_CODE[code]?.name ?? code;
}

function favTag(code: string, favorites: string[]): string {
  const idx = favorites.indexOf(code);
  if (idx < 0) return "";
  return ` ★fav#${idx + 1}`;
}

export function generateGroupProposals(input: GenerateInput): AiProposal[] {
  const { favorites, existing, fillOnlyEmpty } = input;
  const overrides = new Map<string, ManualScoreOverride>(
    (input.manualScores ?? []).map(o => [o.fixtureId, o])
  );

  const fixtures = allGroupFixtures();
  const out: AiProposal[] = [];

  for (const fx of fixtures) {
    if (fillOnlyEmpty && existing[fx.id]?.pick) continue;

    const override = overrides.get(fx.id);
    if (override) {
      const pick: Pick1X2 = override.homeGoals > override.awayGoals ? "H" : override.homeGoals < override.awayGoals ? "A" : "D";
      out.push({
        fixtureId: fx.id,
        group: fx.group,
        home: fx.home,
        away: fx.away,
        pick,
        homeGoals: override.homeGoals,
        awayGoals: override.awayGoals,
        reason: `marcador pineado por usuario (${override.homeGoals}-${override.awayGoals})`,
        source: "manual-override",
      });
      continue;
    }

    out.push(modelPick(fx, favorites));
  }

  return out;
}

function modelPick(fx: GroupFixture, favorites: string[]): AiProposal {
  const sH = getStrength(fx.home)?.strength ?? 50;
  const sA = getStrength(fx.away)?.strength ?? 50;
  const fH = favoriteBoost(fx.home, favorites);
  const fA = favoriteBoost(fx.away, favorites);
  const effH = sH + HOME_FIELD_BONUS + fH;
  const effA = sA + fA;
  const diff = effH - effA;
  const absDiff = Math.abs(diff);
  const isDraw = absDiff < DRAW_BAND;

  let pick: Pick1X2;
  let homeGoals: number;
  let awayGoals: number;

  const { hi, lo } = scoreFromDiff(absDiff, isDraw);
  if (isDraw) {
    pick = "D";
    homeGoals = hi;
    awayGoals = lo;
  } else if (diff > 0) {
    pick = "H";
    homeGoals = hi;
    awayGoals = lo;
  } else {
    pick = "A";
    homeGoals = lo;
    awayGoals = hi;
  }

  const reason = buildReason(fx, sH, sA, fH, fA, diff, pick, favorites);
  return {
    fixtureId: fx.id,
    group: fx.group,
    home: fx.home,
    away: fx.away,
    pick,
    homeGoals,
    awayGoals,
    reason,
    source: "ai",
  };
}

function buildReason(
  fx: GroupFixture,
  sH: number,
  sA: number,
  fH: number,
  fA: number,
  diff: number,
  pick: Pick1X2,
  favorites: string[],
): string {
  const tierH = TEAM_STRENGTH[fx.home]?.tier ?? "?";
  const tierA = TEAM_STRENGTH[fx.away]?.tier ?? "?";
  const homeLabel = `${shortName(fx.home)} (${tierH}, ${sH}${favTag(fx.home, favorites)})`;
  const awayLabel = `${shortName(fx.away)} (${tierA}, ${sA}${favTag(fx.away, favorites)})`;
  const homeBonus = `+${HOME_FIELD_BONUS} local`;
  const favNote = (fH || fA)
    ? ` · favs boost ${fH ? `+${fH} H` : ""}${fH && fA ? " / " : ""}${fA ? `+${fA} A` : ""}`
    : "";
  const verdict =
    pick === "D" ? `empate (diff ${diff.toFixed(0)} dentro de ±${DRAW_BAND})`
    : pick === "H" ? `gana ${shortName(fx.home)} (diff +${diff.toFixed(0)})`
    : `gana ${shortName(fx.away)} (diff ${diff.toFixed(0)})`;
  return `${homeLabel} vs ${awayLabel} · ${homeBonus}${favNote} → ${verdict}`;
}

export function applyManualScoreOverrides(
  proposals: AiProposal[],
  overrides: ManualScoreOverride[],
): AiProposal[] {
  if (!overrides.length) return proposals;
  const byId = new Map(overrides.map(o => [o.fixtureId, o]));
  return proposals.map(p => {
    const o = byId.get(p.fixtureId);
    if (!o) return p;
    const pick: Pick1X2 = o.homeGoals > o.awayGoals ? "H" : o.homeGoals < o.awayGoals ? "A" : "D";
    return {
      ...p,
      pick,
      homeGoals: o.homeGoals,
      awayGoals: o.awayGoals,
      reason: `marcador pineado por usuario (${o.homeGoals}-${o.awayGoals})`,
      source: "manual-override",
    };
  });
}

// Bot picks for the virtual "AI" player. Driven by:
//   1) the dynamic effective strength (base + ELO delta from past results), and
//   2) — if provided — the day's vig-stripped market odds, blended at MARKET_WEIGHT.
// Returns one proposal per fixture (caller filters out locked/finished ones).
const MARKET_WEIGHT = 0.5;

export function generateAiBotPicks(delta: EloDelta, market: MarketProbMap = {}): AiProposal[] {
  const fixtures = allGroupFixtures();
  return fixtures.map(fx => modelPickWithDelta(fx, delta, market[fx.id]));
}

function modelPickWithDelta(
  fx: GroupFixture,
  delta: EloDelta,
  market?: { H: number; D: number; A: number },
): AiProposal {
  const sH = effectiveStrength(fx.home, delta);
  const sA = effectiveStrength(fx.away, delta);
  const modelProb = dynamicMatchProbability(fx.home, fx.away, delta);
  const probs = market
    ? {
        H: (1 - MARKET_WEIGHT) * modelProb.H + MARKET_WEIGHT * market.H,
        D: (1 - MARKET_WEIGHT) * modelProb.D + MARKET_WEIGHT * market.D,
        A: (1 - MARKET_WEIGHT) * modelProb.A + MARKET_WEIGHT * market.A,
      }
    : modelProb;

  const diff = (sH + HOME_FIELD_BONUS) - sA;
  const absDiff = Math.abs(diff);

  // Pick the outcome with the highest blended probability; if H/A is the winner
  // but its margin over D is razor thin, fall back to a draw to match the
  // curated strength table's DRAW_BAND behavior on tight games.
  let pick: Pick1X2 = probs.H >= probs.A && probs.H >= probs.D ? "H"
    : probs.A >= probs.H && probs.A >= probs.D ? "A"
    : "D";
  if (pick !== "D" && Math.abs(diff) < DRAW_BAND && Math.abs((pick === "H" ? probs.H : probs.A) - probs.D) < 0.05) {
    pick = "D";
  }

  const isDraw = pick === "D";
  const { hi, lo } = scoreFromDiff(absDiff, isDraw);
  let homeGoals: number;
  let awayGoals: number;
  if (isDraw) { homeGoals = hi; awayGoals = lo; }
  else if (pick === "H") { homeGoals = hi; awayGoals = lo; }
  else { homeGoals = lo; awayGoals = hi; }

  const pct = (p: number) => `${Math.round(p * 100)}%`;
  const mktNote = market ? ` · mkt H/D/A ${pct(market.H)}/${pct(market.D)}/${pct(market.A)}` : "";
  const reason = `${shortName(fx.home)} (${sH.toFixed(0)}) vs ${shortName(fx.away)} (${sA.toFixed(0)}) · +${HOME_FIELD_BONUS} local · model H/D/A ${pct(modelProb.H)}/${pct(modelProb.D)}/${pct(modelProb.A)}${mktNote} → ${pick === "D" ? "empate" : pick === "H" ? `gana ${shortName(fx.home)}` : `gana ${shortName(fx.away)}`}`;

  return {
    fixtureId: fx.id,
    group: fx.group,
    home: fx.home,
    away: fx.away,
    pick,
    homeGoals,
    awayGoals,
    reason,
    source: "ai",
  };
}

// Helper used by the agent to format the proposal list as a compact markdown bullet list.
export function renderProposalsMarkdown(proposals: AiProposal[]): string {
  // Group by group letter so the bot can render in tournament order.
  const byGroup = new Map<string, AiProposal[]>();
  for (const p of proposals) {
    if (!byGroup.has(p.group)) byGroup.set(p.group, []);
    byGroup.get(p.group)!.push(p);
  }
  const lines: string[] = [];
  for (const [g, items] of Array.from(byGroup.entries()).sort()) {
    lines.push(`**Grupo ${g}**`);
    for (const p of items) {
      const pickLabel = p.pick === "H" ? p.home : p.pick === "A" ? p.away : "Empate";
      lines.push(`- \`${p.fixtureId}\` ${p.home} vs ${p.away} → **${pickLabel}** (${p.homeGoals}-${p.awayGoals})`);
    }
  }
  return lines.join("\n");
}
