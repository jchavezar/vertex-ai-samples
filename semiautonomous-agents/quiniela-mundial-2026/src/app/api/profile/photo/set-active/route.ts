// Set a previously-uploaded or generated photo (or the original baseline)
// as the active profile photo for the logged-in player. Writes to
// `player_avatars/{id}` so `useProfileAvatar` picks it up.

import { NextRequest } from "next/server";
import { readAuth } from "@/lib/auth-server";
import { db } from "@/lib/firestore-server";
import { CROMO_BUCKET } from "@/lib/avatar-image";
import { PLAYERS } from "@/data/players";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const COLLECTION = "player_avatars";

function knownPlayer(id: string): boolean {
  return PLAYERS.some(p => p.id === id);
}

// URL must belong to this player's history OR be their public baseline photo.
function urlAllowedFor(playerId: string, url: string, source: string): boolean {
  if (source === "original") {
    return /^\/players\/[a-z0-9_-]+\.(jpg|jpeg|png|webp)$/i.test(url);
  }
  const re = new RegExp(`^https://storage\\.googleapis\\.com/${CROMO_BUCKET}/profiles/${playerId}/history/`);
  return re.test(url);
}

export async function POST(req: NextRequest) {
  const auth = await readAuth();
  if (!auth) return Response.json({ ok: false, error: "unauthorized" }, { status: 401 });
  if (auth.playerId === "ai") return Response.json({ ok: false, error: "forbidden" }, { status: 403 });
  if (!knownPlayer(auth.playerId)) return Response.json({ ok: false, error: "unknown_player" }, { status: 400 });

  type Body = { url?: string; source?: "generated" | "uploaded" | "original" };
  let body: Body = {};
  try { body = (await req.json()) as Body; } catch {}
  const url = (body.url ?? "").trim();
  const source = body.source ?? "generated";
  if (!url) return Response.json({ ok: false, error: "url_required" }, { status: 400 });
  if (!["generated", "uploaded", "original"].includes(source)) {
    return Response.json({ ok: false, error: "bad_source" }, { status: 400 });
  }
  if (!urlAllowedFor(auth.playerId, url, source)) {
    return Response.json({ ok: false, error: "url_not_allowed" }, { status: 403 });
  }

  const ref = db.collection(COLLECTION).doc(auth.playerId);
  if (source === "original") {
    // null active URL → useProfileAvatar falls back to the public baseline.
    await ref.set({
      playerId: auth.playerId,
      url: null,
      source: "original",
      style: null,
      note: null,
      updatedAt: Date.now(),
    }, { merge: true });
  } else {
    await ref.set({
      playerId: auth.playerId,
      url,
      source,
      updatedAt: Date.now(),
    }, { merge: true });
  }

  // Los cromos toman la foto activa como referencia, así que activar otra
  // foto invalida el cromo actual. El stale-guard en /api/cromos/portrait
  // detecta updatedAt > cromo.createdAt y regenera en el próximo GET.

  return Response.json({ ok: true, url: source === "original" ? null : url, source });
}
