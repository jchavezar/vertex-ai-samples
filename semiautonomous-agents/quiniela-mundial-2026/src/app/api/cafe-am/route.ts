// GET /api/cafe-am — public read of today's AVA morning brief. Doc lives
// at `cafe_am/{YYYY-MM-DD}` (CDMX). Returns `{ ok, brief: null }` if it
// hasn't been generated yet (cron runs at 7am).

import { fetchTodayCafeBrief } from "./_logic";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

// Daily content — long CDN cache + longer SWR so cold visits don't refetch
// from Firestore. The cron at 7am CDMX overwrites the doc; SWR will pick it
// up at the next request within the SWR window.
const CACHE_HEADER = "public, max-age=600, stale-while-revalidate=1800";

export async function GET() {
  try {
    const brief = await fetchTodayCafeBrief();
    return Response.json({ ok: true, brief }, { headers: { "Cache-Control": CACHE_HEADER } });
  } catch (err) {
    console.warn("[cafe-am GET] failed", err);
    return Response.json({ ok: false, brief: null }, { status: 200 });
  }
}
