// Admin-only endpoint to patch bracket picks for any player, bypassing lock checks.
// POST /api/admin/patch-picks
// Headers: x-admin-secret: q26admin2026
// Body: { playerId: string, bracket: { R16?: string[], QF?: string[], SF?: string[], FINAL?: string } }
// Returns: { ok: true, updated: { playerId, r16 } }

import { db } from "@/lib/firestore-server";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const ADMIN_SECRET = "q26admin2026";
const PICKS_COLLECTION = "quiniela_charales_picks";

type BracketPatch = {
  R16?: string[];
  QF?: string[];
  SF?: string[];
  FINAL?: string;
};

type PatchBody = {
  playerId?: string;
  bracket?: BracketPatch;
};

const ROUND_SIZES: Record<string, number> = { R16: 8, QF: 4, SF: 2 };

export async function POST(req: Request) {
  // Auth check
  const secret = req.headers.get("x-admin-secret");
  if (secret !== ADMIN_SECRET) {
    return Response.json({ ok: false, error: "forbidden" }, { status: 403 });
  }

  let body: PatchBody;
  try {
    body = await req.json();
  } catch {
    return Response.json({ ok: false, error: "invalid_json" }, { status: 400 });
  }

  const { playerId, bracket: incomingBracket } = body ?? {};

  if (!playerId || typeof playerId !== "string") {
    return Response.json({ ok: false, error: "missing playerId" }, { status: 400 });
  }
  if (!incomingBracket || typeof incomingBracket !== "object") {
    return Response.json({ ok: false, error: "missing bracket" }, { status: 400 });
  }

  try {
    const ref = db.collection(PICKS_COLLECTION).doc(playerId);
    const snap = await ref.get();
    const existing = (snap.exists ? snap.data() : {}) as Record<string, unknown>;
    const prevBracket = (existing.bracket as Record<string, unknown>) ?? {};

    // Build patched bracket: per-slot merge for array rounds (incoming non-empty wins, else keep prev)
    const nextBracket: Record<string, unknown> = { ...prevBracket };

    const arrayRounds = ["R16", "QF", "SF"] as const;
    for (const r of arrayRounds) {
      if (!(r in incomingBracket)) continue; // not patching this round
      const size = ROUND_SIZES[r] ?? 0;
      const inc: string[] = (incomingBracket[r] as string[] | undefined) ?? [];
      const prv: string[] = (prevBracket[r] as string[] | undefined) ?? [];
      const merged: string[] = Array(size).fill("");
      for (let i = 0; i < size; i++) {
        // If incoming[i] is non-empty, overwrite; otherwise keep existing
        merged[i] = inc[i] || prv[i] || "";
      }
      nextBracket[r] = merged;
    }

    if ("FINAL" in incomingBracket && incomingBracket.FINAL) {
      nextBracket.FINAL = incomingBracket.FINAL;
    }

    // Write merged doc — preserve all other fields (group picks, etc.)
    await ref.set(
      { ...existing, playerId, bracket: nextBracket, updatedAt: Date.now() },
      { merge: false },
    );

    const r16 = (nextBracket.R16 as string[] | undefined) ?? [];
    return Response.json({ ok: true, updated: { playerId, r16 } });
  } catch (e) {
    console.error("[/api/admin/patch-picks POST]", e);
    return Response.json({ ok: false, error: "internal" }, { status: 500 });
  }
}
