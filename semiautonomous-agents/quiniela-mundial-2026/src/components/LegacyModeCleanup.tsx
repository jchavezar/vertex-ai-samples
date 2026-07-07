"use client";

import { useEffect } from "react";

export function LegacyModeCleanup() {
  useEffect(() => {
    try {
      window.localStorage.removeItem("q26_mode");
      window.localStorage.removeItem("q26_theme");
      window.localStorage.removeItem("q26:nba-predictions");
      document.documentElement.removeAttribute("data-theme");
    } catch {}
  }, []);
  return null;
}
