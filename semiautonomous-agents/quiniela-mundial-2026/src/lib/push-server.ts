// Server-side Web Push helpers. VAPID config from env, Firestore-backed
// subscription registry, and small `sendPushToAll` / `sendPushToPlayer` fanout.
import webpush, { type PushSubscription as WPSubscription } from "web-push";
import { createHash } from "node:crypto";
import { db } from "@/lib/firestore-server";

export type PushPayload = {
  title: string;
  body?: string;
  url?: string;
  tag?: string;
  icon?: string;
  badge?: string;
};

type StoredSubscription = {
  playerId: string;
  endpoint: string;
  keys: { p256dh: string; auth: string };
  createdAt: number;
  ua?: string;
};

let _vapidReady = false;
function configureVapid(): boolean {
  if (_vapidReady) return true;
  const pub = process.env.NEXT_PUBLIC_VAPID_PUBLIC_KEY;
  const priv = process.env.VAPID_PRIVATE_KEY;
  const subject = process.env.VAPID_SUBJECT || "mailto:admin@charales.mx";
  if (!pub || !priv) return false;
  webpush.setVapidDetails(subject, pub, priv);
  _vapidReady = true;
  return true;
}

export function endpointHash(endpoint: string): string {
  return createHash("sha256").update(endpoint).digest("hex").slice(0, 24);
}

export async function storeSubscription(
  playerId: string,
  sub: WPSubscription,
  ua?: string,
): Promise<string> {
  const id = endpointHash(sub.endpoint);
  const doc: StoredSubscription = {
    playerId,
    endpoint: sub.endpoint,
    keys: { p256dh: sub.keys.p256dh, auth: sub.keys.auth },
    createdAt: Date.now(),
    ua,
  };
  await db.collection("push_subscriptions").doc(playerId).collection("devices").doc(id).set(doc);
  return id;
}

export async function removeSubscriptionByEndpoint(playerId: string, endpoint: string): Promise<void> {
  const id = endpointHash(endpoint);
  await db.collection("push_subscriptions").doc(playerId).collection("devices").doc(id).delete().catch(() => {});
}

async function listAllSubscriptions(): Promise<Array<{ playerId: string; id: string; sub: StoredSubscription }>> {
  const snap = await db.collectionGroup("devices").get();
  const out: Array<{ playerId: string; id: string; sub: StoredSubscription }> = [];
  for (const d of snap.docs) {
    const data = d.data() as StoredSubscription;
    if (data?.endpoint && data?.keys) out.push({ playerId: data.playerId, id: d.id, sub: data });
  }
  return out;
}

async function listPlayerSubscriptions(playerId: string): Promise<Array<{ id: string; sub: StoredSubscription }>> {
  const snap = await db.collection("push_subscriptions").doc(playerId).collection("devices").get();
  return snap.docs.map(d => ({ id: d.id, sub: d.data() as StoredSubscription }));
}

async function sendOne(sub: StoredSubscription, payload: PushPayload): Promise<"ok" | "gone" | "error"> {
  try {
    await webpush.sendNotification(
      { endpoint: sub.endpoint, keys: sub.keys } as WPSubscription,
      JSON.stringify(payload),
      { TTL: 60 * 60 * 12 },
    );
    return "ok";
  } catch (err: unknown) {
    const status = (err as { statusCode?: number } | null)?.statusCode;
    if (status === 404 || status === 410) return "gone";
    console.error("[push] sendNotification failed", status, err);
    return "error";
  }
}

export async function sendPushToAll(payload: PushPayload): Promise<{ sent: number; pruned: number; failed: number }> {
  if (!configureVapid()) return { sent: 0, pruned: 0, failed: 0 };
  const subs = await listAllSubscriptions();
  let sent = 0, pruned = 0, failed = 0;
  await Promise.all(subs.map(async ({ playerId, id, sub }) => {
    const r = await sendOne(sub, payload);
    if (r === "ok") sent++;
    else if (r === "gone") {
      pruned++;
      await db.collection("push_subscriptions").doc(playerId).collection("devices").doc(id).delete().catch(() => {});
    } else failed++;
  }));
  return { sent, pruned, failed };
}

export async function sendPushToPlayer(playerId: string, payload: PushPayload): Promise<{ sent: number; pruned: number; failed: number }> {
  if (!configureVapid()) return { sent: 0, pruned: 0, failed: 0 };
  const subs = await listPlayerSubscriptions(playerId);
  let sent = 0, pruned = 0, failed = 0;
  await Promise.all(subs.map(async ({ id, sub }) => {
    const r = await sendOne(sub, payload);
    if (r === "ok") sent++;
    else if (r === "gone") {
      pruned++;
      await db.collection("push_subscriptions").doc(playerId).collection("devices").doc(id).delete().catch(() => {});
    } else failed++;
  }));
  return { sent, pruned, failed };
}

export function pushConfigured(): boolean {
  return configureVapid();
}
