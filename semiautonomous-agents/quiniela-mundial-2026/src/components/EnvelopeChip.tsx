"use client";

// Small floating chip rendered near the top of the home hero. Polls
// /api/envelope/today to know if the user's daily envelope is available or
// already opened. Click → /sobre for the full reveal experience.

import Link from "next/link";
import { useEffect, useState } from "react";
import { Mail, CheckCircle2 } from "lucide-react";
import { useLocale } from "@/lib/i18n";
import { usePlayer } from "@/lib/player-context";

type State =
  | { kind: "loading" }
  | { kind: "anonymous" }
  | { kind: "available"; countdownUntilMs: number }
  | { kind: "opened"; countdownUntilMs: number; rewardType: string };

function formatCountdown(ms: number): string {
  if (ms <= 0) return "0m";
  const totalMin = Math.floor(ms / 60_000);
  const h = Math.floor(totalMin / 60);
  const m = totalMin % 60;
  if (h <= 0) return `${m}m`;
  return `${h}h ${m}m`;
}

export function EnvelopeChip() {
  const { t } = useLocale();
  const { currentPlayer } = usePlayer();
  const [state, setState] = useState<State>({ kind: "loading" });

  useEffect(() => {
    let cancelled = false;
    if (!currentPlayer) {
      setState({ kind: "anonymous" });
      return () => { cancelled = true; };
    }
    setState({ kind: "loading" });
    fetch("/api/envelope/today", { cache: "no-store" })
      .then(r => r.ok ? r.json() : null)
      .then(j => {
        if (cancelled || !j?.ok) return;
        if (j.opened) {
          setState({
            kind: "opened",
            countdownUntilMs: j.countdownUntilMs ?? 0,
            rewardType: j.reward?.type ?? "visual",
          });
        } else {
          setState({ kind: "available", countdownUntilMs: j.countdownUntilMs ?? 0 });
        }
      })
      .catch(() => { /* keep loading */ });
    return () => { cancelled = true; };
  }, [currentPlayer]);

  // Live tick the countdown every minute.
  useEffect(() => {
    if (state.kind !== "available" && state.kind !== "opened") return;
    const id = setInterval(() => {
      setState(prev => {
        if (prev.kind !== "available" && prev.kind !== "opened") return prev;
        const remaining = Math.max(0, prev.countdownUntilMs - 60_000);
        return { ...prev, countdownUntilMs: remaining };
      });
    }, 60_000);
    return () => clearInterval(id);
  }, [state.kind]);

  if (state.kind === "loading" || state.kind === "anonymous") return null;

  if (state.kind === "available") {
    return (
      <Link
        href="/sobre"
        className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider ring-1 ring-[#7C3AED]/40 shadow-sm hover:-translate-y-0.5 transition-transform"
        style={{
          background: "linear-gradient(135deg, #EDE9FE 0%, #C4B5FD 60%, #7C3AED 100%)",
          color: "#1a0b3a",
        }}
        title={t("envelope.title")}
      >
        <Mail size={12} className="-mt-0.5" />
        <span className="hidden sm:inline">{t("envelope.title")}</span>
        <span className="opacity-70">·</span>
        <span>{t("envelope.available")}</span>
      </Link>
    );
  }

  // opened
  return (
    <Link
      href="/sobre"
      className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider ring-1 ring-[#14B8A6]/40 shadow-sm hover:-translate-y-0.5 transition-transform bg-white/80"
      style={{ color: "#08291f" }}
      title={t("envelope.openedToday")}
    >
      <CheckCircle2 size={12} className="-mt-0.5" />
      <span className="hidden sm:inline">{t("envelope.title")}</span>
      <span className="opacity-70">·</span>
      <span className="normal-case tracking-normal">{t("envelope.countdown")}</span>
      <span className="tabular-nums">{formatCountdown(state.countdownUntilMs)}</span>
    </Link>
  );
}
