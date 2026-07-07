"use client";

// Tiny banner shown above the user's own cromo hero. Compares the live
// rating against the one we stored the last time this player viewed home,
// and reports the OVR delta in mint (up) or rose (down). Hides on first
// view (no baseline) or when the rating hasn't moved.

import { useEffect, useState } from "react";
import { useLocale } from "@/lib/i18n";

const KEY = (pid: string) => `q26:cromo-rating:${pid}`;

export function CromoDeltaBanner({ playerId, rating }: { playerId: string; rating: number }) {
  const { t } = useLocale();
  const [prev, setPrev] = useState<number | null>(null);
  // Only read storage on mount AND when the player/rating pair changes — that
  // way bouncing between Home re-renders doesn't keep resetting the banner.
  useEffect(() => {
    if (typeof window === "undefined") return;
    let stored: number | null = null;
    try {
      const raw = window.localStorage.getItem(KEY(playerId));
      const parsed = raw ? Number(raw) : NaN;
      if (Number.isFinite(parsed)) stored = parsed;
    } catch { /* private mode */ }
    setPrev(stored);
    // Stamp the new rating so the next visit compares against this one.
    try { window.localStorage.setItem(KEY(playerId), String(rating)); } catch {}
  }, [playerId, rating]);

  if (prev === null || prev === rating) return null;
  const diff = rating - prev;
  if (diff === 0) return null;
  const up = diff > 0;
  const label = up
    ? t("delta.cromoUp")
        .replace("{prev}", String(prev))
        .replace("{next}", String(rating))
        .replace("{diff}", String(diff))
    : t("delta.cromoDown")
        .replace("{prev}", String(prev))
        .replace("{next}", String(rating))
        .replace("{diff}", String(Math.abs(diff)));

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
      <span aria-hidden>{up ? "🔼" : "🔽"}</span>
      <span>{label}</span>
    </div>
  );
}
