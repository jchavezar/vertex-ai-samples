"use client";

import { useEffect, useState } from "react";
import { formatKickoffTime, formatKickoffDate, type KickoffShape } from "@/lib/fixture-time";

// Renders kickoff time/date in the viewer's browser timezone. Mount-gated to
// avoid SSR (UTC) -> client hydration mismatch: until mount we show the
// stadium-local time from the feed, which both server and client agree on.
export function ViewerKickoffTime({ fx }: { fx: KickoffShape }) {
  const [mounted, setMounted] = useState(false);
  useEffect(() => { setMounted(true); }, []);
  return <>{mounted ? formatKickoffTime(fx) : fx.kickoffLocal}</>;
}

export function ViewerKickoffDate({ fx }: { fx: KickoffShape }) {
  const [mounted, setMounted] = useState(false);
  useEffect(() => { setMounted(true); }, []);
  if (!mounted) {
    const mo = fx.date.slice(5, 7);
    const d = fx.date.slice(8, 10);
    return <>{`${mo}/${d}`}</>;
  }
  return <>{formatKickoffDate(fx)}</>;
}
