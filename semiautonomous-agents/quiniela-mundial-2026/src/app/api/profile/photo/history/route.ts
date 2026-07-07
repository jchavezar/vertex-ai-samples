// List the logged-in player's photo history (generated + uploaded).
// Newest first, up to 60 entries.

import { readAuth } from "@/lib/auth-server";
import { db } from "@/lib/firestore-server";
import { PLAYERS } from "@/data/players";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const COLLECTION = "player_avatars";
const LIMIT = 60;

function knownPlayer(id: string): boolean {
  return PLAYERS.some(p => p.id === id);
}

export async function GET() {
  const auth = await readAuth();
  if (!auth) return Response.json({ ok: false, error: "unauthorized" }, { status: 401 });
  if (auth.playerId === "ai") return Response.json({ ok: false, error: "forbidden" }, { status: 403 });
  if (!knownPlayer(auth.playerId)) return Response.json({ ok: false, error: "unknown_player" }, { status: 400 });

  const snap = await db
    .collection(COLLECTION)
    .doc(auth.playerId)
    .collection("photo_history")
    .orderBy("createdAt", "desc")
    .limit(LIMIT)
    .get();

  const items = snap.docs.map(d => {
    const data = d.data() as {
      url?: string;
      source?: string;
      presetId?: string | null;
      prompt?: string | null;
      createdAt?: number;
    };
    return {
      id: d.id,
      url: data.url ?? "",
      source: data.source ?? "generated",
      presetId: data.presetId ?? null,
      prompt: data.prompt ?? null,
      createdAt: data.createdAt ?? 0,
    };
  });

  return Response.json({ ok: true, items });
}
