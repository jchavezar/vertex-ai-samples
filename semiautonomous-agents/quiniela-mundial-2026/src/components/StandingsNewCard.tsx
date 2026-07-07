"use client";

// Home "NEW" hero band promoting /standings — only shows for ~7 days after
// the page is announced; once the user lands on /standings the chip self-hides
// via localStorage. Mexican-flag palette + pulse lozenge keeps it visible
// without crowding the existing Charal del Día chip.

import Link from "next/link";
import { useEffect, useState } from "react";
import { BarChart3, ArrowUpRight, Flame, Sparkles } from "lucide-react";
import { useLocale } from "@/lib/i18n";

const SEEN_KEY = "q26:standings-new-seen-at";
const NEW_TTL_MS = 7 * 24 * 60 * 60 * 1000; // 7 days

export function StandingsNewCard() {
  const { t } = useLocale();
  const [showNew, setShowNew] = useState(false);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    try {
      const seenAt = Number(localStorage.getItem(SEEN_KEY) ?? 0);
      if (!Number.isFinite(seenAt) || seenAt <= 0) {
        // First view ever — start the 7-day countdown now.
        localStorage.setItem(SEEN_KEY, String(Date.now()));
        setShowNew(true);
        return;
      }
      const age = Date.now() - seenAt;
      setShowNew(age < NEW_TTL_MS);
    } catch {
      setShowNew(true);
    }
  }, []);

  if (!mounted) return null;

  return (
    <Link
      href="/standings"
      className="block group relative overflow-hidden rounded-3xl ring-1 ring-black/5 shadow-[0_18px_50px_-25px_rgba(0,0,0,0.45)] transition-transform hover:-translate-y-0.5"
      style={{
        background:
          "linear-gradient(135deg, #006847 0%, #00734f 38%, #ffffff 49%, #ffffff 51%, #d31a30 62%, #CE1126 100%)",
      }}
    >
      {/* Subtle grid overlay */}
      <div
        className="absolute inset-0 opacity-25 pointer-events-none"
        style={{
          backgroundImage:
            "linear-gradient(rgba(255,255,255,.18) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,.18) 1px, transparent 1px)",
          backgroundSize: "32px 32px",
        }}
      />

      {/* Soft glow on hover */}
      <div className="absolute -top-24 -right-16 w-72 h-72 rounded-full blur-3xl opacity-40 bg-white/40 group-hover:opacity-60 transition-opacity" />

      <div className="relative grid sm:grid-cols-[auto_1fr_auto] items-center gap-4 px-5 py-4 sm:px-6 sm:py-5">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 rounded-2xl bg-black/85 grid place-items-center text-white shadow-lg ring-2 ring-white/70">
            <BarChart3 size={22} />
          </div>
          {showNew && (
            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-[#CE1126] text-white text-[10px] font-extrabold tracking-[0.18em] uppercase shadow ring-2 ring-white animate-pulse">
              <Sparkles size={10} /> {t("standings.newChip")}
            </span>
          )}
        </div>

        <div className="text-white drop-shadow-[0_1px_2px_rgba(0,0,0,0.35)]">
          <div className="text-[10px] uppercase tracking-[0.22em] font-extrabold text-white/85 flex items-center gap-1.5">
            <Flame size={11} /> {t("standings.heroKicker")}
          </div>
          <div className="font-display text-xl sm:text-2xl font-bold leading-tight">
            {t("standings.heroTitle")}
          </div>
          <div className="text-sm text-white/90 mt-0.5 max-w-xl">
            {t("standings.heroSubtitle")}
          </div>
        </div>

        <div className="flex items-center gap-1 self-end sm:self-center justify-end">
          <span className="hidden sm:inline-flex items-center gap-1 px-3 py-1.5 rounded-full bg-black/85 text-white text-xs font-bold tracking-wide">
            {t("standings.heroCta")} <ArrowUpRight size={14} />
          </span>
          <span className="sm:hidden inline-flex items-center gap-1 px-3 py-1.5 rounded-full bg-black/85 text-white text-xs font-bold">
            <ArrowUpRight size={14} />
          </span>
        </div>
      </div>
    </Link>
  );
}
