"use client";

// Drama spotlight: when ESPN reports a "hot" play (VAR review / red card /
// penalty awarded) on an in-progress fixture, elevate it above the
// NextWhistleCard with a pulsing red urgency banner. Polls `/api/live/drama`
// every 30s — and ONLY while at least one match is in `phase==="live"`
// (otherwise idle).
//
// Auto-disappears when:
//   - the API returns `hit: null` (play resolved / staled out)
//   - 90s elapse since detection (client safety net)

import Image from "next/image";
import { useEffect, useMemo, useState } from "react";
import { AlertTriangle } from "lucide-react";
import { useLiveScoreboard } from "@/lib/live-scoreboard";
import { TEAMS, flagUrl } from "@/data/teams";
import { useLocale } from "@/lib/i18n";
import type { DramaResponse, DramaHit } from "@/app/api/live/drama/route";

const CATEGORY_EMOJI: Record<DramaHit["category"], string> = {
  var: "🚨",
  red: "🟥",
  penalty: "🅿️",
};

export function DramaSpotlight() {
  const { byId } = useLiveScoreboard();
  const { t } = useLocale();
  const [hit, setHit] = useState<DramaHit | null>(null);
  const [now, setNow] = useState<number>(() => Date.now());

  const anyLive = useMemo(
    () => Object.values(byId).some(f => f.phase === "live"),
    [byId],
  );

  // Poll only when something is actually live. Otherwise the spotlight stays
  // hidden and we don't hammer ESPN.
  useEffect(() => {
    if (!anyLive) {
      setHit(null);
      return;
    }
    let alive = true;
    const fetchOnce = async () => {
      try {
        const r = await fetch("/api/live/drama", { cache: "no-store" });
        if (!r.ok) return;
        const j = (await r.json()) as DramaResponse;
        if (!alive) return;
        setHit(j.ok ? j.hit : null);
      } catch { /* ignore — try again next tick */ }
    };
    fetchOnce();
    const poll = setInterval(fetchOnce, 15_000);
    const tick = setInterval(() => setNow(Date.now()), 5_000);
    return () => { alive = false; clearInterval(poll); clearInterval(tick); };
  }, [anyLive]);

  if (!hit) return null;
  // Client-side safety: 90s after detection, clear it visually even if the
  // next poll hasn't run yet.
  if (now - hit.detectedAt > 45_000) return null;

  const home = TEAMS.find(t => t.code === hit.fixture.home);
  const away = TEAMS.find(t => t.code === hit.fixture.away);
  const matchLabel = `${hit.fixture.home} vs ${hit.fixture.away}`;
  const categoryKey: Record<DramaHit["category"], string> = {
    var: "live.dramaVAR",
    red: "live.dramaRed",
    penalty: "live.dramaPK",
  };
  const headline = t(categoryKey[hit.category]);

  return (
    <div
      className="relative overflow-hidden rounded-3xl p-4 md:p-5 animate-pulse"
      style={{
        background: "linear-gradient(135deg, rgba(255,59,130,0.95), rgba(225,29,72,0.92))",
        boxShadow: "0 12px 40px rgba(255,59,130,0.45), 0 0 0 1px rgba(255,255,255,0.15)",
        color: "white",
      }}
      role="alert"
      aria-live="assertive"
    >
      <div className="absolute -top-10 -right-10 w-40 h-40 rounded-full" style={{ background: "radial-gradient(closest-side, rgba(255,255,255,0.30), transparent)" }} />
      <div className="relative">
        <div className="flex items-center gap-2 mb-2">
          <span className="inline-flex items-center gap-1 text-[10px] uppercase tracking-[0.2em] font-extrabold px-2 py-0.5 rounded-full" style={{ background: "rgba(255,255,255,0.18)" }}>
            <AlertTriangle size={11} /> EN VIVO
          </span>
          <span className="text-[10px] uppercase tracking-[0.15em] opacity-85 truncate">
            Grupo {hit.fixture.group} · J{hit.fixture.matchday}
          </span>
        </div>

        <div className="font-display text-lg md:text-2xl font-extrabold leading-tight">
          <span className="mr-2">{CATEGORY_EMOJI[hit.category]}</span>
          {headline} en {matchLabel}
          {hit.minute ? <span className="opacity-85"> · {hit.minute}</span> : null}
        </div>

        {hit.text && (
          <div className="text-sm md:text-base opacity-95 mt-1 line-clamp-2">
            {hit.text}
          </div>
        )}

        <div className="mt-3 flex items-center gap-3">
          <div className="flex items-center gap-1.5">
            {home && (
              <span className="relative w-6 h-6 rounded overflow-hidden ring-1 ring-white/40">
                <Image src={flagUrl(home.iso2, 48)} alt={home.name} fill sizes="24px" className="object-cover" unoptimized />
              </span>
            )}
            <span className="font-display text-base font-bold tabular-nums">{hit.homeScore}</span>
          </div>
          <span className="opacity-70 text-sm">·</span>
          <div className="flex items-center gap-1.5">
            <span className="font-display text-base font-bold tabular-nums">{hit.awayScore}</span>
            {away && (
              <span className="relative w-6 h-6 rounded overflow-hidden ring-1 ring-white/40">
                <Image src={flagUrl(away.iso2, 48)} alt={away.name} fill sizes="24px" className="object-cover" unoptimized />
              </span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
