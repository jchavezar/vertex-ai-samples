"use client";

// Tiny 3-segment H/D/A probability bar for upcoming match cards.
// Stays out of the way visually — single row with mini bar + tight pct labels.

import { useMemo } from "react";

export function ProbabilityStrip({
  probs,
  loading,
  homeLabel,
  awayLabel,
}: {
  probs?: { H: number; D: number; A: number } | null;
  loading?: boolean;
  homeLabel?: string;
  awayLabel?: string;
}) {
  const norm = useMemo(() => {
    if (!probs) return null;
    const s = (probs.H || 0) + (probs.D || 0) + (probs.A || 0);
    if (s <= 0) return null;
    return { H: probs.H / s, D: probs.D / s, A: probs.A / s };
  }, [probs]);

  if (loading) {
    return (
      <div className="mt-2 pt-2 border-t border-[var(--line)] flex items-center gap-2">
        <span className="text-[10px] uppercase tracking-wider text-[var(--ink-muted)]">Probabilidad</span>
        <div className="flex-1 h-1.5 rounded-full bg-[var(--bg-tint)] shimmer" />
      </div>
    );
  }
  if (!norm) return null;

  const pct = (n: number) => `${Math.round(n * 100)}%`;
  return (
    <div className="mt-2 pt-2 border-t border-[var(--line)]">
      <div className="flex items-center justify-between text-[10px] text-[var(--ink-muted)] mb-1">
        <span className="uppercase tracking-wider">Probabilidad blend-v2</span>
        <span className="tabular-nums">
          <span style={{ color: "var(--accent-mint)" }}>{pct(norm.H)}</span>
          <span className="mx-1">·</span>
          <span>{pct(norm.D)}</span>
          <span className="mx-1">·</span>
          <span style={{ color: "var(--accent-coral)" }}>{pct(norm.A)}</span>
        </span>
      </div>
      <div className="h-1.5 rounded-full overflow-hidden flex bg-[var(--bg-tint)]" role="img"
           aria-label={`Probabilidad: ${homeLabel ?? "local"} ${pct(norm.H)}, empate ${pct(norm.D)}, ${awayLabel ?? "visita"} ${pct(norm.A)}`}>
        <div style={{ width: `${norm.H * 100}%`, background: "var(--accent-mint)" }} />
        <div style={{ width: `${norm.D * 100}%`, background: "var(--ink-muted)" }} />
        <div style={{ width: `${norm.A * 100}%`, background: "var(--accent-coral)" }} />
      </div>
    </div>
  );
}
