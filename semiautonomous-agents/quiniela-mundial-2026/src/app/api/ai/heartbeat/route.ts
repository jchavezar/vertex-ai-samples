// GET /api/ai/heartbeat — public, safe metadata about AVA's latest
// re-evaluation snapshot. Read by <AvaThinkingChip /> on the home page to
// render "just changed pick" or "learning, next tick in HH:MM".

import { fetchLatestHeartbeat } from "./_logic";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

// Heartbeat changes at most every ~6h (cron cadence). Long-ish max-age + SWR
// keeps the home snappy without going stale beyond the cron window.
const CACHE_HEADER = "public, max-age=180, stale-while-revalidate=900";

export async function GET() {
  try {
    const latest = await fetchLatestHeartbeat();
    return Response.json(
      { ok: true, latest },
      { headers: { "Cache-Control": CACHE_HEADER } },
    );
  } catch (err) {
    console.warn("[ai/heartbeat] read failed", err);
    return Response.json({ ok: false, latest: null }, { status: 200 });
  }
}
