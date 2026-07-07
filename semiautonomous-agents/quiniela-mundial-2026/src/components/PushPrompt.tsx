"use client";

/**
 * @deprecated Replaced by `<PushActivationModal />`, `<PushActivationNag />`
 * and `<PushActivationInline />` from `src/components/PushActivationFlow.tsx`.
 * The single-shot inline prompt wasn't converting (0/10 charales subscribed
 * as of 2026-06-16). Safe to delete once the new flow is verified live.
 */

import { useEffect, useState } from "react";
import { Bell, BellOff, Check } from "lucide-react";
import {
  currentPermission,
  getActiveSubscription,
  isPushSupported,
  subscribeToPush,
  unsubscribeFromPush,
} from "@/lib/push-client";
import { track } from "@/lib/track";

type Status = "loading" | "unsupported" | "off" | "denied" | "on";

const VAPID = process.env.NEXT_PUBLIC_VAPID_PUBLIC_KEY || "";

export function PushPrompt() {
  const [status, setStatus] = useState<Status>("loading");
  const [busy, setBusy] = useState(false);
  const [dismissed, setDismissed] = useState(false);

  useEffect(() => {
    let alive = true;
    (async () => {
      if (!isPushSupported() || !VAPID) {
        if (alive) setStatus("unsupported");
        return;
      }
      const perm = currentPermission();
      if (perm === "denied") {
        if (alive) setStatus("denied");
        return;
      }
      const sub = await getActiveSubscription();
      if (!alive) return;
      setStatus(sub ? "on" : "off");
    })();
    return () => { alive = false; };
  }, []);

  useEffect(() => {
    try {
      if (sessionStorage.getItem("q26:push-prompt-dismissed") === "1") setDismissed(true);
    } catch {}
  }, []);

  if (status === "loading" || status === "unsupported" || dismissed) return null;
  if (status === "denied") return null;

  async function enable() {
    setBusy(true);
    try {
      const r = await subscribeToPush(VAPID);
      if (r.ok) { setStatus("on"); track("push_subscribed"); }
      else if (r.reason === "denied") setStatus("denied");
    } finally {
      setBusy(false);
    }
  }

  async function disable() {
    setBusy(true);
    try {
      await unsubscribeFromPush();
      setStatus("off");
    } finally {
      setBusy(false);
    }
  }

  function dismissOnce() {
    setDismissed(true);
    try { sessionStorage.setItem("q26:push-prompt-dismissed", "1"); } catch {}
  }

  if (status === "on") {
    return (
      <div className="container-app pt-2">
        <button
          type="button"
          onClick={disable}
          disabled={busy}
          className="chip w-full md:w-auto justify-center gap-2"
          style={{ color: "var(--accent-emerald)" }}
        >
          <Check size={12} /> Notificaciones activas · tocar para desactivar
        </button>
      </div>
    );
  }

  return (
    <div className="container-app pt-2">
      <div
        className="glass rounded-2xl p-3 flex items-center gap-3"
        style={{ borderColor: "color-mix(in srgb, var(--accent-violet) 35%, transparent)" }}
      >
        <div
          className="w-9 h-9 rounded-full flex items-center justify-center shrink-0"
          style={{ background: "color-mix(in srgb, var(--accent-violet) 18%, transparent)", color: "var(--accent-violet)" }}
        >
          <Bell size={16} />
        </div>
        <div className="min-w-0 flex-1">
          <div className="text-sm font-semibold text-[var(--ink)]">Avísame antes de cada partido</div>
          <div className="text-xs text-[var(--ink-muted)]">Te ping cuando se cierran los picks y cuando hay marcador.</div>
        </div>
        <button
          type="button"
          onClick={enable}
          disabled={busy}
          className="px-3 h-9 rounded-full font-semibold text-xs shrink-0"
          style={{ background: "var(--accent-violet)", color: "#0a0a0c" }}
        >
          {busy ? "..." : "Activar"}
        </button>
        <button
          type="button"
          onClick={dismissOnce}
          className="w-8 h-8 rounded-full flex items-center justify-center text-[var(--ink-muted)] shrink-0"
          aria-label="Ahora no"
        >
          <BellOff size={14} />
        </button>
      </div>
    </div>
  );
}
