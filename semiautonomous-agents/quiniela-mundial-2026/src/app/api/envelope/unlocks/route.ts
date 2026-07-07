// GET /api/envelope/unlocks — read-only collection of all unlocked rewards
// (visuals, insights, spoilers, previews, badges) for the logged-in player.
import { readAuth } from "@/lib/auth-server";
import { db } from "@/lib/firestore-server";
import type { UnlockEntry } from "@/lib/envelope";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET() {
  const auth = await readAuth();
  if (!auth) {
    return Response.json({ ok: false, error: "unauthorized" }, { status: 401 });
  }
  const snap = await db.collection("player_unlocks").doc(auth.playerId).get();
  const entries: UnlockEntry[] = snap.exists ? ((snap.data()?.entries as UnlockEntry[]) ?? []) : [];
  // Newest first so the gallery feels current.
  entries.sort((a, b) => (b.awardedAt ?? 0) - (a.awardedAt ?? 0));
  return Response.json({ ok: true, entries });
}
