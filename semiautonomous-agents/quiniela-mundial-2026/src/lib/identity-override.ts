// Firestore-backed override for PLAYER_IDENTITY text. Lets the admin tune a
// player's identity-lock from the workshop UI without redeploying the file.
// generatePortrait reads override first, falls back to the hardcoded entry,
// then to a generic fallback — so deleting the override restores file behavior.

import { db } from "@/lib/firestore-server";

export const IDENTITY_OVERRIDE_COLLECTION = "cromo_identity_overrides";

export async function getIdentityOverride(playerId: string): Promise<string | null> {
  try {
    const snap = await db.collection(IDENTITY_OVERRIDE_COLLECTION).doc(playerId).get();
    if (!snap.exists) return null;
    const data = snap.data() as { text?: string };
    const t = data?.text;
    return typeof t === "string" && t.trim().length > 0 ? t : null;
  } catch {
    return null;
  }
}

export async function setIdentityOverride(playerId: string, text: string): Promise<void> {
  await db.collection(IDENTITY_OVERRIDE_COLLECTION).doc(playerId).set({
    text,
    updatedAt: Date.now(),
  });
}

export async function deleteIdentityOverride(playerId: string): Promise<void> {
  await db.collection(IDENTITY_OVERRIDE_COLLECTION).doc(playerId).delete();
}
