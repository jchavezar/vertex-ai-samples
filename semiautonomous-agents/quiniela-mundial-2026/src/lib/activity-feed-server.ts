// Activity feed: tiny social stream so the 9 charales feel each other's moves.
// Each event is one Firestore doc; the home page polls /api/activity every 30s.
import { db } from "@/lib/firestore-server";

export const ACTIVITY_COLLECTION = "activity_feed";
const MAX_AGE_MS = 7 * 24 * 60 * 60 * 1000;

export type ActivityType = "pick_made" | "leader_change" | "streak" | "exact_score";

export type ActivityEvent = {
  id: string;
  type: ActivityType;
  playerId: string;
  text: string;
  fixtureId?: string;
  createdAt: number;
  metadata?: Record<string, unknown>;
};

export type ActivityInput = Omit<ActivityEvent, "id" | "createdAt"> & {
  createdAt?: number;
};

function stripUndefined<T extends Record<string, unknown>>(obj: T): T {
  const out: Record<string, unknown> = {};
  for (const [k, v] of Object.entries(obj)) {
    if (v !== undefined) out[k] = v;
  }
  return out as T;
}

export async function appendActivity(event: ActivityInput): Promise<void> {
  const createdAt = event.createdAt ?? Date.now();
  const ref = db.collection(ACTIVITY_COLLECTION).doc();
  const doc = stripUndefined({
    type: event.type,
    playerId: event.playerId,
    text: event.text,
    fixtureId: event.fixtureId,
    createdAt,
    metadata: event.metadata,
  });
  await ref.set(doc);
}

// Debounced variant for pick_made: if the same player+fixture posted in the
// last `windowMs`, update that doc's text/createdAt instead of appending a new
// one. Keeps the feed from spamming when someone toggles a pick rapidly.
export async function appendOrUpdateRecentPick(
  playerId: string,
  fixtureId: string,
  text: string,
  windowMs = 60_000,
): Promise<void> {
  const cutoff = Date.now() - windowMs;
  const snap = await db
    .collection(ACTIVITY_COLLECTION)
    .where("type", "==", "pick_made")
    .where("playerId", "==", playerId)
    .where("fixtureId", "==", fixtureId)
    .where("createdAt", ">=", cutoff)
    .orderBy("createdAt", "desc")
    .limit(1)
    .get();
  const now = Date.now();
  if (!snap.empty) {
    await snap.docs[0].ref.update({ text, createdAt: now });
    return;
  }
  await appendActivity({ type: "pick_made", playerId, fixtureId, text, createdAt: now });
}

export async function getRecentActivity(limit = 30): Promise<ActivityEvent[]> {
  const cutoff = Date.now() - MAX_AGE_MS;
  const snap = await db
    .collection(ACTIVITY_COLLECTION)
    .orderBy("createdAt", "desc")
    .limit(limit)
    .get();
  const events: ActivityEvent[] = [];
  for (const doc of snap.docs) {
    const data = doc.data() as Omit<ActivityEvent, "id">;
    if (typeof data.createdAt !== "number" || data.createdAt < cutoff) continue;
    events.push({ id: doc.id, ...data });
  }
  return events;
}
