// GET /api/ranking/people
// Aggregates every compa's picks from Firestore (collection
// quiniela_charales_picks) and returns, per team code:
//   - championVotes:    how many players picked that team as champion
//   - groupPickShare:   share of group-stage picks where that team was the
//                       winner (across all human players)
//   - totalPlayers:     total number of human compas with at least one pick
// The AI bot is excluded so this reflects "lo que dice la gente".

import { db } from "@/lib/firestore-server";
import { PICKS_COLLECTION } from "@/lib/predictions-server";
import { AI_PLAYER_ID } from "@/data/players";
import { allGroupFixtures } from "@/data/groups";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

type GroupPick = { pick?: "H" | "D" | "A" };
type PlayerDoc = {
  playerId?: string;
  champion?: string;
  runnerUp?: string;
  group?: Record<string, GroupPick>;
};

export async function GET() {
  try {
    const snap = await db.collection(PICKS_COLLECTION).get();
    const fixtures = allGroupFixtures();
    const fxByPair = new Map<string, { home: string; away: string }>();
    for (const fx of fixtures) fxByPair.set(fx.id, { home: fx.home, away: fx.away });

    const championVotes: Record<string, number> = {};
    const runnerUpVotes: Record<string, number> = {};
    const groupWinCounts: Record<string, number> = {};
    let totalGroupPicks = 0;
    let totalPlayers = 0;

    for (const doc of snap.docs) {
      const data = doc.data() as PlayerDoc;
      const pid = data.playerId ?? doc.id;
      if (pid === AI_PLAYER_ID) continue;

      const hasAnyPick =
        (data.champion && typeof data.champion === "string") ||
        (data.group && Object.keys(data.group).length > 0);
      if (!hasAnyPick) continue;
      totalPlayers++;

      if (data.champion) {
        championVotes[data.champion] = (championVotes[data.champion] ?? 0) + 1;
      }
      if (data.runnerUp) {
        runnerUpVotes[data.runnerUp] = (runnerUpVotes[data.runnerUp] ?? 0) + 1;
      }

      if (data.group) {
        for (const [fxId, gp] of Object.entries(data.group)) {
          const fx = fxByPair.get(fxId);
          if (!fx || !gp?.pick) continue;
          totalGroupPicks++;
          // Count which team got the "favor" in this pick (winner = +1; draw = +0.5 each).
          if (gp.pick === "H") {
            groupWinCounts[fx.home] = (groupWinCounts[fx.home] ?? 0) + 1;
          } else if (gp.pick === "A") {
            groupWinCounts[fx.away] = (groupWinCounts[fx.away] ?? 0) + 1;
          } else {
            groupWinCounts[fx.home] = (groupWinCounts[fx.home] ?? 0) + 0.5;
            groupWinCounts[fx.away] = (groupWinCounts[fx.away] ?? 0) + 0.5;
          }
        }
      }
    }

    const groupPickShare: Record<string, number> = {};
    if (totalGroupPicks > 0) {
      for (const [code, n] of Object.entries(groupWinCounts)) {
        groupPickShare[code] = n / totalGroupPicks;
      }
    }

    return Response.json({
      ok: true,
      totalPlayers,
      totalGroupPicks,
      championVotes,
      runnerUpVotes,
      groupPickShare,
      updatedAt: Date.now(),
    });
  } catch (e) {
    console.error("[/api/ranking/people] error", e);
    return Response.json(
      { ok: false, error: (e as Error).message },
      { status: 500 },
    );
  }
}
