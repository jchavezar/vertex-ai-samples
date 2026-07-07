// POST /api/push/test — admin-gated test push to all subscribers (or one
// player). Use for smoke-testing VAPID + service worker push handler.
import { NextRequest } from "next/server";
import { sendPushToAll, sendPushToPlayer, pushConfigured } from "@/lib/push-server";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

type Body = {
  title?: string;
  body?: string;
  url?: string;
  tag?: string;
  playerId?: string;
};

export async function POST(req: NextRequest) {
  const expected = process.env.ADMIN_SECRET;
  if (!expected) return Response.json({ ok: false, error: "admin_disabled" }, { status: 503 });
  if (req.headers.get("x-admin-secret") !== expected) {
    return Response.json({ ok: false, error: "forbidden" }, { status: 403 });
  }
  if (!pushConfigured()) return Response.json({ ok: false, error: "vapid_missing" }, { status: 503 });

  let body: Body = {};
  try { body = (await req.json()) as Body; } catch {}

  const payload = {
    title: body.title || "Charales 2026",
    body: body.body || "Notificación de prueba",
    url: body.url || "/",
    tag: body.tag || "test",
  };

  const result = body.playerId
    ? await sendPushToPlayer(body.playerId, payload)
    : await sendPushToAll(payload);
  return Response.json({ ok: true, ...result });
}
