"use client";

import { useEffect, useState } from "react";
import { usePlayer } from "@/lib/player-context";
import { useLocale } from "@/lib/i18n";
import { currentStreak, wasBroken } from "@/lib/daily-streak";

// Suppresses the one-shot "racha rota" banner for the rest of the tab session
// so a returning user only sees it once per visit.
const BROKEN_SUPPRESS_KEY = "q26:daily-streak:broken-shown";

export function DailyStreakChip() {
  const { currentPlayer } = usePlayer();
  const { t } = useLocale();
  const [streak, setStreak] = useState(0);
  const [showBroken, setShowBroken] = useState(false);

  useEffect(() => {
    if (!currentPlayer) {
      setStreak(0);
      setShowBroken(false);
      return;
    }
    const pid = currentPlayer.id;
    const n = currentStreak(pid);
    setStreak(n);
    if (n < 2 && wasBroken(pid)) {
      try {
        const seen = window.sessionStorage.getItem(`${BROKEN_SUPPRESS_KEY}:${pid}`);
        if (!seen) {
          setShowBroken(true);
          window.sessionStorage.setItem(`${BROKEN_SUPPRESS_KEY}:${pid}`, "1");
        }
      } catch {
        setShowBroken(true);
      }
    }
  }, [currentPlayer]);

  useEffect(() => {
    if (!showBroken) return;
    const tm = setTimeout(() => setShowBroken(false), 5000);
    return () => clearTimeout(tm);
  }, [showBroken]);

  if (!currentPlayer) return null;

  if (showBroken && streak < 2) {
    return (
      <span
        role="status"
        title={t("streak.broken")}
        className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider bg-[#fee2e2] text-[#991b1b] ring-1 ring-[#fecaca]"
      >
        <span aria-hidden>💀</span>
        <span className="hidden sm:inline">{t("streak.broken")}</span>
      </span>
    );
  }

  if (streak < 2) return null;

  const hot = streak >= 7;
  const bg = hot ? "#14F195" : "#F59E0B";
  const fg = hot ? "#052e1c" : "#3b1d00";

  return (
    <span
      title={`${streak} ${t("streak.days")}`}
      className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider"
      style={{ background: bg, color: fg }}
    >
      <span aria-hidden>📅</span>
      <span className="tabular-nums">{streak}</span>
      <span className="hidden sm:inline">{t("streak.days")}</span>
    </span>
  );
}
