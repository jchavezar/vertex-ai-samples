"use client";

// Reads the approved AI profile avatar URL for a player. Returns null until
// loaded or if none has been approved yet (PlayerAvatar then falls back to
// the static /players/{id}.jpg).
//
// Strategy: stale-while-revalidate. Cache in sessionStorage so paint is
// instant, but ALWAYS hit the server in the background so a change made on
// device A propagates to device B on next render — no manual refresh needed.
// In-memory dedupes within a single tab session (multiple PlayerAvatar mounts
// of the same player share one network request).

import { useEffect, useState } from "react";

type Entry = { url: string | null; loadedAt: number };
const mem: Record<string, Entry> = {};
// Dedupe in-flight requests across mounts of the same playerId in one tab.
const inflight: Record<string, Promise<string | null>> = {};
// How long to dedupe back-to-back fetches inside one tab. The cache itself
// has no TTL — cross-device sync requires always-fresh fetches.
const DEDUPE_MS = 8_000;

function storageKey(playerId: string): string {
  return `q26:profile-avatar:${playerId}`;
}

function readSession(playerId: string): Entry | null {
  try {
    if (typeof sessionStorage === "undefined") return null;
    const raw = sessionStorage.getItem(storageKey(playerId));
    if (!raw) return null;
    return JSON.parse(raw) as Entry;
  } catch {
    return null;
  }
}

function writeSession(playerId: string, entry: Entry) {
  try {
    if (typeof sessionStorage === "undefined") return;
    sessionStorage.setItem(storageKey(playerId), JSON.stringify(entry));
  } catch {
    // quota — ignore
  }
}

function invalidate(playerId: string) {
  delete mem[playerId];
  // Drop any in-flight/recently-resolved promise too — otherwise refresh()
  // immediately after notify hands back the SAME stale resolved value during
  // the 8s dedupe window, and the UI never updates without a manual reload.
  delete inflight[playerId];
  try {
    if (typeof sessionStorage !== "undefined") sessionStorage.removeItem(storageKey(playerId));
  } catch {}
}

/** Dispatch from anywhere to force every PlayerAvatar mount of this player to refetch. */
export function notifyProfileAvatarUpdated(playerId: string) {
  invalidate(playerId);
  if (typeof window !== "undefined") {
    window.dispatchEvent(new CustomEvent("q26:profile-avatar-updated", { detail: { playerId } }));
  }
}

function fetchActive(playerId: string): Promise<string | null> {
  return fetch(`/api/avatars/profile?playerId=${encodeURIComponent(playerId)}`, { cache: "no-store" })
    .then(r => r.json())
    .then((j: { ok: boolean; url?: string | null }) => (j?.ok && j.url ? j.url : null))
    .catch(() => null);
}

function fetchDeduped(playerId: string): Promise<string | null> {
  const existing = inflight[playerId];
  if (existing) return existing;
  const p = fetchActive(playerId).finally(() => {
    setTimeout(() => { delete inflight[playerId]; }, DEDUPE_MS);
  });
  inflight[playerId] = p;
  return p;
}

export function useProfileAvatar(playerId: string | undefined): string | null {
  const [url, setUrl] = useState<string | null>(() => {
    if (!playerId) return null;
    const m = mem[playerId];
    if (m) return m.url;
    const s = readSession(playerId);
    if (s) {
      mem[playerId] = s;
      return s.url;
    }
    return null;
  });

  useEffect(() => {
    if (!playerId) return;
    let cancelled = false;

    const refresh = async () => {
      const fresh = await fetchDeduped(playerId);
      if (cancelled) return;
      const entry: Entry = { url: fresh, loadedAt: Date.now() };
      mem[playerId] = entry;
      writeSession(playerId, entry);
      setUrl(fresh);
    };

    // Paint instantly with cached value (if any), then always revalidate.
    const cached = mem[playerId] ?? readSession(playerId);
    if (cached) {
      mem[playerId] = cached;
      setUrl(cached.url);
    }
    void refresh();

    const handler = (e: Event) => {
      const ce = e as CustomEvent<{ playerId: string }>;
      if (ce.detail?.playerId === playerId) {
        invalidate(playerId);
        void refresh();
      }
    };
    // Re-check when the tab regains focus — covers the "I changed it on my
    // phone, switched to my laptop" case the moment the user comes back.
    const onVisible = () => { if (document.visibilityState === "visible") void refresh(); };
    if (typeof window !== "undefined") {
      window.addEventListener("q26:profile-avatar-updated", handler);
      document.addEventListener("visibilitychange", onVisible);
      window.addEventListener("focus", onVisible);
    }
    return () => {
      cancelled = true;
      if (typeof window !== "undefined") {
        window.removeEventListener("q26:profile-avatar-updated", handler);
        document.removeEventListener("visibilitychange", onVisible);
        window.removeEventListener("focus", onVisible);
      }
    };
  }, [playerId]);

  return url;
}
