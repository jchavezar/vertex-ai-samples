"use client";

// Bold H/D/A thermometer bar — goes on every match card.
// For group-stage fixtures: pass the blended probs from useFixtureProbs().
// For KO fixtures (no draw): pass { H, D:0, A } derived from ELO matchOdds().

import { useMemo } from "react";

export type HDA = { H: number; D: number; A: number };

export function ProbabilityBar({
  probs,
  homeCode,
  awayCode,
  loading,
  compact = false,
}: {
  probs?: HDA | null;
  homeCode?: string;
  awayCode?: string;
  loading?: boolean;
  compact?: boolean;   // shorter labels, no legend row
}) {
  const norm = useMemo(() => {
    if (!probs) return null;
    const s = (probs.H || 0) + (probs.D || 0) + (probs.A || 0);
    if (s <= 0) return null;
    return { H: probs.H / s, D: probs.D / s, A: probs.A / s };
  }, [probs]);

  if (loading) {
    return (
      <div className={`w-full ${compact ? "h-1.5" : "h-2"} rounded-full bg-white/8 overflow-hidden`}>
        <div className="h-full w-1/2 bg-white/15 animate-pulse rounded-full" />
      </div>
    );
  }
  if (!norm) return null;

  const pct = (n: number) => `${Math.round(n * 100)}%`;
  const hW = Math.round(norm.H * 100);
  const dW = Math.round(norm.D * 100);
  const aW = 100 - hW - dW;

  // Dominant side
  const dominant = norm.H > norm.A ? "home" : norm.A > norm.H ? "away" : "draw";

  return (
    <div className="w-full space-y-1">
      {/* Labels row */}
      {!compact && (
        <div className="flex items-center justify-between text-[9px] font-black uppercase tracking-[0.12em]">
          <span style={{ color: dominant === "home" ? "#34d399" : "rgba(255,255,255,0.35)" }}>
            {homeCode ?? "Local"} {pct(norm.H)}
          </span>
          {norm.D > 0.01 && (
            <span style={{ color: dominant === "draw" ? "#a3a3a3" : "rgba(255,255,255,0.25)" }}>
              X {pct(norm.D)}
            </span>
          )}
          <span style={{ color: dominant === "away" ? "#f87171" : "rgba(255,255,255,0.35)" }}>
            {pct(norm.A)} {awayCode ?? "Visita"}
          </span>
        </div>
      )}

      {/* The bar */}
      <div
        className="relative w-full overflow-hidden flex"
        style={{ height: compact ? 6 : 10, borderRadius: 99 }}
        role="img"
        aria-label={`${homeCode ?? "Local"} ${pct(norm.H)}, empate ${pct(norm.D)}, ${awayCode ?? "Visita"} ${pct(norm.A)}`}
      >
        {/* Home segment */}
        <div
          style={{
            width: `${hW}%`,
            background: "linear-gradient(90deg, #059669, #34d399)",
            transition: "width 0.6s ease",
          }}
        />
        {/* Draw segment */}
        {norm.D > 0.005 && (
          <div
            style={{
              width: `${dW}%`,
              background: "linear-gradient(90deg, #525252, #737373)",
              transition: "width 0.6s ease",
            }}
          />
        )}
        {/* Away segment */}
        <div
          style={{
            flex: 1,
            background: "linear-gradient(90deg, #f87171, #dc2626)",
            transition: "width 0.6s ease",
          }}
        />

        {/* Dominant glow overlay */}
        {dominant === "home" && norm.H > 0.55 && (
          <div className="absolute inset-0 pointer-events-none"
            style={{ background: "linear-gradient(90deg, rgba(52,211,153,0.25) 0%, transparent 60%)" }} />
        )}
        {dominant === "away" && norm.A > 0.55 && (
          <div className="absolute inset-0 pointer-events-none"
            style={{ background: "linear-gradient(270deg, rgba(248,113,113,0.25) 0%, transparent 60%)" }} />
        )}
      </div>

      {/* Compact mode: inline pct labels below the bar */}
      {compact && (
        <div className="flex justify-between text-[8px] font-black tabular-nums">
          <span style={{ color: "#34d399", opacity: dominant === "home" ? 1 : 0.5 }}>{pct(norm.H)}</span>
          {norm.D > 0.01 && <span style={{ color: "#a3a3a3", opacity: dominant === "draw" ? 1 : 0.4 }}>X {pct(norm.D)}</span>}
          <span style={{ color: "#f87171", opacity: dominant === "away" ? 1 : 0.5 }}>{pct(norm.A)}</span>
        </div>
      )}
    </div>
  );
}
