// POST /api/ai/sync
//
// Single source of truth for the AI bot's picks. On every call:
//   1) Ingests finished ESPN group-stage results into the per-team ELO delta
//      (and persists the event log).
//   2) Snapshots fresh market odds from ESPN (carry-forward when absent).
//   3) Rebuilds blended {H, D, A} probabilities for every fixture via
//      `buildAllFixtureProbs` + persists them as the daily snapshot.
//   4) For every fixture NOT yet locked at kickoff, runs the Gemini reasoner
//      and persists pick + reasoning + confidence under the `ai` player.
//
// Anti-cheat: the AI never sees future data. Steps 1 & 2 read live ESPN, but
// only fixtures with `state==="post"` contribute to ELO and only non-locked
// fixtures are re-picked. The server-side lock in `predictions-server.ts`
// is the ultimate guarantee.
//
// Idempotent: ingested fixture IDs are tracked in `ai_state`; finished
// fixtures' picks are preserved as-is once locked.

import { NextResponse } from "next/server";
import { allGroupFixtures } from "@/data/groups";
import {
  fetchScoreboard,
  groupStageRange,
  normalizeAbbr,
  type EspnEvent,
} from "@/lib/espn";
import { applyResult, effectiveStrength, dynamicMatchProbability, type EloEvent } from "@/lib/elo-dynamic";
import {
  appendEvent,
  appendPickSnapshot,
  getAiState,
  getInitialProbs,
  setAiState,
  setInitialProbs,
  type AiPickSnapshot,
  type InitialProbsDoc,
} from "@/lib/ai-state-server";
import { upsertPicks, getPicks } from "@/lib/predictions-server";
import { AI_PLAYER_ID } from "@/data/players";
import { TEAMS } from "@/data/teams";
import type {
  GroupPrediction,
  PlayerPredictions,
  Pick1X2,
} from "@/lib/predictions";
import { isFixtureLocked } from "@/lib/fixture-time";
import { currentChampionLockRound } from "@/data/tournament";
import { buildAllFixtureProbs } from "@/lib/probabilities-builder";
import { writeFixtureProbs } from "@/lib/probability-snapshots";
import { reasonPick } from "@/lib/ai-reasoner";
import { buildFormSummary, type FinishedMatch } from "@/lib/probability-engine";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";
export const maxDuration = 300;

const REASONER_CONCURRENCY = 4;

function scoreFromOutcome(pick: Pick1X2, blended: { H: number; D: number; A: number }): { homeGoals: number; awayGoals: number } {
  // Map confidence → goals. Wider blended margin → bigger projected score.
  const fav = pick === "H" ? blended.H : pick === "A" ? blended.A : blended.D;
  const dog = pick === "H" ? blended.A : pick === "A" ? blended.H : 0;
  const margin = pick === "D" ? 0 : Math.max(0, fav - dog);
  if (pick === "D") {
    if (fav > 0.30) return { homeGoals: 1, awayGoals: 1 };
    return { homeGoals: 0, awayGoals: 0 };
  }
  let hi = 1, lo = 0;
  if (margin > 0.10) hi = 2;
  if (margin > 0.30) { hi = 2; lo = 0; }
  if (margin > 0.45) { hi = 3; lo = 1; }
  if (margin > 0.60) { hi = 3; lo = 0; }
  return pick === "H" ? { homeGoals: hi, awayGoals: lo } : { homeGoals: lo, awayGoals: hi };
}

async function runReasonersConcurrent<T>(items: T[], worker: (t: T) => Promise<void>, concurrency: number): Promise<void> {
  let idx = 0;
  const lanes: Promise<void>[] = [];
  for (let i = 0; i < concurrency; i++) {
    lanes.push((async () => {
      while (true) {
        const my = idx++;
        if (my >= items.length) return;
        try { await worker(items[my]); } catch (e) { console.warn("[ai/sync worker]", e); }
      }
    })());
  }
  await Promise.all(lanes);
}

export async function POST() {
  try {
    const fixtures = allGroupFixtures();
    const now = Date.now();

    // 1) Seed initial-probability snapshot once.
    let initial = await getInitialProbs();
    if (!initial) {
      const seed: InitialProbsDoc = { fixtures: {}, createdAt: now };
      for (const fx of fixtures) {
        seed.fixtures[fx.id] = dynamicMatchProbability(fx.home, fx.away, {});
      }
      await setInitialProbs(seed);
      initial = seed;
    }

    // 2) Pull ESPN scoreboard & ingest any newly-finished match into ELO delta.
    const sb = await fetchScoreboard(groupStageRange(), "fifa.world").catch(() => null);
    const espnEvents: EspnEvent[] = sb?.events ?? [];
    const fxByPair = new Map<string, typeof fixtures[number]>();
    for (const fx of fixtures) {
      fxByPair.set(`${fx.home}-${fx.away}-${fx.date}`, fx);
      fxByPair.set(`${fx.away}-${fx.home}-${fx.date}`, fx);
    }

    const state = await getAiState();
    const ingested = new Set(state.ingestedFixtures);
    let delta = state.delta;
    const newEvents: EloEvent[] = [];
    const finishedAll: FinishedMatch[] = [];

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
      if (e.status.type.state !== "post") continue;
      const hg = Number(h.score);
      const ag = Number(a.score);
      if (!Number.isFinite(hg) || !Number.isFinite(ag)) continue;
      const ourHomeIsEspnHome = fx.home === hCode;
      const homeGoals = ourHomeIsEspnHome ? hg : ag;
      const awayGoals = ourHomeIsEspnHome ? ag : hg;
      finishedAll.push({ date: fx.date, homeCode: fx.home, awayCode: fx.away, homeGoals, awayGoals });
      if (ingested.has(fx.id)) continue;
      const { newDelta, event } = applyResult(delta, fx.home, fx.away, homeGoals, awayGoals);
      delta = newDelta;
      const evt: EloEvent = { ...event, fixtureId: fx.id, date: fx.date, ts: now };
      newEvents.push(evt);
      await appendEvent(evt);
      ingested.add(fx.id);
    }

    await setAiState({
      delta,
      ingestedFixtures: Array.from(ingested),
      lastSyncAt: now,
    });

    // 3) Build per-fixture probabilities (also persists market odds + snapshot).
    const built = await buildAllFixtureProbs();
    await writeFixtureProbs({ fixtures: built.byFixture, source: "blend-v2" });

    // 4) For every non-locked fixture, run the Gemini reasoner. Locked-but-already-
    //    picked fixtures keep their stored pick (it counted as the bot's commit).
    const prevPayload = (await getPicks(AI_PLAYER_ID)) as Partial<PlayerPredictions> | null;
    const prevGroup = prevPayload?.group ?? {};
    const group: Record<string, GroupPrediction> = {};
    const targets: typeof fixtures = [];
    for (const fx of fixtures) {
      const prev = prevGroup[fx.id];
      const locked = isFixtureLocked(fx, now);
      if (locked) {
        if (prev) group[fx.id] = prev;
        continue;
      }
      targets.push(fx);
    }

    let reasonerSuccesses = 0;
    let reasonerFallbacks = 0;
    let snapshotsThisRun = 0;

    await runReasonersConcurrent(targets, async (fx) => {
      const entry = built.byFixture[fx.id];
      if (!entry) return;
      const homeForm = buildFormSummary(fx.home, finishedAll, 5);
      const awayForm = buildFormSummary(fx.away, finishedAll, 5);
      const matchday: 1 | 2 | 3 = fx.matchday;
      const r = await reasonPick({
        fixture: fx,
        modelProbs: entry.components?.model ?? entry.probs,
        blendedProbs: entry.probs,
        marketProbs: entry.market,
        homeFormScores: homeForm.scores,
        awayFormScores: awayForm.scores,
        matchday,
        previousReasoning: prevGroup[fx.id]?.reasoning,
      });
      if (r.fallback) reasonerFallbacks += 1; else reasonerSuccesses += 1;
      const { homeGoals, awayGoals } = scoreFromOutcome(r.pick, entry.probs);

      // History snapshot — only when there's something MEANINGFUL to record.
      // Same pick + same scoreline = pure reasoning/confidence churn, that's
      // noise. Initial (no prior) and any change (pick or scoreline) count.
      const prev = prevGroup[fx.id];
      const pickChanged = !prev || prev.pick !== r.pick;
      const scoreChanged = !prev
        || prev.homeGoals !== homeGoals
        || prev.awayGoals !== awayGoals;
      if (!prev || pickChanged || scoreChanged) {
        const snap: AiPickSnapshot = {
          fixtureId: fx.id,
          ts: now,
          pick: r.pick,
          homeGoals,
          awayGoals,
          confidence: r.confidence,
          reasoning: r.reasoning,
          prevPick: (prev?.pick as "H" | "D" | "A" | undefined) ?? null,
          prevReasoning: prev?.reasoning ?? null,
          source: prev ? "sync" : "initial",
          blendedProbs: { H: entry.probs.H, D: entry.probs.D, A: entry.probs.A },
          reasonerModel: r.model,
        };
        try {
          await appendPickSnapshot(snap);
          snapshotsThisRun += 1;
        } catch (e) {
          console.warn("[ai/sync] snapshot append failed", fx.id, (e as Error).message);
        }
      }

      group[fx.id] = {
        pick: r.pick,
        homeGoals,
        awayGoals,
        source: "ai",
        aiAt: now,
        reasoning: r.reasoning,
        confidence: r.confidence,
        reasonerModel: r.model,
      };
    }, REASONER_CONCURRENCY);

    // 5) Champion + runner-up by effective strength (unchanged behavior).
    const lockRound = currentChampionLockRound(new Date(now));
    const prevChampion = prevPayload?.champion;
    const prevRunnerUp = prevPayload?.runnerUp;
    const prevChampLock = prevPayload?.championLockedAt;
    const prevRunLock = prevPayload?.runnerUpLockedAt;
    const ranked = TEAMS
      .map(t => ({ code: t.code, eff: effectiveStrength(t.code, delta) }))
      .sort((a, b) => b.eff - a.eff);
    const aiChampion = ranked[0]?.code ?? prevChampion;
    const aiRunnerUp = ranked.find(t => t.code !== aiChampion)?.code ?? prevRunnerUp;
    const freezeChampion = prevChampion && prevChampLock && prevChampLock !== "PRE";
    const freezeRunnerUp = prevRunnerUp && prevRunLock && prevRunLock !== "PRE";
    const champion = freezeChampion ? prevChampion : aiChampion;
    const runnerUp = freezeRunnerUp ? prevRunnerUp : aiRunnerUp;
    const championLockedAt = freezeChampion ? prevChampLock : lockRound;
    const runnerUpLockedAt = freezeRunnerUp ? prevRunLock : lockRound;

    await upsertPicks(AI_PLAYER_ID, {
      playerId: AI_PLAYER_ID,
      group,
      bracket: prevPayload?.bracket ?? {},
      champion,
      runnerUp,
      championLockedAt,
      runnerUpLockedAt,
      updatedAt: now,
    });

    return NextResponse.json({
      ok: true,
      ingestedThisRun: newEvents.length,
      totalIngested: ingested.size,
      marketOddsUpdated: built.marketUpdates,
      reasoned: { ok: reasonerSuccesses, fallback: reasonerFallbacks, total: targets.length },
      snapshots: snapshotsThisRun,
      lastSyncAt: now,
    });
  } catch (e) {
    console.error("[/api/ai/sync] error", e);
    return NextResponse.json({ ok: false, error: (e as Error).message }, { status: 500 });
  }
}

// GET — diagnostic snapshot of state + per-fixture blended probabilities.
export async function GET() {
  try {
    const state = await getAiState();
    const initial = await getInitialProbs();
    const built = await buildAllFixtureProbs();
    return NextResponse.json({
      ok: true,
      lastSyncAt: state.lastSyncAt,
      ingested: state.ingestedFixtures.length,
      delta: state.delta,
      probabilities: Object.values(built.byFixture).map(e => ({
        fixtureId: e.fixtureId,
        home: e.home,
        away: e.away,
        initial: initial?.fixtures[e.fixtureId] ?? null,
        blended: e.probs,
        market: e.market,
      })),
    });
  } catch (e) {
    return NextResponse.json({ ok: false, error: (e as Error).message }, { status: 500 });
  }
}
