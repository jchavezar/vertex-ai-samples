"use client";

// Hybrid banner. Two modes share the same real estate at the top of the app:
//
//   1. ALERT mode (violet) — personalized "for you" nudges computed client-side
//      from the logged-in player's picks + live scoreboard + MVP doc. Highest
//      priority alert wins; multiple alerts cycle. Dismissible per-alert with
//      a localStorage TTL.
//
//   2. NEWS mode (default) — the original Mundial news rotation. Fallback when
//      there are no active alerts or when the player isn't logged in.
//
// The strategy: push notifications on web are too fragile and WhatsApp
// automation is risky for the owner's personal account, so we lean on
// in-app delivery whenever the user opens the PWA.

import { useCallback, useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Newspaper, ChevronRight, Bell, X } from "lucide-react";
import { usePlayer } from "@/lib/player-context";
import { useLocale } from "@/lib/i18n";
import { loadPredictions } from "@/lib/predictions";
import { useLiveScoreboard } from "@/lib/live-scoreboard";
import {
  computeAlerts,
  dismissAlert,
  readRankSnapshot,
  type Alert,
  type MvpEntry,
} from "@/lib/personal-alerts";

type NewsItem = {
  title: string;
  link: string;
  source: string;
  pubDate: string;
};

const ALERT_CYCLE_MS = 6000;
const NEWS_CYCLE_MS = 5000;

export function NewsBanner() {
  const { currentPlayer } = usePlayer();
  const { t } = useLocale();
  const live = useLiveScoreboard();

  const [items, setItems] = useState<NewsItem[]>([]);
  const [newsIdx, setNewsIdx] = useState(0);
  const [newsLoaded, setNewsLoaded] = useState(false);

  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [alertIdx, setAlertIdx] = useState(0);
  const [mvp, setMvp] = useState<MvpEntry | null>(null);
  // bump to force a recompute (predictions-updated, visibility change, etc.)
  const [tick, setTick] = useState(0);

  // ---------------- News fetch (unchanged behavior) ----------------
  useEffect(() => {
    let alive = true;
    fetch("/api/news")
      .then(r => r.json())
      .then((d: { items?: NewsItem[] }) => {
        if (!alive) return;
        setItems(d.items ?? []);
        setNewsLoaded(true);
      })
      .catch(() => alive && setNewsLoaded(true));
    return () => { alive = false; };
  }, []);

  // ---------------- MVP fetch (once on mount) ----------------
  useEffect(() => {
    let alive = true;
    fetch("/api/daily-mvp", { cache: "no-store" })
      .then(r => r.ok ? r.json() : null)
      .then((j: { entries?: MvpEntry[] } | null) => {
        if (!alive || !j?.entries) return;
        // entries are date-desc; take [0] only if it's actually TODAY's
        const todayISO = new Date().toLocaleDateString("en-CA", { timeZone: "America/New_York" });
        const todays = j.entries.find(e => e.date === todayISO) ?? null;
        setMvp(todays);
      })
      .catch(() => {});
    return () => { alive = false; };
  }, []);

  // ---------------- Recompute alerts ----------------
  const recompute = useCallback(() => {
    if (!currentPlayer) { setAlerts([]); return; }
    const predictions = loadPredictions(currentPlayer.id);

    // Build a finals-as-MatchResult map. live.finals only has goals; we need
    // home/away codes too. Pull from the fixtures list.
    const finals = Object.fromEntries(
      Object.entries(live.finals).flatMap(([fxId, f]) => {
        return [[fxId, { home: "", away: "", homeGoals: f.homeGoals, awayGoals: f.awayGoals }]] as const;
      })
    );

    const computed = computeAlerts({
      playerId: currentPlayer.id,
      playerName: currentPlayer.name,
      predictions,
      liveByFixture: live.byId,
      finals,
      mvpToday: mvp,
      // myCurrentRank/lastSeenRank intentionally omitted in this pass — the
      // banner doesn't have all-players' picks loaded, and re-fetching on
      // every open would be wasteful. Rank snapshots get written by other
      // surfaces (leaderboard page) and we'd surface "te rebasaron" there.
      myCurrentRank: null,
      lastSeenRank: readRankSnapshot(currentPlayer.id),
      overtakerName: null,
      t,
    });
    setAlerts(computed);
    setAlertIdx(0);
  }, [currentPlayer, live.byId, live.finals, mvp, t]);

  useEffect(() => { recompute(); }, [recompute, tick]);

  // Recompute on predictions-updated + visibility change. Visibility ensures
  // "pick por cerrar" timers stay fresh when the user tabs back.
  useEffect(() => {
    const onPredUpd = () => setTick(n => n + 1);
    const onVis = () => { if (document.visibilityState === "visible") setTick(n => n + 1); };
    window.addEventListener("q26:predictions-updated", onPredUpd);
    document.addEventListener("visibilitychange", onVis);
    window.addEventListener("focus", onVis);
    return () => {
      window.removeEventListener("q26:predictions-updated", onPredUpd);
      document.removeEventListener("visibilitychange", onVis);
      window.removeEventListener("focus", onVis);
    };
  }, []);

  // ---------------- Cycle indices ----------------
  useEffect(() => {
    if (alerts.length < 2) return;
    const id = setInterval(() => setAlertIdx(i => (i + 1) % alerts.length), ALERT_CYCLE_MS);
    return () => clearInterval(id);
  }, [alerts.length]);

  useEffect(() => {
    if (items.length < 2) return;
    const id = setInterval(() => setNewsIdx(i => (i + 1) % items.length), NEWS_CYCLE_MS);
    return () => clearInterval(id);
  }, [items.length]);

  // ---------------- Dismiss handler ----------------
  const handleDismiss = useCallback((alert: Alert) => {
    dismissAlert(alert.id, alert.ttlSec);
    setAlerts(prev => prev.filter(a => a.id !== alert.id));
    setAlertIdx(0);
  }, []);

  // ---------------- Render ----------------
  const showAlert = alerts.length > 0;
  const currentAlert = showAlert ? alerts[Math.min(alertIdx, alerts.length - 1)] : null;
  const currentNews = items.length > 0 ? items[newsIdx] : null;

  if (!showAlert && (!newsLoaded || !currentNews)) return null;

  if (showAlert && currentAlert) {
    return (
      <div
        className="md:hidden w-full text-[var(--accent-violet)] relative overflow-hidden"
        style={{
          background: "color-mix(in srgb, var(--accent-violet) 14%, var(--bg))",
          borderBottom: "1px solid color-mix(in srgb, var(--accent-violet) 22%, transparent)",
        }}
      >
        {/* Pulsing violet left rail */}
        <span
          aria-hidden
          className="absolute left-0 top-0 bottom-0 w-[3px] animate-pulse"
          style={{ background: "var(--accent-violet)" }}
        />
        <div className="flex items-center gap-2 pl-3 pr-2 py-2 min-h-9">
          <a
            href={currentAlert.href}
            className="flex items-center gap-2 flex-1 min-w-0"
          >
            <span className="flex items-center gap-1 shrink-0 text-[10px] font-bold uppercase tracking-wider">
              <Bell size={12} />
              <span
                className="px-1.5 py-0.5 rounded-full text-[9px]"
                style={{ background: "color-mix(in srgb, var(--accent-violet) 18%, transparent)" }}
              >
                {t("alert.forYou", "Para ti")}
              </span>
              {alerts.length > 1 && (
                <span className="opacity-70">{alertIdx + 1}/{alerts.length}</span>
              )}
            </span>
            <div className="relative flex-1 h-4 overflow-hidden">
              <AnimatePresence mode="wait">
                <motion.p
                  key={currentAlert.id}
                  initial={{ y: 14, opacity: 0 }}
                  animate={{ y: 0, opacity: 1 }}
                  exit={{ y: -14, opacity: 0 }}
                  transition={{ duration: 0.35, ease: "easeOut" }}
                  className="absolute inset-0 text-xs leading-4 truncate font-semibold"
                >
                  <span aria-hidden className="mr-1">{currentAlert.emoji}</span>
                  {currentAlert.text}
                </motion.p>
              </AnimatePresence>
            </div>
            <ChevronRight size={14} className="shrink-0 opacity-70" />
          </a>
          <button
            type="button"
            onClick={(e) => { e.preventDefault(); e.stopPropagation(); handleDismiss(currentAlert); }}
            className="shrink-0 inline-flex items-center justify-center w-7 h-7 rounded-full hover:bg-[color-mix(in_srgb,var(--accent-violet)_18%,transparent)] transition-colors"
            aria-label={t("alert.dismiss", "Cerrar alerta")}
          >
            <X size={14} />
          </button>
        </div>
      </div>
    );
  }

  // News fallback (unchanged from original)
  if (!currentNews) return null;
  return (
    <div className="md:hidden w-full bg-[var(--ink)] text-white">
      <a
        href={currentNews.link}
        target="_blank"
        rel="noopener noreferrer"
        className="flex items-center gap-2 px-3 py-2 min-h-9"
      >
        <span className="flex items-center gap-1 shrink-0 text-[10px] font-bold uppercase tracking-wider text-[var(--accent-mint)]">
          <Newspaper size={12} />
          <span>{newsIdx + 1}/{items.length}</span>
        </span>
        <div className="relative flex-1 h-4 overflow-hidden">
          <AnimatePresence mode="wait">
            <motion.p
              key={newsIdx}
              initial={{ y: 14, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              exit={{ y: -14, opacity: 0 }}
              transition={{ duration: 0.35, ease: "easeOut" }}
              className="absolute inset-0 text-xs leading-4 truncate"
            >
              {currentNews.title}
              {currentNews.source && (
                <span className="text-white/50"> · {currentNews.source}</span>
              )}
            </motion.p>
          </AnimatePresence>
        </div>
        <ChevronRight size={14} className="shrink-0 text-white/60" />
      </a>
    </div>
  );
}

