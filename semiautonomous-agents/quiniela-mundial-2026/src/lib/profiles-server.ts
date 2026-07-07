// Server-side Firestore CRUD for player profile overrides
// (avatar/photo + custom name + emoji). Mirrors src/lib/profile-overrides.ts.
import { db } from "@/lib/firestore-server";

export const PROFILES_COLLECTION = "quiniela_charales_profiles";

export type ProfileDoc = {
  playerId: string;
  name?: string;
  emoji?: string;
  photoDataUrl?: string;   // base64 data URL (capped at ~700KB)
  updatedAt: number;
};

const MAX_PHOTO_BYTES = 700_000; // hard cap, Firestore doc limit is 1MB

export function validatePhoto(dataUrl: string | undefined): string | null {
  if (!dataUrl) return null;
  if (!dataUrl.startsWith("data:image/")) return "photo must be data:image/* URL";
  // Approx byte length of the data URL string.
  if (dataUrl.length > MAX_PHOTO_BYTES) return `photo too large (${(dataUrl.length / 1024).toFixed(0)} KB > ${MAX_PHOTO_BYTES / 1024} KB)`;
  return null;
}

export async function getProfile(playerId: string): Promise<ProfileDoc | null> {
  const snap = await db.collection(PROFILES_COLLECTION).doc(playerId).get();
  if (!snap.exists) return null;
  return snap.data() as ProfileDoc;
}

export async function listProfiles(): Promise<Record<string, ProfileDoc>> {
  const qs = await db.collection(PROFILES_COLLECTION).get();
  const out: Record<string, ProfileDoc> = {};
  qs.forEach(doc => { out[doc.id] = doc.data() as ProfileDoc; });
  return out;
}

export async function upsertProfile(playerId: string, patch: Partial<ProfileDoc>): Promise<ProfileDoc> {
  const ref = db.collection(PROFILES_COLLECTION).doc(playerId);
  const snap = await ref.get();
  const current = snap.exists ? (snap.data() as ProfileDoc) : { playerId, updatedAt: 0 };
  const next: ProfileDoc = { ...current, ...patch, playerId, updatedAt: Date.now() };
  // Strip empty strings (lets the caller delete a field by sending "").
  if (patch.name === "") delete next.name;
  if (patch.emoji === "") delete next.emoji;
  if (patch.photoDataUrl === "") delete next.photoDataUrl;
  await ref.set(next);
  return next;
}
