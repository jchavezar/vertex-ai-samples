// Admin-only delete for cromo reference photos. Three sources, two strategies:
//
// 1. GCS uploaded photos (profiles/{playerId}/history/...): hard-delete the
//    Firestore photo_history doc + the GCS object. Permanent, no soft-delete
//    needed since the underlying file is gone.
// 2. Local refs (/players/{playerId}.jpg, /players/refs/{playerId}/...): the
//    container FS is read-only, so add the URL to a Firestore soft-delete list.
//    listRefUrls + loadRefPhotos both filter against this list.

import { NextRequest } from "next/server";
import { Storage } from "@google-cloud/storage";
import { db } from "@/lib/firestore-server";
import { PLAYERS } from "@/data/players";
import { isAdminRequest } from "@/lib/admin-gate";
import { addDeletedRef } from "@/lib/deleted-refs";
import { removeActiveGcsRef } from "@/lib/active-gcs-refs";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const BUCKET = process.env.CROMO_BUCKET || "q26-cromo-portraits";
let _storage: Storage | null = null;
function getStorage(): Storage {
  if (!_storage) _storage = new Storage({ projectId: process.env.GOOGLE_CLOUD_PROJECT || "vtxdemos" });
  return _storage;
}

export async function DELETE(req: NextRequest) {
  if (!(await isAdminRequest(req))) {
    return Response.json({ ok: false, error: "forbidden" }, { status: 403 });
  }
  const { searchParams } = new URL(req.url);
  const playerId = (searchParams.get("playerId") ?? "").trim();
  const url = (searchParams.get("url") ?? "").trim();
  if (!playerId || !PLAYERS.some(p => p.id === playerId)) {
    return Response.json({ ok: false, error: "bad_playerId" }, { status: 400 });
  }
  if (!url) {
    return Response.json({ ok: false, error: "url_required" }, { status: 400 });
  }

  // Case 1: GCS-uploaded — hard delete (Firestore + GCS).
  const gcsPrefix = `https://storage.googleapis.com/${BUCKET}/`;
  if (url.startsWith(gcsPrefix)) {
    const objectName = url.slice(gcsPrefix.length);
    // Find the matching photo_history doc to delete (URL match within
    // player_avatars/{playerId}/photo_history).
    try {
      const histSnap = await db.collection("player_avatars").doc(playerId).collection("photo_history").get();
      for (const doc of histSnap.docs) {
        const d = doc.data() as { url?: string };
        if (d.url === url) {
          await doc.ref.delete();
        }
      }
    } catch (e) {
      console.warn("[ref delete] firestore doc removal failed", e);
    }
    try {
      await getStorage().bucket(BUCKET).file(objectName).delete({ ignoreNotFound: true });
    } catch (e) {
      console.warn("[ref delete] gcs file removal failed", e);
    }
    // Also drop from active-GCS-refs list if it was a workshop upload.
    await removeActiveGcsRef(playerId, url);
    return Response.json({ ok: true, mode: "hard", playerId, url });
  }

  // Case 2: local file → soft-delete via Firestore list.
  await addDeletedRef(playerId, url);
  return Response.json({ ok: true, mode: "soft", playerId, url });
}
