// Persists HIL feedback from the cromo-compare page to Firestore. Claude reads
// `cromo_feedback/{playerId}_{ts}` on the next turn to iterate identity prompts
// and variant generation. Admin-secret gated via query string (matches the
// parent compare endpoint).

import { NextRequest } from "next/server";
import { db } from "@/lib/firestore-server";
import { PLAYERS } from "@/data/players";
import { isAdminRequest } from "@/lib/admin-gate";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

type VariantVote = { style: string; votes: string[] };
type Body = {
  playerId?: string;
  variants?: Record<string, VariantVote>;
  notes?: string;
};

export async function POST(req: NextRequest) {
  if (!(await isAdminRequest(req))) {
    return Response.json({ ok: false, error: "forbidden" }, { status: 403 });
  }
  let body: Body = {};
  try { body = (await req.json()) as Body; } catch {}
  const playerId = (body.playerId ?? "").trim();
  if (!playerId) return Response.json({ ok: false, error: "playerId_required" }, { status: 400 });
  if (!PLAYERS.some(p => p.id === playerId)) {
    return Response.json({ ok: false, error: "unknown_player" }, { status: 400 });
  }
  const ts = Date.now();
  const id = `${playerId}_${ts}`;
  try {
    await db.collection("cromo_feedback").doc(id).set({
      playerId,
      variants: body.variants ?? {},
      notes: (body.notes ?? "").trim(),
      createdAt: ts,
    });
    return Response.json({ ok: true, id, persisted: true });
  } catch (err) {
    // Local dev usually lacks roles/datastore.user; still return ok so the UI
    // surfaces the feedback (Claude reads server stdout instead).
    console.warn("[cromo-compare/feedback] firestore write failed — logging instead", err instanceof Error ? err.message : err);
    console.warn("[cromo-compare/feedback] PAYLOAD", JSON.stringify({ playerId, variants: body.variants, notes: body.notes }));
    return Response.json({ ok: true, id, persisted: false, note: "logged to server stdout" });
  }
}
