"use client";

import { useEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";
import Image from "next/image";
import { Crown, X } from "lucide-react";
import { PLAYERS, type Player } from "@/data/players";
import { getTeam, flagUrl } from "@/data/teams";
import { useProfileAvatar } from "@/lib/profile-avatar";

// ─── Types ────────────────────────────────────────────────────────────────────

type PlayerStats = {
  rank: number;
  score: number;
  groupHits: number;
  groupMiss: number;
  koHits: number;
  koMiss: number;
  champion?: string;
  r32Picks: Array<{ slot: string; pick: string; actual?: string; hit?: boolean }>;
};

// ─── Data fetching ────────────────────────────────────────────────────────────

async function fetchPlayerStats(playerId: string): Promise<PlayerStats | null> {
  try {
    const res = await fetch(`/api/player-stats?playerId=${encodeURIComponent(playerId)}`, { cache: "no-store" });
    const json = await res.json();
    if (!json.ok || !json.stats) return null;
    return json.stats as PlayerStats;
  } catch {
    return null;
  }
}

// ─── Avatar with profile lookup ───────────────────────────────────────────────

function PlayerPhoto({ player, size }: { player: Player; size: number }) {
  const aiUrl = useProfileAvatar(player.id);
  const src = aiUrl || player.photoDataUrl || player.defaultPhoto;
  if (src) {
    return (
      <div className="rounded-2xl overflow-hidden ring-2 ring-white/10 shrink-0 shadow-2xl"
        style={{ width: size, height: size }}>
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img src={src} alt={player.name} className="w-full h-full object-cover" />
      </div>
    );
  }
  return (
    <div className="rounded-2xl grid place-items-center shrink-0"
      style={{ width: size, height: size, background: player.accent + "33", fontSize: size * 0.45 }}>
      <span>{player.emoji}</span>
    </div>
  );
}

// ─── Rank badge ───────────────────────────────────────────────────────────────

function RankBadge({ rank }: { rank: number }) {
  const medals: Record<number, string> = { 1: "🥇", 2: "🥈", 3: "🥉" };
  const colors: Record<number, string> = {
    1: "rgba(212,175,55,0.2)",
    2: "rgba(192,192,192,0.2)",
    3: "rgba(205,127,50,0.2)",
  };
  return (
    <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-black"
      style={{ background: colors[rank] ?? "rgba(255,255,255,0.08)", color: "rgba(255,255,255,0.9)" }}>
      {medals[rank] ?? ""}#{rank}
    </span>
  );
}

// ─── Stat bar ─────────────────────────────────────────────────────────────────

function StatRow({ label, hits, total, color }: { label: string; hits: number; total: number; color: string }) {
  const pct = total > 0 ? Math.round((hits / total) * 100) : 0;
  return (
    <div className="space-y-1">
      <div className="flex justify-between items-center">
        <span className="text-[10px] font-bold uppercase tracking-wider text-white/50">{label}</span>
        <span className="text-[11px] font-black tabular-nums text-white/80">
          {hits}/{total} <span className="text-white/40 font-normal">({pct}%)</span>
        </span>
      </div>
      <div className="h-1.5 rounded-full overflow-hidden bg-white/10">
        <div className="h-full rounded-full transition-all duration-700"
          style={{ width: `${pct}%`, background: color }} />
      </div>
    </div>
  );
}

// ─── R32 grid ─────────────────────────────────────────────────────────────────

function R32Grid({ picks }: { picks: PlayerStats["r32Picks"] }) {
  if (!picks.length) return null;
  return (
    <div>
      <div className="text-[9px] font-black uppercase tracking-[0.2em] text-white/30 mb-2">
        32avos · {picks.filter(p => p.pick).length}/16 picks
      </div>
      <div className="grid grid-cols-4 gap-1.5">
        {picks.map(({ slot, pick, actual, hit }) => {
          const team = pick ? getTeam(pick) : null;
          const slotNum = slot.replace("R32-", "");
          const bg = hit === true
            ? "rgba(20,200,100,0.18)"
            : hit === false
            ? "rgba(239,68,68,0.15)"
            : pick
            ? "rgba(94,91,255,0.15)"
            : "rgba(255,255,255,0.04)";
          const border = hit === true
            ? "1px solid rgba(20,200,100,0.4)"
            : hit === false
            ? "1px solid rgba(239,68,68,0.3)"
            : pick
            ? "1px solid rgba(94,91,255,0.3)"
            : "1px solid rgba(255,255,255,0.08)";

          return (
            <div key={slot} className="rounded-lg p-1.5 flex flex-col items-center gap-0.5"
              style={{ background: bg, border }}>
              <span className="text-[7px] font-bold text-white/30">{slotNum}</span>
              {team ? (
                <div className="relative w-5 h-5 rounded-sm overflow-hidden">
                  <Image src={flagUrl(team.iso2, 32)} alt={pick} fill sizes="20px" className="object-cover" unoptimized />
                </div>
              ) : (
                <div className="w-5 h-5 rounded-sm bg-white/10 grid place-items-center">
                  <span className="text-[8px] text-white/20">?</span>
                </div>
              )}
              <span className="text-[7px] font-black text-white/60 tabular-nums leading-none">
                {pick || "—"}
              </span>
              {hit === true && <span className="text-[8px] leading-none">✅</span>}
              {hit === false && <span className="text-[8px] leading-none">❌</span>}
            </div>
          );
        })}
      </div>
    </div>
  );
}

// ─── Modal ────────────────────────────────────────────────────────────────────

function Modal({ player, onClose }: { player: Player; onClose: () => void }) {
  const [stats, setStats] = useState<PlayerStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [mounted, setMounted] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setMounted(true);
    const onKey = (e: KeyboardEvent) => { if (e.key === "Escape") onClose(); };
    document.addEventListener("keydown", onKey);
    const prev = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => { document.removeEventListener("keydown", onKey); document.body.style.overflow = prev; };
  }, [onClose]);

  useEffect(() => {
    fetchPlayerStats(player.id).then(s => { setStats(s); setLoading(false); });
  }, [player.id]);

  const champion = stats?.champion ? getTeam(stats.champion) : null;
  const totalResolved = (stats?.koHits ?? 0) + (stats?.koMiss ?? 0);
  const totalGroup = (stats?.groupHits ?? 0) + (stats?.groupMiss ?? 0);

  if (!mounted || typeof document === "undefined") return null;

  return createPortal(
    <div
      className="fixed inset-0 z-[200] flex items-end sm:items-center justify-center p-0 sm:p-4"
      style={{ background: "rgba(0,0,0,0.75)", backdropFilter: "blur(8px)" }}
      onClick={onClose}
    >
      <div
        ref={scrollRef}
        className="relative w-full sm:max-w-sm rounded-t-3xl sm:rounded-3xl overflow-hidden overflow-y-auto max-h-[92vh]"
        style={{
          background: "linear-gradient(160deg, #1a1a2e 0%, #16213e 60%, #0f1020 100%)",
          boxShadow: `0 -4px 60px -10px ${player.accent}44, 0 0 0 1px rgba(255,255,255,0.06)`,
        }}
        onClick={e => e.stopPropagation()}
      >
        {/* Close */}
        <button type="button" onClick={onClose} aria-label="Cerrar"
          className="absolute top-3 right-3 z-10 w-8 h-8 rounded-full grid place-items-center text-white/60 hover:text-white transition-colors"
          style={{ background: "rgba(255,255,255,0.08)" }}>
          <X size={16} />
        </button>

        {/* Header with accent gradient */}
        <div className="px-5 pt-6 pb-4" style={{
          background: `linear-gradient(135deg, ${player.accent}22 0%, transparent 60%)`,
        }}>
          <div className="flex items-end gap-4">
            <PlayerPhoto player={player} size={88} />
            <div className="flex-1 min-w-0 pb-1">
              <div className="flex items-center gap-2 mb-1.5 flex-wrap">
                {stats && <RankBadge rank={stats.rank} />}
                {player.isBot && (
                  <span className="text-[9px] font-bold px-1.5 py-0.5 rounded-full bg-white/8 text-white/40">
                    referencia
                  </span>
                )}
              </div>
              <div className="font-display font-black text-xl text-white leading-tight truncate">
                {player.name}
              </div>
              <div className="text-sm text-white/40 mt-0.5">{player.emoji}</div>
            </div>
          </div>

          {/* Score */}
          {stats && (
            <div className="mt-4 flex items-baseline gap-1.5">
              <span className="font-display font-black text-4xl tabular-nums" style={{ color: player.accent }}>
                {stats.score}
              </span>
              <span className="text-sm font-bold text-white/40">pts</span>
              <span className="ml-auto text-[11px] text-white/40 font-semibold tabular-nums">
                {stats.groupHits + stats.koHits} aciertos
              </span>
            </div>
          )}
        </div>

        {/* Stats */}
        <div className="px-5 pb-6 space-y-4">
          {loading && (
            <div className="py-8 flex items-center justify-center gap-2 text-white/30">
              <span className="w-4 h-4 border-2 border-white/20 border-t-white/60 rounded-full animate-spin" />
              <span className="text-sm">Cargando stats…</span>
            </div>
          )}

          {!loading && stats && (
            <>
              {/* Stat bars */}
              <div className="space-y-3">
                <StatRow
                  label="Fase de grupos"
                  hits={stats.groupHits}
                  total={totalGroup}
                  color="rgb(94,91,255)"
                />
                {totalResolved > 0 && (
                  <StatRow
                    label="Ronda eliminatoria"
                    hits={stats.koHits}
                    total={totalResolved}
                    color="rgb(20,200,120)"
                  />
                )}
              </div>

              {/* Champion */}
              {champion && (
                <div className="flex items-center gap-3 p-3 rounded-xl"
                  style={{ background: "rgba(212,175,55,0.08)", border: "1px solid rgba(212,175,55,0.2)" }}>
                  <Crown size={14} className="text-[#D4AF37] shrink-0" />
                  <span className="text-[11px] font-bold text-white/50 uppercase tracking-wider">Campeón</span>
                  <div className="flex items-center gap-2 ml-auto">
                    <div className="relative w-6 h-4 rounded-sm overflow-hidden ring-1 ring-white/10">
                      <Image src={flagUrl(champion.iso2, 40)} alt={champion.name} fill sizes="24px" className="object-cover" unoptimized />
                    </div>
                    <span className="font-display font-black text-[13px] text-white/90">{champion.code}</span>
                  </div>
                </div>
              )}

              {/* R32 grid */}
              {stats.r32Picks.length > 0 && <R32Grid picks={stats.r32Picks} />}
            </>
          )}

          {!loading && !stats && (
            <div className="py-6 text-center text-white/30 text-sm">
              Sin datos disponibles
            </div>
          )}
        </div>
      </div>
    </div>,
    document.body,
  );
}

// ─── Public hook + wrapper ────────────────────────────────────────────────────

export function useCharalModal() {
  const [open, setOpen] = useState<Player | null>(null);
  const openModal = (player: Player) => setOpen(player);
  const closeModal = () => setOpen(null);
  const ModalNode = open ? <Modal player={open} onClose={closeModal} /> : null;
  return { openModal, closeModal, ModalNode };
}

export function CharalProfileTrigger({
  player,
  children,
  className = "",
}: {
  player: Player;
  children: React.ReactNode;
  className?: string;
}) {
  const { openModal, ModalNode } = useCharalModal();
  return (
    <>
      <button
        type="button"
        className={`appearance-none bg-transparent border-none p-0 m-0 cursor-pointer ${className}`}
        onClick={e => { e.stopPropagation(); openModal(player); }}
        aria-label={`Ver stats de ${player.name}`}
      >
        {children}
      </button>
      {ModalNode}
    </>
  );
}
