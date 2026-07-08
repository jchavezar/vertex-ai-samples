"use client";

import Image from "next/image";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Lock, MapPin, Zap, Flame, Trophy, Sparkles } from "lucide-react";
import { useGroupRealResults } from "@/lib/real-results";
import { computeR32Pairings, R32_TEMPLATE } from "@/lib/standings";
import {
  blank,
  loadPredictions,
  savePredictions,
  loadAllPredictionsFromServer,
  type BracketPick,
} from "@/lib/predictions";
import { matchProbability, TEAM_STRENGTH } from "@/data/team-strength";
import { getTeam, flagUrl } from "@/data/teams";
import { KO_SCHEDULE } from "@/data/knockout-schedule";
import { VENUES } from "@/data/venues";
import { isKOSlotLocked } from "@/lib/fixture-time";
import { usePlayer } from "@/lib/player-context";
import { PLAYERS } from "@/data/players";
import { PlayerAvatar } from "@/components/PlayerAvatar";
import { useNow } from "@/lib/use-now";
import { ProbabilityBar } from "@/components/ProbabilityBar";
import { useKOProbs } from "@/lib/probabilities-client";

// ─── helpers ──────────────────────────────────────────────────────────────

const VENUE_MAP = new Map(VENUES.map(v => [v.city, v]));

type LiveStatus = "played" | "live" | "upcoming";

function liveStatus(dateISO: string, now: number | null): LiveStatus {
  if (!now) return "upcoming";
  const start = new Date(dateISO).getTime();
  if (now < start) return "upcoming";
  if (now <= start + 150 * 60_000) return "live";
  return "played";
}

function countdown(dateISO: string, now: number | null): string | null {
  if (!now) return null;
  const diff = new Date(dateISO).getTime() - now;
  if (diff <= 0) return null;
  const d = Math.floor(diff / 86_400_000);
  const h = Math.floor((diff % 86_400_000) / 3_600_000);
  const m = Math.floor((diff % 3_600_000) / 60_000);
  if (d > 0) return `${d}d ${h}h`;
  if (h > 0) return `${h}h ${m}m`;
  return `${m}m`;
}

function cdmxTime(iso: string) {
  return new Intl.DateTimeFormat("es-MX", { hour: "numeric", minute: "2-digit", timeZone: "America/Mexico_City" }).format(new Date(iso));
}
function cdmxDate(iso: string) {
  return new Intl.DateTimeFormat("es-MX", { weekday: "short", day: "numeric", month: "short", timeZone: "America/Mexico_City" }).format(new Date(iso));
}
function etTime(iso: string) {
  return new Intl.DateTimeFormat("en-US", { hour: "numeric", minute: "2-digit", timeZone: "America/New_York" }).format(new Date(iso));
}

function posLabel(token: string): string {
  if (!token) return "";
  if (token.startsWith("3rd")) return "3° grupos";
  if (token[0] === "1") return `1° Gr.${token.slice(1)}`;
  if (token[0] === "2") return `2° Gr.${token.slice(1)}`;
  return token;
}

// team had a flawless group (9 pts = 3W) → 🔥 badge
function groupBadge(token: string): "perfect" | "surprise" | null {
  if (!token) return null;
  if (token[0] === "1") return "perfect";   // group winner — show flame if dominant
  if (token.startsWith("3rd")) return "surprise";
  return null;
}

// ─── Ripple ───────────────────────────────────────────────────────────────

function Ripple({ x, y, onDone }: { x: number; y: number; onDone: () => void }) {
  return (
    <motion.span
      className="pointer-events-none absolute rounded-full"
      style={{ left: x - 40, top: y - 40, width: 80, height: 80, background: "rgba(20,241,149,0.45)", zIndex: 10 }}
      initial={{ scale: 0, opacity: 1 }}
      animate={{ scale: 4, opacity: 0 }}
      transition={{ duration: 0.55, ease: "easeOut" }}
      onAnimationComplete={onDone}
    />
  );
}

// ─── Consensus avatars ────────────────────────────────────────────────────

function ConsensusRow({
  slotIdx,
  teamA,
  teamB,
  allPicksMap,
}: {
  slotIdx: number;
  teamA: string;
  teamB: string;
  allPicksMap: Record<string, BracketPick>;
}) {
  const pickersA: typeof PLAYERS = [];
  const pickersB: typeof PLAYERS = [];

  for (const p of PLAYERS) {
    const pick = allPicksMap[p.id]?.R32?.[slotIdx];
    if (!pick) continue;
    if (pick === teamA) pickersA.push(p);
    else if (pick === teamB) pickersB.push(p);
  }

  const total = pickersA.length + pickersB.length;
  if (total === 0) {
    return (
      <div className="text-[9px] text-center py-1" style={{ color: "var(--ink-muted)", opacity: 0.5 }}>
        sé el primero en picar
      </div>
    );
  }

  return (
    <div className="flex items-center justify-between px-1 py-1">
      <div className="flex flex-wrap gap-0.5">
        {pickersA.map(p => (
          <PlayerAvatar key={p.id} player={p} size={22} rounded="rounded-full" className="ring-1 ring-green-400/50" />
        ))}
        {pickersA.length === 0 && <span className="text-[9px]" style={{ color: "var(--ink-muted)", opacity: 0.4 }}>–</span>}
      </div>
      <div className="text-[8px] tabular-nums font-bold px-2" style={{ color: "var(--ink-muted)" }}>
        {pickersA.length}:{pickersB.length}
      </div>
      <div className="flex flex-wrap gap-0.5 justify-end">
        {pickersB.map(p => (
          <PlayerAvatar key={p.id} player={p} size={22} rounded="rounded-full" className="ring-1 ring-purple-400/50" />
        ))}
        {pickersB.length === 0 && <span className="text-[9px]" style={{ color: "var(--ink-muted)", opacity: 0.4 }}>–</span>}
      </div>
    </div>
  );
}

// ─── Compact played row ───────────────────────────────────────────────────

function PlayedPill({
  slotIdx,
  teamA,
  teamB,
  myPick,
  scoreStr,
  allPicks,
}: {
  slotIdx: number;
  teamA: string;
  teamB: string;
  myPick: string;
  scoreStr?: string;
  allPicks?: Record<string, string | null>;
}) {
  const tA = teamA ? getTeam(teamA) : null;
  const tB = teamB ? getTeam(teamB) : null;
  const [sA, sB] = scoreStr?.split("-").map(Number) ?? [null, null];
  const winner = sA !== null && sB !== null ? (sA > sB ? teamA : sB > sA ? teamB : null) : null;
  const hit = myPick && winner && myPick === winner;
  const miss = myPick && winner && myPick !== winner;

  // Human players only (no bot)
  const humanPlayers = PLAYERS.filter(p => !p.isBot);

  return (
    <div
      className="rounded-xl overflow-hidden"
      style={{ background: "var(--bg-tint)", opacity: 0.92 }}
    >
      {/* Score row */}
      <div
        className="grid items-center gap-2 px-3 py-2.5"
        style={{ gridTemplateColumns: "1fr auto 1fr" }}
      >
        {/* Team A */}
        <div className="flex items-center gap-1.5 min-w-0">
          {tA ? (
            <div className="relative w-5 h-5 rounded-sm overflow-hidden shrink-0">
              <Image src={flagUrl(tA.iso2, 32)} alt={tA.name} fill sizes="20px" className="object-cover" unoptimized />
            </div>
          ) : null}
          <span
            className="font-display font-black text-[12px] tabular-nums truncate"
            style={{ opacity: winner ? (winner === teamA ? 1 : 0.3) : 0.7, color: "var(--ink)" }}
          >
            {tA?.code ?? (teamA || "?")}
          </span>
          {hit && myPick === teamA && <span className="text-[10px] ml-0.5">✅</span>}
          {miss && myPick === teamA && <span className="text-[10px] ml-0.5">❌</span>}
        </div>

        {/* Score */}
        <div className="text-center shrink-0 px-1">
          {sA !== null && sB !== null ? (
            <span className="font-display font-black text-[14px] tabular-nums" style={{ color: "var(--ink)" }}>
              {sA} – {sB}
            </span>
          ) : (
            <span className="font-display font-bold text-[9px] uppercase tracking-widest" style={{ color: "var(--ink-muted)", opacity: 0.5 }}>
              FIN
            </span>
          )}
        </div>

        {/* Team B */}
        <div className="flex items-center gap-1.5 min-w-0 justify-end">
          {hit && myPick === teamB && <span className="text-[10px] mr-0.5">✅</span>}
          {miss && myPick === teamB && <span className="text-[10px] mr-0.5">❌</span>}
          <span
            className="font-display font-black text-[12px] tabular-nums truncate text-right"
            style={{ opacity: winner ? (winner === teamB ? 1 : 0.3) : 0.7, color: "var(--ink)" }}
          >
            {tB?.code ?? (teamB || "?")}
          </span>
          {tB ? (
            <div className="relative w-5 h-5 rounded-sm overflow-hidden shrink-0">
              <Image src={flagUrl(tB.iso2, 32)} alt={tB.name} fill sizes="20px" className="object-cover" unoptimized />
            </div>
          ) : null}
        </div>
      </div>

      {/* Charales picks row */}
      {allPicks && (
        <div
          className="flex flex-wrap items-center gap-2 px-3 pb-2.5 pt-0 border-t border-[var(--line)]/20"
          style={{ paddingTop: 6 }}
        >
          {humanPlayers.map(p => {
            const pick = allPicks[p.id] ?? null;
            const correct = pick && winner && pick === winner;
            const wrong = pick && winner && pick !== winner;
            const noPick = !pick;
            return (
              <div key={p.id} className="flex flex-col items-center gap-0.5" style={{ minWidth: 24 }}>
                <div className="relative">
                  <PlayerAvatar player={p} size={22} rounded="rounded-full" tint={0.18} />
                  <span
                    className="absolute -bottom-0.5 -right-1 text-[9px] leading-none"
                    style={{ textShadow: "0 0 3px rgba(0,0,0,0.5)" }}
                  >
                    {correct ? "✅" : wrong ? "❌" : noPick ? "➖" : ""}
                  </span>
                </div>
                {pick && (
                  <span
                    className="font-display font-black tabular-nums text-center leading-none"
                    style={{ fontSize: 7, color: correct ? "rgb(16,185,129)" : wrong ? "rgb(239,68,68)" : "var(--ink-muted)", opacity: noPick ? 0.4 : 0.85 }}
                  >
                    {pick}
                  </span>
                )}
                {!pick && (
                  <span className="font-display font-black tabular-nums text-center leading-none" style={{ fontSize: 7, color: "var(--ink-muted)", opacity: 0.3 }}>
                    —
                  </span>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

// ─── KO probability bar (ELO-based, no draw) ─────────────────────────────

function KOMatchProbBar({ homeCode, awayCode }: { homeCode: string; awayCode: string }) {
  const probs = useKOProbs(homeCode, awayCode);
  if (!probs) return null;
  return <ProbabilityBar probs={probs} homeCode={homeCode} awayCode={awayCode} />;
}

// ─── Single match card ────────────────────────────────────────────────────

function MatchCard({
  slotIdx,
  teamA,
  teamB,
  tokenA,
  tokenB,
  dateISO,
  venueCity,
  venueStadium,
  myPick,
  onPick,
  allPicksMap,
  now,
  cardRef,
  isToday,
}: {
  slotIdx: number;
  teamA: string;
  teamB: string;
  tokenA: string;
  tokenB: string;
  dateISO: string;
  venueCity: string;
  venueStadium: string;
  myPick: string;
  onPick: (code: string, x: number, y: number) => void;
  allPicksMap: Record<string, BracketPick>;
  now: number | null;
  cardRef: (el: HTMLElement | null) => void;
  isToday?: boolean;
}) {
  const slot = `R32-${slotIdx + 1}`;
  const locked = isKOSlotLocked(slot, now ?? Date.now());
  const status = liveStatus(dateISO, now);
  const venue = VENUE_BY_MAP.get(venueCity);
  const tA = teamA ? getTeam(teamA) : null;
  const tB = teamB ? getTeam(teamB) : null;
  const [ripple, setRipple] = useState<{ x: number; y: number } | null>(null);

  const probs = (teamA && teamB) ? (() => {
    const p = matchProbability(teamA, teamB);
    const tot = p.H + p.A;
    const h = Math.round(p.H / tot * 100);
    return { h, a: 100 - h };
  })() : null;

  const isLive = status === "live";
  const isPlayed = status === "played";
  const cd = countdown(dateISO, now);

  const borderStyle = isLive
    ? { border: "1.5px solid rgba(239,68,68,0.7)", boxShadow: "0 0 0 1px rgba(239,68,68,0.2), 0 8px 28px -6px rgba(239,68,68,0.28)" }
    : isToday
    ? { border: "1.5px solid rgba(245,158,11,0.55)", boxShadow: "0 0 0 1px rgba(245,158,11,0.12), 0 8px 32px -6px rgba(245,158,11,0.2)" }
    : { border: "1px solid var(--line)", boxShadow: "0 2px 12px -4px rgba(0,0,0,0.1)" };

  function handleTeamClick(code: string, e: React.MouseEvent) {
    if (locked || !code) return;
    const rect = (e.currentTarget as HTMLElement).getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    setRipple({ x, y });
    onPick(code, x, y);
  }

  const TeamRow = ({ code, token, side }: { code: string; token: string; side: "A" | "B" }) => {
    const team = code ? getTeam(code) : null;
    const isPicked = myPick === code && !!code;
    const badge = groupBadge(token);
    const label = posLabel(token);
    const str = code ? TEAM_STRENGTH[code] : null;
    const canPick = !locked && !!code;

    const El = canPick ? "button" : "div";
    return (
      <El
        type={canPick ? "button" : undefined}
        onClick={canPick ? (e: React.MouseEvent) => handleTeamClick(code, e) : undefined}
        className={`relative flex items-center gap-3 w-full rounded-xl px-3 py-2.5 transition-all select-none ${canPick ? "cursor-pointer" : "cursor-default"} overflow-hidden`}
        style={isPicked
          ? { background: "rgba(94,91,255,0.10)", boxShadow: "inset 0 0 0 1.5px rgba(94,91,255,0.55)" }
          : canPick ? { background: "var(--bg-tint)" } : { background: "var(--bg-tint)", opacity: isPlayed ? 0.7 : 1 }
        }
      >
        {/* flag */}
        {team ? (
          <div className="relative w-9 h-9 rounded-lg overflow-hidden ring-1 ring-black/10 shrink-0 shadow-sm">
            <Image src={flagUrl(team.iso2, 56)} alt={team.name} fill sizes="36px" className="object-cover" unoptimized />
          </div>
        ) : (
          <div className="w-9 h-9 rounded-lg bg-[var(--bg)] shrink-0 grid place-items-center text-[var(--ink-muted)] font-bold text-lg">?</div>
        )}

        {/* name + label */}
        <div className="flex-1 min-w-0">
          <div className="font-display font-bold text-[14px] leading-tight truncate">
            {team?.name ?? (token ? label : "Pendiente")}
          </div>
          {label && code && (
            <div className="text-[10px] mt-0.5 flex items-center gap-1" style={{ color: "var(--ink-muted)" }}>
              {badge === "perfect" && str && <span className="text-[9px]">🔥</span>}
              {badge === "surprise" && <span className="text-[9px]">⚡</span>}
              {label}
            </div>
          )}
        </div>

        {/* picked indicator */}
        {isPicked && (
          <span className="shrink-0 text-[9px] font-black px-1.5 py-0.5 rounded-full"
            style={{ background: "rgba(94,91,255,0.15)", color: "rgb(94,91,255)" }}>
            📌 elegido
          </span>
        )}

        {/* ripple */}
        <AnimatePresence>
          {ripple && isPicked && (
            <Ripple key={Date.now()} x={ripple.x} y={ripple.y} onDone={() => setRipple(null)} />
          )}
        </AnimatePresence>
      </El>
    );
  };

  return (
    <motion.article
      ref={cardRef as React.Ref<HTMLElement>}
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="rounded-2xl overflow-hidden"
      style={{ background: "var(--bg-tint)", ...borderStyle, opacity: isPlayed ? 0.82 : 1 }}
    >
      {/* combined header: status + venue + times in one compact strip */}
      <div
        className="px-3 pt-2 pb-2 flex items-center gap-2 border-b border-[var(--line)]/25"
        style={{
          background: isLive
            ? "rgba(239,68,68,0.08)"
            : isToday
            ? "linear-gradient(135deg, rgba(245,158,11,0.10) 0%, rgba(251,191,36,0.06) 100%)"
            : "rgba(94,91,255,0.04)",
        }}
      >
        {/* left: status badge + venue */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-1.5 mb-0.5">
            {isLive && <span className="live-dot" />}
            <span
              className="font-display font-black text-[9px] uppercase tracking-[0.2em]"
              style={{
                color: isLive ? "rgb(239,68,68)" : isToday ? "rgb(245,158,11)" : "rgb(94,91,255)",
              }}
            >
              {isLive ? "EN VIVO" : isToday ? `HOY · ${cd ?? ""}` : cd ?? "PRÓXIMO"}
            </span>
            {locked && !isPlayed && <Lock size={8} className="opacity-40" style={{ color: "var(--ink-muted)" }} />}
          </div>
          <div className="flex items-center gap-1" style={{ color: "var(--ink-muted)" }}>
            <MapPin size={7} className="shrink-0 opacity-50" />
            <span className="text-[8px] truncate opacity-60">{venueStadium} · {venueCity}</span>
          </div>
        </div>
        {/* right: times */}
        <div className="flex gap-2.5 shrink-0">
          <div className="text-right">
            <div className="text-[7px] opacity-40" style={{ color: "var(--ink-muted)" }}>🇲🇽</div>
            <div className="font-display font-black text-[11px] tabular-nums">{cdmxTime(dateISO)}</div>
          </div>
          <div className="text-right">
            <div className="text-[7px] opacity-40" style={{ color: "var(--ink-muted)" }}>🇺🇸</div>
            <div className="font-display font-black text-[11px] tabular-nums">{etTime(dateISO)}</div>
          </div>
        </div>
      </div>

      {/* teams + probs */}
      <div className="px-2 pt-2 pb-1 space-y-1.5">
        <TeamRow code={teamA} token={tokenA} side="A" />

        {/* separator */}
        <div className="flex items-center gap-2 px-2 my-0.5">
          <div className="flex-1 h-px bg-[var(--line)]" />
          <span className="text-[9px] font-display font-black tracking-widest text-[var(--ink-muted)]">VS</span>
          <div className="flex-1 h-px bg-[var(--line)]" />
        </div>

        <TeamRow code={teamB} token={tokenB} side="B" />
      </div>

      {/* Probability thermometer */}
      {teamA && teamB && !isPlayed && (
        <div className="px-3 pb-2">
          <KOMatchProbBar homeCode={teamA} awayCode={teamB} />
        </div>
      )}

      {/* consensus row */}
      {(teamA || teamB) && (
        <div className="border-t border-[var(--line)]/30 mx-2 mb-2">
          <ConsensusRow slotIdx={slotIdx} teamA={teamA} teamB={teamB} allPicksMap={allPicksMap} />
        </div>
      )}

      {/* my pick label */}
      <div className="px-3 pb-2 min-h-[20px]">
        {myPick ? (
          <span className="text-[9px] font-display font-bold" style={{ color: "rgb(94,91,255)" }}>
            📌 Tu pick: {getTeam(myPick)?.name ?? myPick}
          </span>
        ) : !locked && teamA && teamB ? (
          <span className="text-[9px]" style={{ color: "var(--ink-muted)", opacity: 0.5 }}>
            👆 Toca un equipo para elegir
          </span>
        ) : locked && !myPick && teamA ? (
          <span className="text-[9px]" style={{ color: "var(--ink-muted)", opacity: 0.4 }}>🔒 Partido bloqueado</span>
        ) : null}
      </div>
    </motion.article>
  );
}

// Alias to satisfy TS inside MatchCard (module-level const)
const VENUE_BY_MAP = new Map(VENUES.map(v => [v.city, v]));

// ─── R16 pick card ────────────────────────────────────────────────────────

function R16PickCard({
  slotIdx,
  teamA,
  teamB,
  dateISO,
  venueStadium,
  venueCity,
  myPick,
  onPick,
  now,
  slotScore,
}: {
  slotIdx: number;
  teamA: string;
  teamB: string;
  dateISO: string;
  venueStadium: string;
  venueCity: string;
  myPick: string;
  onPick: (code: string) => void;
  now: number | null;
  slotScore?: string;
}) {
  const slot = `R16-${slotIdx + 1}`;
  const locked = isKOSlotLocked(slot, now ?? Date.now());
  const tA = teamA ? getTeam(teamA) : null;
  const tB = teamB ? getTeam(teamB) : null;
  const hasBoth = !!teamA && !!teamB;
  const cd = countdown(dateISO, now);
  const status = liveStatus(dateISO, now);
  const isPlayed = status === "played";
  const isLive = status === "live";

  // Per-player picks for locked/finished slots
  const [allPicks, setAllPicks] = useState<Record<string, string | null> | null>(null);
  useEffect(() => {
    if (!locked && !isPlayed) return;
    fetch(`/api/ko/match-picks?slot=${slot}`)
      .then(r => r.json())
      .then(d => { if (d.ok) setAllPicks(d.picks as Record<string, string | null>); })
      .catch(() => {});
  }, [slot, locked, isPlayed]);

  // Derive winner from score
  const [sA, sB] = slotScore?.split("-").map(Number) ?? [null, null];
  const winner = sA !== null && sB !== null ? (sA > sB ? teamA : sB > sA ? teamB : null) : null;

  const humanPlayers = PLAYERS.filter(p => !p.isBot);

  function TeamBtn({ code }: { code: string }) {
    const team = code ? getTeam(code) : null;
    const picked = myPick === code && !!code;
    const canPick = !locked && hasBoth && !!code;
    const El = canPick ? "button" : "div";
    return (
      <El
        type={canPick ? "button" : undefined}
        onClick={canPick ? () => onPick(code) : undefined}
        className={`relative flex items-center gap-2.5 w-full rounded-xl px-3 py-2.5 transition-all select-none ${canPick ? "cursor-pointer" : "cursor-default"}`}
        style={picked
          ? { background: "rgba(94,91,255,0.10)", boxShadow: "inset 0 0 0 1.5px rgba(94,91,255,0.55)" }
          : { background: "var(--bg-tint)", opacity: !hasBoth ? 0.45 : 1 }
        }
      >
        {team ? (
          <div className="relative w-8 h-8 rounded-lg overflow-hidden ring-1 ring-black/10 shrink-0 shadow-sm">
            <Image src={flagUrl(team.iso2, 48)} alt={team.name} fill sizes="32px" className="object-cover" unoptimized />
          </div>
        ) : (
          <div className="w-8 h-8 rounded-lg bg-[var(--bg)] shrink-0 grid place-items-center text-[var(--ink-muted)] font-bold text-base">?</div>
        )}
        <div className="flex-1 min-w-0">
          <div className="font-display font-bold text-[13px] leading-tight truncate">{team?.name ?? "TBD"}</div>
          <div className="text-[10px] opacity-50" style={{ color: "var(--ink-muted)" }}>{team?.code ?? "—"}</div>
        </div>
        {picked && (
          <span className="shrink-0 text-[9px] font-black px-1.5 py-0.5 rounded-full"
            style={{ background: "rgba(94,91,255,0.15)", color: "rgb(94,91,255)" }}>
            📌 elegido
          </span>
        )}
      </El>
    );
  }

  return (
    <motion.article
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25 }}
      className="rounded-2xl overflow-hidden"
      style={{
        background: "var(--bg-tint)",
        border: "1px solid var(--line)",
        boxShadow: "0 2px 12px -4px rgba(0,0,0,0.1)",
      }}
    >
      {/* header strip */}
      <div
        className="px-3 pt-2 pb-2 flex items-center gap-2 border-b border-[var(--line)]/25"
        style={{
          background: isLive
            ? "rgba(239,68,68,0.08)"
            : isPlayed
            ? "rgba(0,0,0,0.04)"
            : "rgba(20,200,120,0.04)",
        }}
      >
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-1.5 mb-0.5">
            {isLive && <span className="live-dot" />}
            <span
              className="font-display font-black text-[9px] uppercase tracking-[0.2em]"
              style={{ color: isLive ? "rgb(239,68,68)" : isPlayed ? "var(--ink-muted)" : "rgb(20,200,120)" }}
            >
              {isLive ? `EN VIVO · ${slot}` : isPlayed ? `FIN · ${slot}` : `${cd ?? "Próximo"} · ${slot}`}
            </span>
            {locked && !isPlayed && !isLive && <Lock size={8} className="opacity-40" style={{ color: "var(--ink-muted)" }} />}
          </div>
          <div className="flex items-center gap-1" style={{ color: "var(--ink-muted)" }}>
            <MapPin size={7} className="shrink-0 opacity-50" />
            <span className="text-[8px] truncate opacity-60">{venueStadium} · {venueCity}</span>
          </div>
        </div>
        <div className="flex gap-2.5 shrink-0">
          <div className="text-right">
            <div className="text-[7px] opacity-40" style={{ color: "var(--ink-muted)" }}>🇲🇽</div>
            <div className="font-display font-black text-[11px] tabular-nums">{cdmxTime(dateISO)}</div>
          </div>
          <div className="text-right">
            <div className="text-[7px] opacity-40" style={{ color: "var(--ink-muted)" }}>🇺🇸</div>
            <div className="font-display font-black text-[11px] tabular-nums">{etTime(dateISO)}</div>
          </div>
        </div>
      </div>

      {/* teams */}
      <div className="px-2 pt-2 pb-1 space-y-1">
        <TeamBtn code={teamA} />
        <div className="flex items-center gap-2 px-2 my-0.5">
          <div className="flex-1 h-px bg-[var(--line)]" />
          <span className="text-[9px] font-display font-black tracking-widest text-[var(--ink-muted)]">VS</span>
          <div className="flex-1 h-px bg-[var(--line)]" />
        </div>
        <TeamBtn code={teamB} />
      </div>

      {/* footer */}
      <div className="px-3 pb-2 min-h-[20px]">
        {myPick ? (
          <span className="text-[9px] font-display font-bold" style={{ color: "rgb(94,91,255)" }}>
            📌 Tu pick: {getTeam(myPick)?.name ?? myPick}
          </span>
        ) : !locked && hasBoth ? (
          <span className="text-[9px]" style={{ color: "var(--ink-muted)", opacity: 0.5 }}>
            👆 Toca un equipo para elegir
          </span>
        ) : !hasBoth ? (
          <span className="text-[9px]" style={{ color: "var(--ink-muted)", opacity: 0.35 }}>
            Esperando resultado R32…
          </span>
        ) : null}
      </div>

      {/* Charales picks row for locked/finished R16 slots */}
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
    </motion.article>
  );
}

// Official FIFA 2026 R16 pairings — verified against ESPN scheduled matchups
// (July 4-7, 2026). Each entry is [R32-slotA, R32-slotB] for R16-N.
const R16_PAIRINGS: Array<[number, number]> = [
  [1, 3],    // R16-1: winner R32-1 vs winner R32-3  (CAN vs MAR)
  [2, 5],    // R16-2: winner R32-2 vs winner R32-5  (PAR vs FRA)
  [4, 6],    // R16-3: winner R32-4 vs winner R32-6  (BRA vs NOR)
  [7, 8],    // R16-4: winner R32-7 vs winner R32-8  (MEX vs ENG)
  [11, 12],  // R16-5: winner R32-11 vs winner R32-12 (POR vs ESP)
  [9, 10],   // R16-6: winner R32-9 vs winner R32-10  (USA vs BEL)
  [14, 16],  // R16-7: winner R32-14 vs winner R32-16 (ARG vs EGY)
  [13, 15],  // R16-8: winner R32-13 vs winner R32-15 (SUI vs COL)
];

function R16Section({
  slotResults,
  slotScores,
  r16Picks,
  onPick,
  now,
}: {
  slotResults: Record<string, string>;
  slotScores: Record<string, string>;
  r16Picks: string[];
  onPick: (idx: number, code: string) => void;
  now: number | null;
}) {
  const r16Schedule = useMemo(
    () => KO_SCHEDULE.filter(m => m.round === "R16").sort((a, b) => new Date(a.dateISO).getTime() - new Date(b.dateISO).getTime()),
    [],
  );

  // Only show when at least one R16 pairing is known
  const knownPairings = r16Schedule.filter((_, i) => {
    const [a, b] = R16_PAIRINGS[i] ?? [0, 0];
    return slotResults[`R32-${a}`] || slotResults[`R32-${b}`];
  });

  if (knownPairings.length === 0) return null;

  return (
    <div className="mt-6">
      <div className="flex items-center gap-2 mb-3">
        <Zap size={13} style={{ color: "rgb(20,200,120)" }} />
        <span className="font-display font-black text-[11px] uppercase tracking-[0.22em]" style={{ color: "rgb(20,200,120)" }}>
          Octavos de Final
        </span>
        <span className="text-[8px] font-bold px-1.5 py-0.5 rounded-full" style={{ background: "rgba(20,200,120,0.12)", color: "rgb(20,200,120)" }}>
          {knownPairings.length}/{r16Schedule.length} definidos
        </span>
      </div>
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
        {r16Schedule.map((ko, i) => {
          const [a, b] = R16_PAIRINGS[i] ?? [0, 0];
          const teamA = slotResults[`R32-${a}`] ?? "";
          const teamB = slotResults[`R32-${b}`] ?? "";
          return (
            <R16PickCard
              key={ko.slot}
              slotIdx={i}
              teamA={teamA}
              teamB={teamB}
              dateISO={ko.dateISO}
              venueStadium={ko.venueStadium}
              venueCity={ko.venueCity}
              myPick={r16Picks[i] ?? ""}
              onPick={(code) => onPick(i, code)}
              now={now}
              slotScore={slotScores[ko.slot]}
            />
          );
        })}
      </div>
    </div>
  );
}

// ─── Main section ─────────────────────────────────────────────────────────

export function KnockoutSection() {
  const { results: real } = useGroupRealResults();
  const now = useNow(15_000);
  const { currentPlayer } = usePlayer();

  // R32 pairings derived from real group results
  const pairings = useMemo(() => computeR32Pairings(blank("__ko__"), real), [real]);

  // My R32 picks
  const [r32Picks, setR32Picks] = useState<string[]>(() => Array(16).fill(""));

  useEffect(() => {
    if (!currentPlayer) return;
    const pred = loadPredictions(currentPlayer.id);
    setR32Picks(pred.bracket?.R32 ?? Array(16).fill(""));
  }, [currentPlayer]);

  useEffect(() => {
    if (!currentPlayer) return;
    const refresh = () => setR32Picks(loadPredictions(currentPlayer.id).bracket?.R32 ?? Array(16).fill(""));
    window.addEventListener("q26:predictions-updated", refresh);
    return () => window.removeEventListener("q26:predictions-updated", refresh);
  }, [currentPlayer]);

  // All Charales bracket picks (for consensus)
  const [allPicksMap, setAllPicksMap] = useState<Record<string, BracketPick>>({});
  useEffect(() => {
    loadAllPredictionsFromServer().then(all => {
      const m: Record<string, BracketPick> = {};
      for (const p of all) { if (p.bracket) m[p.playerId] = p.bracket; }
      setAllPicksMap(m);
    }).catch(() => {});
  }, []);

  // Card refs for auto-scroll
  const cardRefs = useRef<Array<HTMLElement | null>>(Array(16).fill(null));

  const savePick = useCallback((slotIdx: number, code: string) => {
    if (!currentPlayer) return;
    setR32Picks(prev => {
      const next = [...prev];
      if (next[slotIdx] === code) return prev; // no-op if already selected
      next[slotIdx] = code;
      const pred = loadPredictions(currentPlayer.id);
      pred.bracket = { ...(pred.bracket ?? {}), R32: next };
      savePredictions(pred);

      // Auto-scroll to next unpicked unlocked slot
      setTimeout(() => {
        for (let i = slotIdx + 1; i < 16; i++) {
          const slot = `R32-${i + 1}`;
          if (!isKOSlotLocked(slot) && !next[i] && pairings[i]?.teams[0] && pairings[i]?.teams[1]) {
            cardRefs.current[i]?.scrollIntoView({ behavior: "smooth", block: "center" });
            break;
          }
        }
      }, 200);

      return next;
    });
  }, [currentPlayer, pairings]);

  // Progress
  const pickCount = r32Picks.filter(p => !!p).length;
  const totalPickable = pairings.filter((p, i) => !isKOSlotLocked(`R32-${i + 1}`) && p.teams[0] && p.teams[1]).length;

  // AI auto-pick
  const [aiState, setAiState] = useState<"idle" | "loading" | "done">("idle");
  const [aiMsg, setAiMsg] = useState("");

  const handleAiPick = useCallback(async () => {
    if (!currentPlayer || aiState === "loading") return;
    const slots = pairings
      .map((p, i) => {
        const slot = `R32-${i + 1}`;
        if (isKOSlotLocked(slot) || !p.teams[0] || !p.teams[1]) return null;
        const prob = matchProbability(p.teams[0], p.teams[1]);
        const tot = prob.H + prob.A;
        const h = Math.round(prob.H / tot * 100);
        return { slot, teamA: p.teams[0], teamB: p.teams[1], hPct: h, aPct: 100 - h };
      })
      .filter(Boolean);

    if (!slots.length) return;
    setAiState("loading");
    try {
      const res = await fetch("/api/bracket/ai-picks", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ slots }),
      });
      const data = await res.json() as { ok: boolean; picks?: Array<{ slot: string; pick: string }> };
      if (!data.ok || !data.picks?.length) throw new Error();

      setR32Picks(prev => {
        const next = [...prev];
        for (const pk of data.picks!) {
          const idx = parseInt(pk.slot.replace("R32-", ""), 10) - 1;
          if (idx >= 0 && idx < 16 && !isKOSlotLocked(pk.slot)) next[idx] = pk.pick;
        }
        const pred = loadPredictions(currentPlayer.id);
        pred.bracket = { ...(pred.bracket ?? {}), R32: next };
        savePredictions(pred);
        return next;
      });
      setAiMsg(`✨ IA eligió ${data.picks.length} ganadores`);
    } catch {
      setAiMsg("Error al consultar IA");
    } finally {
      setAiState("done");
      setTimeout(() => { setAiState("idle"); setAiMsg(""); }, 4000);
    }
  }, [currentPlayer, pairings, aiState]);

  // Shake detection → auto-suggest pick for first empty card
  useEffect(() => {
    if (typeof window === "undefined" || !currentPlayer) return;
    let lastShake = 0;
    const THRESH = 18;

    function onMotion(e: DeviceMotionEvent) {
      const a = e.accelerationIncludingGravity;
      if (!a) return;
      const mag = Math.sqrt((a.x ?? 0) ** 2 + (a.y ?? 0) ** 2 + (a.z ?? 0) ** 2);
      if (mag < THRESH) return;
      if (Date.now() - lastShake < 1500) return;
      lastShake = Date.now();

      // Find first unlocked unpicked slot with both teams known
      setR32Picks(prev => {
        for (let i = 0; i < 16; i++) {
          const slot = `R32-${i + 1}`;
          if (!isKOSlotLocked(slot) && !prev[i] && pairings[i]?.teams[0] && pairings[i]?.teams[1]) {
            const [tA, tB] = pairings[i].teams;
            const prob = matchProbability(tA, tB);
            const pick = prob.H >= prob.A ? tA : tB;
            const next = [...prev];
            next[i] = pick;
            const pred = loadPredictions(currentPlayer!.id);
            pred.bracket = { ...(pred.bracket ?? {}), R32: next };
            savePredictions(pred);
            cardRefs.current[i]?.scrollIntoView({ behavior: "smooth", block: "center" });
            break;
          }
        }
        return prev; // state update happens inside
      });
    }

    window.addEventListener("devicemotion", onMotion);
    return () => window.removeEventListener("devicemotion", onMotion);
  }, [currentPlayer, pairings]);

  // Sort R32 matches by date
  const r32Schedule = useMemo(
    () => KO_SCHEDULE.filter(m => m.round === "R32").sort((a, b) => new Date(a.dateISO).getTime() - new Date(b.dateISO).getTime()),
    [],
  );

  // Scores + results from ESPN (for compact played rows and R16 section)
  const [slotScores, setSlotScores] = useState<Record<string, string>>({});
  const [slotResults, setSlotResults] = useState<Record<string, string>>({});
  useEffect(() => {
    fetch("/api/bracket/ko-results")
      .then(r => r.json())
      .then(d => {
        if (d.ok) {
          if (d.slotScores) setSlotScores(d.slotScores);
          if (d.slotResults) setSlotResults(d.slotResults);
        }
      })
      .catch(() => {});
  }, []);

  // All players' picks per R32 slot (keyed by slot string e.g. "R32-1")
  const [slotAllPicks, setSlotAllPicks] = useState<Record<string, Record<string, string | null>>>({});
  useEffect(() => {
    // Fetch per-slot picks for all played matches
    const played = r32Schedule.filter(ko => liveStatus(ko.dateISO, now) === "played");
    if (played.length === 0) return;
    Promise.all(
      played.map(ko =>
        fetch(`/api/ko/match-picks?slot=${ko.slot}`)
          .then(r => r.json())
          .then(d => d.ok ? { slot: ko.slot, picks: d.picks as Record<string, string | null> } : null)
          .catch(() => null)
      )
    ).then(results => {
      const m: Record<string, Record<string, string | null>> = {};
      for (const r of results) {
        if (r) m[r.slot] = r.picks;
      }
      setSlotAllPicks(m);
    });
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [r32Schedule, now]);

  // R16 picks — stable string dep (not the whole object) to avoid spurious re-runs on profile refresh
  const [r16Picks, setR16Picks] = useState<string[]>(() => Array(8).fill(""));
  const currentPlayerId = currentPlayer?.id ?? null;
  useEffect(() => {
    if (!currentPlayerId) return;
    const stored = loadPredictions(currentPlayerId).bracket?.R16;
    setR16Picks((stored && stored.length > 0) ? stored : Array(8).fill(""));
  }, [currentPlayerId]); // eslint-disable-line
  useEffect(() => {
    if (!currentPlayerId) return;
    const refresh = () => {
      const stored = loadPredictions(currentPlayerId).bracket?.R16;
      setR16Picks((stored && stored.length > 0) ? stored : Array(8).fill(""));
    };
    window.addEventListener("q26:predictions-updated", refresh);
    return () => window.removeEventListener("q26:predictions-updated", refresh);
  }, [currentPlayerId]); // eslint-disable-line
  const saveR16Pick = useCallback((idx: number, code: string) => {
    if (!currentPlayer) return;
    setR16Picks(prev => {
      const next = Array(8).fill("") as string[];
      for (let i = 0; i < 8; i++) next[i] = prev[i] ?? "";
      if (next[idx] === code) return prev; // no-op if already selected
      next[idx] = code;
      const pred = loadPredictions(currentPlayer.id);
      const existingR16 = (pred.bracket?.R16 as string[] | undefined);
      const base: string[] = Array(8).fill("");
      if (existingR16 && existingR16.length > 0) {
        for (let i = 0; i < 8; i++) base[i] = existingR16[i] ?? "";
      }
      base[idx] = code;
      pred.bracket = { ...(pred.bracket ?? {}), R16: base };
      savePredictions(pred); // savePredictions already dispatches q26:predictions-updated
      return next;
    });
  }, [currentPlayer]);

  // Helper: is dateISO "today" in CDMX?
  function isTodayCDMX(dateISO: string): boolean {
    if (!now) return false;
    const nowStr = new Intl.DateTimeFormat("sv-SE", { timeZone: "America/Mexico_City" }).format(new Date(now));
    const matchStr = new Intl.DateTimeFormat("sv-SE", { timeZone: "America/Mexico_City" }).format(new Date(dateISO));
    return nowStr === matchStr;
  }

  // Bucket matches — today's matches are already shown in KOMatchFeed, skip them here
  const upcomingMatches = r32Schedule.filter(ko => {
    const st = liveStatus(ko.dateISO, now);
    return st === "upcoming" && !isTodayCDMX(ko.dateISO);
  });
  const playedMatches = r32Schedule.filter(ko => liveStatus(ko.dateISO, now) === "played");

  function renderMatchCard(ko: typeof r32Schedule[number]) {
    const slotNum = parseInt(ko.slot.replace("R32-", ""), 10);
    const idx = slotNum - 1;
    const pairing = pairings[idx];
    const [tA, tB] = pairing?.teams ?? ["", ""];
    const [tokA, tokB] = R32_TEMPLATE[idx] ?? ["", ""];
    return (
      <MatchCard
        key={ko.slot}
        slotIdx={idx}
        teamA={tA}
        teamB={tB}
        tokenA={tokA}
        tokenB={tokB}
        dateISO={ko.dateISO}
        venueCity={ko.venueCity}
        venueStadium={ko.venueStadium}
        myPick={r32Picks[idx] ?? ""}
        onPick={(code) => savePick(idx, code)}
        allPicksMap={allPicksMap}
        now={now}
        cardRef={el => { cardRefs.current[idx] = el; }}
      />
    );
  }

  return (
    <section className="container-app pt-4 pb-6">
      {/* ── HEADER ── */}
      <div className="mb-5">
        <div className="flex items-center gap-2 mb-3">
          <Zap size={13} style={{ color: "rgb(94,91,255)" }} />
          <span className="font-display font-black text-[11px] uppercase tracking-[0.22em]" style={{ color: "rgb(94,91,255)" }}>
            Dieciseisavos · Mundial 2026
          </span>
        </div>

        <div className="flex items-center gap-3 flex-wrap">
          {currentPlayer && (
            <div className="flex items-center gap-2 flex-1 min-w-0">
              <div className="flex-1 h-1.5 rounded-full overflow-hidden" style={{ background: "var(--bg-tint)" }}>
                <motion.div
                  className="h-full rounded-full"
                  style={{ background: "linear-gradient(90deg, rgb(94,91,255), rgb(20,200,120))" }}
                  initial={{ width: 0 }}
                  animate={{ width: totalPickable > 0 ? `${Math.round(pickCount / 16 * 100)}%` : "0%" }}
                  transition={{ duration: 0.5 }}
                />
              </div>
              <span className="text-[10px] font-display font-bold tabular-nums shrink-0" style={{ color: pickCount === 16 ? "rgb(20,180,100)" : "var(--ink-muted)" }}>
                {pickCount}/16 ✓
              </span>
            </div>
          )}
          {currentPlayer && (
            <button
              type="button"
              onClick={handleAiPick}
              disabled={aiState === "loading"}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-full text-[11px] font-display font-bold shrink-0 transition-opacity"
              style={{
                background: "linear-gradient(135deg, rgba(94,91,255,0.18), rgba(20,241,149,0.14))",
                boxShadow: "0 0 0 1px rgba(94,91,255,0.25)",
                opacity: aiState === "loading" ? 0.6 : 1,
              }}
            >
              {aiState === "loading"
                ? <span className="inline-block w-3 h-3 border-2 border-purple-400/50 border-t-purple-600 rounded-full animate-spin" />
                : "🤖"}
              {aiState === "loading" ? "Pensando…" : "Auto-pick IA"}
            </button>
          )}
          {aiMsg && <span className="text-[10px] font-bold" style={{ color: "rgb(10,150,90)" }}>{aiMsg}</span>}
        </div>
      </div>

      {/* ── PRÓXIMOS (excluye hoy — ya están en KOMatchFeed) ── */}
      {upcomingMatches.length > 0 && (
        <div className="mb-5">
          <div className="flex items-center gap-2 mb-2.5">
            <span className="text-[9px] font-display font-black uppercase tracking-[0.22em]" style={{ color: "rgb(94,91,255)" }}>
              Próximos
            </span>
          </div>
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
            {upcomingMatches.map(ko => renderMatchCard(ko))}
          </div>
        </div>
      )}

      {/* ── JUGADOS — always visible, no toggle needed ── */}
      {playedMatches.length > 0 && (
        <div className="mb-4">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-[9px] font-display font-black uppercase tracking-[0.22em]" style={{ color: "var(--ink-muted)" }}>
              R32 · Jugados
            </span>
            <span className="text-[8px] font-bold px-1.5 py-0.5 rounded-full" style={{ background: "var(--bg)", color: "var(--ink-muted)" }}>
              {playedMatches.length}
            </span>
          </div>
          <div className="space-y-1.5">
            {playedMatches.map(ko => {
              const slotNum = parseInt(ko.slot.replace("R32-", ""), 10);
              const idx = slotNum - 1;
              const pairing = pairings[idx];
              const [tA, tB] = pairing?.teams ?? ["", ""];
              return (
                <PlayedPill
                  key={ko.slot}
                  slotIdx={idx}
                  teamA={tA}
                  teamB={tB}
                  myPick={r32Picks[idx] ?? ""}
                  scoreStr={slotScores[ko.slot]}
                  allPicks={slotAllPicks[ko.slot]}
                />
              );
            })}
          </div>
        </div>
      )}

      {/* ── OCTAVOS DE FINAL ── R16 picks, shown as teams become known */}
      <R16Section slotResults={slotResults} slotScores={slotScores} r16Picks={r16Picks} onPick={saveR16Pick} now={now} />

      {/* footer hint */}
      <div className="mt-5 flex items-center justify-center gap-2 text-[9px] uppercase tracking-[0.22em]" style={{ color: "var(--ink-muted)", opacity: 0.35 }}>
        <Trophy size={9} />
        Agita el teléfono para auto-picar el favorito del slot vacío
      </div>
    </section>
  );
}
