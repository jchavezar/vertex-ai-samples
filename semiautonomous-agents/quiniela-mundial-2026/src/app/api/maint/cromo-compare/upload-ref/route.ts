// Admin upload of a new reference photo straight into the cromo identity bank.
// Saves to GCS at refs/{playerId}/{ts}.{ext} and writes a Firestore index doc
// so listRefUrls/loadRefPhotos can find it without touching the local FS.
//
// Accepts raw image bytes (from clipboard paste or drag-drop). Content-type
// dictates the extension. The uploaded image becomes an ACTIVE ref —
// immediately fed to the model on the next generation.

import { NextRequest } from "next/server";
import { Storage } from "@google-cloud/storage";
import { db } from "@/lib/firestore-server";
import { PLAYERS } from "@/data/players";
import { isAdminRequest } from "@/lib/admin-gate";
import { addActiveGcsRef } from "@/lib/active-gcs-refs";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const BUCKET = process.env.CROMO_BUCKET || "q26-cromo-portraits";
const MAX_BYTES = 8 * 1024 * 1024; // 8 MB

let _storage: Storage | null = null;
function getStorage(): Storage {
  if (!_storage) _storage = new Storage({ projectId: process.env.GOOGLE_CLOUD_PROJECT || "vtxdemos" });
  return _storage;
}

function extFor(mime: string): string | null {
  if (mime === "image/jpeg" || mime === "image/jpg") return "jpg";
  if (mime === "image/png") return "png";
  if (mime === "image/webp") return "webp";
  return null;
}

export async function POST(req: NextRequest) {
  if (!(await isAdminRequest(req))) {
    return Response.json({ ok: false, error: "forbidden" }, { status: 403 });
  }
  const { searchParams } = new URL(req.url);
  const playerId = (searchParams.get("playerId") ?? "").trim();
  if (!playerId || !PLAYERS.some(p => p.id === playerId)) {
    return Response.json({ ok: false, error: "bad_playerId" }, { status: 400 });
  }
  const mime = req.headers.get("content-type") || "application/octet-stream";
  const ext = extFor(mime);
  if (!ext) {
    return Response.json({ ok: false, error: `bad_mime:${mime}` }, { status: 400 });
  }
  const buf = Buffer.from(await req.arrayBuffer());
  if (buf.length === 0) return Response.json({ ok: false, error: "empty_body" }, { status: 400 });
  if (buf.length > MAX_BYTES) return Response.json({ ok: false, error: "too_large" }, { status: 413 });

  const ts = Date.now();
  const objectName = `profiles/${playerId}/history/${ts}_uploaded.${ext}`;
  const file = getStorage().bucket(BUCKET).file(objectName);
  await file.save(buf, { contentType: mime, metadata: { cacheControl: "public, max-age=86400" } });
  const url = `https://storage.googleapis.com/${BUCKET}/${objectName}`;

  // Add to the active-GCS-refs list — loadRefPhotos picks it up on the next
  // generation, no redeploy required.
  await addActiveGcsRef(playerId, url);

  return Response.json({ ok: true, playerId, url });
}
