// Workshop-uploaded refs that live in GCS (not in the read-only Cloud Run FS).
// The list of URLs lives in Firestore at cromo_active_gcs_refs/{playerId}.
// Both loadRefPhotos (generation) and listRefUrls (workshop UI) consume this
// list so a workshop upload becomes an active ref on the very next render —
// no redeploy needed.

import { db } from "@/lib/firestore-server";

const COLLECTION = "cromo_active_gcs_refs";

export async function listActiveGcsRefs(playerId: string): Promise<string[]> {
  try {
    const snap = await db.collection(COLLECTION).doc(playerId).get();
    if (!snap.exists) return [];
    const data = snap.data() as { urls?: string[] };
    return Array.isArray(data?.urls) ? data.urls.filter(u => typeof u === "string") : [];
  } catch {
    return [];
  }
}

export async function addActiveGcsRef(playerId: string, url: string): Promise<void> {
  const current = await listActiveGcsRefs(playerId);
  if (current.includes(url)) return;
  current.push(url);
  await db.collection(COLLECTION).doc(playerId).set({
    urls: current,
    updatedAt: Date.now(),
  });
}

export async function removeActiveGcsRef(playerId: string, url: string): Promise<void> {
  const current = await listActiveGcsRefs(playerId);
  const next = current.filter(u => u !== url);
  if (next.length === current.length) return;
  await db.collection(COLLECTION).doc(playerId).set({
    urls: next,
    updatedAt: Date.now(),
  });
}
