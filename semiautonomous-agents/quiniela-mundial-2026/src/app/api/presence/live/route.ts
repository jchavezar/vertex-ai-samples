// Public read: who is currently online (lastPing within 90s) + the N most
// recent activity events from the existing `activity_feed` collection. No auth
// — same posture as /api/activity. Polled by GhostActivityFeed every 30s.
import { db } from "@/lib/firestore-server";
import { getRecentActivity, type ActivityEvent } from "@/lib/activity-feed-server";
import { PRESENCE_COLLECTION } from "@/app/api/presence/ping/route";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const ONLINE_WINDOW_MS = 90_000;

export type PresenceEntry = {
  playerId: string;
  lastPing: number;
  currentPath?: string;
  action?: string;
};

export type PresenceLiveResponse = {
  ok: boolean;
  online: PresenceEntry[];
  events: ActivityEvent[];
  serverTime: number;
};

export async function GET() {
  try {
    const cutoff = Date.now() - ONLINE_WINDOW_MS;
    const snap = await db
      .collection(PRESENCE_COLLECTION)
      .where("lastPing", ">=", cutoff)
      .get();
    const online: PresenceEntry[] = [];
    for (const doc of snap.docs) {
      const data = doc.data() as Partial<PresenceEntry>;
      if (typeof data.lastPing !== "number") continue;
      online.push({
        playerId: data.playerId ?? doc.id,
        lastPing: data.lastPing,
        currentPath: typeof data.currentPath === "string" ? data.currentPath : undefined,
        action: typeof data.action === "string" ? data.action : undefined,
      });
    }
    online.sort((a, b) => b.lastPing - a.lastPing);

    let events: ActivityEvent[] = [];
    try {
      events = await getRecentActivity(10);
    } catch (e) {
      console.warn("[/api/presence/live] activity read failed", e);
    }

    const body: PresenceLiveResponse = {
      ok: true,
      online,
      events,
      serverTime: Date.now(),
    };
    return Response.json(body);
  } catch (e) {
    console.error("[/api/presence/live] error", e);
    return Response.json({ ok: false, online: [], events: [], serverTime: Date.now() }, { status: 500 });
  }
}
