"use client";

// One-shot migration: a player's photo lives in TWO places historically —
// localStorage `q26_profile_overrides[id].photoDataUrl` (legacy ProfileEditor
// base64 path) and the server's `player_avatars/{id}` (new studio path). Only
// the latter is cross-device. If a device has a local-only photoDataUrl that
// the server doesn't know about, the user sees it on that device and nowhere
// else. Detect that, upload the data URL to the studio so it becomes canonical,
// then clear local so future renders use the server URL.

import { loadOverrides, setOverride } from "@/lib/profile-overrides";
import { notifyProfileAvatarUpdated } from "@/lib/profile-avatar";

const FLAG = "q26_photo_migrated";

function dataUrlToBlob(dataUrl: string): Blob | null {
  const m = /^data:(image\/[a-zA-Z+]+);base64,(.+)$/.exec(dataUrl);
  if (!m) return null;
  const [, mime, b64] = m;
  try {
    const bin = atob(b64);
    const len = bin.length;
    const buf = new Uint8Array(len);
    for (let i = 0; i < len; i++) buf[i] = bin.charCodeAt(i);
    return new Blob([buf], { type: mime });
  } catch {
    return null;
  }
}

export async function migrateLocalPhotoIfNeeded(playerId: string): Promise<void> {
  if (typeof window === "undefined") return;
  if (!playerId || playerId === "ai") return;

  const flagKey = `${FLAG}:${playerId}`;
  if (localStorage.getItem(flagKey) === "1") return;

  const overrides = loadOverrides();
  const dataUrl = overrides[playerId]?.photoDataUrl;
  if (!dataUrl || !dataUrl.startsWith("data:image/")) {
    localStorage.setItem(flagKey, "1");
    return;
  }

  let serverHasPhoto = false;
  try {
    const r = await fetch(`/api/avatars/profile?playerId=${encodeURIComponent(playerId)}`, { cache: "no-store" });
    const j = (await r.json()) as { ok?: boolean; url?: string | null };
    serverHasPhoto = !!(j?.ok && j.url);
  } catch {
    return;
  }

  if (serverHasPhoto) {
    setOverride(playerId, { photoDataUrl: "" });
    localStorage.setItem(flagKey, "1");
    return;
  }

  const blob = dataUrlToBlob(dataUrl);
  if (!blob) {
    localStorage.setItem(flagKey, "1");
    return;
  }
  const ext = blob.type === "image/png" ? "png" : blob.type === "image/webp" ? "webp" : "jpg";
  const form = new FormData();
  form.append("file", blob, `legacy.${ext}`);

  try {
    const r = await fetch("/api/profile/photo/upload", { method: "POST", body: form });
    if (!r.ok) {
      if (r.status === 401 || r.status === 403) return;
      localStorage.setItem(flagKey, "1");
      return;
    }
    setOverride(playerId, { photoDataUrl: "" });
    localStorage.setItem(flagKey, "1");
    notifyProfileAvatarUpdated(playerId);
  } catch {
    // network — try again next session
  }
}
