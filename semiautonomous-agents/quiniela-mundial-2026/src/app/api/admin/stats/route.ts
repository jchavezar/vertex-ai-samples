// GET /api/admin/stats — owner-only telemetry. Gated to playerId === "jesus"
// via the auth cookie. Aggregates picks, photos, cromos, chat, push, and
// activity into a single payload for the personal dashboard.

import { NextRequest } from "next/server";
import { readAuth } from "@/lib/auth-server";
import { db } from "@/lib/firestore-server";
import { PLAYERS } from "@/data/players";
import { allGroupFixtures } from "@/data/groups";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const OWNER_ID = "jesus";

type PerPlayer = {
  id: string;
  name: string;
  isBot: boolean;
  picks: {
    groupTotal: number;
    groupWithScore: number;
    bracketRounds: number;
    champion: string | null;
    runnerUp: string | null;
    updatedAt: number | null;
  };
  photo: {
    activeSource: "uploaded" | "generated" | "original" | null;
    activeUrl: string | null;
    activeUpdatedAt: number | null;
    historyTotal: number;
    historyUploaded: number;
    historyGenerated: number;
    lastHistoryAt: number | null;
  };
  cromo: { total: number; lastDate: string | null };
  push: { devices: number; lastDeviceAt: number | null };
  chat: { messages: number; lastMessageAt: number | null };
  activity: { total7d: number; pickEvents7d: number };
};

type DailyBucket = { date: string; total: number; byType: Record<string, number>; byPlayer: Record<string, number> };

type StatsPayload = {
  generatedAt: number;
  totals: {
    players: number;
    humanPlayers: number;
    picksTotal: number;
    photosGeneratedTotal: number;
    photosUploadedTotal: number;
    cromosTotal: number;
    chatMessagesTotal: number;
    pushDevicesTotal: number;
    activityTotal7d: number;
  };
  players: PerPlayer[];
  activityByDay: DailyBucket[];
  cromosByDay: { date: string; total: number; byPlayer: Record<string, number> }[];
  chatByDay: { date: string; total: number; byPlayer: Record<string, number> }[];
  photosByDay: { date: string; uploaded: number; generated: number; byPlayer: Record<string, number> }[];
  fixturesConsensus: {
    fixtureId: string;
    home: string;
    away: string;
    date: string;
    h: number; d: number; a: number;
    scoreCount: number;
    voters: string[];
  }[];
};

function ymd(ms: number, tz = "America/Mexico_City"): string {
  return new Intl.DateTimeFormat("en-CA", {
    timeZone: tz,
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  }).format(new Date(ms));
}

function emptyDailyRange(days: number): string[] {
  const out: string[] = [];
  const now = Date.now();
  for (let i = days - 1; i >= 0; i--) {
    out.push(ymd(now - i * 86_400_000));
  }
  return out;
}

async function loadPicks(playerId: string) {
  try {
    const snap = await db.collection("quiniela_charales_picks").doc(playerId).get();
    if (!snap.exists) return null;
    return snap.data() as {
      group?: Record<string, { pick?: string; homeGoals?: number; awayGoals?: number }>;
      bracket?: Record<string, string | string[]>;
      champion?: string;
      runnerUp?: string;
      updatedAt?: number;
    };
  } catch {
    return null;
  }
}

async function loadPhoto(playerId: string) {
  const active = await db.collection("player_avatars").doc(playerId).get().catch(() => null);
  const histSnap = await db.collection("player_avatars").doc(playerId)
    .collection("photo_history")
    .orderBy("createdAt", "desc")
    .limit(200)
    .get()
    .catch(() => null);
  return { active, histSnap };
}

async function loadCromoCount(playerId: string) {
  const snap = await db.collection("cromo_portraits")
    .where("playerId", "==", playerId)
    .get()
    .catch(() => null);
  if (!snap) return { total: 0, lastDate: null as string | null };
  let lastDate: string | null = null;
  for (const d of snap.docs) {
    const data = d.data() as { date?: string };
    if (data.date && (!lastDate || data.date > lastDate)) lastDate = data.date;
  }
  return { total: snap.size, lastDate };
}

async function loadPushDevices(playerId: string) {
  const snap = await db.collection("push_subscriptions").doc(playerId)
    .collection("devices").get().catch(() => null);
  if (!snap) return { devices: 0, lastDeviceAt: null as number | null };
  let lastDeviceAt: number | null = null;
  for (const d of snap.docs) {
    const data = d.data() as { createdAt?: number };
    if (typeof data.createdAt === "number" && (!lastDeviceAt || data.createdAt > lastDeviceAt)) {
      lastDeviceAt = data.createdAt;
    }
  }
  return { devices: snap.size, lastDeviceAt };
}

async function loadChatMeta(playerId: string) {
  const snap = await db.collection("quiniela_charales_chats").doc(playerId).get().catch(() => null);
  if (!snap || !snap.exists) return { messages: 0, lastMessageAt: null as number | null };
  const data = snap.data() as { messageCount?: number; lastMessageAt?: number | { toMillis?: () => number } };
  let lastMs: number | null = null;
  if (typeof data.lastMessageAt === "number") lastMs = data.lastMessageAt;
  else if (data.lastMessageAt && typeof (data.lastMessageAt as { toMillis?: () => number }).toMillis === "function") {
    lastMs = (data.lastMessageAt as { toMillis: () => number }).toMillis();
  }
  return { messages: data.messageCount ?? 0, lastMessageAt: lastMs };
}

async function loadActivity7d() {
  const cutoff = Date.now() - 7 * 86_400_000;
  const snap = await db.collection("activity_feed")
    .where("createdAt", ">=", cutoff)
    .orderBy("createdAt", "desc")
    .limit(800)
    .get()
    .catch(() => null);
  if (!snap) return [];
  return snap.docs.map(d => {
    const data = d.data() as { type?: string; playerId?: string; createdAt?: number };
    return {
      type: data.type ?? "unknown",
      playerId: data.playerId ?? "unknown",
      createdAt: data.createdAt ?? 0,
    };
  });
}

async function loadCromoBuckets(days: number) {
  const cutoff = Date.now() - days * 86_400_000;
  const snap = await db.collection("cromo_portraits")
    .where("createdAt", ">=", cutoff)
    .get()
    .catch(() => null);
  if (!snap) return [] as { date: string; playerId: string }[];
  return snap.docs.map(d => {
    const data = d.data() as { playerId?: string; date?: string; createdAt?: number };
    return { date: data.date ?? ymd(data.createdAt ?? Date.now()), playerId: data.playerId ?? "?" };
  });
}

async function loadPhotoBuckets(days: number) {
  const cutoff = Date.now() - days * 86_400_000;
  const out: { date: string; playerId: string; source: string }[] = [];
  await Promise.all(PLAYERS.map(async p => {
    const snap = await db.collection("player_avatars").doc(p.id)
      .collection("photo_history")
      .where("createdAt", ">=", cutoff)
      .get()
      .catch(() => null);
    if (!snap) return;
    for (const d of snap.docs) {
      const data = d.data() as { createdAt?: number; source?: string };
      out.push({
        date: ymd(data.createdAt ?? Date.now()),
        playerId: p.id,
        source: data.source ?? "generated",
      });
    }
  }));
  return out;
}

async function loadChatBuckets(days: number) {
  const cutoff = Date.now() - days * 86_400_000;
  const cutoffSec = Math.floor(cutoff / 1000);
  const out: { date: string; playerId: string }[] = [];
  await Promise.all(PLAYERS.map(async p => {
    const snap = await db.collection("quiniela_charales_chats").doc(p.id)
      .collection("events")
      .where("ts", ">=", cutoffSec)
      .get()
      .catch(() => null);
    if (!snap) return;
    for (const d of snap.docs) {
      const data = d.data() as { ts?: number; role?: string };
      if (data.role !== "user") continue; // count user turns only
      const ms = typeof data.ts === "number" ? data.ts * 1000 : Date.now();
      out.push({ date: ymd(ms), playerId: p.id });
    }
  }));
  return out;
}

async function loadConsensus(): Promise<StatsPayload["fixturesConsensus"]> {
  const now = Date.now();
  const fixtures = allGroupFixtures()
    .filter(fx => {
      const t = new Date(`${fx.date}T12:00:00Z`).getTime();
      return t > now - 86_400_000 * 2; // upcoming + last 2d
    })
    .slice(0, 12);
  if (fixtures.length === 0) return [];
  const allPicks: Record<string, Awaited<ReturnType<typeof loadPicks>>> = {};
  await Promise.all(PLAYERS.map(async p => { allPicks[p.id] = await loadPicks(p.id); }));
  return fixtures.map(fx => {
    let h = 0, d = 0, a = 0, scoreCount = 0;
    const voters: string[] = [];
    for (const p of PLAYERS) {
      const pick = allPicks[p.id]?.group?.[fx.id];
      if (!pick?.pick) continue;
      voters.push(p.name);
      if (pick.pick === "H") h++;
      else if (pick.pick === "D") d++;
      else if (pick.pick === "A") a++;
      if (typeof pick.homeGoals === "number" && typeof pick.awayGoals === "number") scoreCount++;
    }
    return { fixtureId: fx.id, home: fx.home, away: fx.away, date: fx.date, h, d, a, scoreCount, voters };
  });
}

export async function GET(_req: NextRequest) {
  const auth = await readAuth();
  if (!auth) return Response.json({ ok: false, error: "unauthorized" }, { status: 401 });
  if (auth.playerId !== OWNER_ID) {
    return Response.json({ ok: false, error: "forbidden" }, { status: 403 });
  }

  const days = 14;

  const [activity, cromoRaw, photoRaw, chatRaw, consensus] = await Promise.all([
    loadActivity7d(),
    loadCromoBuckets(days),
    loadPhotoBuckets(days),
    loadChatBuckets(days),
    loadConsensus(),
  ]);

  const players: PerPlayer[] = await Promise.all(PLAYERS.map(async p => {
    const [picksDoc, photo, cromo, push, chat] = await Promise.all([
      loadPicks(p.id),
      loadPhoto(p.id),
      loadCromoCount(p.id),
      loadPushDevices(p.id),
      loadChatMeta(p.id),
    ]);
    const group = picksDoc?.group ?? {};
    const groupKeys = Object.keys(group);
    const groupWithScore = groupKeys.filter(k => {
      const g = group[k];
      return typeof g?.homeGoals === "number" && typeof g?.awayGoals === "number";
    }).length;
    const bracket = picksDoc?.bracket ?? {};
    const bracketRounds = Object.keys(bracket).filter(k => {
      const v = bracket[k as keyof typeof bracket];
      if (Array.isArray(v)) return v.length > 0;
      return typeof v === "string" && v.length > 0;
    }).length;

    const activeData = photo.active && photo.active.exists ? (photo.active.data() as { url?: string | null; source?: string; updatedAt?: number }) : null;
    const historyDocs = photo.histSnap?.docs ?? [];
    const historyUploaded = historyDocs.filter(d => (d.data() as { source?: string }).source === "uploaded").length;
    const historyGenerated = historyDocs.filter(d => (d.data() as { source?: string }).source === "generated").length;
    const lastHistoryAt = historyDocs.length > 0 ? ((historyDocs[0].data() as { createdAt?: number }).createdAt ?? null) : null;

    const cutoff7 = Date.now() - 7 * 86_400_000;
    const myActivity = activity.filter(ev => ev.playerId === p.id && ev.createdAt >= cutoff7);
    const myPickEvents = myActivity.filter(ev => ev.type === "pick_made").length;

    return {
      id: p.id,
      name: p.name,
      isBot: !!p.isBot,
      picks: {
        groupTotal: groupKeys.length,
        groupWithScore,
        bracketRounds,
        champion: picksDoc?.champion ?? null,
        runnerUp: picksDoc?.runnerUp ?? null,
        updatedAt: picksDoc?.updatedAt ?? null,
      },
      photo: {
        activeSource: (activeData?.source as PerPlayer["photo"]["activeSource"]) ?? null,
        activeUrl: activeData?.url ?? null,
        activeUpdatedAt: activeData?.updatedAt ?? null,
        historyTotal: historyDocs.length,
        historyUploaded,
        historyGenerated,
        lastHistoryAt,
      },
      cromo: { total: cromo.total, lastDate: cromo.lastDate },
      push: { devices: push.devices, lastDeviceAt: push.lastDeviceAt },
      chat: { messages: chat.messages, lastMessageAt: chat.lastMessageAt },
      activity: { total7d: myActivity.length, pickEvents7d: myPickEvents },
    };
  }));

  const dates14 = emptyDailyRange(days);
  const dates7 = emptyDailyRange(7);

  const activityByDay: DailyBucket[] = dates7.map(date => ({ date, total: 0, byType: {}, byPlayer: {} }));
  const activityIndex: Record<string, DailyBucket> = Object.fromEntries(activityByDay.map(b => [b.date, b]));
  for (const ev of activity) {
    const date = ymd(ev.createdAt);
    const bucket = activityIndex[date];
    if (!bucket) continue;
    bucket.total++;
    bucket.byType[ev.type] = (bucket.byType[ev.type] ?? 0) + 1;
    bucket.byPlayer[ev.playerId] = (bucket.byPlayer[ev.playerId] ?? 0) + 1;
  }

  const cromosByDay = dates14.map(date => ({ date, total: 0, byPlayer: {} as Record<string, number> }));
  const cromosIndex: Record<string, typeof cromosByDay[number]> = Object.fromEntries(cromosByDay.map(b => [b.date, b]));
  for (const row of cromoRaw) {
    const bucket = cromosIndex[row.date];
    if (!bucket) continue;
    bucket.total++;
    bucket.byPlayer[row.playerId] = (bucket.byPlayer[row.playerId] ?? 0) + 1;
  }

  const photosByDay = dates14.map(date => ({ date, uploaded: 0, generated: 0, byPlayer: {} as Record<string, number> }));
  const photosIndex: Record<string, typeof photosByDay[number]> = Object.fromEntries(photosByDay.map(b => [b.date, b]));
  for (const row of photoRaw) {
    const bucket = photosIndex[row.date];
    if (!bucket) continue;
    if (row.source === "uploaded") bucket.uploaded++; else bucket.generated++;
    bucket.byPlayer[row.playerId] = (bucket.byPlayer[row.playerId] ?? 0) + 1;
  }

  const chatByDay = dates14.map(date => ({ date, total: 0, byPlayer: {} as Record<string, number> }));
  const chatIndex: Record<string, typeof chatByDay[number]> = Object.fromEntries(chatByDay.map(b => [b.date, b]));
  for (const row of chatRaw) {
    const bucket = chatIndex[row.date];
    if (!bucket) continue;
    bucket.total++;
    bucket.byPlayer[row.playerId] = (bucket.byPlayer[row.playerId] ?? 0) + 1;
  }

  const totals = {
    players: players.length,
    humanPlayers: players.filter(p => !p.isBot).length,
    picksTotal: players.reduce((acc, p) => acc + p.picks.groupTotal, 0),
    photosGeneratedTotal: players.reduce((acc, p) => acc + p.photo.historyGenerated, 0),
    photosUploadedTotal: players.reduce((acc, p) => acc + p.photo.historyUploaded, 0),
    cromosTotal: players.reduce((acc, p) => acc + p.cromo.total, 0),
    chatMessagesTotal: players.reduce((acc, p) => acc + p.chat.messages, 0),
    pushDevicesTotal: players.reduce((acc, p) => acc + p.push.devices, 0),
    activityTotal7d: activity.length,
  };

  const payload: StatsPayload = {
    generatedAt: Date.now(),
    totals,
    players,
    activityByDay,
    cromosByDay,
    chatByDay,
    photosByDay,
    fixturesConsensus: consensus,
  };

  return Response.json(payload, {
    headers: { "Cache-Control": "private, no-store" },
  });
}
