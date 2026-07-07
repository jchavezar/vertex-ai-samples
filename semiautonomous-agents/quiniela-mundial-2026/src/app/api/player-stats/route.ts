// GET /api/player-stats?playerId=X
// Single server-side endpoint: reads all picks from Firestore in one batch,
// fetches ESPN actuals + KO results, computes score + rank, returns pre-digested stats.
// Much faster than the client doing 3+ fetch() calls in sequence.

import { db } from "@/lib/firestore-server";
import { PLAYERS } from "@/data/players";
import { allGroupFixtures } from "@/data/groups";
import { KO_SCHEDULE } from "@/data/knockout-schedule";
import { computePlayerScoreDetail, type MatchResult, actualPick, type PlayerPredictions, type GroupPrediction } from "@/lib/predictions";
import { fetchScoreboard } from "@/lib/espn";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const PICKS_COLLECTION = "quiniela_charales_picks";

// Build pair → fixtureId lookup once at module init
const FIXTURES = allGroupFixtures();
const PAIR_MAP = new Map<string, string>();
for (const fx of FIXTURES) {
  PAIR_MAP.set(`${fx.home}-${fx.away}`, fx.id);
  PAIR_MAP.set(`${fx.away}-${fx.home}`, fx.id);
}

export async function GET(req: Request) {
  const url = new URL(req.url);
  const playerId = url.searchParams.get("playerId");
  if (!playerId) return Response.json({ ok: false, error: "playerId required" }, { status: 400 });

  try {
    // 1. Fetch ALL players' picks + ESPN data in parallel (Firestore batch is fast server-side)
    const [allDocsSnap, sbData, koData] = await Promise.all([
      db.collection(PICKS_COLLECTION).get(),
      fetchScoreboard("", "fifa.world").catch(() => ({ events: [] })),
      fetchScoreboard("20260628-20260719", "fifa.world").catch(() => ({ events: [] })),
    ]);

    // 2. Build actuals map from ESPN group-stage events
    const actuals: Record<string, MatchResult> = {};
    for (const e of (sbData.events ?? [])) {
      if (e.status?.type?.state !== "post") continue;
      const comp = e.competitions?.[0];
      const h = comp?.competitors?.find((c: { homeAway: string }) => c.homeAway === "home");
      const a = comp?.competitors?.find((c: { homeAway: string }) => c.homeAway === "away");
      if (!h || !a) continue;
      const fxId = PAIR_MAP.get(`${h.team.abbreviation}-${a.team.abbreviation}`);
      if (!fxId) continue;
      actuals[fxId] = {
        home: h.team.abbreviation,
        away: a.team.abbreviation,
        homeGoals: Number(h.score ?? 0),
        awayGoals: Number(a.score ?? 0),
      };
    }

    // 3. Build KO results map from ESPN knockout events
    const koResults: Record<string, string> = {};
    for (const slot of KO_SCHEDULE) {
      const slotUtcMs = new Date(slot.dateISO).getTime();
      const match = (koData.events ?? []).find((e: { date: string }) => {
        const eMs = new Date(e.date).getTime();
        return Math.abs(eMs - slotUtcMs) < 2 * 60 * 60 * 1000;
      });
      if (!match) continue;
      if (match.status?.type?.state !== "post") continue;
      const comp = match.competitions?.[0];
      if (!comp) continue;
      let winner = comp.competitors?.find((c: { winner?: boolean }) => c.winner);
      if (!winner) {
        const [hh, aa] = comp.competitors ?? [];
        if (hh && aa) winner = Number(hh.score) > Number(aa.score) ? hh : aa;
      }
      if (!winner) continue;
      koResults[slot.slot] = winner.team.abbreviation;
    }

    // 4. Build doc map and compute all player scores for ranking
    const docMap = new Map<string, Record<string, unknown>>();
    for (const d of allDocsSnap.docs) docMap.set(d.id, d.data() as Record<string, unknown>);

    type PlayerDoc = {
      group?: Record<string, { pick?: string; homeGoals?: number; awayGoals?: number }>;
      bracket?: { R32?: string[]; R16?: string[]; QF?: string[]; SF?: string[]; THIRD?: string; FINAL?: string };
      champion?: string;
    };

    function toPlayerPredictions(id: string, doc: Record<string, unknown> | undefined) {
      const d = (doc ?? {}) as PlayerDoc;
      return {
        playerId: id,
        group: (d.group ?? {}) as Record<string, GroupPrediction>,
        bracket: d.bracket ?? {},
        champion: d.champion,
        updatedAt: 0,
      } as PlayerPredictions;
    }

    const allScores = PLAYERS.map(p => {
      const doc = docMap.get(p.id);
      const pred = toPlayerPredictions(p.id, doc);
      const detail = computePlayerScoreDetail(pred, actuals, koResults);
      return { id: p.id, ...detail };
    }).sort((a, b) => b.score - a.score);

    // 5. Extract target player's stats
    const myDoc = docMap.get(playerId) as PlayerDoc | undefined;
    if (!myDoc && !docMap.has(playerId)) {
      return Response.json({ ok: true, stats: null });
    }

    const myPred = toPlayerPredictions(playerId, myDoc);
    const myDetail = computePlayerScoreDetail(myPred, actuals, koResults);
    const rank = allScores.findIndex(s => s.id === playerId) + 1;

    // 6. Build group hit/miss counts
    let groupHits = 0; let groupMiss = 0;
    for (const [fxId, pred] of Object.entries(myPred.group)) {
      const actual = actuals[fxId];
      if (!actual || !pred?.pick) continue;
      if (pred.pick === actualPick(actual)) groupHits++;
      else groupMiss++;
    }

    // 7. Build R32 picks with hit/miss
    const r32 = myPred.bracket?.R32 ?? [];
    const r32Picks = r32.map((pick, i) => {
      const slot = `R32-${i + 1}`;
      const actual = koResults[slot];
      const hit = actual ? pick === actual : undefined;
      return { slot, pick, actual, hit };
    });

    return Response.json({
      ok: true,
      stats: {
        rank,
        score: myDetail.score,
        groupHits,
        groupMiss,
        koHits: myDetail.bracketHits,
        koMiss: Object.keys(koResults).filter(k => {
          const arr = myPred.bracket as Record<string, unknown>;
          // Count resolved KO slots where the player had a pick but missed
          const round = k.replace(/-\d+$/, "") as keyof typeof myPred.bracket;
          const idx = parseInt(k.split("-")[1] ?? "1", 10) - 1;
          const picks = Array.isArray(arr[round]) ? (arr[round] as string[]) : undefined;
          const pick = picks ? picks[idx] : (arr[round] as string | undefined);
          return pick && pick !== koResults[k];
        }).length,
        champion: myDoc?.champion,
        r32Picks,
      },
    }, { headers: { "Cache-Control": "no-store" } });
  } catch (e) {
    console.error("[/api/player-stats]", e);
    return Response.json({ ok: false, error: "internal" }, { status: 500 });
  }
}
