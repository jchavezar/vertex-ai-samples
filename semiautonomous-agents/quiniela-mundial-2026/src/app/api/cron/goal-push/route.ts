// POST /api/cron/goal-push
//
// Cloud Scheduler entry point (gated by `x-cron-secret`). Polls the ESPN
// scoreboard for in-progress events, diffs the current score against the
// last-known score stored in Firestore (`goal_push_state/main`), and pushes
// a "⚽ Gol!" notification to every human charal whose pick is on the right
// side of the new scoreline.
//
// Cloud Scheduler config the owner needs to add (one-time):
//   gcloud scheduler jobs create http q26-goal-push \
//     --schedule="* * * * *" \
//     --time-zone="America/Mexico_City" \
//     --uri="https://charales-2026.../api/cron/goal-push" \
//     --http-method=POST \
//     --headers="x-cron-secret=$CRON_SECRET"
//
// Cron syntax only allows 1-minute resolution; for a true 30s cadence on
// match days the owner can attach two jobs offset by 30s, or move to Cloud
// Tasks. The route is idempotent — re-running with the same scoreboard
// produces no extra pushes because the state doc gates emission.
//
// Returns { ok, eventsChecked, goalsDetected, pushesSent, pushesFailed }.

import { NextRequest } from "next/server";
import { fetchScoreboard, homeAway, normalizeAbbr, type EspnEvent } from "@/lib/espn";
import { allGroupFixtures, type GroupFixture } from "@/data/groups";
import { PLAYERS } from "@/data/players";
import { db } from "@/lib/firestore-server";
import { PICKS_COLLECTION } from "@/lib/predictions-server";
import { sendPushToPlayer, pushConfigured, type PushPayload } from "@/lib/push-server";
import { TEAMS } from "@/data/teams";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";
export const maxDuration = 120;

const STATE_DOC = "goal_push_state/main";

type GroupPick = { pick?: "H" | "D" | "A"; homeGoals?: number; awayGoals?: number };
type StoredState = { scores: Record<string, { home: number; away: number }>; updatedAt?: number };

function teamName(code: string): string {
  return TEAMS.find(t => t.code === code)?.name ?? code;
}

// Match an ESPN event to a tournament fixture. ESPN abbreviations get
// normalized through ABBR_MAP; we match on (home, away) code pair. Returns
// null when ESPN is broadcasting a friendly or a fixture we don't track.
function matchFixture(e: EspnEvent, fixtures: GroupFixture[]): GroupFixture | null {
  try {
    const { home, away } = homeAway(e);
    const h = normalizeAbbr(home.team.abbreviation);
    const a = normalizeAbbr(away.team.abbreviation);
    return fixtures.find(fx => fx.home === h && fx.away === a) ?? null;
  } catch {
    return null;
  }
}

async function loadState(): Promise<StoredState> {
  const [coll, doc] = STATE_DOC.split("/");
  const snap = await db.collection(coll).doc(doc).get();
  if (!snap.exists) return { scores: {} };
  const data = snap.data() as StoredState | undefined;
  return { scores: data?.scores ?? {}, updatedAt: data?.updatedAt };
}

async function saveState(state: StoredState): Promise<void> {
  const [coll, doc] = STATE_DOC.split("/");
  await db.collection(coll).doc(doc).set({ scores: state.scores, updatedAt: Date.now() }, { merge: false });
}

async function loadAllPicks(): Promise<Map<string, Record<string, GroupPick>>> {
  const snap = await db.collection(PICKS_COLLECTION).get();
  const out = new Map<string, Record<string, GroupPick>>();
  for (const d of snap.docs) {
    const data = d.data() as { group?: Record<string, GroupPick> };
    out.set(d.id, data?.group ?? {});
  }
  return out;
}

// Players to notify when a goal lands. We push to everyone whose pick
// matches the unfolding scoreline winner OR who picked the exact running
// score. Picks that are "live correct" feel rewarded; picks that just got
// invalidated still get the ping so they re-engage.
function playersToNotify(
  picksByPlayer: Map<string, Record<string, GroupPick>>,
  fxId: string,
  newHome: number,
  newAway: number,
): { matching: string[]; exact: string[] } {
  const lead: "H" | "D" | "A" = newHome > newAway ? "H" : newHome < newAway ? "A" : "D";
  const matching: string[] = [];
  const exact: string[] = [];
  for (const player of PLAYERS) {
    if (player.isBot) continue;
    const pick = picksByPlayer.get(player.id)?.[fxId];
    if (!pick?.pick) continue;
    if (pick.pick === lead) matching.push(player.id);
    if (pick.homeGoals === newHome && pick.awayGoals === newAway) exact.push(player.id);
  }
  return { matching, exact };
}

export async function POST(req: NextRequest) {
  const expected = process.env.CRON_SECRET;
  if (!expected) {
    return Response.json({ ok: false, error: "cron_disabled" }, { status: 503 });
  }
  if (req.headers.get("x-cron-secret") !== expected) {
    return Response.json({ ok: false, error: "forbidden" }, { status: 403 });
  }
  if (!pushConfigured()) {
    return Response.json({ ok: false, error: "vapid_missing" }, { status: 503 });
  }

  let scoreboard;
  try {
    scoreboard = await fetchScoreboard();
  } catch (e) {
    return Response.json({ ok: false, error: "espn_failed", detail: String(e) }, { status: 502 });
  }

  const fixtures = allGroupFixtures();
  const state = await loadState();
  const newScores: Record<string, { home: number; away: number }> = { ...state.scores };

  // For every event currently "in", determine if either team's score went up
  // versus state. If so, push the relevant players.
  type Goal = {
    fixture: GroupFixture;
    team: "home" | "away";
    teamCode: string;
    homeGoals: number;
    awayGoals: number;
  };
  const goals: Goal[] = [];
  let eventsChecked = 0;

  for (const e of scoreboard.events) {
    if (e.status.type.state !== "in") continue;
    eventsChecked++;
    const fx = matchFixture(e, fixtures);
    if (!fx) continue;

    let home = 0, away = 0;
    try {
      const ha = homeAway(e);
      home = Number(ha.home.score);
      away = Number(ha.away.score);
    } catch { continue; }
    if (!Number.isFinite(home) || !Number.isFinite(away)) continue;

    const prev = state.scores[fx.id] ?? { home: 0, away: 0 };
    if (home > prev.home) {
      goals.push({ fixture: fx, team: "home", teamCode: fx.home, homeGoals: home, awayGoals: away });
    }
    if (away > prev.away) {
      goals.push({ fixture: fx, team: "away", teamCode: fx.away, homeGoals: home, awayGoals: away });
    }
    newScores[fx.id] = { home, away };
  }

  if (goals.length === 0) {
    // Persist state even when nothing changed — covers the case where the
    // doc was missing entirely and we just saw 0-0 events.
    await saveState({ scores: newScores });
    return Response.json({
      ok: true,
      eventsChecked,
      goalsDetected: 0,
      pushesSent: 0,
      pushesFailed: 0,
    });
  }

  const picksByPlayer = await loadAllPicks();

  // Build (playerId, payload) push jobs. Deduplicate per goal so the same
  // player doesn't get two notifications for the same scoreline change.
  type Job = { playerId: string; payload: PushPayload };
  const jobs: Job[] = [];
  for (const g of goals) {
    const { matching, exact } = playersToNotify(picksByPlayer, g.fixture.id, g.homeGoals, g.awayGoals);
    const notifyIds = new Set<string>([...matching, ...exact]);
    if (notifyIds.size === 0) continue;
    const scorer = teamName(g.teamCode);
    const score = `${g.homeGoals}-${g.awayGoals}`;
    for (const playerId of notifyIds) {
      const goingWell = matching.includes(playerId);
      jobs.push({
        playerId,
        payload: {
          title: `⚽ Gol! ${scorer} ${score}`,
          body: goingWell ? "Tu pick va bien. Ver en vivo →" : "Tu pick va mamando. Ver en vivo →",
          url: `/partido/${g.fixture.id}/live`,
          tag: `goal:${g.fixture.id}:${score}`,
        },
      });
    }
  }

  const results = await Promise.allSettled(jobs.map(j => sendPushToPlayer(j.playerId, j.payload)));
  let pushesSent = 0;
  let pushesFailed = 0;
  for (let i = 0; i < results.length; i++) {
    const r = results[i];
    if (r.status === "fulfilled") {
      pushesSent += r.value.sent;
      pushesFailed += r.value.failed;
    } else {
      pushesFailed += 1;
      console.error("[goal-push] job failed", jobs[i].playerId, r.reason);
    }
  }

  // Only persist the new scoreboard *after* pushes were attempted — if the
  // route crashes before this point, the next run will retry the same goals.
  await saveState({ scores: newScores });

  return Response.json({
    ok: true,
    eventsChecked,
    goalsDetected: goals.length,
    pushJobs: jobs.length,
    pushesSent,
    pushesFailed,
  });
}
