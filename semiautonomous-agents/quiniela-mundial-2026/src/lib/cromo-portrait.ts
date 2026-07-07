"use client";

// Stale-while-revalidate cache for the daily AI portrait.
//
// HARD INVARIANT: this hook NEVER returns null once any portrait URL has ever
// been seen for the player on this device. If the day rolls over or a new
// theme is generated, the previously cached portrait stays visible until the
// fresh URL arrives. The CromoCard MUST NOT fall back to the raw photo —
// doing so caused the kitchen-background flicker that motivated this design.
//
// Storage: localStorage, keyed only by playerId. Persists across tabs and
// browser restarts. The portrait we get back from the API is a versioned
// HTTPS URL (`gcs/...?v={createdAt}`) — small (sub-150 bytes), no quota risk.

import { useEffect, useState } from "react";

// Bump this any time the cache shape or upstream URL format changes —
// it forces every browser to drop the stale entry on next mount.
const CACHE_VERSION = "v4";

const mem: Record<string, string> = {};
const inflight: Record<string, Promise<string | null>> = {};

function storageKey(playerId: string): string {
  return `q26:cromo-portrait:${CACHE_VERSION}:${playerId}`;
}

function readLocal(playerId: string): string | null {
  try {
    if (typeof localStorage === "undefined") return null;
    return localStorage.getItem(storageKey(playerId));
  } catch {
    return null;
  }
}

function writeLocal(playerId: string, url: string) {
  try {
    if (typeof localStorage === "undefined") return;
    localStorage.setItem(storageKey(playerId), url);
  } catch {
    // quota / private mode — fine, mem cache still wins
  }
}

function readAny(playerId: string): string | null {
  if (mem[playerId]) return mem[playerId];
  const stored = readLocal(playerId);
  if (stored) {
    mem[playerId] = stored;
    return stored;
  }
  return null;
}

function fetchPortrait(playerId: string): Promise<string | null> {
  const existing = inflight[playerId];
  if (existing) return existing;
  const p = fetch(`/api/cromos/portrait?playerId=${encodeURIComponent(playerId)}`, { cache: "no-store" })
    .then(r => r.json())
    .then((j: { ok: boolean; dataUrl?: string }) => (j?.ok && j.dataUrl ? j.dataUrl : null))
    .catch(() => null)
    .finally(() => { delete inflight[playerId]; });
  inflight[playerId] = p;
  return p;
}

export function useCromoPortrait(playerId: string | undefined): string | null {
  const [url, setUrl] = useState<string | null>(() => (playerId ? readAny(playerId) : null));

  useEffect(() => {
    if (!playerId) return;
    // Re-sync state for a possible playerId change after mount.
    const cached = readAny(playerId);
    if (cached && cached !== url) setUrl(cached);

    let cancelled = false;
    const sync = () => {
      fetchPortrait(playerId).then(next => {
        if (cancelled || !next) return;
        if (mem[playerId] === next) return;
        mem[playerId] = next;
        writeLocal(playerId, next);
        setUrl(next);
      });
    };
    sync();

    // Refetch whenever the tab regains focus or comes back online. This is the
    // mechanism that propagates a server-side regen to every friend's browser
    // without them having to clear cache or pull-to-refresh: switching tabs,
    // unlocking the phone, or reconnecting wifi all trigger a silent re-check.
    const onVisible = () => {
      if (typeof document !== "undefined" && document.visibilityState === "visible") sync();
    };
    document.addEventListener("visibilitychange", onVisible);
    window.addEventListener("focus", sync);
    window.addEventListener("online", sync);
    return () => {
      cancelled = true;
      document.removeEventListener("visibilitychange", onVisible);
      window.removeEventListener("focus", sync);
      window.removeEventListener("online", sync);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [playerId]);

  return url;
}
