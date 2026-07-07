"use client";

// Live-ish indicator of AVA's latest re-evaluation. Hits the public
// /api/ai/heartbeat endpoint, then renders either "just changed pick" if
// the most recent snapshot is within 30 minutes, or an idle "learning"
// state with a countdown to the next 6-hour cron tick.

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { Bot } from "lucide-react";
import { useLocale } from "@/lib/i18n";
import { useNow } from "@/lib/use-now";
import { usePlayer } from "@/lib/player-context";
import { useHomeSnapshot } from "@/lib/home-snapshot";

type Heartbeat = {
  ok: boolean;
  latest: {
    fixtureId: string;
    fixtureLabel: string;        // "MEX vs ARG"
    ts: number;
    pick: "H" | "D" | "A";
    prevPick: "H" | "D" | "A" | null;
    reasoning?: string;
  } | null;
};

const FRESH_WINDOW_MS = 30 * 60 * 1000; // 30 minutes
const CRON_HOURS_UTC = [0, 6, 12, 18];

function nextCronInMs(now: number): number {
  const next = new Date(now);
  // Round up to the next 6h UTC boundary.
  const hUtc = next.getUTCHours();
  let target = CRON_HOURS_UTC.find(h => h > hUtc) ?? (CRON_HOURS_UTC[0] + 24);
  next.setUTCHours(target, 0, 0, 0);
  return Math.max(0, next.getTime() - now);
}

function fmtHM(ms: number): string {
  const total = Math.max(0, Math.round(ms / 1000));
  const h = Math.floor(total / 3600);
  const m = Math.floor((total % 3600) / 60);
  return `${String(h).padStart(2, "0")}:${String(m).padStart(2, "0")}`;
}

const PICK_LABEL: Record<"H" | "D" | "A", string> = { H: "Local", D: "Empate", A: "Visitante" };

export function AvaThinkingChip() {
  const { t } = useLocale();
  const { currentPlayer } = usePlayer();
  const now = useNow(60_000);
  const snapshot = useHomeSnapshot();
  const snapshotLatest = snapshot?.data?.aiHeartbeat?.latest ?? null;
  const [fallback, setFallback] = useState<Heartbeat["latest"]>(null);

  // Snapshot wins. Fallback only when there's no provider (defensive — e.g.
  // future use on a non-home page).
  useEffect(() => {
    if (snapshot) return;
    let cancelled = false;
    fetch("/api/ai/heartbeat")
      .then(r => (r.ok ? r.json() : null))
      .then((j: Heartbeat | null) => {
        if (cancelled || !j?.ok) return;
        setFallback(j.latest);
      })
      .catch(() => {});
    return () => { cancelled = true; };
  }, [snapshot]);

  const data = snapshotLatest ?? fallback;

  const fresh = useMemo(() => {
    if (!data || now === null) return false;
    return now - data.ts < FRESH_WINDOW_MS;
  }, [data, now]);

  const isJesus = currentPlayer?.id === "jesus";
  const href = fresh && data
    ? (isJesus ? "/admin/ai-evolution" : `/partido/${data.fixtureId}`)
    : (isJesus ? "/admin/ai-evolution" : "/");

  const message = useMemo(() => {
    if (fresh && data) {
      const prev = data.prevPick ? PICK_LABEL[data.prevPick] : "—";
      const next = PICK_LABEL[data.pick];
      return t("ava.justChanged")
        .replace("{fixture}", data.fixtureLabel)
        .replace("{old}", prev)
        .replace("{new}", next);
    }
    const ms = now !== null ? nextCronInMs(now) : 0;
    return t("ava.learning").replace("{eta}", fmtHM(ms));
  }, [fresh, data, now, t]);

  return (
    <section className="container-app pt-2 pb-2">
      <Link
        href={href}
        className="block rounded-2xl px-4 py-3 ring-1 ring-[var(--line)] bg-[var(--bg-tint)] hover:bg-[var(--bg)] transition-colors"
      >
        <div className="flex items-center gap-3">
          <span
            className="relative inline-flex items-center justify-center w-8 h-8 rounded-full text-white"
            style={{ background: "linear-gradient(135deg, #0F172A, #5E5BFF)" }}
            aria-hidden
          >
            <Bot size={16} />
            <span
              className={`absolute inset-0 rounded-full ${fresh ? "animate-ping" : ""}`}
              style={{ background: fresh ? "rgba(94,91,255,0.35)" : "transparent" }}
            />
          </span>
          <div className="min-w-0 flex-1">
            <div className="text-[10px] uppercase tracking-wider text-[var(--ink-muted)] font-extrabold">
              {fresh ? t("ava.thinking") : "AVA"}
            </div>
            <div className="text-sm font-semibold text-[var(--ink)] truncate">
              {message}
            </div>
            {fresh && data?.reasoning && (
              <div className="text-[11px] text-[var(--ink-muted)] mt-0.5 line-clamp-1">
                {data.reasoning}
              </div>
            )}
          </div>
        </div>
      </Link>
    </section>
  );
}
