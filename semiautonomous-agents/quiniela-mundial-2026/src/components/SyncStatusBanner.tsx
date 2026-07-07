"use client";

// Surfaces predictions-sync failures so a 401/500 doesn't silently lose data.
//
// Backstory: 2026-06-16 Jochabe's USA pick never reached Firestore because his
// cookie expired between picking and the debounced PUT. The sync emitted an
// `unauthorized` event into the void — nothing rendered it, so he had no idea
// his picks were going nowhere. This banner reads that event stream.

import { useCallback, useEffect, useState } from "react";
import { AlertTriangle, LogIn, X } from "lucide-react";
import type { SyncEvent } from "@/lib/predictions";
import { useLocale } from "@/lib/i18n";

type BannerState =
  | { kind: "hidden" }
  | { kind: "auth"; playerId: string }
  | { kind: "error"; playerId: string; error: string };

export function SyncStatusBanner() {
  const [state, setState] = useState<BannerState>({ kind: "hidden" });
  const [dismissed, setDismissed] = useState(false);
  const { t } = useLocale();

  useEffect(() => {
    function onSync(e: Event) {
      const detail = (e as CustomEvent<SyncEvent>).detail;
      if (!detail) return;
      if (detail.status === "unauthorized") {
        setDismissed(false);
        setState({ kind: "auth", playerId: detail.playerId });
      } else if (detail.status === "error") {
        setDismissed(false);
        setState({ kind: "error", playerId: detail.playerId, error: detail.error ?? "" });
      } else if (detail.status === "ok") {
        // Success after retry → clear the banner automatically.
        setState({ kind: "hidden" });
      }
    }
    window.addEventListener("q26:predictions-sync", onSync as EventListener);
    return () => window.removeEventListener("q26:predictions-sync", onSync as EventListener);
  }, []);

  const openLogin = useCallback(() => {
    window.dispatchEvent(new CustomEvent("q26:open-chat"));
  }, []);

  if (state.kind === "hidden" || dismissed) return null;

  const isAuth = state.kind === "auth";
  return (
    <div
      role="alert"
      aria-live="polite"
      className="fixed top-2 inset-x-2 sm:top-3 sm:left-1/2 sm:-translate-x-1/2 sm:inset-x-auto sm:max-w-md z-[60] rounded-2xl shadow-xl border px-3 py-2.5 flex items-start gap-2"
      style={{
        background: isAuth
          ? "color-mix(in srgb, #FBBF24 18%, var(--bg-strong, white))"
          : "color-mix(in srgb, #EF4444 18%, var(--bg-strong, white))",
        borderColor: isAuth ? "#F59E0B" : "#DC2626",
        color: isAuth ? "#7C2D12" : "#7F1D1D",
      }}
    >
      <AlertTriangle size={16} className="shrink-0 mt-0.5" />
      <div className="flex-1 min-w-0 text-[12px] leading-snug">
        {isAuth ? (
          <>
            <strong>{t("sync.auth.title")}</strong>{" "}
            {t("sync.auth.copy")}
            <button
              type="button"
              onClick={openLogin}
              className="ml-2 inline-flex items-center gap-1 px-2 py-0.5 rounded-full font-bold text-[11px] bg-amber-600 text-white hover:bg-amber-700"
            >
              <LogIn size={11} /> {t("sync.auth.cta")}
            </button>
          </>
        ) : (
          <>
            <strong>{t("sync.error.title")}</strong>{" "}
            {t("sync.error.copy")}
            {state.kind === "error" && state.error && (
              <span className="block text-[10px] opacity-70 mt-0.5 truncate">{state.error}</span>
            )}
          </>
        )}
      </div>
      <button
        type="button"
        aria-label={t("sync.close")}
        onClick={() => setDismissed(true)}
        className="shrink-0 -mr-1 -mt-0.5 p-1 rounded hover:bg-black/5"
      >
        <X size={14} />
      </button>
    </div>
  );
}
