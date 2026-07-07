"use client";

import { useEffect } from "react";

const BUILD = process.env.NEXT_PUBLIC_BUILD_HASH ?? "";
const VERSION_POLL_MS = 5 * 60 * 1000; // 5 min

export function SwRegister() {
  useEffect(() => {
    if (typeof window === "undefined") return;
    if (process.env.NODE_ENV !== "production") return;

    // ── SW update cycle ──────────────────────────────────────────────────────
    // When the SW activates a new cache version it sends q26-sw-updated.
    // We reload once per cache version so phones on stale bundles pick up new
    // code automatically.
    const onMessage = (evt: MessageEvent) => {
      const data = evt.data as { type?: string; cache?: string } | null;
      if (!data || data.type !== "q26-sw-updated") return;
      try {
        const marker = `q26.sw.reloaded.${data.cache ?? ""}`;
        if (sessionStorage.getItem(marker)) return;
        sessionStorage.setItem(marker, "1");
      } catch { /* private mode */ }
      window.location.reload();
    };

    if ("serviceWorker" in navigator) {
      navigator.serviceWorker.addEventListener("message", onMessage);
      const onLoad = () => {
        navigator.serviceWorker
          .register("/sw.js", { scope: "/", updateViaCache: "none" })
          .then(reg => reg.update().catch(() => {}))
          .catch(() => {});
      };
      window.addEventListener("load", onLoad);
    }

    // ── Build-hash version poller ────────────────────────────────────────────
    // Every 5 min fetch /api/version. If the server reports a different build
    // hash than the one baked into this bundle, the SW didn't manage to reload
    // us (e.g. cached HTML + old bundles). Force a hard reload.
    // Guard: only reload once per session to avoid loops.
    if (!BUILD) return;
    const RELOAD_MARKER = `q26.ver.reloaded.${BUILD}`;

    const checkVersion = async () => {
      try {
        const r = await fetch("/api/version", { cache: "no-store" });
        if (!r.ok) return;
        const { build } = await r.json() as { build?: string };
        if (!build || build === BUILD) return;
        // Server has a newer build — reload once
        try {
          if (sessionStorage.getItem(RELOAD_MARKER)) return;
          sessionStorage.setItem(RELOAD_MARKER, "1");
        } catch {}
        window.location.reload();
      } catch {}
    };

    // First check: 10s after mount (give SW time to finish its own reload if needed)
    const initial = setTimeout(checkVersion, 10_000);
    const interval = setInterval(checkVersion, VERSION_POLL_MS);

    return () => {
      clearTimeout(initial);
      clearInterval(interval);
      if ("serviceWorker" in navigator) {
        navigator.serviceWorker.removeEventListener("message", onMessage);
      }
    };
  }, []);

  return null;
}
