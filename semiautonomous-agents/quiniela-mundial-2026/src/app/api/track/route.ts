// Ingest endpoint for client telemetry. Fire-and-forget batches land here via
// sendBeacon. We attach the authed playerId (if any) server-side so the client
// payload doesn't need to carry it.

import { NextRequest } from "next/server";
import { FieldValue } from "@google-cloud/firestore";
import { readAuth } from "@/lib/auth-server";
import { db } from "@/lib/firestore-server";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const MAX_EVENTS = 50;
const COLLECTION = "usage_events";

type IncomingEvent = {
  event: string;
  props?: unknown;
  ts: number;
  path?: string;
  sessionId?: string;
};

function isPlainSerializable(v: unknown, depth = 0): boolean {
  if (depth > 4) return false;
  if (v === null) return true;
  const t = typeof v;
  if (t === "string" || t === "number" || t === "boolean") return true;
  if (Array.isArray(v)) return v.every((x) => isPlainSerializable(x, depth + 1));
  if (t === "object") {
    return Object.values(v as Record<string, unknown>).every((x) =>
      isPlainSerializable(x, depth + 1),
    );
  }
  return false;
}

function clean(s: unknown, max: number): string | undefined {
  if (typeof s !== "string") return undefined;
  if (s.length === 0) return undefined;
  return s.slice(0, max);
}

function firstIp(header: string | null): string | null {
  if (!header) return null;
  const first = header.split(",")[0]?.trim();
  if (!first) return null;
  return first.slice(0, 64);
}

export async function POST(req: NextRequest) {
  let body: { events?: unknown } = {};
  try {
    body = await req.json();
  } catch {
    return Response.json({ ok: true, n: 0 });
  }
  const incoming = Array.isArray(body?.events) ? (body.events as unknown[]) : [];
  if (incoming.length === 0) return Response.json({ ok: true, n: 0 });

  const auth = await readAuth();
  const playerId = auth?.playerId ?? null;
  const userAgent = (req.headers.get("user-agent") ?? "").slice(0, 200) || null;
  const ip = firstIp(req.headers.get("x-forwarded-for"));

  const slice = incoming.slice(0, MAX_EVENTS) as IncomingEvent[];
  const batch = db.batch();
  let written = 0;
  for (const raw of slice) {
    if (!raw || typeof raw !== "object") continue;
    const event = clean(raw.event, 64);
    if (!event) continue;
    const ts = typeof raw.ts === "number" && Number.isFinite(raw.ts) ? raw.ts : Date.now();
    const path = clean(raw.path, 200) ?? null;
    const sessionId = clean(raw.sessionId, 64) ?? null;
    let props: unknown = null;
    if (raw.props !== undefined && raw.props !== null) {
      if (isPlainSerializable(raw.props)) props = raw.props;
    }
    const ref = db.collection(COLLECTION).doc();
    batch.set(ref, {
      playerId,
      event,
      props,
      ts,
      path,
      sessionId,
      userAgent,
      ip,
      createdAt: FieldValue.serverTimestamp(),
    });
    written++;
  }

  if (written > 0) {
    try {
      await batch.commit();
    } catch (e) {
      // Swallow — never block the client on analytics writes.
      console.warn("[track] batch commit failed", (e as Error).message);
    }
  }

  return Response.json({ ok: true, n: written });
}
