// Pure probability blender for the Mundial 2026 quiniela.
//
// Combines three signals (in priority order):
//   1. Implied vig-stripped market odds (ESPN). Most informed signal when present.
//   2. Effective ELO from `elo-dynamic.ts` (curated baseline + result-driven delta).
//   3. Recent form (W/D/L of last 5) — derived from finished group fixtures.
//
// Returns {H, D, A} that sum to 1. Used by:
//   - /api/probabilities (per-fixture probs surfaced to the UI)
//   - /api/probabilities/bracket (Monte Carlo bracket sims)
//   - /api/ai/sync (input to Gemini reasoner)
//
// IMPORTANT: this function is pure — it never reads "future" data. Callers
// must only pass results from fixtures that have already finished and odds
// snapshots from BEFORE the kickoff of the fixture being scored.
import type { GroupFixture } from "@/data/groups";
import {
  dynamicMatchProbability,
  effectiveStrength,
  type EloDelta,
} from "@/lib/elo-dynamic";
import { HOME_FIELD_BONUS } from "@/data/team-strength";

export type Probs = { H: number; D: number; A: number };

export type FormSummary = {
  // Last-5 outcomes from team's perspective (most recent first).
  // W = 1, D = 0.5, L = 0. Empty if no finished games.
  scores: number[];
  // xG data from ESPN summaries — present when available, absent pre-tournament.
  xgFor?: number[];      // Expected goals generated per match
  xgAgainst?: number[];  // Expected goals conceded per match
};

export type FixtureSignals = {
  fixture: GroupFixture;
  delta: EloDelta;
  market?: Probs;                  // vig-stripped from ESPN, optional
  homeForm?: FormSummary;
  awayForm?: FormSummary;
  // host country boost. The 2026 tournament is co-hosted; only MEX/USA/CAN get
  // a real home-crowd bonus and only when the fixture is in their country.
  homeHostBoost?: boolean;         // true => +small bonus on home prob
};

export type BlendResult = {
  probs: Probs;
  components: {
    model: Probs;
    market: Probs | null;
    formAdjustment: number;        // signed: +ve favors home
    hostAdjustment: number;        // signed: +ve favors home
  };
  weights: { market: number; model: number; form: number };
  source: "blend-v2";
};

// Map form into an additive strength shift on the 0-100 ELO scale.
// Prefers xG differential when available (more predictive than W/D/L).
// xG diff per game typically ranges -2.5 to +2.5; scaled by 2.5 → ±6 pts max.
// W/D/L fallback: 3W-2L vs 2W-3L gives ~±2 pts. Capped at ±5.
function formStrengthShift(home?: FormSummary, away?: FormSummary): number {
  const xgDiff = (f?: FormSummary): number | null => {
    if (!f?.xgFor?.length || !f?.xgAgainst?.length) return null;
    const avgFor = f.xgFor.reduce((a, b) => a + b, 0) / f.xgFor.length;
    const avgAgainst = f.xgAgainst.reduce((a, b) => a + b, 0) / f.xgAgainst.length;
    return avgFor - avgAgainst;
  };

  const hDiff = xgDiff(home);
  const aDiff = xgDiff(away);

  if (hDiff !== null || aDiff !== null) {
    const hv = hDiff ?? 0;
    const av = aDiff ?? 0;
    return Math.max(-5, Math.min(5, (hv - av) * 2.5));
  }

  // Fallback: W/D/L average
  const avg = (f?: FormSummary): number | null => {
    if (!f || f.scores.length === 0) return null;
    return f.scores.reduce((a, b) => a + b, 0) / f.scores.length;
  };
  const h = avg(home);
  const a = avg(away);
  if (h == null && a == null) return 0;
  return Math.max(-4, Math.min(4, ((h ?? 0.5) - (a ?? 0.5)) * 8));
}

// Renormalize {H,D,A} so they sum to 1 and are non-negative.
function normalize(p: Probs): Probs {
  const H = Math.max(0, p.H);
  const D = Math.max(0, p.D);
  const A = Math.max(0, p.A);
  const s = H + D + A;
  if (s <= 0) return { H: 1 / 3, D: 1 / 3, A: 1 / 3 };
  return { H: H / s, D: D / s, A: A / s };
}

const W_MARKET_BASE = 0.55;
const W_MODEL_BASE = 0.30;
const W_FORM_BASE = 0.15;

// Constants for the host-country crowd advantage. The base ELO model already
// has a +4 home-field bonus that applies to every fixture (since fixtures are
// declared with a "home" team). The additional host bonus reflects the *real*
// home-crowd advantage that only applies when MEX/USA/CAN plays in its own country.
const HOST_PROB_SHIFT = 0.04;

export function blendFixtureProbs(sig: FixtureSignals): BlendResult {
  // 1) Model: dynamic ELO with HOME_FIELD_BONUS already baked in.
  const baseModel = dynamicMatchProbability(sig.fixture.home, sig.fixture.away, sig.delta);

  // 2) Form: convert into a strength shift, then bake it into a SECOND model
  //    pass so the H/D/A redistribution respects the same temperature/draw
  //    band as the curated softmax (rather than naively scaling H/A).
  const formShift = formStrengthShift(sig.homeForm, sig.awayForm);
  let formModel = baseModel;
  if (formShift !== 0) {
    const sh = effectiveStrength(sig.fixture.home, sig.delta) + HOME_FIELD_BONUS + formShift;
    const sa = effectiveStrength(sig.fixture.away, sig.delta);
    const diff = sh - sa;
    const T = 40;
    const wH = Math.exp(diff / T);
    const wA = Math.exp(-diff / T);
    const wD = Math.exp(-Math.abs(diff) / T) * 1.05;
    const s = wH + wD + wA;
    formModel = { H: wH / s, D: wD / s, A: wA / s };
  }

  // 3) Blend market + model + form-adjusted-model. If market is absent the
  //    model+form share absorbs the missing weight pro-rata.
  let wMarket = sig.market ? W_MARKET_BASE : 0;
  let wModel = W_MODEL_BASE + (sig.market ? 0 : W_MARKET_BASE * (W_MODEL_BASE / (W_MODEL_BASE + W_FORM_BASE)));
  let wForm = W_FORM_BASE + (sig.market ? 0 : W_MARKET_BASE * (W_FORM_BASE / (W_MODEL_BASE + W_FORM_BASE)));
  const wSum = wMarket + wModel + wForm;
  wMarket /= wSum; wModel /= wSum; wForm /= wSum;

  const blended: Probs = {
    H: (sig.market ? wMarket * sig.market.H : 0) + wModel * baseModel.H + wForm * formModel.H,
    D: (sig.market ? wMarket * sig.market.D : 0) + wModel * baseModel.D + wForm * formModel.D,
    A: (sig.market ? wMarket * sig.market.A : 0) + wModel * baseModel.A + wForm * formModel.A,
  };

  // 4) Host-country boost: shift mass from A → H. Draw share stays put.
  let hostAdj = 0;
  if (sig.homeHostBoost) {
    const shift = Math.min(HOST_PROB_SHIFT, blended.A);
    blended.H += shift;
    blended.A -= shift;
    hostAdj = shift;
  }

  const probs = normalize(blended);

  return {
    probs,
    components: {
      model: baseModel,
      market: sig.market ?? null,
      formAdjustment: formShift,
      hostAdjustment: hostAdj,
    },
    weights: { market: wMarket, model: wModel, form: wForm },
    source: "blend-v2",
  };
}

// Convenience builder: turn a list of finished matches for a team into a
// FormSummary of its last `n` outcomes (most recent first).
export type FinishedMatch = {
  date: string;            // YYYY-MM-DD
  homeCode: string;
  awayCode: string;
  homeGoals: number;
  awayGoals: number;
  homeXg?: number;         // ESPN expectedGoals for the home side
  awayXg?: number;         // ESPN expectedGoals for the away side
};

export function buildFormSummary(
  teamCode: string,
  finished: FinishedMatch[],
  n = 5,
): FormSummary {
  const mine = finished
    .filter(m => m.homeCode === teamCode || m.awayCode === teamCode)
    .sort((a, b) => (a.date < b.date ? 1 : -1))
    .slice(0, n);

  const scores = mine.map(m => {
    const isHome = m.homeCode === teamCode;
    const my = isHome ? m.homeGoals : m.awayGoals;
    const ot = isHome ? m.awayGoals : m.homeGoals;
    if (my > ot) return 1;
    if (my < ot) return 0;
    return 0.5;
  });

  const xgFor: number[] = [];
  const xgAgainst: number[] = [];
  for (const m of mine) {
    const isHome = m.homeCode === teamCode;
    const myXg = isHome ? m.homeXg : m.awayXg;
    const oppXg = isHome ? m.awayXg : m.homeXg;
    if (myXg != null && oppXg != null) {
      xgFor.push(myXg);
      xgAgainst.push(oppXg);
    }
  }

  return {
    scores,
    ...(xgFor.length > 0 ? { xgFor, xgAgainst } : {}),
  };
}
