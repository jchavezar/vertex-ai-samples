"use client";

// Chip shown above the leaderboard table. Tracks the current player's index
// against the last one we recorded on this device. Stamps a fresh snapshot
// for EVERY player so personal-alerts.ts ("te rebasaron") keeps working.

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { useLocale } from "@/lib/i18n";
import { writeRankSnapshot } from "@/lib/personal-alerts";

const KEY = (pid: string) => `q26:last-rank:${pid}`;

type Ordered = { id: string }; // anything with an id, in displayed order

export function RankDeltaChip({
  orderedIds,
  currentPlayerId,
}: {
  orderedIds: ReadonlyArray<Ordered | string>;
  currentPlayerId: string | null;
}) {
  const { t } = useLocale();
  const [delta, setDelta] = useState<number | null>(null);

  useEffect(() => {
    if (typeof window === "undefined" || !currentPlayerId) {
      setDelta(null);
      return;
    }
    const ids: string[] = orderedIds.map(o => (typeof o === "string" ? o : o.id));
    const idx = ids.indexOf(currentPlayerId);
    if (idx < 0) { setDelta(null); return; }
    const myRank = idx + 1;

    // Compare against last-seen rank for me.
    let prev: number | null = null;
    try {
      const raw = window.localStorage.getItem(KEY(currentPlayerId));
      const parsed = raw ? Number(raw) : NaN;
      if (Number.isFinite(parsed) && parsed > 0) prev = parsed;
    } catch {}

    // Stamp current rank for every player — used both by this chip and by
    // personal-alerts.ts which expects q26:alert-rank:{pid} updated each visit.
    ids.forEach((pid, i) => {
      try { window.localStorage.setItem(KEY(pid), String(i + 1)); } catch {}
      writeRankSnapshot(pid, i + 1);
    });

    if (prev === null || prev === myRank) { setDelta(null); return; }
    // movement = prev - new; positive = climbed (smaller rank #).
    setDelta(prev - myRank);
  }, [orderedIds, currentPlayerId]);

  if (delta === null || delta === 0) return null;
  const up = delta > 0;
  const abs = Math.abs(delta);
  const label = up
    ? t("delta.rankUp").replace("{n}", String(abs))
    : t("delta.rankDown").replace("{n}", String(abs));

  return (
    <div
      className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-bold mb-3"
      style={{
        background: up
          ? "color-mix(in srgb, var(--accent-mint) 22%, transparent)"
          : "color-mix(in srgb, #FF3B82 18%, transparent)",
        color: up ? "#059669" : "#BE123C",
      }}
      role="status"
      aria-live="polite"
    >
      <motion.span
        aria-hidden
        initial={{ y: up ? 6 : -6, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ type: "spring", stiffness: 320, damping: 14, repeat: 2, repeatType: "mirror" }}
      >
        {up ? "⬆️" : "⬇️"}
      </motion.span>
      <span>{label}</span>
    </div>
  );
}
