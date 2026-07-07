// Admin-secret-gated endpoint to reset a player's active profile photo to
// the public baseline (`public/players/{id}.jpg`). Use after replacing the
// baseline JPG when the player's active doc still points to an old GCS URL.

import { NextRequest } from "next/server";
import { db } from "@/lib/firestore-server";
import { PLAYERS } from "@/data/players";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

type Body = { playerId?: string };

export async function POST(req: NextRequest) {
  const expected = process.env.ADMIN_SECRET;
  if (!expected) return Response.json({ ok: false, error: "admin_disabled" }, { status: 503 });
  if (req.headers.get("x-admin-secret") !== expected) {
    return Response.json({ ok: false, error: "forbidden" }, { status: 403 });
  }
  let body: Body = {};
  try { body = (await req.json()) as Body; } catch {}
  const playerId = (body.playerId ?? "").trim();
  if (!playerId) return Response.json({ ok: false, error: "playerId_required" }, { status: 400 });
  if (!PLAYERS.some(p => p.id === playerId)) {
    return Response.json({ ok: false, error: "unknown_player" }, { status: 400 });
  }
  await db.collection("player_avatars").doc(playerId).set({
    playerId,
    url: null,
    source: "original",
    style: null,
    note: null,
    updatedAt: Date.now(),
  }, { merge: true });
  return Response.json({ ok: true, playerId });
}
