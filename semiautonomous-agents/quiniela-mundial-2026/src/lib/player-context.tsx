"use client";

import { createContext, useCallback, useContext, useEffect, useMemo, useRef, useState, ReactNode } from "react";
import { PLAYERS, Player } from "@/data/players";
import { loadOverrides, hydrateFromServer, PROFILE_UPDATED_EVENT, type ProfileOverride } from "@/lib/profile-overrides";
import { hydratePredictionsFromServer, flushPendingSync, isDirty } from "@/lib/predictions";
import { usePicksStream } from "@/lib/picks-stream";
import { migrateLocalPhotoIfNeeded } from "@/lib/profile-photo-migrate";
import { recordOpen as recordDailyOpen } from "@/lib/daily-streak";

type PlayerCtx = {
  players: Player[];
  currentPlayer: Player | null;
  setPlayer: (id: string | null) => void;
  getPlayer: (id: string) => Player | undefined;
  ready: boolean;
};

const Ctx = createContext<PlayerCtx>({
  players: PLAYERS,
  currentPlayer: null,
  setPlayer: () => {},
  getPlayer: () => undefined,
  ready: false,
});

function applyOverrides(base: Player[], overrides: Record<string, ProfileOverride>): Player[] {
  return base.map(p => {
    const o = overrides[p.id];
    if (!o) return p;
    const merged: Player = {
      ...p,
      name: o.name?.trim() ? o.name : p.name,
      emoji: o.emoji ?? p.emoji,
    };
    if (o.photoDataUrl) merged.photoDataUrl = o.photoDataUrl;
    return merged;
  });
}

export function PlayerProvider({ children }: { children: ReactNode }) {
  const [overrides, setOverrides] = useState<Record<string, ProfileOverride>>({});
  const [currentId, setCurrentId] = useState<string | null>(null);
  const [ready, setReady] = useState(false);
  // Ref so focus/online/reauthed handlers always see the live playerId without
  // needing to be recreated (they run in an effect with [] deps).
  const currentIdRef = useRef<string | null>(null);
  useEffect(() => { currentIdRef.current = currentId; }, [currentId]);

  useEffect(() => {
    setOverrides(loadOverrides());
    // Auth cookie is the source of truth for identity. Anonymous (uncached) start
    // falls back to localStorage so the picker still works before login.
    const localId = typeof window !== "undefined" ? localStorage.getItem("q26_player") : null;
    if (localId) setCurrentId(localId);
    let cancelled = false;
    fetch("/api/auth/me", { cache: "no-store" })
      .then(r => r.ok ? r.json() : null)
      .then((j: { authed?: boolean; playerId?: string } | null) => {
        if (cancelled) return;
        if (j && j.authed && j.playerId && PLAYERS.some(p => p.id === j.playerId)) {
          if (typeof window !== "undefined") localStorage.setItem("q26_player", j.playerId);
          setCurrentId(j.playerId);
        }
      })
      .catch(() => {})
      .finally(() => { if (!cancelled) setReady(true); });
    const onUpd = () => setOverrides(loadOverrides());
    window.addEventListener(PROFILE_UPDATED_EVENT, onUpd);
    // Hydrate from Firestore on mount, on tab-focus, and on online — so a
    // change made on phone shows up on desktop the moment the tab regains
    // focus, without forcing the user to hard-refresh.
    hydrateFromServer().catch(() => {});
    const syncPicks = () => {
      const id = currentIdRef.current;
      if (id) hydratePredictionsFromServer(id).catch(() => {});
    };
    const onFocus = () => {
      if (document.visibilityState !== "visible") return;
      hydrateFromServer().then(() => setOverrides(loadOverrides())).catch(() => {});
      // Re-push any picks stuck in localStorage from a 401/network blip.
      // Cookie may now be fresh (re-login, network recovered), so try again.
      syncPicks();
    };
    // After a successful re-login the ChatBot dispatches this event so picks
    // that were blocked by a 401 are immediately re-pushed without waiting for
    // the next tab-focus or navigation.
    const onReauthed = (e: Event) => {
      const id = (e as CustomEvent<string>).detail ?? currentIdRef.current;
      if (id) hydratePredictionsFromServer(id).catch(() => {});
    };
    document.addEventListener("visibilitychange", onFocus);
    window.addEventListener("focus", onFocus);
    window.addEventListener("online", onFocus);
    window.addEventListener("q26:reauthed", onReauthed);
    return () => {
      cancelled = true;
      window.removeEventListener(PROFILE_UPDATED_EVENT, onUpd);
      document.removeEventListener("visibilitychange", onFocus);
      window.removeEventListener("focus", onFocus);
      window.removeEventListener("online", onFocus);
      window.removeEventListener("q26:reauthed", onReauthed);
    };
  }, []);

  // Real-time picks sync: open SSE stream per logged-in player.
  // Firestore onSnapshot on the server pushes every write to this client,
  // so picks made on phone show up on desktop in <1s without polling.
  usePicksStream(currentId);

  const players = useMemo(() => applyOverrides(PLAYERS, overrides), [overrides]);

  const getPlayer = useCallback((id: string) => players.find(p => p.id === id), [players]);

  const currentPlayer = useMemo(() => (currentId ? players.find(p => p.id === currentId) ?? null : null), [currentId, players]);

  const setPlayer = useCallback((id: string | null) => {
    if (!id) {
      localStorage.removeItem("q26_player");
      setCurrentId(null);
      return;
    }
    if (PLAYERS.some(p => p.id === id)) {
      localStorage.setItem("q26_player", id);
      setCurrentId(id);
    }
  }, []);

  // Hydrate picks from Firestore on login so picks travel across devices
  // and survive UI changes / cache wipes. Also flush any dirty (failed) syncs.
  useEffect(() => {
    if (!currentId) return;
    // If a previous push failed (401 or network), mark is in localStorage.
    // hydratePredictionsFromServer will detect the local vs remote diff and re-push.
    if (isDirty(currentId)) {
      console.info(`[player-context] dirty flag set for ${currentId} — forcing hydrate+push`);
    }
    hydratePredictionsFromServer(currentId).catch(() => {});
    migrateLocalPhotoIfNeeded(currentId).catch(() => {});
    try { recordDailyOpen(currentId); } catch {}
  }, [currentId]);

  // Flush pending writes when the user closes the tab or backgrounds the app
  // on mobile. Without this, a 200ms-debounced write can be lost forever if
  // they swipe away the browser before it fires.
  useEffect(() => {
    if (typeof window === "undefined") return;
    const flush = () => flushPendingSync();
    window.addEventListener("pagehide", flush);
    window.addEventListener("beforeunload", flush);
    document.addEventListener("visibilitychange", () => {
      if (document.visibilityState === "hidden") flush();
    });
    return () => {
      window.removeEventListener("pagehide", flush);
      window.removeEventListener("beforeunload", flush);
    };
  }, []);

  // Presence heartbeat: ping the server on mount + every 60s + whenever the
  // tab becomes visible. Hidden tabs stop pinging (the 90s TTL on the server
  // will drop them from the "online" list shortly after). No-ops when not
  // signed in.
  useEffect(() => {
    if (typeof window === "undefined") return;
    if (!currentId) return;
    let cancelled = false;
    const ping = () => {
      if (cancelled) return;
      try {
        const path = window.location.pathname || "/";
        fetch("/api/presence/ping", {
          method: "POST",
          headers: { "content-type": "application/json" },
          body: JSON.stringify({ currentPath: path }),
          keepalive: true,
        }).catch(() => {});
      } catch { /* ignore */ }
    };
    ping();
    const id = setInterval(() => {
      if (document.visibilityState === "visible") ping();
    }, 60_000);
    const onVis = () => {
      if (document.visibilityState === "visible") ping();
    };
    document.addEventListener("visibilitychange", onVis);
    return () => {
      cancelled = true;
      clearInterval(id);
      document.removeEventListener("visibilitychange", onVis);
    };
  }, [currentId]);

  return <Ctx.Provider value={{ players, currentPlayer, setPlayer, getPlayer, ready }}>{children}</Ctx.Provider>;
}

export function usePlayer() {
  return useContext(Ctx);
}
