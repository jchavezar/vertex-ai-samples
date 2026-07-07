// Public feed read. No auth — the events are not sensitive (player + match +
// pick) and the home polls this every 30s.
import { getRecentActivity } from "@/lib/activity-feed-server";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET() {
  try {
    const events = await getRecentActivity(30);
    return Response.json({ ok: true, events });
  } catch (e) {
    console.error("[/api/activity GET] error", e);
    return Response.json({ ok: false, error: "internal" }, { status: 500 });
  }
}
