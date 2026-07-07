// Shared builder: computes blended {H, D, A} probabilities for every group
// fixture, using the current Firestore state + latest ESPN scoreboard.
// Used by /api/probabilities, /api/cron/ai-refresh, and /api/ai/sync so all
// three see exactly the same numbers.

import { allGroupFixtures } from "@/data/groups";
import {
  blendFixtureProbs,
  buildFormSummary,
  type FinishedMatch,
  type Probs,
} from "@/lib/probability-engine";
import { fetchScoreboard, groupStageRange, normalizeAbbr, extractMarketProb, type EspnEvent } from "@/lib/espn";
import { getAiState, getMarketOdds, setMarketOdds, type MarketOddsDoc } from "@/lib/ai-state-server";
import { isHomeNationAtHome } from "@/lib/host-country";
import type { FixtureProbsEntry } from "@/lib/probability-snapshots";

// ── ESPN summary types (xG extraction via leaders[]) ─────────────────────────
// xG lives in summary.leaders[i].leaders[0].leaders[0].statistics[], NOT boxscore.
type EspnLeaderStat = { name?: string; value?: number };
type EspnLeaderEntry = { statistics?: EspnLeaderStat[] };
type EspnLeaderGroup = { leaders?: EspnLeaderEntry[] };
type EspnTeamLeader = { team?: { abbreviation?: string }; leaders?: EspnLeaderGroup[] };
type EspnSummaryBox = { leaders?: EspnTeamLeader[] };

const _summaryCache = new Map<string, EspnSummaryBox | null>();

async function fetchSummaryBox(eventId: string): Promise<EspnSummaryBox | null> {
  if (_summaryCache.has(eventId)) return _summaryCache.get(eventId)!;
  try {
    const url = `https://site.api.espn.com/apis/site/v2/sports/soccer/fifa.world/summary?event=${encodeURIComponent(eventId)}`;
    const res = await fetch(url, { cache: "no-store" });
    if (!res.ok) {
      console.warn(`[xG-fetch] event=${eventId} status=${res.status}`);
      _summaryCache.set(eventId, null); return null;
    }
    const data = (await res.json()) as EspnSummaryBox;
    const leadersCount = data?.leaders?.length ?? 0;
    console.log(`[xG-fetch] event=${eventId} ok leaders=${leadersCount}`);
    _summaryCache.set(eventId, data);
    return data;
  } catch (e) {
    console.error(`[xG-fetch] event=${eventId} error:`, e);
    _summaryCache.set(eventId, null); return null;
  }
}

function extractXgFromSummary(
  summary: EspnSummaryBox | null,
  _espnHomeTeamId: string,
  espnHomeAbbr: string,
): { homeXg: number; awayXg: number } | null {
  // ESPN xG path: summary.leaders[i] → team.abbreviation identifies home/away
  // → leaders[0].leaders[0].statistics[] → name === "expectedGoals"
  const teamLeaders = summary?.leaders;
  if (!teamLeaders?.length) return null;

  const getTeamXg = (abbr: string): number | null => {
    const entry = teamLeaders.find(tl =>
      tl.team?.abbreviation?.toUpperCase() === abbr.toUpperCase(),
    );
    if (!entry) return null;
    const stats = entry.leaders?.[0]?.leaders?.[0]?.statistics ?? [];
    const xgStat = stats.find(s => s.name === "expectedGoals");
    return xgStat?.value != null ? Number(xgStat.value) : null;
  };

  // Determine away abbreviation: the other entry in leaders[]
  const awayEntry = teamLeaders.find(tl =>
    tl.team?.abbreviation?.toUpperCase() !== espnHomeAbbr.toUpperCase(),
  );
  const espnAwayAbbr = awayEntry?.team?.abbreviation ?? "";

  const hXg = getTeamXg(espnHomeAbbr);
  const aXg = getTeamXg(espnAwayAbbr);
  if (hXg == null || aXg == null) return null;
  return { homeXg: hXg, awayXg: aXg };
}

export type BuiltProbs = {
  byFixture: Record<string, FixtureProbsEntry>;
  // Convenience map for downstream consumers that just need {H,D,A}.
  probsMap: Record<string, Probs>;
  marketUpdates: number;
  ingestedFinals: number;
};

/**
 * Build the full per-fixture probability map.
 *
 * Side effects:
 *   - Persists fresh ESPN market odds into Firestore via setMarketOdds (so
 *     they survive the moment ESPN drops the odds object on kickoff).
 *   - Does NOT update the ELO delta or AI picks; that's the job of /api/ai/sync.
 */
export async function buildAllFixtureProbs(): Promise<BuiltProbs> {
  const fixtures = allGroupFixtures();
  const state = await getAiState();
  const delta = state.delta;

  // Pull fresh ESPN scoreboard (best-effort).
  const sb = await fetchScoreboard(groupStageRange(), "fifa.world").catch(() => null);
  const espnEvents: EspnEvent[] = sb?.events ?? [];

  // Index our fixtures by date-pair for quick mapping.
  const fxByPair = new Map<string, typeof fixtures[number]>();
  for (const fx of fixtures) {
    fxByPair.set(`${fx.home}-${fx.away}-${fx.date}`, fx);
    fxByPair.set(`${fx.away}-${fx.home}-${fx.date}`, fx);
  }

  // Start from whatever market odds we already saved (carry-forward), then
  // overwrite with anything fresher from ESPN.
  const marketDoc: MarketOddsDoc = (await getMarketOdds()) ?? { fixtures: {}, updatedAt: 0 };
  const market: Record<string, Probs> = {};
  for (const [k, v] of Object.entries(marketDoc.fixtures)) {
    market[k] = { H: v.H, D: v.D, A: v.A };
  }

  // Collect finished matches for form computation, indexed by team code.
  const finished: FinishedMatch[] = [];

  // Collect ESPN event IDs for finished games so we can fetch xG in parallel.
  type PendingFinished = {
    espnEventId: string;
    espnHomeTeamId: string;
    espnHomeAbbr: string;
    ourHomeIsEspnHome: boolean;
    fx: typeof fixtures[number];
    homeGoals: number;
    awayGoals: number;
  };
  const pendingFinished: PendingFinished[] = [];

  let marketUpdates = 0;
  for (const e of espnEvents) {
    const c = e.competitions[0];
    const h = c.competitors.find(cp => cp.homeAway === "home");
    const a = c.competitors.find(cp => cp.homeAway === "away");
    if (!h || !a) continue;
    const hCode = normalizeAbbr(h.team.abbreviation);
    const aCode = normalizeAbbr(a.team.abbreviation);
    const date = e.date.slice(0, 10);
    const fx = fxByPair.get(`${hCode}-${aCode}-${date}`);
    if (!fx) continue;

    // Market odds (only meaningful pre-kickoff and during live; we treat the
    // first non-null snapshot as gospel for that fixture).
    const espnProb = extractMarketProb(c.odds?.[0]);
    if (espnProb) {
      const ourHomeIsEspnHome = fx.home === hCode;
      const ourProb = ourHomeIsEspnHome ? espnProb : { H: espnProb.A, D: espnProb.D, A: espnProb.H };
      const prev = market[fx.id];
      const changed = !prev || Math.abs(prev.H - ourProb.H) > 0.005 || Math.abs(prev.A - ourProb.A) > 0.005;
      if (changed) {
        market[fx.id] = ourProb;
        marketDoc.fixtures[fx.id] = { ...ourProb, updatedAt: Date.now() };
        marketUpdates += 1;
      }
    }

    // Finals → queue for xG fetch + form input.
    if (e.status.type.state === "post") {
      const hg = Number(h.score);
      const ag = Number(a.score);
      if (Number.isFinite(hg) && Number.isFinite(ag)) {
        const ourHomeIsEspnHome = fx.home === hCode;
        const homeGoals = ourHomeIsEspnHome ? hg : ag;
        const awayGoals = ourHomeIsEspnHome ? ag : hg;
        pendingFinished.push({
          espnEventId: e.id,
          espnHomeTeamId: h.team.id ?? "",
          espnHomeAbbr: h.team.abbreviation ?? "",
          ourHomeIsEspnHome,
          fx,
          homeGoals,
          awayGoals,
        });
      }
    }
  }

  // Fetch summaries for all finished games in parallel to get xG data.
  const summaries = await Promise.all(
    pendingFinished.map(p => fetchSummaryBox(p.espnEventId)),
  );

  for (let i = 0; i < pendingFinished.length; i++) {
    const p = pendingFinished[i];
    const xg = extractXgFromSummary(summaries[i], p.espnHomeTeamId, p.espnHomeAbbr);
    // Orient xG to OUR home/away convention (ESPN home may differ).
    const homeXg = xg ? (p.ourHomeIsEspnHome ? xg.homeXg : xg.awayXg) : undefined;
    const awayXg = xg ? (p.ourHomeIsEspnHome ? xg.awayXg : xg.homeXg) : undefined;
    console.log(`[xG] ${p.fx.home} vs ${p.fx.away} (homeAbbr=${p.espnHomeAbbr}): homeXg=${homeXg ?? "n/a"} awayXg=${awayXg ?? "n/a"} (raw=${JSON.stringify(xg)})`);
    finished.push({
      date: p.fx.date,
      homeCode: p.fx.home,
      awayCode: p.fx.away,
      homeGoals: p.homeGoals,
      awayGoals: p.awayGoals,
      ...(homeXg != null && awayXg != null ? { homeXg, awayXg } : {}),
    });
  }

  if (marketUpdates > 0) {
    marketDoc.updatedAt = Date.now();
    await setMarketOdds(marketDoc);
  }

  // Index finished matches by fixture key so we can look up xG per fixture.
  const finishedByKey = new Map<string, FinishedMatch>();
  for (const fm of finished) {
    finishedByKey.set(`${fm.homeCode}-${fm.awayCode}`, fm);
    finishedByKey.set(`${fm.awayCode}-${fm.homeCode}`, fm);
  }

  // Build per-team form summaries from the finished matches (best-effort —
  // empty when we're still pre-tournament, which is the dominant case for
  // the first matchday).
  const byFixture: Record<string, FixtureProbsEntry> = {};
  const probsMap: Record<string, Probs> = {};

  for (const fx of fixtures) {
    const homeForm = buildFormSummary(fx.home, finished, 5);
    const awayForm = buildFormSummary(fx.away, finished, 5);
    const homeHostBoost = isHomeNationAtHome(fx.home, fx.city);
    const mkt = market[fx.id];
    const blend = blendFixtureProbs({
      fixture: fx,
      delta,
      market: mkt,
      homeForm,
      awayForm,
      homeHostBoost,
    });
    const fm = finishedByKey.get(`${fx.home}-${fx.away}`);
    byFixture[fx.id] = {
      fixtureId: fx.id,
      home: fx.home,
      away: fx.away,
      date: fx.date,
      probs: blend.probs,
      market: mkt ?? null,
      ...(fm?.homeXg != null && fm?.awayXg != null
        ? { homeXg: fm.homeXg, awayXg: fm.awayXg }
        : {}),
      components: {
        model: blend.components.model,
        formAdjustment: blend.components.formAdjustment,
        hostAdjustment: blend.components.hostAdjustment,
      },
    };
    probsMap[fx.id] = blend.probs;
  }

  return {
    byFixture,
    probsMap,
    marketUpdates,
    ingestedFinals: finished.length,
  };
}
