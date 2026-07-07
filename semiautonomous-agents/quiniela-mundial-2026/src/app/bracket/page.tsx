"use client";

// /bracket — Mundial 2026 global knockout tracker.
//
// Visual: symmetric tree converging on a centered trophy ("Copa Mundial 2026").
// Left  side: R32 slots 1..8  -> R16 (4) -> QF (2) -> SF (1) -> Final.
// Right side: R32 slots 9..16 -> R16 (4) -> QF (2) -> SF (1) -> Final.
//
// Data sources:
//   - computeR32Pairings(emptyPicks, realResults)  -> R32 reshapes live from group stage.
//   - Downstream rounds (R16, QF, SF, Final) stay as "?" placeholders showing both
//     candidate flags faintly, because we don't yet wire real knockout-round results
//     into the data model. The bracket simply reshapes its FEEDER PAIRINGS as groups
//     finish, which is the main effect the user wants to see.
//
// Animations: SVG connectors stroke-draw in, chips fade+scale, hovered team lights
// its whole path, trophy gently shimmers, real-resolved slots pulse gold.

import Link from "next/link";
import Image from "next/image";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { AnimatePresence, motion, useInView } from "framer-motion";
import { Trophy, Sparkles, Activity, ArrowLeft, RadioTower, MapPin, CalendarClock } from "lucide-react";
import { flagUrl, getTeam } from "@/data/teams";
import { matchProbability } from "@/data/team-strength";
import { useGroupRealResults } from "@/lib/real-results";
import { usePlayer } from "@/lib/player-context";
import { loadPredictions, savePredictions } from "@/lib/predictions";
import { isKOSlotLocked } from "@/lib/fixture-time";
import {
  computeR32Pairings,
  computeThirdPlaceRanking,

  groupConfirmed,
  groupRealCount,
  slotConfirmed,
  R32_TEMPLATE,
  THIRD_TOKEN_TO_ANCHOR,
  type R32Pairing,
  type RealResults,
  type Standing,
} from "@/lib/standings";
import { simulateThirdSlotProbabilities, type ThirdSlotProb } from "@/lib/third-sim";
import { blank, type PlayerPredictions } from "@/lib/predictions";
import { GROUP_LETTERS } from "@/data/groups";
import { findKOMatch, type KOMatch } from "@/data/knockout-schedule";
import { VENUES } from "@/data/venues";
import { useLocale, intlLocale } from "@/lib/i18n";
import { useNow } from "@/lib/use-now";
import { BracketLiveCard } from "@/components/BracketLiveCard";
import { slotStateMap, type SlotState } from "@/lib/bracket-scenarios";
import { useScoreboard } from "@/lib/scoreboard-cache";

const EMPTY_PICKS: PlayerPredictions = blank("__tracker__");

type RoundKey = "R32" | "R16" | "QF" | "SF" | "FINAL";

const ROUND_LABEL: Record<RoundKey, string> = {
  R32: "Dieciseisavos",
  R16: "Octavos",
  QF: "Cuartos",
  SF: "Semis",
  FINAL: "Final",
};

// Match slot model used for the whole tree. `teams` is the [a,b] pair that
// could play this match. `winner` is set only when both feeder matches are
// resolved AND a real result is available (we currently only know that for
// the group stage feeders into R32).
type Slot = {
  id: string;
  round: RoundKey;
  // Index inside the round (0-based)
  idx: number;
  // The two candidate teams (codes). May be empty strings if not yet known.
  teams: [string, string];
  // Winner if known (we only mark it from real group results into R32 pairings,
  // never auto-pick a knockout winner — that's reality's job).
  winner?: string;
  // Whether this slot was just resolved by a real result (used for pulse glow).
  resolved: boolean;
  // True only when the source group(s) of this slot's pairing have closed.
  // R32 slots → both feeder groups confirmed. Downstream rounds → all R32
  // feeders confirmed (i.e. inherits from parents).
  confirmed: boolean;
};

// Builds the full bracket tree from the R32 pairings.
// Currently we only have R32 pairings dynamic; downstream slots remain
// candidate-pair shells (both flags faintly until played).
function buildTree(r32: R32Pairing[], real: RealResults): Record<RoundKey, Slot[]> {
  const r32Slots: Slot[] = r32.map((p, i) => ({
    id: `R32-${i}`,
    round: "R32",
    idx: i,
    teams: p.teams,
    resolved: Boolean(p.teams[0] && p.teams[1]),
    confirmed: slotConfirmed(p, real),
  }));

  function nextRound(prev: Slot[], round: RoundKey): Slot[] {
    const out: Slot[] = [];
    for (let i = 0; i < prev.length; i += 2) {
      const a = prev[i];
      const b = prev[i + 1];
      const candidates: string[] = [];
      const aTeams = a?.winner ? [a.winner] : a?.teams.filter(Boolean) ?? [];
      const bTeams = b?.winner ? [b.winner] : b?.teams.filter(Boolean) ?? [];
      candidates.push(...aTeams.slice(0, 1), ...bTeams.slice(0, 1));
      out.push({
        id: `${round}-${i / 2}`,
        round,
        idx: i / 2,
        teams: [candidates[0] ?? "", candidates[1] ?? ""],
        resolved: false,
        confirmed: Boolean(a?.confirmed && b?.confirmed),
      });
    }
    return out;
  }

  const r16 = nextRound(r32Slots, "R16");
  const qf = nextRound(r16, "QF");
  const sf = nextRound(qf, "SF");
  const fnl = nextRound(sf, "FINAL");

  return { R32: r32Slots, R16: r16, QF: qf, SF: sf, FINAL: fnl };
}

// Compute downstream path slot ids that a given R32 slot index participates in.
// Used for hover-to-light a team's potential path through the tree.
// Ids include the side prefix to match `splitSide`'s namespacing.
function pathForR32(r32Idx: number, side: "left" | "right"): string[] {
  const prefix = side === "left" ? "L" : "R";
  const out: string[] = [`${prefix}-R32-${r32Idx}`];
  let i = r32Idx;
  let round: RoundKey = "R32";
  const next: Record<RoundKey, RoundKey | null> = { R32: "R16", R16: "QF", QF: "SF", SF: "FINAL", FINAL: null };
  let nr: RoundKey | null = next[round];
  while (nr !== null) {
    i = Math.floor(i / 2);
    out.push(`${prefix}-${nr}-${i}`);
    round = nr;
    nr = next[round];
  }
  return out;
}

export default function BracketPage() {
  const { results: real, loading } = useGroupRealResults();
  const { fetchedAt, refresh } = useScoreboard();
  const now = useNow(1_000);
  const r32Pairings = useMemo(() => computeR32Pairings(EMPTY_PICKS, real), [real]);
  const tree = useMemo(() => buildTree(r32Pairings, real), [r32Pairings, real]);
  // Per-token slot state lookup — used by both desktop and mobile views so
  // each individual team can render its own CONF/PROY chip even when the
  // pairing it belongs to is half-resolved.
  const slotStates = useMemo(() => slotStateMap(real), [real]);

  const confirmedGroups = useMemo(
    () => GROUP_LETTERS.filter(l => groupConfirmed(l, real)).length,
    [real],
  );

  // Pulse a fresh-data ring whenever the scoreboard cache delivers a new tick.
  // We capture the previous fetchedAt and run a brief CSS animation when it
  // advances, so the user gets visual confirmation that the tracker IS live.
  const [pulse, setPulse] = useState(false);
  const prevFetchedRef = useRef(fetchedAt);
  useEffect(() => {
    if (fetchedAt > prevFetchedRef.current) {
      prevFetchedRef.current = fetchedAt;
      setPulse(true);
      const id = setTimeout(() => setPulse(false), 1200);
      return () => clearTimeout(id);
    }
  }, [fetchedAt]);

  const secondsAgo = fetchedAt && now ? Math.max(0, Math.round((now - fetchedAt) / 1000)) : null;
  const updatedLabel = secondsAgo === null
    ? "Sincronizando…"
    : secondsAgo < 5
      ? "Recién actualizado"
      : secondsAgo < 60
        ? `Hace ${secondsAgo}s`
        : `Hace ${Math.round(secondsAgo / 60)}min`;

  return (
    <div className="bg-canvas min-h-screen">
      <section className="container-app pt-6 pb-4">
        <Link href="/" className="inline-flex items-center gap-1.5 text-xs font-semibold text-[var(--ink-soft)] hover:text-[var(--ink)] transition-colors">
          <ArrowLeft size={12} /> Inicio
        </Link>
        <div className="mt-4 flex items-end justify-between gap-4 flex-wrap">
          <div>
            <div className="chip mb-2">
              <RadioTower size={11} /> Tracker en vivo
            </div>
            <h1 className="font-display text-3xl md:text-5xl font-bold leading-tight">
              <span className="grad-text">Bracket</span> del Mundial 2026
            </h1>
            <p className="mt-2 text-sm md:text-base text-[var(--ink-soft)] max-w-2xl">
              <strong>PROYECTADO</strong> mientras los grupos no cierran (slots usan picks agregados). <strong>CONFIRMADO</strong> en verde sólo cuando los 6 partidos del grupo fuente terminaron en la vida real.
            </p>
          </div>
          <div className="flex items-center gap-2 flex-wrap">
            <span className="chip" style={{ background: confirmedGroups > 0 ? "rgba(20,241,149,0.15)" : "var(--bg-tint)", color: "var(--ink)" }}>
              {confirmedGroups > 0 && <span className="live-dot" />}
              {confirmedGroups}/12 grupos confirmados
            </span>
            <button
              type="button"
              onClick={() => refresh(true)}
              title="Forzar sincronización"
              className={`chip transition-all ${pulse ? "ring-2 ring-[var(--accent-mint,#14F195)]" : ""}`}
              style={{
                background: pulse ? "rgba(20,241,149,0.18)" : "var(--bg-tint)",
                color: "var(--ink-soft)",
                cursor: "pointer",
              }}
            >
              <Activity size={11} className={loading ? "animate-pulse" : ""} />
              {loading ? "Sincronizando…" : updatedLabel}
            </button>
          </div>
        </div>

        {/* Per-group progress strip */}
        <div className="mt-4 grid grid-cols-6 sm:grid-cols-12 gap-1.5">
          {GROUP_LETTERS.map(letter => {
            const { played, total } = groupRealCount(letter, real);
            const confirmed = played === total;
            const partial = played > 0 && played < total;
            const bg = confirmed
              ? "rgba(20,241,149,0.18)"
              : partial
                ? "rgba(251,191,36,0.18)"
                : "var(--bg-tint)";
            const fg = confirmed
              ? "var(--ink)"
              : partial
                ? "rgb(146,90,7)"
                : "var(--ink-muted)";
            return (
              <div key={letter} className="rounded-lg px-2 py-1.5 text-center" style={{ background: bg, color: fg }} title={`Grupo ${letter}: ${played} de ${total} partidos`}>
                <div className="font-display font-bold text-[10px]">{letter}</div>
                <div className="text-[10px] tabular-nums font-semibold">{played}/{total}</div>
              </div>
            );
          })}
        </div>
      </section>

      {/* AVA's live read on the bracket: confirmados vs proyectados,
          recent slot deltas vs the last snapshot, and what-if scenarios. */}
      <BracketLiveCard />

      {/* Desktop: full symmetric tree. Mobile: tabbed schedule view. */}
      <div className="hidden md:block">
        <BracketTree tree={tree} slotStates={slotStates} />
      </div>
      <div className="md:hidden">
        <MobileBracket tree={tree} real={real} />
      </div>

      <section className="container-app pb-16 pt-4">
        <div className="glass rounded-2xl p-4 text-xs text-[var(--ink-soft)] leading-relaxed flex items-start gap-2">
          <Sparkles size={14} className="mt-0.5 shrink-0 text-[var(--accent-violet)]" />
          <span>
            <strong className="text-[var(--ink)]">PROYECTADO vs CONFIRMADO.</strong>{" "}
            Mientras los grupos siguen abiertos, los slots son hipótesis derivadas
            de los picks agregados de los charales y los pocos resultados reales
            que ya hay. Un slot se pinta <strong className="text-[var(--ink)]">CONFIRMADO</strong>{" "}
            (verde) sólo cuando los 6 partidos del grupo (o grupos) que lo
            alimentan ya terminaron en la vida real. Pasa el mouse por un equipo
            para ver su camino posible hasta la copa.
          </span>
        </div>
      </section>
    </div>
  );
}

// =====================================================================
//                          DESKTOP TREE
// =====================================================================

// Row heights per round (cards take ~70px, gap doubles each round to keep
// pairs aligned with their feeder's midpoint).
const CARD_H = 64;
const R32_GAP = 12;

// Total height = 16 * 64 + 15 * 12 = 1024 + 180 = 1204
const TOTAL_H = 16 * CARD_H + 15 * R32_GAP;

// y-center of each slot in a round (matches the standard binary-tree center math).
function slotY(round: RoundKey, idx: number): number {
  // Distance between successive slot centers in this round
  // R32: card+gap = 76
  // R16: 2 * 76 = 152, centered between two R32s.
  // QF: 304, SF: 608, FINAL: 1216 (but only 1 slot).
  const step = (CARD_H + R32_GAP) * 2 ** ({ R32: 0, R16: 1, QF: 2, SF: 3, FINAL: 4 }[round]);
  const firstCenter = step / 2;
  return firstCenter + step * idx;
}

const COL_WIDTH = 180;
const COL_GAP = 60;
// Columns (per side): R32, R16, QF, SF.   Center has trophy.   Then mirrored.
const SIDE_COLS: RoundKey[] = ["R32", "R16", "QF", "SF"];

function BracketTree({ tree, slotStates }: { tree: Record<RoundKey, Slot[]>; slotStates: Map<string, SlotState> }) {
  const [hovered, setHovered] = useState<{ team: string; r32Idx: number; side: "left" | "right" } | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const inView = useInView(containerRef, { once: true, margin: "-15%" });

  // Split slots into left (first half) and right (second half).
  const left = useMemo(() => splitSide(tree, "left"), [tree]);
  const right = useMemo(() => splitSide(tree, "right"), [tree]);

  // Build a quick lookup from each R32 slot id (e.g. "L-R32-3") to the
  // two template tokens that feed it — used to fetch per-team status from
  // bracketSlotStates without re-deriving it inside every SlotCard.
  const tokensBySlotId = useMemo(() => {
    const m = new Map<string, [string, string]>();
    for (let i = 0; i < R32_TEMPLATE.length; i++) {
      const tokens = R32_TEMPLATE[i] as unknown as [string, string];
      const half = R32_TEMPLATE.length / 2;
      const side = i < half ? "L" : "R";
      const idxInSide = i % half;
      m.set(`${side}-R32-${idxInSide}`, tokens);
    }
    return m;
  }, []);

  const finalSlot = tree.FINAL[0];

  // Width: 4 side columns + center column (trophy + final card) + 4 side columns
  const sideWidth = SIDE_COLS.length * COL_WIDTH + (SIDE_COLS.length - 1) * COL_GAP;
  const centerWidth = 220;
  const totalWidth = sideWidth * 2 + centerWidth + COL_GAP * 2;

  // Hover path lights ALL slot ids that belong to the hovered team's R32-rooted path.
  const pathIds = useMemo(() => {
    if (!hovered) return new Set<string>();
    return new Set(pathForR32(hovered.r32Idx, hovered.side));
  }, [hovered]);

  return (
    <section className="relative pb-8">
      <motion.div
        ref={containerRef}
        initial={{ scale: 0.95, opacity: 0 }}
        animate={inView ? { scale: 1, opacity: 1 } : {}}
        transition={{ duration: 0.7, ease: [0.22, 1, 0.36, 1] }}
        className="mx-auto overflow-x-auto pb-4"
        style={{ maxWidth: "calc(100vw - 16px)" }}
      >
        <div
          className="relative mx-auto"
          style={{ width: totalWidth, height: TOTAL_H }}
        >
          {/* SVG connectors layer — sits behind cards */}
          <svg
            className="absolute inset-0 w-full h-full pointer-events-none"
            viewBox={`0 0 ${totalWidth} ${TOTAL_H}`}
            preserveAspectRatio="none"
          >
            <defs>
              <filter id="bracket-glow" x="-50%" y="-50%" width="200%" height="200%">
                <feGaussianBlur stdDeviation="3" result="coloredBlur" />
                <feMerge>
                  <feMergeNode in="coloredBlur" />
                  <feMergeNode in="SourceGraphic" />
                </feMerge>
              </filter>
            </defs>
            {renderConnectors({
              left,
              right,
              sideWidth,
              centerWidth,
              colGap: COL_GAP,
              totalWidth,
              hoveredTeam: hovered?.team ?? null,
              hoveredPath: pathIds,
            })}
          </svg>

          {/* LEFT side columns */}
          {SIDE_COLS.map((round, colIdx) => {
            const slots = left[round];
            const x = colIdx * (COL_WIDTH + COL_GAP);
            return (
              <div
                key={`L-${round}`}
                className="absolute top-0"
                style={{ left: x, width: COL_WIDTH, height: TOTAL_H }}
              >
                <RoundLabel round={round} side="left" />
                {slots.map((slot) => {
                  const tokens = slot.round === "R32" ? tokensBySlotId.get(slot.id) : undefined;
                  const stateA = tokens ? slotStates.get(tokens[0]) : undefined;
                  const stateB = tokens ? slotStates.get(tokens[1]) : undefined;
                  return (
                    <SlotCard
                      key={slot.id}
                      slot={slot}
                      side="left"
                      inView={inView}
                      hoveredTeam={hovered?.team ?? null}
                      onHover={(team) => {
                        if (!team) return setHovered(null);
                        // Find the originating R32 idx for the path on this side.
                        const r32Idx = findR32Idx(left, team);
                        if (r32Idx >= 0) setHovered({ team, r32Idx, side: "left" });
                      }}
                      inPath={pathIds.has(slot.id)}
                      teamAStatus={stateA?.status}
                      teamBStatus={stateB?.status}
                    />
                  );
                })}
              </div>
            );
          })}

          {/* CENTER — trophy + final */}
          <div
            className="absolute top-0"
            style={{
              left: sideWidth + COL_GAP,
              width: centerWidth,
              height: TOTAL_H,
            }}
          >
            <TrophyCenter slot={finalSlot} inView={inView} />
          </div>

          {/* RIGHT side columns — order reversed so R32 is far right */}
          {SIDE_COLS.map((round, colIdx) => {
            const slots = right[round];
            const xFromRight = colIdx * (COL_WIDTH + COL_GAP);
            const x = totalWidth - COL_WIDTH - xFromRight;
            return (
              <div
                key={`R-${round}`}
                className="absolute top-0"
                style={{ left: x, width: COL_WIDTH, height: TOTAL_H }}
              >
                <RoundLabel round={round} side="right" />
                {slots.map((slot) => {
                  const tokens = slot.round === "R32" ? tokensBySlotId.get(slot.id) : undefined;
                  const stateA = tokens ? slotStates.get(tokens[0]) : undefined;
                  const stateB = tokens ? slotStates.get(tokens[1]) : undefined;
                  return (
                    <SlotCard
                      key={slot.id}
                      slot={slot}
                      side="right"
                      inView={inView}
                      hoveredTeam={hovered?.team ?? null}
                      onHover={(team) => {
                        if (!team) return setHovered(null);
                        const r32Idx = findR32Idx(right, team);
                        if (r32Idx >= 0) setHovered({ team, r32Idx, side: "right" });
                      }}
                      inPath={pathIds.has(slot.id)}
                      teamAStatus={stateA?.status}
                      teamBStatus={stateB?.status}
                    />
                  );
                })}
              </div>
            );
          })}
        </div>
      </motion.div>
    </section>
  );
}

function splitSide(tree: Record<RoundKey, Slot[]>, side: "left" | "right"): Record<RoundKey, Slot[]> {
  const out: Record<RoundKey, Slot[]> = { R32: [], R16: [], QF: [], SF: [], FINAL: [] };
  for (const round of ["R32", "R16", "QF", "SF"] as RoundKey[]) {
    const all = tree[round];
    const half = all.length / 2;
    const slice = side === "left" ? all.slice(0, half) : all.slice(half);
    // Re-id with side-relative idx so position math + path highlight ids match.
    // We namespace by side to keep ids unique across the two halves.
    const prefix = side === "left" ? "L" : "R";
    out[round] = slice.map((s, i) => ({ ...s, idx: i, id: `${prefix}-${round}-${i}` }));
  }
  return out;
}

function findR32Idx(side: Record<RoundKey, Slot[]>, team: string): number {
  const arr = side.R32;
  return arr.findIndex((s) => s.teams.includes(team));
}

function RoundLabel({ round, side }: { round: RoundKey; side: "left" | "right" }) {
  return (
    <div
      className={`absolute -top-7 ${side === "left" ? "left-0" : "right-0"} text-[10px] font-display font-bold uppercase tracking-[0.18em] text-[var(--ink-muted)]`}
    >
      {ROUND_LABEL[round]}
    </div>
  );
}

// =====================================================================
//                              SLOT CARD
// =====================================================================

function SlotCard({
  slot,
  side,
  inView,
  hoveredTeam,
  onHover,
  inPath,
  teamAStatus,
  teamBStatus,
}: {
  slot: Slot;
  side: "left" | "right";
  inView: boolean;
  hoveredTeam: string | null;
  onHover: (team: string | null) => void;
  inPath: boolean;
  /** Per-team status from bracketSlotStates. R32 only — R16+ stays undefined. */
  teamAStatus?: "confirmed" | "projected";
  teamBStatus?: "confirmed" | "projected";
}) {
  const y = slotY(slot.round, slot.idx);
  const top = y - CARD_H / 2;

  // Round-stagger delay (R32 first, then R16, etc).
  const roundOrder: Record<RoundKey, number> = { R32: 0, R16: 1, QF: 2, SF: 3, FINAL: 4 };
  const delay = 0.15 + roundOrder[slot.round] * 0.12 + slot.idx * 0.015;

  // R32 cards now show a tri-state badge instead of a binary one:
  //   2/2 → both teams locked (green mint badge)
  //   1/2 → one team locked (amber badge, hints "half-decided")
  //   0/2 → still projected (muted)
  // Downstream rounds (R16+) still fall back to the parent's `confirmed` field
  // since per-team status doesn't make sense there yet.
  const isR32 = slot.round === "R32";
  const confirmedCount = isR32
    ? (teamAStatus === "confirmed" ? 1 : 0) + (teamBStatus === "confirmed" ? 1 : 0)
    : slot.confirmed ? 2 : 0;
  const fullyConfirmed = confirmedCount === 2;
  const halfConfirmed = confirmedCount === 1;
  const badgeStyle = fullyConfirmed
    ? { background: "var(--accent-mint, #14F195)", color: "white" }
    : halfConfirmed
      ? { background: "rgba(251,191,36,0.95)", color: "white" }
      : { background: "var(--bg-tint)", color: "var(--ink-muted)" };
  const badgeLabel = fullyConfirmed
    ? "Confirmado"
    : halfConfirmed
      ? "1/2 Conf."
      : "Proyectado";

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.85, x: side === "left" ? -8 : 8 }}
      animate={inView ? { opacity: 1, scale: 1, x: 0 } : {}}
      transition={{ duration: 0.45, delay, ease: [0.22, 1, 0.36, 1] }}
      className="absolute"
      style={{ top, left: 0, width: COL_WIDTH, height: CARD_H }}
    >
      <div
        className={`relative glass rounded-xl h-full px-2 py-1.5 flex flex-col justify-center gap-0.5 transition-all duration-300 ${
          inPath ? "ring-2 ring-[var(--accent-violet)]" : ""
        } ${fullyConfirmed ? "ring-1 ring-[var(--accent-mint,#14F195)]" : halfConfirmed ? "ring-1 ring-amber-400" : ""}`}
        style={
          inPath
            ? { boxShadow: "0 0 18px -4px var(--accent-violet)" }
            : fullyConfirmed
              ? { boxShadow: "0 0 14px -4px rgba(20,241,149,0.55)" }
              : halfConfirmed
                ? { boxShadow: "0 0 12px -4px rgba(251,191,36,0.55)" }
                : undefined
        }
      >
        <div className={`absolute ${side === "right" ? "left-1.5" : "right-1.5"} top-0.5 text-[8px] font-display font-bold uppercase tracking-wider px-1 py-px rounded`}
          style={badgeStyle}
        >
          {badgeLabel}
        </div>
        <TeamChip
          code={slot.teams[0]}
          dim={hoveredTeam !== null && hoveredTeam !== slot.teams[0]}
          highlight={hoveredTeam === slot.teams[0]}
          onEnter={() => onHover(slot.teams[0])}
          onLeave={() => onHover(null)}
          isWinner={slot.winner === slot.teams[0]}
          resolved={teamAStatus === "confirmed"}
          status={teamAStatus}
          side={side}
        />
        <TeamChip
          code={slot.teams[1]}
          dim={hoveredTeam !== null && hoveredTeam !== slot.teams[1]}
          highlight={hoveredTeam === slot.teams[1]}
          onEnter={() => onHover(slot.teams[1])}
          onLeave={() => onHover(null)}
          isWinner={slot.winner === slot.teams[1]}
          resolved={teamBStatus === "confirmed"}
          status={teamBStatus}
          side={side}
        />
      </div>
    </motion.div>
  );
}

function TeamChip({
  code,
  dim,
  highlight,
  onEnter,
  onLeave,
  isWinner,
  resolved,
  status,
  side,
}: {
  code: string;
  dim: boolean;
  highlight: boolean;
  onEnter: () => void;
  onLeave: () => void;
  isWinner: boolean;
  resolved: boolean;
  /** Per-team status — undefined for downstream rounds. */
  status?: "confirmed" | "projected";
  side: "left" | "right";
}) {
  const team = code ? getTeam(code) : null;
  const router = useRouter();

  if (!team) {
    return (
      <div className={`flex items-center gap-1.5 px-1 py-0.5 rounded-md text-[10px] text-[var(--ink-muted)] ${side === "right" ? "flex-row-reverse text-right" : ""}`}>
        <span className="w-5 h-5 rounded grid place-items-center bg-[var(--bg-tint)] font-display font-bold">?</span>
        <span className="font-display font-bold opacity-70">Por definir</span>
      </div>
    );
  }

  return (
    <button
      type="button"
      onMouseEnter={onEnter}
      onMouseLeave={onLeave}
      onFocus={onEnter}
      onBlur={onLeave}
      className={`group flex items-center gap-1.5 px-1 py-0.5 rounded-md transition-all cursor-pointer ${side === "right" ? "flex-row-reverse text-right" : ""} ${
        dim ? "opacity-40" : "opacity-100"
      }`}
      style={{
        background: highlight ? "rgba(94,91,255,0.12)" : "transparent",
      }}
    >
      <span
        className={`relative w-5 h-5 rounded overflow-hidden ring-1 transition-transform duration-300 group-hover:scale-110 ${
          isWinner ? "ring-[var(--accent-gold)]" : "ring-[var(--line)]"
        } ${resolved ? "pulse-gold" : ""} cursor-pointer`}
        onClick={(e) => { e.stopPropagation(); router.push(`/equipos/${team.code}`); }}
        title={`Ver ${team.name}`}
      >
        <Image src={flagUrl(team.iso2, 32)} alt={team.name} fill sizes="20px" className="object-cover" unoptimized />
      </span>
      <span className={`font-display font-bold text-[11px] leading-none ${isWinner ? "text-[var(--ink)]" : "text-[var(--ink-soft)]"}`}>
        {team.code}
      </span>
      {/* Per-team status dot: green = source group closed, amber = still projected.
          Sits next to the team code so each side of the slot communicates its
          own state — critical because most R32 cards include a 3rd-place token
          whose group can't be confirmed until ALL 12 groups close. */}
      {status && (
        <span
          className="ml-auto w-1.5 h-1.5 rounded-full shrink-0"
          style={{
            background: status === "confirmed" ? "rgb(20,148,90)" : "rgb(202,138,4)",
            boxShadow: status === "confirmed"
              ? "0 0 0 2px rgba(20,148,90,0.18)"
              : "0 0 0 2px rgba(202,138,4,0.18)",
          }}
          title={status === "confirmed" ? "Equipo confirmado" : "Equipo en proyección"}
        />
      )}
      {isWinner && <span className="text-[8px] text-[var(--accent-gold)] font-bold uppercase tracking-wider">✓</span>}

      <style jsx>{`
        @keyframes pulseGold {
          0%, 100% { box-shadow: 0 0 0 0 rgba(212, 175, 55, 0); }
          50%      { box-shadow: 0 0 0 4px rgba(212, 175, 55, 0.55); }
        }
        .pulse-gold {
          animation: pulseGold 2.4s ease-in-out infinite;
        }
      `}</style>
    </button>
  );
}

// =====================================================================
//                          TROPHY CENTER
// =====================================================================

function TrophyCenter({ slot, inView }: { slot: Slot | undefined; inView: boolean }) {
  const finalY = TOTAL_H / 2 - 110;

  return (
    <div className="absolute left-0 right-0 flex flex-col items-center" style={{ top: finalY }}>
      <motion.div
        initial={{ opacity: 0, scale: 0.6 }}
        animate={inView ? { opacity: 1, scale: 1 } : {}}
        transition={{ duration: 0.9, delay: 0.4, ease: [0.22, 1, 0.36, 1] }}
        className="relative grid place-items-center"
      >
        {/* Halo */}
        <div className="absolute inset-0 rounded-full blur-3xl trophy-halo" />
        {/* Trophy disc */}
        <div className="trophy-disc relative w-32 h-32 rounded-full grid place-items-center overflow-hidden">
          <div className="absolute inset-0 trophy-shimmer" />
          <Trophy size={48} className="relative text-white drop-shadow-md" />
        </div>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 8 }}
        animate={inView ? { opacity: 1, y: 0 } : {}}
        transition={{ duration: 0.6, delay: 0.7 }}
        className="mt-4 text-center"
      >
        <div className="font-display text-[10px] uppercase tracking-[0.28em] text-[var(--ink-muted)]">Copa Mundial</div>
        <div className="font-display text-xl font-bold leading-none mt-1">2026</div>
      </motion.div>

      {/* Final card */}
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={inView ? { opacity: 1, y: 0 } : {}}
        transition={{ duration: 0.5, delay: 0.95 }}
        className="mt-5 w-full glass-strong rounded-2xl p-3"
      >
        <div className="text-[10px] uppercase tracking-[0.18em] text-[var(--ink-muted)] mb-2 text-center">
          Gran Final
        </div>
        <div className="flex items-center justify-between gap-2">
          <FinalTeamSide code={slot?.teams[0] ?? ""} />
          <div className="font-display text-lg text-[var(--ink-muted)] font-bold">vs</div>
          <FinalTeamSide code={slot?.teams[1] ?? ""} right />
        </div>
      </motion.div>

      <style jsx>{`
        .trophy-disc {
          background: conic-gradient(from 0deg, #d4af37, #fde68a, #d4af37, #b8860b, #d4af37);
          box-shadow:
            0 0 0 4px rgba(255, 255, 255, 0.8),
            0 18px 40px -10px rgba(212, 175, 55, 0.55),
            inset 0 0 24px rgba(255, 255, 255, 0.25);
          animation: trophySpin 16s linear infinite;
        }
        @keyframes trophySpin {
          to { transform: rotate(360deg); }
        }
        .trophy-shimmer {
          background: linear-gradient(120deg, transparent 30%, rgba(255, 255, 255, 0.55) 50%, transparent 70%);
          background-size: 200% 200%;
          animation: shimmerSlide 3.6s ease-in-out infinite;
        }
        @keyframes shimmerSlide {
          0% { background-position: -100% -100%; }
          100% { background-position: 200% 200%; }
        }
        .trophy-halo {
          background: radial-gradient(circle, rgba(212, 175, 55, 0.4) 0%, transparent 65%);
          animation: haloPulse 4s ease-in-out infinite;
        }
        @keyframes haloPulse {
          0%, 100% { opacity: 0.4; transform: scale(1); }
          50%      { opacity: 0.7; transform: scale(1.15); }
        }
      `}</style>
    </div>
  );
}

function FinalTeamSide({ code, right }: { code: string; right?: boolean }) {
  const team = code ? getTeam(code) : null;
  if (!team) {
    return (
      <div className={`flex items-center gap-1.5 ${right ? "flex-row-reverse" : ""}`}>
        <div className="w-6 h-6 rounded-md bg-[var(--bg-tint)] grid place-items-center text-[var(--ink-muted)] text-[10px] font-display font-bold">?</div>
        <span className="font-display text-[10px] font-bold text-[var(--ink-muted)] uppercase tracking-wider">TBD</span>
      </div>
    );
  }
  return (
    <div className={`flex items-center gap-1.5 ${right ? "flex-row-reverse" : ""}`}>
      <div className="relative w-6 h-6 rounded-md overflow-hidden ring-1 ring-[var(--line)]">
        <Image src={flagUrl(team.iso2, 32)} alt={team.name} fill sizes="24px" className="object-cover" unoptimized />
      </div>
      <span className="font-display text-xs font-bold">{team.code}</span>
    </div>
  );
}

// =====================================================================
//                            CONNECTORS
// =====================================================================

// Renders the SVG curve network that joins each pair of feeders into its
// downstream match. Animates a stroke-dash draw-in.
function renderConnectors({
  left,
  right,
  sideWidth,
  centerWidth,
  colGap,
  totalWidth,
  hoveredTeam,
  hoveredPath,
}: {
  left: Record<RoundKey, Slot[]>;
  right: Record<RoundKey, Slot[]>;
  sideWidth: number;
  centerWidth: number;
  colGap: number;
  totalWidth: number;
  hoveredTeam: string | null;
  hoveredPath: Set<string>;
}) {
  const paths: React.ReactElement[] = [];

  // Helper to draw a path between (x1,y1) and (x2,y2) with a midpoint elbow.
  function elbow(x1: number, y1: number, x2: number, y2: number) {
    const midX = (x1 + x2) / 2;
    return `M ${x1} ${y1} L ${midX} ${y1} L ${midX} ${y2} L ${x2} ${y2}`;
  }

  function pushSide(side: "left" | "right", slotsByRound: Record<RoundKey, Slot[]>) {
    const order: RoundKey[] = ["R32", "R16", "QF", "SF"];
    for (let r = 0; r < order.length - 1; r++) {
      const from = order[r];
      const to = order[r + 1];
      const feeders = slotsByRound[from];
      const targets = slotsByRound[to];
      for (let i = 0; i < feeders.length; i++) {
        const feeder = feeders[i];
        const target = targets[Math.floor(i / 2)];
        if (!target) continue;
        const colIdxFrom = order.indexOf(from);
        const colIdxTo = order.indexOf(to);
        let x1: number, x2: number;
        if (side === "left") {
          x1 = colIdxFrom * (COL_WIDTH + colGap) + COL_WIDTH; // right edge of feeder col
          x2 = colIdxTo * (COL_WIDTH + colGap); // left edge of target col
        } else {
          // Right side mirrors.
          x1 = totalWidth - (colIdxFrom * (COL_WIDTH + colGap)) - COL_WIDTH; // left edge of feeder col
          x2 = totalWidth - (colIdxTo * (COL_WIDTH + colGap));  // right edge of target col
        }
        const y1 = slotY(from, feeder.idx);
        const y2 = slotY(to, target.idx);

        const onPath = hoveredPath.has(feeder.id) && hoveredPath.has(target.id);
        paths.push(
          <ConnectorPath
            key={`${side}-${from}-${i}`}
            d={elbow(x1, y1, x2, y2)}
            highlight={onPath}
            staggerDelay={0.4 + r * 0.18 + i * 0.025}
          />
        );
      }
    }

    // Last hop: SF -> Final (single center slot).
    const sf = slotsByRound.SF[0];
    if (sf) {
      const colIdxFrom = order.indexOf("SF");
      let x1: number;
      if (side === "left") {
        x1 = colIdxFrom * (COL_WIDTH + colGap) + COL_WIDTH;
      } else {
        x1 = totalWidth - (colIdxFrom * (COL_WIDTH + colGap)) - COL_WIDTH;
      }
      const y1 = slotY("SF", sf.idx);
      // Final card centered horizontally in the center column.
      const cx = sideWidth + colGap + centerWidth / 2;
      const cy = TOTAL_H / 2 + 90; // align with the final card under the trophy
      const onPath = hoveredPath.has(sf.id);
      paths.push(
        <ConnectorPath
          key={`${side}-final`}
          d={elbow(x1, y1, cx, cy)}
          highlight={onPath}
          staggerDelay={0.95}
        />
      );
    }
  }

  pushSide("left", left);
  pushSide("right", right);

  return <g>{paths}</g>;
}

function ConnectorPath({ d, highlight, staggerDelay }: { d: string; highlight: boolean; staggerDelay: number }) {
  return (
    <motion.path
      d={d}
      fill="none"
      stroke={highlight ? "var(--accent-violet)" : "rgba(10,10,10,0.18)"}
      strokeWidth={highlight ? 2.4 : 1.4}
      strokeLinecap="round"
      strokeLinejoin="round"
      filter={highlight ? "url(#bracket-glow)" : undefined}
      initial={{ pathLength: 0, opacity: 0 }}
      animate={{ pathLength: 1, opacity: 1 }}
      transition={{
        pathLength: { duration: 0.9, delay: staggerDelay, ease: [0.22, 1, 0.36, 1] },
        opacity: { duration: 0.3, delay: staggerDelay },
      }}
    />
  );
}

// =====================================================================
//                           MOBILE BRACKET
// =====================================================================
//
// On phones we ditch the symmetric tree (too narrow at 375-414px) and show
// a sticky round-tab nav at the top + a vertical stack of match cards for the
// selected round. Each card shows date, kickoff (CDMX), stadium, both teams.
//
// R32 cards resolve their teams live from `computeR32Pairings`. When a feeder
// group hasn't closed, the slot falls back to its template token rendered as
// Spanish ("1° Grupo A · pendiente"). R16+ rows stay as `?` because we don't
// yet wire knockout results into the data model — but the venue/date/time
// still tells the user when the match happens.

type MobileRoundKey = "R32" | "R16" | "QF" | "SF" | "TF"; // TF = Tercer puesto + Final pair

const VENUE_BY_CITY: Map<string, (typeof VENUES)[number]> = new Map(VENUES.map(v => [v.city, v]));

// Spanish slot label for an R32 template token.
//   "1A"   → "1° Grupo A"
//   "2C"   → "2° Grupo C"
//   "3rd5" → "Mejor 3° (#5)"
function slotLabel(token: string, t: (key: string, fallback?: string) => string): string {
  if (token.startsWith("3rd")) {
    const n = parseInt(token.slice(3), 10);
    return t("bracket.slot.best3rd", `Mejor 3° (#${n})`).replace("{n}", String(n));
  }
  const pos = token[0];
  const letter = token.slice(1);
  if (pos === "1") return t("bracket.slot.first", `1° Grupo ${letter}`).replace("{g}", letter);
  if (pos === "2") return t("bracket.slot.second", `2° Grupo ${letter}`).replace("{g}", letter);
  return token;
}

function formatKickoff(dateISO: string, locale: ReturnType<typeof useLocale>["locale"]): string {
  const d = new Date(dateISO);
  const fmt = new Intl.DateTimeFormat(intlLocale(locale), {
    weekday: "short",
    day: "numeric",
    month: "short",
    hour: "numeric",
    minute: "2-digit",
    timeZone: "America/Mexico_City",
  });
  // "lun 29 jun, 12:00" — the comma style varies by Intl impl; we just trust it.
  return fmt.format(d).replace(/\.,/g, ",");
}

type LiveStatus = "played" | "live" | "upcoming";

function countdownParts(dateISO: string, now: number | null): { d: number; h: number; m: number } | null {
  if (!now) return null;
  const diff = new Date(dateISO).getTime() - now;
  if (diff <= 0) return null;
  const d = Math.floor(diff / 86_400_000);
  const h = Math.floor((diff % 86_400_000) / 3_600_000);
  const m = Math.floor((diff % 3_600_000) / 60_000);
  return { d, h, m };
}

function countdownLabel(dateISO: string, now: number | null): string | null {
  const p = countdownParts(dateISO, now);
  if (!p) return null;
  if (p.d > 0) return `${p.d}d ${p.h}h`;
  if (p.h > 0) return `${p.h}h ${p.m}m`;
  return `${p.m}m`;
}

function formatCDMXTime(dateISO: string): string {
  return new Intl.DateTimeFormat("es-MX", {
    hour: "numeric",
    minute: "2-digit",
    timeZone: "America/Mexico_City",
  }).format(new Date(dateISO));
}

function formatCDMXDate(dateISO: string): string {
  return new Intl.DateTimeFormat("es-MX", {
    weekday: "short",
    day: "numeric",
    month: "short",
    timeZone: "America/Mexico_City",
  }).format(new Date(dateISO));
}

function formatETTime(dateISO: string): string {
  return new Intl.DateTimeFormat("en-US", {
    hour: "numeric",
    minute: "2-digit",
    timeZone: "America/New_York",
  }).format(new Date(dateISO));
}

function formatETDate(dateISO: string): string {
  return new Intl.DateTimeFormat("en-US", {
    weekday: "short",
    day: "numeric",
    month: "short",
    timeZone: "America/New_York",
  }).format(new Date(dateISO));
}

function formatET(dateISO: string): string {
  return new Intl.DateTimeFormat("en-US", {
    hour: "numeric",
    minute: "2-digit",
    timeZone: "America/New_York",
    timeZoneName: "short",
  }).format(new Date(dateISO));
}

function liveStatusFor(dateISO: string, now: number | null): LiveStatus {
  if (now === null) return "upcoming";
  const start = new Date(dateISO).getTime();
  if (Number.isNaN(start)) return "upcoming";
  // Treat a KO match as "EN VIVO" from kickoff to kickoff+150min (covers
  // ET + pens). After that it counts as played.
  const liveEnd = start + 150 * 60_000;
  if (now < start) return "upcoming";
  if (now <= liveEnd) return "live";
  return "played";
}

// Official FIFA 2026 R16 pairings: each entry is [R32-slotA, R32-slotB].
const R16_PAIRINGS_BR: Array<[number, number]> = [
  [1, 3], [2, 5], [4, 6], [7, 8], [11, 12], [9, 10], [15, 16], [13, 14],
];

function MobileBracket({ tree, real }: { tree: Record<RoundKey, Slot[]>; real: RealResults }) {
  const [active, setActive] = useState<MobileRoundKey>("R32");
  const { locale, t } = useLocale();
  const now = useNow(30_000);
  const slotStates = useMemo(() => slotStateMap(real), [real]);
  const thirdRanking = useMemo(() => computeThirdPlaceRanking(EMPTY_PICKS, real), [real]);
  const thirdSlotProbs = useMemo(() => simulateThirdSlotProbabilities(real), [real]);

  const { currentPlayer } = usePlayer();
  const [r32Picks, setR32Picks] = useState<string[]>(() => {
    if (typeof window === "undefined" || !currentPlayer) return Array(16).fill("");
    return loadPredictions(currentPlayer.id).bracket?.R32 ?? Array(16).fill("");
  });

  useEffect(() => {
    if (!currentPlayer) return;
    setR32Picks(loadPredictions(currentPlayer.id).bracket?.R32 ?? Array(16).fill(""));
  }, [currentPlayer]);

  // Re-sync picks from localStorage whenever hydration or SSE stream writes it.
  useEffect(() => {
    if (!currentPlayer) return;
    const refresh = () => {
      setR32Picks(loadPredictions(currentPlayer.id).bracket?.R32 ?? Array(16).fill(""));
    };
    window.addEventListener("q26:predictions-updated", refresh);
    return () => window.removeEventListener("q26:predictions-updated", refresh);
  }, [currentPlayer]);

  // KO results: winners from ESPN for all completed KO matches.
  const [slotResults, setSlotResults] = useState<Record<string, string>>({});
  useEffect(() => {
    fetch("/api/bracket/ko-results")
      .then(r => r.json())
      .then((d: { ok: boolean; slotResults?: Record<string, string> }) => {
        if (d.ok && d.slotResults) setSlotResults(d.slotResults);
      })
      .catch(() => {});
  }, []);

  // R16 / QF / SF / FINAL picks — share the same localStorage key as KnockoutSection.
  const currentPlayerId = currentPlayer?.id ?? null;
  const [r16Picks, setR16Picks] = useState<string[]>(() => Array(8).fill(""));
  const [qfPicks, setQfPicks] = useState<string[]>(() => Array(4).fill(""));
  const [sfPicks, setSfPicks] = useState<string[]>(() => Array(2).fill(""));
  const [finalPick, setFinalPick] = useState<string>("");

  useEffect(() => {
    if (!currentPlayerId) return;
    const p = loadPredictions(currentPlayerId);
    setR16Picks((p.bracket?.R16 as string[] | undefined) ?? Array(8).fill(""));
    setQfPicks((p.bracket?.QF as string[] | undefined) ?? Array(4).fill(""));
    setSfPicks((p.bracket?.SF as string[] | undefined) ?? Array(2).fill(""));
    setFinalPick(typeof p.bracket?.FINAL === "string" ? p.bracket.FINAL : "");
  }, [currentPlayerId]);

  useEffect(() => {
    if (!currentPlayerId) return;
    const refresh = () => {
      const p = loadPredictions(currentPlayerId);
      setR16Picks((p.bracket?.R16 as string[] | undefined) ?? Array(8).fill(""));
      setQfPicks((p.bracket?.QF as string[] | undefined) ?? Array(4).fill(""));
      setSfPicks((p.bracket?.SF as string[] | undefined) ?? Array(2).fill(""));
      setFinalPick(typeof p.bracket?.FINAL === "string" ? p.bracket.FINAL : "");
    };
    window.addEventListener("q26:predictions-updated", refresh);
    return () => window.removeEventListener("q26:predictions-updated", refresh);
  }, [currentPlayerId]);

  const handlePickWinner = useCallback((slotIdx: number, code: string) => {
    if (!currentPlayer) return;
    if (isKOSlotLocked(`R32-${slotIdx + 1}`)) return;
    setR32Picks(prev => {
      const next = [...prev];
      next[slotIdx] = next[slotIdx] === code ? "" : code;
      const pred = loadPredictions(currentPlayer.id);
      pred.bracket = { ...(pred.bracket ?? {}), R32: next };
      savePredictions(pred);
      return next;
    });
  }, [currentPlayer]);

  const [aiPickState, setAiPickState] = useState<"idle" | "loading" | "done">("idle");
  const [aiPickMsg, setAiPickMsg] = useState("");

  const handleAiAutoPick = useCallback(async () => {
    if (!currentPlayer || aiPickState === "loading") return;
    // Collect unlocked R32 slots where both teams are known
    const r32Cards = tree.R32.map((slot, i) => ({
      slot: `R32-${i + 1}`,
      idx: i,
      teamA: slot.teams[0] || null,
      teamB: slot.teams[1] || null,
    })).filter(c => c.teamA && c.teamB && !isKOSlotLocked(c.slot));

    if (r32Cards.length === 0) return;

    setAiPickState("loading");
    setAiPickMsg("");
    try {
      const slots = r32Cards.map(c => {
        const p = matchProbability(c.teamA!, c.teamB!);
        const total = p.H + p.A;
        const h = Math.round(p.H / total * 100);
        return { slot: c.slot, teamA: c.teamA!, teamB: c.teamB!, hPct: h, aPct: 100 - h };
      });

      const res = await fetch("/api/bracket/ai-picks", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ slots }),
      });
      const data = await res.json() as { ok: boolean; picks?: Array<{ slot: string; pick: string; reason: string }> };

      if (!data.ok || !data.picks?.length) throw new Error("no picks");

      setR32Picks(prev => {
        const next = [...prev];
        for (const p of data.picks!) {
          const slotNum = parseInt(p.slot.replace("R32-", ""), 10);
          if (slotNum >= 1 && slotNum <= 16 && !isKOSlotLocked(p.slot)) {
            next[slotNum - 1] = p.pick;
          }
        }
        const pred = loadPredictions(currentPlayer.id);
        pred.bracket = { ...(pred.bracket ?? {}), R32: next };
        savePredictions(pred);
        return next;
      });

      setAiPickMsg(`✨ IA eligió ${data.picks.length} ganador${data.picks.length !== 1 ? "es" : ""}`);
      setAiPickState("done");
      setTimeout(() => setAiPickState("idle"), 4000);
    } catch {
      setAiPickMsg("Error al consultar IA");
      setAiPickState("done");
      setTimeout(() => setAiPickState("idle"), 3000);
    }
  }, [currentPlayer, tree.R32, aiPickState]);

  const handlePickR16 = useCallback((idx: number, code: string) => {
    if (!currentPlayer || isKOSlotLocked(`R16-${idx + 1}`)) return;
    setR16Picks(prev => {
      const next = [...prev];
      if (next[idx] === code) return prev;
      next[idx] = code;
      const pred = loadPredictions(currentPlayer.id);
      pred.bracket = { ...(pred.bracket ?? {}), R16: next };
      savePredictions(pred);
      return next;
    });
  }, [currentPlayer]);

  const handlePickQF = useCallback((idx: number, code: string) => {
    if (!currentPlayer || isKOSlotLocked(`QF-${idx + 1}`)) return;
    setQfPicks(prev => {
      const next = [...prev];
      if (next[idx] === code) return prev;
      next[idx] = code;
      const pred = loadPredictions(currentPlayer.id);
      pred.bracket = { ...(pred.bracket ?? {}), QF: next };
      savePredictions(pred);
      return next;
    });
  }, [currentPlayer]);

  const handlePickSF = useCallback((idx: number, code: string) => {
    if (!currentPlayer || isKOSlotLocked(`SF-${idx + 1}`)) return;
    setSfPicks(prev => {
      const next = [...prev];
      if (next[idx] === code) return prev;
      next[idx] = code;
      const pred = loadPredictions(currentPlayer.id);
      pred.bracket = { ...(pred.bracket ?? {}), SF: next };
      savePredictions(pred);
      return next;
    });
  }, [currentPlayer]);

  const handlePickFinal = useCallback((code: string) => {
    if (!currentPlayer || isKOSlotLocked("FINAL")) return;
    const pred = loadPredictions(currentPlayer.id);
    if ((pred.bracket?.FINAL as string | undefined) === code) return;
    pred.bracket = { ...(pred.bracket ?? {}), FINAL: code };
    savePredictions(pred);
    setFinalPick(code);
  }, [currentPlayer]);

  const tabs: Array<{ key: MobileRoundKey; label: string; count: number }> = [
    { key: "R32", label: t("bracket.round.r32", "Dieciseisavos"), count: 16 },
    { key: "R16", label: t("bracket.round.r16", "Octavos"),        count: 8 },
    { key: "QF",  label: t("bracket.round.qf",  "Cuartos"),        count: 4 },
    { key: "SF",  label: t("bracket.round.sf",  "Semis"),          count: 2 },
    { key: "TF",  label: `${t("bracket.round.third", "3er lugar")} · ${t("bracket.round.final", "Final")}`, count: 2 },
  ];

  // Match cards to render for the active tab.
  const cards = useMemo<MobileCard[]>(() => {
    if (active === "R32") {
      return tree.R32.map((slot, i) => {
        const token = R32_TEMPLATE[i] ?? ["", ""];
        const ko = findKOMatch(`R32-${i + 1}`);
        return {
          slot: `R32-${i + 1}`,
          round: "R32",
          ko,
          teamA: slot.teams[0] || null,
          teamB: slot.teams[1] || null,
          slotTokenA: token[0],
          slotTokenB: token[1],
          confirmed: slot.confirmed,
        };
      });
    }
    if (active === "R16") {
      return Array.from({ length: 8 }, (_, i) => {
        const [a, b] = R16_PAIRINGS_BR[i] ?? [0, 0];
        const teamA = slotResults[`R32-${a}`] || null;
        const teamB = slotResults[`R32-${b}`] || null;
        return {
          slot: `R16-${i + 1}`,
          round: "R16",
          ko: findKOMatch(`R16-${i + 1}`),
          teamA, teamB,
          slotTokenA: "", slotTokenB: "",
          confirmed: !!(teamA && teamB),
        };
      });
    }
    if (active === "QF") {
      return Array.from({ length: 4 }, (_, i) => {
        const teamA = slotResults[`R16-${i * 2 + 1}`] || null;
        const teamB = slotResults[`R16-${i * 2 + 2}`] || null;
        return {
          slot: `QF-${i + 1}`,
          round: "QF",
          ko: findKOMatch(`QF-${i + 1}`),
          teamA, teamB,
          slotTokenA: "", slotTokenB: "",
          confirmed: !!(teamA && teamB),
        };
      });
    }
    if (active === "SF") {
      return Array.from({ length: 2 }, (_, i) => {
        const teamA = slotResults[`QF-${i * 2 + 1}`] || null;
        const teamB = slotResults[`QF-${i * 2 + 2}`] || null;
        return {
          slot: `SF-${i + 1}`,
          round: "SF",
          ko: findKOMatch(`SF-${i + 1}`),
          teamA, teamB,
          slotTokenA: "", slotTokenB: "",
          confirmed: !!(teamA && teamB),
        };
      });
    }
    // TF: 3rd place + Final
    return [
      {
        slot: "THIRD", round: "THIRD",
        ko: findKOMatch("THIRD"),
        teamA: null, teamB: null,
        slotTokenA: "", slotTokenB: "",
        confirmed: false,
      },
      {
        slot: "FINAL", round: "FINAL",
        ko: findKOMatch("FINAL"),
        teamA: slotResults["SF-1"] || null,
        teamB: slotResults["SF-2"] || null,
        slotTokenA: "", slotTokenB: "",
        confirmed: !!(slotResults["SF-1"] && slotResults["SF-2"]),
      },
    ];
  }, [active, tree, slotResults]);

  return (
    <section className="container-app pt-2 pb-6">
      {/* Sticky round-tab pill bar — sits under the existing site header. */}
      <div className="sticky top-[56px] z-20 -mx-3 px-3 pt-1 pb-2 bg-[var(--bg)]/85 backdrop-blur supports-[backdrop-filter]:bg-[var(--bg)]/60">
        <div className="glass-strong rounded-full p-1 flex gap-1 overflow-x-auto no-scrollbar">
          {tabs.map((tab) => {
            const isActive = active === tab.key;
            return (
              <button
                key={tab.key}
                type="button"
                onClick={() => setActive(tab.key)}
                className={`shrink-0 px-3 py-1.5 rounded-full text-xs font-display font-bold transition-colors ${
                  isActive ? "bg-[var(--ink)] text-white" : "text-[var(--ink-soft)] hover:text-[var(--ink)]"
                }`}
              >
                {tab.label}
                <span className="ml-1 text-[9px] opacity-70 tabular-nums">{tab.count}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* ── AI AUTO-PICK BUTTON (R32 only, logged in) ── */}
      {active === "R32" && currentPlayer && (
        <div className="mt-2 flex items-center gap-2">
          <button
            type="button"
            onClick={handleAiAutoPick}
            disabled={aiPickState === "loading"}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-full text-[11px] font-display font-bold transition-all"
            style={{
              background: aiPickState === "loading"
                ? "rgba(94,91,255,0.12)"
                : "linear-gradient(135deg, rgba(94,91,255,0.18), rgba(20,241,149,0.15))",
              color: "var(--ink)",
              boxShadow: "0 0 0 1px rgba(94,91,255,0.25)",
              opacity: aiPickState === "loading" ? 0.7 : 1,
            }}
          >
            {aiPickState === "loading" ? (
              <>
                <span className="inline-block w-3 h-3 border-2 border-[rgba(94,91,255,0.5)] border-t-[rgba(94,91,255,1)] rounded-full animate-spin" />
                Pensando…
              </>
            ) : (
              <>
                <span>🤖</span>
                Auto-pick con IA
              </>
            )}
          </button>
          {aiPickMsg && (
            <span className="text-[10px] font-display font-bold" style={{ color: "rgb(10,150,90)" }}>
              {aiPickMsg}
            </span>
          )}
        </div>
      )}

      <AnimatePresence mode="wait">
        <motion.div
          key={active}
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -8 }}
          transition={{ duration: 0.25 }}
          className="mt-3 flex flex-col gap-3"
        >
          {cards.map((card, i) => {
            const slotIdx = card.round === "R32" ? i : -1;
            const slotLocked = isKOSlotLocked(card.slot);
            let bracketPick = "";
            let pickHandler: ((code: string) => void) | undefined;
            if (card.round === "R32" && slotIdx >= 0) {
              bracketPick = r32Picks[slotIdx] ?? "";
              if (!slotLocked && currentPlayer) pickHandler = (code) => handlePickWinner(slotIdx, code);
            } else if (card.round === "R16") {
              bracketPick = r16Picks[i] ?? "";
              if (!slotLocked && currentPlayer) pickHandler = (code) => handlePickR16(i, code);
            } else if (card.round === "QF") {
              bracketPick = qfPicks[i] ?? "";
              if (!slotLocked && currentPlayer) pickHandler = (code) => handlePickQF(i, code);
            } else if (card.round === "SF") {
              bracketPick = sfPicks[i] ?? "";
              if (!slotLocked && currentPlayer) pickHandler = (code) => handlePickSF(i, code);
            } else if (card.slot === "FINAL") {
              bracketPick = finalPick;
              if (!slotLocked && currentPlayer) pickHandler = handlePickFinal;
            }
            return (
              <MobileMatchCard
                key={card.slot}
                card={card}
                index={i + 1}
                now={now}
                locale={locale}
                t={t}
                slotStates={slotStates}
                thirdRanking={thirdRanking}
                thirdSlotProbs={thirdSlotProbs}
                bracketPick={bracketPick}
                onPickWinner={pickHandler}
                slotLocked={slotLocked}
              />
            );
          })}
        </motion.div>
      </AnimatePresence>

      {/* Trophy block at the bottom — reminds the user where this is all heading. */}
      <div className="mt-8 grid place-items-center">
        <div className="trophy-disc-mobile relative w-20 h-20 rounded-full grid place-items-center overflow-hidden">
          <Trophy size={32} className="relative text-white drop-shadow-md" />
        </div>
        <div className="mt-2 font-display text-[10px] uppercase tracking-[0.28em] text-[var(--ink-muted)]">Copa Mundial 2026</div>
      </div>

      <style jsx>{`
        .trophy-disc-mobile {
          background: conic-gradient(from 0deg, #d4af37, #fde68a, #d4af37, #b8860b, #d4af37);
          box-shadow:
            0 0 0 3px rgba(255,255,255,0.8),
            0 14px 30px -10px rgba(212, 175, 55, 0.55);
          animation: spin 18s linear infinite;
        }
        @keyframes spin { to { transform: rotate(360deg); } }
      `}</style>
    </section>
  );
}

type MobileCard = {
  slot: string;
  round: RoundKey | "THIRD";
  ko: KOMatch | undefined;
  teamA: string | null;       // resolved team code (null if not yet known)
  teamB: string | null;
  slotTokenA: string;          // R32 template token, "" for R16+
  slotTokenB: string;
  confirmed: boolean;          // R32 only: both feeder groups closed
};

function MobileMatchCard({
  card,
  index,
  now,
  locale,
  t,
  slotStates,
  thirdRanking,
  thirdSlotProbs,
  bracketPick,
  onPickWinner,
  slotLocked,
}: {
  card: MobileCard;
  index: number;
  now: number | null;
  locale: ReturnType<typeof useLocale>["locale"];
  t: (key: string, fallback?: string) => string;
  slotStates: Map<string, SlotState>;
  thirdRanking: Standing[];
  thirdSlotProbs: Record<string, ThirdSlotProb[]>;
  bracketPick?: string;
  onPickWinner?: (code: string) => void;
  slotLocked?: boolean;
}) {
  const ko = card.ko;
  const status: LiveStatus = ko ? liveStatusFor(ko.dateISO, now) : "upcoming";
  const venue = ko ? VENUE_BY_CITY.get(ko.venueCity) : undefined;
  const stadium = ko ? (venue?.stadium ?? ko.venueStadium) : "";
  const iso2 = venue?.iso2 ?? "";
  const countdown = (status === "upcoming" && ko) ? countdownLabel(ko.dateISO, now) : null;
  const etTime = ko ? formatET(ko.dateISO) : null;

  const statusStyle: Record<LiveStatus, { bg: string; color: string; label: string; live?: boolean }> = {
    played:   { bg: "var(--bg-tint)",            color: "var(--ink-muted)", label: t("bracket.status.played",   "JUGADO") },
    live:     { bg: "rgba(239,68,68,0.18)",      color: "rgb(185,28,28)",   label: t("bracket.status.live",     "EN VIVO"), live: true },
    upcoming: { bg: "rgba(94,91,255,0.12)",      color: "var(--ink-soft)",  label: t("bracket.status.upcoming", "PRÓXIMO") },
  };
  const stat = statusStyle[status];

  // Resolve Annexe C candidates for the 3rd-place slot in this match
  const thirdToken = [card.slotTokenA, card.slotTokenB].find(tok => tok.startsWith("3rd"));
  const thirdN = thirdToken ? parseInt(thirdToken.slice(3), 10) : null;
  const thirdAnchor = thirdToken ? THIRD_TOKEN_TO_ANCHOR[thirdToken] : null;
  const thirdCandidates = (thirdAnchor ? thirdSlotProbs[thirdAnchor] : null)?.filter(p => p.pct > 0.005) ?? [];

  const cdmxTime = ko ? formatCDMXTime(ko.dateISO) : null;
  const cdmxDate = ko ? formatCDMXDate(ko.dateISO) : null;
  const etTimeStr = ko ? formatETTime(ko.dateISO) : null;
  const etDateStr = ko ? formatETDate(ko.dateISO) : null;

  // Knockout win probabilities (no draw): normalize H/(H+A) and A/(H+A)
  const winProbs = (card.teamA && card.teamB) ? (() => {
    const p = matchProbability(card.teamA!, card.teamB!);
    const total = p.H + p.A;
    const h = Math.round(p.H / total * 100);
    return { h, a: 100 - h };
  })() : null;

  const roundLabel = card.round === "THIRD"
    ? t("bracket.round.third", "3er lugar")
    : card.round === "FINAL"
      ? t("bracket.round.final", "Final")
      : `${ROUND_LABEL[card.round as RoundKey]} · #${index}`;

  const accentColor = status === "live"
    ? "rgba(239,68,68,0.18)"
    : status === "played"
      ? "rgba(0,0,0,0.06)"
      : "rgba(94,91,255,0.10)";

  return (
    <article
      className="rounded-2xl overflow-hidden"
      style={{
        background: "var(--bg-tint)",
        boxShadow: status === "live"
          ? "0 0 0 1.5px rgb(239,68,68), 0 8px 28px -8px rgba(239,68,68,0.35)"
          : "0 2px 16px -6px rgba(0,0,0,0.12), 0 0 0 1px var(--line)",
      }}
    >
      {/* ── VENUE BANNER ── */}
      <div
        className="px-4 py-3 flex items-center gap-3"
        style={{ background: accentColor }}
      >
        {iso2 ? (
          <div className="relative w-5 h-3.5 rounded-sm overflow-hidden ring-1 ring-black/15 shrink-0 shadow-sm">
            <Image src={flagUrl(iso2, 32)} alt="" fill sizes="20px" className="object-cover" unoptimized />
          </div>
        ) : (
          <div className="w-5 h-3.5 rounded-sm bg-[var(--bg)] shrink-0" />
        )}
        <div className="flex-1 min-w-0">
          <div className="font-display font-black text-[13px] leading-tight truncate">{stadium || "?"}</div>
          <div className="text-[10px] text-[var(--ink-muted)] truncate flex items-center gap-1">
            <MapPin size={9} className="shrink-0" />
            {ko?.venueCity ?? ""}
          </div>
        </div>
        <div className="flex flex-col items-end gap-1 shrink-0">
          <span className="text-[8px] font-display font-bold text-[var(--ink-muted)] uppercase tracking-widest">{card.slot}</span>
          <span
            className="flex items-center gap-1 px-2 py-0.5 rounded-full font-display font-bold uppercase tracking-wider text-[9px]"
            style={{ background: stat.bg, color: stat.color }}
          >
            {stat.live && <span className="live-dot" />}
            {stat.label}
          </span>
        </div>
      </div>

      {/* ── DUAL TIMEZONE GRID ── */}
      {ko && (
        <div className="grid grid-cols-2 divide-x divide-[var(--line)] border-y border-[var(--line)]/60">
          <div className="px-4 py-3 text-center">
            <div className="text-[8px] uppercase tracking-[0.2em] text-[var(--ink-muted)] mb-1">🇲🇽 CDMX</div>
            <div className="font-display font-black text-[22px] leading-none tabular-nums">{cdmxTime}</div>
            <div className="text-[9px] text-[var(--ink-muted)] mt-1 capitalize">{cdmxDate}</div>
          </div>
          <div className="px-4 py-3 text-center">
            <div className="text-[8px] uppercase tracking-[0.2em] text-[var(--ink-muted)] mb-1">🇺🇸 ET</div>
            <div className="font-display font-black text-[22px] leading-none tabular-nums">{etTimeStr}</div>
            <div className="text-[9px] text-[var(--ink-muted)] mt-1 capitalize">{etDateStr}</div>
          </div>
        </div>
      )}

      {/* ── COUNTDOWN STRIP ── */}
      {countdown && (
        <div
          className="flex items-center justify-center gap-2 px-4 py-2 border-b border-[var(--line)]/60"
          style={{ background: "rgba(251,191,36,0.10)" }}
        >
          <span className="text-[15px]">⏱</span>
          <span className="font-display font-black text-[16px] tabular-nums" style={{ color: "rgb(146,90,7)" }}>
            {countdown}
          </span>
          <span className="text-[10px] text-[var(--ink-muted)]">para el partido</span>
        </div>
      )}

      {/* ── ROUND LABEL ── */}
      <div className="px-4 pt-2.5 pb-0">
        <span className="text-[9px] font-display font-bold uppercase tracking-[0.18em] text-[var(--ink-muted)]">
          {roundLabel}
        </span>
      </div>

      {/* ── TEAMS ── */}
      <div className="px-3 py-2 flex flex-col gap-1">
        <MobileTeamRow
          code={card.teamA}
          slotToken={card.slotTokenA}
          confirmed={card.confirmed}
          slotStatus={card.slotTokenA ? slotStates.get(card.slotTokenA)?.status : undefined}
          t={t}
          isPicked={!!bracketPick && bracketPick === card.teamA}
          onPick={card.teamA && onPickWinner ? () => onPickWinner(card.teamA!) : undefined}
          isLocked={slotLocked}
        />
        <div className="flex items-center gap-2 my-0.5">
          {winProbs ? (
            /* Probability split bar */
            <div className="flex-1 flex items-center gap-1.5">
              <span className="text-[10px] font-display font-black tabular-nums w-7 text-right shrink-0"
                style={{ color: winProbs.h >= 50 ? "rgb(10,150,90)" : "var(--ink-muted)" }}>
                {winProbs.h}%
              </span>
              <div className="flex-1 h-2 rounded-full overflow-hidden flex" style={{ background: "var(--bg)" }}>
                <div className="h-full rounded-l-full" style={{ width: `${winProbs.h}%`, background: "rgb(94,91,255)", opacity: 0.7 }} />
                <div className="h-full rounded-r-full flex-1" style={{ background: "rgb(239,68,68)", opacity: 0.55 }} />
              </div>
              <span className="text-[10px] font-display font-black tabular-nums w-7 text-left shrink-0"
                style={{ color: winProbs.a >= 50 ? "rgb(10,150,90)" : "var(--ink-muted)" }}>
                {winProbs.a}%
              </span>
            </div>
          ) : (
            <>
              <div className="flex-1 h-px bg-[var(--line)]" />
              <span className="text-[9px] font-display font-black tracking-widest text-[var(--ink-muted)] px-1">VS</span>
              <div className="flex-1 h-px bg-[var(--line)]" />
            </>
          )}
        </div>
        <MobileTeamRow
          code={card.teamB}
          slotToken={card.slotTokenB}
          confirmed={card.confirmed}
          slotStatus={card.slotTokenB ? slotStates.get(card.slotTokenB)?.status : undefined}
          t={t}
          isPicked={!!bracketPick && bracketPick === card.teamB}
          onPick={card.teamB && onPickWinner ? () => onPickWinner(card.teamB!) : undefined}
          isLocked={slotLocked}
        />
      </div>

      {/* ── PICK STATUS ── */}
      {(bracketPick || (onPickWinner && !slotLocked)) && (
        <div className="px-4 pb-2.5 flex items-center gap-1.5">
          {bracketPick ? (
            <>
              <span className="text-[9px]">✅</span>
              <span className="text-[9px] font-display font-bold" style={{ color: "rgb(10,150,90)" }}>
                {t("bracket.pick.picked", "Tu pick:")} {getTeam(bracketPick)?.name ?? bracketPick}
              </span>
            </>
          ) : (
            <>
              <span className="text-[9px]">👆</span>
              <span className="text-[9px]" style={{ color: "var(--ink-muted)", opacity: 0.7 }}>
                {t("bracket.pick.tap", "Toca un equipo para elegir ganador")}
              </span>
            </>
          )}
          {slotLocked && (
            <span className="ml-auto text-[9px]" style={{ color: "var(--ink-muted)", opacity: 0.5 }}>🔒</span>
          )}
        </div>
      )}

      {/* ── 3RD-PLACE CANDIDATES ── */}
      {thirdCandidates.length > 0 && (
        <ThirdCandidates
          candidates={thirdCandidates}
          teamStats={Object.fromEntries(thirdRanking.map(s => [s.team, { pts: s.pts, gd: s.gd }]))}
        />
      )}
    </article>
  );
}

function ThirdCandidates({
  candidates,
  teamStats,
}: {
  candidates: ThirdSlotProb[];
  teamStats?: Record<string, { pts: number; gd: number }>;
}) {
  const [infoOpen, setInfoOpen] = useState(false);
  const show = candidates.slice(0, 5);
  const topPct = show[0]?.pct ?? 1;
  const groups = [...new Set(show.map(c => c.group))].sort().join(", ");
  const leader = show[0];

  return (
    <div className="border-t border-[var(--line)]/60" style={{ background: "rgba(20,241,149,0.03)" }}>
      {/* Header */}
      <div className="px-4 pt-2.5 pb-2 flex items-center justify-between">
        <span className="text-[9px] font-display font-black uppercase tracking-[0.18em] text-[var(--ink-muted)]">
          3ro de grupos {groups}
        </span>
        <span className="text-[8px] text-[var(--ink-muted)] opacity-60">Probabilidad</span>
      </div>

      {/* Candidate rows */}
      <div className="pb-2 space-y-0.5">
        {show.map((c, i) => {
          const team = getTeam(c.team);
          const barPct = Math.round((c.pct / topPct) * 100);
          const pctDisplay = Math.round(c.pct * 100);
          const isLeader = i === 0;
          const stats = teamStats?.[c.team];
          return (
            <div
              key={c.team}
              className="flex items-center gap-2 px-4 py-1.5"
              style={isLeader ? { background: "rgba(20,241,149,0.07)" } : {}}
            >
              {/* Flag */}
              {team ? (
                <div className="relative w-6 h-4 rounded-sm overflow-hidden ring-1 ring-black/10 shrink-0 shadow-sm">
                  <Image src={flagUrl(team.iso2, 32)} alt={team.name} fill sizes="24px" className="object-cover" unoptimized />
                </div>
              ) : (
                <div className="w-6 h-4 rounded-sm bg-[var(--bg-tint)] shrink-0" />
              )}

              {/* Team name */}
              <span className="text-[11px] font-display font-bold min-w-0 flex-[2] truncate"
                style={{ color: isLeader ? "var(--ink)" : "var(--ink-soft)" }}>
                {team?.name ?? c.team}
              </span>

              {/* Group pill */}
              <span className="text-[8px] font-bold px-1.5 py-0.5 rounded shrink-0"
                style={{ background: "var(--bg-tint)", color: "var(--ink-muted)" }}>
                {c.group}
              </span>

              {/* Pts badge */}
              {stats !== undefined && (
                <span className="text-[9px] tabular-nums font-black w-5 text-center shrink-0"
                  style={{ color: isLeader ? "rgb(10,150,90)" : "var(--ink-muted)", opacity: 0.85 }}>
                  {stats.pts}p
                </span>
              )}

              {/* Probability bar */}
              <div className="flex-[3] h-2 bg-[var(--bg)] rounded-full overflow-hidden">
                <div
                  className="h-full rounded-full"
                  style={{
                    width: `${barPct}%`,
                    background: isLeader ? "rgb(20,200,120)" : "var(--ink-muted)",
                    opacity: isLeader ? 0.9 : 0.45,
                  }}
                />
              </div>

              {/* Percentage */}
              <span className="text-[10px] font-display font-black tabular-nums w-8 text-right shrink-0"
                style={{ color: isLeader ? "rgb(10,150,90)" : "var(--ink-muted)" }}>
                {pctDisplay}%
              </span>
            </div>
          );
        })}
      </div>

      {/* Annexe C explainer toggle */}
      <div className="mx-4 mb-3 border-t border-[var(--line)]/40 pt-1.5">
        <button
          className="w-full flex items-center gap-1.5 text-left"
          onClick={() => setInfoOpen(o => !o)}
        >
          <span className="text-[9px] font-bold" style={{ color: "rgba(94,91,255,0.9)" }}>ℹ</span>
          <span className="text-[8px] flex-1" style={{ color: "var(--ink-muted)", opacity: 0.75 }}>
            ¿Cómo funciona el Annexe C de FIFA?
          </span>
          <span className="text-[8px]" style={{ color: "var(--ink-muted)", opacity: 0.4 }}>
            {infoOpen ? "▲" : "▼"}
          </span>
        </button>

        {infoOpen && (
          <div className="mt-2 space-y-2">
            {/* Explanation text */}
            <p className="text-[8px] leading-[1.55]" style={{ color: "var(--ink-muted)", opacity: 0.8 }}>
              FIFA define <strong>495 combinaciones</strong> posibles de los 8 mejores terceros.
              Para cada combinación aplica una matriz (Annexe C) que asigna qué grupo
              va a qué slot. Simulamos <strong>3,000 escenarios</strong> con los partidos
              pendientes y contamos en cuántos el Grupo {leader?.group} aterriza aquí.
            </p>

            {/* Mini standings table */}
            {teamStats && show.length > 0 && (
              <div className="rounded-lg overflow-hidden" style={{ background: "var(--bg-tint)", border: "1px solid rgba(0,0,0,0.06)" }}>
                {/* Table header */}
                <div className="flex items-center gap-2 px-2.5 py-1.5"
                  style={{ background: "rgba(0,0,0,0.04)", borderBottom: "1px solid rgba(0,0,0,0.06)" }}>
                  <span className="flex-[3] text-[7px] font-black uppercase tracking-wider" style={{ color: "var(--ink-muted)", opacity: 0.7 }}>Equipo</span>
                  <span className="w-4 text-right text-[7px] font-black uppercase tracking-wider" style={{ color: "var(--ink-muted)", opacity: 0.7 }}>G</span>
                  <span className="w-6 text-right text-[7px] font-black uppercase tracking-wider" style={{ color: "var(--ink-muted)", opacity: 0.7 }}>Pts</span>
                  <span className="w-8 text-right text-[7px] font-black uppercase tracking-wider" style={{ color: "var(--ink-muted)", opacity: 0.7 }}>DG</span>
                  <span className="w-9 text-right text-[7px] font-black uppercase tracking-wider" style={{ color: "rgba(94,91,255,0.7)" }}>Prob</span>
                </div>
                {/* Rows */}
                {show.map((c, i) => {
                  const tm = getTeam(c.team);
                  const s = teamStats[c.team];
                  const isTop = i === 0;
                  return (
                    <div key={c.team}
                      className="flex items-center gap-2 px-2.5 py-1.5"
                      style={isTop ? { background: "rgba(20,241,149,0.06)" } : {}}>
                      {/* Rank */}
                      <span className="text-[8px] font-bold w-3 shrink-0 text-center"
                        style={{ color: "var(--ink-muted)", opacity: 0.5 }}>{i + 1}</span>
                      {/* Flag */}
                      {tm ? (
                        <div className="relative w-5 h-3.5 rounded-sm overflow-hidden ring-1 ring-black/10 shrink-0">
                          <Image src={flagUrl(tm.iso2, 20)} alt={tm.name} fill sizes="20px" className="object-cover" unoptimized />
                        </div>
                      ) : <div className="w-5 h-3.5 rounded-sm bg-[var(--bg)] shrink-0" />}
                      {/* Name */}
                      <span className="flex-[3] text-[8px] font-bold truncate"
                        style={{ color: isTop ? "var(--ink)" : "var(--ink-soft)" }}>
                        {tm?.name ?? c.team}
                      </span>
                      {/* Group */}
                      <span className="w-4 text-center text-[7px] font-bold"
                        style={{ color: "var(--ink-muted)", opacity: 0.7 }}>{c.group}</span>
                      {/* Pts */}
                      <span className="w-6 text-right text-[8px] font-black tabular-nums"
                        style={{ color: isTop ? "rgb(10,150,90)" : "var(--ink-muted)" }}>
                        {s?.pts ?? "–"}
                      </span>
                      {/* GD */}
                      <span className="w-8 text-right text-[8px] tabular-nums"
                        style={{ color: "var(--ink-muted)", opacity: 0.8 }}>
                        {s !== undefined ? (s.gd >= 0 ? `+${s.gd}` : s.gd) : "–"}
                      </span>
                      {/* Probability */}
                      <span className="w-9 text-right text-[8px] font-black tabular-nums"
                        style={{ color: isTop ? "rgba(94,91,255,0.9)" : "var(--ink-muted)", opacity: isTop ? 1 : 0.7 }}>
                        {Math.round(c.pct * 100)}%
                      </span>
                    </div>
                  );
                })}
              </div>
            )}

            <p className="text-[7px] text-center" style={{ color: "var(--ink-muted)", opacity: 0.45 }}>
              Simulación Monte Carlo · 3,000 escenarios · FIFA Reglamento Annexe C
            </p>
          </div>
        )}
      </div>
    </div>
  );
}

function MobileTeamRow({
  code,
  slotToken,
  confirmed,
  slotStatus,
  t,
  isPicked,
  onPick,
  isLocked,
}: {
  code: string | null;
  slotToken: string;
  confirmed: boolean;
  slotStatus?: "confirmed" | "projected";
  t: (key: string, fallback?: string) => string;
  isPicked?: boolean;
  onPick?: () => void;
  isLocked?: boolean;
}) {
  const team = code ? getTeam(code) : null;
  const label = slotToken ? slotLabel(slotToken, t) : "";

  // CONF / PROY chip rendered per team. Only R32 rows pass a slotToken, so
  // R16+ rows skip the chip naturally.
  const statusChip = slotStatus ? (
    <span
      className="shrink-0 inline-flex items-center gap-1 px-1.5 py-0.5 rounded-full text-[9px] font-display font-bold uppercase tracking-wider"
      style={
        slotStatus === "confirmed"
          ? { background: "rgba(20,241,149,0.18)", color: "rgb(5,122,85)" }
          : { background: "rgba(251,191,36,0.18)", color: "rgb(146,90,7)" }
      }
      title={slotStatus === "confirmed"
        ? t("bracket.confirmed", "confirmado")
        : t("bracket.projected", "proyectado")}
    >
      <span
        className="w-1.5 h-1.5 rounded-full"
        style={{
          background: slotStatus === "confirmed" ? "rgb(20,148,90)" : "rgb(202,138,4)",
        }}
      />
      {slotStatus === "confirmed" ? "CONF" : "PROY"}
    </span>
  ) : null;

  // Resolved team: real flag + code + confirmed badge if its source group closed.
  if (team) {
    const pickedStyle = isPicked
      ? { background: "rgba(20,241,149,0.13)", boxShadow: "inset 0 0 0 1.5px rgba(20,200,120,0.4)" }
      : {};

    if (onPick) {
      return (
        <button
          type="button"
          onClick={onPick}
          className="w-full group flex items-center gap-2.5 rounded-xl px-2 py-1.5 transition-colors text-left"
          style={{ ...pickedStyle, cursor: isLocked ? "default" : "pointer" }}
        >
          <div className="relative w-7 h-7 rounded-md overflow-hidden ring-1 ring-[var(--line)] shrink-0">
            <Image src={flagUrl(team.iso2, 48)} alt={team.name} fill sizes="28px" className="object-cover" unoptimized />
          </div>
          <div className="min-w-0 flex-1">
            <div className="font-display font-bold text-sm leading-tight truncate">{team.name}</div>
            {label && (
              <div className="text-[10px] text-[var(--ink-muted)] truncate">{label}</div>
            )}
          </div>
          {statusChip}
          {isPicked && (
            <span className="shrink-0 w-5 h-5 grid place-items-center rounded-full text-[10px] font-bold"
              style={{ background: "rgb(20,200,120)", color: "white" }}>✓</span>
          )}
        </button>
      );
    }

    return (
      <Link
        href={`/equipos/${team.code}`}
        className="group flex items-center gap-2.5 rounded-xl px-2 py-1.5 hover:bg-[var(--bg-tint)] transition-colors"
      >
        <div className="relative w-7 h-7 rounded-md overflow-hidden ring-1 ring-[var(--line)] shrink-0">
          <Image src={flagUrl(team.iso2, 48)} alt={team.name} fill sizes="28px" className="object-cover" unoptimized />
        </div>
        <div className="min-w-0 flex-1">
          <div className="font-display font-bold text-sm leading-tight truncate">{team.name}</div>
          {label && (
            <div className="text-[10px] text-[var(--ink-muted)] truncate">{label}</div>
          )}
        </div>
        {statusChip}
        {confirmed && (
          <span
            className="shrink-0 w-5 h-5 grid place-items-center rounded-full text-[10px] font-bold"
            style={{ background: "var(--accent-mint, #14F195)", color: "white" }}
            title={t("bracket.confirmed", "confirmado")}
          >
            ✓
          </span>
        )}
      </Link>
    );
  }

  // Unresolved: placeholder card with the slot token in Spanish.
  return (
    <div className="flex items-center gap-2.5 rounded-xl px-2 py-1.5 bg-[var(--bg-tint)]/40">
      <span className="relative w-7 h-7 rounded-md grid place-items-center bg-[var(--bg-tint)] text-[var(--ink-muted)] font-display font-bold shrink-0">?</span>
      <div className="min-w-0 flex-1">
        <div className="font-display font-bold text-sm leading-tight text-[var(--ink-muted)]">
          {label || t("bracket.pending", "pendiente")}
        </div>
        {label && (
          <div className="text-[10px] text-[var(--ink-muted)] opacity-70">
            · {t("bracket.pending", "pendiente")}
          </div>
        )}
      </div>
      {statusChip}
    </div>
  );
}

