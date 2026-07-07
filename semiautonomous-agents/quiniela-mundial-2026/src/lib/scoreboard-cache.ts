"use client";

// Shared scoreboard cache. Single in-memory copy + sessionStorage hydration
// so navigating between Home / Quiniela / Partidos / Leaderboard is instant —
// the page renders cached data on mount and revalidates in background.

import { useEffect, useState } from "react";
import type { EspnEvent } from "@/lib/espn";

export type ScoreboardData = {
  ok: true;
  events: EspnEvent[];
  leagues?: unknown[];
  partialErrors?: string[];
};

const SS_KEY = "q26:scoreboard:v1";
const FRESH_MS = 25_000;
const STALE_MS = 5 * 60_000;

type State = { data: ScoreboardData | null; fetchedAt: number; loading: boolean };

let state: State = { data: null, fetchedAt: 0, loading: false };
let inflight: Promise<void> | null = null;
const subs = new Set<() => void>();

function notify() { for (const fn of subs) fn(); }

function hydrate() {
  if (state.data || typeof window === "undefined") return;
  try {
    const raw = sessionStorage.getItem(SS_KEY);
    if (!raw) return;
    const parsed = JSON.parse(raw) as { data: ScoreboardData; fetchedAt: number };
    if (parsed?.data?.events && Date.now() - parsed.fetchedAt < STALE_MS) {
      state = { data: parsed.data, fetchedAt: parsed.fetchedAt, loading: false };
    }
  } catch {}
}

function persist() {
  if (typeof window === "undefined" || !state.data) return;
  try {
    sessionStorage.setItem(SS_KEY, JSON.stringify({ data: state.data, fetchedAt: state.fetchedAt }));
  } catch {}
}

// Seed the in-memory cache from data the home snapshot endpoint already
// fetched. This lets `useScoreboard()` skip its first network round-trip on
// home-page cold loads — we already have fresh events, just install them.
// Only seeds when the supplied payload is meaningfully newer than what we
// already have, so a slow snapshot response doesn't overwrite a fresher tick.
export function seedScoreboard(data: ScoreboardData, fetchedAt: number): void {
  if (!data?.events) return;
  if (state.data && state.fetchedAt >= fetchedAt) return;
  state = { data, fetchedAt, loading: false };
  persist();
  notify();
}

export async function refreshScoreboard(force = false): Promise<void> {
  if (inflight) return inflight;
  if (!force && state.data && Date.now() - state.fetchedAt < FRESH_MS) return;
  state = { ...state, loading: true };
  notify();
  inflight = (async () => {
    try {
      const res = await fetch("/api/scoreboard");
      const json = (await res.json()) as ScoreboardData | { ok: false; error: string };
      if ("ok" in json && json.ok) {
        state = { data: json, fetchedAt: Date.now(), loading: false };
        persist();
      } else {
        state = { ...state, loading: false };
      }
    } catch {
      state = { ...state, loading: false };
    } finally {
      inflight = null;
      notify();
    }
  })();
  return inflight;
}

export function getScoreboard(): State {
  hydrate();
  return state;
}

export function useScoreboard(): State & { refresh: (force?: boolean) => Promise<void> } {
  hydrate();
  const [snap, setSnap] = useState<State>(state);
  useEffect(() => {
    const fn = () => setSnap(state);
    subs.add(fn);
    // Kick off background revalidation if data is stale or missing.
    refreshScoreboard();
    // Dynamic polling: 8s when any match is live (so 4-0 SUI doesn't show as
    // 0-0 like the owner caught on 2026-06-18), 30s otherwise. The detection
    // re-runs on each tick so cadence adapts as matches start/end.
    let id: ReturnType<typeof setInterval> | null = null;
    const reschedule = () => {
      if (id) clearInterval(id);
      const anyLive = (state.data?.events ?? []).some(e => e?.status?.type?.state === "in");
      const interval = anyLive ? 8_000 : 30_000;
      id = setInterval(async () => {
        // force=true: the interval IS the throttle — bypass FRESH_MS so the 8s
        // live cadence isn't silently collapsed to ~32s by the freshness gate.
        // The CDN's own max-age=3 prevents hammering origin on back-to-back ticks.
        await refreshScoreboard(true);
        // Re-check cadence in case state transitioned (pre → in or in → post).
        const nowLive = (state.data?.events ?? []).some(e => e?.status?.type?.state === "in");
        if (nowLive !== anyLive) reschedule();
      }, interval);
    };
    reschedule();
    // Also refresh hard on tab-visible, so the user gets fresh data the moment
    // they come back from another tab/app.
    const onVisible = () => { if (document.visibilityState === "visible") refreshScoreboard(true); };
    document.addEventListener("visibilitychange", onVisible);
    return () => {
      subs.delete(fn);
      if (id) clearInterval(id);
      document.removeEventListener("visibilitychange", onVisible);
    };
  }, []);
  return { ...snap, refresh: refreshScoreboard };
}
