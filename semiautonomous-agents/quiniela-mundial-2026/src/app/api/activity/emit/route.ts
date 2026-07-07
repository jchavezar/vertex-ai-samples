// Admin-gated event emitter for testing/seeding the feed. Real events are
// emitted server-side from the relevant endpoints (see predictions PUT).
import { NextRequest } from "next/server";
import { appendActivity, type ActivityType } from "@/lib/activity-feed-server";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const VALID_TYPES: ActivityType[] = ["pick_made", "leader_change", "streak", "exact_score"];

export async function POST(req: NextRequest) {
  const expected = process.env.ADMIN_SECRET;
  if (!expected) return Response.json({ ok: false, error: "admin_disabled" }, { status: 503 });
  if (req.headers.get("x-admin-secret") !== expected) {
    return Response.json({ ok: false, error: "forbidden" }, { status: 403 });
  }
  type Body = {
    type?: ActivityType;
    playerId?: string;
    text?: string;
    fixtureId?: string;
    metadata?: Record<string, unknown>;
  };
  let body: Body = {};
  try { body = (await req.json()) as Body; } catch {}
  if (!body.type || !VALID_TYPES.includes(body.type)) {
    return Response.json({ ok: false, error: "invalid type" }, { status: 400 });
  }
  if (!body.playerId || typeof body.playerId !== "string") {
    return Response.json({ ok: false, error: "playerId required" }, { status: 400 });
  }
  if (!body.text || typeof body.text !== "string") {
    return Response.json({ ok: false, error: "text required" }, { status: 400 });
  }
  try {
    await appendActivity({
      type: body.type,
      playerId: body.playerId,
      text: body.text,
      fixtureId: body.fixtureId,
      metadata: body.metadata,
    });
    return Response.json({ ok: true });
  } catch (e) {
    console.error("[/api/activity/emit POST] error", e);
    return Response.json({ ok: false, error: "internal" }, { status: 500 });
  }
}
