// POST /api/push/subscribe — store a Web Push subscription for the logged-in
// player. Requires the auth cookie; the client passes the PushSubscription
// JSON serialized from `pushManager.subscribe()`.
import { NextRequest } from "next/server";
import { readAuth } from "@/lib/auth-server";
import { storeSubscription } from "@/lib/push-server";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

type Body = {
  subscription?: {
    endpoint?: string;
    keys?: { p256dh?: string; auth?: string };
  };
};

export async function POST(req: NextRequest) {
  const auth = await readAuth();
  if (!auth) return Response.json({ ok: false, error: "unauthorized" }, { status: 401 });

  let body: Body = {};
  try { body = (await req.json()) as Body; } catch {}
  const sub = body.subscription;
  if (!sub?.endpoint || !sub.keys?.p256dh || !sub.keys?.auth) {
    return Response.json({ ok: false, error: "invalid subscription" }, { status: 400 });
  }

  try {
    const id = await storeSubscription(
      auth.playerId,
      { endpoint: sub.endpoint, keys: { p256dh: sub.keys.p256dh, auth: sub.keys.auth } },
      req.headers.get("user-agent") || undefined,
    );
    return Response.json({ ok: true, id });
  } catch (e) {
    console.error("[/api/push/subscribe] error", e);
    return Response.json({ ok: false, error: "internal" }, { status: 500 });
  }
}
