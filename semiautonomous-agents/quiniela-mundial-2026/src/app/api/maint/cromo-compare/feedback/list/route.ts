// Read-side counterpart to feedback POST. Lets the admin / Claude pull the
// latest HIL notes for a player without going through the Firestore console.
//
// GET /api/maint/cromo-compare/feedback/list?playerId=charal&limit=5

import { NextRequest } from "next/server";
import { db } from "@/lib/firestore-server";
import { PLAYERS } from "@/data/players";
import { isAdminRequest } from "@/lib/admin-gate";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET(req: NextRequest) {
  if (!(await isAdminRequest(req))) {
    return Response.json({ ok: false, error: "forbidden" }, { status: 403 });
  }
  const { searchParams } = new URL(req.url);
  const playerId = (searchParams.get("playerId") ?? "").trim();
  const limit = Math.min(parseInt(searchParams.get("limit") ?? "10", 10) || 10, 50);
  if (playerId && !PLAYERS.some(p => p.id === playerId)) {
    return Response.json({ ok: false, error: "unknown_player" }, { status: 400 });
  }
  try {
    let q = db.collection("cromo_feedback").orderBy("createdAt", "desc").limit(limit);
    if (playerId) q = db.collection("cromo_feedback").where("playerId", "==", playerId).orderBy("createdAt", "desc").limit(limit);
    const snap = await q.get();
    const entries = snap.docs.map(d => ({ id: d.id, ...(d.data() as object) }));
    return Response.json({ ok: true, count: entries.length, entries });
  } catch (err) {
    return Response.json({ ok: false, error: err instanceof Error ? err.message : String(err) }, { status: 500 });
  }
}
