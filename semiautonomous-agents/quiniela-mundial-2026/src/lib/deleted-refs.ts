// Soft-delete list for cromo reference photos. Cloud Run filesystem is
// read-only, so we can't physically delete files in public/players/refs/.
// Instead the admin marks them deleted via Firestore; loadRefPhotos and the
// workshop's listRefUrls both consult this list and skip those entries.
//
// For uploaded photos (GCS), the delete endpoint also wipes the underlying
// GCS object + Firestore history doc so the soft-delete is permanent. For
// local refs the soft-delete persists across deploys via the Firestore key.

import { db } from "@/lib/firestore-server";

const COLLECTION = "cromo_deleted_refs";

export async function listDeletedRefs(playerId: string): Promise<Set<string>> {
  try {
    const snap = await db.collection(COLLECTION).doc(playerId).get();
    if (!snap.exists) return new Set();
    const data = snap.data() as { urls?: string[] };
    return new Set(Array.isArray(data?.urls) ? data.urls : []);
  } catch {
    return new Set();
  }
}

export async function addDeletedRef(playerId: string, url: string): Promise<void> {
  const current = await listDeletedRefs(playerId);
  current.add(url);
  await db.collection(COLLECTION).doc(playerId).set({
    urls: Array.from(current),
    updatedAt: Date.now(),
  });
}

export async function removeDeletedRef(playerId: string, url: string): Promise<void> {
  const current = await listDeletedRefs(playerId);
  current.delete(url);
  await db.collection(COLLECTION).doc(playerId).set({
    urls: Array.from(current),
    updatedAt: Date.now(),
  });
}
