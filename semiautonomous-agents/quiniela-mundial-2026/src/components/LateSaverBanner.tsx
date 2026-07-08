"use client";

// Late-Saver: when a LIVE match is in its closing minutes (≥80'), and the
// logged-in player's 1X2 pick on that match is currently WINNING by ≥1 goal,
// surface a pulsing red banner urging them to "hold on". If the match ends
// with the pick still right → fire a one-shot CSS confetti animation per
// fixture (deduped via localStorage).
//
// Auto-dismisses when:
//   - match goes final (we still fire confetti once if pick won)
//   - opponent ties or overtakes
//   - minute drops back below 80 (rare, e.g. ESPN data correction)
//
// Reads live state from `useLiveScoreboard` (the cached BFF) and the player's
// picks straight from localStorage via loadPredictions().

import { useEffect, useMemo, useRef, useState } from "react";
import { Heart } from "lucide-react";
import { usePlayer } from "@/lib/player-context";
import { useLiveScoreboard, type LiveFixture } from "@/lib/live-scoreboard";
import { loadPredictions, actualPick, type PlayerPredictions } from "@/lib/predictions";
import { allGroupFixtures } from "@/data/groups";
import { TEAMS } from "@/data/teams";
import { useLocale } from "@/lib/i18n";

const CONFETTI_KEY = (playerId: string, fixtureId: string) => `q26:late-saver-confetti:${playerId}:${fixtureId}`;

function parseMinute(raw: string | undefined): number | null {
  if (!raw) return null;
  // ESPN strings: "84'", "45+2'", "HT", "FT"
  const m = /([0-9]+)(?:\s*\+\s*([0-9]+))?/.exec(raw);
  if (!m) return null;
  const base = Number.parseInt(m[1] ?? "0", 10);
  const extra = m[2] ? Number.parseInt(m[2], 10) : 0;
  if (!Number.isFinite(base)) return null;
  return base + extra;
}

type SaverState =
  | { mode: "hidden" }
  | { mode: "holding"; fxId: string; team: string; homeGoals: number; awayGoals: number; minute: number };

function evaluate(
  picks: PlayerPredictions,
  liveById: Record<string, LiveFixture>,
): SaverState {
  const fixtures = allGroupFixtures();
  for (const fx of fixtures) {
    const live = liveById[fx.id];
    if (!live || live.phase !== "live") continue;
    const minute = parseMinute(live.minute);
    if (minute === null || minute < 80) continue;
    const pred = picks.group[fx.id];
    if (!pred) continue;
    const hg = live.homeGoals ?? 0;
    const ag = live.awayGoals ?? 0;
    if (hg === ag) continue;
    const currentSign = actualPick({ home: fx.home, away: fx.away, homeGoals: hg, awayGoals: ag });
    if (currentSign !== pred.pick) continue;
    const winningTeamCode = pred.pick === "H" ? fx.home : pred.pick === "A" ? fx.away : fx.home;
    return { mode: "holding", fxId: fx.id, team: winningTeamCode, homeGoals: hg, awayGoals: ag, minute };
  }
  return { mode: "hidden" };
}

export function LateSaverBanner() {
  const { currentPlayer } = usePlayer();
  const { byId, finals } = useLiveScoreboard();
  const { t } = useLocale();
  const [picks, setPicks] = useState<PlayerPredictions | null>(null);
  const [confettiFx, setConfettiFx] = useState<string | null>(null);

  // Pull picks from localStorage. Refresh on the same custom event the home
  // already broadcasts so a save→hit propagates instantly.
  useEffect(() => {
    if (!currentPlayer) {
      setPicks(null);
      return;
    }
    const load = () => setPicks(loadPredictions(currentPlayer.id));
    load();
    const onUpd = () => load();
    window.addEventListener("q26:predictions-updated", onUpd);
    return () => window.removeEventListener("q26:predictions-updated", onUpd);
  }, [currentPlayer]);

  const state = useMemo<SaverState>(() => {
    if (!picks || !currentPlayer) return { mode: "hidden" };
    return evaluate(picks, byId);
  }, [picks, currentPlayer, byId]);

  // Confetti trigger: when a match the player held into FT closes with the
  // pick still right, fire once per fixture/player.
  //
  // Bug history (2026-06-18): the previous version returned the cleanup
  // function INSIDE the for loop, so when `finals` re-emitted on poll the
  // cleanup cleared the auto-hide timer without re-arming it, leaving the
  // confetti state set; and because the render re-rolled Math.random() on
  // every parent re-render, fresh confetti pieces spawned from the top every
  // ~30s. Symptom: "cada determinado tiempo hay confeti".
  //
  // Fix: hold the hide timer in a ref so re-runs of the effect don't wipe it;
  // memoize the confetti pieces by fxId so re-renders don't re-roll positions.
  const hideTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  useEffect(() => {
    if (!currentPlayer || !picks) return;
    for (const [fxId, finalScore] of Object.entries(finals)) {
      const pred = picks.group[fxId];
      if (!pred) continue;
      const fx = allGroupFixtures().find(f => f.id === fxId);
      if (!fx) continue;
      const sign = actualPick({ home: fx.home, away: fx.away, homeGoals: finalScore.homeGoals, awayGoals: finalScore.awayGoals });
      if (sign !== pred.pick) continue;
      const key = CONFETTI_KEY(currentPlayer.id, fxId);
      try {
        if (localStorage.getItem(key)) continue;
        localStorage.setItem(key, String(Date.now()));
      } catch {
        continue;
      }
      setConfettiFx(fxId);
      if (hideTimerRef.current) clearTimeout(hideTimerRef.current);
      hideTimerRef.current = setTimeout(() => {
        setConfettiFx(null);
        hideTimerRef.current = null;
      }, 3500);
      break;
    }
  }, [finals, picks, currentPlayer]);
  // Unmount-only cleanup so re-runs of the effect don't wipe the timer.
  useEffect(() => () => {
    if (hideTimerRef.current) clearTimeout(hideTimerRef.current);
  }, []);

  // Memoize confetti particles keyed by fxId so a parent re-render does NOT
  // re-roll their positions (which made it look like fresh confetti was firing
  // on every scoreboard poll).
  const confettiPieces = useMemo(() => {
    if (!confettiFx) return null;
    const colors = ["#FF3B82", "#14F195", "#5E5BFF", "#FFE07A", "#FF9F1C"];
    return Array.from({ length: 60 }).map((_, i) => ({
      key: i,
      left: Math.random() * 100,
      delay: Math.random() * 0.6,
      duration: 2.4 + Math.random() * 1.4,
      size: 6 + Math.floor(Math.random() * 6),
      bg: colors[i % colors.length],
      rounded: i % 3 === 0,
    }));
  }, [confettiFx]);

  if (state.mode !== "holding" && !confettiFx) return null;

  // Lookup team display + group label for the "holding" copy.
  const fx = state.mode === "holding" ? allGroupFixtures().find(f => f.id === state.fxId) : null;
  const remaining = state.mode === "holding" ? Math.max(1, 90 - state.minute + 1) : 0;
  const homeTeam = fx ? TEAMS.find(tm => tm.code === fx.home) : null;
  const awayTeam = fx ? TEAMS.find(tm => tm.code === fx.away) : null;
  const holdingTeam = state.mode === "holding" ? TEAMS.find(tm => tm.code === state.team) : null;

  return (
    <>
      {state.mode === "holding" && (
        <div
          className="relative overflow-hidden rounded-3xl px-4 py-3 md:px-5 md:py-4 animate-pulse"
          style={{
            background: "linear-gradient(120deg, rgba(255,59,130,0.18), rgba(255,59,130,0.05))",
            border: "1px solid rgba(255,59,130,0.55)",
            boxShadow: "0 0 0 1px rgba(255,59,130,0.25), 0 8px 30px rgba(255,59,130,0.15)",
          }}
          role="status"
          aria-live="polite"
        >
          <div className="flex items-center gap-3">
            <div className="grid place-items-center w-10 h-10 rounded-full shrink-0" style={{ background: "rgba(255,59,130,0.22)" }}>
              <Heart size={18} className="text-[#FF3B82]" />
            </div>
            <div className="min-w-0 flex-1">
              <div className="text-[10px] uppercase tracking-[0.18em] font-bold text-[#FF3B82]">
                {t("live.lateSaver")}
              </div>
              <div className="font-display text-base md:text-lg font-bold leading-tight truncate">
                {`Aguanta ${holdingTeam?.code ?? state.team} ${state.homeGoals}-${state.awayGoals} · ${remaining} min`}
              </div>
              {homeTeam && awayTeam && (
                <div className="text-[11px] text-[var(--ink-soft)] truncate">
                  {homeTeam.name} vs {awayTeam.name} · {state.minute}&apos;
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {confettiFx && confettiPieces && (
        <div
          aria-hidden
          className="pointer-events-none fixed inset-0 z-[60] overflow-hidden"
        >
          {confettiPieces.map(p => (
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
                transform: "translateY(0) rotate(0deg)",
                animation: `lateSaverConfetti ${p.duration}s linear ${p.delay}s forwards`,
                opacity: 0.95,
              }}
            />
          ))}
          <style>{`
            @keyframes lateSaverConfetti {
              0%   { transform: translateY(0) rotate(0deg);    opacity: 1; }
              80%  { opacity: 1; }
              100% { transform: translateY(110vh) rotate(720deg); opacity: 0; }
            }
          `}</style>
        </div>
      )}
    </>
  );
}
