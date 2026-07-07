"use client";

import { useEffect } from "react";

export function LegacyModeCleanup() {
  useEffect(() => {
    try {
      window.localStorage.removeItem("q26_mode");
      window.localStorage.removeItem("q26:nba-predictions");
    } catch {}
  }, []);
  return null;
}
