// POST /api/cron/pre-match-push
//
// Cloud Scheduler entry point (gated by `x-cron-secret`). For every fixture
// kicking off in the next 105–135 minutes, finds the human charales who
// still haven't picked (or whose pick is missing a score) and pushes a
// "Falta tu pick" notification to each of their registered devices.
//
// The 30-minute window width is intentional: Cloud Scheduler is expected to
// run this every 30 min, and the window [105, 135) min before kickoff
// guarantees each fixture is hit by *exactly one* invocation. Shrinking the
// scheduler interval without also narrowing the window would duplicate the
// push.
//
// Cloud Scheduler config the owner needs to add (one-time):
//   gcloud scheduler jobs create http q26-pre-match-push \
//     --schedule="*/30 * * * *" \
//     --time-zone="America/Mexico_City" \
//     --uri="https://charales-2026.../api/cron/pre-match-push" \
//     --http-method=POST \
//     --headers="x-cron-secret=$CRON_SECRET"
//
// Returns { ok, fixturesInWindow, pushesSent, pushesFailed }.

import { NextRequest } from "next/server";
import { allGroupFixtures, type GroupFixture } from "@/data/groups";
import { fixtureKickoffMs } from "@/lib/fixture-time";
import { TEAMS } from "@/data/teams";
import { PLAYERS } from "@/data/players";
import { db } from "@/lib/firestore-server";
import { PICKS_COLLECTION } from "@/lib/predictions-server";
import { sendPushToPlayer, pushConfigured } from "@/lib/push-server";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";
export const maxDuration = 120;

const WINDOW_LOW_MS = 105 * 60 * 1000;   // 1h 45m
const WINDOW_HIGH_MS = 135 * 60 * 1000;  // 2h 15m

type GroupPick = { pick?: string; homeGoals?: number; awayGoals?: number };

function fixturesInWindow(now: number): GroupFixture[] {
  return allGroupFixtures().filter(fx => {
    const dt = fixtureKickoffMs(fx) - now;
    return dt >= WINDOW_LOW_MS && dt < WINDOW_HIGH_MS;
  });
}

function teamName(code: string): string {
  return TEAMS.find(t => t.code === code)?.name ?? code;
}

// A pick is considered "incomplete" for nudge purposes if any of the
// following holds: no pick selected, OR pick selected but score missing.
// Both states warrant a 2h-before reminder.
function pickIncomplete(p: GroupPick | undefined): boolean {
  if (!p) return true;
  if (!p.pick) return true;
  if (typeof p.homeGoals !== "number" || typeof p.awayGoals !== "number") return true;
  return false;
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

  const now = Date.now();
  const fixtures = fixturesInWindow(now);
  if (fixtures.length === 0) {
    return Response.json({ ok: true, fixturesInWindow: 0, pushesSent: 0, pushesFailed: 0 });
  }

  const picksByPlayer = await loadAllPicks();
  const humans = PLAYERS.filter(p => !p.isBot);

  // Build the (player, fixture) push queue.
  type Job = { playerId: string; fx: GroupFixture };
  const jobs: Job[] = [];
  for (const fx of fixtures) {
    for (const player of humans) {
      const playerPicks = picksByPlayer.get(player.id) ?? {};
      if (pickIncomplete(playerPicks[fx.id])) {
        jobs.push({ playerId: player.id, fx });
      }
    }
  }

  if (jobs.length === 0) {
    return Response.json({ ok: true, fixturesInWindow: fixtures.length, pushesSent: 0, pushesFailed: 0 });
  }

  const results = await Promise.allSettled(jobs.map(async (job) => {
    const home = teamName(job.fx.home);
    const away = teamName(job.fx.away);
    const r = await sendPushToPlayer(job.playerId, {
      title: `⏰ Falta tu pick — ${home} vs ${away}`,
      body: "Kickoff en 2h. Picea antes de que se cierre.",
      url: `/quiniela?fixture=${job.fx.id}`,
      tag: `pre-match:${job.fx.id}`,
    });
    return r;
  }));

  let pushesSent = 0;
  let pushesFailed = 0;
  for (let i = 0; i < results.length; i++) {
    const r = results[i];
    if (r.status === "fulfilled") {
      pushesSent += r.value.sent;
      pushesFailed += r.value.failed;
    } else {
      pushesFailed += 1;
      console.error("[pre-match-push] job failed", jobs[i], r.reason);
    }
  }

  return Response.json({
    ok: true,
    fixturesInWindow: fixtures.length,
    jobsQueued: jobs.length,
    pushesSent,
    pushesFailed,
  });
}
