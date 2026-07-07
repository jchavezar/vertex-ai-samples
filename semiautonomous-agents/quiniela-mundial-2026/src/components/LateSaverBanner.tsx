"use client";

// Late-Saver: when a LIVE match is in its closing minutes (≥80'), and the
// logged-in player's 1X2 pick on that match is currently WINNING by ≥1 goal,
// surface a pulsing red banner urging them to "hold on".

import { useEffect, useMemo, useState } from "react";
import { Heart } from "lucide-react";
import { usePlayer } from "@/lib/player-context";
import { useLiveScoreboard, type LiveFixture } from "@/lib/live-scoreboard";
import { loadPredictions, actualPick, type PlayerPredictions } from "@/lib/predictions";
import { allGroupFixtures } from "@/data/groups";
import { TEAMS } from "@/data/teams";
import { useLocale } from "@/lib/i18n";

function parseMinute(raw: string | undefined): number | null {
  if (!raw) return null;
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
  const { byId } = useLiveScoreboard();
  const { t } = useLocale();
  const [picks, setPicks] = useState<PlayerPredictions | null>(null);

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

  if (state.mode !== "holding") return null;

  const fx = allGroupFixtures().find(f => f.id === state.fxId);
  const remaining = Math.max(1, 90 - state.minute + 1);
  const homeTeam = fx ? TEAMS.find(tm => tm.code === fx.home) : null;
  const awayTeam = fx ? TEAMS.find(tm => tm.code === fx.away) : null;
  const holdingTeam = TEAMS.find(tm => tm.code === state.team);

  return (
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
  );
}
