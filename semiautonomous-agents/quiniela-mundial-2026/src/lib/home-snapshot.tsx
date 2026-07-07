"use client";

// Home-page snapshot context. Fetches /api/home/snapshot ONCE on mount and
// re-polls adaptively (8s when any match is live, 60s when idle). The home
// page wraps its content in <HomeSnapshotProvider> so above-the-fold
// components read from a single shared payload instead of each firing its
// own request on cold load.
//
// Components that consume this still own a fallback path (their own fetch)
// so they keep working if the provider is not mounted — e.g. when the
// component appears on a different page than the home.

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
  type ReactNode,
} from "react";
import type { HomeSnapshot } from "@/app/api/home/snapshot/route";
import { seedScoreboard } from "@/lib/scoreboard-cache";

type SnapshotState = {
  data: HomeSnapshot | null;
  fetchedAt: number;
  loading: boolean;
};

type SnapshotCtx = SnapshotState & { refresh: () => Promise<void> };

const Ctx = createContext<SnapshotCtx | null>(null);

const POLL_LIVE_MS = 8_000;
const POLL_IDLE_MS = 60_000;
const FRESH_MS = 7_000;     // dedupe rapid back-to-back refreshes
const SS_KEY = "q26:home-snapshot:v1";
const SS_MAX_MS = 5 * 60_000;

function readSession(): { data: HomeSnapshot; fetchedAt: number } | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = sessionStorage.getItem(SS_KEY);
    if (!raw) return null;
    const parsed = JSON.parse(raw) as { data: HomeSnapshot; fetchedAt: number };
    if (parsed?.data && Date.now() - parsed.fetchedAt < SS_MAX_MS) return parsed;
  } catch {}
  return null;
}

function persistSession(data: HomeSnapshot, fetchedAt: number) {
  if (typeof window === "undefined") return;
  try { sessionStorage.setItem(SS_KEY, JSON.stringify({ data, fetchedAt })); } catch {}
}

export function HomeSnapshotProvider({ children }: { children: ReactNode }) {
  const initial = readSession();
  const [state, setState] = useState<SnapshotState>(() => ({
    data: initial?.data ?? null,
    fetchedAt: initial?.fetchedAt ?? 0,
    loading: false,
  }));
  const inflight = useRef<Promise<void> | null>(null);
  const mounted = useRef(true);

  // Seed the scoreboard cache from the cached snapshot ASAP so the first
  // paint of the live scoreboard doesn't wait for a network round-trip.
  useEffect(() => {
    if (initial?.data?.scoreboard?.ok) {
      seedScoreboard({ ok: true, events: initial.data.scoreboard.events, leagues: initial.data.scoreboard.leagues }, initial.fetchedAt);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const refresh = useCallback(async () => {
    if (inflight.current) return inflight.current;
    if (Date.now() - state.fetchedAt < FRESH_MS && state.data) return;
    setState(s => ({ ...s, loading: true }));
    inflight.current = (async () => {
      try {
        const res = await fetch("/api/home/snapshot", { cache: "no-store" });
        if (!res.ok) throw new Error(`snapshot ${res.status}`);
        const json = (await res.json()) as HomeSnapshot;
        if (!mounted.current) return;
        const fetchedAt = Date.now();
        setState({ data: json, fetchedAt, loading: false });
        persistSession(json, fetchedAt);
        if (json.scoreboard?.ok) {
          seedScoreboard(
            { ok: true, events: json.scoreboard.events, leagues: json.scoreboard.leagues },
            fetchedAt,
          );
        }
      } catch {
        if (mounted.current) setState(s => ({ ...s, loading: false }));
      } finally {
        inflight.current = null;
      }
    })();
    return inflight.current;
  }, [state.data, state.fetchedAt]);

  useEffect(() => {
    mounted.current = true;
    // First load: refresh immediately. Session-cached data is shown in the
    // meantime so the user gets pixels before the network responds.
    refresh();
    return () => { mounted.current = false; };
    // refresh is stable enough — we want a single mount-time call
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Adaptive polling. Re-evaluates cadence on each tick so the interval
  // collapses to 8s the instant a match goes live.
  useEffect(() => {
    let timer: ReturnType<typeof setInterval> | null = null;
    const schedule = () => {
      if (timer) clearInterval(timer);
      const live = !!state.data?.scoreboard?.events?.some(
        e => e?.status?.type?.state === "in",
      );
      const interval = live ? POLL_LIVE_MS : POLL_IDLE_MS;
      timer = setInterval(() => { refresh(); }, interval);
    };
    schedule();
    return () => { if (timer) clearInterval(timer); };
  }, [state.data, refresh]);

  // Hard refresh when the tab regains focus, so a snapshot stale by several
  // minutes (phone in pocket, screen off) gets replaced immediately.
  useEffect(() => {
    const onVisible = () => {
      if (document.visibilityState === "visible") refresh();
    };
    document.addEventListener("visibilitychange", onVisible);
    return () => document.removeEventListener("visibilitychange", onVisible);
  }, [refresh]);

  const value = useMemo<SnapshotCtx>(() => ({ ...state, refresh }), [state, refresh]);
  return <Ctx.Provider value={value}>{children}</Ctx.Provider>;
}

export function useHomeSnapshot(): SnapshotCtx | null {
  return useContext(Ctx);
}
