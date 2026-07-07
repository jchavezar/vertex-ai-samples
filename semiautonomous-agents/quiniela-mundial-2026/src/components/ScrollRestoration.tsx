"use client";

import { useEffect, useRef } from "react";
import { usePathname } from "next/navigation";

const KEY = (p: string) => `q26:scroll:${p}`;

export function ScrollRestoration() {
  const pathname = usePathname();
  // True when the current navigation was triggered by back/forward (popstate).
  const isPopRef = useRef(false);

  // Disable browser auto-scroll — we control it entirely.
  useEffect(() => {
    if ("scrollRestoration" in window.history) {
      window.history.scrollRestoration = "manual";
    }
  }, []);

  // Mark back/forward navigations BEFORE the pathname effect fires.
  useEffect(() => {
    const onPop = () => { isPopRef.current = true; };
    window.addEventListener("popstate", onPop);
    return () => window.removeEventListener("popstate", onPop);
  }, []);

  // Save scroll position on scroll (debounced 150ms).
  useEffect(() => {
    let tid: ReturnType<typeof setTimeout>;
    const save = () => {
      clearTimeout(tid);
      tid = setTimeout(() => {
        sessionStorage.setItem(KEY(pathname), String(Math.round(window.scrollY)));
      }, 150);
    };
    window.addEventListener("scroll", save, { passive: true });
    return () => {
      clearTimeout(tid);
      window.removeEventListener("scroll", save);
    };
  }, [pathname]);

  // Route change: restore saved position on back/forward, scroll to top on fresh nav.
  useEffect(() => {
    if (isPopRef.current) {
      isPopRef.current = false;
      const saved = sessionStorage.getItem(KEY(pathname));
      const targetY = saved ? parseInt(saved, 10) : 0;
      if (targetY <= 0) { window.scrollTo({ top: 0, behavior: "instant" }); return; }
      // Page content may still be loading — retry until tall enough (max ~500ms).
      let tries = 0;
      const attempt = () => {
        if (document.documentElement.scrollHeight >= targetY + window.innerHeight) {
          window.scrollTo({ top: targetY, behavior: "instant" });
        } else if (tries++ < 30) {
          requestAnimationFrame(attempt);
        }
      };
      requestAnimationFrame(attempt);
    } else {
      // Fresh link click → always start at top.
      window.scrollTo({ top: 0, behavior: "instant" });
    }
  }, [pathname]);

  // Bfcache restore (iOS Safari back swipe) — browser skips popstate entirely.
  useEffect(() => {
    const onPageShow = (e: PageTransitionEvent) => {
      if (!e.persisted) return;
      const saved = sessionStorage.getItem(KEY(window.location.pathname));
      const targetY = saved ? parseInt(saved, 10) : 0;
      if (targetY <= 0) return;
      setTimeout(() => window.scrollTo({ top: targetY, behavior: "instant" }), 50);
    };
    window.addEventListener("pageshow", onPageShow);
    return () => window.removeEventListener("pageshow", onPageShow);
  }, []);

  return null;
}
