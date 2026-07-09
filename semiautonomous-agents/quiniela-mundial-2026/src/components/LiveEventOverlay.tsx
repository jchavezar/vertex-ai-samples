"use client";

// Live Event Overlay — the global "what just happened" surface. Supersedes
// the goal-only GoalCelebrationOverlay. Watches three sources:
//
//   1. Scoreboard cache (useScoreboard) — the in-process score-delta detector,
//      preserved verbatim. This is the LOW-LATENCY goal path: a score change
//      fires a celebration within one poll tick (≤8s) without any extra fetch.
//   2. /api/live/events?sinceMs=600000 on mount — catch-up queue for the
//      events the user MISSED while they had the app closed.
//   3. /api/live/events?sinceMs=15000 every 8s thereafter — covers red cards,
//      penalties, substitutions, and VAR reviews (none of which show up in
//      the scoreboard payload).
//
// The two paths can race on the same goal (scoreboard delta vs BFF event);
// dedup is the same `seen` set, keyed by:
//   - scoreboard goals  → `${fxId}|h|${n}` / `${fxId}|a|${n}`  (existing v1 scheme)
//   - BFF events        → BFF's `id` (espn play id when present, otherwise
//                          `${fxId}|${cat}|${clockSec}|${teamId}`)
// Both schemes are stored together in `q26:events-seen-v2`.
//
// Queue: strictly serial. ONE overlay at a time, auto-hide per tier + 200ms
// gap. Queue capped at 12; once full, oldest non-goal events are dropped
// (goals always shown). VAR is short — if a goal/penalty lands while a VAR
// overlay is on, the overlay is yanked early so the higher-stakes event
// can fire immediately.

import { useEffect, useMemo, useRef, useState, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import Image from "next/image";
import { useScoreboard } from "@/lib/scoreboard-cache";
import { usePlayer } from "@/lib/player-context";
import { loadPredictions } from "@/lib/predictions";
import { allGroupFixtures } from "@/data/groups";
import { TEAMS, flagUrl } from "@/data/teams";
import { normalizeAbbr, type EspnEvent } from "@/lib/espn";
import { useLocale } from "@/lib/i18n";
import type { LiveEventItem, LiveEventType, LiveEventsResponse } from "@/app/api/live/events/route";

// ─── Constants ────────────────────────────────────────────────────────────
const SEEN_KEY = "q26:events-seen-v2";
const SEEN_CAP = 500;
const QUEUE_CAP = 12;
const SHOW_MS: Record<QueueItem["type"], number> = {
  goal: 4200,
  red: 3000,
  penalty: 3000,
  sub: 2500,
  var: 3200,
};
const GAP_MS = 200;
const POLL_MS = 8000;
const LIVE_THRESHOLD_MS = 30_000;        // "live now" if wallclock < 30s old

// ─── Types ────────────────────────────────────────────────────────────────
type QueueItem = {
  // Local-only signature (covers both scoreboard goals and BFF events).
  id: string;
  type: LiveEventType;
  fixtureId: string;
  homeCode: string;
  awayCode: string;
  homeName: string;
  awayName: string;
  homeColor: string;
  awayColor: string;
  // The "subject" team (scorer / red-carded / subbed-on team).
  teamCode: string;
  teamName: string;
  teamColor: string;
  // Score AT the moment of event (goals only).
  homeScore?: number;
  awayScore?: number;
  minute: string;            // "67'" — already formatted
  wallclock: number;         // ms since epoch (Date.now() for live deltas)
  text?: string;
  scorer?: string;
  // Pick context — null = no player signed in, true = user picked the team
  // that scored / went to PK, false = user picked the OTHER team.
  myPickMatched: boolean | null;
  // Convenience: the (oldest) signature this came from for `seen` dedup.
  seenSig: string;
};

// ─── Local-storage helpers ────────────────────────────────────────────────
function readSeen(): Set<string> {
  if (typeof window === "undefined") return new Set();
  try {
    const raw = localStorage.getItem(SEEN_KEY);
    if (!raw) return new Set();
    const arr = JSON.parse(raw) as string[];
    return new Set(Array.isArray(arr) ? arr.slice(-SEEN_CAP) : []);
  } catch { return new Set(); }
}
function writeSeen(set: Set<string>) {
  if (typeof window === "undefined") return;
  try {
    localStorage.setItem(SEEN_KEY, JSON.stringify(Array.from(set).slice(-SEEN_CAP)));
  } catch { /* full / disabled — best effort */ }
}

function colorFor(team?: { color?: string; accent?: string }): string {
  const raw = team?.color || team?.accent;
  if (!raw) return "#5E5BFF";
  return raw.startsWith("#") ? raw : `#${raw}`;
}

// ─── Scoreboard-delta goal detection (preserved from v1) ──────────────────
function snapshotScores(events: EspnEvent[] | undefined): Map<string, { h: number; a: number }> {
  const out = new Map<string, { h: number; a: number }>();
  if (!events) return out;
  for (const e of events) {
    const state = e.status?.type?.state;
    if (state !== "in") continue;
    const c = e.competitions?.[0];
    if (!c) continue;
    const h = c.competitors?.find(cp => cp.homeAway === "home");
    const a = c.competitors?.find(cp => cp.homeAway === "away");
    if (!h || !a) continue;
    const hg = Number(h.score);
    const ag = Number(a.score);
    if (!Number.isFinite(hg) || !Number.isFinite(ag)) continue;
    out.set(e.id, { h: hg, a: ag });
  }
  return out;
}

// ─── Component ────────────────────────────────────────────────────────────
export function LiveEventOverlay() {
  const { data } = useScoreboard();
  const { currentPlayer } = usePlayer();
  const { t, locale } = useLocale();

  const [current, setCurrent] = useState<QueueItem | null>(null);
  const queueRef = useRef<QueueItem[]>([]);
  const seenRef = useRef<Set<string>>(new Set());
  const lastScoresRef = useRef<Map<string, { h: number; a: number }> | null>(null);
  const hideTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const processingRef = useRef(false);
  const mountedRef = useRef(false);

  // Restore seen ids.
  useEffect(() => {
    seenRef.current = readSeen();
  }, []);

  // ─── Queue scheduler ──────────────────────────────────────────────────
  const showNext = useCallback(() => {
    if (current) return;
    const next = queueRef.current.shift();
    if (!next) {
      processingRef.current = false;
      return;
    }
    processingRef.current = true;
    setCurrent(next);
  }, [current]);

  // Auto-hide once `current` is set.
  useEffect(() => {
    if (!current) return;
    if (hideTimerRef.current) clearTimeout(hideTimerRef.current);
    const dur = SHOW_MS[current.type] ?? 3000;
    hideTimerRef.current = setTimeout(() => {
      setCurrent(null);
    }, dur);
    return () => {
      if (hideTimerRef.current) clearTimeout(hideTimerRef.current);
    };
  }, [current]);

  // After current hides, schedule the next one after a small gap.
  useEffect(() => {
    if (current) return;
    if (queueRef.current.length === 0) {
      processingRef.current = false;
      return;
    }
    const t = setTimeout(showNext, GAP_MS);
    return () => clearTimeout(t);
  }, [current, showNext]);

  // Enqueue helper. Dedups via seenRef + respects QUEUE_CAP (drops oldest
  // non-goal events when full).
  const enqueue = useCallback((items: QueueItem[]) => {
    if (items.length === 0) return;
    const fresh = items.filter(it => {
      if (seenRef.current.has(it.seenSig)) return false;
      seenRef.current.add(it.seenSig);
      return true;
    });
    if (fresh.length === 0) return;
    writeSeen(seenRef.current);

    queueRef.current.push(...fresh);

    // Trim. Always keep goals; drop oldest non-goals when over cap.
    while (queueRef.current.length > QUEUE_CAP) {
      const dropIdx = queueRef.current.findIndex(q => q.type !== "goal");
      if (dropIdx === -1) break; // queue is all goals → keep them all
      queueRef.current.splice(dropIdx, 1);
    }

    // If a high-priority event lands while a VAR overlay is showing, yank
    // the VAR early so the goal/penalty/red doesn't wait its full duration.
    if (current && current.type === "var" && fresh.some(f => f.type === "goal" || f.type === "penalty" || f.type === "red")) {
      if (hideTimerRef.current) clearTimeout(hideTimerRef.current);
      setCurrent(null);
    }

    if (!processingRef.current) showNext();
  }, [current, showNext]);

  // ─── PATH 1: scoreboard-delta goal detection (low-latency) ────────────
  useEffect(() => {
    const events = data?.events;
    if (!events || events.length === 0) return;
    const curMap = snapshotScores(events);
    const prev = lastScoresRef.current;
    lastScoresRef.current = curMap;

    // First snapshot: seed `seen` with the current goal signatures so we
    // don't fire for historical scores on app open.
    if (prev === null) {
      for (const [eventId, score] of curMap) {
        for (let i = 0; i < score.h; i++) seenRef.current.add(`${eventId}|h|${i + 1}`);
        for (let i = 0; i < score.a; i++) seenRef.current.add(`${eventId}|a|${i + 1}`);
      }
      writeSeen(seenRef.current);
      return;
    }

    const fixtures = allGroupFixtures();
    const fired: QueueItem[] = [];
    for (const e of events) {
      const next = curMap.get(e.id);
      if (!next) continue;
      const before = prev.get(e.id) ?? { h: 0, a: 0 };
      const c = e.competitions[0];
      const espnHome = c.competitors.find(cp => cp.homeAway === "home");
      const espnAway = c.competitors.find(cp => cp.homeAway === "away");
      if (!espnHome || !espnAway) continue;

      const espnHomeCode = normalizeAbbr(espnHome.team.abbreviation);
      const espnAwayCode = normalizeAbbr(espnAway.team.abbreviation);
      const cdmxDate = new Date(e.date).toLocaleDateString("en-CA", { timeZone: "America/Mexico_City" });
      const fx = fixtures.find(f =>
        ((f.home === espnHomeCode && f.away === espnAwayCode) || (f.away === espnHomeCode && f.home === espnAwayCode))
        && (f.date === cdmxDate || f.date === e.date.slice(0, 10)),
      );
      if (!fx) continue;

      const goalsHome = Math.max(0, next.h - before.h);
      const goalsAway = Math.max(0, next.a - before.a);

      const ourHomeIsEspnHome = fx.home === espnHomeCode;
      const myPicks = currentPlayer ? loadPredictions(currentPlayer.id) : null;
      const myPick = myPicks?.group[fx.id]?.pick;

      const espnHomeTeam = TEAMS.find(t => t.code === espnHomeCode);
      const espnAwayTeam = TEAMS.find(t => t.code === espnAwayCode);
      const homeColor = colorFor(espnHome.team);
      const awayColor = colorFor(espnAway.team);
      const homeName = espnHomeTeam?.name || espnHomeCode;
      const awayName = espnAwayTeam?.name || espnAwayCode;
      const minute = e.status?.displayClock ? `${e.status.displayClock}'` : "";

      for (let i = 1; i <= goalsHome; i++) {
        const sig = `${e.id}|h|${before.h + i}`;
        fired.push({
          id: sig,
          seenSig: sig,
          type: "goal",
          fixtureId: fx.id,
          homeCode: espnHomeCode, awayCode: espnAwayCode,
          homeName, awayName,
          homeColor, awayColor,
          teamCode: espnHomeCode, teamName: homeName, teamColor: homeColor,
          homeScore: next.h, awayScore: next.a,
          minute, wallclock: Date.now(),
          myPickMatched: myPick == null ? null : myPick === (ourHomeIsEspnHome ? "H" : "A"),
        });
      }
      for (let i = 1; i <= goalsAway; i++) {
        const sig = `${e.id}|a|${before.a + i}`;
        fired.push({
          id: sig,
          seenSig: sig,
          type: "goal",
          fixtureId: fx.id,
          homeCode: espnHomeCode, awayCode: espnAwayCode,
          homeName, awayName,
          homeColor, awayColor,
          teamCode: espnAwayCode, teamName: awayName, teamColor: awayColor,
          homeScore: next.h, awayScore: next.a,
          minute, wallclock: Date.now(),
          myPickMatched: myPick == null ? null : myPick === (ourHomeIsEspnHome ? "A" : "H"),
        });
      }
    }
    if (fired.length) enqueue(fired);
  }, [data, currentPlayer, enqueue]);

  // ─── PATH 2 + 3: BFF events (catch-up + recurring poll) ───────────────
  useEffect(() => {
    let cancelled = false;
    const myPicks = currentPlayer ? loadPredictions(currentPlayer.id) : null;
    const fixtures = allGroupFixtures();

    const toQueueItem = (ev: LiveEventItem): QueueItem | null => {
      const fx = fixtures.find(f => f.id === ev.fixtureId);
      if (!fx) return null;
      const ourHomeIsEspnHome = fx.home === ev.homeCode;
      const myPick = myPicks?.group[fx.id]?.pick;
      const homeColor = ev.homeCode === ev.team.code ? ev.team.color : "#5E5BFF";
      const awayColor = ev.awayCode === ev.team.code ? ev.team.color : "#5E5BFF";
      const teamColor = ev.team.color;
      const teamName = TEAMS.find(t => t.code === ev.team.code)?.name || ev.team.name || ev.team.code;
      // Pick context only meaningful for goals/penalties (decision moments).
      const pickRelevant = ev.type === "goal" || ev.type === "penalty";
      const matched = !pickRelevant || myPick == null
        ? null
        : myPick === ((ev.team.code === fx.home) ? (ourHomeIsEspnHome ? "H" : "A") : (ourHomeIsEspnHome ? "A" : "H"));
      return {
        id: ev.id,
        seenSig: ev.id,
        type: ev.type,
        fixtureId: fx.id,
        homeCode: ev.homeCode, awayCode: ev.awayCode,
        homeName: ev.homeName, awayName: ev.awayName,
        homeColor, awayColor,
        teamCode: ev.team.code, teamName, teamColor,
        homeScore: ev.homeScore, awayScore: ev.awayScore,
        minute: ev.minute,
        wallclock: ev.wallclock,
        text: ev.text,
        scorer: ev.scorer,
        myPickMatched: matched,
      };
    };

    async function fetchEvents(sinceMs: number, seedOnly = false) {
      try {
        const res = await fetch(`/api/live/events?sinceMs=${sinceMs}`, { cache: "no-store" });
        if (!res.ok) return;
        const body = (await res.json()) as LiveEventsResponse;
        if (cancelled) return;
        if (!body.ok || !body.events?.length) return;

        if (seedOnly) {
          // On the very first scoreboard tick we seed `seen` with historical
          // goal signatures. The catch-up call should NOT enqueue events
          // already in `seen`. enqueue() handles that, so just feed it.
        }

        const items = body.events
          .map(toQueueItem)
          .filter((q): q is QueueItem => q !== null);
        enqueue(items);
      } catch { /* network blip — next poll retries */ }
    }

    // Mount: ten-minute catch-up.
    if (!mountedRef.current) {
      mountedRef.current = true;
      fetchEvents(10 * 60_000);
    }

    // Recurring poll.
    const id = setInterval(() => {
      // Use a slightly-wider window (POLL+8s) to tolerate clock skew.
      fetchEvents(POLL_MS + 8_000);
    }, POLL_MS);
    return () => { cancelled = true; clearInterval(id); };
  }, [currentPlayer, enqueue]);

  // ─── Render ───────────────────────────────────────────────────────────
  if (!current) return null;

  const ageMs = Date.now() - current.wallclock;
  const isLive = ageMs < LIVE_THRESHOLD_MS;
  const minutesAgo = Math.max(1, Math.round(ageMs / 60_000));

  const timestampPill = current.minute
    ? (isLive
        ? `${current.minute} · ${t("event.live")}`
        : `${current.minute} · ${t("event.timeAgo").replace("{n}", String(minutesAgo))}`)
    : null;

  const pickBadge = current.myPickMatched === true
    ? t("event.myPickWin")
    : current.myPickMatched === false
      ? t("event.myPickLose")
      : null;

  const team = TEAMS.find(tm => tm.code === current.teamCode);

  if (current.type === "goal") {
    return (
      <BigGoal
        item={current}
        team={team}
        timestampPill={timestampPill}
        pickBadge={pickBadge}
      />
    );
  }
  if (current.type === "sub") {
    return (
      <SmallEvent
        item={current}
        team={team}
        timestampPill={timestampPill}
        t={t}
        locale={locale}
      />
    );
  }
  return (
    <MediumEvent
      item={current}
      team={team}
      timestampPill={timestampPill}
      pickBadge={pickBadge}
      label={
        current.type === "red"     ? t("event.red")     :
        current.type === "penalty" ? t("event.penalty") :
        /* var */                    t("event.var")
      }
    />
  );
}

// ─── BigGoal — preserved from GoalCelebrationOverlay v1 ───────────────────
function BigGoal({ item, team, timestampPill, pickBadge }: {
  item: QueueItem;
  team: { iso2: string } | undefined;
  timestampPill: string | null;
  pickBadge: string | null;
}) {
  const teamColor = item.teamColor;
  const ballPieces = useMemo(() => {
    const palette = [teamColor, teamColor, teamColor, "#FFE07A", "#14F195", "#FFFFFF"];
    return Array.from({ length: 50 }).map((_, i) => ({
      key: i,
      left: Math.random() * 100,
      delay: Math.random() * 0.4,
      duration: 2.2 + Math.random() * 1.6,
      size: 8 + Math.floor(Math.random() * 10),
      bg: palette[i % palette.length],
      rounded: i % 3 === 0,
      rot: Math.floor(Math.random() * 720) - 360,
    }));
  }, [teamColor]);

  return (
    <div
      aria-hidden
      className="pointer-events-none fixed inset-0 z-[80] overflow-hidden"
      style={{
        background: `radial-gradient(circle at 50% 40%, ${teamColor}55 0%, ${teamColor}22 30%, transparent 70%)`,
        animation: "goalPulse 4.2s ease-out forwards",
      }}
    >
      <div className="absolute" style={{ top: "30%", left: "-15%", animation: "goalBall 1.6s cubic-bezier(.2,.6,.4,1) forwards" }}>
        <span className="block" style={{ fontSize: "clamp(96px, 28vw, 220px)", lineHeight: 1, filter: `drop-shadow(0 8px 30px ${teamColor}aa)` }}>⚽</span>
      </div>

      <div className="absolute inset-0 grid place-items-center px-6 text-center">
        <div className="flex flex-col items-center gap-3" style={{ animation: "goalTextIn 0.45s cubic-bezier(.2,1.2,.4,1) forwards" }}>
          <h1
            className="font-display font-black uppercase leading-none"
            style={{
              fontSize: "clamp(72px, 18vw, 220px)",
              color: "white",
              WebkitTextStroke: `3px ${teamColor}`,
              textShadow: `0 8px 24px ${teamColor}cc, 0 0 60px ${teamColor}77`,
              letterSpacing: "-0.02em",
            }}
          >
            ¡G{"O".repeat(4)}L!
          </h1>
          <div className="flex flex-wrap items-center justify-center gap-3 px-4 py-2 rounded-full bg-black/60 backdrop-blur-sm">
            {team && (
              <span className="relative w-7 h-7 rounded-full overflow-hidden ring-2 ring-white">
                <Image src={flagUrl(team.iso2, 64)} alt="" fill className="object-cover" unoptimized />
              </span>
            )}
            <span className="text-white font-display font-bold text-lg tracking-wide">{item.teamName}</span>
            {item.homeScore != null && item.awayScore != null && (
              <span className="text-white/80 font-display font-bold text-base tabular-nums">
                {item.homeCode} {item.homeScore} - {item.awayScore} {item.awayCode}
              </span>
            )}
          </div>
          {item.scorer && (
            <div className="text-white/90 font-display font-semibold text-base">⚽ {item.scorer}</div>
          )}
          {timestampPill && (
            <span className="px-3 py-1 rounded-full bg-white/15 backdrop-blur-sm text-white text-xs font-bold uppercase tracking-wider">
              {timestampPill}
            </span>
          )}
          {pickBadge && (
            <span
              className={`mt-1 px-3 py-1 rounded-full text-white text-xs font-extrabold uppercase tracking-wider ${item.myPickMatched ? "bg-emerald-500" : "bg-rose-600"}`}
            >
              {pickBadge}
            </span>
          )}
        </div>
      </div>

      {ballPieces.map(p => (
        <span
          key={p.key}
          style={{
            position: "absolute",
            top: "-12px",
            left: `${p.left}%`,
            width: `${p.size}px`,
            height: `${p.size}px`,
            background: p.bg,
            borderRadius: p.rounded ? "50%" : "2px",
            transform: `translateY(0) rotate(${p.rot}deg)`,
            animation: `goalConfetti ${p.duration}s cubic-bezier(.45,.02,.7,1.05) ${p.delay}s forwards`,
            opacity: 0.95,
          }}
        />
      ))}

      <style>{`
        @keyframes goalBall {
          0%   { left: -15%; top: 30%; transform: rotate(0deg) scale(0.7); opacity: 0; }
          15%  { opacity: 1; }
          40%  { top: 18%; transform: rotate(540deg) scale(1.1); }
          70%  { top: 32%; transform: rotate(900deg) scale(1); }
          100% { left: 110%; top: 28%; transform: rotate(1440deg) scale(0.85); opacity: 0; }
        }
        @keyframes goalTextIn {
          0% { transform: scale(0.5) rotate(-4deg); opacity: 0; }
          60% { transform: scale(1.08) rotate(0deg); opacity: 1; }
          100% { transform: scale(1) rotate(0deg); opacity: 1; }
        }
        @keyframes goalPulse {
          0%   { opacity: 0; }
          15%  { opacity: 1; }
          70%  { opacity: 1; }
          100% { opacity: 0; }
        }
        @keyframes goalConfetti {
          to { transform: translateY(115vh) rotate(720deg); opacity: 0.85; }
        }
      `}</style>
    </div>
  );
}

// ─── MediumEvent — red / penalty / VAR ────────────────────────────────────
function MediumEvent({ item, team, timestampPill, pickBadge, label }: {
  item: QueueItem;
  team: { iso2: string } | undefined;
  timestampPill: string | null;
  pickBadge: string | null;
  label: string;
}) {
  const teamColor = item.teamColor;
  const isRed = item.type === "red";
  const isPen = item.type === "penalty";

  return (
    <div
      aria-hidden
      className="pointer-events-none fixed inset-0 z-[80] grid place-items-center px-4"
      style={{
        background: `radial-gradient(circle at 50% 50%, ${teamColor}44 0%, ${teamColor}11 35%, transparent 70%)`,
      }}
    >
      <AnimatePresence>
        <motion.div
          key={item.id}
          initial={{ scale: 0.7, opacity: 0, y: 30 }}
          animate={{ scale: 1, opacity: 1, y: 0 }}
          exit={{ scale: 0.9, opacity: 0, y: -10 }}
          transition={{ type: "spring", stiffness: 220, damping: 18 }}
          className="relative max-w-md w-full rounded-3xl px-6 py-7 text-white shadow-2xl"
          style={{
            background: "linear-gradient(135deg, rgba(15,18,30,0.95) 0%, rgba(20,24,42,0.95) 100%)",
            boxShadow: `0 0 60px ${teamColor}55, 0 25px 50px rgba(0,0,0,0.6)`,
            border: `2px solid ${teamColor}`,
          }}
        >
          <div className="flex flex-col items-center gap-3 text-center">
            {/* Icon */}
            <div className="relative">
              {isRed && (
                <motion.div
                  initial={{ rotateY: -180, scale: 0.5 }}
                  animate={{ rotateY: 0, scale: 1 }}
                  transition={{ duration: 0.45, ease: "easeOut" }}
                  className="w-20 h-28 rounded-md shadow-xl"
                  style={{ background: "linear-gradient(135deg, #FF1744 0%, #B71C1C 100%)" }}
                />
              )}
              {isPen && (
                <div className="relative w-24 h-24 grid place-items-center">
                  <motion.span
                    className="absolute inset-0 rounded-full"
                    style={{ border: `2px dashed ${teamColor}` }}
                    animate={{ scale: [1, 1.15, 1], opacity: [0.8, 0.3, 0.8] }}
                    transition={{ duration: 1.6, repeat: Infinity }}
                  />
                  <span className="text-5xl" style={{ filter: `drop-shadow(0 4px 12px ${teamColor}aa)` }}>⚽</span>
                  <span
                    className="absolute bottom-1 left-1/2 -translate-x-1/2 w-3 h-3 rounded-full bg-white"
                    style={{ boxShadow: `0 0 12px ${teamColor}` }}
                  />
                </div>
              )}
              {!isRed && !isPen /* var */ && (
                <motion.div
                  className="w-24 h-24 rounded-full grid place-items-center"
                  style={{ border: `3px solid ${teamColor}`, boxShadow: `0 0 30px ${teamColor}66` }}
                  animate={{ rotate: [0, 360] }}
                  transition={{ duration: 2.4, repeat: Infinity, ease: "linear" }}
                >
                  <span className="text-4xl">🤖</span>
                </motion.div>
              )}
            </div>

            {/* Label */}
            <h2
              className="font-display font-black uppercase leading-none"
              style={{
                fontSize: "clamp(28px, 6vw, 44px)",
                color: "white",
                WebkitTextStroke: `1.5px ${teamColor}`,
                textShadow: `0 4px 14px ${teamColor}aa`,
                letterSpacing: "-0.01em",
              }}
            >
              {label}
            </h2>

            {/* Team chip */}
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-white/10 backdrop-blur-sm">
              {team && (
                <span className="relative w-5 h-5 rounded-full overflow-hidden ring-1 ring-white/60">
                  <Image src={flagUrl(team.iso2, 48)} alt="" fill className="object-cover" unoptimized />
                </span>
              )}
              <span className="font-display font-bold text-sm">{item.teamName}</span>
              <span className="text-white/60 font-display font-bold text-xs tabular-nums">
                {item.homeCode}–{item.awayCode}
              </span>
            </div>

            {/* Body text */}
            {item.text && (
              <p className="text-white/85 text-sm leading-snug max-w-xs line-clamp-2">{item.text}</p>
            )}

            {timestampPill && (
              <span className="px-3 py-1 rounded-full bg-black/40 text-white/90 text-[11px] font-bold uppercase tracking-wider">
                {timestampPill}
              </span>
            )}
            {pickBadge && (
              <span
                className={`px-3 py-1 rounded-full text-white text-[11px] font-extrabold uppercase tracking-wider ${item.myPickMatched ? "bg-emerald-500" : "bg-rose-600"}`}
              >
                {pickBadge}
              </span>
            )}
          </div>
        </motion.div>
      </AnimatePresence>
    </div>
  );
}

// ─── SmallEvent — substitution (corner toast) ─────────────────────────────
function SmallEvent({ item, team, timestampPill, t, locale }: {
  item: QueueItem;
  team: { iso2: string } | undefined;
  timestampPill: string | null;
  t: (key: string, fallback?: string) => string;
  locale: string;
}) {
  void locale;
  const teamColor = item.teamColor;
  // ESPN sub commentary often reads "X comes on for Y" — best-effort split.
  // Fallback to the raw text if we can't parse a clean IN/OUT pair.
  const parsedIn = item.scorer;
  let parsedOut: string | null = null;
  if (item.text) {
    const m = item.text.match(/(?:comes on for|replaces|por)\s+([A-ZÁÉÍÓÚÑa-záéíóúñ.\-'\s]+?)(?:\.|,|$)/);
    if (m && m[1]) parsedOut = m[1].trim();
  }

  return (
    <AnimatePresence>
      <motion.div
        key={item.id}
        initial={{ x: 60, opacity: 0 }}
        animate={{ x: 0, opacity: 1 }}
        exit={{ x: 60, opacity: 0 }}
        transition={{ type: "spring", stiffness: 280, damping: 24 }}
        aria-hidden
        className="pointer-events-none fixed bottom-20 md:bottom-6 right-4 z-[75] max-w-[18rem] rounded-2xl px-4 py-3 text-white shadow-2xl"
        style={{
          background: "linear-gradient(135deg, rgba(15,18,30,0.96) 0%, rgba(20,24,42,0.96) 100%)",
          border: `1.5px solid ${teamColor}`,
          boxShadow: `0 0 28px ${teamColor}55, 0 12px 28px rgba(0,0,0,0.55)`,
        }}
      >
        <div className="flex items-start gap-3">
          <motion.div
            className="text-2xl"
            animate={{ rotate: [0, -8, 8, 0] }}
            transition={{ duration: 1.2, repeat: Infinity, ease: "easeInOut" }}
          >
            🔁
          </motion.div>
          <div className="min-w-0 flex-1">
            <div className="flex items-center gap-2 mb-1">
              {team && (
                <span className="relative w-4 h-4 rounded-full overflow-hidden ring-1 ring-white/60 flex-shrink-0">
                  <Image src={flagUrl(team.iso2, 40)} alt="" fill className="object-cover" unoptimized />
                </span>
              )}
              <span className="font-display font-bold text-xs uppercase tracking-wider text-white/90">{item.teamName}</span>
            </div>
            {parsedIn && (
              <div className="text-sm leading-tight">
                <span className="text-emerald-400 font-bold">↑ {t("event.subIn")}</span>{" "}
                <span className="font-semibold">{parsedIn}</span>
              </div>
            )}
            {parsedOut && (
              <div className="text-sm leading-tight">
                <span className="text-rose-400 font-bold">↓ {t("event.subOut")}</span>{" "}
                <span className="font-semibold">{parsedOut}</span>
              </div>
            )}
            {!parsedIn && !parsedOut && item.text && (
              <div className="text-xs leading-snug text-white/80 line-clamp-2">{item.text}</div>
            )}
            {timestampPill && (
              <div className="mt-1.5 inline-block px-2 py-0.5 rounded-full bg-black/40 text-[10px] font-bold uppercase tracking-wider text-white/80">
                {timestampPill}
              </div>
            )}
          </div>
        </div>
      </motion.div>
    </AnimatePresence>
  );
}
