// Upload a user-supplied photo into the player's photo history AND
// activate it as the player's profile photo in the same shot — the
// owner asked us to skip the "now go to historial and tap Use this"
// extra step. Multipart form (field name: "file"). Accepts jpg/png/webp,
// max 12MB. Client pre-resizes to 2048px JPEG 0.9.

import { NextRequest } from "next/server";
import { readAuth } from "@/lib/auth-server";
import { db } from "@/lib/firestore-server";
import { uploadToGcs } from "@/lib/avatar-image";
import { PLAYERS } from "@/data/players";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const COLLECTION = "player_avatars";
const CROMO_COLLECTION = "cromo_portraits";
const MAX_BYTES = 12 * 1024 * 1024;

function todayKey(): string {
  return new Intl.DateTimeFormat("en-CA", {
    timeZone: "America/New_York",
    year: "numeric", month: "2-digit", day: "2-digit",
  }).format(new Date());
}
const ALLOWED_MIME: Record<string, string> = {
  "image/jpeg": "jpg",
  "image/jpg": "jpg",
  "image/png": "png",
  "image/webp": "webp",
};

function knownPlayer(id: string): boolean {
  return PLAYERS.some(p => p.id === id);
}

export async function POST(req: NextRequest) {
  const auth = await readAuth();
  if (!auth) return Response.json({ ok: false, error: "unauthorized" }, { status: 401 });
  if (auth.playerId === "ai") return Response.json({ ok: false, error: "forbidden" }, { status: 403 });
  if (!knownPlayer(auth.playerId)) return Response.json({ ok: false, error: "unknown_player" }, { status: 400 });

  let form: FormData;
  try {
    form = await req.formData();
  } catch (err) {
    console.error("[photo/upload] formData parse failed", err);
    return Response.json({ ok: false, error: "invalid_multipart" }, { status: 400 });
  }
  const file = form.get("file");
  if (!file || typeof file === "string") {
    return Response.json({ ok: false, error: "file_missing" }, { status: 400 });
  }
  const blob = file as File;
  const ext = ALLOWED_MIME[blob.type];
  if (!ext) {
    return Response.json({ ok: false, error: "bad_mime", got: blob.type }, { status: 400 });
  }
  if (blob.size > MAX_BYTES) {
    return Response.json({ ok: false, error: "too_large", maxMB: MAX_BYTES / 1024 / 1024 }, { status: 413 });
  }

  const buf = Buffer.from(await blob.arrayBuffer());
  let url: string;
  try {
    const stamp = Date.now();
    url = await uploadToGcs({
      objectName: `profiles/${auth.playerId}/history/${stamp}_uploaded.${ext}`,
      buffer: buf,
      mime: blob.type,
    });
  } catch (err) {
    console.error("[photo/upload] gcs upload failed", err);
    return Response.json({ ok: false, error: "upload_failed" }, { status: 502 });
  }

  const playerRef = db.collection(COLLECTION).doc(auth.playerId);
  const historyRef = playerRef.collection("photo_history").doc();
  const now = Date.now();
  await Promise.all([
    historyRef.set({
      url,
      source: "uploaded",
      presetId: null,
      prompt: null,
      createdAt: now,
    }),
    playerRef.set(
      { url, source: "uploaded", updatedAt: now },
      { merge: true },
    ),
    // Active photo changed → today's cromo is stale.
    db.collection(CROMO_COLLECTION).doc(`${auth.playerId}_${todayKey()}`).delete().catch(() => {}),
  ]);

  return Response.json({ ok: true, url, historyId: historyRef.id, activated: true });
}
