"use client";

// Aggressive 3-stage push activation flow. Replaces the single PushPrompt
// nudge that wasn't converting (0 push devices subscribed despite VAPID
// being wired). Stages:
//
//   A. <PushActivationModal /> — post-login modal (one-shot per playerId,
//      with 24h snooze on dismiss).
//   B. <PushActivationNag />   — slim sticky banner under the nav, persistent
//      whenever the logged-in user has no live subscription and snooze is
//      expired. Mount once in the root layout.
//   C. <PushActivationInline placement="quiniela" /> — in-page note rendered
//      inside the quiniela when the user still has unfilled picks. One-shot
//      per session.
//
// All three call the same `subscribeToPush` from push-client, so a single
// permission grant on any surface upgrades every other surface in real time.
//
// localStorage keys used here (so the cron + owner know what to inspect):
//   q26:push-modal-shown:<playerId>   — set after first modal render
//   q26:push-snooze-until              — epoch ms, set on Después / X
//   q26:push-inline-shown:<page>       — sessionStorage one-shot key

import { useCallback, useEffect, useMemo, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { Bell, Trophy, Goal, Clock, X } from "lucide-react";
import {
  currentPermission,
  getActiveSubscription,
  isPushSupported,
  subscribeToPush,
} from "@/lib/push-client";
import { usePlayer } from "@/lib/player-context";
import { track } from "@/lib/track";

const VAPID = process.env.NEXT_PUBLIC_VAPID_PUBLIC_KEY || "";
const SNOOZE_MS = 24 * 60 * 60 * 1000;

const SNOOZE_KEY = "q26:push-snooze-until";
const modalShownKey = (playerId: string) => `q26:push-modal-shown:${playerId}`;
const inlineShownKey = (placement: string) => `q26:push-inline-shown:${placement}`;

function readSnoozeUntil(): number {
  if (typeof window === "undefined") return 0;
  try {
    const v = Number(localStorage.getItem(SNOOZE_KEY) ?? "0");
    return Number.isFinite(v) ? v : 0;
  } catch {
    return 0;
  }
}

function writeSnooze(): void {
  if (typeof window === "undefined") return;
  try {
    localStorage.setItem(SNOOZE_KEY, String(Date.now() + SNOOZE_MS));
  } catch {
    /* quota / private mode — fail silent */
  }
}

function isSnoozed(): boolean {
  return readSnoozeUntil() > Date.now();
}

function clearSnooze(): void {
  if (typeof window === "undefined") return;
  try { localStorage.removeItem(SNOOZE_KEY); } catch {}
}

// Async hook that tracks whether the device currently holds a live push
// subscription. Re-checks on visibility change so the banner disappears the
// moment the user grants permission from another surface.
function useSubscriptionState(): {
  supported: boolean;
  permission: NotificationPermission | "unsupported";
  subscribed: boolean | null; // null = unknown / still loading
  refresh: () => void;
} {
  const [supported, setSupported] = useState(false);
  const [permission, setPermission] = useState<NotificationPermission | "unsupported">("default");
  const [subscribed, setSubscribed] = useState<boolean | null>(null);
  const [tick, setTick] = useState(0);

  const refresh = useCallback(() => setTick(n => n + 1), []);

  useEffect(() => {
    let alive = true;
    (async () => {
      const ok = isPushSupported() && !!VAPID;
      if (!alive) return;
      setSupported(ok);
      if (!ok) {
        setPermission("unsupported");
        setSubscribed(false);
        return;
      }
      setPermission(currentPermission());
      const sub = await getActiveSubscription();
      if (!alive) return;
      setSubscribed(!!sub);
    })();
    return () => { alive = false; };
  }, [tick]);

  useEffect(() => {
    if (typeof document === "undefined") return;
    const onVis = () => { if (document.visibilityState === "visible") refresh(); };
    document.addEventListener("visibilitychange", onVis);
    return () => document.removeEventListener("visibilitychange", onVis);
  }, [refresh]);

  return { supported, permission, subscribed, refresh };
}

// ============================== STAGE A ==============================

export function PushActivationModal() {
  const { currentPlayer, ready } = usePlayer();
  const { supported, permission, subscribed, refresh } = useSubscriptionState();
  const [open, setOpen] = useState(false);
  const [busy, setBusy] = useState(false);

  // Decide whether to auto-open on first login. Runs as soon as
  // PlayerProvider says we're ready AND we know the subscription state.
  useEffect(() => {
    if (!ready || !currentPlayer) return;
    if (!supported) return;
    if (subscribed !== false) return;        // already subscribed or unknown
    if (permission === "denied") return;     // can't re-prompt anyway
    if (isSnoozed()) return;

    const key = modalShownKey(currentPlayer.id);
    try {
      if (localStorage.getItem(key) === "1") return;
      localStorage.setItem(key, "1");
    } catch { /* private mode → still show once per page load */ }

    setOpen(true);
    track("push_modal_shown", { playerId: currentPlayer.id });
  }, [ready, currentPlayer, supported, subscribed, permission]);

  async function activate() {
    if (busy) return;
    setBusy(true);
    try {
      const r = await subscribeToPush(VAPID);
      if (r.ok) {
        track("push_subscribed", { source: "modal" });
        clearSnooze();
        setOpen(false);
        refresh();
      } else if (r.reason === "denied") {
        track("push_denied", { source: "modal" });
        writeSnooze();
        setOpen(false);
      } else {
        track("push_subscribe_failed", { source: "modal", reason: r.reason });
      }
    } finally {
      setBusy(false);
    }
  }

  function later() {
    track("push_snoozed", { source: "modal" });
    writeSnooze();
    setOpen(false);
  }

  return (
    <AnimatePresence>
      {open && (
        <motion.div
          key="push-modal-backdrop"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 z-[60] flex items-end md:items-center justify-center px-4 py-6 bg-black/55 backdrop-blur-sm"
          onClick={later}
        >
          <motion.div
            key="push-modal"
            initial={{ y: 40, opacity: 0, scale: 0.96 }}
            animate={{ y: 0, opacity: 1, scale: 1 }}
            exit={{ y: 40, opacity: 0, scale: 0.96 }}
            transition={{ type: "spring", stiffness: 300, damping: 30 }}
            onClick={(e) => e.stopPropagation()}
            className="relative w-full max-w-md glass-strong rounded-3xl p-6 md:p-7 shadow-2xl"
            style={{ borderColor: "color-mix(in srgb, var(--accent-violet) 35%, transparent)" }}
          >
            <button
              type="button"
              onClick={later}
              aria-label="Cerrar"
              className="absolute top-3 right-3 w-8 h-8 rounded-full flex items-center justify-center text-[var(--ink-muted)] hover:bg-[var(--bg-tint)]"
            >
              <X size={16} />
            </button>

            <div className="flex items-center gap-3 mb-4">
              <div
                className="w-12 h-12 rounded-2xl flex items-center justify-center shrink-0"
                style={{
                  background: "color-mix(in srgb, var(--accent-violet) 20%, transparent)",
                  color: "var(--accent-violet)",
                }}
              >
                <Bell size={22} />
              </div>
              <div className="min-w-0">
                <div className="text-[10px] uppercase tracking-[0.18em] text-[var(--ink-muted)] font-semibold">
                  Charales 26
                </div>
                <h2 className="font-display text-xl md:text-2xl font-bold leading-tight">
                  Avísame cuando juegue mi pick
                </h2>
              </div>
            </div>

            <p className="text-sm text-[var(--ink-soft)] mb-4">
              Te mando un ping al teléfono solo para lo que importa:
            </p>

            <ul className="space-y-2.5 mb-5">
              <li className="flex items-start gap-3">
                <Goal size={16} className="mt-0.5 shrink-0 text-[var(--accent-mint)]" />
                <span className="text-sm text-[var(--ink)]">
                  <strong>Gol</strong> en un partido donde tu pick está vivo.
                </span>
              </li>
              <li className="flex items-start gap-3">
                <Clock size={16} className="mt-0.5 shrink-0 text-[var(--accent-violet)]" />
                <span className="text-sm text-[var(--ink)]">
                  <strong>2h antes</strong> de cada partido sin pick — pa&apos; que no se cierre.
                </span>
              </li>
              <li className="flex items-start gap-3">
                <Trophy size={16} className="mt-0.5 shrink-0 text-[#D4AF37]" />
                <span className="text-sm text-[var(--ink)]">
                  Cuando <strong>te pasen</strong> en el leaderboard.
                </span>
              </li>
            </ul>

            <div className="flex flex-col-reverse sm:flex-row gap-3 sm:justify-end">
              <button
                type="button"
                onClick={later}
                className="text-sm font-semibold text-[var(--ink-muted)] hover:text-[var(--ink)] px-3 py-2"
              >
                Después
              </button>
              <button
                type="button"
                onClick={activate}
                disabled={busy}
                className="px-5 h-11 rounded-full font-bold text-sm shrink-0 transition-transform hover:scale-[1.02] disabled:opacity-60"
                style={{ background: "var(--accent-violet)", color: "#0a0a0c" }}
              >
                {busy ? "Activando..." : "Activar notificaciones"}
              </button>
            </div>

            <p className="text-[10px] text-[var(--ink-muted)] mt-4 text-center">
              Puedes desactivarlas cuando quieras desde la configuración del navegador.
            </p>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}

// ============================== STAGE B ==============================

export function PushActivationNag() {
  const { currentPlayer, ready } = usePlayer();
  const { supported, permission, subscribed, refresh } = useSubscriptionState();
  const [snoozedUntil, setSnoozedUntil] = useState(() => readSnoozeUntil());
  const [busy, setBusy] = useState(false);

  // Re-read snooze on visibility (other tab might have snoozed).
  useEffect(() => {
    const onVis = () => setSnoozedUntil(readSnoozeUntil());
    if (typeof document === "undefined") return;
    document.addEventListener("visibilitychange", onVis);
    return () => document.removeEventListener("visibilitychange", onVis);
  }, []);

  const shouldShow = useMemo(() => {
    if (!ready || !currentPlayer) return false;
    if (!supported) return false;
    if (permission === "denied") return false;
    if (subscribed !== false) return false;
    if (snoozedUntil > Date.now()) return false;
    return true;
  }, [ready, currentPlayer, supported, permission, subscribed, snoozedUntil]);

  async function activate() {
    if (busy) return;
    setBusy(true);
    try {
      const r = await subscribeToPush(VAPID);
      if (r.ok) {
        track("push_subscribed", { source: "nag" });
        clearSnooze();
        setSnoozedUntil(0);
        refresh();
      } else if (r.reason === "denied") {
        track("push_denied", { source: "nag" });
        writeSnooze();
        setSnoozedUntil(readSnoozeUntil());
      }
    } finally {
      setBusy(false);
    }
  }

  function snooze() {
    track("push_snoozed", { source: "nag" });
    writeSnooze();
    setSnoozedUntil(readSnoozeUntil());
  }

  if (!shouldShow) return null;

  return (
    <div className="container-app pt-2">
      <div
        className="glass rounded-full pl-4 pr-2 py-1.5 flex items-center gap-2 text-xs"
        style={{ borderColor: "color-mix(in srgb, var(--accent-violet) 35%, transparent)" }}
      >
        <Bell size={14} className="shrink-0 text-[var(--accent-violet)]" />
        <span className="flex-1 min-w-0 truncate text-[var(--ink-soft)]">
          <span className="hidden sm:inline">Activa notificaciones para no perderte goles, picks y cambios en la tabla.</span>
          <span className="sm:hidden">No te pierdas un gol o un pick.</span>
        </span>
        <button
          type="button"
          onClick={activate}
          disabled={busy}
          className="shrink-0 px-3 h-8 rounded-full font-bold text-[11px] transition-transform hover:scale-[1.02] disabled:opacity-60"
          style={{ background: "var(--accent-violet)", color: "#0a0a0c" }}
        >
          {busy ? "..." : "Activar"}
        </button>
        <button
          type="button"
          onClick={snooze}
          aria-label="Después"
          className="shrink-0 w-7 h-7 rounded-full flex items-center justify-center text-[var(--ink-muted)] hover:bg-[var(--bg-tint)]"
        >
          <X size={13} />
        </button>
      </div>
    </div>
  );
}

// ============================== STAGE C ==============================

export function PushActivationInline({ placement }: { placement: string }) {
  const { currentPlayer, ready } = usePlayer();
  const { supported, permission, subscribed, refresh } = useSubscriptionState();
  const [hidden, setHidden] = useState(false);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    if (typeof sessionStorage === "undefined") return;
    try {
      if (sessionStorage.getItem(inlineShownKey(placement)) === "1") setHidden(true);
    } catch {}
  }, [placement]);

  const shouldShow =
    ready &&
    !!currentPlayer &&
    supported &&
    permission !== "denied" &&
    subscribed === false &&
    !hidden;

  // Record "shown" once per session (separate from snooze so the inline
  // nudge stops repeating across nav within the same tab).
  useEffect(() => {
    if (!shouldShow) return;
    try { sessionStorage.setItem(inlineShownKey(placement), "1"); } catch {}
    track("push_inline_shown", { placement });
  }, [shouldShow, placement]);

  async function activate() {
    if (busy) return;
    setBusy(true);
    try {
      const r = await subscribeToPush(VAPID);
      if (r.ok) {
        track("push_subscribed", { source: `inline:${placement}` });
        clearSnooze();
        refresh();
        setHidden(true);
      } else if (r.reason === "denied") {
        track("push_denied", { source: `inline:${placement}` });
        writeSnooze();
        setHidden(true);
      }
    } finally {
      setBusy(false);
    }
  }

  function dismiss() {
    setHidden(true);
  }

  if (!shouldShow) return null;

  return (
    <div
      className="glass-strong rounded-2xl px-4 py-3 flex items-center gap-3 my-4"
      style={{ borderColor: "color-mix(in srgb, var(--accent-violet) 30%, transparent)" }}
    >
      <div
        className="w-9 h-9 rounded-xl flex items-center justify-center shrink-0"
        style={{
          background: "color-mix(in srgb, var(--accent-violet) 18%, transparent)",
          color: "var(--accent-violet)",
        }}
      >
        <Bell size={16} />
      </div>
      <div className="flex-1 min-w-0">
        <div className="text-sm font-semibold text-[var(--ink)] leading-tight">
          Activa notificaciones
        </div>
        <div className="text-xs text-[var(--ink-muted)] mt-0.5">
          Te recordamos 2h antes de cada partido para que no se te pase un pick.
        </div>
      </div>
      <button
        type="button"
        onClick={activate}
        disabled={busy}
        className="shrink-0 px-3 h-9 rounded-full font-bold text-xs transition-transform hover:scale-[1.02] disabled:opacity-60"
        style={{ background: "var(--accent-violet)", color: "#0a0a0c" }}
      >
        {busy ? "..." : "Activar"}
      </button>
      <button
        type="button"
        onClick={dismiss}
        aria-label="Ahora no"
        className="shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-[var(--ink-muted)] hover:bg-[var(--bg-tint)]"
      >
        <X size={14} />
      </button>
    </div>
  );
}
