// Recover photo_history entries from GCS for the logged-in player. Scans
// gs://q26-cromo-portraits/profiles/{playerId}/history/ and creates a
// Firestore doc for any object that doesn't already have one. Idempotent.
// Fixes the case where a user accidentally deleted history entries via the
// old delete-on-tap UI but the GCS objects are still alive.

import { readAuth } from "@/lib/auth-server";
import { db } from "@/lib/firestore-server";
import { getStorage, CROMO_BUCKET } from "@/lib/avatar-image";
import { PLAYERS } from "@/data/players";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const COLLECTION = "player_avatars";

function knownPlayer(id: string): boolean {
  return PLAYERS.some(p => p.id === id);
}

export async function POST() {
  const auth = await readAuth();
  if (!auth) return Response.json({ ok: false, error: "unauthorized" }, { status: 401 });
  if (auth.playerId === "ai") return Response.json({ ok: false, error: "forbidden" }, { status: 403 });
  if (!knownPlayer(auth.playerId)) return Response.json({ ok: false, error: "unknown_player" }, { status: 400 });

  const prefix = `profiles/${auth.playerId}/history/`;
  const [files] = await getStorage().bucket(CROMO_BUCKET).getFiles({ prefix });

  const subcol = db.collection(COLLECTION).doc(auth.playerId).collection("photo_history");
  const existing = await subcol.get();
  const knownUrls = new Set<string>();
  for (const d of existing.docs) {
    const u = (d.data() as { url?: string }).url;
    if (u) knownUrls.add(u);
  }

  const recovered: Array<{ url: string; source: string; createdAt: number }> = [];
  for (const f of files) {
    const url = `https://storage.googleapis.com/${CROMO_BUCKET}/${f.name}`;
    if (knownUrls.has(url)) continue;
    const base = f.name.slice(prefix.length); // e.g. "1781318991701.png" or "1781346369929_uploaded.jpg"
    const tsMatch = /^(\d{10,16})/.exec(base);
    const createdAt = tsMatch ? Number(tsMatch[1]) : Date.now();
    const source = /_uploaded\./i.test(base) ? "uploaded" : "generated";
    const ref = subcol.doc();
    await ref.set({
      url,
      source,
      presetId: null,
      prompt: null,
      createdAt,
      recovered: true,
    });
    recovered.push({ url, source, createdAt });
  }

  return Response.json({
    ok: true,
    scanned: files.length,
    alreadyTracked: knownUrls.size,
    recovered: recovered.length,
    items: recovered.sort((a, b) => b.createdAt - a.createdAt),
  });
}
