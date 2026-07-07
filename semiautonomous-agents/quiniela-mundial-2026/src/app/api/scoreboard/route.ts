// Server-side proxy to ESPN scoreboard (handles CORS + caching).
// Merges FIFA World Cup events with international friendlies in the pre-WC window.
// The aggregation lives in ./_logic.ts so the home snapshot endpoint can share it.
import { NextResponse } from "next/server";
import { computeScoreboard, anyLiveEvent } from "./_logic";

// No edge revalidation: we set fine-grained Cache-Control headers per response
// based on whether any match is live. A stale 30s cache during a goal flurry
// is exactly the kind of UX problem the owner flagged (4-1 SUI shown as 0-0).
export const dynamic = "force-dynamic";
export const revalidate = 0;

export async function GET(req: Request) {
  const url = new URL(req.url);
  const wcDates = url.searchParams.get("dates") || undefined;

  const result = await computeScoreboard(wcDates);
  if (!result.ok) {
    return NextResponse.json({ ok: false, error: result.error }, { status: 502 });
  }
  // If ANY event is live we serve a very short cache so goals propagate within
  // seconds. Otherwise we can afford a longer cache for stability.
  const cacheHeader = anyLiveEvent(result.events)
    ? "public, max-age=3, stale-while-revalidate=10"
    : "public, max-age=20, stale-while-revalidate=60";
  return NextResponse.json(
    { ok: true, leagues: result.leagues, events: result.events, partialErrors: result.partialErrors },
    { headers: { "Cache-Control": cacheHeader } },
  );
}
