// POST /api/push/unsubscribe — remove a stored subscription by endpoint.
import { NextRequest } from "next/server";
import { readAuth } from "@/lib/auth-server";
import { removeSubscriptionByEndpoint } from "@/lib/push-server";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

type Body = { endpoint?: string };

export async function POST(req: NextRequest) {
  const auth = await readAuth();
  if (!auth) return Response.json({ ok: false, error: "unauthorized" }, { status: 401 });

  let body: Body = {};
  try { body = (await req.json()) as Body; } catch {}
  if (!body.endpoint) return Response.json({ ok: false, error: "endpoint required" }, { status: 400 });

  try {
    await removeSubscriptionByEndpoint(auth.playerId, body.endpoint);
    return Response.json({ ok: true });
  } catch (e) {
    console.error("[/api/push/unsubscribe] error", e);
    return Response.json({ ok: false, error: "internal" }, { status: 500 });
  }
}
