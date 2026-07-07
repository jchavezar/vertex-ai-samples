// Owner-only aggregator over usage_events. Reads last 14 days raw and folds
// per-player + per-day + heatmap counts in memory.

import { readAuth } from "@/lib/auth-server";
import { db } from "@/lib/firestore-server";
import { PLAYERS } from "@/data/players";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const OWNER_ID = "jesus";
const RANGE_DAYS = 14;
const MAX_DOCS = 20_000;

type EventDoc = {
  playerId: string | null;
  event: string;
  props?: unknown;
  ts: number;
  path?: string | null;
  sessionId?: string | null;
};

function dayKey(ms: number): string {
  const d = new Date(ms);
  const y = d.getUTCFullYear();
  const m = String(d.getUTCMonth() + 1).padStart(2, "0");
  const day = String(d.getUTCDate()).padStart(2, "0");
  return `${y}-${m}-${day}`;
}

function lastNDays(n: number): string[] {
  const out: string[] = [];
  const today = Date.now();
  for (let i = n - 1; i >= 0; i--) out.push(dayKey(today - i * 86_400_000));
  return out;
}

export async function GET() {
  const auth = await readAuth();
  if (!auth || auth.playerId !== OWNER_ID) {
    return new Response("Not Found", { status: 404 });
  }

  const since = Date.now() - RANGE_DAYS * 86_400_000;
  let docs: EventDoc[] = [];
  try {
    const snap = await db
      .collection("usage_events")
      .where("ts", ">=", since)
      .orderBy("ts", "desc")
      .limit(MAX_DOCS)
      .get();
    docs = snap.docs.map((d) => d.data() as EventDoc);
  } catch (e) {
    return Response.json({ ok: false, error: (e as Error).message }, { status: 500 });
  }

  const totalEvents = docs.length;
  const sessionSet = new Set<string>();
  const eventCounts = new Map<string, number>();
  const pathCounts = new Map<string, number>();

  type PerPlayerAgg = {
    id: string;
    events: number;
    sessions: Set<string>;
    lastSeen: number | null;
    featureCounts: Map<string, number>;
    sessionFirstTs: Map<string, number>;
    sessionLastTs: Map<string, number>;
  };
  const playerMap = new Map<string, PerPlayerAgg>();
  function pp(id: string): PerPlayerAgg {
    let cur = playerMap.get(id);
    if (!cur) {
      cur = {
        id,
        events: 0,
        sessions: new Set<string>(),
        lastSeen: null,
        featureCounts: new Map<string, number>(),
        sessionFirstTs: new Map<string, number>(),
        sessionLastTs: new Map<string, number>(),
      };
      playerMap.set(id, cur);
    }
    return cur;
  }

  const dayBuckets = new Map<
    string,
    { events: number; sessions: Set<string>; players: Set<string> }
  >();
  for (const d of lastNDays(RANGE_DAYS)) {
    dayBuckets.set(d, { events: 0, sessions: new Set(), players: new Set() });
  }

  for (const ev of docs) {
    if (typeof ev.event !== "string") continue;
    eventCounts.set(ev.event, (eventCounts.get(ev.event) ?? 0) + 1);
    if (ev.sessionId) sessionSet.add(ev.sessionId);

    if (ev.event === "page_view" && ev.path) {
      pathCounts.set(ev.path, (pathCounts.get(ev.path) ?? 0) + 1);
    }

    const pid = ev.playerId ?? "_anon";
    const agg = pp(pid);
    agg.events++;
    if (ev.sessionId) {
      agg.sessions.add(ev.sessionId);
      const prevFirst = agg.sessionFirstTs.get(ev.sessionId);
      if (prevFirst === undefined || ev.ts < prevFirst) {
        agg.sessionFirstTs.set(ev.sessionId, ev.ts);
      }
      const prevLast = agg.sessionLastTs.get(ev.sessionId);
      if (prevLast === undefined || ev.ts > prevLast) {
        agg.sessionLastTs.set(ev.sessionId, ev.ts);
      }
    }
    if (agg.lastSeen === null || ev.ts > agg.lastSeen) agg.lastSeen = ev.ts;
    agg.featureCounts.set(ev.event, (agg.featureCounts.get(ev.event) ?? 0) + 1);

    const dk = dayKey(ev.ts);
    const bucket = dayBuckets.get(dk);
    if (bucket) {
      bucket.events++;
      if (ev.sessionId) bucket.sessions.add(ev.sessionId);
      bucket.players.add(pid);
    }
  }

  const playerMeta = new Map(PLAYERS.map((p) => [p.id, p]));
  const perPlayer = Array.from(playerMap.values())
    .map((agg) => {
      const meta = playerMeta.get(agg.id);
      const name = meta?.name ?? (agg.id === "_anon" ? "Anónimo" : agg.id);
      const isBot = meta?.isBot ?? false;
      let durSum = 0;
      let durN = 0;
      for (const sid of agg.sessions) {
        const f = agg.sessionFirstTs.get(sid) ?? 0;
        const l = agg.sessionLastTs.get(sid) ?? 0;
        if (l > f) {
          durSum += l - f;
          durN++;
        }
      }
      const avgSessionSec = durN > 0 ? Math.round(durSum / durN / 1000) : 0;
      const topFeatures = Array.from(agg.featureCounts.entries())
        .map(([event, count]) => ({ event, count }))
        .sort((a, b) => b.count - a.count)
        .slice(0, 12);
      return {
        id: agg.id,
        name,
        isBot,
        events: agg.events,
        sessions: agg.sessions.size,
        lastSeen: agg.lastSeen,
        avgSessionSec,
        topFeatures,
      };
    })
    .sort((a, b) => b.events - a.events);

  const eventCountsGlobal = Array.from(eventCounts.entries())
    .map(([event, count]) => ({ event, count }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 30);

  const perDay = lastNDays(RANGE_DAYS).map((date) => {
    const b = dayBuckets.get(date)!;
    return {
      date,
      events: b.events,
      sessions: b.sessions.size,
      uniquePlayers: b.players.size,
    };
  });

  const topPlayers = perPlayer.slice(0, 8);
  const topFeatures = eventCountsGlobal.slice(0, 10).map((f) => f.event);
  const featureIdx = new Map(topFeatures.map((f, i) => [f, i]));
  const matrix: number[][] = topPlayers.map(() =>
    new Array(topFeatures.length).fill(0),
  );
  topPlayers.forEach((p, pi) => {
    const agg = playerMap.get(p.id);
    if (!agg) return;
    for (const [feature, count] of agg.featureCounts) {
      const fi = featureIdx.get(feature);
      if (fi === undefined) continue;
      matrix[pi][fi] = count;
    }
  });

  const pageViews = Array.from(pathCounts.entries())
    .map(([path, count]) => ({ path, count }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 20);

  return Response.json({
    generatedAt: Date.now(),
    rangeDays: RANGE_DAYS,
    totalEvents,
    uniqueSessions: sessionSet.size,
    eventCountsGlobal,
    perPlayer,
    perDay,
    heatmap: {
      players: topPlayers.map((p) => p.name),
      features: topFeatures,
      matrix,
    },
    pageViews,
  });
}
