// Admin-only: backfill a player's pick bypassing the kickoff lock.
// Used when a player's manual pick never reached Firestore due to a sync bug.
import { NextRequest } from "next/server";
import { db, PINS_COLLECTION as _ } from "@/lib/firestore-server";
import { PICKS_COLLECTION } from "@/lib/predictions-server";

void _;
export const runtime = "nodejs";
export const dynamic = "force-dynamic";

type Body = {
  playerId: string;
  group?: Record<string, { pick: "H" | "D" | "A"; homeGoals?: number; awayGoals?: number; source?: string }>;
};

export async function POST(req: NextRequest) {
  const expected = process.env.ADMIN_SECRET;
  if (!expected) return Response.json({ error: "admin_disabled" }, { status: 503 });
  if (req.headers.get("x-admin-secret") !== expected) return Response.json({ error: "forbidden" }, { status: 403 });
  const body = (await req.json()) as Body;
  if (!body?.playerId) return Response.json({ error: "missing_playerId" }, { status: 400 });
  const ref = db.collection(PICKS_COLLECTION).doc(body.playerId);
  const snap = await ref.get();
  const cur = (snap.exists ? snap.data() : { playerId: body.playerId, group: {}, bracket: {} }) as Record<string, unknown>;
  const curGroup = (cur.group as Record<string, unknown>) || {};
  const merged = { ...curGroup };
  for (const [fxId, pick] of Object.entries(body.group || {})) {
    merged[fxId] = { ...pick, source: pick.source ?? "manual-backfill" };
  }
  const next = { ...cur, playerId: body.playerId, group: merged, updatedAt: Date.now() };
  await ref.set(next, { merge: false });
  return Response.json({ ok: true, playerId: body.playerId, groupCount: Object.keys(merged).length });
}
