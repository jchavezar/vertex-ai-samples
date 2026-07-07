// GET /api/daily-mvp
//
// Returns the latest two `daily_mvp` docs (today + yesterday window) so the
// home page chip can show "Caliente HOY" with a graceful fallback to "AYER".
// Public read — the docs only contain pool-internal data (player name,
// points) that the leaderboard already exposes.

import { fetchDailyMvpEntries, type MvpEntry } from "./_logic";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

// Cache for ~5min — the doc is rewritten by a cron at most once/day so
// staleness within that window is harmless. SWR keeps the home snappy
// even when origin is cold.
const CACHE_HEADER = "public, max-age=300, stale-while-revalidate=600";

export type { MvpEntry };

export async function GET() {
  try {
    const entries = await fetchDailyMvpEntries();
    return Response.json({ ok: true, entries }, { headers: { "Cache-Control": CACHE_HEADER } });
  } catch (e) {
    console.warn("[daily-mvp] read failed", e);
    return Response.json({ ok: false, entries: [] }, { status: 200 });
  }
}
