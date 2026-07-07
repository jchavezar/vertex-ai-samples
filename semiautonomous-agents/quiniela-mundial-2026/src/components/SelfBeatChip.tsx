"use client";

// Self-vs-self comparison: today's points vs the player's daily average.
// Computed across all decided fixtures grouped by their fixture date.
// Mounts as a tiny pill near "Tus puntos hoy".

import { useEffect, useMemo, useState } from "react";
import { Flame } from "lucide-react";
import { useLocale } from "@/lib/i18n";
import { allGroupFixtures } from "@/data/groups";
import {
  loadPredictions,
  scoreGroupPrediction,
  type MatchResult,
} from "@/lib/predictions";

type Finals = Record<string, { homeGoals: number; awayGoals: number }>;

function cdmxDateOf(ms: number): string {
  return new Date(ms).toLocaleDateString("en-CA", { timeZone: "America/Mexico_City" });
}

export function SelfBeatChip({
  playerId,
  finals,
}: {
  playerId: string | null;
  finals: Finals;
}) {
  const { t } = useLocale();
  const [now, setNow] = useState<number | null>(null);
  // Hydrate on mount only — daily breakdown doesn't need a live ticker.
  useEffect(() => { setNow(Date.now()); }, []);

  const data = useMemo(() => {
    if (!playerId || now === null) return null;
    const picks = loadPredictions(playerId);
    if (!picks) return null;
    const fxById = new Map(allGroupFixtures().map(fx => [fx.id, fx]));
    const ptsByDate = new Map<string, number>();
    for (const [fxId, final] of Object.entries(finals)) {
      const fx = fxById.get(fxId);
      if (!fx) continue;
      const pred = picks.group[fxId];
      if (!pred?.pick) continue;
      const actual: MatchResult = {
        home: fx.home, away: fx.away,
        homeGoals: final.homeGoals, awayGoals: final.awayGoals,
      };
      const pts = scoreGroupPrediction(pred, actual);
      ptsByDate.set(fx.date, (ptsByDate.get(fx.date) ?? 0) + pts);
    }
    if (ptsByDate.size === 0) return null;
    const today = cdmxDateOf(now);
    const todayPts = ptsByDate.get(today) ?? 0;
    // Average across days that actually had finals — gives an honest baseline.
    let sum = 0, n = 0;
    for (const [, v] of ptsByDate) { sum += v; n += 1; }
    const avg = n > 0 ? sum / n : 0;
    return { todayPts, avg, hasToday: ptsByDate.has(today) };
  }, [playerId, finals, now]);

  if (!data || !data.hasToday) return null;
  const { todayPts, avg } = data;
  const above = todayPts >= avg;
  const avgRounded = Math.round(avg);
  const label = above
    ? t("delta.dayRecord")
        .replace("{today}", String(todayPts))
        .replace("{avg}", String(avgRounded))
    : t("delta.calmDay")
        .replace("{today}", String(todayPts))
        .replace("{avg}", String(avgRounded));

  return (
    <div
      className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-bold tabular-nums"
      style={{
        background: above
          ? "color-mix(in srgb, var(--accent-mint) 20%, transparent)"
          : "var(--bg-tint)",
        color: above ? "#059669" : "var(--ink-muted)",
      }}
      title={`${todayPts} hoy · promedio diario ${avgRounded}`}
    >
      {above && <Flame size={11} />}
      <span>{label}</span>
    </div>
  );
}
