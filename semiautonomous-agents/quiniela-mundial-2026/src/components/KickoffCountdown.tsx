"use client";

import { useEffect, useState } from "react";
import { Clock, Zap } from "lucide-react";

type Props = {
  kickoff: Date;
  /** When true, show "Iniciado" instead of nothing after kickoff. */
  showLiveBadge?: boolean;
  /** Visual size variant. */
  size?: "sm" | "md";
  className?: string;
};

const HOUR = 60 * 60 * 1000;
const MIN  = 60 * 1000;

export function KickoffCountdown({ kickoff, showLiveBadge = false, size = "sm", className = "" }: Props) {
  const target = kickoff.getTime();
  const [now, setNow] = useState(() => Date.now());

  useEffect(() => {
    let timer: ReturnType<typeof setTimeout>;
    function tick() {
      const t = Date.now();
      setNow(t);
      const diff = target - t;
      let next = 60_000;
      if (diff <= 0) next = 60_000;
      else if (diff <= 15 * MIN) next = 1_000;
      else if (diff <= 2 * HOUR) next = 30_000;
      else if (diff > 24 * HOUR) next = 5 * 60_000;
      timer = setTimeout(tick, next);
    }
    tick();
    return () => clearTimeout(timer);
  }, [target]);

  const diff = target - now;
  if (diff <= 0) {
    if (!showLiveBadge) return null;
    return (
      <span className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[10px] font-extrabold uppercase tracking-wider bg-[var(--ink)] text-white ${className}`}>
        Iniciado
      </span>
    );
  }

  // Only show within the same calendar day (Mexico City). Otherwise stay quiet.
  const sameDay = isSameDayInMexico(target, now);
  if (!sameDay) return null;
  const small = size === "sm";

  // <15 min: URGENT (red, pulses, ticks every second)
  if (diff <= 15 * MIN) {
    const m = Math.floor(diff / MIN);
    const s = Math.floor((diff % MIN) / 1000);
    const txt = m > 0 ? `${m}m ${String(s).padStart(2,"0")}s` : `${s}s`;
    return (
      <span
        className={`kickoff-urgent inline-flex items-center gap-1 rounded-full px-2 py-0.5 ${small ? "text-[10.5px]" : "text-[11px]"} font-extrabold uppercase tracking-wider bg-red-500 text-white ${className}`}
        title="Quedan pocos minutos para que cierre la quiniela de este partido"
      >
        <Zap size={11} className="-mx-0.5" />
        Por comenzar · <span className="tabular-nums">{txt}</span>
      </span>
    );
  }

  // 15min–2h: SOFT amber pulse
  if (diff <= 2 * HOUR) {
    const m = Math.round(diff / MIN);
    return (
      <span
        className={`kickoff-soft inline-flex items-center gap-1 rounded-full px-2 py-0.5 ${small ? "text-[10.5px]" : "text-[11px]"} font-extrabold uppercase tracking-wider bg-amber-500/15 text-amber-700 ring-1 ring-amber-500/30 ${className}`}
        title="El partido está por arrancar"
      >
        <Clock size={11} />
        Se acerca · <span className="tabular-nums">{m}m</span>
      </span>
    );
  }

  // Same day, >2h away: quiet "Hoy · Xh Ym"
  const h = Math.floor(diff / HOUR);
  const m = Math.round((diff % HOUR) / MIN);
  const txt = h > 0 ? `${h}h ${m}m` : `${m}m`;
  return (
    <span className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 ${small ? "text-[10.5px]" : "text-[11px]"} font-bold uppercase tracking-wide bg-[var(--accent-violet)]/10 text-[var(--accent-violet)] ${className}`}>
      <Clock size={10} />
      Hoy · <span className="tabular-nums">{txt}</span>
    </span>
  );
}

// True when `ts` falls on the same calendar day as `now` in Mexico City.
function isSameDayInMexico(ts: number, now: number): boolean {
  const fmt = new Intl.DateTimeFormat("en-CA", {
    timeZone: "America/Mexico_City",
    year: "numeric", month: "2-digit", day: "2-digit",
  });
  return fmt.format(new Date(ts)) === fmt.format(new Date(now));
}
