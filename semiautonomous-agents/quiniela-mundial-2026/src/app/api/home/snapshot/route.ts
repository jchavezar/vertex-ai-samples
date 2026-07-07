// GET /api/home/snapshot
//
// Single BFF endpoint that batches every above-the-fold dataset the home
// page used to fetch in N parallel client-side requests:
//
//   scoreboard + scorers + dailyMvp + cafeAm + aiHeartbeat
//
// Each sub-fetch runs in parallel via Promise.allSettled so a single failure
// (e.g. ESPN flaking out) degrades just that field — the rest of the snapshot
// still serves. `partial: true` is set whenever ANY field fell back to null.
//
// Cache-Control adapts: short when any match is live (so freshly-scored goals
// propagate within ~15s), longer when idle.

import { NextResponse } from "next/server";
import { computeScoreboard, anyLiveEvent, type ScoreboardPayload } from "../../scoreboard/_logic";
import { computeTopScorers, type ScorerEntry } from "../../scorers/_logic";
import { fetchDailyMvpEntries, type MvpEntry } from "../../daily-mvp/_logic";
import { fetchTodayCafeBrief, cdmxDate, type PublicCafeBrief } from "../../cafe-am/_logic";
import { fetchLatestHeartbeat, type HeartbeatPayload } from "../../ai/heartbeat/_logic";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";
export const revalidate = 0;

export type HomeSnapshot = {
  ok: true;
  generatedAt: number;
  partial: boolean;
  scoreboard: ScoreboardPayload | null;
  scorers: { top5: ScorerEntry[] } | null;
  dailyMvp: { entries: MvpEntry[] } | null;
  aiHeartbeat: { latest: HeartbeatPayload | null } | null;
  cafeAm: { date: string; brief: PublicCafeBrief | null } | null;
};

function pickValue<T>(r: PromiseSettledResult<T>): { value: T | null; failed: boolean } {
  if (r.status === "fulfilled") return { value: r.value, failed: false };
  return { value: null, failed: true };
}

export async function GET() {
  const [scoreboardR, scorersR, mvpR, briefR, heartbeatR] = await Promise.allSettled([
    computeScoreboard(),
    computeTopScorers(),
    fetchDailyMvpEntries(),
    fetchTodayCafeBrief(),
    fetchLatestHeartbeat(),
  ]);

  let partial = false;
  const failures: string[] = [];

  const sb = pickValue(scoreboardR);
  if (sb.failed) { partial = true; failures.push("scoreboard"); }
  const scoreboard =
    sb.value && sb.value.ok ? (sb.value as ScoreboardPayload) : null;
  if (sb.value && !sb.value.ok) { partial = true; failures.push("scoreboard"); }

  const sc = pickValue(scorersR);
  if (sc.failed) { partial = true; failures.push("scorers"); }
  const scorers =
    sc.value && sc.value.ok ? { top5: sc.value.top5 } : null;
  if (sc.value && !sc.value.ok) { partial = true; failures.push("scorers"); }

  const mv = pickValue(mvpR);
  if (mv.failed) { partial = true; failures.push("dailyMvp"); }
  const dailyMvp = mv.value ? { entries: mv.value } : null;

  const cb = pickValue(briefR);
  if (cb.failed) { partial = true; failures.push("cafeAm"); }
  const cafeAm = cb.failed ? null : { date: cdmxDate(), brief: cb.value };

  const hb = pickValue(heartbeatR);
  if (hb.failed) { partial = true; failures.push("aiHeartbeat"); }
  const aiHeartbeat = hb.failed ? null : { latest: hb.value };

  if (failures.length) {
    console.warn("[home/snapshot] partial failures:", failures.join(", "));
  }

  const live = scoreboard ? anyLiveEvent(scoreboard.events) : false;
  // Live windows: short cache so scoreboard / scorers refresh within 15s,
  // matching the per-route adaptive policy. Idle: longer cache to soak the
  // first-paint cost of cold visits.
  const cacheHeader = live
    ? "public, max-age=15, stale-while-revalidate=60"
    : "public, max-age=120, stale-while-revalidate=300";

  const body: HomeSnapshot = {
    ok: true,
    generatedAt: Date.now(),
    partial,
    scoreboard,
    scorers,
    dailyMvp,
    aiHeartbeat,
    cafeAm,
  };

  return NextResponse.json(body, { headers: { "Cache-Control": cacheHeader } });
}
