"use client";

import { useLiveScoreboard } from "@/lib/live-scoreboard";
import type { RealResults } from "@/lib/standings";

export function useGroupRealResults(): { results: RealResults; loading: boolean } {
  const { finals, loading } = useLiveScoreboard();
  return { results: finals, loading };
}
