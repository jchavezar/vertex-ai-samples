"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import Image from "next/image";
import Link from "next/link";
import { motion, AnimatePresence } from "framer-motion";
import { Radio, Clock, ChevronDown, ChevronRight, Swords, Calendar } from "lucide-react";
import { KO_SCHEDULE, type KOMatch, type KORound } from "@/data/knockout-schedule";
import { TEAMS_BY_CODE, flagUrl } from "@/data/teams";
import { usePlayer } from "@/lib/player-context";
import { SCORING } from "@/data/tournament";
import { PlayerAvatar } from "@/components/PlayerAvatar";
import { PLAYERS, AI_PLAYER_ID } from "@/data/players";
import { loadPredictions, savePredictions, type BracketPick } from "@/lib/predictions";
import { isKOSlotLocked } from "@/lib/fixture-time";
import { CharalProfileTrigger } from "@/components/CharalProfileModal";
import { ProbabilityBar } from "@/components/ProbabilityBar";
import { useKOProbs } from "@/lib/probabilities-client";
import { getStrength } from "@/data/team-strength";

// ── Types ──────────────────────────────────────────────────────────────────

type MatchPhase = "pre" | "in" | "post";

type KOEventData = {
  slot: string;
  koMatch: KOMatch;
  phase: MatchPhase;
  homeCode: string;
  awayCode: string;
  homeGoals?: number;
  awayGoals?: number;
  minute?: string;
  espnId?: string;
};

type LiveStats = {
  statsMap: Record<string, Record<string, string>>;
  keyEvents: Array<{ type: string; clock: string; team?: string; athlete?: string; text?: string }>;
};

// ── Round label ────────────────────────────────────────────────────────────

function roundLabel(round: KORound): string {
  switch (round) {
    case "R32":   return "32avos";
    case "R16":   return "Octavos";
    case "QF":    return "Cuartos";
    case "SF":    return "Semis";
    case "THIRD": return "3er lugar";
    case "FINAL": return "Final";
  }
}

// ── ESPN abbr map ──────────────────────────────────────────────────────────

const ESPN_ABBR: Record<string, string> = {
  RSA: "RSA", CAN: "CAN", BRA: "BRA", JPN: "JPN", GER: "GER",
  PAR: "PAR", NED: "NED", MAR: "MAR", CIV: "CIV", NOR: "NOR",
  USA: "USA", MEX: "MEX", ENG: "ENG", SEN: "SEN", POR: "POR",
  ESP: "ESP", SUI: "SUI", CPV: "CPV", COL: "COL", EGY: "EGY",
  FRA: "FRA", ARG: "ARG", URU: "URU", ECU: "ECU", KOR: "KOR",
  CZE: "CZE", AUS: "AUS", NGA: "NGA", IRN: "IRN", TUN: "TUN",
};
function normCode(abbr: string): string { return ESPN_ABBR[abbr] ?? abbr; }

// ── Scoreboard hook ────────────────────────────────────────────────────────

function useKOScoreboard() {
  const [events, setEvents] = useState<KOEventData[]>([]);
  const [loading, setLoading] = useState(true);

  const doFetch = useCallback(async () => {
    try {
      const res = await fetch("/api/scoreboard?dates=20260628-20260719", { cache: "no-store" });
      const json = await res.json();
      if (!json?.ok) return;

      const espnEvents: Array<{
        id: string;
        date: string;
        status: { type: { state: string }; displayClock: string };
        competitions: Array<{ competitors: Array<{ homeAway: string; score: string; winner?: boolean; team: { abbreviation: string } }> }>;
      }> = json.events ?? [];

      const mapped: KOEventData[] = KO_SCHEDULE.map(slot => {
        const slotUtcMs = new Date(slot.dateISO).getTime();
        const match = espnEvents.find(e => Math.abs(new Date(e.date).getTime() - slotUtcMs) < 2 * 60 * 60 * 1000);

        if (!match) {
          return { slot: slot.slot, koMatch: slot, phase: "pre" as const, homeCode: "???", awayCode: "???" };
        }

        const state = match.status.type.state as "pre" | "in" | "post";
        const comp = match.competitions[0];
        const home = comp?.competitors.find(c => c.homeAway === "home");
        const away = comp?.competitors.find(c => c.homeAway === "away");

        return {
          slot: slot.slot,
          koMatch: slot,
          phase: state,
          homeCode: home ? normCode(home.team.abbreviation) : "???",
          awayCode: away ? normCode(away.team.abbreviation) : "???",
          homeGoals: state !== "pre" ? Number(home?.score ?? 0) : undefined,
          awayGoals: state !== "pre" ? Number(away?.score ?? 0) : undefined,
          minute: state === "in" ? match.status.displayClock : undefined,
          espnId: match.id,
        };
      });

      setEvents(mapped);
    } catch {}
    finally { setLoading(false); }
  }, []);

  useEffect(() => {
    doFetch();
    const id = setInterval(doFetch, 15_000);
    return () => clearInterval(id);
  }, [doFetch]);

  return { events, loading };
}

// ── Live stats hook ────────────────────────────────────────────────────────

function useLiveStats(espnId: string | undefined, phase: MatchPhase) {
  const [stats, setStats] = useState<LiveStats | null>(null);

  useEffect(() => {
    if (!espnId || phase === "pre") return;
    let cancelled = false;
    const doFetch = async () => {
      try {
        const res = await fetch(`/api/ko/live-stats?eventId=${espnId}`, { cache: "no-store" });
        const j = await res.json();
        if (!cancelled && j?.ok) setStats({ statsMap: j.statsMap, keyEvents: j.keyEvents });
      } catch {}
    };
    doFetch();
    if (phase === "in") {
      const id = setInterval(doFetch, 20_000);
      return () => { cancelled = true; clearInterval(id); };
    }
    return () => { cancelled = true; };
  }, [espnId, phase]);

  return stats;
}

// ── Countdown hook ─────────────────────────────────────────────────────────

function useCountdown(targetMs: number) {
  const [now, setNow] = useState(() => Date.now());
  useEffect(() => {
    const remaining = targetMs - Date.now();
    const interval = remaining < 3_600_000 ? 1_000 : 30_000;
    const id = setInterval(() => setNow(Date.now()), interval);
    return () => clearInterval(id);
  }, [targetMs]);
  const ms = Math.max(0, targetMs - now);
  return {
    h: Math.floor(ms / 3_600_000),
    m: Math.floor((ms / 60_000) % 60),
    s: Math.floor((ms / 1_000) % 60),
    ms,
  };
}

// ── All R32 picks hook ─────────────────────────────────────────────────────

// Parses "R16-3" → { round: "R16", idx: 2 }, "R32-7" → { round: "R32", idx: 6 }
function parseKOSlot(slot: string): { round: keyof import("@/lib/predictions").BracketPick; idx: number } | null {
  const m = slot.match(/^(R32|R16|QF|SF)-(\d+)$/);
  if (!m) return null;
  return { round: m[1] as keyof import("@/lib/predictions").BracketPick, idx: parseInt(m[2], 10) - 1 };
}

function useAllKOPicks(slot: string) {
  const [picks, setPicks] = useState<{ playerId: string; pick: string }[]>([]);
  useEffect(() => {
    const parsed = parseKOSlot(slot);
    if (!parsed) return;
    import("@/lib/predictions").then(m => {
      m.loadAllPredictionsFromServer().then(all => {
        setPicks(
          all
            .filter(p => p.playerId !== AI_PLAYER_ID)
            .map(p => {
              const arr = p.bracket?.[parsed.round] as string[] | undefined;
              return { playerId: p.playerId, pick: arr?.[parsed.idx] ?? "" };
            })
            .filter(x => x.pick !== ""),
        );
      }).catch(() => {});
    });
  }, [slot]);
  return picks;
}

function useAllR32Picks(slotIdx: number) {
  return useAllKOPicks(`R32-${slotIdx + 1}`);
}

// ── StatBar ────────────────────────────────────────────────────────────────

function StatBar({ label, homeVal, awayVal }: { label: string; homeVal: number; awayVal: number }) {
  const total = homeVal + awayVal;
  if (total === 0) return null;
  const homePct = Math.round((homeVal / total) * 100);
  return (
    <div className="space-y-1">
      <div className="flex justify-between text-[10px] text-white/40 uppercase tracking-wider font-semibold">
        <span className="tabular-nums">{homeVal}</span>
        <span>{label}</span>
        <span className="tabular-nums">{awayVal}</span>
      </div>
      <div className="flex h-1.5 rounded-full overflow-hidden gap-px">
        <div className="rounded-l-full transition-all duration-700" style={{ width: `${homePct}%`, background: "#5E5BFF" }} />
        <div className="rounded-r-full transition-all duration-700" style={{ width: `${100 - homePct}%`, background: "#FF3B82" }} />
      </div>
    </div>
  );
}

// ── TeamFlag ───────────────────────────────────────────────────────────────

function TeamFlag({ code, align, dark }: { code: string; align: "left" | "right"; dark?: boolean }) {
  const team = TEAMS_BY_CODE[code];
  const textColor = dark ? "text-white" : "var(--ink)";
  const mutedColor = dark ? "text-white/40" : "text-[var(--ink-muted)]";

  if (!team || code === "???") {
    return (
      <div className={`flex items-center gap-2 min-w-0 ${align === "right" ? "flex-row-reverse" : ""}`}>
        <div className="w-10 h-10 rounded-xl bg-white/10 shrink-0" />
        <span className={`font-display text-lg font-bold ${mutedColor}`}>TBD</span>
      </div>
    );
  }
  return (
    <div className={`flex items-center gap-2 min-w-0 ${align === "right" ? "flex-row-reverse text-right" : ""}`}>
      <div className="relative w-10 h-10 rounded-xl overflow-hidden ring-1 ring-white/20 shrink-0">
        <Image src={flagUrl(team.iso2, 64)} alt={team.name} fill sizes="40px" className="object-cover" unoptimized />
      </div>
      <div className="min-w-0">
        <div className={`font-display text-lg font-bold leading-none truncate`} style={{ color: dark ? "white" : "var(--ink)" }}>{team.code}</div>
        <div className={`text-[10px] truncate ${mutedColor}`}>{team.name}</div>
      </div>
    </div>
  );
}

// ── PickersRow ─────────────────────────────────────────────────────────────

function PickersRow({
  picks, teamCode, alignRight,
}: {
  picks: { playerId: string; pick: string }[];
  teamCode: string;
  alignRight?: boolean;
}) {
  return (
    <div className={`flex flex-col gap-1.5 ${alignRight ? "items-end" : "items-start"}`}>
      <span className="text-[9px] uppercase tracking-wider font-bold text-white/50">
        {teamCode} · {picks.length}
      </span>
      <div className="flex flex-wrap gap-1">
        {picks.length === 0
          ? <span className="text-[9px] text-white/25 italic">nadie</span>
          : picks.slice(0, 6).map(p => {
              const player = PLAYERS.find(pl => pl.id === p.playerId);
              if (!player) return null;
              return (
                <CharalProfileTrigger key={p.playerId} player={player}>
                  <PlayerAvatar player={player} size={22} rounded="rounded-full" textClass="text-[8px]" tint={0.2} />
                </CharalProfileTrigger>
              );
            })
        }
        {picks.length > 6 && (
          <div className="w-[22px] h-[22px] rounded-full grid place-items-center text-[8px] font-bold text-white bg-white/20">
            +{picks.length - 6}
          </div>
        )}
      </div>
    </div>
  );
}

// ── LiveMatchCard ──────────────────────────────────────────────────────────

function LiveMatchCard({ event }: { event: KOEventData }) {
  const stats = useLiveStats(event.espnId, event.phase);
  const allPicks = useAllKOPicks(event.slot);
  const { currentPlayer } = usePlayer();

  const homePoss = Number(stats?.statsMap[event.homeCode]?.possessionPct ?? 50);
  const homeShots = Number(stats?.statsMap[event.homeCode]?.shotsTotal ?? 0);
  const awayShots = Number(stats?.statsMap[event.awayCode]?.shotsTotal ?? 0);
  const homeSOT = Number(stats?.statsMap[event.homeCode]?.shotsOnTarget ?? 0);
  const awaySOT = Number(stats?.statsMap[event.awayCode]?.shotsOnTarget ?? 0);
  const homeCorners = Number(stats?.statsMap[event.homeCode]?.corners ?? 0);
  const awayCorners = Number(stats?.statsMap[event.awayCode]?.corners ?? 0);

  const homeGoals = event.homeGoals ?? 0;
  const awayGoals = event.awayGoals ?? 0;
  const lead: "H" | "D" | "A" = homeGoals > awayGoals ? "H" : homeGoals < awayGoals ? "A" : "D";

  const pickersHome = allPicks.filter(p => p.pick === event.homeCode);
  const pickersAway = allPicks.filter(p => p.pick === event.awayCode);
  const myPick = currentPlayer ? (allPicks.find(p => p.playerId === currentPlayer.id)?.pick ?? null) : null;
  const winner = lead === "H" ? event.homeCode : lead === "A" ? event.awayCode : null;
  const myPickCorrect = myPick && winner && myPick === winner;

  const goalEvents = stats?.keyEvents.filter(e => e.type === "goal") ?? [];

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      className="relative rounded-3xl overflow-hidden"
      style={{ background: "linear-gradient(135deg, #0A0A1E 0%, #1A0A2E 100%)" }}
    >
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute -top-20 left-1/2 -translate-x-1/2 w-80 h-80 rounded-full opacity-25 animate-pulse"
          style={{ background: "radial-gradient(closest-side, rgba(255,59,130,0.6), transparent)" }} />
      </div>

      <div className="relative p-5">
        <div className="flex items-center justify-between mb-4">
          {event.phase === "in" ? (
            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-extrabold text-white bg-[#FF3B82]">
              <Radio size={10} className="animate-pulse" /> EN VIVO · {event.minute ?? ""}
            </span>
          ) : (
            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-extrabold text-white/60 bg-white/10">
              Final
            </span>
          )}
          <span className="text-[10px] text-white/40 uppercase tracking-wider">{roundLabel(event.koMatch.round)}</span>
        </div>

        {/* Score */}
        <div className="grid grid-cols-[1fr_auto_1fr] items-center gap-3 mb-5">
          <TeamFlag code={event.homeCode} align="left" dark />
          <div className="text-center">
            <div className="font-display text-5xl font-bold tabular-nums text-white leading-none">
              <span style={{ color: lead === "H" ? "#14F195" : lead === "D" ? "white" : "rgba(255,255,255,0.35)" }}>{homeGoals}</span>
              <span className="text-white/25 mx-2">-</span>
              <span style={{ color: lead === "A" ? "#14F195" : lead === "D" ? "white" : "rgba(255,255,255,0.35)" }}>{awayGoals}</span>
            </div>
          </div>
          <TeamFlag code={event.awayCode} align="right" dark />
        </div>

        {/* Goal timeline */}
        {goalEvents.length > 0 && (
          <div className="mb-4 space-y-1">
            {goalEvents.slice(-4).map((e, i) => (
              <div key={i} className="flex items-center gap-2 text-xs text-white/60">
                <span className="text-[10px] tabular-nums text-white/30 w-8 shrink-0">{e.clock}&apos;</span>
                <span className="text-[#14F195]">⚽</span>
                <span className="truncate flex-1">{e.athlete ?? e.text}</span>
                <span className="text-white/30 text-[10px] shrink-0">{e.team}</span>
              </div>
            ))}
          </div>
        )}

        {/* Stats bars */}
        {(homeShots + awayShots > 0 || homePoss !== 50) && (
          <div className="space-y-2.5 mb-4 px-1">
            <StatBar label="Posesión %" homeVal={homePoss} awayVal={100 - homePoss} />
            {homeShots + awayShots > 0 && <StatBar label="Tiros" homeVal={homeShots} awayVal={awayShots} />}
            {homeSOT + awaySOT > 0 && <StatBar label="A portería" homeVal={homeSOT} awayVal={awaySOT} />}
            {homeCorners + awayCorners > 0 && <StatBar label="Corners" homeVal={homeCorners} awayVal={awayCorners} />}
          </div>
        )}

        {/* Charales picks split — left = home, right = away */}
        <div className="grid grid-cols-[1fr_auto_1fr] gap-2 pt-3 border-t border-white/10">
          <PickersRow picks={pickersHome} teamCode={event.homeCode} />
          <div className="text-white/20 text-xs font-bold self-center">|</div>
          <PickersRow picks={pickersAway} teamCode={event.awayCode} alignRight />
        </div>

        {/* My pick result */}
        {myPick && event.phase === "post" && winner && (
          <div className={`mt-3 text-center text-xs font-bold py-1.5 rounded-full ${
            myPickCorrect ? "bg-[#14F195]/15 text-[#14F195]" : "bg-[#FF3B82]/15 text-[#FF3B82]"
          }`}>
            {myPickCorrect
              ? `✓ Acertaste ${myPick} · +${SCORING.knockoutWinner.R32} pts`
              : `✗ Mamaste · ganó ${winner}`
            }
          </div>
        )}
      </div>
    </motion.div>
  );
}

// ── UpcomingMatchCard ──────────────────────────────────────────────────────

const TIER_STARS: Record<string, string> = { S: "⭐⭐⭐⭐⭐", A: "⭐⭐⭐⭐", B: "⭐⭐⭐", C: "⭐⭐", D: "⭐", E: "·", F: "·" };
const TIER_COLOR: Record<string, string> = {
  S: "rgb(212,175,55)", A: "rgb(20,200,120)", B: "rgb(94,91,255)",
  C: "rgb(251,191,36)", D: "rgb(156,163,175)", E: "rgb(107,114,128)", F: "rgb(107,114,128)",
};

function TeamStatRow({ code, align }: { code: string; align: "left" | "right" }) {
  const s = getStrength(code);
  if (!s) return <div className="text-[9px] text-[var(--ink-muted)] opacity-40">—</div>;
  const tierColor = TIER_COLOR[s.tier] ?? "var(--ink-muted)";
  const pct = Math.round((s.strength / 100) * 100);
  return (
    <div className={`flex flex-col gap-1 ${align === "right" ? "items-end" : "items-start"}`}>
      <div className="flex items-center gap-1.5">
        <span className="text-[9px] font-black px-1.5 py-0.5 rounded-full" style={{ background: `${tierColor}22`, color: tierColor }}>
          {s.tier}
        </span>
        <span className="text-[8px]" style={{ color: tierColor }}>{TIER_STARS[s.tier]}</span>
      </div>
      <div className="w-full h-1.5 rounded-full overflow-hidden" style={{ background: "rgba(255,255,255,0.08)", maxWidth: 80 }}>
        <div className="h-full rounded-full" style={{ width: `${pct}%`, background: tierColor, opacity: 0.7 }} />
      </div>
      <div className="text-[8px] leading-snug text-[var(--ink-muted)] opacity-60 max-w-[120px] line-clamp-2"
        style={{ textAlign: align === "right" ? "right" : "left" }}>
        {s.notes.split(",")[0]}
      </div>
    </div>
  );
}

function UpcomingMatchCard({ event }: { event: KOEventData }) {
  const allPicks = useAllKOPicks(event.slot);
  const { currentPlayer } = usePlayer();
  const kickoffMs = new Date(event.koMatch.dateISO).getTime();
  const { h, m, s, ms } = useCountdown(kickoffMs);

  const homeTeam = TEAMS_BY_CODE[event.homeCode];
  const awayTeam = TEAMS_BY_CODE[event.awayCode];
  const isToday = new Date(kickoffMs).toDateString() === new Date().toDateString();
  const urgent = ms > 0 && ms < 3_600_000;
  const locked = isKOSlotLocked(event.slot);

  // Parse slot: "R32-3" → { round: "R32", idx: 2 }, "R16-1" → { round: "R16", idx: 0 }
  const slotParsed = (() => {
    const m = event.slot.match(/^(R32|R16|QF|SF|THIRD|FINAL)-(\d+)$/);
    if (!m) return null;
    return { round: m[1] as keyof BracketPick, idx: parseInt(m[2], 10) - 1 };
  })();

  const currentPlayerId = currentPlayer?.id ?? null;

  const readPickFromStorage = useCallback((pid: string): string => {
    if (!slotParsed) return "";
    const b = loadPredictions(pid).bracket;
    if (!b) return "";
    const arr = b[slotParsed.round] as string[] | undefined;
    return arr?.[slotParsed.idx] ?? "";
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [slotParsed?.round, slotParsed?.idx]);

  const [myLocalPick, setMyLocalPick] = useState<string>(() =>
    typeof window !== "undefined" && currentPlayerId ? readPickFromStorage(currentPlayerId) : ""
  );

  // Reload from localStorage only when the logged-in player or slot changes.
  // Using currentPlayer?.id (not the object) prevents re-runs from profile
  // override refreshes that recreate the player object with the same id.
  useEffect(() => {
    if (!currentPlayerId) return;
    setMyLocalPick(readPickFromStorage(currentPlayerId));
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [currentPlayerId, event.slot]);

  // Server events (SSE / hydrate) write to localStorage and fire
  // q26:predictions-updated. We only accept that update when we have NO pick
  // yet — so fresh picks from a previous session load correctly, but a server
  // delivery never reverts a pick the user just made.
  useEffect(() => {
    if (!currentPlayerId) return;
    const refresh = () => {
      setMyLocalPick(prev => {
        if (prev) return prev;                         // already have a pick → keep it
        return readPickFromStorage(currentPlayerId);   // empty → restore from server
      });
    };
    window.addEventListener("q26:predictions-updated", refresh);
    return () => window.removeEventListener("q26:predictions-updated", refresh);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [currentPlayerId, event.slot]);

  function handlePick(code: string) {
    if (!currentPlayer || locked || !code || code === "???" || !slotParsed) return;
    const pred = loadPredictions(currentPlayer.id);
    const b = { ...(pred.bracket ?? {}) } as BracketPick;
    const sizes: Record<string, number> = { R32: 16, R16: 8, QF: 4, SF: 2 };
    const size = sizes[slotParsed.round] ?? 1;
    // Always produce a proper fixed-length array — guards against corrupt
    // localStorage entries (e.g. [] from a bad merge) creating sparse arrays.
    const existing = b[slotParsed.round] as string[] | undefined;
    const arr: string[] = Array(size).fill("");
    if (existing && existing.length > 0) {
      for (let i = 0; i < Math.min(existing.length, size); i++) arr[i] = existing[i] ?? "";
    }
    arr[slotParsed.idx] = code;
    (b as Record<string, unknown>)[slotParsed.round] = arr;
    pred.bracket = b;
    savePredictions(pred);
    setMyLocalPick(code);
  }

  const [showStats, setShowStats] = useState(false);

  // Merge server picks with current user's local pick so their avatar always shows,
  // even before Firestore sync completes.
  const allPicksWithMe = useMemo(() => {
    if (!currentPlayer || !myLocalPick) return allPicks;
    const alreadyIn = allPicks.some(p => p.playerId === currentPlayer.id);
    if (alreadyIn) return allPicks;
    return [...allPicks, { playerId: currentPlayer.id, pick: myLocalPick }];
  }, [allPicks, currentPlayer, myLocalPick]);

  function TeamButton({ code, align }: { code: string; align: "left" | "right" }) {
    const team = TEAMS_BY_CODE[code];
    const picked = myLocalPick === code && !!code;
    const canPick = !!slotParsed && !locked && code !== "???";
    const El = canPick ? "button" : "div";
    const pickers = allPicksWithMe.filter(p => p.pick === code);

    return (
      <El
        type={canPick ? "button" : undefined}
        onClick={canPick ? () => handlePick(code) : undefined}
        className={`flex flex-col gap-1.5 rounded-xl p-2.5 transition-all w-full ${canPick ? "cursor-pointer active:scale-95" : "cursor-default"} ${align === "right" ? "items-end" : "items-start"}`}
        style={picked
          ? { background: "rgba(94,91,255,0.12)", boxShadow: "inset 0 0 0 1.5px rgba(94,91,255,0.55)" }
          : { background: "rgba(255,255,255,0.04)" }
        }
      >
        <div className={`flex items-center gap-2 ${align === "right" ? "flex-row-reverse" : ""}`}>
          {team ? (
            <div className="relative w-8 h-8 rounded-lg overflow-hidden ring-1 ring-[var(--line)] shrink-0">
              <Image src={flagUrl(team.iso2, 48)} alt={team.name} fill sizes="32px" className="object-cover" unoptimized />
            </div>
          ) : <div className="w-8 h-8 rounded-lg bg-[var(--bg-tint)] shrink-0" />}
          <div className={`min-w-0 ${align === "right" ? "text-right" : ""}`}>
            <div className="font-display font-bold text-sm leading-none truncate">{code === "???" ? "TBD" : code}</div>
            <div className="text-[10px] text-[var(--ink-muted)] truncate">{team?.name ?? ""}</div>
          </div>
        </div>
        {picked && (
          <span className="text-[8px] font-black px-1.5 py-0.5 rounded-full"
            style={{ background: "rgba(94,91,255,0.15)", color: "rgb(94,91,255)" }}>
            📌 tu pick
          </span>
        )}
        {pickers.length > 0 && (
          <div className={`flex flex-wrap gap-1 ${align === "right" ? "justify-end" : ""}`}>
            {pickers.slice(0, 5).map(p => {
              const player = PLAYERS.find(pl => pl.id === p.playerId);
              if (!player) return null;
              return (
                <CharalProfileTrigger key={p.playerId} player={player}>
                  <PlayerAvatar player={player} size={20} rounded="rounded-full" textClass="text-[7px]" tint={0.2} />
                </CharalProfileTrigger>
              );
            })}
          </div>
        )}
      </El>
    );
  }

  return (
    <div className="glass-strong rounded-2xl p-4 relative overflow-hidden">
      <div className="absolute top-0 right-0 w-32 h-32 rounded-full blur-3xl opacity-10 pointer-events-none"
        style={{ background: "radial-gradient(closest-side, #5E5BFF, transparent)", transform: "translate(40%, -40%)" }} />

      <div className="flex items-center justify-between mb-3">
        <span className="chip text-[10px] py-0.5 flex items-center gap-1">
          {isToday ? <Clock size={9} /> : <Calendar size={9} />}
          {isToday ? "Hoy" : "Próximo"} · {roundLabel(event.koMatch.round)}
        </span>
        {ms > 0 ? (
          <span className="font-display text-sm font-bold tabular-nums" style={{ color: urgent ? "#FF3B82" : "var(--ink)" }}>
            {h > 0 ? `${h}h ${String(m).padStart(2, "0")}m` : `${m}m ${String(s).padStart(2, "0")}s`}
          </span>
        ) : (
          <span className="text-xs font-bold text-[#FF3B82]">Inminente</span>
        )}
      </div>

      {/* Interactive team buttons */}
      <div className="grid grid-cols-[1fr_auto_1fr] items-start gap-2">
        <TeamButton code={event.homeCode} align="left" />
        <div className="text-center text-[var(--ink-muted)] font-bold text-sm pt-3">vs</div>
        <TeamButton code={event.awayCode} align="right" />
      </div>

      {!!slotParsed && !myLocalPick && !locked && event.homeCode !== "???" && (
        <div className="mt-2 text-center text-[9px] font-semibold" style={{ color: "var(--ink-muted)", opacity: 0.5 }}>
          👆 Toca un equipo para elegir tu pick
        </div>
      )}

      {/* Probability thermometer */}
      {event.homeCode !== "???" && event.awayCode !== "???" && (
        <KOProbBar homeCode={event.homeCode} awayCode={event.awayCode} />
      )}

      {/* Stats toggle */}
      {event.homeCode !== "???" && event.awayCode !== "???" && (
        <div className="mt-2">
          <button
            type="button"
            onClick={() => setShowStats(v => !v)}
            className="w-full flex items-center justify-center gap-1.5 py-1 rounded-lg transition-colors text-[9px] font-bold uppercase tracking-widest"
            style={{ color: "var(--ink-muted)", opacity: 0.55 }}
          >
            {showStats ? "▲ Ocultar stats" : "▼ Ver estadísticas"}
          </button>
          <AnimatePresence>
            {showStats && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: "auto" }}
                exit={{ opacity: 0, height: 0 }}
                transition={{ duration: 0.18 }}
                className="overflow-hidden"
              >
                <div className="pt-2 border-t border-white/8 grid grid-cols-2 gap-3">
                  <TeamStatRow code={event.homeCode} align="left" />
                  <TeamStatRow code={event.awayCode} align="right" />
                </div>
                <div className="mt-2 text-[8px] text-center" style={{ color: "var(--ink-muted)", opacity: 0.35 }}>
                  Fuerza ELO · Mundial 2026
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      )}
    </div>
  );
}

function KOProbBar({ homeCode, awayCode }: { homeCode: string; awayCode: string }) {
  const probs = useKOProbs(homeCode, awayCode);
  if (!probs) return null;
  return (
    <div className="mt-3 pt-3 border-t border-white/8">
      <ProbabilityBar probs={probs} homeCode={homeCode} awayCode={awayCode} />
    </div>
  );
}

// ── PastMatchCard ──────────────────────────────────────────────────────────

function PastMatchCard({ event }: { event: KOEventData }) {
  const homeTeam = TEAMS_BY_CODE[event.homeCode];
  const awayTeam = TEAMS_BY_CODE[event.awayCode];
  const { currentPlayer } = usePlayer();
  const [myPick, setMyPick] = useState<string | null>(null);
  const [allPicks, setAllPicks] = useState<Record<string, string | null> | null>(null);
  const [slotWinner, setSlotWinner] = useState<string | null>(null);

  useEffect(() => {
    if (!currentPlayer) return;
    const parsed = parseKOSlot(event.slot);
    if (!parsed) return;
    import("@/lib/predictions").then(m => {
      const pred = m.loadPredictions(currentPlayer.id);
      const arr = pred.bracket?.[parsed.round] as string[] | undefined;
      setMyPick(arr?.[parsed.idx] || null);
    });
  }, [currentPlayer, event.slot]);

  useEffect(() => {
    if (!event.slot) return;
    fetch(`/api/ko/match-picks?slot=${event.slot}`)
      .then(r => r.json())
      .then(d => { if (d.ok) setAllPicks(d.picks as Record<string, string | null>); })
      .catch(() => {});
    // Use ko-results for winner so penalty games (0-0 scoreline) are handled correctly
    fetch("/api/bracket/ko-results", { cache: "no-store" })
      .then(r => r.json())
      .then((d: { ok: boolean; slotResults?: Record<string, string> }) => {
        if (d.ok && d.slotResults?.[event.slot]) setSlotWinner(d.slotResults[event.slot]);
      })
      .catch(() => {});
  }, [event.slot]);

  const homeGoals = event.homeGoals ?? 0;
  const awayGoals = event.awayGoals ?? 0;
  // Prefer ko-results winner (handles penalties); fall back to goals for in-progress display
  const winner = slotWinner ?? (homeGoals > awayGoals ? event.homeCode : awayGoals > homeGoals ? event.awayCode : null);
  const hit = myPick && winner && myPick === winner;
  const humanPlayers = PLAYERS.filter(p => !p.isBot);

  return (
    <div className={`rounded-xl overflow-hidden transition-colors ${hit ? "bg-[#14F195]/8" : "bg-[var(--bg-tint)]"}`}>
      {/* Score row */}
      <div className="flex items-center gap-3 px-3 py-2.5">
        {homeTeam && (
          <div className="relative w-6 h-6 rounded-md overflow-hidden shrink-0">
            <Image src={flagUrl(homeTeam.iso2, 32)} alt={homeTeam.name} fill sizes="24px" className="object-cover" unoptimized />
          </div>
        )}
        <span className="font-display font-bold text-sm tabular-nums whitespace-nowrap">
          <span style={{ color: homeGoals > awayGoals ? "var(--ink)" : "var(--ink-muted)" }}>{homeGoals}</span>
          <span className="text-[var(--ink-muted)] mx-1">-</span>
          <span style={{ color: awayGoals > homeGoals ? "var(--ink)" : "var(--ink-muted)" }}>{awayGoals}</span>
        </span>
        {awayTeam && (
          <div className="relative w-6 h-6 rounded-md overflow-hidden shrink-0">
            <Image src={flagUrl(awayTeam.iso2, 32)} alt={awayTeam.name} fill sizes="24px" className="object-cover" unoptimized />
          </div>
        )}
        <span className="flex-1 text-[10px] text-[var(--ink-muted)] truncate">
          {event.homeCode === "???" ? "?" : event.homeCode} vs {event.awayCode === "???" ? "?" : event.awayCode}
        </span>
        {myPick && (
          <span className={`text-[10px] font-bold shrink-0 ${hit ? "text-[#0B7D4F]" : "text-[#A1144C]"}`}>
            {hit ? `+${SCORING.knockoutWinner.R32}pts` : "✗"}
          </span>
        )}
      </div>

      {/* Charales picks row */}
      {allPicks && (
        <div className="flex flex-wrap items-center gap-2 px-3 pb-2.5 border-t border-[var(--line)]/20 pt-2">
          {humanPlayers.map(p => {
            const pick = allPicks[p.id] ?? null;
            const correct = pick && winner && pick === winner;
            const wrong = pick && winner && pick !== winner;
            return (
              <div key={p.id} className="flex flex-col items-center gap-0.5" style={{ minWidth: 24 }}>
                <div className="relative">
                  <PlayerAvatar player={p} size={22} rounded="rounded-full" tint={0.18} />
                  <span
                    className="absolute -bottom-0.5 -right-1 text-[9px] leading-none"
                    style={{ textShadow: "0 0 3px rgba(0,0,0,0.5)" }}
                  >
                    {correct ? "✅" : wrong ? "❌" : pick ? "➖" : ""}
                  </span>
                </div>
                <span
                  className="font-display font-black tabular-nums text-center leading-none"
                  style={{ fontSize: 7, color: correct ? "rgb(16,185,129)" : wrong ? "rgb(239,68,68)" : "var(--ink-muted)", opacity: pick ? 0.85 : 0.3 }}
                >
                  {pick ?? "—"}
                </span>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

// ── Main KOMatchFeed ───────────────────────────────────────────────────────

export function KOMatchFeed() {
  const { events, loading } = useKOScoreboard();
  const [showPast, setShowPast] = useState(false);

  const liveEvents  = useMemo(() => events.filter(e => e.phase === "in"),   [events]);
  const upcomingEvents = useMemo(() => events.filter(e => e.phase === "pre").slice(0, 4), [events]);
  const pastEvents  = useMemo(() => events.filter(e => e.phase === "post"), [events]);

  if (loading && events.length === 0) {
    return (
      <div className="glass rounded-2xl p-5 flex items-center gap-3">
        <div className="w-8 h-8 rounded-full bg-[var(--bg-tint)] animate-pulse shrink-0" />
        <div className="space-y-2 flex-1">
          <div className="h-4 w-40 bg-[var(--bg-tint)] rounded animate-pulse" />
          <div className="h-3 w-24 bg-[var(--bg-tint)] rounded animate-pulse" />
        </div>
      </div>
    );
  }

  const isEmpty = liveEvents.length === 0 && upcomingEvents.length === 0 && pastEvents.length === 0;

  return (
    <div className="space-y-3">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Swords size={16} className="text-[var(--accent-violet)]" />
          <span className="font-display font-bold text-lg">Eliminatorias</span>
          {liveEvents.length > 0 && (
            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold text-white bg-[#FF3B82]">
              <Radio size={8} className="animate-pulse" /> {liveEvents.length} EN VIVO
            </span>
          )}
        </div>
        <Link href="/bracket" className="text-xs font-semibold text-[var(--ink-muted)] hover:text-[var(--ink)] flex items-center gap-1">
          Bracket <ChevronRight size={12} />
        </Link>
      </div>

      {/* Live */}
      {liveEvents.map(event => (
        <LiveMatchCard key={event.slot} event={event} />
      ))}

      {/* Upcoming */}
      {upcomingEvents.length > 0 && (
        <div className="space-y-2">
          {liveEvents.length > 0 && (
            <div className="text-[10px] uppercase tracking-wider text-[var(--ink-muted)] font-semibold px-1">Próximos</div>
          )}
          {upcomingEvents.map(event => (
            <UpcomingMatchCard key={event.slot} event={event} />
          ))}
        </div>
      )}

      {/* Past — collapsed */}
      {pastEvents.length > 0 && (
        <div>
          <button
            type="button"
            onClick={() => setShowPast(v => !v)}
            className="w-full flex items-center justify-between px-3 py-2 rounded-xl bg-[var(--bg-tint)] text-sm font-semibold text-[var(--ink-muted)] hover:text-[var(--ink)] transition-colors"
          >
            <span>{pastEvents.length} {pastEvents.length === 1 ? "partido terminado" : "partidos terminados"}</span>
            <ChevronDown size={14} className={`transition-transform duration-200 ${showPast ? "rotate-180" : ""}`} />
          </button>
          <AnimatePresence>
            {showPast && (
              <motion.div
                key="past"
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: "auto", opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                transition={{ duration: 0.2, ease: "easeOut" }}
                className="overflow-hidden"
              >
                <div className="mt-2 space-y-1">
                  {pastEvents.map(event => (
                    <PastMatchCard key={event.slot} event={event} />
                  ))}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      )}

      {isEmpty && !loading && (
        <div className="text-center py-6 text-[var(--ink-muted)] text-sm">
          Los partidos de eliminatorias empiezan el 28 de junio.
        </div>
      )}
    </div>
  );
}
